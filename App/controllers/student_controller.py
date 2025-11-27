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

def create_hours_request(student_id,hours): #creates a new hours request for a student
    from App.models import Request
    student = Student.query.get(student_id)
    if not student:
        raise ValueError(f"Student with id {student_id} not found.")
    
    request = Request(student_id=student.student_id, hours=hours, status='pending')
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
