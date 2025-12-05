from App.database import db
from App.models import User,Staff,Student,Request

def register_staff(name,email,password): #registers a new staff member
    newstaff = Staff(username=name, email=email, password=password)
    db.session.add(newstaff)
    db.session.commit()
    return newstaff

def fetch_all_requests(): #fetches all pending requests for staff to review
    pending_requests = Request.query.filter_by(status='pending').all()
    if not pending_requests:
        return []
    
    requests_data=[]
    for req in pending_requests:
        student = Student.query.get(req.student_id)
        student_name = student.username if student else "Unknown"
        
        requests_data.append({
            'id': req.id,
            'student_name': student_name,
            'hours': req.hours,
            'status':req.status
        })
    
    return requests_data

def process_request_approval(staff_id, request_id): #staff approves a student's hours request
    from App.models import LoggedHours
    staff = Staff.query.get(staff_id)
    if not staff:
        raise ValueError(f"Staff with id {staff_id} not found.")
    
    request = Request.query.get(request_id)
    if not request:
        raise ValueError(f"Request with id {request_id} not found.")
    
    if request.status != 'pending':
        raise ValueError(f"Request {request_id} is not pending.")
    
    student = Student.query.get(request.student_id)
    name = student.username if student else "Unknown"
    
    # Mark request as approved
    request.status = 'approved'
    # Create a LoggedHours entry
    logged = LoggedHours(student_id=request.student_id, staff_id=staff.staff_id, hours=request.hours, status='approved')
    db.session.add(logged)
    db.session.commit()

    return {
        'request': request,
        'student_name': name,
        'staff_name': staff.username,
        'logged_hours': logged
    }

def process_request_denial(staff_id, request_id): #staff denies a student's hours request
    staff = Staff.query.get(staff_id)
    if not staff:
        raise ValueError(f"Staff with id {staff_id} not found.")
    
    request = Request.query.get(request_id)
    if not request:
        raise ValueError(f"Request with id {request_id} not found.")
    
    if request.status != 'pending':
        raise ValueError(f"Request {request_id} is not pending.")
    
    student = Student.query.get(request.student_id)
    name = student.username if student else "Unknown"
    
    request.status = 'denied'
    db.session.commit()
    
    return {
        'request': request,
        'student_name': name,
        'staff_name': staff.username,
        'denial_successful': True
    }
    
def get_all_staff_json(): #returns all staff members in JSON format
    staff_members = Staff.query.all()
    return [staff.get_json() for staff in staff_members]