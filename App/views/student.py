from flask import Blueprint, render_template, jsonify, request, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user as jwt_current_user
from App.models import Student
from.index import index_views
from App.controllers.student_controller import get_all_students_json,fetch_accolades,create_hours_request,get_activity_history

student_views = Blueprint('student_views', __name__, template_folder='../templates')

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