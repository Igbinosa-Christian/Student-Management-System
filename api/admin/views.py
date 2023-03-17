from flask import request, abort
from flask_restx import Namespace, Resource, fields
from ..models.admin import Admin
from ..models.courses import Course
from ..models.courses import RegCourse
from ..models.students import Student
from ..models.students import UnverifiedStudent 
from werkzeug.security import generate_password_hash
from http import HTTPStatus  # for server response
from ..utils import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import jsonify



# Namespace is same as blueprint
adminoperation_namespace = Namespace('admin_operations', description='Operations for Admins')

# # For sterialization(creating a student)
student_model = adminoperation_namespace.model(
    'Student', {
        'id': fields.Integer(),
        'username': fields.String(required=True, description='A username'),
        'email': fields.String(required=True, description='An email'),
        'GPA': fields.Float(description='GPA of Student')
    }
)


# # For sterialization(creating a student)
unverifiedstudent_model = adminoperation_namespace.model(
    'UnStudent', {
        'id': fields.Integer(),
        'username': fields.String(required=True, description='A username'),
        'email': fields.String(required=True, description='An email'),
    }
)


# For sterialization(Create Course)
register_course_model = adminoperation_namespace.model(
    'Register_course', {
        'name': fields.String(required=True, description='Course Name'),
        'teacher': fields.String(required=True, description='Course Teacher')
    }
)



# For sterialization(Display Course)
course_model = adminoperation_namespace.model(
    'Course', {
        'name': fields.String(required=True, description='Course Name'),
        'teacher': fields.String(required=True, description='Course Teacher'),
        'grade': fields.String(description='Student Grade on Course'),
        'student_name': fields.String(description='Student Taking Course')
    }
)


# For sterialization(Display Course)
student_course_model = adminoperation_namespace.model(
    'Course', {
        'grade': fields.String(description='Student Grade on Course'),
        'student_name': fields.String(description='Student Taking Course')
    }
)


# For sterialization(Add Grade)
add_grade_model = adminoperation_namespace.model(
    'Grade', {
        'grade': fields.String(description='Student Grade on Course')
    }
)




# For sterialization(Course)
course_get_model = adminoperation_namespace.model(
    'Course', {
        'name': fields.String(required=True, description='Course Name'),
        'teacher': fields.String(required=True, description='Course Teacher'),
    }
)


@adminoperation_namespace.route('/unverified_students')
class GetUnverified(Resource):
    
    # Route To Get all Student Applications(Unverified Students)
    @jwt_required()
    @adminoperation_namespace.marshal_with(unverifiedstudent_model)
    @adminoperation_namespace.doc(
        description="Get all Student Applications(Unverified Students)",
    )
    def get(self):
        """
        Get all Student Applications(Unverified Students)
        
        """
        
        current_user = get_jwt_identity()


        admin = Admin.query.filter_by(username=current_user).first()

        if not admin:
            abort (401, description='Admin Login Required')

        if admin.is_admin==1:
                 
            unverifiedstudents = UnverifiedStudent.query.all()

            return unverifiedstudents, HTTPStatus.OK
        else:
            abort (401, description='Admin Login Required')



@adminoperation_namespace.route('/students')
class GetVerified(Resource):
    
    # Route To Get all Students 
    @jwt_required()
    @adminoperation_namespace.marshal_with(student_model)
    @adminoperation_namespace.doc(
        description="Get all Students",
    )
    def get(self):
        """
        Get all Students 
        
        """
        
        current_user = get_jwt_identity()


        admin = Admin.query.filter_by(username=current_user).first()

        if not admin:
            abort (401, description='Admin Login Required')

        if admin.is_admin==1:
                 
            students = Student.query.all()

            return students, HTTPStatus.OK
        else:
            abort (401, description='Admin Login Required')




