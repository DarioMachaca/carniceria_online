from PIL import Image
import os

def guardar_imagen_optimizada(
    archivo,
    ruta_destino,
    ancho_max=1200,
    alto_max=1200,
    calidad=85
):

    img = Image.open(archivo)

    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    img.thumbnail((ancho_max, alto_max))

    os.makedirs(
        os.path.dirname(ruta_destino),
        exist_ok=True
    )

    img.save(
        ruta_destino,
        format="JPEG",
        quality=calidad,
        optimize=True
    )