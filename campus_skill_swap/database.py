import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "campus_skill_swap.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        gender TEXT DEFAULT 'Prefer not to say',
        college TEXT DEFAULT 'University Campus',
        department TEXT DEFAULT 'Computer Science',
        year TEXT DEFAULT '3rd Year',
        skills_teach TEXT NOT NULL,
        skills_learn TEXT NOT NULL,
        academic_performance TEXT DEFAULT 'CGPA 3.8 / 4.0',
        experience TEXT DEFAULT 'Experienced student mentor',
        extra_skills TEXT DEFAULT 'Project Management, Problem Solving',
        bio TEXT,
        profile_pic TEXT,
        tutor_rating REAL DEFAULT 5.0,
        tutor_reviews_count INTEGER DEFAULT 0,
        conduct_rating REAL DEFAULT 5.0,
        conduct_reviews_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        tutor_id INTEGER NOT NULL,
        skill_topic TEXT NOT NULL,
        session_date TEXT NOT NULL,
        session_time TEXT NOT NULL,
        duration_minutes INTEGER DEFAULT 60,
        meet_mode TEXT DEFAULT 'Google Meet',
        meet_link TEXT,
        notes TEXT,
        status TEXT DEFAULT 'pending',
        student_rated INTEGER DEFAULT 0,
        tutor_rated INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES users (id),
        FOREIGN KEY (tutor_id) REFERENCES users (id)
    );

    CREATE TABLE IF NOT EXISTS ratings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        reviewer_id INTEGER NOT NULL,
        reviewee_id INTEGER NOT NULL,
        role TEXT NOT NULL,
        teaching_score REAL DEFAULT 5.0,
        conduct_score REAL DEFAULT 5.0,
        comment TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES sessions (id),
        FOREIGN KEY (reviewer_id) REFERENCES users (id),
        FOREIGN KEY (reviewee_id) REFERENCES users (id)
    );

    CREATE TABLE IF NOT EXISTS resources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        domain TEXT DEFAULT 'Computer Science',
        skill_tag TEXT,
        file_path TEXT,
        external_link TEXT,
        downloads INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    );
    """)

    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    return generate_password_hash(password)

def verify_password(stored_hash: str, password: str) -> bool:
    return check_password_hash(stored_hash, password)

def update_user_ratings(user_id: int):
    """
    Recalculates tutor rating (teaching_score) and conduct rating (conduct_score)
    for a user based on received ratings.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Recalculate teaching rating (when user acted as tutor)
    cursor.execute("""
        SELECT AVG(teaching_score), COUNT(teaching_score)
        FROM ratings
        WHERE reviewee_id = ? AND role = 'student_to_tutor'
    """, (user_id,))
    tutor_row = cursor.fetchone()
    avg_tutor = round(tutor_row[0], 1) if tutor_row and tutor_row[0] is not None else 5.0
    count_tutor = tutor_row[1] if tutor_row else 0

    # Recalculate conduct rating (respectful behavior across all interactions)
    cursor.execute("""
        SELECT AVG(conduct_score), COUNT(conduct_score)
        FROM ratings
        WHERE reviewee_id = ?
    """, (user_id,))
    conduct_row = cursor.fetchone()
    avg_conduct = round(conduct_row[0], 1) if conduct_row and conduct_row[0] is not None else 5.0
    count_conduct = conduct_row[1] if conduct_row else 0

    cursor.execute("""
        UPDATE users
        SET tutor_rating = ?,
            tutor_reviews_count = ?,
            conduct_rating = ?,
            conduct_reviews_count = ?
        WHERE id = ?
    """, (avg_tutor, count_tutor, avg_conduct, count_conduct, user_id))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at:", DB_PATH)
