from flask import Blueprint
from flask import Response
from flask import request

from db import get_connection


sitemap_bp = Blueprint(
    "sitemap",
    __name__
)


@sitemap_bp.route("/sitemap.xml")
def sitemap():

    base_url = request.url_root.rstrip("/")

    conexion = get_connection()

    cursor = conexion.cursor(
        dictionary=True
    )

    cursor.execute("""
        SELECT id_categoria
        FROM categorias
        WHERE activo = 1
    """)

    categorias = cursor.fetchall()

    cursor.close()
    conexion.close()

    xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
"""

    paginas_fijas = [
        "",
        "/categorias",
        "/nosotros",
        "/contacto",
        "/envios",
        "/medios-pago"
    ]

    for pagina in paginas_fijas:

        xml += f"""
    <url>
        <loc>{base_url}{pagina}</loc>
    </url>
"""

    for categoria in categorias:

        xml += f"""
    <url>
        <loc>{base_url}/productos/{categoria['id_categoria']}</loc>
    </url>
"""

    xml += """
</urlset>
"""

    return Response(
        xml,
        mimetype="application/xml"
    )