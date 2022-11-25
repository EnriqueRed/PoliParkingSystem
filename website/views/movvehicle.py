from cmath import e
from tkinter import E
from flask import Blueprint, render_template, jsonify, request, redirect, session, url_for, flash, make_response, current_app
from flask_login import login_required
from website.models import MovimientoVehiculo, Parqueadero, Vehiculo, Tipovehiculo, User, Factura, Tarifa
from .. import db
from datetime import date, datetime
import pytz, os, pdfkit, base64
from sqlalchemy.sql import text


mov_vehicles = Blueprint('mov_vehicles', __name__)

# Vehiculos ------------------------------------------------------------------------
@mov_vehicles.route('/mov_vehiculo', methods=['GET'])
@login_required
def get_mov_vehiculo():
    mov_vehiculo = MovimientoVehiculo.query.with_entities(MovimientoVehiculo.id, 
                                            MovimientoVehiculo.estado, MovimientoVehiculo.placa, MovimientoVehiculo.minutos,
                                            MovimientoVehiculo.fecha_ingreso.label("ingreso"),
                                            MovimientoVehiculo.fecha_salida.label("salida")
                                            ).filter(MovimientoVehiculo.parqueadero_id == session['user']['parqueadero']
                                            ).order_by(MovimientoVehiculo.estado.asc(),MovimientoVehiculo.id.desc())

    contexto = {"lista_mov": mov_vehiculo}

    return render_template('/sitio/movimiento_vehiculos/ver_movimiento.html', context=contexto)

@mov_vehicles.route('/ajax_register_mov', methods=['GET','POST'])
@login_required
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

    parking_id = session['user']['parqueadero']
    parkings = Parqueadero.query.with_entities(Parqueadero.id, Parqueadero.nombre).filter(Parqueadero.id == parking_id).first()
    vehicles = Vehiculo.query.join(Tipovehiculo).with_entities(Vehiculo.id, Vehiculo.placa, Tipovehiculo.nombre.label("tipo")).all()

    contexto = {"tipo_mov": tipo_mov,
                "option_id": optionid,
                "parqueadero": parkings,
                "lista_vehiculos": vehicles,
                "date_a": datetime.today().date()}    

    return jsonify({'htmlresponse': render_template('/sitio/movimiento_vehiculos/registrar_mov.html', context=contexto)})


@mov_vehicles.route('/ajax_view_invoice', methods=['GET','POST'])
@login_required
def ajax_view_invoice():
    if request.form['invoiceid']:
        invoiceid = int(request.form['invoiceid'])
    else:
        invoiceid = 0

    # Se generan los datos para la factura
    obj_movvehiculo = MovimientoVehiculo.query.with_entities(MovimientoVehiculo.tipo_vehiculo_id).filter(MovimientoVehiculo.id==invoiceid).first()
    obj_user = MovimientoVehiculo.query.join(Vehiculo).join(User).with_entities(User.tipo_funcionario_id).filter(MovimientoVehiculo.id==invoiceid).first()

    tipo_v = obj_movvehiculo.tipo_vehiculo_id

    if not obj_user:
        tipo_f = 1
    else:
        tipo_f = obj_user.tipo_funcionario_id

    sql = '''
        select C.nombre, C.nit, C.direccion, A.id::varchar, B.placa, D.nombre as tarifa, 
                substring(B.fecha_ingreso::varchar, 1, 10) as fecha_ingreso, substring(B.fecha_ingreso::varchar, 12, 5) as hora_ingreso,
                substring(B.fecha_salida::varchar, 1, 10) as fecha_salida, substring(B.fecha_salida::varchar, 12, 5) as hora_salida,
                date_part('minute', B.fecha_salida) - date_part('minute', B.fecha_ingreso) as minutos, D.valor_minuto, A.total_a_pagar, 
                lpad((date_part('hour', B.fecha_salida) - date_part('hour', B.fecha_ingreso))::varchar, 2, '0') || ':'::text ||
                lpad((date_part('minute', B.fecha_salida) - date_part('minute', B.fecha_ingreso))::varchar, 2, '0') as tiempo
        from factura A
        inner join movimiento_vehiculo B on A.movimiento_id = B.id and B.id = %s
        inner join parqueadero C on A.parqueadero_id = C.id 
        inner join tarifa D on D.tipo_vehiculo_id = %s and D.tipo_funcionario_id = %s 
        limit 1
    '''  % (invoiceid,tipo_v, tipo_f)
    
    engine = current_app.config.get('engine')
    with engine.connect().execution_options(autocommit=True) as conn:
        query = conn.execute(text(sql))         
    report = query.fetchone()

    contexto = {"report": report} 

    # Generación de la factura en PDF
    config = pdfkit.configuration(wkhtmltopdf=os.getenv("WKHTMLTOPDF_DIRECTORY"))
    rendered = render_template('/sitio/invoice_report/invoice.html', context=contexto)
    pdf = pdfkit.from_string(rendered, False, configuration=config)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    # response.headers['Content-Disposition'] = 'attachment; filename=Factura.pdf'
    response.headers['Content-Disposition'] = 'inline; filename=Factura.pdf'

    b64pdf = base64.b64encode(response.get_data())
    base64pdf = 'data:application/pdf;base64,' + b64pdf.decode('utf-8')

    return base64pdf

