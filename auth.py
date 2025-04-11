from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from datetime import datetime
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please enter all fields', 'error')
            return render_template('login.html')
        
        user = User.get_by_username(username)
        
        if not user or not check_password_hash(user.password_hash, password):
            flash('Invalid username or password', 'error')
            return render_template('login.html')
        
        login_user(user)
        return redirect(url_for('dashboard'))
    
    now = datetime.now()
    return render_template('login.html', now=now)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        password = request.form.get('password')
        
        if password:
            user = User.get_by_id(current_user.id)
            user.password_hash = generate_password_hash(password)
            flash('Password updated successfully', 'success')
        
        return redirect(url_for('dashboard'))
    
    return render_template('profile.html')
