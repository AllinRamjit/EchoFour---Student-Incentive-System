
from App.database import db
from App.models import User,Staff,Student,Request

def register_student(name,email,password):
    newstudent = Student(username=name, email=email, password=password)
    db.session.add(newstudent)
    db.session.commit()
    return newstudent

def get_approved_hours(student_id): #calculates and returns the total approved hours for a student
    student = Student.query.get(student_id)
    if not student:
        raise ValueError(f"Student with id {student_id} not found.")
    
    total_hours = sum(lh.hours for lh in student.loggedhours if lh.status == 'approved')
    return (student.username,total_hours)

def create_hours_request(student_id, hours, activity=None): #creates a new hours request for a student
    from App.models import Request
    student = Student.query.get(student_id)
    if not student:
        raise ValueError(f"Student with id {student_id} not found.")
    
    request = Request(student_id=student.student_id, hours=hours, status='pending', activity=activity)
    db.session.add(request)
    db.session.commit()
    return request

def fetch_requests(student_id): #fetch requests for a student
    student = Student.query.get(student_id)
    if not student:
        raise ValueError(f"Student with id {student_id} not found.")
    
    return student.requests

def fetch_accolades(student_id): #fetch accolades for a student
    student = Student.query.get(student_id)
    if not student:
        raise ValueError(f"Student with id {student_id} not found.")
    
    # Only count approved logged hours
    total_hours = sum(lh.hours for lh in student.loggedhours if lh.status == 'approved')
    accolades = []
    if total_hours >= 10:
        accolades.append('10 Hours Milestone')
    if total_hours >= 25:
        accolades.append('25 Hours Milestone')
    if total_hours >= 50:
        accolades.append('50 Hours Milestone')
    return accolades

def generate_leaderboard():
    students = Student.query.all()
    leaderboard = []
    for student in students:
        total_hours=sum(lh.hours for lh in student.loggedhours if lh.status == 'approved')

        leaderboard.append({
            'name': student.username,
            'hours': total_hours
        })

    leaderboard.sort(key=lambda item: item['hours'], reverse=True)

    return leaderboard

def get_all_students_json():
    students = Student.query.all()
    return [student.get_json() for student in students]

def get_activity_history(student_id):
    """Fetch complete activity history for a student including logged hours and milestones"""
    student = Student.query.get(student_id)
    if not student:
        raise ValueError(f"Student with id {student_id} not found.")
    
    # Get all logged hours sorted by timestamp
    logged_hours = sorted(student.loggedhours, key=lambda x: x.timestamp, reverse=True)
    
    # Calculate cumulative hours and milestones
    activity_history = []
    cumulative_hours = 0
    milestones_achieved = set()
    
    # Process in chronological order to track milestones
    for lh in reversed(logged_hours):
        if lh.status == 'approved':
            cumulative_hours += lh.hours
            
            # Check for new milestones
            new_milestones = []
            if cumulative_hours >= 10 and '10 Hours Milestone' not in milestones_achieved:
                milestones_achieved.add('10 Hours Milestone')
                new_milestones.append('10 Hours Milestone')
            if cumulative_hours >= 25 and '25 Hours Milestone' not in milestones_achieved:
                milestones_achieved.add('25 Hours Milestone')
                new_milestones.append('25 Hours Milestone')
            if cumulative_hours >= 50 and '50 Hours Milestone' not in milestones_achieved:
                milestones_achieved.add('50 Hours Milestone')
                new_milestones.append('50 Hours Milestone')
            
            activity_history.append({
                'type': 'hours_logged',
                'hours': lh.hours,
                'cumulative_hours': cumulative_hours,
                'status': lh.status,
                'timestamp': lh.timestamp.isoformat(),
                'milestones_achieved': new_milestones
            })
    
    # Return in reverse chronological order
    return list(reversed(activity_history))
