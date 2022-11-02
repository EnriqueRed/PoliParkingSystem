from cmath import e
from tkinter import E
from flask import Blueprint, render_template, jsonify, request, redirect, session, url_for, flash
from flask_login import login_required
from website.models import MovimientoVehiculo, Parqueadero, Vehiculo, Tipovehiculo, User
from .. import db
from datetime import date, datetime
import pytz


mov_vehicles = Blueprint('mov_vehicles', __name__)

# Vehiculos ------------------------------------------------------------------------
@mov_vehicles.route('/mov_vehiculo', methods=['GET'])
@login_required
def get_mov_vehiculo():
    mov_vehiculo = MovimientoVehiculo.query.join(Vehiculo).with_entities(MovimientoVehiculo.id, 
                                            MovimientoVehiculo.estado, Vehiculo.placa, MovimientoVehiculo.minutos,
                                            MovimientoVehiculo.fecha_ingreso.label("ingreso"),
                                            MovimientoVehiculo.fecha_salida.label("salida")).order_by(MovimientoVehiculo.id.desc())

    contexto = {"lista_mov": mov_vehiculo}

    return render_template('/sitio/movimiento_vehiculos/ver_movimiento.html', context=contexto)

@mov_vehicles.route('/ajax_register_mov', methods=['GET','POST'])
def ajax_register_mov():
    if request.form['optionid']:
        optionid = int(request.form['optionid'])
    else:
        optionid = 0

    tipo_mov = ''

    if optionid == 1:
        tipo_mov = 'Ingreso'
    elif optionid == 2:
        tipo_mov = 'Salida'

    parking_id = session['parking']
    parkings = Parqueadero.query.with_entities(Parqueadero.id, Parqueadero.nombre).filter(Parqueadero.id == parking_id).first()
    vehicles = Vehiculo.query.join(Tipovehiculo).with_entities(Vehiculo.id, Vehiculo.placa, Tipovehiculo.nombre.label("tipo")).all()

    contexto = {"tipo_mov": tipo_mov,
                "option_id": optionid,
                "parqueadero": parkings,
                "lista_vehiculos": vehicles,
                "estado": 'Ninguno'}    

    return jsonify({'htmlresponse': render_template('/sitio/movimiento_vehiculos/registrar_mov.html', context=contexto)})

@mov_vehicles.route("/mov_vehiculo/registrar", methods=['POST'])
def register_mov():
    if request.method == 'POST':
        fecha_in = request.form.get('in_date')
        hora_in = request.form.get('in_hour')
        fecha_out= request.form.get('out_date')
        hora_out = request.form.get('out_hour')
        vehiculo_id = int(request.form.get('vehicle'))
        parqueadero_id = int(request.form.get('parking'))

        vehicle_mov = MovimientoVehiculo.query.filter(MovimientoVehiculo.vehiculo_id==vehiculo_id, MovimientoVehiculo.parqueadero_id==parqueadero_id).order_by(MovimientoVehiculo.id.desc()).first()
        utc=pytz.timezone('America/Lima')
        
        if hora_in:
            if vehicle_mov:
                if vehicle_mov.estado == 'ingreso':
                    flash('No es posible registrar ingreso de un vehículo que ya está dentro del parqueadero. Por favor verifique!', category='error')
                    mov_vehiculo = MovimientoVehiculo.query.join(Vehiculo).with_entities(MovimientoVehiculo.id, 
                                                            MovimientoVehiculo.estado, Vehiculo.placa,
                                                            MovimientoVehiculo.fecha_ingreso.label("ingreso"),
                                                            MovimientoVehiculo.fecha_salida.label("salida"))

                    contexto = {"lista_mov": mov_vehiculo}

                    return render_template('/sitio/movimiento_vehiculos/ver_movimiento.html', context=contexto)
            
            fecha_ingreso = datetime.strptime(str(fecha_in) + ' ' + str(hora_in), '%Y-%m-%d %H:%M')

        if hora_out:
            if vehicle_mov:
                if vehicle_mov.estado == 'salida':
                    flash('No es posible registrar salida de un vehículo que ya no se encuentra en el parqueadero. Por favor verifique!', category='error')
                    mov_vehiculo = MovimientoVehiculo.query.join(Vehiculo).with_entities(MovimientoVehiculo.id, 
                                                            MovimientoVehiculo.estado, Vehiculo.placa,
                                                            MovimientoVehiculo.fecha_ingreso.label("ingreso"),
                                                            MovimientoVehiculo.fecha_salida.label("salida"))

                    contexto = {"lista_mov": mov_vehiculo}

                    return render_template('/sitio/movimiento_vehiculos/ver_movimiento.html', context=contexto)

            fecha_salida = datetime.strptime(str(fecha_out) + ' ' + str(hora_out), '%Y-%m-%d %H:%M')   

            if fecha_salida.replace(tzinfo=utc) < vehicle_mov.fecha_ingreso.replace(tzinfo=utc):
                flash('La fecha y hora de salida no puede ser menor a la de entrada. Por favor verifique!', category='error')
                mov_vehiculo = MovimientoVehiculo.query.join(Vehiculo).with_entities(MovimientoVehiculo.id, 
                                                        MovimientoVehiculo.estado, Vehiculo.placa,
                                                        MovimientoVehiculo.fecha_ingreso.label("ingreso"),
                                                        MovimientoVehiculo.fecha_salida.label("salida"))

                contexto = {"lista_mov": mov_vehiculo}

                return render_template('/sitio/movimiento_vehiculos/ver_movimiento.html', context=contexto)

            minutos = int(divmod((fecha_salida.replace(tzinfo=utc) - vehicle_mov.fecha_ingreso.replace(tzinfo=utc)).total_seconds(), 60)[0])
        try:
            if hora_in:
                new_mov = MovimientoVehiculo(fecha_ingreso= fecha_ingreso,
                                            estado= 'ingreso',
                                            vehiculo_id= vehiculo_id,
                                            parqueadero_id= parqueadero_id)

                db.session.add(new_mov)
            elif hora_out:
                vehicle_mov.fecha_salida= fecha_salida
                vehicle_mov.estado= 'salida'
                vehicle_mov.minutos= minutos

            db.session.commit()
        except BaseException as error:
            db.session.rollback()

        return redirect(url_for('mov_vehicles.get_mov_vehiculo'))
