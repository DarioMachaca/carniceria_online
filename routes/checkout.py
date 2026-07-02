from flask import Blueprint
from flask import render_template
from flask import session
from flask import request
from flask import redirect
from datetime import datetime
from urllib.parse import quote

from db import get_connection

checkout_bp = Blueprint(
    "checkout",
    __name__
)


@checkout_bp.route(
    "/checkout"
)
def checkout():

    carrito = session.get(
        "carrito",
        {}
    )

    productos = []

    subtotal_general = 0

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

                subtotal_general += subtotal

                producto["cantidad"] = cantidad
                producto["subtotal"] = subtotal

                productos.append(
                    producto
                )

        cursor.close()
        conexion.close()
    
    zonas = []

    conexion = get_connection()

    cursor = conexion.cursor(
        dictionary=True
    )

    cursor.execute("""
        SELECT
            id_zona,
            nombre_zona,
            descripcion,
            costo_envio
        FROM zonas_envio
        WHERE activo = 1
        ORDER BY nombre_zona
    """)

    zonas = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template(
        "checkout.html",
        productos=productos,
        subtotal_general=subtotal_general,
        zonas=zonas
    )

@checkout_bp.route(
    "/medio-pago",
    methods=["POST"]
)
def medio_pago():

    carrito = session.get(
        "carrito",
        {}
    )

    subtotal = 0

    conexion = get_connection()

    cursor = conexion.cursor(
        dictionary=True
    )

    for id_producto, cantidad in carrito.items():

        cursor.execute(
            """
            SELECT precio
            FROM productos
            WHERE id_producto = %s
            """,
            (id_producto,)
        )

        producto = cursor.fetchone()

        if producto:

            subtotal += (
                float(producto["precio"])
                * float(cantidad)
            )

    envio = float(
        request.form.get(
            "envio",
            0
        )
    )

    total = subtotal + envio

    zona_id = request.form.get(
        "zona_envio"
    )

    zona_nombre = ""

    if (
        request.form.get(
            "tipo_entrega"
        ) == "domicilio"
        and zona_id
        and zona_id != "0"
    ):

        cursor.execute(
            """
            SELECT nombre_zona
            FROM zonas_envio
            WHERE id_zona = %s
            """,
            (zona_id,)
        )

        zona = cursor.fetchone()

        if zona:

            zona_nombre = (
                zona["nombre_zona"]
            )

    cursor.close()
    conexion.close()

    session["checkout"] = {

        "cliente_nombre":
            request.form.get(
                "cliente_nombre"
            ),

        "cliente_telefono":
            request.form.get(
                "cliente_telefono"
            ),

        "tipo_entrega":
            request.form.get(
                "tipo_entrega"
            ),

        "direccion":
            request.form.get(
                "direccion"
            ),

        "observaciones":
            request.form.get(
                "observaciones"
            ),

        "zona":
            zona_id,

        "zona_nombre":
            zona_nombre,

        "envio":
            envio,

        "subtotal":
            subtotal,

        "total":
            total
    }

    return redirect(
        "/seleccionar-pago"
    )

@checkout_bp.route(
    "/seleccionar-pago"
)
def seleccionar_pago():

    datos = session.get(
        "checkout"
    )

    return render_template(
        "medio_pago.html",
        datos=datos
    )

