from App.database import db
from App.models import Activity, Student
from datetime import datetime
import uuid

def generate_unique_log_id():
    return str(uuid.uuid4())

def create_activity_log(studentID, hours, description):
    """Create a new activity log for a student"""
    logID = generate_unique_log_id()
    new_log = Activity(logID=logID, studentID=studentID, hoursLogged=hours, description=description)
    db.session.add(new_log)
    db.session.commit()
    return new_log

def update_activity_status(logID, newStatus):
    """Update the status of an activity log"""
    activity = Activity.query.filter_by(logID=logID).first()
    if not activity:
        return None
    
    activity.status = newStatus
    db.session.commit()
    return activity

def get_student_activities(studentID):
    """Get all activity logs for a student"""
    return Activity.query.filter_by(studentID=studentID).all()

def get_pending_activities():
    """Get all pending activity logs"""
    return Activity.query.filter_by(status='Pending').all()

def get_activity_by_id(logID):
    """Get activity log by ID"""
    return Activity.query.filter_by(logID=logID).first()

def delete_activity(logID):
    """Delete an activity log"""
    activity = Activity.query.filter_by(logID=logID).first()
    if activity:
        db.session.delete(activity)
        db.session.commit()
        return True
    return False