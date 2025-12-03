# Remove the class methods from Accolade model
from App.database import db
from datetime import datetime
from sqlalchemy import String

class Accolade(db.Model):
    __tablename__ = 'accolade'
    accoladeID = db.Column(db.String, primary_key=True)
    studentID = db.Column(db.Integer, db.ForeignKey('student.student_id'))
    name = db.Column(db.String)
    milestoneHours = db.Column(db.Integer)
    dateAwarded = db.Column(db.DateTime)

    def __init__(self, accoladeID, studentID, name, milestoneHours, dateAwarded=None):
        self.accoladeID = accoladeID
        self.studentID = studentID
        self.name = name
        self.milestoneHours = milestoneHours
        self.dateAwarded = dateAwarded if dateAwarded else datetime.utcnow()

    def to_dict(self):
        return {
            'accoladeID': self.accoladeID,
            'studentID': self.studentID,
            'name': self.name,
            'milestoneHours': self.milestoneHours,
            'dateAwarded': self.dateAwarded.isoformat() if self.dateAwarded else None
        }