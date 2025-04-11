import os
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Import modules (after app is created to avoid circular imports)
from models import User, Customer, Billing, PPPConnection
from auth import auth_bp
from api import api_bp

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(api_bp, url_prefix='/api')

# Load user for login manager
@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(int(user_id))

# Main routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('auth.login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get summary data for dashboard
    total_customers = Customer.count()
    active_connections = PPPConnection.count_active()
    monthly_revenue = Billing.calculate_monthly_revenue()
    pending_payments = Billing.count_pending_payments()
    
    # Pass the current date for the footer
    now = datetime.now()
    
    return render_template('dashboard.html', 
                          total_customers=total_customers,
                          active_connections=active_connections,
                          monthly_revenue=monthly_revenue,
                          pending_payments=pending_payments,
                          now=now)

@app.errorhandler(404)
def page_not_found(e):
    now = datetime.now()
    return render_template('base.html', error="Page not found", now=now), 404

@app.errorhandler(500)
def internal_server_error(e):
    now = datetime.now()
    return render_template('base.html', error="Internal server error", now=now), 500

# Additional pages
@app.route('/customers')
@login_required
def customers():
    now = datetime.now()
    return render_template('customers.html', now=now)

@app.route('/billing')
@login_required
def billing():
    now = datetime.now()
    return render_template('billing.html', now=now)

@app.route('/reports')
@login_required
def reports():
    now = datetime.now()
    return render_template('reports.html', now=now)

# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
