from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for, session
from flask_jwt_extended import jwt_required, current_user, unset_jwt_cookies, set_access_cookies

from App.controllers import login
from App.controllers.student_controller import register_student
from App.controllers.staff_controller import register_staff
from App.controllers.session_auth import login_user, logout_user, get_current_user

auth_views = Blueprint('auth_views', __name__, template_folder='../templates')


@auth_views.route('/login', methods=['GET'])
def login_page():
    if 'user_id' in session:
        user = get_current_user()
        if user:
            if user.role == 'student':
                return redirect(url_for('student_views.student_dashboard'))
            elif user.role == 'staff':
                return redirect(url_for('staff_views.staff_dashboard'))
    return render_template('login.html')


@auth_views.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')


@auth_views.route('/auth/login', methods=['POST'])
def login_action():
    data = request.form
    username = data.get('username')
    password = data.get('password')
    
    user = login_user(username, password)
    
    if not user:
        flash('Invalid username or password', 'error')
        return redirect(url_for('auth_views.login_page'))
    
    flash('Login successful!', 'success')
    
    if user.role == 'student':
        return redirect(url_for('student_views.student_dashboard'))
    elif user.role == 'staff':
        return redirect(url_for('staff_views.staff_dashboard'))
    else:
        return redirect(url_for('index_views.index_page'))


@auth_views.route('/auth/register', methods=['POST'])
def register_action():
    data = request.form
    role = data.get('role', 'student')
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not username or not email or not password:
        flash('All fields are required', 'error')
        return redirect(url_for('auth_views.register_page'))
    
    try:
        if role == 'staff':
            user = register_staff(username, email, password)
        else:
            user = register_student(username, email, password)
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth_views.login_page'))
    except Exception as e:
        flash(f'Registration failed: {str(e)}', 'error')
        return redirect(url_for('auth_views.register_page'))


@auth_views.route('/logout', methods=['GET'])
def logout_action():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('auth_views.login_page'))


@auth_views.route('/identify', methods=['GET'])
def identify_page():
    user = get_current_user()
    if not user:
        return redirect(url_for('auth_views.login_page'))
    return render_template('message.html', title="Identify", message=f"You are logged in as {user.user_id} - {user.username}")


@auth_views.route('/api/login', methods=['POST'])
def user_login_api():
    data = request.json
    token = login(data['username'], data['password'])
    if not token:
        return jsonify(message='bad username or password given'), 401
    response = jsonify(access_token=token)
    set_access_cookies(response, token)
    return response


@auth_views.route('/api/identify', methods=['GET'])
@jwt_required()
def identify_user():
    return jsonify({'message': f"username: {current_user.username}, id : {current_user.user_id}"})


@auth_views.route('/api/logout', methods=['GET'])
def logout_api():
    response = jsonify(message="Logged Out!")
    unset_jwt_cookies(response)
    return response
