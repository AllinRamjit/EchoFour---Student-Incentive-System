from App.database import db
from datetime import datetime

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)  # 'hours_earned', 'milestone', 'accolade'
    description = db.Column(db.String(500))
    points = db.Column(db.Float, default=0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, student_id, activity_type, description, points=0):
        self.student_id = student_id
        self.activity_type = activity_type
        self.description = description
        self.points = points
    
    def get_json(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'activity_type': self.activity_type,
            'description': self.description,
            'points': self.points,
            'timestamp': self.timestamp.isoformat()
        }