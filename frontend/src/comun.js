// Utilidades compartidas entre las páginas del frontend -- el equivalente,
// del lado del cliente, de backend/compartido/. Cambios acá se coordinan
// entre los 3 devs, mismo criterio que compartido/ en el backend.

const API_BASE = `${location.protocol}//${location.hostname}:5000`;

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
