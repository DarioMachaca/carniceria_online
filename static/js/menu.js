document.addEventListener(
    "DOMContentLoaded",
    () => {

        const menuBtn =
            document.querySelector(
                ".menu-btn"
            );

        const menu =
            document.getElementById(
                "menu-lateral"
            );

        const cerrar =
            document.getElementById(
                "cerrar-menu"
            );

        const overlay =
            document.getElementById(
                "overlay-menu"
            );

        menuBtn.addEventListener(
            "click",
            () => {

                menu.classList.add(
                    "abierto"
                );

                overlay.classList.add(
                    "abierto"
                );

            }
        );

        cerrar.addEventListener(
            "click",
            cerrarMenu
        );

        overlay.addEventListener(
            "click",
            cerrarMenu
        );

        function cerrarMenu() {

            menu.classList.remove(
                "abierto"
            );

            overlay.classList.remove(
                "abierto"
            );
        }

    }
);