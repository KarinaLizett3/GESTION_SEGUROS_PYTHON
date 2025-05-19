import sqlite3

def crear_tabla_usuarios():
    conexion = sqlite3.connect('base_datos.db')
    cursor = conexion.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            email TEXT UNIQUE,
            contrasena TEXT,
            rol TEXT,
            fecha_registro TEXT
        )
    ''')

    conexion.commit()
    conexion.close()
    print("✅ Tabla 'usuarios' creada o verificada correctamente.")

# Ejecuta la función directamente
if __name__ == '__main__':
    crear_tabla_usuarios()
