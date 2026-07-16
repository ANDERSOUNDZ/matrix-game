// Configuración de entorno del frontend -- se carga ANTES que comun.js en
// cada página. En local no hace falta tocar nada: al quedar vacío,
// comun.js detecta automáticamente "mismo host, puerto 5000" (como hoy).
//
// En producción (Railway u otro hosting), el frontend y el backend quedan
// en dominios completamente distintos (no "mismo host, otro puerto"), así
// que hay que completar esto con la URL pública del servicio backend una
// vez creado, por ejemplo:
// En produccion (Railway), descomentar y poner la URL real:
// window.MATRIX_GAME_BACKEND_URL = "https://matrix-game-production.up.railway.app";
// En local se detecta automaticamente (mismo host, puerto 5000)