@adminoperation_namespace.route('/student/<string:student_name>')
class VerifyDel(Resource):

     # Route To Get a Student by Username
    @jwt_required()
    @adminoperation_namespace.doc(
        description="Get a Student by Username",
    )
    def get(self,student_name):
        """
        Get a Student by Username
        
        """
        
        current_user = get_jwt_identity()


        admin = Admin.query.filter_by(username=current_user).first()

        student = Student.query.filter_by(username=student_name).first()

        if not admin:
            return {'Message':'Admin Login Required'}, HTTPStatus.UNAUTHORIZED

        if admin.is_admin == 1:
            if not student:
                return {'Message':'Student Not Found'}, HTTPStatus.NOT_FOUND

            if student:

                data = {
                    'id': student.id,
                    'Username': student.username,
                    'Email': student.email,
                    'GPA': student.GPA
                }

                return data, HTTPStatus.CREATED
        else:
            return {'Message':'Admin Login Required'}, HTTPStatus.UNAUTHORIZED
            



    # Route To Verify a Student by username
    @jwt_required()
    @adminoperation_namespace.doc(
        description="Verify a Student by username",
    )
    def post(self,student_name):
        """
        Verify a Student by username
        
        """
        
        current_user = get_jwt_identity()


        admin = Admin.query.filter_by(username=current_user).first()

        student = UnverifiedStudent.query.filter_by(username=student_name).first()

        if not admin:
            return {'Message':'Admin Login Required'}, HTTPStatus.UNAUTHORIZED

        if admin.is_admin == 1:
            if not student:
                return {'Message':'Student Application Not Found'}, HTTPStatus.NOT_FOUND

            if student:

                new_student = Student(
                    username = student.username, email = student.email,
                    password_hash = generate_password_hash((student.email)+'5555')
                )
                 
                new_student.save()

                db.session.delete(student)
                db.session.commit()

                return {'Message':'Student Successfully verified and Created'},HTTPStatus.CREATED
        else:
            return {'Message':'Admin Login Required'}, HTTPStatus.UNAUTHORIZED
            

    
    # Route to Delete a Student by Username
    @jwt_required()
    @adminoperation_namespace.doc(
        description="Delete a Student by Username",
    )
    def delete(self,student_name):
        """
        Delete a Student by Username
        
        """

        current_user = get_jwt_identity()

        admin = Admin.query.filter_by(username=current_user).first()

        student = Student.query.filter_by(username=student_name).first()

        if not admin:
            return {'Message':'Admin Login Required'}, HTTPStatus.FORBIDDEN

        if admin.is_admin==1:
            if not student:
                return {'Message':'Student Not Found'}, HTTPStatus.NOT_FOUND
            if student:
                db.session.delete(student)
                db.session.commit()
                return {'Message':'Student Successfully Deleted'}, HTTPStatus.OK
        else:
            return {'Message': 'Admin Login Required'}, HTTPStatus.OK



@adminoperation_namespace.route('/courses')
class GetCourses(Resource):
    
    # Route To Get all Courses 
    @jwt_required()
    @adminoperation_namespace.marshal_with(course_get_model)
    @adminoperation_namespace.doc(
        description="Get all Courses",
    )
    def get(self):
        """
        Get all Courses 
        
        """
        
        current_user = get_jwt_identity()


        admin = Admin.query.filter_by(username=current_user).first()

        if not admin:
            abort (401, description='Admin Login Required')

        if admin.is_admin==1:
                 
            courses = Course.query.all()

            return courses, HTTPStatus.OK
        else:
            abort (401, description='Admin Login Required')



@adminoperation_namespace.route('/course')
class CourseGetRegister(Resource):
    
    # Route To Create a Course
    @jwt_required()
    @adminoperation_namespace.expect(register_course_model)
    @adminoperation_namespace.doc(
        description="Course Creation",
    )
    def post(self):
        """
        Course Creation
        
        """
        
        current_user = get_jwt_identity()


        admin = Admin.query.filter_by(username=current_user).first()

        if not admin:
            return {'Message':'Admin Login Required'}, HTTPStatus.UNAUTHORIZED

        if admin.is_admin==1:
                 
            data = request.get_json()

            course_exist = Course.query.filter_by(name=data.get('name')).first()

            if course_exist:
                return {'Message':'Course Already Exists'}, HTTPStatus.FORBIDDEN
            else:

                new_course = Course(
                    name = data.get('name'), teacher = data.get('teacher')
                )
                 
                new_course.save()

                return {'Message':'Course Successfully created'},HTTPStatus.CREATED
        else:
            return {'Message':'Admin Login Required'}, HTTPStatus.UNAUTHORIZED




@adminoperation_namespace.route('/student/<string:student_name>/courses')
class GetCourses(Resource):

     # Route To Get a Student's Courses by Username 
    @jwt_required()
    @adminoperation_namespace.marshal_with(course_model)
    @adminoperation_namespace.doc(
        description="Get a Student's Courses by Username",
    )
    def get(self,student_name):
        """
        Get a Student's Courses by Username
        
        """
        
        current_user = get_jwt_identity()


        admin = Admin.query.filter_by(username=current_user).first()

        student = Student.query.filter_by(username=student_name).first()

        if not admin:
            abort (401, description='Admin Login Required')

        if admin.is_admin == 1:
            if not student:
                abort (404, description='Student Not Found')

            if student:

                courses = RegCourse.query.filter_by(student_name=student_name).all()

                return courses,HTTPStatus.CREATED
        else:
            abort (401, description='Admin Login Required')




@adminoperation_namespace.route('/course/<string:course_name>')
class GetCourseStudents(Resource):

     # Route To Get all Students taking a Course by Course Name 
    @jwt_required()
    @adminoperation_namespace.marshal_with(student_course_model)
    @adminoperation_namespace.doc(
        description="Get all Students taking a Course by Course Name",
    )
    def get(self,course_name):
        """
        Get all Students taking a Course by Course Name
        
        """
        
        current_user = get_jwt_identity()


        admin = Admin.query.filter_by(username=current_user).first()

        course = RegCourse.query.filter_by(name=course_name).first()

        course_created = Course.query.filter_by(name=course_name).first()

        if not admin:
            abort (401, description='Admin Login Required')

        if admin.is_admin == 1:

            if course:

                courses = RegCourse.query.filter_by(name=course_name).all()

                return courses, HTTPStatus.CREATED
            
            if course_created:
                abort (404, description='No Students are Taking this Course')

            if not course:
                abort (404, description='Course Not Found')
        else:
            abort (401, description='Admin Login Required')
        



