from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user as jwt_current_user
from App.models import Student, Request, LoggedHours
from App.controllers.student_controller import (
    get_all_students_json,
    fetch_accolades,
    create_hours_request,
    get_activity_history,
    fetch_requests,
    generate_leaderboard
)
from App.controllers.session_auth import student_required, get_current_user
from App import db

student_views = Blueprint('student_views', __name__, template_folder='../templates')


def get_next_milestone(hours):
    milestones = [10, 25, 50, 100]
    for m in milestones:
        if hours < m:
            return m
    return milestones[-1]


def calculate_milestone_progress(hours, next_milestone):
    if next_milestone == 10:
        return min(100, int((hours / 10) * 100))
    elif next_milestone == 25:
        return min(100, int(((hours - 10) / 15) * 100))
    elif next_milestone == 50:
        return min(100, int(((hours - 25) / 25) * 100))
    elif next_milestone == 100:
        return min(100, int(((hours - 50) / 50) * 100))
    return 100


@student_views.route('/student/dashboard', methods=['GET'])
@student_required
def student_dashboard():
    user = get_current_user()
    
    confirmed_hours = sum(lh.hours for lh in user.loggedhours if lh.status == 'approved')
    pending_hours = sum(r.hours for r in user.requests if r.status == 'pending')
    next_milestone = get_next_milestone(confirmed_hours)
    milestone_progress = calculate_milestone_progress(confirmed_hours, next_milestone)
    
    recent_activities = []
    all_entries = list(user.loggedhours) + list(user.requests)
    all_entries.sort(key=lambda x: x.timestamp, reverse=True)
    for entry in all_entries[:5]:
        recent_activities.append({
            'hours': entry.hours,
            'status': entry.status,
            'timestamp': entry.timestamp.strftime('%Y-%m-%d %H:%M')
        })
    
    return render_template('student/dashboard.html',
        confirmed_hours=confirmed_hours,
        pending_hours=pending_hours,
        next_milestone=next_milestone,
        milestone_progress=milestone_progress,
        recent_activities=recent_activities
    )


@student_views.route('/student/request-hours', methods=['POST'])
@student_required
def request_hours():
    user = get_current_user()
    
    hours = request.form.get('hours', type=float)
    if not hours or hours <= 0:
        flash('Please enter valid hours', 'error')
        return redirect(url_for('student_views.student_dashboard'))
    
    try:
        create_hours_request(user.student_id, hours)
        flash(f'Successfully requested {hours} hours!', 'success')
    except Exception as e:
        flash(f'Error creating request: {str(e)}', 'error')
    
    return redirect(url_for('student_views.student_dashboard'))


@student_views.route('/student/accolades', methods=['GET'])
@student_required
def student_accolades():
    user = get_current_user()
    
    total_hours = sum(lh.hours for lh in user.loggedhours if lh.status == 'approved')
    accolades = fetch_accolades(user.student_id)
    
    all_milestones = [
        {'name': '10 Hours Milestone', 'hours': 10},
        {'name': '25 Hours Milestone', 'hours': 25},
        {'name': '50 Hours Milestone', 'hours': 50},
        {'name': '100 Hours Milestone', 'hours': 100}
    ]
    
    upcoming_milestones = []
    for m in all_milestones:
        if m['name'] not in accolades:
            progress = min(100, int((total_hours / m['hours']) * 100))
            upcoming_milestones.append({
                'name': m['name'],
                'hours': m['hours'],
                'progress': progress
            })
    
    return render_template('student/accolades.html',
        total_hours=total_hours,
        accolades=accolades,
        upcoming_milestones=upcoming_milestones
    )


@student_views.route('/student/confirmations', methods=['GET'])
@student_required
def student_confirmations():
    user = get_current_user()
    
    pending_requests = [r for r in user.requests if r.status == 'pending']
    confirmed_requests = [r for r in user.requests if r.status in ['approved', 'denied']]
    total_confirmed = sum(lh.hours for lh in user.loggedhours if lh.status == 'approved')
    
    selected_request = None
    if pending_requests:
        selected_request = pending_requests[0]
    
    return render_template('student/confirmations.html',
        pending_requests=pending_requests,
        confirmed_requests=confirmed_requests,
        total_confirmed=total_confirmed,
        selected_request=selected_request
    )


@student_views.route('/student/hours', methods=['GET'])
@student_required
def student_hours():
    user = get_current_user()
    
    filter_status = request.args.get('filter', 'all')
    
    all_activities = list(user.loggedhours) + list(user.requests)
    all_activities.sort(key=lambda x: x.timestamp, reverse=True)
    
    if filter_status != 'all':
        all_activities = [a for a in all_activities if a.status == filter_status]
    
    activities = list(enumerate(all_activities, 1))
    
    return render_template('student/hours.html',
        activities=activities,
        filter=filter_status
    )


@student_views.route('/student/history', methods=['GET'])
@student_required
def student_history():
    user = get_current_user()
    
    try:
        history_data = get_activity_history(user.student_id)
        history = list(enumerate(history_data, 1))
    except:
        history = []
    
    return render_template('student/history.html', history=history)


@student_views.route('/student/leaderboard', methods=['GET'])
@student_required
def student_leaderboard():
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


@student_views.route('/api/accolades', methods=['GET'])
@jwt_required()
def accolades_report_action():
    user = jwt_current_user
    if user.role != 'student':
        return jsonify(message='Access forbidden: Not a student'), 403
    report = fetch_accolades(user.student_id)
    if not report:
        return jsonify(message='No accolades for this student'), 404
    return jsonify(report)


@student_views.route('/api/make_request', methods=['POST'])
@jwt_required()
def make_request_action():
    user = jwt_current_user
    if user.role != 'student':
        return jsonify(message='Access forbidden: Not a student'), 403
    data = request.json
    if not data or 'hours' not in data:
        return jsonify(message='Invalid request data'), 400
    request_2 = create_hours_request(user.student_id, data['hours'])
    return jsonify(request_2.get_json()), 201


@student_views.route('/api/activity_history', methods=['GET'])
@jwt_required()
def activity_history_action():
    user = jwt_current_user
    if user.role != 'student':
        return jsonify(message='Access forbidden: Not a student'), 403
    try:
        history = get_activity_history(user.student_id)
        return jsonify({
            'student_id': user.student_id,
            'student_name': user.username,
            'activity_history': history
        }), 200
    except ValueError as e:
        return jsonify(message=str(e)), 404
