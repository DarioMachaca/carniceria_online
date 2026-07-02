from db import get_connection


def obtener_configuracion():

    conexion = get_connection()

    cursor = conexion.cursor(
        dictionary=True
    )

    cursor.execute("""
        SELECT *
        FROM configuracion
        WHERE id_configuracion = 1
    """)

    config = cursor.fetchone()

    cursor.close()
    conexion.close()

    return config