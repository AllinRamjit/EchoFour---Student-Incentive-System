from flask import Blueprint, redirect, render_template, request, send_from_directory, jsonify, url_for, session
from App.controllers import create_user, initialize
from App import db
from App.models import User
from App.controllers.session_auth import get_current_user

index_views = Blueprint('index_views', __name__, template_folder='../templates')

@index_views.route('/', methods=['GET'])
def index_page():
    if 'user_id' in session:
        user = get_current_user()
        if user:
            if user.role == 'student':
                return redirect(url_for('student_views.student_dashboard'))
            elif user.role == 'staff':
                return redirect(url_for('staff_views.staff_dashboard'))
    
    return redirect(url_for('auth_views.login_page'))

@index_views.route('/init', methods=['GET'])
def init():
    initialize()
    return jsonify(message='db initialized!')

@index_views.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status':'healthy'})
