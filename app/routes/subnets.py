"""Subnet management routes."""
from flask import Blueprint, render_template_string
from flask_login import login_required

bp = Blueprint('subnets', __name__, url_prefix='/subnets')


@bp.route('/')
@login_required
def index():
    """List all subnets."""
    return render_template_string('''
    {% extends "base.html" %}
    {% block content %}
    <div class="container-fluid">
        <h1><i class="fas fa-sitemap"></i> Subnets</h1>
        <p>Subnet yönetimi yakında eklenecek.</p>
    </div>
    {% endblock %}
    ''')


@bp.route('/create')
@login_required
def create():
    """Create new subnet."""
    return render_template_string('''
    {% extends "base.html" %}
    {% block content %}
    <div class="container-fluid">
        <h1><i class="fas fa-plus"></i> Subnet Ekle</h1>
        <p>Subnet ekleme formu yakında eklenecek.</p>
    </div>
    {% endblock %}
    ''')
