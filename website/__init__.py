from flask import Flask
from decouple import config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'Xp2s5v8y/B?E(H+MbQeThWmYq3t6w9z$C&F)J@NcRfUjXn2r4u7x!A%D*G-KaPdS'
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://poli:Poli_123@localhost/PoliParkingSystem"
    app.config['engine'] = db.create_engine("postgresql://poli:Poli_123@localhost/PoliParkingSystem",{})
    db.init_app(app)
    
    migrate.init_app(app, db)
    
    from .views.main import main
    from .views.vehicles import vehicles
    from .views.parking import parkings
    from .views.movvehicle import mov_vehicles
    from .views.dashboard import dashboard
    from .auth import auth

    # Login Manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    app.register_blueprint(main, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(vehicles, url_prefix='/')
    app.register_blueprint(parkings, url_prefix='/')
    app.register_blueprint(mov_vehicles, url_prefix='/')
    app.register_blueprint(dashboard, url_prefix='/')

    from .models import User, Rol

    return app