@checkout_bp.route(
    "/confirmar-pedido",
    methods=["POST"]
)
def confirmar_pedido():

    checkout = session.get(
        "checkout",
        {}
    )

    checkout["medio_pago"] = request.form.get(
        "medio_pago"
    )

    session["checkout"] = checkout

    carrito = session.get(
        "carrito",
        {}
    )

    productos = []

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
                precio
            FROM productos
            WHERE id_producto=%s
            """,
            (id_producto,)
        )

        producto = cursor.fetchone()

        if producto:

            producto["cantidad"] = cantidad

            producto["subtotal"] = (
                float(producto["precio"])
                * float(cantidad)
            )

            productos.append(
                producto
            )

    cursor.close()
    conexion.close()

    return render_template(
        "confirmar_pedido.html",
        datos=checkout,
        productos=productos
    )

@checkout_bp.route(
    "/guardar-pedido",
    methods=["POST"]
)
def guardar_pedido():

    checkout = session.get(
        "checkout"
    )

    carrito = session.get(
        "carrito"
    )

    if not checkout or not carrito:

        return redirect(
            "/"
        )

    conexion = get_connection()

    cursor = conexion.cursor(
        dictionary=True
    )

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

    sql = """
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
            estado_pedido
        )
        VALUES
        (
            %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
        )
    """

    cursor.execute(
        sql,
        (
            codigo_compra,
            datetime.now(),
            checkout["cliente_nombre"],
            checkout["cliente_telefono"],
            checkout["tipo_entrega"],
            checkout["direccion"],
            checkout["observaciones"],
            checkout["subtotal"],
            checkout["envio"],
            checkout["total"],
            "pendiente",
            "pendiente"
        )
    )

    id_pedido = (
        cursor.lastrowid
    )

    productos_comprobante = []

    for id_producto, cantidad in carrito.items():

        cursor.execute(
            """
            SELECT
                nombre,
                precio
            FROM productos
            WHERE id_producto = %s
            """,
            (id_producto,)
        )

        producto = cursor.fetchone()

        precio_unitario = float(
            producto["precio"]
        )

        subtotal_producto = (
            precio_unitario
            * float(cantidad)
        )

        productos_comprobante.append({

            "nombre":
                producto["nombre"],

            "cantidad":
                cantidad,

            "subtotal":
                subtotal_producto
        })

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
                id_producto,
                cantidad,
                precio_unitario,
                subtotal_producto
            )
        )

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
            checkout["medio_pago"],
            None,
            checkout["total"],
            "pendiente"
        )
    )

    cursor.execute(
        """
        UPDATE control_pedidos
        SET ultimo_numero = %s
        WHERE id_control = 1
        """,
        (nuevo_numero,)
    )

    conexion.commit()

    cursor.close()
    conexion.close()

    session["comprobante"] = {

        "codigo_compra":
            codigo_compra,

        "fecha":
            datetime.now().strftime(
                "%d/%m/%Y %H:%M"
            ),

        "cliente_nombre":
            checkout["cliente_nombre"],

        "cliente_telefono":
            checkout["cliente_telefono"],

        "tipo_entrega":
            checkout["tipo_entrega"],

        "direccion":
            checkout["direccion"],

        "zona_nombre":
            checkout.get(
                "zona_nombre",
                ""
            ),

        "medio_pago":
            checkout["medio_pago"],

        "estado_pedido":
            "pendiente",

        "observaciones":
            checkout["observaciones"],

        "subtotal":
            checkout["subtotal"],

        "envio":
            checkout["envio"],

        "total":
            checkout["total"],

        "productos":
            productos_comprobante
    }

    session.pop(
        "carrito",
        None
    )

    session.pop(
        "checkout",
        None
    )

    return redirect(
        "/comprobante"
    )

@checkout_bp.route(
    "/comprobante"
)
def comprobante():

    datos = session.get(
        "comprobante"
    )

    if not datos:

        return redirect(
            "/"
        )

    mensaje = f"""
Pedido {datos['codigo_compra']}

Cliente: {datos['cliente_nombre']}

"""

    for producto in datos["productos"]:

        mensaje += (
            f"{producto['cantidad']} x "
            f"{producto['nombre']} "
            f"= ${producto['subtotal']}\n"
        )

    mensaje += f"""

Subtotal: ${datos['subtotal']}
Envío: ${datos['envio']}
Total: ${datos['total']}

Medio de pago:
{datos['medio_pago']}
"""

    mensaje_whatsapp = quote(
        mensaje
    )

    conexion = get_connection()

    cursor = conexion.cursor(
        dictionary=True
    )

    cursor.execute("""
        SELECT telefono
        FROM configuracion
        LIMIT 1
    """)

    configuracion = cursor.fetchone()

    cursor.close()
    conexion.close()

    telefono = ""

    if configuracion:

        telefono = configuracion["telefono"]
    
    telefono = (
        telefono
        .replace(" ", "")
        .replace("-", "")
        .replace("(", "")
        .replace(")", "")
        .replace("+", "")
    )

    return render_template(
        "comprobante.html",
        datos=datos,
        mensaje_whatsapp=mensaje_whatsapp,
        telefono=telefono
    )