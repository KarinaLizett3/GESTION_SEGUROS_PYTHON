from flask import Blueprint, render_template, session, redirect, url_for, flash,request
from flask import send_file
import sqlite3
import csv
import io
import pandas as pd
import csv
from flask import Response, session, flash, redirect, url_for
import pandas as pd
from flask import send_file
from io import BytesIO

medico_bp = Blueprint('medico', __name__, url_prefix='/medico')

def get_db_connection():
    conn = sqlite3.connect('base_datos.db')
    conn.row_factory = sqlite3.Row
    return conn

@medico_bp.route('/dashboard')
def dashboard():
    if 'usuario_id' not in session or session.get('usuario_rol') != 'medico':
        flash("Acceso no autorizado.")
        return redirect(url_for('auth.login'))
    return render_template('medico/dashboard.html', nombre=session.get('usuario_nombre'))

@medico_bp.route('/agrega', methods=['GET', 'POST'])
def registrar_consulta():
    if 'usuario_id' not in session or session.get('usuario_rol') != 'medico':
        flash("Acceso no autorizado.")
        return redirect(url_for('auth.login'))

    conn = sqlite3.connect('base_datos.db')
    pacientes = conn.execute('SELECT id, nombre FROM pacientes').fetchall()

    if request.method == 'POST':
        paciente_id = request.form['paciente_id']
        fecha = request.form['fecha']
        motivo = request.form['motivo']
        sintomas = request.form['sintomas']
        diagnostico = request.form['diagnostico']
        tratamiento = request.form['tratamiento']
        consulta_actual = request.form['consulta_actual']
        consulta_proxima = request.form['consulta_proxima']
        medico_id = session['usuario_id']

        

        conn.execute('''
            INSERT INTO consultas (paciente_id, medico_id, fecha, motivo, sintomas, diagnostico, tratamiento, consulta_actual, consulta_proxima)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (paciente_id, medico_id, fecha, motivo, sintomas, diagnostico, tratamiento, consulta_actual, consulta_proxima))
        conn.commit()
        conn.close()

        flash("Consulta registrada exitosamente.")
        return redirect(url_for('medico.dashboard'))

    conn.close()
    return render_template('medico/agregar.html', pacientes=pacientes)

@medico_bp.route('/registrar_paciente', methods=['GET', 'POST'])
def registrar_paciente():
    if 'usuario_id' not in session or session.get('usuario_rol') != 'medico':
        flash("Acceso no autorizado.")
        return redirect(url_for('auth.login'))

    conn = sqlite3.connect('base_datos.db')
    conn.row_factory = sqlite3.Row
    usuarios = conn.execute("SELECT id, nombre FROM usuarios WHERE rol = 'paciente'").fetchall()

    if request.method == 'POST':
        usuario_id = request.form['usuario_id']
        nombre = request.form['nombre']
        fecha_nacimiento = request.form['fecha_nacimiento']
        nss = request.form['nss']
        telefono = request.form['telefono']
        direccion = request.form['direccion']

        conn.execute('''
            INSERT INTO pacientes (usuario_id, nombre, fecha_nacimiento, nss, telefono, direccion)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (usuario_id, nombre, fecha_nacimiento, nss, telefono, direccion))
        conn.commit()
        conn.close()

        flash("Paciente registrado exitosamente.")
        return redirect(url_for('medico.dashboard'))

    conn.close()
    return render_template('medico/registrar_paciente.html', usuarios=usuarios)

@medico_bp.route('/pacientes')
def mostrar_pacientes():
    if 'usuario_id' not in session or session.get('usuario_rol') != 'medico':
        flash("Acceso no autorizado.")
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    # Trae  el nombre del usuario para mostrar en la tabla
    pacientes = conn.execute('''
        SELECT p.*, u.nombre AS usuario_nombre
        FROM pacientes p
        JOIN usuarios u ON p.usuario_id = u.id
    ''').fetchall()
    conn.close()

    return render_template('medico/listar.html', pacientes=pacientes)


