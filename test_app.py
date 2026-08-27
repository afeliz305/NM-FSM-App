import unittest
from app import app, db, Students, init_db

class TestFlaskStudentsApp(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        init_db()

    def test_show_all_screen(self):
        """Test GET / (All Students screen)"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("All Students", html)
        self.assertIn("<th>Phone Number</th>", html)
        # Check that existing students and their phone numbers are displayed
        with app.app_context():
            students = Students.query.all()
            self.assertGreater(len(students), 0)
            for student in students:
                self.assertIn(student.name.strip(), html)
                if student.phone_number:
                    self.assertIn(student.phone_number, html)

    def test_new_student_screen_get(self):
        """Test GET /new (Add New Student screen)"""
        response = self.client.get('/new')
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Add New Student", html)
        self.assertIn('name="phone_number"', html)

    def test_new_student_post_success(self):
        """Test POST /new (Adding student with phone number)"""
        test_student_data = {
            'name': 'Test Student',
            'city': 'Tampa',
            'addr': '456 College Way',
            'pin': '33620',
            'phone_number': '813-555-0144'
        }
        response = self.client.post('/new', data=test_student_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Record was successfully added", html)
        self.assertIn("Test Student", html)
        self.assertIn("813-555-0144", html)

        # Verify record in database and clean up test record
        with app.app_context():
            student = Students.query.filter_by(name='Test Student').first()
            self.assertIsNotNone(student)
            self.assertEqual(student.phone_number, '813-555-0144')
            db.session.delete(student)
            db.session.commit()

    def test_new_student_post_validation_failure(self):
        """Test POST /new validation error when required fields are missing"""
        response = self.client.post('/new', data={'name': '', 'city': '', 'addr': ''}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Please enter all the fields", html)

if __name__ == '__main__':
    unittest.main()
