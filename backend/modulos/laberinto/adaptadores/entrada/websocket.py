"""Adaptador de entrada websocket del módulo `laberinto`.

Valida el JWT recibido al conectar usando el puerto compartido
`VerificadorDeSesion` (inyectado desde compartido/app.py) -- este módulo
nunca importa el módulo `autenticacion`, solo recibe algo que cumple ese
puerto. Ver GUIA-ARQUITECTURA-Y-CALIDAD.md, Nivel 1, secciones 1.3 y 1.5.

El enemigo se mueve solo, en tiempo real: un hilo de fondo por conexión
(uno por partida activa) llama a `MoverEnemigoUseCase` cada
`INTERVALO_ENEMIGO_SEGUNDOS` y emite el estado actualizado -- ver
`docs/decisiones/0003-laberinto-3d-con-enemigo.md`.

Usa `flask.session` para guardar el usuario autenticado durante la
duración de la conexión de Socket.IO (comportamiento documentado de
Flask-SocketIO: la sesión se mantiene por conexión, no requiere cookie).
"""

from flask import request, session
from flask_socketio import Namespace, disconnect

from modulos.laberinto.adaptadores.persistencia.memoria import PartidaRepositoryEnMemoria
from modulos.laberinto.aplicacion.casos_de_uso import (
    CrearPartidaUseCase,
    MoverEnemigoUseCase,
    MoverJugadorUseCase,
)

_repositorio = PartidaRepositoryEnMemoria()
_crear_partida_use_case = CrearPartidaUseCase(_repositorio)
_mover_jugador_use_case = MoverJugadorUseCase(_repositorio)
_mover_enemigo_use_case = MoverEnemigoUseCase(_repositorio)

INTERVALO_ENEMIGO_SEGUNDOS = 1.1

# sid -> True mientras el tick del enemigo de esa conexion deba seguir
# corriendo. Se pone en False para detenerlo (desconexion, victoria o
# derrota) en vez de intentar matar el hilo a la fuerza -- ver
# GUIA-ARQUITECTURA-Y-CALIDAD.md, seccion 2.3, sobre por que "dejar de
# insistir" es preferible a forzar la baja de un recurso en uso.
_conexiones_activas = {}


class LaberintoNamespace(Namespace):
    def __init__(self, namespace, verificador_de_sesion, socketio):
        super().__init__(namespace)
        self._verificador_de_sesion = verificador_de_sesion
        self._socketio = socketio

    def on_connect(self, auth):
        token = (auth or {}).get("token")
        usuario_id = self._verificador_de_sesion.usuario_id_desde_token(token)
        if usuario_id is None:
            disconnect()
            return

        sid = request.sid
        session["usuario_id"] = usuario_id

        partida = _crear_partida_use_case.ejecutar(usuario_id)
        self.emit("estado", partida.a_dict())

        _conexiones_activas[sid] = True
        self._socketio.start_background_task(self._tick_enemigo, sid, usuario_id)

    def _tick_enemigo(self, sid, usuario_id):
        """Corre en un hilo de fondo (uno por conexion). No tiene contexto
        de request, por eso usa `socketio.emit(..., to=sid)` en vez de
        `self.emit(...)` -- ver GUIA-ARQUITECTURA-Y-CALIDAD.md, seccion 2.5,
        sobre separar la infraestructura de resiliencia/temporizacion del
        resto del codigo."""
        while _conexiones_activas.get(sid):
            self._socketio.sleep(INTERVALO_ENEMIGO_SEGUNDOS)
            if not _conexiones_activas.get(sid):
                break

            partida = _mover_enemigo_use_case.ejecutar(usuario_id)
            if partida is None:
                break

            self._socketio.emit("estado", partida.a_dict(), to=sid, namespace=self.namespace)

            if partida.perdida:
                self._socketio.emit("perdiste", {}, to=sid, namespace=self.namespace)
                _conexiones_activas[sid] = False
            elif partida.ganada:
                # ya se avisó "ganaste" desde on_mover; el enemigo deja de perseguir
                _conexiones_activas[sid] = False

    def on_mover(self, datos):
        usuario_id = session.get("usuario_id")
        if usuario_id is None:
            return

        direccion = (datos or {}).get("direccion")
        partida = _mover_jugador_use_case.ejecutar(usuario_id, direccion)
        self.emit("estado", partida.a_dict())

        if partida.ganada:
            self.emit("ganaste", {"tiempo_segundos": partida.tiempo_segundos})
            _conexiones_activas[request.sid] = False
        elif partida.perdida:
            self.emit("perdiste", {})
            _conexiones_activas[request.sid] = False

    def on_disconnect(self):
        _conexiones_activas.pop(request.sid, None)


def registrar_namespace_laberinto(socketio, verificador_de_sesion) -> None:
    """Se llama una vez al arrancar la app (ver compartido/app.py)."""
    socketio.on_namespace(LaberintoNamespace("/laberinto", verificador_de_sesion, socketio))
