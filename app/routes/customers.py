"""Customer management routes."""
from flask import Blueprint, render_template_string
from flask_login import login_required

bp = Blueprint('customers', __name__, url_prefix='/customers')


@bp.route('/')
@login_required
def index():
    return render_template_string('''
    {% extends "base.html" %}
    {% block content %}
    <div class="container-fluid">
        <h1><i class="fas fa-users"></i> Müşteriler</h1>
        <p>Müşteri yönetimi yakında eklenecek.</p>
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
        <h1><i class="fas fa-user-plus"></i> Müşteri Ekle</h1>
        <p>Müşteri ekleme formu yakında eklenecek.</p>
    </div>
    {% endblock %}
    ''')
