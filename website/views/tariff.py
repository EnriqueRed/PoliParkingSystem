from flask import Blueprint, current_app, render_template, jsonify, request, redirect, session, url_for 
from flask_login import login_required
from website.models import Tarifa, TipoFuncionario, Tipovehiculo
from sqlalchemy.sql import text
from .. import db

tariff = Blueprint('tariff', __name__)

# Tarifa ------------------------------------------------------------------------
@tariff.route('/tarifa', methods=['GET'])
@login_required
def get_tarifa():
    if session['user']['rol'] == 1:
        return render_template('/sitio/Error404.html'), 404

    tarifa_list = Tarifa.query.join(TipoFuncionario).join(Tipovehiculo).with_entities(Tarifa.id, Tarifa.nombre, Tipovehiculo.nombre.label("tipo_v"),
                                            Tarifa.valor_minuto, Tarifa.valor_plena, Tarifa.valor_mensualidad, TipoFuncionario.nombre.label("tipo_f")).filter(
                                                Tarifa.parqueadero_id == session['user']['parqueadero']
                                            )

    list_tipov = Tipovehiculo.query.all()
    list_func = TipoFuncionario.query.all()

    contexto = {"lista_tipof": list_func,
                "lista_tipov": list_tipov,
                "lista_tarifa": tarifa_list}    

    return render_template('/sitio/tarifa.html', context=contexto)

@tariff.route('/tarifa/crear', methods=['POST'])
@login_required
def crear_tarifa():
    if session['user']['rol'] == 1:
        return render_template('/sitio/Error404.html'), 404

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        tipo_v = int(request.form.get('tipo_v'))
        valor_minuto = request.form.get('valor_minuto')
        valor_plena = request.form.get('valor_plena')
        valor_mensualidad = request.form.get('valor_mensualidad')
        tipo_f = int(request.form.get('tipo_f'))
        parqueadero_id = session['user']['parqueadero']

        try:
            new_tariff = Tarifa(nombre= nombre,
                                tipo_vehiculo_id= tipo_v,
                                valor_minuto= valor_minuto,
                                valor_plena= valor_plena,
                                valor_mensualidad= valor_mensualidad,
                                tipo_funcionario_id= tipo_f,
                                parqueadero_id= parqueadero_id)
            db.session.add(new_tariff)

            db.session.commit()
        except BaseException as error:
            db.session.rollback()

        return redirect(url_for('tariff.get_tarifa'))

@tariff.route('/tarifa/editar', methods=['POST'])
@login_required
def editar_tarifa():
    if session['user']['rol'] == 1:
        return render_template('/sitio/Error404.html'), 404

    if request.method == 'POST':
        id_f = int(request.form.get('id_f'))
        nombre = request.form.get('nombre')
        tipo_v = int(request.form.get('tipo_v'))
        valor_minuto = float(request.form.get('valor_minuto'))
        valor_plena = float(request.form.get('valor_plena'))
        valor_mensualidad = float(request.form.get('valor_mensualidad'))
        tipo_f = int(request.form.get('tipo_f'))

        try:
            tmp_tariff = Tarifa.query.filter(Tarifa.id == id_f).first()
            tmp_tariff.nombre= nombre
            tmp_tariff.tipo_vehiculo_id= tipo_v
            tmp_tariff.valor_minuto= valor_minuto
            tmp_tariff.valor_plena= valor_plena
            tmp_tariff.valor_mensualidad= valor_mensualidad
            tmp_tariff.tipo_funcionario_id= tipo_f

            db.session.commit()
        except BaseException as error:
            db.session.rollback()

        return redirect(url_for('tariff.get_tarifa'))

@tariff.route('/ajax_get_tarifa_id', methods=['GET','POST'])
@login_required
def get_tarifa_id():
    if session['user']['rol'] == 1:
        return render_template('/sitio/Error404.html'), 404

    if request.form['tarifaid']:
        tarifaid = int(request.form['tarifaid'])
    else:
        tarifaid = 0

    tarifa = Tarifa.query.join(TipoFuncionario).join(Tipovehiculo).with_entities(Tarifa.id, Tarifa.nombre, Tipovehiculo.nombre.label("tipo_v"),
                                            Tarifa.valor_minuto, Tarifa.valor_plena, Tarifa.valor_mensualidad, Tipovehiculo.id.label("tipo_v_id"),
                                            TipoFuncionario.nombre.label("tipo_f"), TipoFuncionario.id.label("tipo_f_id")).filter(Tarifa.id == tarifaid).filter(
                                                Tarifa.parqueadero_id == session['user']['parqueadero']
                                            ).first()

    list_tipov = Tipovehiculo.query.all()
    list_func = TipoFuncionario.query.all()

    contexto = {"lista_tipof": list_func,
                "lista_tipov": list_tipov,
                "tariff": tarifa}

    return jsonify({'htmlresponse': render_template('/sitio/tarifa_response.html', context=contexto)})

@tariff.route('/ajax_delete_tarifa_id', methods=['GET','POST'])
@login_required
def delete_tarifa_id():
    if session['user']['rol'] == 1:
        return render_template('/sitio/Error404.html'), 404
        
    if request.form['tarifaid']:
        tarifaid = int(request.form['tarifaid'])
    else:
        tarifaid = 0

    try:
        Tarifa.query.filter(Tarifa.id == tarifaid).delete()
        db.session.commit()
    except BaseException as error:
        db.session.rollback()

    return jsonify('true')

