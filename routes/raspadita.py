from flask import Blueprint
from flask import render_template
from flask import request
from flask import jsonify

from db import get_connection


raspadita_bp = Blueprint(
    "raspadita",
    __name__
)


@raspadita_bp.route("/raspadita")
def raspadita():

    return render_template(
        "raspadita.html"
    )


@raspadita_bp.route(
    "/raspadita/revelar",
    methods=["POST"]
)
def revelar_raspadita():

    codigo = request.form["codigo"].strip().upper()
    nombre = request.form["nombre"].strip()
    telefono = request.form["telefono"].strip()

    conexion = get_connection()

    cursor = conexion.cursor(
        dictionary=True
    )

    # Buscar código

    cursor.execute("""
        SELECT *
        FROM raspadita_codigos
        WHERE codigo = %s
    """, (codigo,))

    codigo_db = cursor.fetchone()

    if not codigo_db:

        cursor.close()
        conexion.close()

        return jsonify({
            "ok": False,
            "mensaje": "El código ingresado no existe."
        })

    if codigo_db["usado"]:

        cursor.close()
        conexion.close()

        return jsonify({
            "ok": False,
            "mensaje": "Este código ya participó."
        })

    # Buscar próximo premio disponible

    cursor.execute("""
        SELECT *
        FROM raspadita_programacion
        WHERE fecha_inicio <= NOW()
        AND entregado = 0
        AND activo = 1
        ORDER BY fecha_inicio
        LIMIT 1
    """)

    premio_programado = cursor.fetchone()

    if premio_programado:

        premio = premio_programado["premio"]

        cursor.execute("""
            UPDATE raspadita_programacion
            SET entregado = 1,
                fecha_entrega = NOW()
            WHERE id_raspadita_programacion = %s
        """, (
            premio_programado["id_raspadita_programacion"],
        ))

    else:

        premio = "Seguí Participando"

    # Registrar participante

    cursor.execute("""
        INSERT INTO raspadita_participantes
        (
            codigo,
            nombre,
            telefono,
            premio
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s
        )
    """, (
        codigo,
        nombre,
        telefono,
        premio
    ))

    # Marcar código utilizado

    cursor.execute("""
        UPDATE raspadita_codigos
        SET usado = 1,
            fecha_uso = NOW()
        WHERE codigo = %s
    """, (codigo,))

    conexion.commit()

    cursor.close()
    conexion.close()

    return jsonify({
        "ok": True,
        "premio": premio
    })