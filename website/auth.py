from flask import Blueprint, render_template, request, flash, redirect, url_for
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
                return redirect(url_for('views.inicio'))
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

        if password != confirmpassword:
            flash('Las contraseñas no coinciden. Por favor verifique!', category='error')
            return render_template('/admin/register.html')

        if '@poligran.edu.co' not in email:
            flash('El correo debe ser un correo asociado al Politécnico Grancolombiano. Por favor verifique!', category='error')
        else:
            user = User.query.filter_by(email=email).first()
            if user:
                flash('Ya existe un usuario con el correo ingresado. Por favor verifique!', category='error')
                return render_template('/admin/register.html')
            else:
                try:
                    new_user = User(nombre= name,
                                    email= email,
                                    usuario= username,
                                    password= generate_password_hash(password, method='sha256'))
                    db.session.add(new_user)
                    db.session.commit()
                except:
                    db.session.rollback()

                login_user(new_user, remember=True)
                return redirect(url_for('views.inicio'))
    
    return render_template('/admin/register.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))