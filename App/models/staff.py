from App.database import db
from .user import User


class Staff(User):
    __tablename__ = 'staff'

    staff_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    staffID = db.Column(db.String(50), unique=True, nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': 'staff',
    }

    def __init__(self, username, email, password):
        super().__init__(username, email, password, role='staff')

    def to_dict(self):
        user_dict = self.get_json()
        user_dict.update({
            'staff_id': getattr(self, 'staff_id', None),
            'staffID': self.staffID,
        })
        return user_dict