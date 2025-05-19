from functools import wraps
from flask import session, redirect, url_for, flash

def login_requerido(rol_requerido):
    def decorador(f):
        @wraps(f)
        def decorada(*args, **kwargs):
            if 'usuario_rol' not in session:
                flash("Debes iniciar sesión primero.")
                return redirect(url_for('auth.login'))
            elif session['usuario_rol'] != rol_requerido:
                flash("Acceso no autorizado para este rol.")
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorada
    return decorador
