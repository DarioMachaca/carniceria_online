from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from werkzeug.utils import secure_filename
import os
from flask import session
from functools import wraps
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from datetime import datetime

from db import get_connection

admin_bp = Blueprint(
    "admin",
    __name__
)

def login_requerido(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        if "admin" not in session:

            return redirect(
                "/admin/login"
            )

        return func(
            *args,
            **kwargs
        )

    return wrapper

def solo_admin(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        if "admin" not in session:

            return redirect(
                "/admin/login"
            )

        if session["admin"]["rol"] != "admin":

            return redirect(
                "/admin"
            )

        return func(
            *args,
            **kwargs
        )

    return wrapper

def admin_o_encargado(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        if "admin" not in session:

            return redirect(
                "/admin/login"
            )

        if session["admin"]["rol"] not in [

            "admin",
            "encargado"

        ]:

            return redirect(
                "/admin"
            )

        return func(
            *args,
            **kwargs
        )

    return wrapper

@admin_bp.route(
    "/admin/pedidos"
)
@login_requerido
def pedidos():

    fecha = request.args.get(
        "fecha",
        ""
    )

    codigo = request.args.get(
        "codigo",
        ""
    )

    estado_pago = request.args.get(
        "estado_pago",
        ""
    )

    estado_pedido = request.args.get(
        "estado_pedido",
        ""
    )

    conexion = get_connection()

    cursor = conexion.cursor(
        dictionary=True
    )

    sql = """
        SELECT
            id_pedido,
            codigo_compra,
            fecha,
            cliente_nombre,
            total,
            estado_pago,
            estado_pedido
        FROM pedidos
        WHERE 1=1
    """

    valores = []

    if fecha:

        sql += """
            AND DATE(fecha) = %s
        """

        valores.append(
            fecha
        )

    if codigo:

        sql += """
            AND codigo_compra LIKE %s
        """

        valores.append(
            f"%{codigo}%"
        )

    if estado_pago:

        sql += """
            AND estado_pago = %s
        """

        valores.append(
            estado_pago
        )
    
    if estado_pedido:

        sql += """
            AND estado_pedido = %s
        """

        valores.append(
            estado_pedido
        )

    sql += """
        ORDER BY id_pedido DESC
    """

    cursor.execute(
        sql,
        valores
    )

    pedidos = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template(
        "admin_pedidos.html",
        pedidos=pedidos,
        fecha=fecha,
        codigo=codigo,
        estado_pago=estado_pago,
        estado_pedido=estado_pedido
    )

@admin_bp.route(
    "/admin/pedido/<int:id_pedido>"
)
@login_requerido
def ver_pedido(id_pedido):

    conexion = get_connection()

    cursor = conexion.cursor(
        dictionary=True
    )

    cursor.execute(
        """
        SELECT *
        FROM pedidos
        WHERE id_pedido = %s
        """,
        (id_pedido,)
    )

    pedido = cursor.fetchone()

    cursor.execute(
        """
        SELECT
            pd.cantidad,
            pd.precio_unitario,
            pd.subtotal,
            p.nombre
        FROM pedido_detalle pd
        INNER JOIN productos p
            ON pd.id_producto = p.id_producto
        WHERE pd.id_pedido = %s
        """,
        (id_pedido,)
    )

    detalle = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template(
        "admin_ver_pedido.html",
        pedido=pedido,
        detalle=detalle
    )

@admin_bp.route(
    "/admin/actualizar-pedido/<int:id_pedido>",
    methods=["POST"]
)
@login_requerido
def actualizar_pedido(id_pedido):

    estado_pago = request.form.get(
        "estado_pago"
    )

    estado_pedido = request.form.get(
        "estado_pedido"
    )

    conexion = get_connection()

    cursor = conexion.cursor()

    cursor.execute(
        """
        UPDATE pedidos
        SET
            estado_pago = %s,
            estado_pedido = %s
        WHERE id_pedido = %s
        """,
        (
            estado_pago,
            estado_pedido,
            id_pedido
        )
    )

    conexion.commit()

    cursor.close()
    conexion.close()

    return redirect(
        f"/admin/pedido/{id_pedido}"
    )

# ==========================
# ADMINISTRACION DE PRODUCTOS
# ==========================

@admin_bp.route(
    "/admin/productos"
)
@admin_o_encargado
def productos_admin():

    buscar = request.args.get(
        "buscar",
        ""
    )

    categoria_filtro = request.args.get(
        "categoria",
        ""
    )

    pagina = int(
        request.args.get(
            "pagina",
            1
        )
    )

    por_pagina = 25

    offset = (
        pagina - 1
    ) * por_pagina

    conexion = get_connection()

    cursor = conexion.cursor(
        dictionary=True
    )

    where = []

    parametros = []

    if buscar:

        where.append(
            "p.nombre LIKE %s"
        )

        parametros.append(
            f"%{buscar}%"
        )

    if categoria_filtro:

        where.append(
            "p.id_categoria = %s"
        )

        parametros.append(
            categoria_filtro
        )

    where_sql = ""

    if where:

        where_sql = (
            "WHERE "
            + " AND ".join(where)
        )

    # ==========================
    # TOTAL REGISTROS
    # ==========================

    sql_total = f"""
        SELECT COUNT(*) AS total
        FROM productos p
        {where_sql}
    """

    cursor.execute(
        sql_total,
        parametros
    )

    total_registros = cursor.fetchone()[
        "total"
    ]

    total_paginas = max(
        1,
        (total_registros + por_pagina - 1)
        // por_pagina
    )

    # ==========================
    # PRODUCTOS
    # ==========================

    sql_productos = f"""
        SELECT
            p.id_producto,
            p.nombre,
            c.nombre AS categoria,
            p.precio,
            p.imagen,
            p.destacado,
            p.orden_visual,
            p.sin_stock,
            p.activo
        FROM productos p
        INNER JOIN categorias c
            ON p.id_categoria = c.id_categoria
        {where_sql}
        ORDER BY
            c.nombre,
            p.orden_visual,
            p.nombre
        LIMIT %s
        OFFSET %s
    """

    parametros_productos = (
        parametros.copy()
    )

    parametros_productos.extend(
        [
            por_pagina,
            offset
        ]
    )

    cursor.execute(
        sql_productos,
        parametros_productos
    )

    productos = cursor.fetchall()

    # ==========================
    # CATEGORIAS FILTRO
    # ==========================

    cursor.execute("""
        SELECT
            id_categoria,
            nombre
        FROM categorias
        WHERE activo = 1
        ORDER BY nombre
    """)

    categorias = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template(
        "admin_productos.html",
        productos=productos,
        categorias=categorias,
        buscar=buscar,
        categoria_filtro=categoria_filtro,
        pagina=pagina,
        total_paginas=total_paginas
    )

@admin_bp.route(
    "/admin/producto/nuevo"
)
@admin_o_encargado
def nuevo_producto():

    conexion = get_connection()

    cursor = conexion.cursor(
        dictionary=True
    )

    cursor.execute("""
        SELECT
            id_categoria,
            nombre
        FROM categorias
        WHERE activo = 1
        ORDER BY nombre
    """)

    categorias = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template(
        "admin_producto_nuevo.html",
        categorias=categorias
    )

@admin_bp.route(
    "/admin/producto/guardar",
    methods=["POST"]
)
@admin_o_encargado
def guardar_producto():

    imagen_nombre = ""

    archivo = request.files.get(
        "imagen"
    )

    if archivo and archivo.filename:

        imagen_nombre = secure_filename(
            archivo.filename
        )

        ruta = os.path.join(
            "uploads",
            "productos",
            imagen_nombre
        )

        os.makedirs(
            os.path.dirname(ruta),
            exist_ok=True
        )

        archivo.save(
            ruta
        )

    conexion = get_connection()

    cursor = conexion.cursor()

    cursor.execute(
        """
        INSERT INTO productos
        (
            id_categoria,
            nombre,
            descripcion,
            unidad_medida,
            precio,
            imagen,
            destacado,
            orden_visual,
            sin_stock,
            activo
        )
        VALUES
        (
            %s,%s,%s,%s,%s,%s,%s,%s,%s,%s
        )
        """,
        (
            request.form.get(
                "id_categoria"
            ),

            request.form.get(
                "nombre"
            ),

            request.form.get(
                "descripcion"
            ),

            request.form.get(
                "unidad_medida"
            ),

            request.form.get(
                "precio"
            ),

            imagen_nombre,

            1 if request.form.get(
                "destacado"
            ) else 0,

            request.form.get(
                "orden_visual"
            ),

            1 if request.form.get(
                "sin_stock"
            ) else 0,

            1 if request.form.get(
                "activo"
            ) else 0
        )
    )

    conexion.commit()

    cursor.close()
    conexion.close()

    return redirect(
        "/admin/productos"
    )

@admin_bp.route(
    "/admin/producto/editar/<int:id_producto>"
)
@admin_o_encargado
def editar_producto(id_producto):

    conexion = get_connection()

    cursor = conexion.cursor(
        dictionary=True
    )

    cursor.execute("""
        SELECT *
        FROM productos
        WHERE id_producto = %s
    """,
    (id_producto,))
    
    producto = cursor.fetchone()

    cursor.execute("""
        SELECT
            id_categoria,
            nombre
        FROM categorias
        WHERE activo = 1
        ORDER BY nombre
    """)

    categorias = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template(
        "admin_producto_editar.html",
        producto=producto,
        categorias=categorias
    )

@admin_bp.route(
    "/admin/producto/actualizar/<int:id_producto>",
    methods=["POST"]
)
@admin_o_encargado
def actualizar_producto(id_producto):

    conexion = get_connection()

    cursor = conexion.cursor(
        dictionary=True
    )

    cursor.execute("""
        SELECT imagen
        FROM productos
        WHERE id_producto = %s
    """,
    (id_producto,))

    producto = cursor.fetchone()

    imagen_nombre = producto["imagen"]

    archivo = request.files.get(
        "imagen"
    )

    if archivo and archivo.filename:

        imagen_nombre = secure_filename(
            archivo.filename
        )

        ruta = os.path.join(
            "uploads",
            "productos",
            imagen_nombre
        )

        os.makedirs(
            os.path.dirname(ruta),
            exist_ok=True
        )

        archivo.save(ruta)

    cursor.execute("""
        UPDATE productos
        SET
            id_categoria = %s,
            nombre = %s,
            descripcion = %s,
            unidad_medida = %s,
            precio = %s,
            imagen = %s,
            destacado = %s,
            orden_visual = %s,
            sin_stock = %s,
            activo = %s
        WHERE id_producto = %s
    """,
    (
        request.form.get(
            "id_categoria"
        ),

        request.form.get(
            "nombre"
        ),

        request.form.get(
            "descripcion"
        ),

        request.form.get(
            "unidad_medida"
        ),

        request.form.get(
            "precio"
        ),

        imagen_nombre,

        1 if request.form.get(
            "destacado"
        ) else 0,

        request.form.get(
            "orden_visual"
        ),

        1 if request.form.get(
            "sin_stock"
        ) else 0,

        1 if request.form.get(
            "activo"
        ) else 0,

        id_producto
    ))

    conexion.commit()

    cursor.close()
    conexion.close()

    return redirect(
        "/admin/productos"
    )

#=============================
# ADMINISTRACION DE CATEGORIAS
#=============================

@admin_bp.route(
    "/admin/categorias"
)
@admin_o_encargado
def categorias_admin():

    conexion = get_connection()

    cursor = conexion.cursor(
        dictionary=True
    )

    cursor.execute("""
        SELECT
            id_categoria,
            nombre,
            imagen,
            activo
        FROM categorias
        ORDER BY nombre
    """)

    categorias = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template(
        "admin_categorias.html",
        categorias=categorias
    )

@admin_bp.route(
    "/admin/categoria/nueva"
)
@admin_o_encargado
def nueva_categoria():

    return render_template(
        "admin_categoria_nueva.html"
    )

@admin_bp.route(
    "/admin/categoria/guardar",
    methods=["POST"]
)
@admin_o_encargado
def guardar_categoria():

    conexion = get_connection()

    cursor = conexion.cursor()

    archivo = request.files.get("imagen")

    imagen_nombre = None

    if archivo and archivo.filename:

        imagen_nombre = secure_filename(
            archivo.filename
        )

        ruta = os.path.join(
            "uploads",
            "categorias",
            imagen_nombre
        )

        os.makedirs(
            os.path.dirname(ruta),
            exist_ok=True
        )

        archivo.save(ruta)

    cursor.execute("""
        INSERT INTO categorias
        (
            nombre,
            imagen,
            activo
        )
        VALUES
        (
            %s,
            %s,
            %s
        )
    """,
    (
        request.form.get(
            "nombre"
        ),

        imagen_nombre,

        1 if request.form.get(
            "activo"
        ) else 0
    ))

    conexion.commit()

    cursor.close()
    conexion.close()

    return redirect(
        "/admin/categorias"
    )

@admin_bp.route(
    "/admin/categoria/editar/<int:id_categoria>"
)
@admin_o_encargado
def editar_categoria(id_categoria):

    conexion = get_connection()

    cursor = conexion.cursor(
        dictionary=True
    )

    cursor.execute("""
        SELECT *
        FROM categorias
        WHERE id_categoria = %s
    """,
    (id_categoria,))

    categoria = cursor.fetchone()

    cursor.close()
    conexion.close()

    return render_template(
        "admin_categoria_editar.html",
        categoria=categoria
    )

@admin_bp.route(
    "/admin/categoria/actualizar/<int:id_categoria>",
    methods=["POST"]
)
@admin_o_encargado
def actualizar_categoria(id_categoria):

    conexion = get_connection()

    cursor = conexion.cursor(
        dictionary=True
    )

    cursor.execute("""
        SELECT imagen
        FROM categorias
        WHERE id_categoria = %s
    """,
    (id_categoria,))

    categoria = cursor.fetchone()

    imagen_nombre = categoria["imagen"]

    archivo = request.files.get(
        "imagen"
    )

    if archivo and archivo.filename:

        imagen_nombre = secure_filename(
            archivo.filename
        )

        ruta = os.path.join(
            "uploads",
            "categorias",
            imagen_nombre
        )

        os.makedirs(
            os.path.dirname(ruta),
            exist_ok=True
        )

        archivo.save(ruta)

    cursor.execute("""
        UPDATE categorias
        SET
            nombre = %s,
            imagen = %s,
            activo = %s
        WHERE id_categoria = %s
    """,
    (
        request.form.get(
            "nombre"
        ),

        imagen_nombre,

        1 if request.form.get(
            "activo"
        ) else 0,

        id_categoria
    ))

    conexion.commit()

    cursor.close()
    conexion.close()

    return redirect(
        "/admin/categorias"
    )

#============================
# CONFIGURACION EMPRESA
#============================

@admin_bp.route(
    "/admin/configuracion"
)
@solo_admin
def configuracion():

    conexion = get_connection()

    cursor = conexion.cursor(
        dictionary=True
    )

    cursor.execute("""
        SELECT *
        FROM configuracion
        WHERE id_configuracion = 1
    """)

    config = cursor.fetchone()

    cursor.close()
    conexion.close()

    return render_template(
        "admin_configuracion.html",
        config=config
    )

@admin_bp.route(
    "/admin/configuracion/guardar",
    methods=["POST"]
)
@solo_admin
def guardar_configuracion():

    conexion = get_connection()

    cursor = conexion.cursor(
        dictionary=True
    )

    cursor.execute("""
        SELECT logo
        FROM configuracion
        WHERE id_configuracion = 1
    """)

    config = cursor.fetchone()

    logo_nombre = config["logo"]

    archivo = request.files.get(
        "logo"
    )

    if archivo and archivo.filename:

        logo_nombre = secure_filename(
            archivo.filename
        )

        ruta_logo = os.path.join(
            "uploads",
            "logo",
            logo_nombre
        )

        os.makedirs(
            os.path.dirname(ruta_logo),
            exist_ok=True
        )

        archivo.save(
            ruta_logo
        )

    cursor.execute("""
        UPDATE configuracion
        SET
            nombre_empresa = %s,
            slogan = %s,
            telefono = %s,
            direccion = %s,
            google_maps_url = %s,
            whatsapp = %s,
            whatsapp_mensaje = %s,
            mostrar_whatsapp = %s,
            email = %s,
            facebook_nombre = %s,
            facebook_url = %s,
            horario_manana_desde = %s,
            horario_manana_hasta = %s,
            horario_tarde_desde = %s,
            horario_tarde_hasta = %s,
            horario_domingos_feriados = %s,
            logo = %s
        WHERE id_configuracion = 1
    """,
    (
        request.form.get("nombre_empresa"),
        request.form.get("slogan"),
        request.form.get("telefono"),
        request.form.get("direccion"),
        request.form.get("google_maps_url"),
        request.form.get("whatsapp"),
        request.form.get("whatsapp_mensaje"),
        request.form.get("mostrar_whatsapp"),
        request.form.get("email"),
        request.form.get("facebook_nombre"),
        request.form.get("facebook_url"),
        request.form.get("horario_manana_desde"),
        request.form.get("horario_manana_hasta"),
        request.form.get("horario_tarde_desde"),
        request.form.get("horario_tarde_hasta"),
        request.form.get("horario_domingos_feriados"),
        logo_nombre
    ))

    conexion.commit()

    cursor.close()
    conexion.close()

    return redirect(
        "/admin/configuracion"
    )

@admin_bp.route("/admin/config-display")
@solo_admin
def config_display():

    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM config_display
        WHERE id_display = 1
    """)

    display = cursor.fetchone()

    cursor.close()
    conexion.close()

    return render_template(
        "admin_config_display.html",
        display=display
    )

@admin_bp.route(
    "/admin/config-display/guardar",
    methods=["POST"]
)
@solo_admin
def guardar_config_display():

    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM config_display
        WHERE id_display = 1
    """)

    display = cursor.fetchone()

    cursor.execute("""
        UPDATE config_display
        SET
            banner_activo = %s,
            banner_texto = %s,
            banner_color = %s,
            banner_texto_color = %s,
            mensaje_envio = %s,
            mostrar_mensaje_envio = %s
        WHERE id_display = 1
    """, (
        request.form.get("banner_activo"),
        request.form.get("banner_texto"),
        request.form.get("banner_color"),
        request.form.get("banner_texto_color"),
        request.form.get("mensaje_envio"),
        request.form.get("mostrar_mensaje_envio")
    ))

    conexion.commit()
    cursor.close()
    conexion.close()

    return redirect("/admin/configuracion")

#==============================
# CONFIGURAR PROMOCIONES
#==============================

@admin_bp.route("/admin/promociones")
@solo_admin
def promociones():

    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM promociones
        ORDER BY orden_visualizacion ASC
    """)

    promociones = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template(
        "admin_promociones.html",
        promociones=promociones
    )

@admin_bp.route("/admin/promociones/nueva")
@solo_admin
def nueva_promocion():

    return render_template(
        "admin_promocion_nueva.html"
    )

@admin_bp.route("/admin/promociones/guardar", methods=["POST"])
@solo_admin
def guardar_promocion():

    conexion = get_connection()
    cursor = conexion.cursor()

    archivo = request.files.get("imagen")
    imagen_nombre = None

    if archivo and archivo.filename:

        imagen_nombre = secure_filename(archivo.filename)

        ruta = os.path.join(
            "uploads",
            "promociones",
            imagen_nombre
        )

        os.makedirs(
            os.path.dirname(ruta),
            exist_ok=True
        )

        archivo.save(ruta)

    cursor.execute("""
        INSERT INTO promociones
        (
            titulo,
            imagen,
            descripcion,
            fecha_inicio,
            fecha_fin,
            tipo_temporizador,
            activo,
            orden_visualizacion,
            fecha_creacion
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,NOW())
    """, (
        request.form.get("titulo"),
        imagen_nombre,
        request.form.get("descripcion"),
        request.form.get("fecha_inicio") or None,
        request.form.get("fecha_fin") or None,
        request.form.get("activo"),
        request.form.get("tipo_temporizador"),
        request.form.get("orden_visualizacion")
    ))

    conexion.commit()
    cursor.close()
    conexion.close()

    return redirect("/admin/promociones")

@admin_bp.route("/admin/promociones/editar/<int:id>")
@solo_admin
def editar_promocion(id):

    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM promociones
        WHERE id_promocion = %s
    """, (id,))

    promo = cursor.fetchone()

    cursor.close()
    conexion.close()

    return render_template(
        "admin_promocion_editar.html",
        promo=promo
    )

@admin_bp.route("/admin/promociones/actualizar/<int:id>", methods=["POST"])
@solo_admin
def actualizar_promocion(id):

    conexion = get_connection()
    cursor = conexion.cursor()

    archivo = request.files.get("imagen")

    if archivo and archivo.filename:

        imagen_nombre = secure_filename(archivo.filename)

        ruta = os.path.join(
            "uploads",
            "promociones",
            imagen_nombre
        )

        os.makedirs(
            os.path.dirname(ruta),
            exist_ok=True
        )

        archivo.save(ruta)

        cursor.execute("""
            UPDATE promociones
            SET imagen=%s
            WHERE id_promocion=%s
        """, (imagen_nombre, id))

    cursor.execute("""
        UPDATE promociones
        SET
            titulo=%s,
            descripcion=%s,
            fecha_inicio=%s,
            fecha_fin=%s,
            tipo_temporizador=%s,
            activo=%s,
            orden_visualizacion=%s
        WHERE id_promocion=%s
    """, (
        request.form.get("titulo"),
        request.form.get("descripcion"),
        request.form.get("fecha_inicio") or None,
        request.form.get("fecha_fin") or None,
        request.form.get("tipo_temporizador"),
        request.form.get("activo"),
        request.form.get("orden_visualizacion"),
        id
    ))

    conexion.commit()
    cursor.close()
    conexion.close()

    return redirect("/admin/promociones")


#==============================
# ADMINISTRACION DE ZONAS ENVIOS
#==============================

@admin_bp.route(
    "/admin/zonas-envio"
)
@solo_admin
def zonas_envio():

    conexion = get_connection()

    cursor = conexion.cursor(
        dictionary=True
    )

    cursor.execute("""
        SELECT
            id_zona,
            nombre_zona,
            descripcion,
            costo_envio,
            hora_desde,
            hora_hasta,
            activo
        FROM zonas_envio
        ORDER BY nombre_zona
    """)

    zonas = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template(
        "admin_zonas_envio.html",
        zonas=zonas
    )

@admin_bp.route(
    "/admin/zona/nueva"
)
@solo_admin
def nueva_zona():

    return render_template(
        "admin_zona_nueva.html"
    )

@admin_bp.route(
    "/admin/zona/guardar",
    methods=["POST"]
)
@solo_admin
def guardar_zona():

    conexion = get_connection()

    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO zonas_envio
        (
            nombre_zona,
            descripcion,
            costo_envio,
            hora_desde,
            hora_hasta,
            activo
        )
        VALUES
        (
            %s,%s,%s,%s,%s,%s
        )
    """,
    (
        request.form.get(
            "nombre_zona"
        ),

        request.form.get(
            "descripcion"
        ),

        request.form.get(
            "costo_envio"
        ),

        request.form.get(
            "hora_desde"
        ) or None,

        request.form.get(
            "hora_hasta"
        ) or None,

        1 if request.form.get(
            "activo"
        ) else 0
    ))

    conexion.commit()

    cursor.close()
    conexion.close()

    return redirect(
        "/admin/zonas-envio"
    )

@admin_bp.route(
    "/admin/zona/editar/<int:id_zona>"
)
@solo_admin
def editar_zona(id_zona):

    conexion = get_connection()

    cursor = conexion.cursor(
        dictionary=True
    )

    cursor.execute("""
        SELECT *
        FROM zonas_envio
        WHERE id_zona = %s
    """,
    (id_zona,))

    zona = cursor.fetchone()

    cursor.close()
    conexion.close()

    return render_template(
        "admin_zona_editar.html",
        zona=zona
    )

@admin_bp.route(
    "/admin/zona/actualizar/<int:id_zona>",
    methods=["POST"]
)
@solo_admin
def actualizar_zona(id_zona):

    conexion = get_connection()

    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE zonas_envio
        SET
            nombre_zona = %s,
            descripcion = %s,
            costo_envio = %s,
            hora_desde = %s,
            hora_hasta = %s,
            activo = %s
        WHERE id_zona = %s
    """,
    (
        request.form.get(
            "nombre_zona"
        ),

        request.form.get(
            "descripcion"
        ),

        request.form.get(
            "costo_envio"
        ),

        request.form.get(
            "hora_desde"
        ) or None,

        request.form.get(
            "hora_hasta"
        ) or None,

        1 if request.form.get(
            "activo"
        ) else 0,

        id_zona
    ))

    conexion.commit()

    cursor.close()
    conexion.close()

    return redirect(
        "/admin/zonas-envio"
    )

