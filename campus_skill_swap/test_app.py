import unittest
import time
from app import app
from database import get_db_connection

class TestCampusSkillSwap(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    def test_01_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Campus', response.data)
        self.assertIn(b'Swap', response.data)
        self.assertIn(b'Verified Peer Mentors', response.data)

    def test_02_search_skill(self):
        response = self.client.get('/search?q=Python')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Aarav Sharma', response.data)
        self.assertIn(b'Matching Profiles', response.data)
        self.assertIn(b'Conduct Score', response.data)

    def test_03_registration(self):
        email = f"test_{int(time.time())}@campus.edu"
        data = {
            'name': 'Test Student',
            'email': email,
            'password': 'testpassword123',
            'gender': 'Female',
            'college': 'Test College',
            'department': 'Computer Science',
            'year': '2nd Year',
            'skills_teach': 'Go, Docker, Kubernetes',
            'skills_learn': 'Rust, WebAssembly',
            'academic_performance': 'CGPA 9.6 / 10.0',
            'experience': 'Cloud dev intern',
            'extra_skills': 'Docker Certified',
            'bio': 'Passionate about distributed systems.'
        }
        response = self.client.post('/register', data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Student', response.data)

    def test_04_login(self):
        self.client.get('/logout')
        data = {
            'email': 'aarav@campus.edu',
            'password': 'password123'
        }
        response = self.client.post('/login', data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Aarav', response.data)

    def test_05_profile_view(self):
        response = self.client.get('/profile/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Aarav Sharma', response.data)
        self.assertIn(b'Safe Conduct & Respect Score', response.data)
        self.assertIn(b'Skills & Academic Profile', response.data)

    def test_06_resources_hub(self):
        response = self.client.get('/resources')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Notes & Academic Resources', response.data)
        self.assertIn(b'Cheatsheet', response.data)

    def test_07_session_workflow_and_rating(self):
        client = app.test_client()
        # 1. Student logs in
        client.post('/login', data={'email': 'priya@campus.edu', 'password': 'password123'})
        
        # 2. Student schedules session with tutor 5 (Devansh)
        sched_data = {
            'skill_topic': 'Embedded C++ Pointers',
            'session_date': '2026-10-20',
            'session_time': '16:00',
            'duration_minutes': '60',
            'meet_mode': 'Google Meet',
            'notes': 'Need help with memory management.'
        }
        sched_resp = client.post('/schedule/5', data=sched_data, follow_redirects=True)
        self.assertEqual(sched_resp.status_code, 200)
        self.assertIn(b'Tutoring session successfully requested', sched_resp.data)

        # Get latest session ID
        conn = get_db_connection()
        sess = conn.execute("SELECT id FROM sessions WHERE student_id = 4 AND tutor_id = 5 ORDER BY id DESC LIMIT 1").fetchone()
        session_id = sess['id']
        conn.close()

        # 3. Tutor logs in (using new test client)
        tutor_client = app.test_client()
        tutor_client.post('/login', data={'email': 'devansh@campus.edu', 'password': 'password123'})

        # Accept session
        acc_resp = tutor_client.post(f'/session/{session_id}/update-status', data={'status': 'accepted'}, follow_redirects=True)
        self.assertEqual(acc_resp.status_code, 200)

        # Mark completed
        comp_resp = tutor_client.post(f'/session/{session_id}/update-status', data={'status': 'completed'}, follow_redirects=True)
        self.assertEqual(comp_resp.status_code, 200)

        # 4. Student rates tutor
        rate_data = {
            'teaching_score': '5.0',
            'conduct_score': '5.0',
            'comment': 'Devansh was very polite, professional, and clear!'
        }
        rate_resp = client.post(f'/session/{session_id}/rate', data=rate_data, follow_redirects=True)
        self.assertEqual(rate_resp.status_code, 200)
        self.assertIn(b'Feedback Submitted', rate_resp.data)

    def test_08_edit_profile(self):
        client = app.test_client()
        client.post('/login', data={'email': 'aarav@campus.edu', 'password': 'password123'})
        edit_data = {
            'name': 'Aarav Sharma Updated',
            'college': 'Apex Institute of Technology',
            'department': 'Computer Science & AI',
            'year': '4th Year',
            'skills_teach': 'Python, PyTorch, Algorithms, Distributed Systems',
            'skills_learn': 'Rust, WebAssembly',
            'academic_performance': 'CGPA 9.5 / 10.0',
            'experience': '3 years tutoring CS101, solved 600+ LeetCode problems',
            'extra_skills': 'ICPC Finalist, Cloud Architect',
            'bio': 'Updated bio description.',
            'profile_pic': 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6'
        }
        resp = client.post('/my-profile', data=edit_data, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Aarav Sharma Updated', resp.data)

    def test_09_resource_upload_and_download(self):
        client = app.test_client()
        client.post('/login', data={'email': 'aarav@campus.edu', 'password': 'password123'})
        upload_data = {
            'title': 'Test Python Guide',
            'domain': 'Computer Science',
            'skill_tag': 'Python',
            'description': 'A quick summary of python concurrency',
            'external_link': 'https://github.com/python/cpython'
        }
        up_resp = client.post('/resources/upload', data=upload_data, follow_redirects=True)
        self.assertEqual(up_resp.status_code, 200)
        self.assertIn(b'Test Python Guide', up_resp.data)

        # Download resource with external link
        conn = get_db_connection()
        res = conn.execute("SELECT id FROM resources WHERE title = 'Test Python Guide'").fetchone()
        res_id = res['id']
        conn.close()

        down_resp = client.get(f'/resources/download/{res_id}')
        # Should redirect to external link (302)
        self.assertEqual(down_resp.status_code, 302)
        self.assertEqual(down_resp.headers['Location'], 'https://github.com/python/cpython')

    def test_10_demo_login(self):
        client = app.test_client()
        resp = client.get('/demo-login/aarav', follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Logged in instantly as Aarav', resp.data)

if __name__ == '__main__':
    unittest.main()
