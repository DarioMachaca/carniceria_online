from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import session
from datetime import datetime
from urllib.parse import quote
from flask import jsonify
from services.mercadopago_service import (
    crear_preferencia
)
from routes.admin import login_requerido

from db import get_connection


admin_whatsapp_bp = Blueprint(
    "admin_whatsapp",
    __name__
)


@admin_whatsapp_bp.route(
    "/admin/ventas-whatsapp"
)
def ventas_whatsapp():

    buscar = request.args.get(
        "buscar",
        ""
    )

    productos = []

    conexion = get_connection()

    cursor = conexion.cursor(
        dictionary=True
    )

    if buscar:

        cursor.execute(
            """
            SELECT
                id_producto,
                nombre,
                precio,
                unidad_medida,
                imagen
            FROM productos
            WHERE activo = 1
            AND nombre LIKE %s
            ORDER BY nombre
            LIMIT 30
            """,
            (
                f"%{buscar}%",
            )
        )

        productos = cursor.fetchall()

    cursor.close()
    conexion.close()

    carrito = session.get(
        "carrito_whatsapp",
        {}
    )

    productos_carrito = []

    total_general = 0

    if carrito:

        conexion = get_connection()

        cursor = conexion.cursor(
            dictionary=True
        )

        for id_producto, cantidad in carrito.items():

            cursor.execute(
                """
                SELECT
                    id_producto,
                    nombre,
                    precio,
                    unidad_medida
                FROM productos
                WHERE id_producto = %s
                """,
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

                productos_carrito.append(
                    producto
                )

        cursor.close()
        conexion.close()

    return render_template(
        "admin_ventas_whatsapp.html",
        buscar=buscar,
        productos=productos,
        carrito=productos_carrito,
        total_general=total_general
    )

# ==================================
# BUSCAR - MOSTRAR SUGERENCIAS
# ==================================

@admin_whatsapp_bp.route(
    "/admin/whatsapp/sugerencias"
)
def whatsapp_sugerencias():

    texto = request.args.get(
        "q",
        ""
    )

    conexion = get_connection()

    cursor = conexion.cursor(
        dictionary=True
    )

    cursor.execute(
        """
        SELECT
            id_producto,
            nombre,
            precio,
            unidad_medida
        FROM productos
        WHERE activo = 1
        AND nombre LIKE %s
        ORDER BY nombre
        LIMIT 10
        """,
        (
            f"%{texto}%",
        )
    )

    productos = cursor.fetchall()

    cursor.close()
    conexion.close()

    return jsonify(productos)

# ==========================
# AGREGAR PRODUCTOS
# ==========================

@admin_whatsapp_bp.route(
    "/admin/whatsapp/agregar/<int:id_producto>"
)
def whatsapp_agregar(id_producto):

    conexion = get_connection()

    cursor = conexion.cursor(
        dictionary=True
    )

    cursor.execute(
        """
        SELECT
            id_producto,
            unidad_medida
        FROM productos
        WHERE id_producto = %s
        """,
        (id_producto,)
    )

    producto = cursor.fetchone()

    cursor.close()
    conexion.close()

    if not producto:

        return redirect(
            "/admin/ventas-whatsapp"
        )

    carrito = session.get(
        "carrito_whatsapp",
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

    session["carrito_whatsapp"] = carrito

    return redirect(
        request.referrer
        or "/admin/ventas-whatsapp"
    )

# ==========================
# AJAX AGREGAR
# ==========================

@admin_whatsapp_bp.route(
    "/ajax/whatsapp/agregar/<int:id_producto>"
)
def ajax_whatsapp_agregar(id_producto):

    whatsapp_agregar(id_producto)

    return jsonify({
        "ok": True
    })

# ==========================
# QUITAR PRODUCTOS
# ==========================

@admin_whatsapp_bp.route(
    "/admin/whatsapp/quitar/<int:id_producto>"
)
def whatsapp_quitar(id_producto):

    conexion = get_connection()

    cursor = conexion.cursor(
        dictionary=True
    )

    cursor.execute(
        """
        SELECT unidad_medida
        FROM productos
        WHERE id_producto = %s
        """,
        (id_producto,)
    )

    producto = cursor.fetchone()

    cursor.close()
    conexion.close()

    if not producto:

        return redirect(
            "/admin/ventas-whatsapp"
        )

    carrito = session.get(
        "carrito_whatsapp",
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

    else:

        carrito[id_str] = cantidad_actual

    session["carrito_whatsapp"] = carrito

    return redirect(
        request.referrer
        or "/admin/ventas-whatsapp"
    )

# ==========================
# AJAX QUITAR
# ==========================

@admin_whatsapp_bp.route(
    "/ajax/whatsapp/quitar/<int:id_producto>"
)
def ajax_whatsapp_quitar(id_producto):

    whatsapp_quitar(id_producto)

    return jsonify({
        "ok": True
    })

# ==========================
# ELIMINAR PRODUCTOS
# ==========================

@admin_whatsapp_bp.route(
    "/admin/whatsapp/eliminar/<int:id_producto>"
)
def whatsapp_eliminar(id_producto):

    carrito = session.get(
        "carrito_whatsapp",
        {}
    )

    carrito.pop(
        str(id_producto),
        None
    )

    session["carrito_whatsapp"] = carrito

    return redirect(
        "/admin/ventas-whatsapp"
    )

# ==========================
# AJAX ELIMINAR
# ==========================

@admin_whatsapp_bp.route(
    "/ajax/whatsapp/eliminar/<int:id_producto>"
)
def ajax_whatsapp_eliminar(id_producto):

    whatsapp_eliminar(id_producto)

    return jsonify({
        "ok": True
    })

# ==========================
# GENERAR PEDIDO Y GUARDAR
# ==========================

@admin_whatsapp_bp.route(
    "/admin/whatsapp/generar-pedido",
    methods=["POST"]
)
@login_requerido
def generar_pedido_whatsapp():

    carrito = session.get(
        "carrito_whatsapp",
        {}
    )

    if not carrito:

        return redirect(
            "/admin/ventas-whatsapp"
        )

    cliente_nombre = request.form.get(
        "cliente_nombre"
    )

    cliente_telefono = request.form.get(
        "cliente_telefono"
    )

    tipo_entrega = request.form.get(
        "tipo_entrega"
    )

    direccion = request.form.get(
        "direccion"
    )

    observaciones = request.form.get(
        "observaciones"
    )

    medio_pago = request.form.get(
        "medio_pago"
    )

    envio = float(
        request.form.get(
            "envio",
            0
        )
    )

    conexion = get_connection()

    cursor = conexion.cursor(
        dictionary=True
    )

    # ==========================
    # GENERAR CODIGO COMPRA
    # ==========================

    cursor.execute("""
        SELECT
            ultimo_numero
        FROM control_pedidos
        WHERE id_control = 1
    """)

    control = cursor.fetchone()

    nuevo_numero = (
        control["ultimo_numero"]
        + 1
    )

    codigo_compra = (
        f"A-{nuevo_numero:05}"
    )

    # ==========================
    # CALCULAR TOTALES
    # ==========================

    subtotal = 0

    productos_pedido = []

    for id_producto, cantidad in carrito.items():

        cursor.execute(
            """
            SELECT
                id_producto,
                nombre,
                precio
            FROM productos
            WHERE id_producto = %s
            """,
            (id_producto,)
        )

        producto = cursor.fetchone()

        if not producto:

            continue

        subtotal_producto = (
            float(producto["precio"])
            * float(cantidad)
        )

        subtotal += subtotal_producto

        productos_pedido.append({

            "id_producto":
                producto["id_producto"],

            "nombre":
                producto["nombre"],

            "precio":
                float(producto["precio"]),

            "cantidad":
                float(cantidad),

            "subtotal":
                subtotal_producto
        })

    total = subtotal + envio

    # ==========================
    # GUARDAR PEDIDO
    # ==========================

    cursor.execute(
        """
        INSERT INTO pedidos
        (
            codigo_compra,
            fecha,
            cliente_nombre,
            cliente_telefono,
            tipo_entrega,
            direccion,
            observaciones,
            subtotal,
            envio,
            total,
            estado_pago,
            estado_pedido,
            origen_pedido
        )
        VALUES
        (
            %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
        )
        """,
        (
            codigo_compra,
            datetime.now(),
            cliente_nombre,
            cliente_telefono,
            tipo_entrega,
            direccion,
            observaciones,
            subtotal,
            envio,
            total,
            "pendiente",
            "pendiente",
            "whatsapp"
        )
    )

    id_pedido = (
        cursor.lastrowid
    )

    # ==========================
    # GUARDAR DETALLE
    # ==========================

    for producto in productos_pedido:

        cursor.execute(
            """
            INSERT INTO pedido_detalle
            (
                id_pedido,
                id_producto,
                cantidad,
                precio_unitario,
                subtotal
            )
            VALUES
            (
                %s,%s,%s,%s,%s
            )
            """,
            (
                id_pedido,
                producto["id_producto"],
                producto["cantidad"],
                producto["precio"],
                producto["subtotal"]
            )
        )

    productos_mp = []

    for producto in productos_pedido:

        productos_mp.append({

            "nombre":
                f"{producto['nombre']} ({producto['cantidad']})",

            "cantidad":
                1,

            "precio_unitario":
                producto["subtotal"]
        })

    # ==========================
    # GUARDAR PAGO
    # ==========================

    cursor.execute(
        """
        INSERT INTO pagos
        (
            id_pedido,
            fecha,
            medio_pago,
            referencia_pago,
            importe,
            estado
        )
        VALUES
        (
            %s,%s,%s,%s,%s,%s
        )
        """,
        (
            id_pedido,
            datetime.now(),
            medio_pago,
            None,
            total,
            "pendiente"
        )
    )

    id_pago = cursor.lastrowid

    # ==========================
    # ACTUALIZAR CONTADOR
    # ==========================

    cursor.execute(
        """
        UPDATE control_pedidos
        SET ultimo_numero = %s
        WHERE id_control = 1
        """,
        (nuevo_numero,)
    )

    link_pago = ""

    if medio_pago == "mercadopago":

        preferencia = crear_preferencia(
            codigo_compra,
            productos_mp,
            envio
        )

        if "id" not in preferencia:

            return str(preferencia)

        link_pago = (
            preferencia["init_point"]
        )

        cursor.execute(
            """
            UPDATE pagos
            SET mp_preference_id = %s
            WHERE id_pago = %s
            """,
            (
                preferencia["id"],
                id_pago
            )
        )

    conexion.commit()

    cursor.close()
    conexion.close()

    detalle_productos = ""

    for producto in productos_pedido:

        unidad = "kg"

        if producto["cantidad"] == int(producto["cantidad"]):
            cantidad = int(producto["cantidad"])
        else:
            cantidad = producto["cantidad"]

        detalle_productos += (
            f"• {producto['nombre']} - "
            f"{cantidad} {unidad}\n"
        )

    if medio_pago == "mercadopago":

        mensaje = f"""
    Hola {cliente_nombre} 👋

    Gracias por elegir FRICAR.

    Tu pedido {codigo_compra} fue registrado correctamente.

    DETALLE DEL PEDIDO

    {detalle_productos}

    TOTAL: ${total:,.2f}

    Para completar la compra podés pagar desde el siguiente enlace:

    {link_pago}

    Muchas gracias.
    """

    elif medio_pago == "transferencia":

        mensaje = f"""
    Hola {cliente_nombre} 👋

    Gracias por elegir FRICAR.

    Tu pedido {codigo_compra} fue registrado correctamente.

    DETALLE DEL PEDIDO

    {detalle_productos}

    TOTAL: ${total:,.2f}

    Datos para transferencia:

    Alias: TU_ALIAS
    CBU: TU_CBU

    Una vez realizada la transferencia envianos el comprobante.

    Muchas gracias.
    """

    else:

        mensaje = f"""
    Hola {cliente_nombre} 👋

    Gracias por elegir FRICAR.

    Tu pedido {codigo_compra} fue registrado correctamente.

    DETALLE DEL PEDIDO

    {detalle_productos}

    TOTAL: ${total:,.2f}

    Forma de pago:
    Efectivo al retirar.

    Muchas gracias.
    """

    mensaje_whatsapp = quote(
        mensaje
    )

    telefono = (
        cliente_telefono
        .replace(" ", "")
        .replace("-", "")
        .replace("(", "")
        .replace(")", "")
        .replace("+", "")
    )

    session.pop(
        "carrito_whatsapp",
        None
    )

    return redirect(
        f"https://wa.me/{telefono}?text={mensaje_whatsapp}"
    )