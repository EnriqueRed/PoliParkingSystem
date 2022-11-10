from cmath import e
from tkinter import E
from flask import Blueprint, current_app, render_template, jsonify, request, redirect, session, url_for
from flask_login import login_required
from website.models import Parqueadero, User
from sqlalchemy.sql import text
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
@login_required
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
@login_required
def editar_parqueadero():
    if request.method == 'POST':
        id_p = request.form.get('id_p')
        nombre = request.form.get('nombre')
        c_carros = request.form.get('c_carros')
        c_motos = request.form.get('c_motos')
        direccion = request.form.get('direccion')
        url_map = request.form.get('url_map')

        try:
            tmp_parking = Parqueadero.query.filter(Parqueadero.id == id_p).first()
            tmp_parking.nombre= nombre
            tmp_parking.capacidad_carros= c_carros
            tmp_parking.capacidad_motos= c_motos
            tmp_parking.direccion= direccion
            tmp_parking.url_mapa= url_map

            db.session.commit()
        except BaseException as error:
            db.session.rollback()

        return redirect(url_for('parkings.get_parqueadero'))

@parkings.route('/ajax_get_parqueadero_id', methods=['GET','POST'])
@login_required
def get_parqueadero_id():
    if request.form['parqueaderoid']:
        parqueaderoid = int(request.form['parqueaderoid'])
    else:
        parqueaderoid = 0

    parqueadero = Parqueadero.query.with_entities(Parqueadero.id, Parqueadero.nombre, Parqueadero.capacidad_carros, 
                                                Parqueadero.capacidad_motos, Parqueadero.direccion, Parqueadero.url_mapa).filter(Parqueadero.id == parqueaderoid).first()

    contexto = {"parking": parqueadero}    

    return jsonify({'htmlresponse': render_template('/sitio/parqueadero_response.html', context=contexto)})

@parkings.route('/ajax_delete_parqueadero_id', methods=['GET','POST'])
@login_required
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


@parkings.route('/parqueadero/disponibilidad', methods=['GET'])
@login_required
def get_parqueadero_disponibilidad():
    sql = '''
        select *, round(100 - (A.carro * 100 / A.capacidad_carros),0) as percent_carro, 
                round(100 - (A.moto * 100 / A.capacidad_motos),0) as percent_moto
        from 
        (
            select A.id, A.nombre,	sum(case vehiculo when 'Carro' then cant else 0 end) as Carro,
                    A.capacidad_carros, sum(case vehiculo when 'Moto' then cant else 0 end) as Moto,
                    A.capacidad_motos, A.direccion, A.url_mapa
            from
            (
                select A.id, A.nombre, A.capacidad_carros, A.capacidad_motos, A.direccion, B.cant, B.nombre as vehiculo, A.url_mapa
                from parqueadero A
                left join
                (
                    select count(A.id) as cant, A.parqueadero_id, C.nombre
                    from movimiento_vehiculo A
                    inner join vehiculo B on A.vehiculo_id = B.id
                    inner join tipovehiculo C on B.tipo_vehiculo_id = C.id 
                    where estado = 'ingreso'
                    group by A.parqueadero_id, C.nombre	
                ) B on A.id = B.parqueadero_id    
            ) A 
            group by A.id, A.nombre, A.capacidad_carros, A.capacidad_motos, A.direccion, A.url_mapa
        ) A
    ''' 
    
    engine = current_app.config.get('engine')
    with engine.connect().execution_options(autocommit=True) as conn:
        query = conn.execute(text(sql))         
    disponibilidad = query.fetchall()

    contexto = {"disponibilidad": disponibilidad}  

    return render_template('/sitio/parqueadero_disponibilidad.html', context=contexto)