#================================
# LOGIN PANEL ADMINISTRATIVO
#================================

@admin_bp.route(
    "/admin/login"
)
def login_admin():

    return render_template(
        "admin_login.html"
    )

@admin_bp.route(
    "/admin/login",
    methods=["POST"]
)
def validar_login():

    usuario = request.form.get(
        "usuario"
    )

    password = request.form.get(
        "password"
    )

    conexion = get_connection()

    cursor = conexion.cursor(
        dictionary=True
    )

    cursor.execute("""
        SELECT *
        FROM usuarios_admin
        WHERE usuario = %s
        AND activo = 1
    """,
    (
        usuario,
    ))

    admin = cursor.fetchone()

    if not check_password_hash(
        admin["password"],
        password
    ):

        cursor.close()
        conexion.close()

        return render_template(
            "admin_login.html",
            error="Usuario o contraseña incorrectos"
        )
    

    cursor.close()
    conexion.close()

    session["admin"] = {

        "id_usuario":
            admin["id_usuario"],

        "usuario":
            admin["usuario"],

        "rol":
            admin["rol"]
    }

    return redirect(
        "/admin"
    )

@admin_bp.route(
    "/admin/logout"
)
def logout_admin():

    session.pop(
        "admin",
        None
    )

    return redirect(
        "/admin/login"
    )

