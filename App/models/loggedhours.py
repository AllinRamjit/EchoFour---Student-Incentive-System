from App.database import db
from datetime import datetime

class LoggedHours(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.staff_id'), nullable=True)
    hours = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='approved')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, student_id, staff_id, hours, status='approved', timestamp=None):
        self.student_id = student_id
        self.staff_id = staff_id
        self.hours = hours
        self.status = status
        self.timestamp = timestamp if timestamp is not None else datetime.utcnow()

    def __repr__(self):
        return f"[Log ID={self.id} StudentID ={self.student_id} Approved By (StaffID)={self.staff_id} Hours Approved={self.hours}]"

    def get_json(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'staff_id': self.staff_id,
            'hours': self.hours,
            'status': self.status,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }