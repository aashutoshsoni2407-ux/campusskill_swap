import os
from database import get_db_connection, init_db, hash_password

def seed_database():
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if users already seeded
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] > 0:
        print("Database already contains records. Skipping seed.")
        conn.close()
        return

    users = [
        (
            "Aarav Sharma",
            "aarav@campus.edu",
            hash_password("password123"),
            "Male",
            "Apex Institute of Technology",
            "Computer Science",
            "3rd Year",
            "Python, Data Structures, Algorithms, Flask, Backend Engineering",
            "Deep Learning, Rust, Cloud Architecture",
            "CGPA: 9.4 / 10.0 (Top 2% Department)",
            "Teaching Assistant for CS101, solved 500+ LeetCode problems, 2 years mentoring",
            "ACM-ICPC Regional Finalist, Hackathon Winner 2025, Git / GitHub",
            "Passionate about algorithms and backend web systems. Known for breaking down complex dynamic programming and tree traversal into intuitive real-world examples.",
            "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?auto=format&fit=crop&w=400&q=80",
            4.9, 18,
            5.0, 16
        ),
        (
            "Ananya Iyer",
            "ananya@campus.edu",
            hash_password("password123"),
            "Female",
            "Apex Institute of Technology",
            "AI & Data Science",
            "4th Year",
            "Machine Learning, Python, PyTorch, Data Analysis, SQL, Statistics",
            "System Design, Kubernetes, Cyber Security",
            "CGPA: 9.8 / 10.0 (Dean's Gold Medalist)",
            "Research Fellow at University AI Lab, mentored 25+ students in neural networks",
            "TensorFlow Certified Developer, 1 IEEE Conference Paper, PyData Speaker",
            "I make machine learning and linear algebra easy and visual. Let's master everything from regression to deep neural architectures together!",
            "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=400&q=80",
            5.0, 24,
            5.0, 22
        ),
        (
            "Rohan Verma",
            "rohan@campus.edu",
            hash_password("password123"),
            "Male",
            "Metropolitan University",
            "Mathematics & Computing",
            "2nd Year",
            "Calculus, Linear Algebra, Probability & Statistics, Discrete Mathematics",
            "React, Modern Frontend, Flutter Mobile",
            "CGPA: 9.2 / 10.0 (National Math Olympiad Qualifier)",
            "1.5 years peer tutoring in University Mathematics Assistance Centre",
            "LaTeX Master, Chess Club Captain, Proof Writing Specialist",
            "Math becomes delightful when you grasp the intuition behind formulas. Patient tutor dedicated to zero-judgment, step-by-step derivations.",
            "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=400&q=80",
            4.8, 14,
            4.9, 13
        ),
        (
            "Priya Nair",
            "priya@campus.edu",
            hash_password("password123"),
            "Female",
            "Metropolitan University",
            "Information Technology",
            "3rd Year",
            "UI/UX Design, Figma, React, JavaScript, HTML/CSS, Tailwind CSS",
            "Go Lang, Docker, Cloud Security",
            "CGPA: 9.1 / 10.0 (Dean's Merit List)",
            "Lead UI Designer at Campus Developer Club, designed 8 production apps",
            "Design Systems, Figma Pro, Responsive Design, User Research",
            "Clean code meets captivating aesthetics. I teach modern frontend with real Figma files and modern responsive CSS best practices.",
            "https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=400&q=80",
            4.9, 19,
            5.0, 20
        ),
        (
            "Devansh Gupta",
            "devansh@campus.edu",
            hash_password("password123"),
            "Male",
            "Apex Institute of Technology",
            "Electronics & Communication",
            "4th Year",
            "C++, Object Oriented Programming, Embedded Systems, IoT, Arduino",
            "Computer Vision, Python, ROS Robotics",
            "CGPA: 8.9 / 10.0 (Engineering Honor Roll)",
            "Robotics Club Technical Lead, 2 years conducting hands-on lab sessions",
            "Microcontroller Architecture, Hardware Debugging, PCB Layout",
            "Dedicated to hands-on learning. I guide students through pointers, memory management, and microcontroller programming with utmost patience and respect.",
            "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=400&q=80",
            4.8, 15,
            5.0, 15
        ),
        (
            "Sneha Mukherjee",
            "sneha@campus.edu",
            hash_password("password123"),
            "Female",
            "Apex Institute of Technology",
            "Cyber Security & Networks",
            "3rd Year",
            "Cyber Security, Linux, Network Protocols, Ethical Hacking, Cryptography",
            "Competitive Programming, WebAssembly",
            "CGPA: 9.5 / 10.0 (Distinction in Network Security)",
            "Captain of Campus CTF Team, Top 30 in National Cyber Defense Challenge",
            "CompTIA Security+, Wireshark Certified, Bash Automation",
            "Demystifying packets, firewalls, and cryptographic handshakes. Every session includes hands-on labs on virtual Linux machines.",
            "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&w=400&q=80",
            5.0, 16,
            5.0, 18
        )
    ]

    cursor.executemany("""
    INSERT INTO users (
        name, email, password_hash, gender, college, department, year,
        skills_teach, skills_learn, academic_performance, experience,
        extra_skills, bio, profile_pic, tutor_rating, tutor_reviews_count,
        conduct_rating, conduct_reviews_count
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, users)

    # Insert sample resources / study notes
    resources = [
        (
            1, # Aarav
            "Data Structures & Algorithms Comprehensive Cheatsheet",
            "Complete hand-crafted quick reference covering Trees, Graphs, Dynamic Programming, and time-space complexities with Python snippets.",
            "Computer Science",
            "Python",
            None,
            "https://github.com/topics/data-structures-and-algorithms",
            84
        ),
        (
            2, # Ananya
            "Applied Machine Learning & Neural Networks Notes",
            "Detailed lecture summaries on backpropagation, gradient descent, CNNs, and PyTorch tensors with visual intuition diagrams.",
            "AI & Data Science",
            "Machine Learning",
            None,
            "https://github.com/topics/machine-learning",
            129
        ),
        (
            3, # Rohan
            "Engineering Mathematics: Multivariable Calculus & Linear Algebra Guide",
            "Concise formula sheet, eigenvalue calculation shortcuts, and double/triple integral step-by-step problem sets.",
            "Mathematics",
            "Calculus",
            None,
            "https://khanacademy.org/math/multivariable-calculus",
            72
        ),
        (
            4, # Priya
            "Modern UI/UX Design System Guide & Figma Component Kit",
            "Guidelines on visual hierarchy, typography scales, contrast ratios, and building reusable responsive React components.",
            "Design & Web",
            "UI/UX Design",
            None,
            "https://www.figma.com/community",
            95
        ),
        (
            6, # Sneha
            "Linux Commands & Cyber Defense Fundamentals Pocket Book",
            "Essential Bash commands, socket analysis, Wireshark filters, and hardening configurations for college labs.",
            "Cyber Security",
            "Cyber Security",
            None,
            "https://overthewire.org/wargames/",
            110
        )
    ]

    cursor.executemany("""
    INSERT INTO resources (
        user_id, title, description, domain, skill_tag, file_path, external_link, downloads
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, resources)

    # Insert sample completed session and ratings to demonstrate the review & conduct score system
    cursor.execute("""
    INSERT INTO sessions (
        student_id, tutor_id, skill_topic, session_date, session_time,
        duration_minutes, meet_mode, meet_link, notes, status, student_rated, tutor_rated
    ) VALUES (
        4, 1, 'Dynamic Programming & Memoization in Python', '2026-10-10', '18:00',
        60, 'Google Meet', 'https://meet.google.com/abc-swap-xyz',
        'Preparing for upcoming tech interviews. Need clarity on knapsack problems.',
        'completed', 1, 1
    )
    """)
    session_id = cursor.lastrowid

    # Review by Priya (Female student) for Aarav (Male tutor)
    cursor.execute("""
    INSERT INTO ratings (
        session_id, reviewer_id, reviewee_id, role, teaching_score, conduct_score, comment
    ) VALUES (
        ?, 4, 1, 'student_to_tutor', 5.0, 5.0,
        'Aarav was extraordinarily patient, clear, and exceptionally respectful throughout the entire session. He explained DP using diagrams that finally made sense. Highly recommended peer tutor!'
    )
    """, (session_id,))

    # Reciprocal review by Aarav for Priya
    cursor.execute("""
    INSERT INTO ratings (
        session_id, reviewer_id, reviewee_id, role, teaching_score, conduct_score, comment
    ) VALUES (
        ?, 1, 4, 'tutor_to_student', 5.0, 5.0,
        'Priya came thoroughly prepared with specific questions and wrote clean test cases during our coding exercise. Great collaboration and respect.'
    )
    """, (session_id,))

    conn.commit()
    conn.close()
    print("Seed data successfully added with realistic student profiles, resources, and reviews!")

if __name__ == "__main__":
    seed_database()
