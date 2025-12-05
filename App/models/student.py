from App.database import db
from .user import User


class Student(User):

    _tablename_ = "student"
    student_id = db.Column(db.Integer,
                           db.ForeignKey("users.user_id"),
                           primary_key=True)
    totalHours = db.Column(db.Integer, default=0)
    points = db.Column(db.Integer, default=0)

    loggedhours = db.relationship('LoggedHours',
                                  backref='student',
                                  lazy=True,
                                  cascade="all, delete-orphan")
    requests = db.relationship('Request',
                               backref='student',
                               lazy=True,
                               cascade="all, delete-orphan")

    __mapper_args__ = {"polymorphic_identity": "student"}

    def __init__(self, username, email, password):
        super().__init__(username, email, password, role="student")
        self.totalHours = 0
        self.points = 0

    @property
    def studentID(self):
        """Property for backward compatibility with studentID naming convention."""
        return self.student_id

    def __repr__(self):
        return f"[Student ID= {str(self.student_id):<3}  Name= {self.username:<10} Email= {self.email}]"

    def get_json(self):
        return {
            'student_id': self.student_id,
            'username': self.username,
            'email': self.email,
            'totalHours': self.totalHours,
            'points': self.points
        }

    def to_dict(self):
        return {
            'student_id': self.student_id,
            'studentID': self.student_id,  # For backward compatibility
            'username': self.username,
            'email': self.email,
            'totalHours': self.totalHours,
            'points': self.points,
            'role': self.role
        }

