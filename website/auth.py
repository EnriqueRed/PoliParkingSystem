from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from .models import User
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(usuario=username).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)

                session['username'] = user.usuario
                session['parking'] = user.parqueadero_id

                return redirect(url_for('main.inicio'))
            else:
                flash('El usuario o contraseña es inválido. Por favor verifique!', category='error')
        else:
            flash('El usuario no existe. Por favor verifique!', category='error')

    return render_template('/admin/login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        username = email[:email.find("@poligran.edu.co")]
        password = request.form.get('password')
        confirmpassword = request.form.get('confirmpassword')
        propietario = bool(request.form.get('propietario'))
        
        if not request.form.get('parqueadero'):
            parqueadero = None
        else:
            parqueadero = int(request.form.get('parqueadero'))

        if password != confirmpassword:
            flash('Las contraseñas no coinciden. Por favor verifique!', category='error')
            return render_template('/admin/register.html')

        if not propietario:
            if '@poligran.edu.co' not in email:
                flash('El correo debe ser un correo asociado al Politécnico Grancolombiano. Por favor verifique!', category='error')
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Ya existe un usuario con el correo ingresado. Por favor verifique!', category='error')
            return render_template('/admin/register.html')
        else:
            try:
                new_user = User(nombre= name,
                                email= email,
                                usuario= username,
                                password= generate_password_hash(password, method='sha256'),
                                es_propietario= propietario,
                                parqueadero_id= parqueadero)
                db.session.add(new_user)
                db.session.commit()
            except:
                db.session.rollback()

            session['username'] = new_user.usuario
            session['parking'] = new_user.parqueadero_id

            login_user(new_user, remember=True)
            return redirect(url_for('main.inicio'))

    return render_template('/admin/register.html')

@auth.route('/logout')
@login_required
def logout():
    session.pop('username', None)
    session.pop('parking', None)
    logout_user()
    return redirect(url_for('auth.login'))