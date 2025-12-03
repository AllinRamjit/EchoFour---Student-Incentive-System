from App.database import db
from App.models import User, Staff, Student, Request, Activity
from App.controllers.activity_controller import update_activity_status

def confirm_hours(activityLogID):
    """Staff confirms hours for an activity"""
    activity = Activity.query.filter_by(logID=activityLogID).first()
    if not activity:
        return None
    
    # Update activity status
    updated_activity = update_activity_status(activityLogID, 'Confirmed')
    
    # Update student's total hours
    student = Student.query.get(activity.studentID)
    if student:
        student.totalHours += activity.hoursLogged
        db.session.commit()

    return updated_activity

def reject_hours(activityLogID):
    """Staff rejects hours for an activity"""
    return update_activity_status(activityLogID, 'Rejected')

def log_hours_for_student(staff_id, studentID, hours, description):
    """Staff logs hours for a student"""
    from App.controllers.activity_controller import create_activity_log
    activity = create_activity_log(studentID, hours, description)
    
    # Automatically confirm if staff is logging
    confirm_hours(activity.logID)
    
    return activity

def view_leaderboard():
    """View leaderboard of students by total hours"""
    from App.models import LeaderBoardEntry
    
    students = Student.query.order_by(Student.totalHours.desc()).all()
    
    leaderboard = []
    for rank, student in enumerate(students, 1):
        # Create or update leaderboard entry
        entry = LeaderBoardEntry.query.filter_by(studentID=student.student_id).first()
        if not entry:
            entry = LeaderBoardEntry(
                studentID=student.student_id,
                rank=rank,
                totalHours=student.totalHours,
                totalAccolades=0  # You'll need to calculate this
            )
            db.session.add(entry)
        else:
            entry.rank = rank
            entry.totalHours = student.totalHours
        
        leaderboard.append(entry.to_dict())
    
    db.session.commit()
    return leaderboard


def get_all_staff_json():
    staffs = Staff.query.all()
    return [s.get_json() for s in staffs]


def register_staff(name, email, password):
    # prevent duplicate username or email
    existing = User.query.filter((User.username == name) | (User.email == email)).first()
    if existing:
        raise ValueError("User with that username or email already exists")

    newstaff = Staff(username=name, email=email, password=password)
    db.session.add(newstaff)
    db.session.commit()
    return newstaff


def fetch_all_requests():
    from App.models import Request
    pending = Request.query.filter_by(status='pending').all()
    return [r.get_json() for r in pending]


def process_request_approval(staff_user_id, request_id):
    from App.models import Request, LoggedHours

    staff = Staff.query.get(staff_user_id)
    if not staff:
        raise ValueError(f"Staff with id {staff_user_id} not found.")

    req = Request.query.get(request_id)
    if not req:
        raise ValueError(f"Request with id {request_id} not found.")

    if req.status != 'pending':
        raise ValueError("Request already processed")

    # create logged hours
    logged = LoggedHours(student_id=req.student_id, staff_id=staff_user_id, hours=req.hours, status='approved')
    db.session.add(logged)

    req.status = 'approved'
    db.session.commit()

    return {'request': req, 'logged_hours': logged}


def process_request_denial(staff_user_id, request_id):
    from App.models import Request

    staff = Staff.query.get(staff_user_id)
    if not staff:
        raise ValueError(f"Staff with id {staff_user_id} not found.")

    req = Request.query.get(request_id)
    if not req:
        raise ValueError(f"Request with id {request_id} not found.")

    if req.status != 'pending':
        raise ValueError("Request already processed")

    req.status = 'denied'
    db.session.commit()

    return {'denial_successful': True, 'request': req}