from flask import Blueprint, render_template, jsonify, request, redirect, session, url_for
from flask_login import login_user, login_required, logout_user, current_user
from website.models import Vehiculo, Tipovehiculo, Parqueadero, MovimientoVehiculo, User
from .. import db

main = Blueprint('main', __name__)

@main.route('/')
def login():
    rol_id = (session['user']['rol'])
    if rol_id != 1:
        return redirect(url_for('dashboard.inicio'))
    else:
        return redirect(url_for('parkings.get_parqueadero_disponibilidad'))



