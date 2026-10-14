# CampusSkillSwap 🎓
> **Pure-Python Peer-to-Peer Student Skill Exchange, Mentorship & Safe Conduct Platform**

CampusSkillSwap is a web platform designed for college and university students to exchange academic skills, mentor peers, schedule 1-on-1 tutoring sessions, share study notes in a digital locker, and foster a safe, respectful learning community through verified peer conduct ratings.

---

## ✨ Core Interfaces & Features

### 1. 1st Interface: Authentication & Comprehensive Student Registration
- **Identity & Academic Details**: Full Name, College Email, Gender, Institute Name, Academic Department, and Academic Year.
- **Skill Swap Core**:
  - **"Skills I can teach"**: Indexed for prospective learners searching for mentors.
  - **"Skills I want to learn"**: Helps find reciprocal study partners across departments.
- **Academic Credentials & Experience**:
  - Academic Performance (CGPA / GPA, Dean's List, Honors).
  - Tutoring & project experience summary.
  - Extra skills & certifications (AWS, Hackathons, LaTeX, Debate, etc.).
  - About me / Teaching philosophy bio.

### 2. 2nd Interface: Intelligent Skill Search
- Instant search bar querying skills you want to learn (e.g. *Python, Calculus, Machine Learning, UI/UX*).
- Filter by Academic Domain / Department (Computer Science, Mathematics, AI, Electronics, IT).

### 3. 3rd Interface: Matching Profiles & Conduct Ranking
- Multi-tutor matching grid displaying all academic credentials, skills tags, and experience.
- **Tutor Teaching Rating**: 1-to-5 star rating based on instructional clarity and subject depth.
- **Peer Safety & Respectful Conduct Score**: Transparent rating and badge evaluating respectful behavior, professionalism, and safe peer environment.
- Rank by highest tutor rating, safest conduct score, academic performance (CGPA), or tutoring experience.

### 4. 4th Interface: 1-on-1 Session Scheduling
- Book sessions directly from profile cards with topic, date, time, and meeting format (Google Meet auto-links, Campus Library, Discord).
- Dedicated **My Sessions** dashboard:
  - Accept/Decline incoming requests (for tutors).
  - Mark completed sessions.

### 5. 5th Interface: Notes & Resource Exchange Locker
- Central repository to upload and download study materials:
  - Upload lecture notes, exam cheat sheets, and code repositories (PDF, DOCX, ZIP, PY, IPYNB) or share external cloud links (GitHub, Google Drive).
  - Domain categorization and download counters.

### 6. 6th Interface: Reciprocal Post-Session Rating System
- Once a session is completed, both student and tutor submit mutual feedback:
  - Student rates tutor on teaching clarity (1-5★) and respectful conduct/safety (1-5★).
  - Tutor rates student on engagement and courteous communication.
  - Dynamically updates database scores and public profile badges.

---

## 🎨 Visual Design
- **Theme**: Dark aesthetic with deep obsidian and blackish undertone form inputs (`#080c14`, `#0d131f`).
- **Collegiate Atmosphere**: Curated collegiate campus architecture, library study banners, and academic honor badges.
- **Pure Python**: Zero JavaScript build steps, zero node_modules.

---

## 🚀 Quickstart & Local Setup

### 1. Clone or Navigate to the Directory
```bash
cd campus_skill_swap
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize & Populate Sample Campus Data
```bash
python seed_data.py
```
*(Pre-seeds 6 student mentors with realistic CGPA, skills, ratings, sample study notes, and reviews).*

### 4. Run the Web Application
```bash
python app.py
```
Open your browser and navigate to:
**`http://127.0.0.1:5000`**

---

## 🔑 Pre-Seeded Demo Accounts

You can immediately log in using any of the following accounts (Password for all: `password123`):
- `aarav@campus.edu` (Male, CS Tutor, 9.4 CGPA, 5.0 Conduct Score)
- `ananya@campus.edu` (Female, AI & ML Tutor, 9.8 CGPA, 5.0 Conduct Score)
- `priya@campus.edu` (Female, UI/UX & Web Dev, 9.1 CGPA)
- `rohan@campus.edu` (Male, Mathematics & Calculus, 9.2 CGPA)

Or click **Join Network** to register a new student account!

---

## 🌐 How to Deploy on GitHub

### Step 1: Initialize Git and Commit
```bash
git init
git add .
git commit -m "Initial commit: CampusSkillSwap pure-python platform"
```

### Step 2: Push to Your GitHub Repository
1. Create a new repository on [GitHub](https://github.com/new) named `campus-skill-swap`.
2. Link your local project and push:
```bash
git remote add origin https://github.com/YOUR_USERNAME/campus-skill-swap.git
git branch -M main
git push -u origin main
```

---

## ☁️ 1-Click Free Cloud Deployment (e.g. Render / Railway)

### Deploying to Render:
1. Go to [Render.com](https://render.com) and log in with your GitHub account.
2. Click **New +** $\rightarrow$ **Web Service**.
3. Select your `campus-skill-swap` GitHub repository.
4. Render will automatically detect the included `render.yaml` or you can enter:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && python seed_data.py`
   - **Start Command**: `gunicorn app:app`
5. Click **Create Web Service**. Your app is live with free SSL!
