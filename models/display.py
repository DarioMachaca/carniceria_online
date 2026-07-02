from db import get_connection

def obtener_display():

    conn = get_connection()

    cursor = conn.cursor(
        dictionary=True
    )

    cursor.execute(
        """
        SELECT *
        FROM config_display
        LIMIT 1
        """
    )

    resultado = cursor.fetchone()

    cursor.close()
    conn.close()

    return resultado