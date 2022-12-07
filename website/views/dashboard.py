from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from flask import Blueprint, current_app, render_template, jsonify, request, redirect, session, url_for
from flask_login import login_required
from sqlalchemy.sql import text
from website.models import Vehiculo, Tipovehiculo, User, MovimientoVehiculo
from .. import db
import pandas as pd
import json

dashboard = Blueprint('dashboard', __name__)

# Dashboard ------------------------------------------------------------------------
@dashboard.route('/inicio')
@login_required
def inicio():
    if session['user']['rol'] == 1:
        return render_template('/sitio/Error404.html'), 404

    mov_in = get_vehiculo_in(1,2)
    mov_out = get_vehiculo_out(1,2)
    users_i = get_users_indic(1,2)
    mov_r = get_recent_mov(1)
    data = get_trafico_vehiculo()
    dias_c = get_dias_concurridos()

    contexto = {"mov_in": mov_in,
                "mov_out": mov_out,
                "users_i": users_i,
                "mov_r": mov_r,
                "data": data,
                "dias_c": dias_c}

    return render_template('/sitio/index.html', context=contexto)

def get_dates_option(optionid):
    if optionid == 1:
        date_ini = datetime.today().replace(hour=0,minute=0,second=0,microsecond=0)
        date_fin = datetime.today().replace(hour=23,minute=59,second=59,microsecond=0)
        date_ini_ant = date_ini - timedelta(days=1)
        date_fin_ant = date_fin - timedelta(days=1)
        filtro = 'Hoy'
        interval = 'día'   
    elif optionid == 2:
        date_ini = datetime.today().replace(day=1,hour=0,minute=0,second=0,microsecond=0)
        date_fin = date_ini + relativedelta(months=1) - timedelta(days=1)
        date_ini_ant = date_ini - relativedelta(months=1)
        date_fin_ant = date_ini - timedelta(days=1)
        filtro = 'Mes'
        interval = 'mes'
    else:
        date_ini = datetime.today().replace(day=1,month=1,hour=0,minute=0,second=0,microsecond=0)
        date_fin = date_ini.replace(day=31,month=12,hour=23,minute=59,second=59,microsecond=0)
        date_ini_ant = date_ini - relativedelta(year=1)
        date_fin_ant = date_fin - relativedelta(year=1)
        filtro = 'Año'
        interval = 'año'
    
    return date_ini,date_fin,date_ini_ant,date_fin_ant,filtro,interval


@dashboard.route('/ajax_get_vehiculo_in', methods=['GET','POST'])
@login_required
def get_vehiculo_in(return_context=0,optionid=0):
    if session['user']['rol'] == 1:
        return render_template('/sitio/Error404.html'), 404

    if not optionid:
        if request.form['optionid']:
            optionid = int(request.form['optionid'])
        else:
            optionid = 0

    date_ini,date_fin,date_ini_ant,date_fin_ant,filtro,interval = get_dates_option(optionid=optionid)

    mov_vehiculo = MovimientoVehiculo.query.filter(MovimientoVehiculo.parqueadero_id == session['user']['parqueadero'],
                                                MovimientoVehiculo.fecha_ingreso >= date_ini, 
                                                MovimientoVehiculo.fecha_ingreso <= date_fin)    
    mov_vehiculo_ant = MovimientoVehiculo.query.filter(MovimientoVehiculo.parqueadero_id == session['user']['parqueadero'],
                                                MovimientoVehiculo.fecha_ingreso >= date_ini_ant,
                                                MovimientoVehiculo.fecha_ingreso <= date_fin_ant)

    cantidad_act = mov_vehiculo.count()
    cantidad_ant = mov_vehiculo_ant.count()

    cantidad = cantidad_act - cantidad_ant

    if cantidad > 0:
        descripcion = 'Más con respecto al ' + interval + ' anterior'
    elif cantidad < 0:
        descripcion = 'Ménos con respecto al ' + interval + ' anterior'
    else:
        descripcion = 'Sin variación con respecto al ' + interval + ' anterior' 

    contexto = {"filtro": filtro,
                "cantidad": cantidad_act,
                "variacion": abs(cantidad),
                "descripcion": descripcion}

    if return_context:
        return contexto

    return jsonify({'htmlresponse': render_template('/sitio/dashboard/vehiculo_ingreso.html', context=contexto)})


