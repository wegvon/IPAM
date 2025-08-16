"""Reports and analytics routes."""
from flask import Blueprint, render_template_string
from flask_login import login_required

bp = Blueprint('reports', __name__, url_prefix='/reports')


@bp.route('/')
@login_required
def index():
    return render_template_string('''
    {% extends "base.html" %}
    {% block content %}
    <div class="container-fluid">
        <h1><i class="fas fa-chart-bar"></i> Raporlar</h1>
        <p>Raporlama ve analitik özellikleri yakında eklenecek.</p>
    </div>
    {% endblock %}
    ''')
