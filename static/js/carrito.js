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

                    document.getElementById(
                        `cantidad-${id}`
                    ).innerText =
                    data.cantidad;

                    document.querySelector(
                        ".cart-badge"
                    ).innerText =
                    data.total_items;
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

                    document.getElementById(
                        `cantidad-${id}`
                    ).innerText =
                    data.cantidad;

                    document.querySelector(
                        ".cart-badge"
                    ).innerText =
                    data.total_items;
                }
            );

        });

    }
);