@dashboard.route('/ajax_get_vehiculo_out', methods=['GET','POST'])
@login_required
def get_vehiculo_out(return_context=0,optionid=0):
    if session['user']['rol'] == 1:
        return render_template('/sitio/Error404.html'), 404

    if not optionid:
        if request.form['optionid']:
            optionid = int(request.form['optionid'])
        else:
            optionid = 0

    date_ini,date_fin,date_ini_ant,date_fin_ant,filtro,interval = get_dates_option(optionid=optionid)

    mov_vehiculo = MovimientoVehiculo.query.filter(MovimientoVehiculo.parqueadero_id == session['user']['parqueadero'],
                                                    MovimientoVehiculo.fecha_salida >= date_ini,
                                                    MovimientoVehiculo.fecha_salida <= date_fin,
                                                    MovimientoVehiculo.estado=='salida')
    mov_vehiculo_ant = MovimientoVehiculo.query.filter(MovimientoVehiculo.parqueadero_id == session['user']['parqueadero'],
                                                    MovimientoVehiculo.fecha_salida >= date_ini_ant,
                                                    MovimientoVehiculo.fecha_salida <= date_fin_ant,
                                                    MovimientoVehiculo.estado=='salida')

    cantidad_act = mov_vehiculo.count()
    cantidad_ant = mov_vehiculo_ant.count()

    cantidad = cantidad_act - cantidad_ant

    if cantidad > 0:
        descripcion = 'Más con respecto al ' + interval + ' anterior'
    elif cantidad < 0:
        descripcion = 'Ménos con respecto al ' + interval + ' anterior'
    else:
        descripcion = 'Sin variación con respecto al ' + interval + ' anterior' 

    contexto = {"filtro": filtro,
                "cantidad": cantidad_act,
                "variacion": abs(cantidad),
                "descripcion": descripcion}  

    if return_context:
        return contexto  

    return jsonify({'htmlresponse': render_template('/sitio/dashboard/vehiculo_salida.html', context=contexto)})


@dashboard.route('/ajax_get_users_indic', methods=['GET','POST'])
@login_required
def get_users_indic(return_context=0,optionid=0):
    if session['user']['rol'] == 1:
        return render_template('/sitio/Error404.html'), 404

    if not optionid:
        if request.form['optionid']:
            optionid = int(request.form['optionid'])
        else:
            optionid = 0

    date_ini,date_fin,date_ini_ant,date_fin_ant,filtro,interval = get_dates_option(optionid=optionid)

    usuarios = User.query.filter(User.fecha_creacion >= date_ini).filter(User.fecha_creacion <= date_fin)
    usuarios_ant = User.query.filter(User.fecha_creacion >= date_ini_ant).filter(User.fecha_creacion <= date_fin_ant)

    cantidad_act = usuarios.count()
    cantidad_ant = usuarios_ant.count()

    cantidad = cantidad_act - cantidad_ant

    if cantidad > 0:
        descripcion = 'Más con respecto al ' + interval + ' anterior'
    elif cantidad < 0:
        descripcion = 'Ménos con respecto al ' + interval + ' anterior'
    else:
        descripcion = 'Sin variación con respecto al ' + interval + ' anterior' 

    contexto = {"filtro": filtro,
                "cantidad": cantidad_act,
                "variacion": abs(cantidad),
                "descripcion": descripcion}  

    if return_context:
        return contexto  

    return jsonify({'htmlresponse': render_template('/sitio/dashboard/indicador_usuarios.html', context=contexto)})

