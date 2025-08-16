"""Assignment management routes."""
from flask import Blueprint, render_template_string
from flask_login import login_required

bp = Blueprint('assignments', __name__, url_prefix='/assignments')


@bp.route('/')
@login_required
def index():
    return render_template_string('''
    {% extends "base.html" %}
    {% block content %}
    <div class="container-fluid">
        <h1><i class="fas fa-handshake"></i> Atamalar</h1>
        <p>Atama yönetimi yakında eklenecek.</p>
    </div>
    {% endblock %}
    ''')


@bp.route('/create')
@login_required
def create():
    return render_template_string('''
    {% extends "base.html" %}
    {% block content %}
    <div class="container-fluid">
        <h1><i class="fas fa-handshake"></i> Atama Yap</h1>
        <p>Atama formu yakında eklenecek.</p>
    </div>
    {% endblock %}
    ''')
