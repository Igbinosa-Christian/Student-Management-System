from ..utils import db

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(45), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.Text(45), nullable=False)
    GPA = db.Column(db.Float())
    is_admin = db.Column(db.Integer(), default=0)

    def __repr__(self):
        return f"<User {self.username}>"


    def save(self):
        db.session.add(self)
        db.session.commit()


class UnverifiedStudent(db.Model):
    __tablename__ = 'unverifiedstudents'
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(45), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)

    def __repr__(self):
        return f"<User {self.username}>"


    def save(self):
        db.session.add(self)
        db.session.commit()

