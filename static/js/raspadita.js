console.log("Raspadita cargada");

const formulario =
    document.getElementById(
        "form-raspadita"
    );

let premioActual = "";
let raspadoCompleto = false;

formulario.addEventListener(
    "submit",
    async function(e) {

        e.preventDefault();

        const datos =
            new FormData(formulario);

        const boton =
            document.querySelector(
                ".btn-girar"
            );

        boton.disabled = true;

        const respuesta =
            await fetch(
                "/raspadita/revelar",
                {
                    method: "POST",
                    body: datos
                }
            );

        const resultado =
            await respuesta.json();

        if (!resultado.ok) {

            const modal =
                document.getElementById(
                    "modal-raspadita"
                );

            const modalBody =
                document.getElementById(
                    "modal-body"
                );

            modalBody.innerHTML =
`
<h2>❌ Atención</h2>
<p>${resultado.mensaje}</p>
`;

            modal.style.display =
                "flex";

            boton.disabled = false;

            return;
        }

        premioActual =
            resultado.premio;

        document
            .getElementById(
                "texto-premio"
            )
            .innerHTML =
            premioActual;

        document
            .querySelector(
                ".ruleta-form"
            )
            .style.display =
            "none";

        document
            .getElementById(
                "raspadita-container"
            )
            .style.display =
            "flex";

        iniciarRaspadita();

        boton.disabled = false;

    }
);

function iniciarRaspadita() {

    const canvas =
        document.getElementById(
            "canvas-raspadita"
        );

    const ctx =
        canvas.getContext("2d");

    ctx.fillStyle =
        "#BDBDBD";

    ctx.fillRect(
        0,
        0,
        canvas.width,
        canvas.height
    );

    ctx.fillStyle =
        "#666";

    ctx.font =
        "bold 28px Montserrat";

    ctx.textAlign =
        "center";

    ctx.fillText(
        "RASPÁ AQUÍ",
        canvas.width / 2,
        canvas.height / 2
    );

    let dibujando = false;

    function raspar(x, y) {

        ctx.globalCompositeOperation =
            "destination-out";

        ctx.beginPath();

        ctx.arc(
            x,
            y,
            25,
            0,
            Math.PI * 2
        );

        ctx.fill();

    }

    canvas.addEventListener(
        "mousedown",
        () => dibujando = true
    );

    canvas.addEventListener(
        "mouseup",
        () => {

            dibujando = false;

            verificarRaspado();

        }
    );

    canvas.addEventListener(
        "mousemove",
        function(e) {

            if (!dibujando) {
                return;
            }

            const rect =
                canvas.getBoundingClientRect();

            raspar(
                e.clientX - rect.left,
                e.clientY - rect.top
            );

        }
    );

    canvas.addEventListener(
        "touchstart",
        () => dibujando = true
    );

    canvas.addEventListener(
        "touchend",
        () => {

            dibujando = false;

            verificarRaspado();

        }
    );

    canvas.addEventListener(
        "touchmove",
        function(e) {

            e.preventDefault();

            if (!dibujando) {
                return;
            }

            const rect =
                canvas.getBoundingClientRect();

            const touch =
                e.touches[0];

            raspar(
                touch.clientX - rect.left,
                touch.clientY - rect.top
            );

        }
    );

    function verificarRaspado() {

        if (raspadoCompleto) {
            return;
        }

        const imageData =
            ctx.getImageData(
                0,
                0,
                canvas.width,
                canvas.height
            );

        let transparentes = 0;

        for (
            let i = 3;
            i < imageData.data.length;
            i += 4
        ) {

            if (
                imageData.data[i] === 0
            ) {

                transparentes++;

            }

        }

        const porcentaje =
            (
                transparentes /
                (canvas.width * canvas.height)
            ) * 100;

        if (porcentaje > 45) {

            raspadoCompleto = true;

            mostrarResultado();

        }

    }

}

function mostrarResultado() {

    const modal =
        document.getElementById(
            "modal-raspadita"
        );

    const modalBody =
        document.getElementById(
            "modal-body"
        );

    if (
        premioActual ===
        "Seguí Participando"
    ) {

        modalBody.innerHTML =
`
<h2>😊 Seguí Participando</h2>

<p>
Esta vez no hubo premio.
</p>
`;

    } else {

        modalBody.innerHTML =
`
<h2>🎉 FELICITACIONES 🎉</h2>

<p>Ganaste:</p>

<h3>${premioActual}</h3>

<p>
Mostrá esta pantalla
en caja para retirar
tu premio.
</p>
`;

        const fin =
            Date.now() + 3000;

        const intervalo =
            setInterval(() => {

                if (
                    Date.now() > fin
                ) {

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

    }

    modal.style.display =
        "flex";

}

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
                    "modal-raspadita"
                )
                .style.display =
                "none";

        }
    );

}