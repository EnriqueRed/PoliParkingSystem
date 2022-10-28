from email.policy import default
from enum import unique
import imp
from time import timezone
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

# Usuarios -----------------------------------------------------------------------------
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150))
    usuario = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))    
    imagen = db.Column(db.Text)
    rol_id = db.Column(db.Integer, db.ForeignKey('rol.id'))

# Roles
class Rol(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150))
    
# Vehículo -----------------------------------------------------------------------------
class Vehiculo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(10))
    imagen = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    tipo_vehiculo_id = db.Column(db.Integer, db.ForeignKey('tipovehiculo.id'))
    
# Tipo de vehículos
class Tipovehiculo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150))

# Movimiento de vehículos
class MovimientoVehiculo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha_ingreso = db.Column(db.DateTime(timezone=True), default=func.now())
    fecha_salida = db.Column(db.DateTime(timezone=True), default=func.now())
    estado = db.Column(db.String(20))
    vehiculo_id = db.Column(db.Integer, db.ForeignKey('vehiculo.id'))
    parqueadero_id = db.Column(db.Integer, db.ForeignKey('parqueadero.id'))

# Parqueaderos --------------------------------------------------------------------------
class Parqueadero(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150))
    capacidad_carros = db.Column(db.Integer)
    capacidad_motos = db.Column(db.Integer)
    