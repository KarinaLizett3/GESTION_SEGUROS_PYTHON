from flask import Flask
from .administrador import admin_bp
from .auth import auth_bp
from .paciente import paciente_bp
from .main import main_bp
from mi_app.medico.routes import medico_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = 'tu_clave_secreta'

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(paciente_bp, url_prefix='/paciente')
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(medico_bp)

    return app

