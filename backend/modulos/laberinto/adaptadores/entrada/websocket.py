"""Adaptador de entrada websocket del módulo `laberinto`.

Valida el JWT recibido al conectar usando el puerto compartido
`VerificadorDeSesion` (inyectado desde compartido/app.py) -- este módulo
nunca importa el módulo `autenticacion`, solo recibe algo que cumple ese
puerto. Ver GUIA-ARQUITECTURA-Y-CALIDAD.md, Nivel 1, secciones 1.3 y 1.5.

Usa `flask.session` para guardar el usuario autenticado durante la
duración de la conexión de Socket.IO (comportamiento documentado de
Flask-SocketIO: la sesión se mantiene por conexión, no requiere cookie).
"""

from flask import session
from flask_socketio import Namespace, disconnect

from modulos.laberinto.adaptadores.persistencia.memoria import PartidaRepositoryEnMemoria
from modulos.laberinto.aplicacion.casos_de_uso import CrearPartidaUseCase, MoverJugadorUseCase

_repositorio = PartidaRepositoryEnMemoria()
_crear_partida_use_case = CrearPartidaUseCase(_repositorio)
_mover_jugador_use_case = MoverJugadorUseCase(_repositorio)


class LaberintoNamespace(Namespace):
    def __init__(self, namespace, verificador_de_sesion):
        super().__init__(namespace)
        self._verificador_de_sesion = verificador_de_sesion

    def on_connect(self, auth):
        token = (auth or {}).get("token")
        usuario_id = self._verificador_de_sesion.usuario_id_desde_token(token)
        if usuario_id is None:
            disconnect()
            return

        session["usuario_id"] = usuario_id
        partida = _crear_partida_use_case.ejecutar(usuario_id)
        self.emit("estado", partida.a_dict())

    def on_mover(self, datos):
        usuario_id = session.get("usuario_id")
        if usuario_id is None:
            return

        direccion = (datos or {}).get("direccion")
        partida = _mover_jugador_use_case.ejecutar(usuario_id, direccion)
        self.emit("estado", partida.a_dict())
        if partida.ganada:
            self.emit("ganaste", {"tiempo_segundos": partida.tiempo_segundos})

    def on_disconnect(self):
        pass


def registrar_namespace_laberinto(socketio, verificador_de_sesion) -> None:
    """Se llama una vez al arrancar la app (ver compartido/app.py)."""
    socketio.on_namespace(LaberintoNamespace("/laberinto", verificador_de_sesion))
