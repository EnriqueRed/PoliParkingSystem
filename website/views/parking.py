from cmath import e
from tkinter import E
from flask import Blueprint, render_template, jsonify, request, redirect, url_for
from flask_login import login_required
from website.models import Parqueadero, User
from .. import db

parkings = Blueprint('parkings', __name__)

# Parqueaderos ------------------------------------------------------------------------
@parkings.route('/parqueadero', methods=['GET'])
@login_required
def get_parqueadero():
    parking_list = Parqueadero.query.with_entities(Parqueadero.id, Parqueadero.nombre, Parqueadero.capacidad_carros, Parqueadero.capacidad_motos, Parqueadero.direccion)

    contexto = {"lista_parqueadero": parking_list}    

    return render_template('/sitio/parqueadero.html', context=contexto)

@parkings.route('/parqueadero/crear', methods=['POST'])
def crear_parqueadero():
    if request.method == 'POST':
        tmp_nombre = request.form.get('nombre')
        tmp_c_carros = request.form.get('c_carros')
        tmp_c_motos = request.form.get('c_motos')
        tmp_direccion = request.form.get('direccion')

        try:
            new_parking = Parqueadero(nombre= tmp_nombre,
                                    capacidad_carros= tmp_c_carros,
                                    capacidad_motos= tmp_c_motos,
                                    direccion= tmp_direccion)
            db.session.add(new_parking)

            db.session.commit()
        except BaseException as error:
            db.session.rollback()

        return redirect(url_for('parkings.get_parqueadero'))

@parkings.route('/parqueadero/editar', methods=['POST'])
def editar_parqueadero():
    if request.method == 'POST':
        id_p = request.form.get('id_p')
        nombre = request.form.get('nombre')
        c_carros = request.form.get('c_carros')
        c_motos = request.form.get('c_motos')
        direccion = request.form.get('direccion')

        try:
            tmp_parking = Parqueadero.query.filter(Parqueadero.id == id_p).first()
            tmp_parking.nombre= nombre
            tmp_parking.capacidad_carros= c_carros
            tmp_parking.capacidad_motos= c_motos
            tmp_parking.direccion= direccion

            db.session.commit()
        except BaseException as error:
            db.session.rollback()

        return redirect(url_for('parkings.get_parqueadero'))

@parkings.route('/ajax_get_parqueadero_id', methods=['GET','POST'])
def get_parqueadero_id():
    if request.form['parqueaderoid']:
        parqueaderoid = int(request.form['parqueaderoid'])
    else:
        parqueaderoid = 0

    parqueadero = Parqueadero.query.with_entities(Parqueadero.id, Parqueadero.nombre, Parqueadero.capacidad_carros, 
                                                Parqueadero.capacidad_motos, Parqueadero.direccion).filter(Parqueadero.id == parqueaderoid).first()

    contexto = {"parking": parqueadero}    

    return jsonify({'htmlresponse': render_template('/sitio/parqueadero_response.html', context=contexto)})

@parkings.route('/ajax_delete_parqueadero_id', methods=['GET','POST'])
def delete_parqueadero_id():
    if request.form['parqueaderoid']:
        parqueaderoid = int(request.form['parqueaderoid'])
    else:
        parqueaderoid = 0

    try:
        Parqueadero.query.filter(Parqueadero.id == parqueaderoid).delete()
        db.session.commit()
    except BaseException as error:
        db.session.rollback()

    return jsonify('true')



