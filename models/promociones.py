from db import get_connection


def obtener_promociones_activas():

    conn = get_connection()

    cursor = conn.cursor(
        dictionary=True
    )

    cursor.execute(
        """
        SELECT *
        FROM promociones
        WHERE activo = 1
        ORDER BY orden_visualizacion
        """
    )

    promociones = cursor.fetchall()

    cursor.close()
    conn.close()

    return promociones