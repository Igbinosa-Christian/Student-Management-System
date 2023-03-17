
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
from flask_jwt_extended import jwt_required, get_jwt_identity


class AdminTestCase(unittest.TestCase):

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


    # Test Admin Registration
    def test_admin_registration(self):
        data = {
            "username": "TestAdmin",
            "email": "testAdmin@gmail.com",
            "password": "password"
        }

        response = self.client.post('/admin/adminsignup', json=data)

        admin = Admin.query.filter_by(email='testAdmin@gmail.com').first()

        assert admin.is_admin == 1


        assert response.status_code == 201



    def test_admin_login(self):
        data = {
            "email": "testAeeedmin@gmail.com",
            "password": "password"
        }

        response = self.client.post('/admin/adminlogin', json=data)

        assert response.status_code == 200





    
    def test_admin_get_students(self):
        admin = Admin(
            username = 'Admin', email = 'admin@gmail.com', password_hash = 'wdwjkhwhewjejwhejw'
        )

        admin.save()

        # for jwt_required
        token = create_access_token(identity=admin.username)

        headers = {
            "Authorization": f"Bearer {token}"
        }

        response = self.client.get('/admin/students', headers=headers )

        assert get_jwt_identity() == 'Admin'

        assert response.status_code == 200






    def test_admin_verify_get_student_by_username(self):
        admin = Admin(
            username = 'Admin', email = 'admin@gmail.com', password_hash = 'wdwjkhwhewjejwhejw'
        )

        admin.save()

        unverifiedStudent = UnverifiedStudent(
            username = 'Sam', email = 'sam@gmail.com'
        )

        unverifiedStudent.save()

        # for jwt_required
        token = create_access_token(identity=admin.username)

        headers = {
            "Authorization": f"Bearer {token}"
        }

        # Verify Student Application by Username
        response = self.client.post('/admin/student/Sam', headers=headers )

        assert response.status_code == 201




        # Get Student by Username
        response2 = self.client.get('/admin/student/Sam', headers=headers )

        assert response2.status_code == 201
        students = Student.query.all()
        assert students[0].username == 'Sam'




        # Delete Student by Username
        response3 = self.client.delete('/admin/student/Sam', headers=headers)
        
        assert response3.status_code == 200
        
        students2 = Student.query.all()
        assert len(students2) == 0






    def test_admin_create_get_courses(self):
        admin = Admin(
            username = 'Admin', email = 'admin@gmail.com', password_hash = 'wdwjkhwhewjejwhejw'
        )

        admin.save()

        data = {
            'name': 'MTH111',
            'teacher': 'Mr Paul'
        }

        # for jwt_required
        token = create_access_token(identity=admin.username)

        headers = {
            "Authorization": f"Bearer {token}"
        }

        # Create Course
        response = self.client.post('/admin/course', headers=headers, json=data )

        assert response.status_code == 201



        # Get all Courses
        response2 = self.client.get('/admin/courses', headers=headers)

        assert response2.status_code == 200






    def test_admin_courses_by_username_courseName(self):
        admin = Admin(
            username = 'Admin', email = 'admin@gmail.com', password_hash = 'wdwjkhwhewjejwhejw'
        )

        admin.save()

        student = Student(
            username = 'Sam', email = 'sammy@gmail.com', password_hash = 'ahhwdjgfwjqdfewgq'
        )

        student.save()

        regCourse = RegCourse(
            name = 'GSE111', teacher = 'Daniel', student_name = student.username
        )

        regCourse.save()

        # for jwt_required
        token = create_access_token(identity=admin.username)

        headers = {
            "Authorization": f"Bearer {token}"
        }

        # Get a Student's Courses by Username
        response = self.client.get('/admin/student/Sam/courses', headers=headers)

        assert response.status_code == 201




        # Get all Students taking a Course by Course Name
        response2 = self.client.get('/admin/course/GSE111', headers=headers)

        assert response2.status_code == 201

        registeredCourses = RegCourse.query.all()

        assert registeredCourses[0].student_name == student.username




        # Add grade by Student name and Course name
        data = {
            'grade':'B'
        }

        response3 = self.client.put('/admin/student/grade/Sam/GSE111', headers=headers, json=data)
        
        assert response3.status_code == 201

        registeredCourses = RegCourse.query.all()

        assert registeredCourses[0].student_name == 'Sam'
        assert registeredCourses[0].grade == 'B' 



        # Get grade by Student name and Course name
        response4 = self.client.get('/admin/student/grade/Sam/GSE111', headers=headers)
        
        assert response4.status_code == 200


    
        # Calculate GPA by Student Name/Username
        response5 = self.client.put('/admin/student/gpa/Sam', headers=headers)

        assert response5.status_code == 200

        student_sam = Student.query.filter_by(username='Sam').first()

        assert student_sam.GPA == 3








        


        
        

        

        

        



    