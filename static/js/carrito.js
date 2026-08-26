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

                    const respuesta =
                    await fetch(
                        `/ajax/agregar-carrito/${id}`
                    );

                    const data =
                    await respuesta.json();

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

                    const respuesta =
                    await fetch(
                        `/ajax/quitar-carrito/${id}`
                    );

                    const data =
                    await respuesta.json();

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