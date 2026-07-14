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

    primer_estado = next(m["args"][0] for m in recibidos if m["name"] == "estado")
    assert "paredes" in primer_estado
    assert "enemigo" in primer_estado
    assert primer_estado["jugador"] != primer_estado["enemigo"]

    # Detiene el hilo de fondo del tick del enemigo (ver on_disconnect en
    # websocket.py) para no dejarlo corriendo entre tests.
    cliente.disconnect(namespace="/laberinto")


def test_namespace_rechaza_conexion_con_token_invalido():
    app, socketio = _crear_app_y_socketio()

    cliente = socketio.test_client(app, namespace="/laberinto", auth={"token": "invalido"})

    assert cliente.is_connected(namespace="/laberinto") is False


def test_mover_no_transmite_el_estado_a_otras_conexiones():
    """Regresion: self.emit() en una clase Namespace de Flask-SocketIO NO
    manda solo al que disparo el evento por defecto -- sin `to=sid` explicito
    se transmite a TODOS los conectados al namespace. Con dos conexiones (aca
    la misma cuenta, pero aplica igual a cuentas distintas) activas a la vez,
    el jugador de una veia su pantalla sobreescrita con el estado de la otra
    cada vez que esa otra se movia. Ver adaptadores/entrada/websocket.py.
    """
    app, socketio = _crear_app_y_socketio()

    cliente_a = socketio.test_client(app, namespace="/laberinto", auth={"token": "token-valido"})
    cliente_b = socketio.test_client(app, namespace="/laberinto", auth={"token": "token-valido"})
    # descarta el "estado" inicial que cada uno recibe al conectar
    cliente_a.get_received(namespace="/laberinto")
    cliente_b.get_received(namespace="/laberinto")

    cliente_a.emit("mover", {"direccion": "abajo"}, namespace="/laberinto")

    recibidos_a = cliente_a.get_received(namespace="/laberinto")
    recibidos_b = cliente_b.get_received(namespace="/laberinto")

    assert any(m["name"] == "estado" for m in recibidos_a)
    assert recibidos_b == []

    cliente_a.disconnect(namespace="/laberinto")
    cliente_b.disconnect(namespace="/laberinto")
