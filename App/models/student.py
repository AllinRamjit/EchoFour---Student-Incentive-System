from App.database import db
from .user import User

class Student(User):

    _tablename_ = "student"
    student_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), primary_key=True)

    #relationship to LoggedHours and Request both One-to-Many
    loggedhours = db.relationship('LoggedHours', backref='student', lazy=True, cascade="all, delete-orphan")
    requests = db.relationship('Request', backref='student', lazy=True, cascade="all, delete-orphan")

    #Inheritance setup
    _mapper_args_ = {
        "polymorphic_identity": "student"
    }
    #calls parent constructor
    def _init_(self, username, email, password):
       super()._init_(username, email, password, role="student")

    def _repr_(self):
        return f"[Student ID= {str(self.student_id):<3}  Name= {self.username:<10} Email= {self.email}]"

    def get_json(self):
        return{
            'student_id': self.student_id,
            'username': self.username,
            'email': self.email
        }
