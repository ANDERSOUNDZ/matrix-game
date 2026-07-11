// Utilidades compartidas entre las páginas del frontend -- el equivalente,
// del lado del cliente, de backend/compartido/. Cambios acá se coordinan
// entre los 3 devs, mismo criterio que compartido/ en el backend.

// En local, backend y frontend comparten host y solo difieren en el puerto
// (:5000) -- se detecta solo. En producción (Railway u otro hosting) son
// dominios distintos, así que se usa la URL configurada en config.js (debe
// cargarse ANTES que este archivo en cada página).
const API_BASE = window.MATRIX_GAME_BACKEND_URL || `${location.protocol}//${location.hostname}:5000`;

function obtenerSesion() {
  const crudo = localStorage.getItem("matrix_game_sesion");
  return crudo ? JSON.parse(crudo) : null;
}

function guardarSesion(sesion) {
  localStorage.setItem("matrix_game_sesion", JSON.stringify(sesion));
}

function borrarSesion() {
  localStorage.removeItem("matrix_game_sesion");
}
