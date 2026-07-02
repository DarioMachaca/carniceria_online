from flask import Blueprint
from flask import session
from flask import redirect
from flask import request
from flask import render_template
from flask import jsonify

from db import get_connection

carrito_bp = Blueprint(
    "carrito",
    __name__
)


@carrito_bp.route(
    "/agregar-carrito/<int:id_producto>"
)
def agregar_carrito(id_producto):

    conexion = get_connection()

    cursor = conexion.cursor(
        dictionary=True
    )

    sql = """
        SELECT
            id_producto,
            unidad_medida
        FROM productos
        WHERE id_producto = %s
    """

    cursor.execute(
        sql,
        (id_producto,)
    )

    producto = cursor.fetchone()

    cursor.close()
    conexion.close()

    if not producto:

        return redirect(
            request.referrer
        )

    carrito = session.get(
        "carrito",
        {}
    )

    id_str = str(
        id_producto
    )

    cantidad_actual = float(
        carrito.get(
            id_str,
            0
        )
    )

    if producto["unidad_medida"] == "kg":

        cantidad_actual += 0.5

    else:

        cantidad_actual += 1

    carrito[id_str] = cantidad_actual

    session["carrito"] = carrito

    return redirect(
        request.referrer
    )

@carrito_bp.route(
    "/quitar-carrito/<int:id_producto>"
)
def quitar_carrito(id_producto):

    conexion = get_connection()

    cursor = conexion.cursor(
        dictionary=True
    )

    sql = """
        SELECT
            id_producto,
            unidad_medida
        FROM productos
        WHERE id_producto = %s
    """

    cursor.execute(
        sql,
        (id_producto,)
    )

    producto = cursor.fetchone()

    cursor.close()
    conexion.close()

    if not producto:

        return redirect(
            request.referrer
        )

    carrito = session.get(
        "carrito",
        {}
    )

    id_str = str(
        id_producto
    )

    cantidad_actual = float(
        carrito.get(
            id_str,
            0
        )
    )

    if producto["unidad_medida"] == "kg":

        cantidad_actual -= 0.5

    else:

        cantidad_actual -= 1

    if cantidad_actual <= 0:

        carrito.pop(
            id_str,
            None
        )

    else:

        carrito[id_str] = cantidad_actual

    session["carrito"] = carrito

    return redirect(
        request.referrer
    )

@carrito_bp.route(
    "/mi-carrito"
)
def ver_carrito():

    carrito = session.get(
        "carrito",
        {}
    )

    productos = []

    total_general = 0

    if carrito:

        conexion = get_connection()

        cursor = conexion.cursor(
            dictionary=True
        )

        for id_producto, cantidad in carrito.items():

            sql = """
                SELECT
                    id_producto,
                    nombre,
                    precio,
                    unidad_medida
                FROM productos
                WHERE id_producto = %s
            """

            cursor.execute(
                sql,
                (id_producto,)
            )

            producto = cursor.fetchone()

            if producto:

                subtotal = (
                    float(cantidad)
                    * float(producto["precio"])
                )

                total_general += subtotal

                producto["cantidad"] = cantidad
                producto["subtotal"] = subtotal

                productos.append(
                    producto
                )

        cursor.close()
        conexion.close()

    return render_template(
        "carrito.html",
        productos=productos,
        total_general=total_general
    )

@carrito_bp.route(
    "/eliminar-carrito/<int:id_producto>"
)
def eliminar_carrito(id_producto):

    carrito = session.get(
        "carrito",
        {}
    )

    carrito.pop(
        str(id_producto),
        None
    )

    session["carrito"] = carrito

    return redirect(
        "/mi-carrito"
    )

@carrito_bp.route(
    "/ajax/agregar-carrito/<int:id_producto>"
)
def ajax_agregar_carrito(id_producto):

    conexion = get_connection()

    cursor = conexion.cursor(
        dictionary=True
    )

    cursor.execute("""
        SELECT unidad_medida
        FROM productos
        WHERE id_producto = %s
    """, (id_producto,))

    producto = cursor.fetchone()

    cursor.close()
    conexion.close()

    if not producto:

        return jsonify({
            "error": True
        })

    carrito = session.get(
        "carrito",
        {}
    )

    id_str = str(id_producto)

    cantidad_actual = float(
        carrito.get(
            id_str,
            0
        )
    )

    if producto["unidad_medida"] == "kg":

        cantidad_actual += 0.5

    else:

        cantidad_actual += 1

    carrito[id_str] = cantidad_actual

    session["carrito"] = carrito

    return jsonify({
        "cantidad": cantidad_actual,
        "total_items": len(carrito)
    })

@carrito_bp.route(
    "/ajax/quitar-carrito/<int:id_producto>"
)
def ajax_quitar_carrito(id_producto):

    conexion = get_connection()

    cursor = conexion.cursor(
        dictionary=True
    )

    cursor.execute("""
        SELECT unidad_medida
        FROM productos
        WHERE id_producto = %s
    """, (id_producto,))

    producto = cursor.fetchone()

    cursor.close()
    conexion.close()

    if not producto:

        return jsonify({
            "error": True
        })

    carrito = session.get(
        "carrito",
        {}
    )

    id_str = str(id_producto)

    cantidad_actual = float(
        carrito.get(
            id_str,
            0
        )
    )

    if producto["unidad_medida"] == "kg":

        cantidad_actual -= 0.5

    else:

        cantidad_actual -= 1

    if cantidad_actual <= 0:

        carrito.pop(
            id_str,
            None
        )

        cantidad_actual = 0

    else:

        carrito[id_str] = cantidad_actual

    session["carrito"] = carrito

    return jsonify({
        "cantidad": cantidad_actual,
        "total_items": len(carrito)
    })