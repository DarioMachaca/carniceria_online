document.addEventListener(
    "DOMContentLoaded",
    () => {

        const slider =
            document.querySelector(
                ".slider-promociones"
            );

        if (!slider) return;

        const slides =
            document.querySelectorAll(
                ".promo-slide"
            );

        const dots =
            document.querySelectorAll(
                ".dot"
            );

        let index = 0;

        function mostrarSlide(i) {

            slider.style.transform =
                `translateX(-${i * 100}%)`;

            dots.forEach(
                dot => dot.classList.remove(
                    "active"
                )
            );

            dots[i].classList.add(
                "active"
            );
        }

        function siguiente() {

            index++;

            if (
                index >= slides.length
            ) {

                index = 0;
            }

            mostrarSlide(index);
        }

        function anterior() {

            index--;

            if (
                index < 0
            ) {

                index =
                    slides.length - 1;
            }

            mostrarSlide(index);
        }

        document
            .querySelector(".next")
            ?.addEventListener(
                "click",
                siguiente
            );

        document
            .querySelector(".prev")
            ?.addEventListener(
                "click",
                anterior
            );

        dots.forEach(
            (dot, i) => {

                dot.addEventListener(
                    "click",
                    () => {

                        index = i;

                        mostrarSlide(
                            index
                        );
                    }
                );
            }
        );

        mostrarSlide(0);

        setInterval(
            siguiente,
            4000
        );
    }
);