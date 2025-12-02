import App
from App.database import db
from App.models import activity
from App.models.activity import Activity
from .user import User

class Student(User):

    _tablename_ = "student"
    student_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), primary_key=True)

    #relationship to LoggedHours and Request both One-to-Many
    loggedhours = db.relationship('LoggedHours', backref='student', lazy=True, cascade="all, delete-orphan")
    requests = db.relationship('Request', backref='student', lazy=True, cascade="all, delete-orphan")

    #Inheritance setup
    __mapper_args__ = {
        "polymorphic_identity": "student"
    }
    #calls parent constructor
    def __init__(self, username, email, password):
        super().__init__(username, email, password, role="student")

    def __repr__(self):
        return f"[Student ID= {str(self.student_id):<3}  Name= {self.username:<10} Email= {self.email}]"

    def get_json(self):
        return{
            'student_id': self.student_id,
            'username': self.username,
            'email': self.email
        }
    
    def get_activity_history(self):
        return activity.Activity.query.filter_by(student_id=self.student_id).order_by(activity.Activity.timestamp.desc()).all()

    def add_activity(self, activity_type, description, points=0):
        activity = activity.Activity(
            student_id=self.student_id,
            activity_type=activity_type,
            description=description,
            points=points
        )
        db.session.add(activity)
        db.session.commit()
