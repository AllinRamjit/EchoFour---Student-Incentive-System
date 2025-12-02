from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user, unset_jwt_cookies, set_access_cookies

from App.controllers import login
from App.controllers.student_controller import register_student
from App.controllers.staff_controller import register_staff

auth_views = Blueprint('auth_views', __name__, template_folder='../templates')


@auth_views.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')


@auth_views.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')


@auth_views.route('/auth/login', methods=['POST'])
def login_action():
    data = request.form
    username = data.get('username')
    password = data.get('password')
    
    token = login(username, password)
    
    if not token:
        flash('Invalid username or password', 'error')
        return redirect(url_for('auth_views.login_page'))
    
    from App.models import User
    from App import db
    user = db.session.execute(db.select(User).filter_by(username=username)).scalar_one_or_none()
    
    if user.role == 'student':
        response = redirect(url_for('student_views.student_dashboard'))
    elif user.role == 'staff':
        response = redirect(url_for('staff_views.staff_dashboard'))
    else:
        response = redirect(url_for('index_views.index_page'))
    
    flash('Login successful!', 'success')
    set_access_cookies(response, token)
    return response


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
    response = redirect(url_for('auth_views.login_page'))
    flash('Logged out successfully!', 'success')
    unset_jwt_cookies(response)
    return response


@auth_views.route('/identify', methods=['GET'])
@jwt_required()
def identify_page():
    return render_template('message.html', title="Identify", message=f"You are logged in as {current_user.id} - {current_user.username}")


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
