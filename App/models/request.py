from App.database import db
from datetime import datetime

class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    hours = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, student_id, hours, status='pending', timestamp=None):
        self.student_id = student_id
        self.hours = hours
        self.status = status
        self.timestamp = timestamp if timestamp is not None else datetime.utcnow()

    
    def __repr__(self):
        return f"**RequestID={str(self.id):<5} StudentID={self.student_id:<5} Requested Hours={self.hours:<10} Status={self.status:<5}**"

    def get_json(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'hours': self.hours,
            'status': self.status,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
