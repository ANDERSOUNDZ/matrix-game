"""Test de humo del módulo laberinto: confirma que el namespace de
Socket.IO valida el JWT (vía un fake que cumple el puerto compartido
`VerificadorDeSesion`) y responde, sin necesitar Postgres ni el módulo
autenticación real.
"""

from flask import Flask
from flask_socketio import SocketIO

from modulos.laberinto.adaptadores.entrada.websocket import registrar_namespace_laberinto


class VerificadorDeSesionFake:
    """Cumple compartido.puertos.VerificadorDeSesion sin depender de JWT real."""

    def usuario_id_desde_token(self, token):
        return "usuario-de-prueba" if token == "token-valido" else None


def _crear_app_y_socketio():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "solo-para-tests"
    socketio = SocketIO(app)
    registrar_namespace_laberinto(socketio, VerificadorDeSesionFake())
    return app, socketio


def test_namespace_emite_estado_al_conectar_con_token_valido():
    app, socketio = _crear_app_y_socketio()

    cliente = socketio.test_client(app, namespace="/laberinto", auth={"token": "token-valido"})
    recibidos = cliente.get_received(namespace="/laberinto")

    nombres_de_evento = [mensaje["name"] for mensaje in recibidos]
    assert "estado" in nombres_de_evento


def test_namespace_rechaza_conexion_con_token_invalido():
    app, socketio = _crear_app_y_socketio()

    cliente = socketio.test_client(app, namespace="/laberinto", auth={"token": "invalido"})

    assert cliente.is_connected(namespace="/laberinto") is False
