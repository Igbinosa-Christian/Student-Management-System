from flask import request
from flask_restx import Namespace, Resource, fields
from ..models.admin import Admin
from ..models.courses import Course
from ..models.students import Student
from ..models.students import UnverifiedStudent
from werkzeug.security import check_password_hash, generate_password_hash
from http import HTTPStatus  # for server response
from ..utils import db
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from ..utils.blocklist import BLOCKLIST



# Namespace is same as blueprint
admin_namespace = Namespace('admin', description='Auth for Admin')


# For sterialization(creating an admin)
admin_signup_model = admin_namespace.model(
    'Register', {
        'username': fields.String(required=True, description='A username'),
        'email': fields.String(required=True, description='An email'),
        'password': fields.String(required=True, description='A password')
    }
)

# For sterialization(Login)
admin_login_model = admin_namespace.model(
    'Login', {
        'email': fields.String(required=True, description='An email'),
        'password': fields.String(required=True, description='A password'),
    }
)



# Route to Create an Admin
@admin_namespace.route('/adminsignup')
class SignUp(Resource):

    @admin_namespace.expect(admin_signup_model)
    @admin_namespace.doc(
        description="Create an Admin"
    )
    def post(self):
        """
        Create a admin
        
        """
        data = request.get_json()

        new_admin = Admin(
            username=data.get('username'), email=data.get('email'),
            password_hash=generate_password_hash(data.get('password'))
        )

       
        new_admin.save()

        return {'Message': 'Admin Successfully Created'}, HTTPStatus.CREATED



# Route to Log in an Admin
@admin_namespace.route('/adminlogin')
class LogIn(Resource):

    @admin_namespace.expect(admin_login_model)
    @admin_namespace.doc(
        description="Login an Admin"
    )
    def post(self):
        """
        Login an admin
        
        """
        data = request.get_json()

        email = data.get('email')
        password = data.get('password')

        my_admin = Admin.query.filter_by(email=email).first()

        if not my_admin:
            return {'Message': 'Admin Not Found'}

        if my_admin and check_password_hash(my_admin.password_hash, password):
            access_token = create_access_token(identity=my_admin.username)
            refresh_token = create_refresh_token(identity=my_admin.username)


            response = {
                'access_token': access_token,
                'refresh_token': refresh_token
            }

            return response, HTTPStatus.CREATED 

        else:
            return {'Message':'Incorrect Password'}




# To create a new token with same admin identity
@admin_namespace.route('/refresh')
class RefreshAdmin(Resource):

    @jwt_required(refresh=True)
    def post(self):
        admin_username = get_jwt_identity()

        access_token = create_access_token(identity=admin_username)

        return {'access_token': access_token}, HTTPStatus.OK
    



@admin_namespace.route('/logout')
class AdminLogout(Resource):


    @jwt_required(verify_type=False)
    def post(self):
        token = get_jwt()
        jti = token["jti"]
        BLOCKLIST.add(jti)
       

        return {'Message': 'Token Successfully revoked'}
 








