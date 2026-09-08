from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import jsonify
from db import get_connection

ruleta_bp = Blueprint(
    "ruleta",
    __name__
)

@ruleta_bp.route("/ruleta")
def ruleta():

    return render_template(
        "ruleta.html"
    )

@ruleta_bp.route(
    "/ruleta/girar",
    methods=["POST"]
)
def girar_ruleta():

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
        FROM ruleta_codigos
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

    cursor.execute("""
        SELECT *
        FROM ruleta_programacion
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
            UPDATE ruleta_programacion
            SET entregado = 1,
                fecha_entrega = NOW()
            WHERE id_ruleta_programacion = %s
        """, (
            premio_programado["id_ruleta_programacion"],
        ))

    else:

        premio = "Seguí Participando"

    cursor.execute("""
        INSERT INTO ruleta_participantes
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

    cursor.execute("""
        UPDATE ruleta_codigos
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
