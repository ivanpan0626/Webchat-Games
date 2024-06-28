from flask import Flask
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from os import path
from flask_socketio import SocketIO
from flask_login import LoginManager

socketio = SocketIO()
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    CORS(app, supports_credentials=True)
    login_manager.init_app(app)
    socketio.init_app(app)
    db.init_app(app)

    from server.auth import auth
    from server.chat import chat
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(chat, url_prefix='/')

    from .models import User
    login_manager.login_view = 'auth.login'
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(id)

    with app.app_context():
        db.create_all()

    return app

def create_database(app):
    if not path.exists('server/mydatabase.db'):
        db.create_all(app=app)
        print('Created Database!')