@admin_bp.route(
    "/admin"
)
@login_requerido
def dashboard_admin():

    conexion = get_connection()

    cursor = conexion.cursor(
        dictionary=True
    )

    cursor.execute("""
        SELECT COUNT(*) total
        FROM pedidos
        WHERE estado_pedido = 'Pendiente'
    """)

    pedidos_pendientes = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) total
        FROM pedidos
        WHERE estado_pedido = 'Preparado'
    """)

    pedidos_preparados = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) total
        FROM pedidos
        WHERE estado_pedido = 'Listo'
    """)

    pedidos_listos = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT
            COALESCE(SUM(total),0) total
        FROM pedidos
        WHERE DATE(fecha) = CURDATE()
    """)

    ventas_hoy = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT
            COALESCE(SUM(total),0) total
        FROM pedidos
        WHERE YEAR(fecha)=YEAR(CURDATE())
        AND MONTH(fecha)=MONTH(CURDATE())
    """)

    ventas_mes = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) total
        FROM productos
        WHERE sin_stock = 1
          AND activo = 1
    """)

    productos_sin_stock = cursor.fetchone()["total"]

    cursor.close()
    conexion.close()

    return render_template(
        "admin_dashboard.html",

        pedidos_pendientes=pedidos_pendientes,

        pedidos_preparados=pedidos_preparados,

        pedidos_listos=pedidos_listos,

        ventas_hoy=ventas_hoy,

        ventas_mes=ventas_mes,

        productos_sin_stock=productos_sin_stock
    )

@admin_bp.route(
    "/admin/usuarios"
)
@solo_admin
def usuarios_admin():

    conexion = get_connection()

    cursor = conexion.cursor(
        dictionary=True
    )

    cursor.execute("""
        SELECT
            id_usuario,
            usuario,
            rol,
            activo
        FROM usuarios_admin
        ORDER BY usuario
    """)

    usuarios = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template(
        "admin_usuarios.html",
        usuarios=usuarios
    )

@admin_bp.route(
    "/admin/usuario/nuevo"
)
@solo_admin
def nuevo_usuario():

    return render_template(
        "admin_usuario_nuevo.html"
    )

@admin_bp.route(
    "/admin/usuario/guardar",
    methods=["POST"]
)
@solo_admin
def guardar_usuario():

    conexion = get_connection()

    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO usuarios_admin
        (
            usuario,
            password,
            rol,
            activo
        )
        VALUES
        (
            %s,%s,%s,%s
        )
    """,
    (
        request.form.get(
            "usuario"
        ),

        generate_password_hash(
            request.form.get(
                "password"
            )
        ),

        request.form.get(
            "rol"
        ),

        1 if request.form.get(
            "activo"
        ) else 0
    ))

    conexion.commit()

    cursor.close()
    conexion.close()

    return redirect(
        "/admin/usuarios"
    )

