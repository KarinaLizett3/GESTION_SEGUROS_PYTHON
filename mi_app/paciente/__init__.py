from flask import Blueprint

paciente_bp = Blueprint('paciente', __name__, template_folder='templates/paciente')


from . import routes