@adminoperation_namespace.route('/student/grade/<string:student_name>/<string:course_name>')
class AddGrade(Resource):

    # Route To Add grade by Student name and Course name 
    @jwt_required()
    @adminoperation_namespace.expect(add_grade_model)
    @adminoperation_namespace.doc(
        description="Add grade by Student name and Course name ('A','B','C','D','F')",
    )
    def put(self,student_name,course_name):
        """
        Add grade by Student name and Course name ('A','B','C','D','F')
        
        """
        
        current_user = get_jwt_identity()


        admin = Admin.query.filter_by(username=current_user).first()

        course = RegCourse.query.filter_by(name=course_name).filter_by(student_name=student_name).first()

        if not admin:
            return {'Message':'Admin Login Required'}, HTTPStatus.UNAUTHORIZED

        if admin.is_admin == 1:
            if not course:
                return {'Message':'Course or Student Not Found'}, HTTPStatus.NOT_FOUND

            if course:

                grade_list = ['A','B','C','D','F']

                data = request.get_json()

                grade = (data.get('grade')).upper()

                if grade in grade_list:
                    course.grade = grade

                    db.session.commit()

                    data = {
                        'Course Name': course.name,
                        'Teacher': course.teacher,
                        'Student Name': course.student_name,
                        'Grade': course.grade
                    }

                    return data, HTTPStatus.CREATED
            
                else:
                    return {'Message': 'Invalid Grade Entered'}, HTTPStatus.UNPROCESSABLE_ENTITY
            else:
                return {'Message':'Admin Login Required'}, HTTPStatus.NOT_FOUND
            


    
    # Route To Get Grade by Student name and Course name 
    @jwt_required()
    @adminoperation_namespace.doc(
        description="Get grade by Student name and Course name"
    )
    def get(self,student_name,course_name):
        """
        Get grade by Student name and Course name
        
        """
        
        current_user = get_jwt_identity()


        admin = Admin.query.filter_by(username=current_user).first()

        course = RegCourse.query.filter_by(name=course_name).filter_by(student_name=student_name).first()

        if not admin:
            return {'Message':'Admin Login Required'}, HTTPStatus.UNAUTHORIZED

        if admin.is_admin == 1:
            if not course:
                return {'Message':'Course Grade Not Found - Confirm Student, Course Names and Check if Student is Taking this Course'}, HTTPStatus.NOT_FOUND

            if course:

                data = {
                        'Course Name': course.name,
                        'Teacher': course.teacher,
                        'Student Name': course.student_name,
                        'Grade': course.grade
                    }
    
                return data, HTTPStatus.OK

            else:
                return {'Message':'Course Grade Not Found - Confirm Student, Course Names and Check if Student is Taking this Course'}, HTTPStatus.NOT_FOUND

                



@adminoperation_namespace.route('/student/gpa/<string:student_name>')
class AddGPA(Resource):

    # Route To Calculate GPA by Student Name
    @jwt_required()

    @adminoperation_namespace.doc(
        description="Calculate GPA by Student Name",
    )
    def put(self,student_name):
        """
        Calculate GPA by Student Name
        
        """
        
        current_user = get_jwt_identity()


        admin = Admin.query.filter_by(username=current_user).first()

        courses = RegCourse.query.filter_by(student_name=student_name).all()

        student = Student.query.filter_by(username=student_name).first()


        if not admin:
            return {'Message':'Admin Login Required'}, HTTPStatus.UNAUTHORIZED

        if admin.is_admin == 1:

            if student:

                i=0
                courses_sum = 0
                grade_sum = 0
                for i in range(len(courses)):
                    if courses[i].grade == None:
                        return {'Message':f'Some Courses not graded for {courses[i].student_name}'},HTTPStatus.UNPROCESSABLE_ENTITY
                    else:
                        courses_sum +=1
                        if courses[i].grade == 'A':
                            grade_sum += 4
                            i+=1
                        elif courses[i].grade == 'B':
                            grade_sum += 3
                            i+=1
                        elif courses[i].grade == 'C':
                            grade_sum += 2
                            i+=1
                        elif courses[i].grade == 'D':
                            grade_sum += 1
                            i+=1
                        else:
                            grade_sum += 0
                            i+=1

                gpa = grade_sum/courses_sum

                data = {
                    'GPA': gpa
                }

                student.GPA = gpa
                db.session.commit()

                return jsonify(data)
            else:
                return {'Message':'Student Not Found'}, HTTPStatus.NOT_FOUND

        






                    

            
                