# app/administrador/routes.py
from flask import render_template, session, redirect, url_for, flash, request
from . import admin_bp
from utils.permisos import tiene_permiso
from utils.permisos import verificar_acceso_restringido
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from datetime import datetime
import sqlite3


def get_db_connection():
    conn = sqlite3.connect('base_datos.db')
    conn.row_factory = sqlite3.Row
    return conn

@admin_bp.route('/dashboard')
def dashboard():
    if 'usuario_id' not in session or session.get('usuario_rol') != 'administrador':
        flash('Acceso no autorizado.')
        return redirect(url_for('auth.login'))
    return render_template('administrador/dashboard.html', usuario=session.get('usuario_nombre'))

@admin_bp.route('/usuarios')
@verificar_acceso_restringido(['administrador'])
def listar_usuarios():
    if 'usuario_id' not in session or session.get('usuario_rol') != 'administrador':
        flash('Acceso no autorizado.')
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    usuarios = conn.execute('SELECT * FROM usuarios').fetchall()
    conn.close()
    return render_template('administrador/listar_usuarios.html', usuarios=usuarios)

@admin_bp.route('/usuarios/editar/<int:id>', methods=['GET', 'POST'])
def editar_usuario(id):
    if 'usuario_id' not in session or session.get('usuario_rol') != 'administrador':
        flash('Acceso no autorizado.')
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    usuario = conn.execute('SELECT * FROM usuarios WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        rol = request.form['rol']

        conn.execute('''
            UPDATE usuarios SET nombre = ?, email = ?, rol = ? WHERE id = ?
        ''', (nombre, email, rol, id))
        conn.commit()
        conn.close()
        flash('Usuario actualizado correctamente.')
        return redirect(url_for('admin.listar_usuarios'))

    conn.close()
    return render_template('administrador/editar_usuario.html', usuario=usuario)


@admin_bp.route('/usuarios/eliminar/<int:id>', methods=['GET'])
def eliminar_usuario(id):
    if 'usuario_id' not in session or session.get('usuario_rol') != 'administrador':
        flash('Acceso no autorizado.')
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM usuarios WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Usuario eliminado correctamente.')
    return redirect(url_for('admin.listar_usuarios'))

@admin_bp.route('/usuarios/registrar', methods=['GET', 'POST'])
def registrar_usuario():
    if 'usuario_id' not in session or session.get('usuario_rol') != 'administrador':
        flash('Acceso no autorizado.')
        return redirect(url_for('auth.login'))

    error = None
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        contrasena = request.form['contrasena']
        rol = request.form['rol']

        if not nombre or not email or not contrasena or not rol:
            error = "Todos los campos son obligatorios."
        else:
            try:
                conn = get_db_connection()
                hashed_password = generate_password_hash(contrasena)
                fecha_registro = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                conn.execute('''
                    INSERT INTO usuarios (nombre, email, contrasena, rol, fecha_registro)
                    VALUES (?, ?, ?, ?, ?)
                ''', (nombre, email, hashed_password, rol, fecha_registro))
                conn.commit()
                conn.close()
                flash("Usuario registrado exitosamente.")
                return redirect(url_for('admin.listar_usuarios'))
            except sqlite3.IntegrityError:
                error = "El correo ya está registrado."

    return render_template('administrador/registrar_usuario.html', error=error)

