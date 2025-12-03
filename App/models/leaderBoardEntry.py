import uuid
from App.database import db

class LeaderBoardEntry(db.Model):
    __tablename__ = 'leaderBoardEntry'

    entryID = db.Column(db.String, primary_key=True)
    studentID = db.Column(db.Integer, db.ForeignKey('student.student_id'))
    rank = db.Column(db.Integer)
    totalHours = db.Column(db.Integer)
    totalAccolades = db.Column(db.Integer)

    def __init__(self, studentID, rank, totalHours, totalAccolades):
        self.entryID = str(uuid.uuid4())
        self.studentID = studentID
        self.rank = rank
        self.totalHours = totalHours
        self.totalAccolades = totalAccolades
    
    def to_dict(self):
        return {
            'entryID': self.entryID,
            'studentID': self.studentID,
            'rank': self.rank,
            'totalHours': self.totalHours,
            'totalAccolades': self.totalAccolades
        }
    
    def updateEntry(self, student):
        self.totalHours = student.totalHours
        self.totalAccolades = len(student.viewAccolades())
    
    def getRank(self):
        return self.rank