from ..utils import db

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique = True)
    teacher = db.Column(db.String(100), nullable=False)
    

    def __repr__(self):
        return f"<Course {self.id}>"


    def save(self):
        db.session.add(self)
        db.session.commit()


class RegCourse(db.Model):
    __tablename__ = 'reg_courses'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    teacher = db.Column(db.String(100), nullable=False)
    grade = db.Column(db.String())
    student_name = db.Column(db.String())
    

    def __repr__(self):
        return f"<Course {self.id}>"


    def save(self):
        db.session.add(self)
        db.session.commit()

    

