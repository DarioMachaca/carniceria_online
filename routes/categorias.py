from flask import Blueprint
from flask import render_template

from db import get_connection

categorias_bp = Blueprint(
    "categorias",
    __name__
)


@categorias_bp.route("/categorias")
def categorias():

    conexion = get_connection()

    cursor = conexion.cursor(
        dictionary=True
    )

    sql = """
        SELECT
            c.id_categoria,
            c.nombre,
            c.imagen,
            COUNT(p.id_producto) AS cantidad_productos
        FROM categorias c

        LEFT JOIN productos p
            ON p.id_categoria = c.id_categoria
            AND p.activo = 1

        WHERE c.activo = 1

        GROUP BY
            c.id_categoria,
            c.nombre,
            c.imagen

        ORDER BY c.nombre
    """

    cursor.execute(sql)

    categorias = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template(
        "categorias.html",
        categorias=categorias
    )