from flask import Blueprint
from flask import session
from flask import render_template
from flask import request

from db import get_connection

productos_bp = Blueprint(
    "productos",
    __name__
)


@productos_bp.route(
    "/productos/<int:id_categoria>"
)
def productos(id_categoria):

    conexion = get_connection()

    cursor = conexion.cursor(
        dictionary=True
    )

    sql_categoria = """
        SELECT
            nombre
        FROM categorias
        WHERE id_categoria = %s
    """

    cursor.execute(
        sql_categoria,
        (id_categoria,)
    )

    categoria = cursor.fetchone()

    pagina = request.args.get(
        "page",
        1,
        type=int
    )

    productos_por_pagina = 15

    offset = (
        pagina - 1
    ) * productos_por_pagina

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM productos
        WHERE id_categoria = %s
        AND activo = 1
    """,
    (id_categoria,))

    total_productos = cursor.fetchone()["total"]

    total_paginas = (
        total_productos +
        productos_por_pagina - 1
    ) // productos_por_pagina

    sql_productos = """
        SELECT
            id_producto,
            nombre,
            descripcion,
            unidad_medida,
            precio,
            imagen,
            destacado,
            orden_visual,
            sin_stock
        FROM productos
        WHERE id_categoria = %s
        AND activo = 1
        ORDER BY
            destacado DESC,
            orden_visual ASC,
            nombre ASC
        LIMIT %s
        OFFSET %s
    """

    cursor.execute(
        sql_productos,
        (
            id_categoria,
            productos_por_pagina,
            offset
        )
    )

    productos = cursor.fetchall()

    cursor.close()
    conexion.close()

    carrito = session.get(
        "carrito",
        {}
    )

    return render_template(
        "productos.html",
        categoria=categoria,
        productos=productos,
        carrito=carrito,
        pagina=pagina,
        total_paginas=total_paginas
    )