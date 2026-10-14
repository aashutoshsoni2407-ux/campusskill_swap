import os
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for, session,
    flash, send_from_directory, abort
)
from werkzeug.utils import secure_filename
from database import (
    get_db_connection, init_db, hash_password, verify_password, update_user_ratings
)
from seed_data import seed_database

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "campus-skill-swap-secret-key-super-secure-2026")

UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads")
ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "txt", "zip", "png", "jpg", "jpeg", "ipynb", "py"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max upload

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this feature.", "warning")
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.context_processor
def inject_user():
    user = None
    if "user_id" in session:
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
        conn.close()
    return dict(current_user=user)

# -------------------------------------------------------------
# Home & Landing Interface
# -------------------------------------------------------------
@app.route("/")
def index():
    conn = get_db_connection()
    # Featured tutors (top rated with high conduct score)
    featured_tutors = conn.execute("""
        SELECT * FROM users
        ORDER BY tutor_rating DESC, conduct_rating DESC, tutor_reviews_count DESC
        LIMIT 4
    """).fetchall()

    stats = {
        "students": conn.execute("SELECT COUNT(*) FROM users").fetchone()[0],
        "sessions": conn.execute("SELECT COUNT(*) FROM sessions WHERE status = 'completed'").fetchone()[0],
        "resources": conn.execute("SELECT COUNT(*) FROM resources").fetchone()[0],
        "tutors": conn.execute("SELECT COUNT(*) FROM users WHERE tutor_reviews_count > 0").fetchone()[0]
    }
    conn.close()
    return render_template("index.html", featured_tutors=featured_tutors, stats=stats)

