console.log("Ruleta cargada");

const sectores = {
    "20% Descuento": 0,
    "10% Descuento": 1,
    "5% Descuento": 2,
    "Seguí Participando": 3,
    "Combo Hamburguesas": 4,
    "Combo Milanesas Sandwich": 5,
    "Mila XXL": 6,
    "Gorra": 7,
    "Envío Gratis": 9
};



const ruleta =
    document.getElementById(
        "ruleta-svg"
    );

    console.log("Ruleta:", ruleta);

let rotacion = 0;

function girarHastaSector(sector) {

    document
        .querySelector(
            ".ruleta-form"
        )
        .style.display = "none";

    const gradosPorSector = 36;

    const centroSector =
        (sector * gradosPorSector) + 18;

    rotacion +=
        1800 +
        (360 - centroSector);

    ruleta.style.transform =
        `rotate(${rotacion}deg)`;
}

const formulario =
    document.getElementById(
        "form-ruleta"
    );

    console.log(formulario);

formulario.addEventListener(
    "submit",
    async function(e) {

        console.log("Formulario enviado");

        e.preventDefault();

        const mensaje =
            document.getElementById(
                "mensaje-ruleta"
            );

        mensaje.style.display = "none";
        mensaje.innerHTML = "";

        const datos =
            new FormData(formulario);

            console.log(
                "Código enviado:",
                datos.get("codigo")
            );
        
        const boton =
            document.querySelector(
                ".btn-girar"
            );

        boton.disabled = true;

        const respuesta =
            await fetch(
                "/ruleta/girar",
                {
                    method: "POST",
                    body: datos
                }
            );

        const resultado =
            await respuesta.json();

        console.log(resultado);

        if (!resultado.ok) {

            const modal =
                document.getElementById(
                    "modal-ruleta"
                );

            const modalBody =
                document.getElementById(
                    "modal-body"
                );

            modalBody.innerHTML =
`
                <h2>❌ Atención</h2>

                <p>
                    ${resultado.mensaje}
                </p>
`       ;

            modal.style.display = "flex";

            boton.disabled = false;

            return;
        }

        const sector =
            sectores[resultado.premio];

        console.log(
            "Premio:",
            resultado.premio
        );

        console.log(
            "Sector:",
            sector
        );

        girarHastaSector(sector);

        setTimeout(() => {

            if (
                resultado.premio ===
                "Seguí Participando"
            ) {

                const modal =
                    document.getElementById(
                        "modal-ruleta"
                    );

                const modalBody =
                    document.getElementById(
                        "modal-body"
                    );

                modalBody.innerHTML =
`
                    <h2>😊 Seguí Participando</h2>

                    <p>
                        Esta vez no hubo premio.
                    </p>

                    <p>
                        Te esperamos nuevamente.
                    </p>
`               ;

                modal.style.display = "flex";

            } else {

                const modal =
                    document.getElementById(
                        "modal-ruleta"
                    );

                const modalBody =
                    document.getElementById(
                        "modal-body"
                    );

                modalBody.innerHTML =
`
                    <h2>🎉 FELICITACIONES 🎉</h2>

                    <p>Ganaste:</p>

                    <h3>${resultado.premio}</h3>

                    <p>
                        Mostrá esta pantalla
                        o una captura de pantalla
                        en caja para retirar
                        tu premio, o presentá
                        tu cartoncito.
                    </p>
`               ;

                modal.style.display = "flex";

                setTimeout(() => {

                    const fin =
                        Date.now() + 3000;

                    const intervalo =
                        setInterval(() => {

                            if (Date.now() > fin) {

                                clearInterval(
                                    intervalo
                                );

                                return;
                            }

                            confetti({
                                particleCount: 50,
                                spread: 80,
                                zIndex: 99999
                            });

                        }, 250);

                }, 500);
            }

        }, 5000);

        boton.disabled = false;

    }
);

// ==================================
// BOTON IR A LA TIENDA
// ==================================

const btnCerrar =
    document.getElementById(
        "cerrar-modal"
    );

if (btnCerrar) {

    btnCerrar.addEventListener(
        "click",
        function() {

            window.location.href = "/";

        }
    );
}

const btnCerrarX =
    document.getElementById(
        "cerrar-modal-x"
    );

if (btnCerrarX) {

    btnCerrarX.addEventListener(
        "click",
        function() {

            document
                .getElementById(
                    "modal-ruleta"
                )
                .style.display = "none";

        }
    );
}