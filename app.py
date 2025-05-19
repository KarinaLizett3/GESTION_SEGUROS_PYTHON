from flask import Flask
from mi_app.auth.routes import auth_bp
from mi_app.paciente.routes import paciente_bp
from mi_app.administrador.routes import admin_bp
from mi_app.medico.routes import medico_bp 


app = Flask(__name__)
app = Flask(__name__, template_folder='mi_app/templates')
app.secret_key = 'clave_secreta_super_segura'  # Cambiar por una más segura en producción

# Registro de Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(paciente_bp, url_prefix='/paciente')
app.register_blueprint(medico_bp) 

# Ruta raíz
@app.route('/')
def index():
    return "<h2>Bienvenido al sistema. <a href='/auth/login'>Iniciar sesión</a></h2>"
# Imprimir rutas al inicio
@app.before_first_request
def listar_rutas():
    print("\n📍 RUTAS REGISTRADAS EN LA APLICACIÓN:\n")
    for regla in app.url_map.iter_rules():
        print(f"Endpoint: {regla.endpoint:30s} -> Ruta: {str(regla)}")
    print("\n")


if __name__ == '__main__':
    app.run(debug=True)

