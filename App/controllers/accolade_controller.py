from App.database import db
from App.models import Accolade, Student
from datetime import datetime
import uuid

def generate_unique_accolade_id():
    return str(uuid.uuid4())

def create_accolade(name, milestone):
    """Create a new accolade template"""
    accoladeID = generate_unique_accolade_id()
    new_accolade = Accolade(accoladeID=accoladeID, studentID=None, name=name, milestoneHours=milestone)
    db.session.add(new_accolade)
    db.session.commit()
    return new_accolade

def award_accolade(studentID, accoladeID):
    """Award an existing accolade to a student"""
    accolade = Accolade.query.filter_by(accoladeID=accoladeID).first()
    if not accolade:
        return None
    
    accolade.studentID = studentID
    accolade.dateAwarded = datetime.utcnow()
    db.session.commit()
    return accolade

def get_student_accolades(student_id):
    """Get all accolades for a specific student"""
    return Accolade.query.filter_by(studentID=student_id).all()

def get_all_accolades():
    """Get all accolades (both awarded and template)"""
    return Accolade.query.all()

def delete_accolade(accoladeID):
    """Delete an accolade"""
    accolade = Accolade.query.filter_by(accoladeID=accoladeID).first()
    if accolade:
        db.session.delete(accolade)
        db.session.commit()
        return True
    return False