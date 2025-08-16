"""Application entry point for Flask CLI commands."""
from app import create_app, db
from app.models import User, Customer, Subnet, Assignment, ExchangeRate, AuditLog

app = create_app()


@app.shell_context_processor
def make_shell_context():
    """Make database models available in flask shell."""
    return {
        'db': db,
        'User': User,
        'Customer': Customer,
        'Subnet': Subnet,
        'Assignment': Assignment,
        'ExchangeRate': ExchangeRate,
        'AuditLog': AuditLog
    }
