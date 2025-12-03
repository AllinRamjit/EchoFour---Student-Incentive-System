from App.database import db
from App.models import Student, Request, Activity, Accolade, User, Staff
from App.controllers.activity_controller import get_student_activities
from App.controllers.accolade_controller import get_student_accolades
import uuid

def request_confirmation_of_hours(studentID, activityLogID):
    """Student requests confirmation for logged hours"""
    from App.controllers.activity_controller import update_activity_status
    return update_activity_status(activityLogID, 'Pending')

def get_activity_history(student_id):
    """Fetch complete activity history for a student"""
    student = Student.query.get(student_id)
    if not student:
        raise ValueError(f"Student with id {student_id} not found.")
    
    # Get activities using the relationship
    activities = student.activities if hasattr(student, 'activities') else Activity.query.filter_by(studentID=student_id).all()
    
    # Return activities as dicts
    return [activity.to_dict() for activity in activities]

def register_student(name, email, password):
    # prevent duplicate username or email
    existing = User.query.filter((User.username == name) | (User.email == email)).first()
    if existing:
        raise ValueError("User with that username or email already exists")

    newstudent = Student(username=name, email=email, password=password)
    db.session.add(newstudent)
    db.session.commit()
    return newstudent

def get_approved_hours(student_id):
    """calculates and returns the total approved hours for a student"""
    student = Student.query.get(student_id)
    if not student:
        raise ValueError(f"Student with id {student_id} not found.")
    
    total_hours = sum(lh.hours for lh in student.loggedhours if lh.status == 'approved')
    return (student.username, total_hours)

def create_hours_request(student_id, hours):
    """creates a new hours request for a student"""
    student = Student.query.get(student_id)
    if not student:
        raise ValueError(f"Student with id {student_id} not found.")
    
    request = Request(student_id=student.student_id, hours=hours, status='pending')
    db.session.add(request)
    db.session.commit()
    return request

def fetch_requests(student_id):
    """fetch requests for a student"""
    student = Student.query.get(student_id)
    if not student:
        raise ValueError(f"Student with id {student_id} not found.")
    
    return student.requests

def fetch_accolades(student_id):
    """fetch accolades for a student"""
    student = Student.query.get(student_id)
    if not student:
        raise ValueError(f"Student with id {student_id} not found.")
    
    # Get actual accolades from database using relationship
    accolades = Accolade.query.filter_by(studentID=student_id).all()
    return [accolade.to_dict() for accolade in accolades]

def generate_leaderboard():
    students = Student.query.all()
    leaderboard = []
    for student in students:
        total_hours = sum(lh.hours for lh in student.loggedhours if lh.status == 'approved')

        leaderboard.append({
            'name': student.username,
            'hours': total_hours
        })

    leaderboard.sort(key=lambda item: item['hours'], reverse=True)

    return leaderboard

def get_all_students_json():
    students = Student.query.all()
    return [student.get_json() for student in students]
