from ..utils import db

class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(45), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    is_admin = db.Column(db.Integer(), default=1)
    password_hash = db.Column(db.Text(45), nullable=False)

    def __repr__(self):
        return f"<User {self.name}>"


    def save(self):
        db.session.add(self)
        db.session.commit()

