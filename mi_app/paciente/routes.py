from flask import render_template, redirect, url_for, flash, session, request
from . import paciente_bp
import sqlite3

def get_db_connection():
    conn = sqlite3.connect('base_datos.db')
    conn.row_factory = sqlite3.Row
    return conn

# Dashboard principal
@paciente_bp.route('/dashboard')
def dashboard():
    if 'usuario_id' not in session or session.get('usuario_rol') != 'paciente':
        flash('Acceso no autorizado.')
        return redirect(url_for('auth.login'))

    usuario_id = session['usuario_id']
    conn = get_db_connection()
    paciente = conn.execute('SELECT * FROM pacientes WHERE usuario_id = ?', (usuario_id,)).fetchone()
    conn.close()

    if not paciente:
        flash("No se encontraron datos del paciente.")
        return redirect(url_for('auth.login'))

    return render_template('paciente/dashboard.html', paciente=paciente, usuario=session.get('usuario_nombre'))

@paciente_bp.route('/editar', methods=['GET', 'POST'])
def editar_datos():
    if 'usuario_id' not in session or session.get('usuario_rol') != 'paciente':
        flash('Acceso no autorizado.')
        return redirect(url_for('auth.login'))

    usuario_id = session['usuario_id']
    conn = get_db_connection()
    paciente = conn.execute('SELECT * FROM pacientes WHERE usuario_id = ?', (usuario_id,)).fetchone()

    if request.method == 'POST':
        nombre = request.form['nombre']
        fecha_nacimiento = request.form['fecha_nacimiento']
        nss = request.form['nss']
        telefono = request.form['telefono']
        direccion = request.form['direccion']

        conn.execute('''
            UPDATE pacientes
            SET nombre = ?, fecha_nacimiento = ?, nss = ?, telefono = ?, direccion = ?
            WHERE usuario_id = ?
        ''', (nombre, fecha_nacimiento, nss, telefono, direccion, usuario_id))
        conn.commit()
        conn.close()

        flash("Tus datos han sido actualizados.")
        return redirect(url_for('paciente.dashboard'))

    conn.close()
    return render_template('paciente/editar.html', paciente=paciente)

@paciente_bp.route('/historial')
def historial():
    if 'usuario_id' not in session or session.get('usuario_rol') != 'paciente':
        flash('Acceso no autorizado.')
        return redirect(url_for('auth.login'))

    usuario_id = session['usuario_id']
    conn = get_db_connection()

    # Obtener ID del paciente
    paciente = conn.execute('SELECT id FROM pacientes WHERE usuario_id = ?', (usuario_id,)).fetchone()
    if not paciente:
        flash("No se encontró información del paciente.")
        conn.close()
        return redirect(url_for('paciente.dashboard'))

    paciente_id = paciente['id']

    # Obtener historial de consultas
    consultas = conn.execute('''
        SELECT c.fecha, m.nombre AS medico, c.descripcion
        FROM consultas c
        JOIN medicos m ON c.medico_id = m.id
        WHERE c.paciente_id = ?
        ORDER BY c.fecha DESC
    ''', (paciente_id,)).fetchall()

    # Obtener antecedentes médicos
    antecedentes = conn.execute('''
        SELECT fecha_registro, tipo, descripcion
        FROM antecedentes_medicos
        WHERE paciente_id = ?
        ORDER BY fecha_registro DESC
    ''', (paciente_id,)).fetchall()

    conn.close()

    return render_template('paciente/historial.html', consultas=consultas, antecedentes=antecedentes)

