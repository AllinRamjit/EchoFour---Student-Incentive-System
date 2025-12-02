from flask import Blueprint, redirect, render_template, request, send_from_directory, jsonify, url_for
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from App.controllers import create_user, initialize
from App import db
from App.models import User

index_views = Blueprint('index_views', __name__, template_folder='../templates')

@index_views.route('/', methods=['GET'])
def index_page():
    try:
        verify_jwt_in_request()
        identity = get_jwt_identity()
        user_id = int(identity) if identity is not None else None
        current_user = db.session.get(User, user_id) if user_id is not None else None
        
        if current_user:
            if current_user.role == 'student':
                return redirect(url_for('student_views.student_dashboard'))
            elif current_user.role == 'staff':
                return redirect(url_for('staff_views.staff_dashboard'))
    except:
        pass
    
    return redirect(url_for('auth_views.login_page'))

@index_views.route('/init', methods=['GET'])
def init():
    initialize()
    return jsonify(message='db initialized!')

@index_views.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status':'healthy'})
