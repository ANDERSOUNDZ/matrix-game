/**
 * Efecto de lluvia de caracteres estilo Matrix.
 *
 * @param {Object} options
 * @param {string|HTMLElement} options.target Contenedor o selector CSS.
 * @param {string} options.effect Nombre del efecto.
 * @param {number} options.time Duración en milisegundos.
 * @param {number} options.fontSize Tamaño de las letras.
 * @param {number} options.speed Velocidad de actualización.
 * @param {string} options.text Caracteres utilizados.
 * @param {boolean} options.removeOnFinish Elimina el efecto al terminar.
 * @param {Function} options.onFinish Función ejecutada al finalizar.
 * @param {string|HTMLAudioElement} options.sound Sonido a reproducir mientras
 *   dura el efecto: una URL/ruta de audio, o un HTMLAudioElement ya creado.
 * @param {number} options.soundVolume Volumen del sonido (0 a 1).
 *
 * @returns {{ stop: Function }}
 */
function matrixRain(options = {}) {
    const config = {
        target: "#aquiQuiero",
        effect: "RAIN-TEXT",
        time: 3000,
        fontSize: 18,
        speed: 45,
        text: "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZアイウエオカキクケコ",
        removeOnFinish: true,
        onFinish: null,
        sound: null,
        soundVolume: 0.5,
        ...options
    };

    const container =
        typeof config.target === "string"
            ? document.querySelector(config.target)
            : config.target;

    if (!container) {
        console.error(
            `matrixRain: no se encontró el contenedor "${config.target}".`
        );

        return {
            stop() {}
        };
    }

    if (config.effect !== "RAIN-TEXT") {
        console.error(
            `matrixRain: el efecto "${config.effect}" no existe.`
        );

        return {
            stop() {}
        };
    }

    /*
     * El efecto solamente modifica visualmente este contenedor.
     * No coloca negro el body ni el resto de la página.
     */
    const originalPosition = getComputedStyle(container).position;
    const originalOverflow = container.style.overflow;

    if (originalPosition === "static") {
        container.style.position = "relative";
    }

    container.style.overflow = "hidden";

    /*
     * Eliminar una animación anterior del mismo contenedor.
     */
    const previousEffect = container.querySelector(
        ":scope > .matrix-rain-overlay"
    );

    if (previousEffect) {
        previousEffect.remove();
    }

    const overlay = document.createElement("div");
    overlay.className = "matrix-rain-overlay";

    Object.assign(overlay.style, {
        position: "absolute",
        inset: "0",
        width: "100%",
        height: "100%",
        overflow: "hidden",
        backgroundColor: "#000000",
        zIndex: "9999",
        opacity: "1",
        transition: "opacity 500ms ease",
        pointerEvents: "none"
    });

    const canvas = document.createElement("canvas");

    Object.assign(canvas.style, {
        display: "block",
        width: "100%",
        height: "100%"
    });

    overlay.appendChild(canvas);
    container.appendChild(overlay);

    const context = canvas.getContext("2d");

    let animationInterval = null;
    let finishTimeout = null;
    let removeTimeout = null;
    let resizeObserver = null;
    let fadeAudioInterval = null;
    let stopped = false;
    let drops = [];

    const audio = config.sound
        ? (config.sound instanceof HTMLAudioElement
            ? config.sound
            : new Audio(config.sound))
        : null;

    function reproducirSonido() {
        if (!audio) {
            return;
        }

        audio.loop = true;
        audio.volume = config.soundVolume;
        audio.currentTime = 0;

        const promesa = audio.play();

        if (promesa && typeof promesa.catch === "function") {
            promesa.catch(() => {
                /*
                 * El navegador puede bloquear el autoplay si no hubo
                 * interacción previa del usuario; no es un error fatal.
                 */
            });
        }
    }

    function detenerSonido() {
        if (!audio) {
            return;
        }

        const volumenInicial = audio.volume;
        const pasos = 10;
        let paso = 0;

        fadeAudioInterval = setInterval(() => {
            paso++;
            audio.volume = Math.max(0, volumenInicial * (1 - paso / pasos));

            if (paso >= pasos) {
                clearInterval(fadeAudioInterval);
                audio.pause();
                audio.currentTime = 0;
            }
        }, 50);
    }

    const characters = Array.from(config.text);

    function configureCanvas() {
        const rectangle = container.getBoundingClientRect();

        const width = Math.max(1, Math.floor(rectangle.width));
        const height = Math.max(1, Math.floor(rectangle.height));

        const pixelRatio = window.devicePixelRatio || 1;

        canvas.width = Math.floor(width * pixelRatio);
        canvas.height = Math.floor(height * pixelRatio);

        canvas.style.width = `${width}px`;
        canvas.style.height = `${height}px`;

        /*
         * Restablecer transformación antes de aplicar el escalado.
         */
        context.setTransform(
            pixelRatio,
            0,
            0,
            pixelRatio,
            0,
            0
        );

        const columns = Math.ceil(width / config.fontSize);

        drops = Array.from(
            { length: columns },
            () => Math.floor(Math.random() * -30)
        );
    }

    function drawMatrixRain() {
        const width = canvas.clientWidth;
        const height = canvas.clientHeight;

        /*
         * El negro semitransparente produce el rastro de las letras.
         */
        context.fillStyle = "rgba(0, 0, 0, 0.12)";
        context.fillRect(0, 0, width, height);

        context.font = `bold ${config.fontSize}px monospace`;
        context.textBaseline = "top";

        drops.forEach((drop, column) => {
            const character =
                characters[
                    Math.floor(Math.random() * characters.length)
                ];

            const x = column * config.fontSize;
            const y = drop * config.fontSize;

            /*
             * Algunas letras se muestran más claras para simular
             * la cabeza luminosa de cada columna.
             */
            if (Math.random() > 0.94) {
                context.fillStyle = "#d5ffe0";
            } else {
                context.fillStyle = "#00ff55";
            }

            context.shadowColor = "#00ff55";
            context.shadowBlur = 7;

            context.fillText(character, x, y);

            context.shadowBlur = 0;

            /*
             * Cuando la columna pasa la pantalla, vuelve arriba
             * con una pequeña probabilidad para evitar uniformidad.
             */
            if (
                y > height &&
                Math.random() > 0.975
            ) {
                drops[column] = Math.floor(
                    Math.random() * -15
                );
            } else {
                drops[column]++;
            }
        });
    }

    function restoreContainer() {
        if (originalPosition === "static") {
            container.style.position = "";
        }

        container.style.overflow = originalOverflow;
    }

    function removeEffect() {
        if (overlay.isConnected) {
            overlay.remove();
        }

        restoreContainer();

        if (typeof config.onFinish === "function") {
            config.onFinish(container);
        }
    }

    function stop() {
        if (stopped) {
            return;
        }

        stopped = true;

        if (animationInterval) {
            clearInterval(animationInterval);
        }

        if (finishTimeout) {
            clearTimeout(finishTimeout);
        }

        if (removeTimeout) {
            clearTimeout(removeTimeout);
        }

        if (resizeObserver) {
            resizeObserver.disconnect();
        }

        if (fadeAudioInterval) {
            clearInterval(fadeAudioInterval);
        }

        detenerSonido();

        overlay.style.opacity = "0";

        removeTimeout = setTimeout(
            removeEffect,
            500
        );
    }

    configureCanvas();

    /*
     * Actualizar el tamaño si cambia el contenedor.
     */
    if ("ResizeObserver" in window) {
        resizeObserver = new ResizeObserver(() => {
            configureCanvas();
        });

        resizeObserver.observe(container);
    }

    animationInterval = setInterval(
        drawMatrixRain,
        config.speed
    );

    reproducirSonido();

    if (
        Number.isFinite(config.time) &&
        config.time > 0
    ) {
        finishTimeout = setTimeout(() => {
            if (config.removeOnFinish) {
                stop();
            }
        }, config.time);
    }

    return {
        stop
    };
}

/*
 * Hacer disponible la función globalmente.
 */
window.matrixRain = matrixRain;