import mysql.connector


def get_connection():

    try:

        return mysql.connector.connect(

            host="127.0.0.1",

            user="root",

            password="1234",

            port=3307,

            database="carrito_sistema",

            auth_plugin="mysql_native_password",

            connection_timeout=5,

            use_pure=True
        )

    except Exception as e:

        print(
            "ERROR al obtener conexión:",
            e
        )

        return None