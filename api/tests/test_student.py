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



        

    
    