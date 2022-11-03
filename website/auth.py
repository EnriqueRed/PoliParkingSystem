from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from .models import User, Rol, Parqueadero
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
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        username = email[:email.find("@poligran.edu.co")]
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
                                parqueadero_id= parqueadero,
                                rol_id= rol_id)
                db.session.add(new_user)
                db.session.commit()
            except:
                db.session.rollback()

            session['user'] = {'usuario': new_user.usuario,
                                'nombre': new_user.nombre,
                                'rol': new_user.rol_id,
                                'propietario': new_user.es_propietario,
                                'parqueadero': user.parqueadero_id}

            login_user(new_user, remember=True)
            return redirect(url_for('dashboard.inicio'))
    else:
        list_parking = Parqueadero.query.with_entities(Parqueadero.id, Parqueadero.nombre).all()
        lista_roles = Rol.query.with_entities(Rol.id, Rol.nombre).all()

        contexto = {"lista_roles": lista_roles,
                    "lista_parking": list_parking}

        return render_template('/admin/register.html', context=contexto)

@auth.route('/logout')
@login_required
def logout():
    session.pop('user', None)
    logout_user()
    return redirect(url_for('auth.login'))