@mov_vehicles.route("/mov_vehiculo/registrar", methods=['POST'])
@login_required
def register_mov():
    if request.method == 'POST':        
        placa = request.form.get('placa')
        fecha_in = request.form.get('in_date')
        hora_in = request.form.get('in_hour')
        fecha_out= request.form.get('out_date')
        hora_out = request.form.get('out_hour')
        vehicle_type = int(request.form.get('vehicle_type'))
        parqueadero_id = int(request.form.get('parking'))

        vehicle_mov = MovimientoVehiculo.query.filter(MovimientoVehiculo.placa==placa,  MovimientoVehiculo.parqueadero_id==parqueadero_id
                                                    ).order_by(MovimientoVehiculo.estado.asc(), MovimientoVehiculo.id.desc()).first()
        utc=pytz.timezone('America/Lima')
        
        if hora_in:
            if vehicle_mov:
                if vehicle_mov.estado == 'ingreso':
                    flash('No es posible registrar ingreso de un vehículo que ya está dentro del parqueadero. Por favor verifique!', category='error')
                    mov_vehiculo = MovimientoVehiculo.query.with_entities(MovimientoVehiculo.id, 
                                                            MovimientoVehiculo.estado, MovimientoVehiculo.placa,
                                                            MovimientoVehiculo.fecha_ingreso.label("ingreso"),
                                                            MovimientoVehiculo.fecha_salida.label("salida")).filter(MovimientoVehiculo.parqueadero_id == parqueadero_id)

                    contexto = {"lista_mov": mov_vehiculo}

                    return render_template('/sitio/movimiento_vehiculos/ver_movimiento.html', context=contexto)
            
            fecha_ingreso = datetime.strptime(str(fecha_in) + ' ' + str(hora_in), '%Y-%m-%d %H:%M')

        if hora_out:
            if vehicle_mov:
                if vehicle_mov.estado == 'salida':
                    flash('No es posible registrar salida de un vehículo que ya no se encuentra en el parqueadero. Por favor verifique!', category='error')
                    mov_vehiculo = MovimientoVehiculo.query.with_entities(MovimientoVehiculo.id, 
                                                            MovimientoVehiculo.estado, MovimientoVehiculo.placa,
                                                            MovimientoVehiculo.fecha_ingreso.label("ingreso"),
                                                            MovimientoVehiculo.fecha_salida.label("salida")).filter(MovimientoVehiculo.parqueadero_id == parqueadero_id)

                    contexto = {"lista_mov": mov_vehiculo}

                    return render_template('/sitio/movimiento_vehiculos/ver_movimiento.html', context=contexto)

            fecha_salida = datetime.strptime(str(fecha_out) + ' ' + str(hora_out), '%Y-%m-%d %H:%M')   

            if fecha_salida.replace(tzinfo=utc) < vehicle_mov.fecha_ingreso.replace(tzinfo=utc):
                flash('La fecha y hora de salida no puede ser menor a la de entrada. Por favor verifique!', category='error')
                mov_vehiculo = MovimientoVehiculo.query.with_entities(MovimientoVehiculo.id, 
                                                        MovimientoVehiculo.estado, MovimientoVehiculo.placa,
                                                        MovimientoVehiculo.fecha_ingreso.label("ingreso"),
                                                        MovimientoVehiculo.fecha_salida.label("salida")).filter(MovimientoVehiculo.parqueadero_id == parqueadero_id)

                contexto = {"lista_mov": mov_vehiculo}

                return render_template('/sitio/movimiento_vehiculos/ver_movimiento.html', context=contexto)

            minutos = int(divmod((fecha_salida.replace(tzinfo=utc) - vehicle_mov.fecha_ingreso.replace(tzinfo=utc)).total_seconds(), 60)[0])
        try:
            obj_vehicle = Vehiculo.query.filter(Vehiculo.placa==placa).first()
            if not obj_vehicle:
                vehiculo_id = None
                obj_tarifa = Tarifa.query.filter(Tarifa.tipo_vehiculo_id==vehicle_type, Tarifa.tipo_funcionario_id==1).first()
            else:
                vehiculo_id =  obj_vehicle.id

                obj_user = User.query.filter(User.id==obj_vehicle.user_id).first()
                obj_tarifa = Tarifa.query.filter(Tarifa.tipo_vehiculo_id==obj_vehicle.tipo_vehiculo_id, Tarifa.tipo_funcionario_id==obj_user.tipo_funcionario_id).first()

            if not obj_tarifa:
                flash('No se encontró una tarifa. Por favor verifique!', category='error')
                mov_vehiculo = MovimientoVehiculo.query.with_entities(MovimientoVehiculo.id, 
                                                        MovimientoVehiculo.estado, MovimientoVehiculo.placa,
                                                        MovimientoVehiculo.fecha_ingreso.label("ingreso"),
                                                        MovimientoVehiculo.fecha_salida.label("salida")).filter(MovimientoVehiculo.parqueadero_id == parqueadero_id)

                contexto = {"lista_mov": mov_vehiculo}

                return render_template('/sitio/movimiento_vehiculos/ver_movimiento.html', context=contexto)

            if hora_out:
                total_a_pagar = round(minutos * obj_tarifa.valor_minuto,0)

            if hora_in:
                new_mov = MovimientoVehiculo(fecha_ingreso= fecha_ingreso,
                                            estado= 'ingreso',
                                            placa= placa,
                                            tipo_vehiculo_id = vehicle_type,
                                            vehiculo_id= vehiculo_id,
                                            parqueadero_id= parqueadero_id)

                db.session.add(new_mov)
                db.session.commit()
            elif hora_out:
                vehicle_mov.fecha_salida= fecha_salida
                vehicle_mov.estado= 'salida'
                vehicle_mov.minutos= minutos

                new_fac = Factura(total_a_pagar= total_a_pagar,
                                    minutos= minutos,
                                    movimiento_id= vehicle_mov.id,
                                    parqueadero_id= parqueadero_id)
                db.session.add(new_fac)                
                db.session.commit()

        except BaseException as error:
            db.session.rollback()

        return redirect(url_for('mov_vehicles.get_mov_vehiculo'))
