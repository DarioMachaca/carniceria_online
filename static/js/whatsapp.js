console.log("Whatsapp JS cargado");
document.addEventListener(
    "DOMContentLoaded",
    () => {

        document
        .querySelectorAll(".btn-whatsapp-agregar")
        .forEach(btn => {

            btn.addEventListener(
                "click",
                async () => {

                    const id =
                        btn.dataset.id;

                    await fetch(
                        `/ajax/whatsapp/agregar/${id}`
                    );

                    location.reload();

                }
            );

        });

        document
        .querySelectorAll(".btn-whatsapp-quitar")
        .forEach(btn => {

            btn.addEventListener(
                "click",
                async () => {

                    const id =
                        btn.dataset.id;

                    await fetch(
                        `/ajax/whatsapp/quitar/${id}`
                    );

                    location.reload();

                }
            );

        });

        document
        .querySelectorAll(".btn-whatsapp-eliminar")
        .forEach(btn => {

            btn.addEventListener(
                "click",
                async () => {

                    const id =
                        btn.dataset.id;

                    await fetch(
                        `/ajax/whatsapp/eliminar/${id}`
                    );

                    location.reload();

                }
            );

        });

    }
);

const buscador =
document.getElementById(
    "buscar-producto"
);

const sugerencias =
document.getElementById(
    "sugerencias-productos"
);

buscador.addEventListener(
    "keyup",
    async () => {

        const texto =
        buscador.value;

        if(texto.length < 2){

            sugerencias.innerHTML = "";
            return;
        }

        const respuesta =
        await fetch(
            `/admin/whatsapp/sugerencias?q=${texto}`
        );

        const productos =
        await respuesta.json();

        let html = "";

        productos.forEach(
            producto => {

                html += `
                <div class="item-sugerencia">

                    <strong>
                        ${producto.nombre}
                    </strong>

                    <br>

                    $ ${producto.precio}

                    ${
                        producto.unidad_medida == "kg"
                        ? "/kg"
                        : "/un"
                    }

                    <br><br>

                    <button
                        type="button"
                        class="btn-admin"
                        onclick="agregarProductoDirecto(${producto.id_producto})"
                    >
                        ➕ Agregar
                    </button>

                </div>

                <hr>
        `       ;
            }
        );

        sugerencias.innerHTML = html;
    }
);

function seleccionarProducto(nombre){

    buscador.value = nombre;

    sugerencias.innerHTML = "";
}

async function agregarProductoDirecto(id){

    await fetch(
        `/ajax/whatsapp/agregar/${id}`
    );

    location.reload();
}