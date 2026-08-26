document.addEventListener(
    "DOMContentLoaded",
    () => {

        document
        .querySelectorAll(".btn-mas")
        .forEach(btn => {

            btn.addEventListener(
                "click",
                async () => {

                    const id = btn.dataset.id;

                    const nombre =
                    btn.dataset.nombre;

                    const precio =
                    parseFloat(
                        btn.dataset.precio
                    );

                    const unidad =
                    btn.dataset.unidad;

                    const respuesta =
                    await fetch(
                        `/ajax/agregar-carrito/${id}`
                    );

                    const data =
                    await respuesta.json();

                    if (
                        typeof gtag !==
                        "undefined"
                    ) {

                        const cantidadAgregada =
                        unidad === "kg"
                            ? 0.5
                            : 1;

                        gtag(
                            "event",
                            "add_to_cart",
                            {
                                currency: "ARS",
                                value:
                                    precio *
                                    cantidadAgregada,
                                items: [
                                    {
                                        item_id: id,
                                        item_name: nombre,
                                        price: precio,
                                        quantity:
                                            cantidadAgregada
                                    }
                                ]
                            }
                        );

                    }

                    const cantidadElemento =
                    document.getElementById(
                        `cantidad-${id}`
                    );

                    if (cantidadElemento) {

                        if (
                            document.getElementById(
                                `subtotal-${id}`
                            )
                        ) {

                            const textoActual =
                            cantidadElemento.innerText;

                            if (
                                textoActual.includes(
                                    "kg"
                                )
                            ) {

                                cantidadElemento.innerText =
                                `${data.cantidad} kg`;

                            } else {

                                cantidadElemento.innerText =
                                `${data.cantidad} un`;

                            }

                        } else {

                            cantidadElemento.innerText =
                            data.cantidad;

                        }

                    }

                    document.querySelector(
                        ".cart-badge"
                    ).innerText =
                    data.total_items;

                    const subtotalElemento =
                    document.getElementById(
                        `subtotal-${id}`
                    );

                    if (subtotalElemento) {

                        subtotalElemento.innerText =
    `                   $ ${data.subtotal}`;

                    }

                    const totalElemento =
                    document.getElementById(
                        "total-general"
                    );

                    if (totalElemento) {

                        totalElemento.innerText =
    `                   TOTAL: $ ${data.total_general}`;

                    }
                }
            );

        });

        document
        .querySelectorAll(".btn-menos")
        .forEach(btn => {

            btn.addEventListener(
                "click",
                async () => {

                    const id = btn.dataset.id;

                    const nombre =
                    btn.dataset.nombre;

                    const precio =
                    parseFloat(
                        btn.dataset.precio
                    );

                    const unidad =
                    btn.dataset.unidad;

                    const respuesta =
                    await fetch(
                        `/ajax/quitar-carrito/${id}`
                    );

                    const data =
                    await respuesta.json();

                    if (
                        typeof gtag !==
                        "undefined"
                    ) {

                        const cantidadQuitada =
                        unidad === "kg"
                            ? 0.5
                            : 1;

                        gtag(
                            "event",
                            "remove_from_cart",
                            {
                                currency: "ARS",
                                value:
                                    precio *
                                    cantidadQuitada,
                                items: [
                                    {
                                        item_id: id,
                                        item_name: nombre,
                                        price: precio,
                                        quantity:
                                            cantidadQuitada
                                    }
                                ]
                            }
                        );

                    }

                    if (data.cantidad === 0) {

                        const producto =
                        document.getElementById(
                            `producto-${id}`
                        );

                        if (producto) {

                            producto.remove();

                        }

                    }

                    const cantidadElemento =
                    document.getElementById(
                        `cantidad-${id}`
                    );

                    if (cantidadElemento) {

                        if (
                            document.getElementById(
                                `subtotal-${id}`
                            )
                        ) {

                            const textoActual =
                            cantidadElemento.innerText;

                            if (
                                textoActual.includes(
                                    "kg"
                                )
                            ) {

                                cantidadElemento.innerText =
                                `${data.cantidad} kg`;

                            } else {

                                cantidadElemento.innerText =
                                `${data.cantidad} un`;

                            }

                        } else {

                            cantidadElemento.innerText =
                            data.cantidad;

                        }

                    }

                    document.querySelector(
                        ".cart-badge"
                    ).innerText =
                    data.total_items;

                    const subtotalElemento =
                    document.getElementById(
                        `subtotal-${id}`
                    );

                    if (subtotalElemento) {

                        subtotalElemento.innerText =
    `                   $ ${data.subtotal}`;

                    }

                    const totalElemento =
                    document.getElementById(
                        "total-general"
                    );

                    if (totalElemento) {

                        totalElemento.innerText =
    `                   TOTAL: $ ${data.total_general}`;

                    }
                    
                }
            );

        });

    }
);