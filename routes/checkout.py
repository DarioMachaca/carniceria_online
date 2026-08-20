from flask import Blueprint
from flask import render_template
from flask import session
from flask import request
from flask import redirect
from datetime import datetime
from urllib.parse import quote

from services.mercadopago_service import (
    crear_preferencia
)

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

    productos_mp = []

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

        productos_mp.append({

            "nombre":
                f"{producto['nombre']} ({cantidad} kg)",

            "cantidad":
                1,

            "precio_unitario":
                subtotal_producto
        })

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

    id_pago = cursor.lastrowid


    cursor.execute(
        """
        UPDATE control_pedidos
        SET ultimo_numero = %s
        WHERE id_control = 1
        """,
        (nuevo_numero,)
    )

    if (
        checkout["medio_pago"]
        == "mercadopago"
    ):

        preferencia = crear_preferencia(
            codigo_compra,
            productos_mp,
            checkout["envio"]
        )

        if "id" not in preferencia:

            return str(preferencia)

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

    if (
        checkout["medio_pago"]
        == "mercadopago"
    ):

        return redirect(
            preferencia["init_point"]
        )

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

    if (
        checkout["medio_pago"]
        == "transferencia"
    ):

        return redirect(
            "/transferencia"
        )

    return redirect(
        "/comprobante"
    )

def reconstruir_comprobante(
    external_reference,
    payment_id=None
):

    conexion = get_connection()

    cursor = conexion.cursor(
        dictionary=True
    )

    cursor.execute(
        """
        SELECT *
        FROM pedidos
        WHERE codigo_compra = %s
        """,
        (external_reference,)
    )

    pedido = cursor.fetchone()

    cursor.execute(
        """
        SELECT
            pr.nombre,
            pd.cantidad,
            pd.subtotal
        FROM pedido_detalle pd
        INNER JOIN productos pr
            ON pd.id_producto = pr.id_producto
        WHERE pd.id_pedido = %s
        """,
        (pedido["id_pedido"],)
    )

    productos = cursor.fetchall()

    session["comprobante"] = {

        "codigo_compra":
            pedido["codigo_compra"],

        "referencia_pago":
            payment_id,

        "fecha":
            pedido["fecha"].strftime(
                "%d/%m/%Y %H:%M"
            ),

        "cliente_nombre":
            pedido["cliente_nombre"],

        "cliente_telefono":
            pedido["cliente_telefono"],

        "tipo_entrega":
            pedido["tipo_entrega"],

        "direccion":
            pedido["direccion"],

        "zona_nombre":
            "",

        "medio_pago":
            "mercadopago",

        "estado_pedido":
            pedido["estado_pedido"],

        "estado_pago":
            pedido["estado_pago"],

        "observaciones":
            pedido["observaciones"],

        "subtotal":
            float(pedido["subtotal"]),

        "envio":
            float(pedido["envio"]),

        "total":
            float(pedido["total"]),

        "productos":
            productos
    }

    cursor.close()
    conexion.close()

    session.pop(
        "carrito",
        None
    )

    session.pop(
        "checkout",
        None
    )

@checkout_bp.route("/pago-exitoso")
def pago_exitoso():

    payment_id = request.args.get(
        "payment_id"
    )

    external_reference = request.args.get(
        "external_reference"
    )

    conexion = get_connection()

    cursor = conexion.cursor(
        dictionary=True
    )

    cursor.execute(
        """
        UPDATE pedidos
        SET estado_pago = 'aprobado'
        WHERE codigo_compra = %s
        """,
        (external_reference,)
    )

    cursor.execute(
        """
        UPDATE pagos p
        INNER JOIN pedidos pe
            ON p.id_pedido = pe.id_pedido
        SET
            p.estado = 'aprobado',
            p.referencia_pago = %s
        WHERE pe.codigo_compra = %s
        """,
        (
            payment_id,
            external_reference
        )
    )

    conexion.commit()

    cursor.close()
    conexion.close()

    reconstruir_comprobante(
        external_reference,
        payment_id
    )

    return redirect(
        "/comprobante"
    )


@checkout_bp.route("/pago-pendiente")
def pago_pendiente():

    external_reference = request.args.get(
        "external_reference"
    )

    conexion = get_connection()

    cursor = conexion.cursor()

    cursor.execute(
        """
        UPDATE pedidos
        SET estado_pago = 'pendiente'
        WHERE codigo_compra = %s
        """,
        (external_reference,)
    )

    cursor.execute(
        """
        UPDATE pagos p
        INNER JOIN pedidos pe
            ON p.id_pedido = pe.id_pedido
        SET p.estado = 'pendiente'
        WHERE pe.codigo_compra = %s
        """,
        (external_reference,)
    )

    conexion.commit()

    cursor.close()
    conexion.close()

    reconstruir_comprobante(
        external_reference
    )

    return redirect(
        "/comprobante"
    )
    


@checkout_bp.route("/pago-fallido")
def pago_fallido():

    external_reference = request.args.get(
        "external_reference"
    )

    conexion = get_connection()

    cursor = conexion.cursor()

    cursor.execute(
        """
        UPDATE pedidos
        SET estado_pago = 'rechazado'
        WHERE codigo_compra = %s
        """,
        (external_reference,)
    )

    cursor.execute(
        """
        UPDATE pagos p
        INNER JOIN pedidos pe
            ON p.id_pedido = pe.id_pedido
        SET p.estado = 'rechazado'
        WHERE pe.codigo_compra = %s
        """,
        (external_reference,)
    )

    conexion.commit()

    cursor.close()
    conexion.close()

    reconstruir_comprobante(
        external_reference
    )

    return redirect(
        "/comprobante"
    )

@checkout_bp.route(
    "/webhook/mercadopago",
    methods=["POST"]
)
def webhook_mercadopago():

    data = request.get_json()

    print("WEBHOOK MP:")
    print(data)

    return "OK", 200


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

@checkout_bp.route(
    "/transferencia"
)
def transferencia():

    datos = session.get(
        "comprobante"
    )

    if not datos:

        return redirect(
            "/"
        )

    conexion = get_connection()

    cursor = conexion.cursor(
        dictionary=True
    )

    cursor.execute("""
        SELECT *
        FROM datos_bancarios
        WHERE activo = 1
        LIMIT 1
    """)

    datos_bancarios = cursor.fetchone()

    cursor.execute("""
        SELECT telefono
        FROM configuracion
        LIMIT 1
    """)

    configuracion = cursor.fetchone()

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

    mensaje = f"""
    Hola.

    Soy {datos['cliente_nombre']}.

    Realicé una transferencia correspondiente al pedido {datos['codigo_compra']} por un total de ${datos['total']}.

    Adjunto comprobante."""

    mensaje_whatsapp = quote(
        mensaje
    )

    cursor.close()
    conexion.close()

    return render_template(
        "transferencia.html",
        datos=datos,
        datos_bancarios=datos_bancarios,
        mensaje_whatsapp=mensaje_whatsapp,
        telefono=telefono
    )

