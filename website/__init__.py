from flask import Flask, render_template
from decouple import config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from dotenv import load_dotenv
load_dotenv()
import os

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()

def create_app():
    # print()
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'Xp2s5v8y/B?E(H+MbQeThWmYq3t6w9z$C&F)J@NcRfUjXn2r4u7x!A%D*G-KaPdS'
    app.config['SECURITY_PASSWORD_SALT'] = 'W4yyhZVAPYkF03NR9cuMBJ2jxGDsVT'
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://poli:Poli_123@localhost/PoliParkingSystem"
    app.config['engine'] = db.create_engine("postgresql://poli:Poli_123@localhost/PoliParkingSystem",{})
    app.config['MAIL_SERVER']='smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USERNAME'] = 'poliparkingsystem@gmail.com'
    app.config['MAIL_DEFAULT_SENDER'] = 'poliparkingsystem@gmail.com'
    app.config['MAIL_PASSWORD'] = 'arptglmqmwlqxxjn'
    app.config['MAIL_USE_TLS'] = True
    db.init_app(app)

    # https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
    
    migrate.init_app(app, db)

    mail.init_app(app)
    
    from .views.main import main
    from .views.vehicles import vehicles
    from .views.parking import parkings
    from .views.tariff import tariff
    from .views.movvehicle import mov_vehicles
    from .views.dashboard import dashboard
    from .views.notifications import notifications
    from .auth import auth

    def not_found(e):
        return render_template('/sitio/Error404.html'), 404

    # Login Manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'

    app.register_error_handler(404, not_found)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    app.register_blueprint(main, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(vehicles, url_prefix='/')
    app.register_blueprint(parkings, url_prefix='/')
    app.register_blueprint(tariff, url_prefix='/')
    app.register_blueprint(mov_vehicles, url_prefix='/')
    app.register_blueprint(dashboard, url_prefix='/')
    app.register_blueprint(notifications, url_prefix='/')

    from .models import User, Rol

    return app