# -------------------------------------------------------------
# 1st Interface: Authentication & Comprehensive Registration
# -------------------------------------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        gender = request.form.get("gender", "Prefer not to say")
        college = request.form.get("college", "University Campus").strip()
        department = request.form.get("department", "Computer Science").strip()
        year = request.form.get("year", "1st Year")
        skills_teach = request.form.get("skills_teach", "").strip()
        skills_learn = request.form.get("skills_learn", "").strip()
        academic_performance = request.form.get("academic_performance", "CGPA 3.8 / 4.0").strip()
        experience = request.form.get("experience", "Passionate student tutor").strip()
        extra_skills = request.form.get("extra_skills", "").strip()
        bio = request.form.get("bio", "").strip()

        if not name or not email or not password or not skills_teach or not skills_learn:
            flash("Please fill in all mandatory fields.", "danger")
            return render_template("register.html", form=request.form)

        conn = get_db_connection()
        existing = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing:
            conn.close()
            flash("An account with this email already exists. Please log in.", "warning")
            return redirect(url_for("login"))

        password_hash = hash_password(password)

        # Default avatar based on gender selection
        if gender == "Female":
            default_pic = "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=400&q=80"
        elif gender == "Male":
            default_pic = "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=400&q=80"
        else:
            default_pic = "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=400&q=80"

        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (
                name, email, password_hash, gender, college, department, year,
                skills_teach, skills_learn, academic_performance, experience,
                extra_skills, bio, profile_pic, tutor_rating, tutor_reviews_count,
                conduct_rating, conduct_reviews_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 5.0, 0, 5.0, 0)
        """, (
            name, email, password_hash, gender, college, department, year,
            skills_teach, skills_learn, academic_performance, experience,
            extra_skills, bio, default_pic
        ))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()

        session["user_id"] = user_id
        session["user_name"] = name
        flash(f"Welcome to CampusSkillSwap, {name}! Your profile is active.", "success")
        return redirect(url_for("search"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please enter both campus email and password.", "warning")
            return render_template("login.html")

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()

        if not user:
            flash(f"No account found with '{email}'. Please click 'Join Network' below to register first, or use a 1-click demo login.", "warning")
            return render_template("login.html")

        # Allow exact match or stripped match (handles accidental trailing spaces)
        if verify_password(user["password_hash"], password) or verify_password(user["password_hash"], password.strip()):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            flash(f"Welcome back, {user['name']}!", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("search"))
        else:
            flash("Incorrect password. Please try again. (Demo accounts password is: password123)", "danger")

    return render_template("login.html")

@app.route("/demo-login/<string:demo_user>")
def demo_login(demo_user):
    demo_emails = {
        "aarav": "aarav@campus.edu",
        "ananya": "ananya@campus.edu",
        "priya": "priya@campus.edu",
        "rohan": "rohan@campus.edu",
        "devansh": "devansh@campus.edu",
        "sneha": "sneha@campus.edu"
    }
    target_email = demo_emails.get(demo_user.lower())
    if not target_email:
        flash("Demo persona not recognized.", "warning")
        return redirect(url_for("login"))

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (target_email,)).fetchone()
    conn.close()

    if not user:
        seed_database()
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (target_email,)).fetchone()
        conn.close()

    if user:
        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        flash(f"⚡ Logged in instantly as {user['name']} ({user['department']} • {user['year']})!", "success")
        return redirect(url_for("search"))
    else:
        flash("Could not initialize demo user. Please register a new account.", "danger")
        return redirect(url_for("register"))

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out safely.", "info")
    return redirect(url_for("index"))

# -------------------------------------------------------------
# 2nd & 3rd Interface: Search & Matching Profiles Grid
# -------------------------------------------------------------
@app.route("/search")
def search():
    query = request.args.get("q", "").strip()
    domain = request.args.get("domain", "").strip()
    min_rating = request.args.get("min_rating", "")
    min_conduct = request.args.get("min_conduct", "")
    sort_by = request.args.get("sort_by", "rating")

    conn = get_db_connection()
    sql = "SELECT * FROM users WHERE 1=1"
    params = []

    # If logged in, optionally don't prioritize self in matching
    current_uid = session.get("user_id")

    if query:
        sql += " AND (skills_teach LIKE ? OR skills_learn LIKE ? OR extra_skills LIKE ? OR name LIKE ?)"
        pattern = f"%{query}%"
        params.extend([pattern, pattern, pattern, pattern])

    if domain:
        sql += " AND department = ?"
        params.append(domain)

    if min_rating:
        try:
            sql += " AND tutor_rating >= ?"
            params.append(float(min_rating))
        except ValueError:
            pass

    if min_conduct:
        try:
            sql += " AND conduct_rating >= ?"
            params.append(float(min_conduct))
        except ValueError:
            pass

    # Order/Ranking logic
    if sort_by == "conduct":
        # Sort by Conduct / Respectful Behavior Score
        sql += " ORDER BY conduct_rating DESC, conduct_reviews_count DESC, tutor_rating DESC"
    elif sort_by == "experience":
        sql += " ORDER BY tutor_reviews_count DESC, tutor_rating DESC"
    elif sort_by == "academic":
        sql += " ORDER BY academic_performance DESC, tutor_rating DESC"
    else:
        # Default: Tutor Rating + Conduct Score
        sql += " ORDER BY tutor_rating DESC, conduct_rating DESC"

    tutors = conn.execute(sql, params).fetchall()

    # Get distinct departments for filter dropdown
    departments = [row[0] for row in conn.execute("SELECT DISTINCT department FROM users WHERE department IS NOT NULL").fetchall()]
    conn.close()

    return render_template(
        "search.html",
        tutors=tutors,
        query=query,
        selected_domain=domain,
        min_rating=min_rating,
        min_conduct=min_conduct,
        sort_by=sort_by,
        departments=departments
    )

# -------------------------------------------------------------
# Detailed Profile View
# -------------------------------------------------------------
@app.route("/profile/<int:user_id>")
def profile(user_id):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        conn.close()
        flash("Student profile not found.", "danger")
        return redirect(url_for("search"))

    # Fetch reviews for this user (both teaching and conduct)
    reviews = conn.execute("""
        SELECT r.*, u.name as reviewer_name, u.profile_pic as reviewer_pic, u.department as reviewer_dept
        FROM ratings r
        JOIN users u ON r.reviewer_id = u.id
        WHERE r.reviewee_id = ?
        ORDER BY r.created_at DESC
    """, (user_id,)).fetchall()

    # User's uploaded resources
    user_resources = conn.execute("""
        SELECT * FROM resources WHERE user_id = ? ORDER BY created_at DESC
    """, (user_id,)).fetchall()

    conn.close()
    return render_template("profile.html", profile_user=user, reviews=reviews, resources=user_resources)

# -------------------------------------------------------------
# 4th Interface: Session Scheduling
# -------------------------------------------------------------
@app.route("/schedule/<int:tutor_id>", methods=["POST"])
@login_required
def schedule_session(tutor_id):
    student_id = session["user_id"]

    if student_id == tutor_id:
        flash("You cannot schedule a tutoring session with yourself.", "warning")
        return redirect(url_for("profile", user_id=tutor_id))

    skill_topic = request.form.get("skill_topic", "").strip()
    session_date = request.form.get("session_date", "").strip()
    session_time = request.form.get("session_time", "").strip()
    try:
        duration_minutes = int(request.form.get("duration_minutes", 60))
    except (ValueError, TypeError):
        duration_minutes = 60
    meet_mode = request.form.get("meet_mode", "Google Meet")
    meet_link = request.form.get("meet_link", "").strip()
    notes = request.form.get("notes", "").strip()

    if not skill_topic or not session_date or not session_time:
        flash("Please provide topic, date, and time for the session.", "danger")
        return redirect(url_for("profile", user_id=tutor_id))

    if not meet_link:
        if meet_mode == "Google Meet":
            meet_link = f"https://meet.google.com/swap-{abs(hash(skill_topic + session_date)) % 1000000}"
        else:
            meet_link = f"{meet_mode} - Scheduled Location"

    conn = get_db_connection()
    conn.execute("""
        INSERT INTO sessions (
            student_id, tutor_id, skill_topic, session_date, session_time,
            duration_minutes, meet_mode, meet_link, notes, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')
    """, (
        student_id, tutor_id, skill_topic, session_date, session_time,
        duration_minutes, meet_mode, meet_link, notes
    ))
    conn.commit()
    conn.close()

    flash("Tutoring session successfully requested! Waiting for tutor confirmation.", "success")
    return redirect(url_for("my_sessions"))

@app.route("/sessions")
@login_required
def my_sessions():
    user_id = session["user_id"]
    conn = get_db_connection()

    # Sessions where current user is student
    as_student = conn.execute("""
        SELECT s.*, t.name as partner_name, t.profile_pic as partner_pic,
               t.department as partner_dept, t.tutor_rating as partner_rating,
               t.conduct_rating as partner_conduct
        FROM sessions s
        JOIN users t ON s.tutor_id = t.id
        WHERE s.student_id = ?
        ORDER BY s.session_date DESC, s.session_time DESC
    """, (user_id,)).fetchall()

    # Sessions where current user is tutor
    as_tutor = conn.execute("""
        SELECT s.*, st.name as partner_name, st.profile_pic as partner_pic,
               st.department as partner_dept, st.tutor_rating as partner_rating,
               st.conduct_rating as partner_conduct
        FROM sessions s
        JOIN users st ON s.student_id = st.id
        WHERE s.tutor_id = ?
        ORDER BY s.session_date DESC, s.session_time DESC
    """, (user_id,)).fetchall()

    conn.close()
    return render_template("sessions.html", as_student=as_student, as_tutor=as_tutor)

@app.route("/session/<int:session_id>/update-status", methods=["POST"])
@login_required
def update_session_status(session_id):
    user_id = session["user_id"]
    new_status = request.form.get("status", "")

    if new_status not in ["accepted", "declined", "completed", "cancelled"]:
        flash("Invalid status update.", "danger")
        return redirect(url_for("my_sessions"))

    conn = get_db_connection()
    session_row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()

    if not session_row:
        conn.close()
        flash("Session not found.", "danger")
        return redirect(url_for("my_sessions"))

    # Authorize: Tutor can accept/decline; either student or tutor can mark completed/cancelled
    if new_status in ["accepted", "declined"] and session_row["tutor_id"] != user_id:
        conn.close()
        flash("Only the tutor can accept or decline requests.", "danger")
        return redirect(url_for("my_sessions"))

    if user_id not in [session_row["student_id"], session_row["tutor_id"]]:
        conn.close()
        flash("Unauthorized action.", "danger")
        return redirect(url_for("my_sessions"))

    conn.execute("UPDATE sessions SET status = ? WHERE id = ?", (new_status, session_id))
    conn.commit()
    conn.close()

    flash(f"Session status updated to '{new_status.capitalize()}'.", "success")
    return redirect(url_for("my_sessions"))

# -------------------------------------------------------------
# 6th Interface: Reciprocal Rating & Respectful Conduct Review
# -------------------------------------------------------------
@app.route("/session/<int:session_id>/rate", methods=["POST"])
@login_required
def submit_rating(session_id):
    user_id = session["user_id"]
    try:
        teaching_score = min(5.0, max(1.0, float(request.form.get("teaching_score", 5.0))))
        conduct_score = min(5.0, max(1.0, float(request.form.get("conduct_score", 5.0))))
    except (ValueError, TypeError):
        teaching_score, conduct_score = 5.0, 5.0
    comment = request.form.get("comment", "").strip()

    conn = get_db_connection()
    session_row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()

    if not session_row or session_row["status"] != "completed":
        conn.close()
        flash("Ratings can only be submitted for completed sessions.", "warning")
        return redirect(url_for("my_sessions"))

    if user_id == session_row["student_id"]:
        # Student rating Tutor
        if session_row["student_rated"]:
            conn.close()
            flash("You have already reviewed this tutor for this session.", "info")
            return redirect(url_for("my_sessions"))

        role = "student_to_tutor"
        reviewee_id = session_row["tutor_id"]

        conn.execute("""
            INSERT INTO ratings (session_id, reviewer_id, reviewee_id, role, teaching_score, conduct_score, comment)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (session_id, user_id, reviewee_id, role, teaching_score, conduct_score, comment))

        conn.execute("UPDATE sessions SET student_rated = 1 WHERE id = ?", (session_id,))
        conn.commit()
        conn.close()

        update_user_ratings(reviewee_id)
        flash("Tutor rating & respectful conduct review submitted successfully!", "success")

    elif user_id == session_row["tutor_id"]:
        # Tutor rating Student
        if session_row["tutor_rated"]:
            conn.close()
            flash("You have already reviewed this student for this session.", "info")
            return redirect(url_for("my_sessions"))

        role = "tutor_to_student"
        reviewee_id = session_row["student_id"]

        conn.execute("""
            INSERT INTO ratings (session_id, reviewer_id, reviewee_id, role, teaching_score, conduct_score, comment)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (session_id, user_id, reviewee_id, role, teaching_score, conduct_score, comment))

        conn.execute("UPDATE sessions SET tutor_rated = 1 WHERE id = ?", (session_id,))
        conn.commit()
        conn.close()

        update_user_ratings(reviewee_id)
        flash("Student performance & conduct feedback submitted successfully!", "success")
    else:
        conn.close()
        flash("Unauthorized action.", "danger")

    return redirect(url_for("my_sessions"))

# -------------------------------------------------------------
# 5th Interface: Notes & Resource Exchange Hub
# -------------------------------------------------------------
@app.route("/resources")
def resources():
    domain = request.args.get("domain", "").strip()
    query = request.args.get("q", "").strip()

    conn = get_db_connection()
    sql = """
        SELECT r.*, u.name as author_name, u.department as author_dept, u.profile_pic as author_pic
        FROM resources r
        JOIN users u ON r.user_id = u.id
        WHERE 1=1
    """
    params = []

    if query:
        sql += " AND (r.title LIKE ? OR r.description LIKE ? OR r.skill_tag LIKE ?)"
        pattern = f"%{query}%"
        params.extend([pattern, pattern, pattern])

    if domain:
        sql += " AND r.domain = ?"
        params.append(domain)

    sql += " ORDER BY r.downloads DESC, r.created_at DESC"
    all_resources = conn.execute(sql, params).fetchall()

    domains = [row[0] for row in conn.execute("SELECT DISTINCT domain FROM resources WHERE domain IS NOT NULL").fetchall()]
    conn.close()

    return render_template(
        "resources.html",
        resources=all_resources,
        domains=domains,
        selected_domain=domain,
        query=query
    )

@app.route("/resources/upload", methods=["POST"])
@login_required
def upload_resource():
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    domain = request.form.get("domain", "Computer Science").strip()
    skill_tag = request.form.get("skill_tag", "").strip()
    external_link = request.form.get("external_link", "").strip()

    if not title:
        flash("Please provide a title for your study resource.", "danger")
        return redirect(url_for("resources"))

    file_path = None
    if "file" in request.files:
        file = request.files["file"]
        if file and file.filename != "":
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"res_{session['user_id']}_{filename}"
                save_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
                file.save(save_path)
                file_path = unique_filename
            else:
                flash("Unsupported file format. Please upload PDF, DOCX, TXT, ZIP, PY, or IPYNB.", "warning")
                return redirect(url_for("resources"))

    if not file_path and not external_link:
        flash("Please either upload a document or provide an external resource link.", "warning")
        return redirect(url_for("resources"))

    conn = get_db_connection()
    conn.execute("""
        INSERT INTO resources (user_id, title, description, domain, skill_tag, file_path, external_link, downloads)
        VALUES (?, ?, ?, ?, ?, ?, ?, 0)
    """, (session["user_id"], title, description, domain, skill_tag, file_path, external_link))
    conn.commit()
    conn.close()

    flash("Study resource uploaded successfully to the campus locker!", "success")
    return redirect(url_for("resources"))

@app.route("/resources/download/<int:resource_id>")
def download_resource(resource_id):
    conn = get_db_connection()
    res = conn.execute("SELECT * FROM resources WHERE id = ?", (resource_id,)).fetchone()

    if not res:
        conn.close()
        flash("Resource not found.", "danger")
        return redirect(url_for("resources"))

    # Increment download count
    conn.execute("UPDATE resources SET downloads = downloads + 1 WHERE id = ?", (resource_id,))
    conn.commit()
    conn.close()

    if res["file_path"]:
        file_disk_path = os.path.join(app.config["UPLOAD_FOLDER"], res["file_path"])
        if os.path.exists(file_disk_path):
            return send_from_directory(app.config["UPLOAD_FOLDER"], res["file_path"], as_attachment=True)
        elif res["external_link"]:
            return redirect(res["external_link"])
        else:
            flash("Uploaded document is currently unavailable on disk.", "warning")
            return redirect(url_for("resources"))
    elif res["external_link"]:
        return redirect(res["external_link"])
    else:
        flash("Resource content unavailable.", "warning")
        return redirect(url_for("resources"))

# -------------------------------------------------------------
# My Profile Management
# -------------------------------------------------------------
@app.route("/my-profile", methods=["GET", "POST"])
@login_required
def my_profile():
    user_id = session["user_id"]
    conn = get_db_connection()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        college = request.form.get("college", "").strip()
        department = request.form.get("department", "").strip()
        year = request.form.get("year", "")
        skills_teach = request.form.get("skills_teach", "").strip()
        skills_learn = request.form.get("skills_learn", "").strip()
        academic_performance = request.form.get("academic_performance", "").strip()
        experience = request.form.get("experience", "").strip()
        extra_skills = request.form.get("extra_skills", "").strip()
        bio = request.form.get("bio", "").strip()
        profile_pic = request.form.get("profile_pic", "").strip()

        conn.execute("""
            UPDATE users
            SET name = ?, college = ?, department = ?, year = ?,
                skills_teach = ?, skills_learn = ?, academic_performance = ?,
                experience = ?, extra_skills = ?, bio = ?, profile_pic = ?
            WHERE id = ?
        """, (
            name, college, department, year,
            skills_teach, skills_learn, academic_performance,
            experience, extra_skills, bio, profile_pic, user_id
        ))
        conn.commit()
        session["user_name"] = name
        flash("Your profile has been updated!", "success")

    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return render_template("profile.html", profile_user=user, is_owner=True, reviews=[], resources=[])

if __name__ == "__main__":
    init_db()
    seed_database()
    # Runs locally on port 5000
    app.run(host="0.0.0.0", port=5000, debug=True)
