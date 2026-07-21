import os
import mercadopago


def crear_preferencia(
    codigo_compra,
    productos,
    envio=0
):

    sdk = mercadopago.SDK(
        os.getenv(
            "MP_ACCESS_TOKEN"
        )
    )

    items = []

    for producto in productos:

        items.append({

            "title":
                producto["nombre"],

            "quantity":
                int(
                    producto["cantidad"]
                ),

            "unit_price":
                float(
                    producto["precio_unitario"]
                ),

            "currency_id":
                "ARS"
        })

    if float(envio) > 0:

        items.append({

            "title":
                "Costo de envío",

            "quantity":
                1,

            "unit_price":
                float(envio),

            "currency_id":
                "ARS"
        })


    preference_data = {

        "items":
            items,

        "external_reference":
            codigo_compra,

        "back_urls": {

            "success":
                f"{os.getenv('URL_BASE')}/pago-exitoso",

            "failure":
                f"{os.getenv('URL_BASE')}/pago-fallido",

            "pending":
                f"{os.getenv('URL_BASE')}/pago-pendiente"
        },

        #"auto_return":
        #    "approved"
    }

    preference_response = (
        sdk.preference()
        .create(
            preference_data
        )
    )

    return (
        preference_response["response"]
    )