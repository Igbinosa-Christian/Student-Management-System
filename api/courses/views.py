from flask_restx import Namespace, Resource, fields
from ..models.courses import Course
from http import HTTPStatus
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.students import Student
from ..models.admin import Admin
from ..models.courses import RegCourse
from ..models.courses import Course
from ..utils import db
from flask import request


# Namespace is same as blueprint(smorest)
course_namespace = Namespace('course', description='Operations on courses(Logged In Student)')



# For sterialization(Create Course)
register_course_model = course_namespace.model(
    'Register_course', {
        'name': fields.String(required=True, description='Course Name'),
        'teacher': fields.String(required=True, description='Course Teacher')
    }
)



# For sterialization(Display Course)
course_model = course_namespace.model(
    'Course', {
        'name': fields.String(required=True, description='Course Name'),
        'teacher': fields.String(required=True, description='Course Teacher'),
        'grade': fields.String(description='Student Grade on Course'),
        'student_name': fields.String(required=True, description='Student Taking Course')
    }
)




@course_namespace.route('/courses')
class CourseGet(Resource):

    # Route to Get Current Student's Courses
    @jwt_required()
    @course_namespace.marshal_with(course_model)
    @course_namespace.doc(
        description="Get Current Student's Courses",
    )
    def get(self):
        """
        Get Current Student's Courses
        
        """

        current_student = get_jwt_identity()

        courses = RegCourse.query.filter_by(student_name=current_student).all()

        
        return courses, HTTPStatus.OK
            
    

# Course by name
@course_namespace.route('/course/<string:course_name>')
class CourseGetDelete(Resource):

    # Route to Get Current Student's Course by course name
    @jwt_required()
    @course_namespace.doc(
        description="Get Current Student's Course by course name",
    )
    def get(self,course_name):
        """
        Get Current Student's Course by course name
        
        """

        current_student = get_jwt_identity()

        course = RegCourse.query.filter_by(name=course_name).filter_by(student_name=current_student).first()

        if not course:
            return {'Message':'Course Not Found'}, HTTPStatus.NOT_FOUND

        if course:

            data = {
                        'Course Name': course.name,
                        'Teacher': course.teacher,
                        'Student Name': course.student_name,
                        'Grade': course.grade
                    }
            
            return data, HTTPStatus.OK                
        



    # Route to Register a Course by Course Name
    @jwt_required()
    @course_namespace.doc(
        description="Register a Course by Course Name",
    )
    def post(self,course_name):
        """
        Register a Course by Course Name
        
        """

        current_student = get_jwt_identity()

        check_user = Student.query.filter_by(username=current_student).first()

        course = Course.query.filter_by(name=course_name).first()

        if not course:
            return {'Message':'Course Not Found'}, HTTPStatus.NOT_FOUND
        
        
        if check_user.is_admin==0:
            if course:
                course_exist = RegCourse.query.filter_by(name=course_name).filter_by(student_name=current_student).first()

                if course_exist:
                    return {'Message':'Course Already Registered'}
                else:
                    reg_course = RegCourse(
                        name = course.name, teacher = course.teacher, student_name = current_student
                    )

                    reg_course.save()

                    return {'Message': 'Course Registered'}, HTTPStatus.CREATED


    
    # Route to Unregister Current Student's Course by Course Name
    @jwt_required()
    @course_namespace.doc(
        description="Unregister Current Student's Course by Course Name",
    )
    def delete(self,course_name):
        """
        Unregister Current Student's Course by Course Name
        
        """

        current_student = get_jwt_identity()

        student = Student.query.filter_by(username=current_student).first()

        course = RegCourse.query.filter_by(name=course_name).filter_by(student_name=current_student).first()

        if course and student.is_admin==0:
            db.session.delete(course)
            db.session.commit()
            return {'Message': 'UnRegistered'}, HTTPStatus.OK
        
        if not course:
            return {'Message': 'Student not Registered to Course or Course does not exist'}, HTTPStatus.NOT_FOUND


    

