from flask import Blueprint
from flask import render_template
from flask_login import login_user, login_required, logout_user, current_user

views = Blueprint('views', __name__)

@views.route('/')
def login():
    return render_template('/admin/login.html')

# Index ---------------------------------------------------------------------------
@views.route('/inicio')
@login_required
def inicio():
    return render_template('/sitio/index.html')