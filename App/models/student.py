import App
from App.database import db
from .user import User

class Student(User):
    __tablename__ = 'student'
    student_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    studentID = db.Column(db.String(50), unique=True, nullable=True)
    totalHours = db.Column(db.Integer, default=0)
    points = db.Column(db.Integer, default=0)

    # relationships
    requests = db.relationship('Request', backref='student', lazy=True, cascade='all, delete-orphan')
    loggedhours = db.relationship('LoggedHours', backref='student', lazy=True, cascade='all, delete-orphan')
    activities = db.relationship('Activity', backref='student', lazy=True, cascade='all, delete-orphan')
    accolades = db.relationship('Accolade', backref='student', lazy=True, cascade='all, delete-orphan')

    __mapper_args__ = {    
        'polymorphic_identity': 'student',
    }

    def __init__(self, username, email, password):
        super().__init__(username, email, password, role='student')
        self.totalHours = 0
        self.points = 0

    def to_dict(self):
        user_dict = self.get_json()
        user_dict.update({
            'student_id': getattr(self, 'student_id', None),
            'studentID': self.studentID,
            'totalHours': self.totalHours,
            'points': self.points,
        })
        return user_dict