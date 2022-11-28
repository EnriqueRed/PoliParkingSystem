from cmath import e
from tkinter import E
from flask import Blueprint, render_template, flash, request
from flask_login import login_required
from website.models import Notificacion, Vehiculo, User, Tipovehiculo
from ..business.email_send import send_email
from .. import db

notifications = Blueprint('notifications', __name__)

# Notificacion ------------------------------------------------------------------------
@notifications.route('/notificacion/crear', methods=['GET','POST'])
@login_required
def crear_notificacion():
    user_list = Vehiculo.query.join(User).join(Tipovehiculo).with_entities(User.id, Vehiculo.placa,User.usuario, User.email,Tipovehiculo.nombre.label("tipo")).order_by(Vehiculo.placa)
    contexto = {"lista_usuario": user_list}    

    if request.method == 'POST':
        usuario = int(request.form.get('usuario'))
        asunto = request.form.get('asunto')
        mensaje = request.form.get('mensaje')
        enviar_correo = True # request.form.get('enviar_correo')

        try:
            new_notification = Notificacion(asunto= asunto,
                                    mensaje= mensaje,
                                    user_id= usuario)
            db.session.add(new_notification)

            db.session.commit()

            if enviar_correo:
                user = User.query.filter_by(id=usuario).first_or_404()

                html = render_template('sitio/notificacion_correo.html', context=mensaje)
                subject = "PoliParkingSystem. Confirmación de correo."
                send_email(user.email, subject, html)
        except BaseException as error:
            db.session.rollback()
            flash('No fue posible enviar el mensaje al usuario. Intente nuevamente en unos minutos', category='error')

    flash('Mensaje enviado correctamente!', category='success')
    return render_template('/sitio/notificacion.html', context=contexto)
