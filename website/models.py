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
    es_propietario = db.Column(db.Boolean)
    parqueadero_id = db.Column(db.Integer, db.ForeignKey('parqueadero.id'))
    fecha_creacion = db.Column(db.DateTime(timezone=True), server_default=func.now())
    confirmed = db.Column(db.Boolean, default=False)
    tipo_funcionario_id = db.Column(db.Integer, db.ForeignKey('tipo_funcionario.id'))

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
    fecha_ingreso = db.Column(db.DateTime(timezone=False))
    fecha_salida = db.Column(db.DateTime(timezone=False))
    estado = db.Column(db.String(20))
    minutos = db.Column(db.Integer)
    vehiculo_id = db.Column(db.Integer, db.ForeignKey('vehiculo.id'))
    parqueadero_id = db.Column(db.Integer, db.ForeignKey('parqueadero.id'))

# Parqueaderos --------------------------------------------------------------------------
class Parqueadero(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150))
    direccion = db.Column(db.String(200))
    capacidad_carros = db.Column(db.Integer)
    capacidad_motos = db.Column(db.Integer)
    url_mapa = db.Column(db.Text)

# Tipo de funcionario --------------------------------------------------------------------------
class TipoFuncionario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150))

# Factura --------------------------------------------------------------------------
class Factura(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    total_a_pagar = db.Column(db.Numeric(20,2))
    movimiento_id = db.Column(db.Integer, db.ForeignKey('movimiento_vehiculo.id'))
    parqueadero_id = db.Column(db.Integer, db.ForeignKey('parqueadero.id'))

# Tarifas --------------------------------------------------------------------------
class Tarifa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150))
    tipo_vehiculo_id = db.Column(db.Integer, db.ForeignKey('tipovehiculo.id'))
    valor_minuto = db.Column(db.Numeric(10,2))
    valor_plena = db.Column(db.Numeric(10,2))
    valor_mensualidad = db.Column(db.Numeric(10,2))
    tipo_funcionario_id = db.Column(db.Integer, db.ForeignKey('tipo_funcionario.id'))

