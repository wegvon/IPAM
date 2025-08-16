"""Error handlers for the application."""
from flask import render_template
from app import db


def not_found_error(error):
    """Handle 404 errors."""
    return render_template('errors/404.html'), 404


def internal_error(error):
    """Handle 500 errors."""
    db.session.rollback()
    return render_template('errors/500.html'), 500


def forbidden_error(error):
    """Handle 403 errors."""
    return render_template('errors/403.html'), 403
