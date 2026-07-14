"""Adaptador de entrada HTTP del módulo `laberinto`.

El resto del módulo se comunica por Socket.IO (ver websocket.py); esta es
la única ruta HTTP, para la tabla de posiciones -- un GET simple no
justifica el vaivén de eventos de un socket.
"""

from flask import Blueprint, jsonify, request

from modulos.laberinto.adaptadores.persistencia.postgres_puntajes import PuntajeRepositoryPostgres
from modulos.laberinto.aplicacion.casos_de_uso import ObtenerTablaDePosicionesUseCase

_repositorio_puntajes = PuntajeRepositoryPostgres()


def _usuario_autenticado(verificador_de_sesion):
    auth = request.headers.get("Authorization", "")
    token = auth[7:] if auth.startswith("Bearer ") else None
    return verificador_de_sesion.usuario_id_desde_token(token)


def crear_blueprint_laberinto(verificador_de_sesion, consulta_usuarios):
    """Recibe los puertos compartidos ya resueltos desde el composition root
    (compartido/app.py) -- este módulo nunca importa `autenticacion`
    directamente, ver compartido/puertos.py."""
    laberinto_bp = Blueprint("laberinto", __name__, url_prefix="/laberinto")
    caso_de_uso = ObtenerTablaDePosicionesUseCase(_repositorio_puntajes, consulta_usuarios)

    @laberinto_bp.get("/tabla-posiciones")
    def tabla_posiciones():
        if _usuario_autenticado(verificador_de_sesion) is None:
            return jsonify(ok=False, error="no autenticado"), 401

        return jsonify(ok=True, posiciones=caso_de_uso.ejecutar(limite=10))

    return laberinto_bp
