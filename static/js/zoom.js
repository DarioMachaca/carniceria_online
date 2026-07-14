console.log("zoom.js cargado correctamente");

document.addEventListener(
    "DOMContentLoaded",
    function(){

        const botonesZoom =
            document.querySelectorAll(
                ".zoom-btn"
            );

        console.log(
            "Botones encontrados:",
            botonesZoom.length
        );


        const modal =
            document.getElementById(
                "modal-imagen"
            );


        const imagen =
            document.getElementById(
                "imagen-modal"
            );


        const cerrar =
            document.querySelector(
                ".cerrar-modal"
            );


        botonesZoom.forEach(
            boton => {


                boton.addEventListener(
                    "click",
                    function(){

                        console.log(
                            "Click en lupa",
                            this.dataset.img
                        );


                        imagen.src =
                            this.dataset.img;


                        modal.style.display =
                            "flex";


                    }
                );


            }
        );


        cerrar.addEventListener(
            "click",
            function(){

                modal.style.display =
                    "none";

            }
        );


        modal.addEventListener(
            "click",
            function(e){

                if(e.target === modal){

                    modal.style.display =
                        "none";

                }

            }
        );


    }
);