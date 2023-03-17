import unittest
from .. import create_app
from ..config.config import config_dict
from ..utils import db
from flask_jwt_extended import create_access_token
from ..models.admin import Admin
from ..models.courses import Course
from ..models.courses import RegCourse
from ..models.students import Student
from ..models.students import UnverifiedStudent
from werkzeug.security import generate_password_hash, check_password_hash



class StudentTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(config=config_dict['test'])

        # To allow us use context
        self.appctx = self.app.app_context()

        # To push data to database
        self.appctx.push()

        # To work with test client
        self.client = self.app.test_client()

        db.create_all()

        

    # To reset everything before running setUp again
    def tearDown(self):
        db.drop_all()

        self.appctx.pop()

        self.app = None

        self.client = None


        
    def test_student_application(self):
        data = {
            "username": "TestUser",
            "email": "test@gmail.com"
        }

        response = self.client.post('/student/signup', json=data)

        unverifiedStudent = UnverifiedStudent.query.filter_by(email='test@gmail.com').first()

        assert unverifiedStudent.email == 'test@gmail.com'


        assert response.status_code == 201




    def test_student_login_passwordUpdate_profile(self):
        student = Student(
            username = 'Dave', email = 'dave@gmail.com', password_hash = generate_password_hash('password')
        )

        student.save()

        # for jwt_required
        token = create_access_token(identity=student.username)

        data = {
            "email": "dave@gmail.com",
            "password": "password"
        }

        headers = {
            "Authorization": f"Bearer {token}"
        }

        # Login Student
        response = self.client.post('/student/login', json=data )

        assert response.status_code == 201



        # Password Update 
        data2 = {
            'old_password':'password',
            'new_password':'sammey'
        }
        response2 = self.client.put('/student/update_password', json=data2, headers=headers )

        assert response2.status_code == 200



        # Get Profile of Logged in Student
        response3 = self.client.get('/student/profile', headers=headers )

        assert response3.status_code == 200

        student = Student.query.filter_by(username='Dave').first()

        assert check_password_hash(student.password_hash, 'sammey')




    def test_student_getUserCourses(self):

        student = Student(
            username = 'David', email = 'david@gmail.com', password_hash = generate_password_hash('password')
        )

        student.save()

        course = Course(
            name = 'MTH111', teacher = 'Daniel'
        )

        course.save()

        # for jwt_required
        token = create_access_token(identity=student.username)

        headers = {
            "Authorization": f"Bearer {token}"
        }

        # Register a course by Course Name
        response = self.client.post('/student/course/MTH111', headers=headers)

        assert response.status_code == 201


    
        # Get Current Student course by Course Name
        response = self.client.get('/student/course/MTH111', headers=headers)

        assert response.status_code == 200


        # Get Current Student's Courses
        response2 = self.client.get('/student/courses', headers=headers)

        assert response2.status_code == 200


        
        # Unregister Current Student's Course by Course Name
        response3 = self.client.delete('/student/course/MTH111', headers=headers)

        assert response3.status_code == 200

        

    
    