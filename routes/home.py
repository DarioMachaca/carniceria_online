from flask import Blueprint
from flask import render_template
from db import get_connection
from models.promociones import (
    obtener_promociones_activas
)

home_bp = Blueprint(
    "home",
    __name__
)


@home_bp.route("/")
def inicio():

    promociones = obtener_promociones_activas()

    return render_template(
        "index.html",
        promociones=promociones
    )

#==============================
# ENVIOS
#==============================

@home_bp.route("/envios")
def envios():

    conexion = get_connection()

    cursor = conexion.cursor(
        dictionary=True
    )

    cursor.execute("""
        SELECT
            nombre_zona,
            descripcion,
            costo_envio,
            hora_desde,
            hora_hasta
        FROM zonas_envio
        WHERE activo = 1
        ORDER BY nombre_zona
    """)

    zonas = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template(
        "envios.html",
        zonas=zonas
    )


@home_bp.route("/medios-pago")
def medios_pago():

    return render_template(
        "medios_pago.html"
    )


@home_bp.route("/contacto")
def contacto():

    return render_template(
        "contacto.html"
    )