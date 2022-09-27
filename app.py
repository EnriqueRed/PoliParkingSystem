from flask import Flask
from flask import render_template

app=Flask(__name__)

# Index ---------------------------------------------------------------------------
@app.route('/')
def inicio():
    return render_template('sitio/index.html')

# Movimiento de vehículos ----------------------------------------------------------
# Registrar Ingreso
@app.route('/movimiento_vehiculos/registrar_ingreso')
def registrar_ingreso():
    return render_template('sitio/movimiento_vehiculos/registrar_ingreso.html')

# Registrar Salida
@app.route('/movimiento_vehiculos/registrar_salida')
def registrar_salida():
    return render_template('sitio/movimiento_vehiculos/registrar_salida.html')

# Ver Movimientos
@app.route('/movimiento_vehiculos/ver_movimiento')
def ver_movimiento():
    return render_template('sitio/movimiento_vehiculos/ver_movimiento.html')

# Páginas -------------------------------------------------------------------------
# Parqueaderos
@app.route('/parqueaderos')
def parqueadero():
    return render_template('sitio/parqueadero.html')


if __name__ == '__main__':
    app.run(debug=True)