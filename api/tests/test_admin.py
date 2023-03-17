
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



    