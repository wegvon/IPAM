"""CLI commands for the application."""
import click
from flask.cli import with_appcontext


def register(app):
    """Register CLI commands."""
    
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Drop existing tables')
    @with_appcontext
    def init_db(drop):
        """Initialize the database."""
        from app import db
        
        if drop:
            click.echo('Dropping existing tables...')
            db.drop_all()
            
        click.echo('Creating database tables...')
        db.create_all()
        click.echo('Database initialized!')
    
    @app.cli.command()
    @with_appcontext
    def seed_data():
        """Seed the database with sample data."""
        from seed_data import seed_database
        
        click.echo('Seeding database...')
        seed_database()
        click.echo('Database seeded!')
    
    @app.cli.command()
    @click.option('--username', prompt=True)
    @click.option('--email', prompt=True)
    @click.option('--password', prompt=True, hide_input=True,
                  confirmation_prompt=True)
    @with_appcontext
    def create_admin(username, email, password):
        """Create an admin user."""
        from app import db
        from app.models import User
        
        user = User(username=username, email=email, is_admin=True)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        click.echo(f'Admin user {username} created!')
