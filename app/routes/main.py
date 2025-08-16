"""Main routes and dashboard."""
from flask import Blueprint, jsonify, render_template, redirect, url_for
from flask_login import login_required

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """Home page - redirect to dashboard or login."""
    return redirect(url_for('auth.login'))


@bp.route('/health')
def health():
    """Health check endpoint for Docker."""
    return jsonify({'status': 'healthy', 'service': 'IPAM Platform'})


@bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard."""
    return render_template('dashboard.html')