@admin_bp.route(
    "/admin/usuario/editar/<int:id_usuario>"
)
@solo_admin
def editar_usuario(id_usuario):

    conexion = get_connection()

    cursor = conexion.cursor(
        dictionary=True
    )

    cursor.execute("""
        SELECT
            id_usuario,
            usuario,
            rol,
            activo
        FROM usuarios_admin
        WHERE id_usuario = %s
    """,
    (id_usuario,))

    usuario = cursor.fetchone()

    cursor.close()
    conexion.close()

    return render_template(
        "admin_usuario_editar.html",
        usuario=usuario
    )

@admin_bp.route(
    "/admin/usuario/actualizar/<int:id_usuario>",
    methods=["POST"]
)
@solo_admin
def actualizar_usuario(id_usuario):

    usuario = request.form.get(
        "usuario"
    )

    rol = request.form.get(
        "rol"
    )

    password = request.form.get(
        "password"
    )

    activo = (
        1 if request.form.get(
            "activo"
        ) else 0
    )

    conexion = get_connection()

    cursor = conexion.cursor()

    if password:

        cursor.execute("""
            UPDATE usuarios_admin
            SET
                usuario = %s,
                password = %s,
                rol = %s,
                activo = %s
            WHERE id_usuario = %s
        """,
        (
            usuario,

            generate_password_hash(
                password
            ),

            rol,

            activo,

            id_usuario
        ))

    else:

        cursor.execute("""
            UPDATE usuarios_admin
            SET
                usuario = %s,
                rol = %s,
                activo = %s
            WHERE id_usuario = %s
        """,
        (
            usuario,

            rol,

            activo,

            id_usuario
        ))

    conexion.commit()

    cursor.close()
    conexion.close()

    return redirect(
        "/admin/usuarios"
    )

#================================
# CONFIGURAR DISPLAY
#================================

@admin_bp.route("/admin/config-display")
def admin_config_display():

    return render_template(
        "admin_config_display.html"
    )

#================================
# CONFIGURAR PROMOCIONES
#================================

@admin_bp.route("/admin/promociones")
def admin_promociones():

    return render_template(
        "admin_promociones.html"
    )