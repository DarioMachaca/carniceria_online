from flask import Flask
from flask import session
from flask import send_from_directory


from routes.home import home_bp
from routes.categorias import categorias_bp
from routes.productos import productos_bp
from routes.carrito import carrito_bp
from routes.checkout import checkout_bp
from routes.admin import admin_bp
from models.display import obtener_display
from models.configuracion import obtener_configuracion

app = Flask(__name__)

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):

    return send_from_directory(
        'uploads',
        filename
    )

app.secret_key = "carrito_sistema_2026"

@app.context_processor
def variables_globales():

    carrito = session.get(
        "carrito",
        {}
    )

    cantidad_items = len(
        carrito
    )

    display = obtener_display()

    config = obtener_configuracion()

    return dict(
        cantidad_items=cantidad_items,
        display=display,
        config=config
    )

app.register_blueprint(home_bp)

app.register_blueprint(
    categorias_bp
)

app.register_blueprint(
    productos_bp
)

app.register_blueprint(
    carrito_bp
)

app.register_blueprint(
    checkout_bp
)

app.register_blueprint(
    admin_bp
)

if __name__ == "__main__":

    app.run(
        debug=True
    )