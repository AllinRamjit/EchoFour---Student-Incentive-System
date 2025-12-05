from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user as jwt_current_user
from App.models import Student, Request, LoggedHours
from App.controllers.student_controller import get_all_students_json, fetch_accolades, create_hours_request, generate_leaderboard
from App.controllers.staff_controller import process_request_approval, process_request_denial, fetch_all_requests
from App.controllers.session_auth import staff_required, get_current_user
from App import db

staff_views = Blueprint('staff_views', __name__, template_folder='../templates')


def get_next_milestone(hours):
    milestones = [10, 25, 50, 100]
    for m in milestones:
        if hours < m:
            return m
    return milestones[-1]


@staff_views.route('/staff/dashboard', methods=['GET'])
@staff_required
def staff_dashboard():
    user = get_current_user()
    
    pending_requests = fetch_all_requests()
    for req in pending_requests:
        r = Request.query.get(req['id'])
        if r:
            req['timestamp'] = r.timestamp.strftime('%Y-%m-%d %H:%M')
    
    return render_template('staff/dashboard.html',
        pending_requests=pending_requests,
        pending_count=len(pending_requests)
    )


@staff_views.route('/staff/log-hours', methods=['GET', 'POST'])
@staff_required
def staff_log_hours():
    user = get_current_user()
    
    if request.method == 'POST':
        student_id = request.form.get('student_id', type=int)
        hours = request.form.get('hours', type=float)
        
        if not student_id or not hours:
            flash('Please fill all fields', 'error')
            return redirect(url_for('staff_views.staff_log_hours'))
        
        try:
            logged = LoggedHours(student_id=student_id, staff_id=user.staff_id, hours=hours, status='approved')
            db.session.add(logged)
            db.session.commit()
            flash(f'Successfully logged {hours} hours!', 'success')
            return redirect(url_for('staff_views.staff_dashboard'))
        except Exception as e:
            flash(f'Error logging hours: {str(e)}', 'error')
    
    students = Student.query.all()
    return render_template('staff/log_hours.html', students=students)


@staff_views.route('/staff/requests', methods=['GET'])
@staff_required
def staff_requests():
    pending_requests = fetch_all_requests()
    for req in pending_requests:
        r = Request.query.get(req['id'])
        if r:
            req['timestamp'] = r.timestamp.strftime('%Y-%m-%d %H:%M')
    
    return render_template('staff/requests.html',
        pending_requests=pending_requests,
        selected_request=None
    )


@staff_views.route('/staff/request/<int:request_id>', methods=['GET'])
@staff_required
def staff_request_detail(request_id):
    req = Request.query.get(request_id)
    if not req:
        flash('Request not found', 'error')
        return redirect(url_for('staff_views.staff_requests'))
    
    student = Student.query.get(req.student_id)
    selected_request = {
        'id': req.id,
        'student_name': student.username if student else 'Unknown',
        'hours': req.hours,
        'timestamp': req.timestamp.strftime('%Y-%m-%d %H:%M'),
        'status': req.status
    }
    
    pending_requests = fetch_all_requests()
    for r in pending_requests:
        req_obj = Request.query.get(r['id'])
        if req_obj:
            r['timestamp'] = req_obj.timestamp.strftime('%Y-%m-%d %H:%M')
    
    return render_template('staff/requests.html',
        pending_requests=pending_requests,
        selected_request=selected_request
    )


@staff_views.route('/staff/approve/<int:request_id>', methods=['POST'])
@staff_required
def approve_request(request_id):
    user = get_current_user()
    
    try:
        result = process_request_approval(user.staff_id, request_id)
        flash(f"Approved {result['logged_hours'].hours} hours for {result['student_name']}", 'success')
    except Exception as e:
        flash(f'Error approving request: {str(e)}', 'error')
    
    return redirect(url_for('staff_views.staff_requests'))


@staff_views.route('/staff/deny/<int:request_id>', methods=['POST'])
@staff_required
def deny_request(request_id):
    user = get_current_user()
    
    try:
        result = process_request_denial(user.staff_id, request_id)
        flash(f"Denied request from {result['student_name']}", 'success')
    except Exception as e:
        flash(f'Error denying request: {str(e)}', 'error')
    
    return redirect(url_for('staff_views.staff_requests'))


@staff_views.route('/staff/leaderboard', methods=['GET'])
@staff_required
def staff_leaderboard():
    leaderboard_data = generate_leaderboard()
    
    leaderboard = []
    for entry in leaderboard_data:
        hours = entry['hours']
        accolades = []
        if hours >= 10:
            accolades.append('10h')
        if hours >= 25:
            accolades.append('25h')
        if hours >= 50:
            accolades.append('50h')
        
        next_m = get_next_milestone(hours)
        if next_m == 10:
            progress = min(100, int((hours / 10) * 100))
        elif next_m == 25:
            progress = min(100, int(((hours - 0) / 25) * 100))
        elif next_m == 50:
            progress = min(100, int(((hours - 0) / 50) * 100))
        else:
            progress = 100
        
        leaderboard.append({
            'name': entry['name'],
            'hours': hours,
            'accolades': accolades,
            'milestone_progress': progress
        })
    
    return render_template('leaderboard.html', leaderboard=leaderboard)


@staff_views.route('/api/accept_request', methods=['PUT'])
@jwt_required()
def accept_request_action():
    user = jwt_current_user
    if user.role != 'staff':
        return jsonify(message='Access forbidden: Not a staff member'), 403
    data = request.json
    if not data or 'request_id' not in data:
        return jsonify(message='Invalid request data'), 400
    req = Request.query.get(data['request_id'])
    if not req:
        return jsonify(message='Request not found'), 404
    
    process_request_approval(user.staff_id, data['request_id'])
    
    return jsonify(message='Request accepted'), 200


@staff_views.route('/api/deny_request', methods=['PUT'])
@jwt_required()
def deny_request_action():
    user = jwt_current_user
    if user.role != 'staff':
        return jsonify(message='Access forbidden: Not a staff member'), 403
    data = request.json
    if not data or 'request_id' not in data:
        return jsonify(message='Invalid request data'), 400
    req = Request.query.get(data['request_id'])
    if not req:
        return jsonify(message='Request not found'), 404
    process_request_denial(user.staff_id, data['request_id'])
    return jsonify(message='Request denied'), 200


@staff_views.route('/api/delete_request', methods=['DELETE'])
@jwt_required()
def delete_request_action():
    user = jwt_current_user
    if user.role != 'staff':
        return jsonify(message='Access forbidden: Not a staff member'), 403
    data = request.json
    if not data or 'request_id' not in data:
        return jsonify(message='Invalid request data'), 400
    req = Request.query.get(data['request_id'])
    if not req:
        return jsonify(message='Request not found'), 404
    db.session.delete(req)
    db.session.commit()
    return jsonify(message='Request deleted'), 200


@staff_views.route('/api/delete_logs', methods=['DELETE'])
@jwt_required()
def delete_logs_action():
    user = jwt_current_user
    if user.role != 'staff':
        return jsonify(message='Access forbidden: Not a staff member'), 403
    data = request.json
    if not data or 'log_id' not in data:
        return jsonify(message='Invalid request data'), 400
    log = LoggedHours.query.get(data['log_id'])
    if not log:
        return jsonify(message='Log not found'), 404
    db.session.delete(log)
    db.session.commit()
    return jsonify(message='Logs deleted'), 200
