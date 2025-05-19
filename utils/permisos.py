import sqlite3

from flask import session, redirect, url_for, flash

def verificar_acceso_restringido(roles_permitidos):
    def decorador(func):
        def envoltura(*args, **kwargs):
            if 'usuario_id' not in session or session.get('usuario_rol') not in roles_permitidos:
                flash('Acceso no autorizado.')
                return redirect(url_for('auth.login'))
            return func(*args, **kwargs)
        envoltura.__name__ = func.__name__
        return envoltura
    return decorador

def get_db_connection():
    conn = sqlite3.connect('base_datos.db')
    conn.row_factory = sqlite3.Row
    return conn

def tiene_permiso(usuario_id, permiso_nombre):
    conn = get_db_connection()
    query = '''
        SELECT 1
        FROM usuarios u
        JOIN roles r ON u.rol = r.nombre
        JOIN rol_permiso rp ON r.id = rp.rol_id
        JOIN permisos p ON rp.permiso_id = p.id
        WHERE u.id = ? AND p.nombre = ?
    '''
    resultado = conn.execute(query, (usuario_id, permiso_nombre)).fetchone()
    conn.close()
    return resultado is not None
