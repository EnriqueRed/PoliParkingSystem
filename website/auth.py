from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from .models import User, Rol, Parqueadero
from .business.email_send import generate_confirmation_token, send_email, confirm_token

from . import db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(usuario=username).first()
        if user:
            if not user.confirmed:
                flash('Se debe confirmar la cuenta antes de ingresar. Por favor verifique!', category='error')
                return render_template('/admin/login.html')
            if check_password_hash(user.password, password):
                login_user(user, remember=True)

                session['user'] = {'usuario': user.usuario,
                                    'nombre': user.nombre,
                                    'rol': user.rol_id,
                                    'propietario': user.es_propietario,
                                    'parqueadero': user.parqueadero_id}

                return redirect(url_for('dashboard.inicio'))
            else:
                flash('El usuario o contraseña es inválido. Por favor verifique!', category='error')
        else:
            flash('El usuario no existe. Por favor verifique!', category='error')

    return render_template('/admin/login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    list_parking = Parqueadero.query.with_entities(Parqueadero.id, Parqueadero.nombre).all()
    lista_roles = Rol.query.with_entities(Rol.id, Rol.nombre).all()

    contexto = {"lista_roles": lista_roles,
                "lista_parking": list_parking}

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        if "@poligran.edu.co" in email:
            username = email[:email.find("@poligran.edu.co")]
        else:
            username = email
        password = request.form.get('password')
        confirmpassword = request.form.get('confirmpassword')
        propietario = bool(request.form.get('propietario'))

        if request.form.get('rol'):
            rol_id = int(request.form.get('rol'))
        else:
            rol_id = None
        
        if not request.form.get('parking'):
            parqueadero = None
        else:
            parqueadero = int(request.form.get('parking'))

        if not rol_id or rol_id == 1:
            parqueadero = None

        if password != confirmpassword:
            flash('Las contraseñas no coinciden. Por favor verifique!', category='error')
            return render_template('/admin/register.html', context=contexto)

        if not propietario:
            if '@poligran.edu.co' not in email:
                flash('El correo debe ser un correo asociado al Politécnico Grancolombiano. Por favor verifique!', category='error')
                return render_template('/admin/register.html', context=contexto)
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Ya existe un usuario con el correo ingresado. Por favor verifique!', category='error')
            return render_template('/admin/register.html', context=contexto)
        else:
            try:
                new_user = User(nombre= name,
                                email= email,
                                usuario= username,
                                password= generate_password_hash(password, method='sha256'),
                                es_propietario= propietario,
                                parqueadero_id= parqueadero,
                                rol_id= rol_id)
                db.session.add(new_user)
                
                token = generate_confirmation_token(new_user.email)
                confirm_url = url_for('auth.confirm_email', token=token, _external=True)
                html = render_template('sitio/user/confirmar_email.html', confirm_url=confirm_url)
                subject = "PoliParkingSystem. Confirmación de correo."
                send_email(new_user.email, subject, html)
                db.session.commit()

                flash('Un mensaje de confirmación de cuenta ha sido enviado a tu correo', 'success')
                return redirect(url_for('auth.login'))
            except BaseException as error:
                db.session.rollback()
    else:
        return render_template('/admin/register.html', context=contexto)

@auth.route('/logout')
@login_required
def logout():
    session.pop('user', None)
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/confirmar/<token>')
def confirm_email(token):
    try:
        email = confirm_token(token)

        if not email:
            return render_template('/sitio/Error404.html'), 404
    except:
        flash('El link de confirmaciòn no es válido o ha expirado. Por favor verifique!', 'error')

    user = User.query.filter_by(email=email).first_or_404()
    if user.confirmed:
        flash('La cuenta ha sido confirmada previamente. Si no puedes iniciar sesión contactate con el administrador del sitio.', 'success')
    else:
        user.confirmed = True
        db.session.add(user)
        db.session.commit()
        flash('Se ha confirmado la cuenta. Ya puedes iniciar sesión!', 'success')

    return redirect(url_for('auth.login'))

@auth.route('/change_password_email', methods=['GET', 'POST'])
def change_password_email():
    if request.method == 'POST':
        email = request.form.get('email')

        user = User.query.filter_by(email=email).first()

        if not user:
            flash('El correo digitado no es válido. Por favor verifique!', 'error')
            return redirect(url_for('auth.change_password_email'))
        
        if not user.confirmed:
            flash('El correo digitado no ha sido confirmado. Por favor verifique!', 'error')
            return redirect(url_for('auth.change_password_email'))

        try:
            token = generate_confirmation_token(user.email)
            confirm_url = url_for('auth.change_password', token=token, _external=True)
            html = render_template('sitio/user/cambiar_password.html', confirm_url=confirm_url)
            subject = "PoliParkingSystem. Actualización de contraseña."
            send_email(user.email, subject, html)
        except:
            flash('No fue posible enviar el correo para el cambio de contraseña. Por favor verifique!', 'error')
            return redirect(url_for('auth.change_password_email'))

        flash('Un mensaje fue enviado a su correo con el link para el cambio de contraseña', 'success')
        return redirect(url_for('auth.change_password_email'))
    else:
        return render_template('/admin/change_password_email.html')


@auth.route('/change_password/<token>', methods=['GET'])
def change_password(token):
    if request.method == 'GET':
        contexto = {"token": token}
        try:
            email = confirm_token(token)

            if not email:
                return render_template('/sitio/Error404.html'), 404
        except:
            flash('El link de cambio de contraseña no es válido o ha expirado. Por favor verifique!', 'error')        
            return redirect(url_for('auth.login'))

        return render_template('/admin/change_password.html', context=contexto)


@auth.route('/change_password_post', methods=['POST'])
def change_password_post():
    if request.method == 'POST':
        token = request.form.get('token')
        password = request.form.get('password')
        confirmpassword = request.form.get('confirmpassword')

        try:
            email = confirm_token(token)

            if not email:
                return render_template('/sitio/Error404.html'), 404
        except:
            flash('El link de cambio de contraseña no es válido o ha expirado. Por favor verifique!', 'error')
            return redirect(url_for('auth.login'))

        user = User.query.filter_by(email=email).first_or_404()

        if password != confirmpassword:
            flash('Las contraseñas no coinciden. Por favor verifique!', category='error')
            return render_template('/admin/change_password.html')

        try:
            user.password = generate_password_hash(password, method='sha256')
            db.session.commit()
        except BaseException as error:
            db.session.rollback()

        flash('La contraseña fue actualizada correctamente.', 'success')
        return redirect(url_for('auth.login'))