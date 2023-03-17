from flask import request
from flask_restx import Namespace, Resource, fields
from ..models.students import Student
from ..models.students import UnverifiedStudent
from werkzeug.security import check_password_hash, generate_password_hash
from http import HTTPStatus  # for server response
from ..utils import db
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from ..utils.blocklist import BLOCKLIST



# Namespace is same as blueprint
student_namespace = Namespace('student', description='Auth for students')


# For sterialization(creating a student)
signup_model = student_namespace.model(
    'Signup', {
        'username': fields.String(required=True, description='A username'),
        'email': fields.String(required=True, description='An email')
    }
)

# For sterialization(Login)
login_model = student_namespace.model(
    'Login', {
        'email': fields.String(required=True, description='An email'),
        'password': fields.String(required=True, description='A password'),
    }
)

# For Udate Password(Login)
update_model = student_namespace.model(
    'Update_password', {
        'old_password': fields.String(required=True, description='Old Password'),
        'new_password': fields.String(required=True, description='A password'),
    }
)


# Route to Create a Student
@student_namespace.route('/signup')
class SignUp(Resource):

    @student_namespace.expect(signup_model)
    @student_namespace.doc(
        description="Apply as a student"
    )
    def post(self):
        """
        Apply as a Student
        
        """
        data = request.get_json()

        new_student = UnverifiedStudent(
            username=data.get('username'), email=data.get('email')
        )

       
        new_student.save()

        return {'Message': 'Application Successfully Sent'}, HTTPStatus.CREATED



# Route to Log in a Student
@student_namespace.route('/login')
class LogIn(Resource):

    @student_namespace.expect(login_model)
    @student_namespace.doc(
        description="Login a Student"
    )
    def post(self):
        """
        Login a Student
        
        """
        data = request.get_json()

        email = data.get('email')
        password = data.get('password')

        my_student = Student.query.filter_by(email=email).first()

        unverified = UnverifiedStudent.query.filter_by(email=email).first()

        if unverified:
            return {'Message': 'Student Not Yet Verified'}, HTTPStatus.FORBIDDEN

        if not my_student:
            return {'Message': 'Student Not Found'}, HTTPStatus.NOT_FOUND

        if my_student and check_password_hash(my_student.password_hash, password):
            access_token = create_access_token(identity=my_student.username)
            refresh_token = create_refresh_token(identity=my_student.username)


            response = {
                'access_token': access_token,
                'refresh_token': refresh_token
            }

            return response, HTTPStatus.CREATED 

        else:
            return {'Message':'Incorrect Password'}, HTTPStatus.FORBIDDEN



@student_namespace.route('/profile')
class StudentGet(Resource):

    # Route to View Current Student
    @jwt_required()
    @student_namespace.doc(
        description="View Current Student",
    )
    def get(self):
        """
        View Current Student
        
        """

        current_student = get_jwt_identity()

        student = Student.query.filter_by(username=current_student).first()

        if not student:
            return {'Message':'Student Not Found'},HTTPStatus.NOT_FOUND
        else:
             data = {
                    'id': student.id,
                    'Username': student.username,
                    'Email': student.email,
                    'GPA': student.GPA
                }
             
             return data, HTTPStatus.OK

        
       



# Route to Update Password
@student_namespace.route('/update_password')
class LogIn(Resource):

    @jwt_required()
    @student_namespace.expect(update_model)
    @student_namespace.doc(
        description="Update Current Student Password"
    )
    def put(self):
        """
        Update Current Student Password
        
        """
        current_student = get_jwt_identity()

        student = Student.query.filter_by(username=current_student).first()

        if student and student.is_admin==0:

            data = request.get_json()

            old_password = data.get('old_password')

            if check_password_hash(student.password_hash, old_password):
                student.password_hash = generate_password_hash(data.get('new_password'))

                db.session.commit()

                return {'Message': 'Password Successfully updated'}, HTTPStatus.OK
            else:
                return {'Message': 'Incorrect Password'}, HTTPStatus.NOT_FOUND
        else:
            return {'Message': 'Not Allowed'}, HTTPStatus.FORBIDDEN

            
       



# To create a new token with same identity
@student_namespace.route('/refresh')
class Refresh(Resource):

    @jwt_required(refresh=True)
    def post(self):
        student_username = get_jwt_identity()

        access_token = create_access_token(identity=student_username)

        return {'access_token': access_token}, HTTPStatus.OK
    



@student_namespace.route('/logout')
class StudentLogout(Resource):


    @jwt_required(verify_type=False)
    def post(self):
        token = get_jwt()
        jti = token["jti"]
        BLOCKLIST.add(jti)
       

        return {'Message': 'Token Successfully revoked'}
 