@dashboard.route('/ajax_get_recent_mov', methods=['GET','POST'])
@login_required
def get_recent_mov(return_context=0):
    if session['user']['rol'] == 1:
        return render_template('/sitio/Error404.html'), 404

    sql = '''
        select A.id, coalesce(C.nombre, 'No registrado') as nombre, A.placa,
                coalesce(substring(cast(A.fecha_ingreso as varchar(50)), 12,5), '-') as ingreso,
                coalesce(substring(cast(A.fecha_salida  as varchar(50)), 12,5), '-') as salida,
                A.estado 
        from movimiento_vehiculo A
        left join vehiculo B on A.vehiculo_id = B.id 
        left join "user" C on B.user_id = C.id
        where A.parqueadero_id = %s
        order by estado asc, id desc
        limit 5
    ''' % (session['user']['parqueadero'])

    engine = current_app.config.get('engine')
    with engine.connect().execution_options(autocommit=True) as conn:
        query = conn.execute(text(sql))         
    recent_mov = query.fetchall()

    contexto = {"recent_mov": recent_mov}  

    if return_context:
        return contexto  

    return jsonify({'htmlresponse': render_template('/sitio/dashboard/movimiento_reciente.html', context=contexto)})


@dashboard.route('/ajax_get_trafico_vehiculo', methods=['GET','POST'])
@login_required
def get_trafico_vehiculo():
    if session['user']['rol'] == 1:
        return render_template('/sitio/Error404.html'), 404

    park_id = session['user']['parqueadero']

    sql = '''
            select count(A.id) as cant, '06:00 - 10:00' as rango
            from movimiento_vehiculo A
            where A.parqueadero_id = %s
                    and to_timestamp(substring(cast(A.fecha_ingreso as varchar(50)), 12,5), 'HH24:MI')::time between '06:00' and '10:00'
            union all
            select count(A.id) as cant, '10:00 - 14:00' as rango
            from movimiento_vehiculo A
            where A.parqueadero_id = %s
                    and to_timestamp(substring(cast(A.fecha_ingreso as varchar(50)), 12,5), 'HH24:MI')::time between '10:00' and '14:00'
            union all
            select count(A.id) as cant, '14:00 - 18:00' as rango
            from movimiento_vehiculo A
            where A.parqueadero_id = %s
                    and to_timestamp(substring(cast(A.fecha_ingreso as varchar(50)), 12,5), 'HH24:MI')::time between '14:00' and '18:00'
            union all
            select count(A.id) as cant, '18:00 - 22:00' as rango
            from movimiento_vehiculo A
            where A.parqueadero_id = %s
                    and to_timestamp(substring(cast(A.fecha_ingreso as varchar(50)), 12,5), 'HH24:MI')::time between '18:00' and '22:00'
    ''' % (park_id, park_id, park_id, park_id) 

    engine = current_app.config.get('engine')
    with engine.connect().execution_options(autocommit=True) as conn:
        query = conn.execute(text(sql))         
    traffic_veh = query.fetchall()

    data=[]
    
    for row in traffic_veh:
        data.append(row[0])

    contexto = {"datos": data}  

    return contexto  

    # return jsonify({'htmlresponse': render_template('/sitio/dashboard/trafico_vehiculos.html', context=contexto)})

@dashboard.route('/ajax_get_dias_concurridos', methods=['GET','POST'])
@login_required
def get_dias_concurridos():
    if session['user']['rol'] == 1:
        return render_template('/sitio/Error404.html'), 404
        
    sql = '''
        select * 
        from 
        (
            select fecha_ingreso::TIMESTAMP::DATE as fecha, count(A.id) as cantidad, sum(minutos) / 60 as horas
            from movimiento_vehiculo A
            where A.parqueadero_id = %s
            group by fecha_ingreso::TIMESTAMP::DATE 
        ) A
        order by horas desc
        limit 3
    ''' % (session['user']['parqueadero'])
    
    engine = current_app.config.get('engine')
    with engine.connect().execution_options(autocommit=True) as conn:
        query = conn.execute(text(sql))         
    dias_concurridos = query.fetchall()

    contexto = {"dias_concurridos": dias_concurridos}  
    return contexto  