@medico_bp.route('/editar_paciente/<int:paciente_id>', methods=['GET', 'POST'])
def actualizar_paciente(paciente_id):
    if 'usuario_id' not in session or session.get('usuario_rol') != 'medico':
        flash("Acceso no autorizado.")
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    paciente = conn.execute('SELECT * FROM pacientes WHERE id = ?', (paciente_id,)).fetchone()

    if paciente is None:
        flash("Paciente no encontrado.")
        return redirect(url_for('medico.listar_pacientes'))

    if request.method == 'POST':
        nombre = request.form['nombre']
        fecha_nacimiento = request.form['fecha_nacimiento']
        nss = request.form['nss']
        telefono = request.form['telefono']
        direccion = request.form['direccion']

        conn.execute('''
            UPDATE pacientes
            SET nombre = ?, fecha_nacimiento = ?, nss = ?, telefono = ?, direccion = ?
            WHERE id = ?
        ''', (nombre, fecha_nacimiento, nss, telefono, direccion, paciente_id))
        conn.commit()
        conn.close()
        flash("Paciente actualizado exitosamente.")
        return redirect(url_for('medico.listar_pacientes'))

    conn.close()
    return render_template('medico/editar.html', paciente=paciente)

@medico_bp.route('/listar_pacientes')
def listar_pacientes():
    if 'usuario_id' not in session or session.get('usuario_rol') != 'medico':
        flash("Acceso no autorizado.")
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    pacientes = conn.execute('SELECT * FROM pacientes').fetchall()
    conn.close()

    return render_template('medico/listar_pacientes.html', pacientes=pacientes)


@medico_bp.route('/eliminar_paciente/<int:paciente_id>', methods=['POST'])
def eliminar_paciente(paciente_id):
    if 'usuario_id' not in session or session.get('usuario_rol') != 'medico':
        flash("Acceso no autorizado.")
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM pacientes WHERE id = ?', (paciente_id,))
    conn.commit()
    conn.close()

    flash("Paciente eliminado exitosamente.")
    return redirect(url_for('medico.listar_pacientes'))

@medico_bp.route('/reporte_consultas')
def reporte_consultas():
    if 'usuario_id' not in session or session.get('usuario_rol') != 'medico':
        flash("Acceso no autorizado.")
        return redirect(url_for('auth.login'))

    conn = sqlite3.connect('base_datos.db')
    conn.row_factory = sqlite3.Row

    # Obtener el ID del médico asociado al usuario actual
    medico = conn.execute('SELECT id FROM medicos WHERE usuario_id = ?', (session['usuario_id'],)).fetchone()

    if not medico:
        conn.close()
        flash("No se encontró el médico asociado a este usuario.")
        return redirect(url_for('medico.dashboard'))

    consultas = conn.execute('''
        SELECT 
            c.fecha,
            c.motivo,
            c.sintomas,
            c.diagnostico,
            c.tratamiento,
            c.consulta_actual,
            c.consulta_proxima,
            p.nombre AS paciente_nombre
        FROM consultas c
        JOIN pacientes p ON c.paciente_id = p.id
        WHERE c.medico_id = ?
        ORDER BY c.fecha DESC
    ''', (medico['id'],)).fetchall()

    conn.close()
    return render_template('medico/reporte_consultas.html', consultas=consultas)

@medico_bp.route('/exportar_pacientes_csv')
def exportar_pacientes_csv():
    if 'usuario_id' not in session:
        flash("Acceso no autorizado.")
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    pacientes = conn.execute('SELECT * FROM pacientes').fetchall()
    conn.close()

    def generate():
        # Cabeceras CSV
        yield 'ID,Nombre,Fecha Nacimiento,NSS,Teléfono,Dirección\n'
        for p in pacientes:
            # Asegúrate de usar los nombres de columnas correctos según tu tabla
            yield f"{p['id']},{p['nombre']},{p['fecha_nacimiento']},{p['nss']},{p['telefono']},{p['direccion']}\n"

    headers = {
        'Content-Disposition': 'attachment; filename=pacientes.csv',
        'Content-Type': 'text/csv',
    }

    return Response(generate(), headers=headers)
@medico_bp.route('/exportar_pacientes_excel')
def exportar_pacientes_excel():
    if 'usuario_id' not in session:
        flash("Acceso no autorizado.")
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    pacientes = conn.execute('SELECT * FROM pacientes').fetchall()
    conn.close()

    # Convertir a DataFrame
    df = pd.DataFrame(pacientes, columns=pacientes[0].keys() if pacientes else [])

    # Crear archivo Excel en memoria
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Pacientes')

    output.seek(0)

    return send_file(output,
                     download_name="pacientes.xlsx",
                     as_attachment=True,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')