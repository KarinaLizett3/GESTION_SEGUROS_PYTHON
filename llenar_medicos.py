import sqlite3

def llenar_medicos():
    conn = sqlite3.connect('base_datos.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Obtener todos los usuarios con rol "medico"
    usuarios_medicos = cursor.execute("SELECT id, nombre FROM usuarios WHERE rol = 'medico'").fetchall()

    for usuario in usuarios_medicos:
        # Verificar si ya existe el médico para ese usuario
        existe_medico = cursor.execute("SELECT id FROM medicos WHERE usuario_id = ?", (usuario['id'],)).fetchone()

        if not existe_medico:
            # Insertar nuevo registro en medicos
            cursor.execute(
                "INSERT INTO medicos (usuario_id, Nombre) VALUES (?, ?)",
                (usuario['id'], usuario['nombre'])
            )
            print(f"Creado médico para usuario_id={usuario['id']} nombre={usuario['nombre']}")

    conn.commit()
    conn.close()
    print("Proceso completado.")

if __name__ == "__main__":
    llenar_medicos()
