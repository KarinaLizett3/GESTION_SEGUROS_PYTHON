from flask import render_template, request, redirect, url_for, flash, session
from . import auth_bp
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

def get_db_connection():
    conn = sqlite3.connect('base_datos.db')
    conn.row_factory = sqlite3.Row
    return conn

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['contrasena']

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()

        if user and check_password_hash(user['contrasena'], password):
            session['usuario_id'] = user['id']
            session['usuario_nombre'] = user['nombre']
            session['usuario_rol'] = user['rol']

            # 🔽 Si es médico, obtener también su ID en la tabla "medicos"
            if user['rol'] == "medico":
                medico = conn.execute("SELECT id FROM medicos WHERE usuario_id = ?", (user['id'],)).fetchone()
                if medico:
                    session['medico_id'] = medico['id']
                else:
                    error = "Este usuario no está registrado como médico."
                    conn.close()
                    return render_template('auth/login.html', error=error)

            conn.close()

            # Redirección según el rol
            if user['rol'] == "administrador":
                return redirect(url_for('admin.dashboard'))
            elif user['rol'] == "medico":
                return redirect(url_for('medico.dashboard'))
            elif user['rol'] == "paciente":
                return redirect(url_for('paciente.dashboard'))
            else:
                error = "Rol no reconocido."
        else:
            error = "Correo o contraseña incorrectos."
            conn.close()

    return render_template('auth/login.html', error=error)

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Has cerrado sesión.")
    return redirect(url_for('auth.login'))

@auth_bp.route('/registro_usuario', methods=['GET', 'POST'])
def registro_usuario():
    error = None
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        contrasena = request.form['contrasena']
        rol = request.form['rol'].lower()  # Convertir a minúsculas

        if not nombre or not email or not contrasena or not rol:
            error = "Todos los campos son obligatorios."
        else:
            conn = get_db_connection()
            usuario_existente = conn.execute('SELECT id FROM usuarios WHERE email = ?', (email,)).fetchone()

            if usuario_existente:
                error = "Este correo ya está registrado."
                conn.close()
            else:
                try:
                    hashed_password = generate_password_hash(contrasena)
                    fecha_registro = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    conn.execute('''
                        INSERT INTO usuarios (nombre, email, contrasena, rol, fecha_registro)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (nombre, email, hashed_password, rol, fecha_registro))
                    conn.commit()

                    # Obtener el ID del nuevo usuario registrado
                    nuevo_usuario = conn.execute('SELECT id FROM usuarios WHERE email = ?', (email,)).fetchone()

                    # Registrar en tabla correspondiente según el rol
                    if rol == 'paciente':
                        conn.execute('''
                            INSERT INTO pacientes (usuario_id, nombre, fecha_nacimiento, nss, telefono, direccion)
                            VALUES (?, ?, '', '', '', '')
                        ''', (nuevo_usuario['id'], nombre))

                    elif rol == 'medico':
                        conn.execute('''
                            INSERT INTO medicos (usuario_id, nombre, especialidad, telefono)
                            VALUES (?, ?, '', '')
                        ''', (nuevo_usuario['id'], nombre))

                    # No se necesita registro adicional para administrador
                    conn.commit()
                    conn.close()

                    flash("Usuario registrado exitosamente.")
                    return redirect(url_for('auth.login'))

                except sqlite3.IntegrityError:
                    conn.close()
                    error = "Hubo un problema al registrar el usuario."

    return render_template('auth/registro_usuario.html', error=error)

@auth_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    conn = get_db_connection()
    paciente = conn.execute('SELECT * FROM pacientes WHERE id = ?', (id,)).fetchone()

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
        ''', (nombre, fecha_nacimiento, nss, telefono, direccion, id))
        conn.commit()
        conn.close()
        flash("Paciente actualizado correctamente.")
        return redirect(url_for('paciente.listar'))

    conn.close()
    return render_template('paciente/editar.html', paciente=paciente)
