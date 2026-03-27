from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated: return redirect(url_for('dashboard.index'))
    if request.method == 'POST':
        db = current_app.config['db']
        username, email, password = request.form['username'], request.form['email'], request.form['password']
        if list(db.collection('users').where('username', '==', username).stream()):
            flash('Username already exists', 'error')
            return render_template('auth/register.html')
        if list(db.collection('users').where('email', '==', email).stream()):
            flash('Email already registered', 'error')
            return render_template('auth/register.html')
        db.collection('users').add({'username': username, 'email': email, 'password_hash': generate_password_hash(password)})
        flash('Registration successful!', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    from app.models import User
    if current_user.is_authenticated: return redirect(url_for('dashboard.index'))
    if request.method == 'POST':
        db = current_app.config['db']
        username, password, remember = request.form['username'], request.form['password'], bool(request.form.get('remember'))
        users = list(db.collection('users').where('username', '==', username).stream())
        if users:
            user_data = users[0].to_dict()
            if check_password_hash(user_data['password_hash'], password):
                user = User(users[0].id) 
                login_user(user, remember=remember)
                return redirect(request.args.get('next') or url_for('dashboard.index'))
        flash('Invalid username or password', 'error')
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))