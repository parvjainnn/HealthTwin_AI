"""Auth blueprint – register, login, logout."""
from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .database import get_user_by_username, get_user_by_email, create_user
from .user_model import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('health.dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'

        user_data = get_user_by_username(username)
        if user_data and check_password_hash(user_data['password_hash'], password):
            user = User(user_data)
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(next_page or url_for('health.dashboard'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('health.dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        # Validations
        if not username or not email or not password:
            flash('All fields are required.', 'error')
        elif password != confirm:
            flash('Passwords do not match.', 'error')
        elif len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
        elif get_user_by_username(username):
            flash('Username already taken.', 'error')
        elif get_user_by_email(email):
            flash('Email already registered.', 'error')
        else:
            pw_hash = generate_password_hash(password)
            user_id = create_user(username, email, pw_hash)
            user_data = {'id': user_id, 'username': username, 'email': email, 'password_hash': pw_hash}
            user = User(user_data)
            login_user(user)
            flash(f'Account created! Welcome, {username}!', 'success')
            return redirect(url_for('health.dashboard'))

    return render_template('register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/api/mobile/auth/register', methods=['POST'])
def mobile_register():
    if current_user.is_authenticated:
        return jsonify({
            'success': True,
            'user': {'id': current_user.id, 'username': current_user.username, 'email': current_user.email}
        })

    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    email = (data.get('email') or '').strip()
    password = data.get('password') or ''
    confirm = data.get('confirm_password') or password

    if not username or not email or not password:
        return jsonify({'error': 'All fields are required.'}), 400
    if password != confirm:
        return jsonify({'error': 'Passwords do not match.'}), 400
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters.'}), 400
    if get_user_by_username(username):
        return jsonify({'error': 'Username already taken.'}), 409
    if get_user_by_email(email):
        return jsonify({'error': 'Email already registered.'}), 409

    pw_hash = generate_password_hash(password)
    user_id = create_user(username, email, pw_hash)
    user_data = {'id': user_id, 'username': username, 'email': email, 'password_hash': pw_hash}
    user = User(user_data)
    login_user(user)

    return jsonify({
        'success': True,
        'user': {'id': user.id, 'username': user.username, 'email': user.email}
    }), 201


@auth_bp.route('/api/mobile/auth/login', methods=['POST'])
def mobile_login():
    if current_user.is_authenticated:
        return jsonify({
            'success': True,
            'user': {'id': current_user.id, 'username': current_user.username, 'email': current_user.email}
        })

    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''
    remember = bool(data.get('remember', True))

    user_data = get_user_by_username(username)
    if not user_data or not check_password_hash(user_data['password_hash'], password):
        return jsonify({'error': 'Invalid username or password.'}), 401

    user = User(user_data)
    login_user(user, remember=remember)
    return jsonify({
        'success': True,
        'user': {'id': user.id, 'username': user.username, 'email': user.email}
    })


@auth_bp.route('/api/mobile/auth/me', methods=['GET'])
@login_required
def mobile_me():
    return jsonify({
        'authenticated': True,
        'user': {'id': current_user.id, 'username': current_user.username, 'email': current_user.email}
    })


@auth_bp.route('/api/mobile/auth/logout', methods=['POST'])
@login_required
def mobile_logout():
    logout_user()
    session.clear()
    return jsonify({'success': True})
