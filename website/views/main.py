from cmath import e
from tkinter import E
from flask import Blueprint, render_template, jsonify, request, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from website.models import Vehiculo, Tipovehiculo, Parqueadero, MovimientoVehiculo, User
from .. import db

main = Blueprint('main', __name__)

@main.route('/')
def login():
    return render_template('/admin/login.html')

# Index ---------------------------------------------------------------------------


# Movimiento de vehiculos ----------------------------------------------------------
@main.route('/vehiculo_mov/lista', methods=['GET'])
@login_required
def get_vehiculo_mov():
    vehiculo_movs = MovimientoVehiculo.query.all()
    return jsonify([vehiculo_mov.to_json() for vehiculo_mov in vehiculo_movs])

# Parqueadero ------------------------------------------------------------------------
@main.route('/parking/lista', methods=['GET'])
@login_required
def get_parking():
    parkings = Parqueadero.query.all()
    return jsonify([parking.to_json() for parking in parkings])



