from App.database import db
from .user import User

class Staff(User):

    _tablename_ = "staff"
    staff_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), primary_key=True)

    #relationaship to LoggedHours
    loggedhours = db.relationship('LoggedHours', backref='staff', lazy=True, cascade="all, delete-orphan")

    #Inheritance, Staff is a child of User
    __mapper_args__ = {
        "polymorphic_identity": "staff"
    }
    #calls parent constructor
    def __init__(self, username, email, password):
        super().__init__(username, email, password, role="staff")

    def __repr__(self):
        return f"[Staff ID= {str(self.staff_id):<3} Name= {self.username:<10} Email= {self.email}]"

    def get_json(self):
        return{
            'staff_id': self.staff_id,
            'username': self.username,
            'email': self.email
        }

