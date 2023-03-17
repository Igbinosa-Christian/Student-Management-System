from flask import Flask
from flask_restx import Api
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from .config.config import config_dict
from .utils import db
from .models.admin import Admin
from .models.students import Student
from .models.courses import Course
from .admin.auth import admin_namespace
from .students.views import student_namespace
from .courses.views import course_namespace
from .admin.views import adminoperation_namespace
from .utils.blocklist import BLOCKLIST
from http import HTTPStatus

def create_app(config=config_dict['dev']):
    app = Flask(__name__)

    # to configure our app to use dev/prod/test
    app.config.from_object(config)

    # to initialize our database
    db.init_app(app)

    # to manage our JWT
    jwt = JWTManager(app)


    # Decorator to check if token has been revoked
    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload['jti'] in BLOCKLIST
    

    # Decorator to return message if token has been revoked
    @jwt.revoked_token_loader
    def revoke_token_callback(jwt_header, jwt_payload):
        return(
            {
                'Description': 'User has been logged out',
                'error': 'token revoked'
            },
            401
        )
    

    # For JWT Token
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {
            "message": "Token has Expired",
            "error": "token_expired"
        }, HTTPStatus.UNAUTHORIZED
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {
            "message": "Token Verification Failed",
            "error": "invalid_token"
        }, HTTPStatus.UNAUTHORIZED
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return {
            "message": "Missing Access Token",
            "error": "authorization_required"
        }, HTTPStatus.UNAUTHORIZED
    
    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback():
        return {
            "message": "The token is not fresh",
            "error": "fresh_token_required"
        }, HTTPStatus.UNAUTHORIZED
    
    

    # to allow easy update of database
    migrate = Migrate(app, db)

    
    # Create field to input JWT Required(Bearer Token)
    authorizations = {
        "Bearer Auth":{
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Add a JWT token to the header for JWT Authoriation by doing Bearer JWT TOKEN"
        }
    }

    # Usually api=Api(app); other details are Swagger UI documentation
    api = Api(app,
              title= 'Student Mangement System',
              description= 'A Student Mangement System made with Python Restx API',
              authorizations=authorizations,
              security='Bearer Auth'
    )

    # Register namespaces
    api.add_namespace(admin_namespace, path='/admin')
    api.add_namespace(student_namespace, path='/student')
    api.add_namespace(course_namespace, path='/student')
    api.add_namespace(adminoperation_namespace, path='/admin')



    # to allow us connect to the database to create and do migration in the shell
    @app.shell_context_processor
    def make_shell_context():
        return {
            'db': db,
            'Student': Student,
            'Course': Course,
            'Admin': Admin
        }

         # do flask shell after creating this in the terminal
         # do db.create_all()

    return app