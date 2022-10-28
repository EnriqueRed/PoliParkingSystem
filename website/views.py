from cmath import e
from tkinter import E
from flask import Blueprint, render_template, jsonify, request, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from website.models import Vehiculo, Tipovehiculo, Parqueadero, MovimientoVehiculo, User
from . import db

views = Blueprint('views', __name__)

@views.route('/')
def login():
    return render_template('/admin/login.html')

# Index ---------------------------------------------------------------------------
@views.route('/inicio')
@login_required
def inicio():
    return render_template('/sitio/index.html')

# Vehiculos ------------------------------------------------------------------------
@views.route('/vehiculo', methods=['GET'])
@login_required
def get_vehiculo():
    vehiculos_list = Vehiculo.query.join(User).join(Tipovehiculo).with_entities(Vehiculo.id, Vehiculo.placa,User.nombre,Tipovehiculo.nombre.label("tipo"))
    list_types = Tipovehiculo.query.all()
    list_users = User.query.with_entities(User.id, User.nombre, User.usuario).order_by(User.nombre)

    contexto = {"lista_users": list_users,
                "lista_tipos": list_types,
                "lista_vehiculo": vehiculos_list}    

    return render_template('/sitio/vehiculo.html', context=contexto)

@views.route('/vehiculo/crear', methods=['POST'])
def crear_vehiculo():
    if request.method == 'POST':
        tmp_placa = request.form.get('placa')

        usuario = int(request.form.get('usuario'))
        tipo = int(request.form.get('tipo'))

        try:
            new_vehicle = Vehiculo(placa= tmp_placa,
                                    user_id= usuario,
                                    tipo_vehiculo_id= tipo)
            db.session.add(new_vehicle)

            db.session.commit()
        except BaseException as error:
            db.session.rollback()

        return redirect(url_for('views.get_vehiculo'))

@views.route('/vehiculo/editar', methods=['POST'])
def editar_vehiculo():
    if request.method == 'POST':
        tmp_placa = request.form.get('placa')
        usuario = int(request.form.get('usuario'))
        tipo = int(request.form.get('tipo'))
        vehiculoid = int(request.form.get('id_v'))

        try:
            tmp_vehicle = Vehiculo.query.filter(Vehiculo.id == vehiculoid).first()
            tmp_vehicle.placa= tmp_placa
            tmp_vehicle.user_id= usuario
            tmp_vehicle.tipo_vehiculo_id= tipo

            db.session.commit()
        except BaseException as error:
            db.session.rollback()

        return redirect(url_for('views.get_vehiculo'))

@views.route('/ajax_get_vehiculo_id', methods=['GET','POST'])
def get_vehiculo_id():
    if request.form['vehiculoid']:
        vehiculoid = int(request.form['vehiculoid'])
    else:
        vehiculoid = 0

    list_types = Tipovehiculo.query.all()
    list_users = User.query.with_entities(User.id, User.nombre, User.usuario).order_by(User.nombre)

    vehiculo = Vehiculo.query.join(User).join(Tipovehiculo).with_entities(Vehiculo.id, Vehiculo.placa,User.id.label("u_id"),
                User.nombre, User.usuario,Tipovehiculo.id.label("t_id"),Tipovehiculo.nombre.label("tipo")).filter(Vehiculo.id == vehiculoid).first()

    contexto = {"lista_users": list_users,
                "lista_tipos": list_types,
                "vehicle": vehiculo}    

    return jsonify({'htmlresponse': render_template('/sitio/vehiculo_response.html', context=contexto)})

@views.route('/ajax_delete_vehiculo_id', methods=['GET','POST'])
def delete_vehiculo_id():
    if request.form['vehiculoid']:
        vehiculoid = int(request.form['vehiculoid'])
    else:
        vehiculoid = 0

    try:
        Vehiculo.query.filter(Vehiculo.id == vehiculoid).delete()
        db.session.commit()
    except BaseException as error:
        db.session.rollback()

    return jsonify('true')

# Movimiento de vehiculos ----------------------------------------------------------
@views.route('/vehiculo_mov/lista', methods=['GET'])
@login_required
def get_vehiculo_mov():
    vehiculo_movs = MovimientoVehiculo.query.all()
    return jsonify([vehiculo_mov.to_json() for vehiculo_mov in vehiculo_movs])

# Parqueadero ------------------------------------------------------------------------
@views.route('/parking/lista', methods=['GET'])
@login_required
def get_parking():
    parkings = Parqueadero.query.all()
    return jsonify([parking.to_json() for parking in parkings])



