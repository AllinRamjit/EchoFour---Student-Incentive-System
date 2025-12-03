from App.database import db
from datetime import datetime

class Activity(db.Model):
    logID = db.Column(db.String, primary_key=True)
    studentID = db.Column(db.Integer, db.ForeignKey('student.student_id'))
    hoursLogged = db.Column(db.Integer)
    dateLogged = db.Column(db.DateTime)
    status = db.Column(db.String)  # (Logged, Pending, Confirmed, Rejected)
    description = db.Column(db.String)

    def __init__(self, logID, studentID, hoursLogged, dateLogged=None, status='Pending', description=''):
        self.logID = logID
        self.studentID = studentID
        self.hoursLogged = hoursLogged
        self.dateLogged = dateLogged if dateLogged else datetime.utcnow()
        self.status = status
        self.description = description

    def to_dict(self):
        return {
            'logID': self.logID,
            'studentID': self.studentID,
            'hoursLogged': self.hoursLogged,
            'dateLogged': self.dateLogged.isoformat() if self.dateLogged else None,
            'status': self.status,
            'description': self.description
        }
    
    def getHoursLogged(self) -> int:
        return self.hoursLogged
    
    def getDescription(self) -> str:
        return self.description