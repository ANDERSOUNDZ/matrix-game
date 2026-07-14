"""Composition root (ver GUIA-ARQUITECTURA-Y-CALIDAD.md, Nivel 1, secciones
1.3 y 1.5): el UNICO lugar de todo el proyecto donde se arma la aplicacion
Flask + Socket.IO y se registran los adaptadores de entrada de los 3
modulos.

Si un modulo todavia no tiene logica de negocio implementada, la app igual
debe poder levantar sin errores -- por eso el cascaron de cada modulo ya
expone al menos un endpoint de salud (o un namespace de socket.io que
responde) antes de que nadie le agregue reglas de negocio reales.
"""

# Tiene que ser el primer import del proceso, antes que cualquier otro
# modulo (incluyendo los del proyecto) toque `socket`/`threading`: eventlet
# reemplaza esas piezas de la libreria estandar por versiones cooperativas.
# Sin esto, Flask-SocketIO cae en modo "threading" sobre el servidor de
# desarrollo de Flask, que no soporta upgrade real a WebSocket -- se veia
# como el juego conectando pero sin recibir nunca el primer estado (el
# laberinto nunca se dibujaba). Con eventlet parcheado, Flask-SocketIO usa
# async_mode="eventlet" solo y WebSocket funciona de verdad.
import eventlet

eventlet.monkey_patch()

import os  # noqa: E402

from flask import Flask, jsonify  # noqa: E402
from flask_cors import CORS  # noqa: E402
from flask_socketio import SocketIO  # noqa: E402

from modulos.autenticacion.adaptadores.entrada.http import autenticacion_bp  # noqa: E402
from modulos.autenticacion.adaptadores.entrada.jwt_sesion import JWTVerificadorDeSesion  # noqa: E402
from modulos.celebracion.adaptadores.entrada.http import celebracion_bp  # noqa: E402
from modulos.celebracion.adaptadores.entrada.websocket import (  # noqa: E402
    registrar_namespace_celebracion_matrix,
)
from modulos.celebracion.aplicacion.casos_de_uso import registrar_suscriptores  # noqa: E402
from modulos.laberinto.adaptadores.entrada.websocket import registrar_namespace_laberinto  # noqa: E402


def crear_app():
    app = Flask(__name__)
    app.config["JWT_SECRET"] = os.environ.get("JWT_SECRET", "cambiar-esto-en-produccion")
    # Necesaria para flask.session (usada por el namespace de laberinto para
    # recordar qué usuario está detrás de cada conexión de Socket.IO).
    app.config["SECRET_KEY"] = app.config["JWT_SECRET"]

    # --- Puerto compartido resuelto acá, en el composition root ---
    # (compartido/puertos.py: VerificadorDeSesion). `laberinto` y
    # `celebracion` lo reciben inyectado -- ninguno de los dos importa el
    # módulo `autenticacion` directamente.
    verificador_de_sesion = JWTVerificadorDeSesion()
    app.config["VERIFICADOR_DE_SESION"] = verificador_de_sesion

    # --- CORS ---
    # El frontend (:8090) y el backend (:5000) son orígenes distintos (ver
    # ADR 0002, decisión sobre el token JWT vía Authorization header en vez
    # de cookie). Sin esto, el navegador bloquea las peticiones del
    # frontend por la política de mismo origen, incluso si el backend
    # respondería bien. `supports_credentials=False` porque no usamos
    # cookies -- el token viaja en el header Authorization.
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=False)

    # --- Adaptadores de entrada HTTP de cada modulo ---
    app.register_blueprint(autenticacion_bp)
    app.register_blueprint(celebracion_bp)

    @app.route("/")
    def raiz():
        return jsonify(
            servicio="matrix-game-backend",
            modulos=["autenticacion", "laberinto", "celebracion"],
        )

    # --- Adaptador de entrada websocket (Socket.IO) ---
    socketio = SocketIO(app, cors_allowed_origins="*")
    registrar_namespace_laberinto(socketio, verificador_de_sesion)
    registrar_namespace_celebracion_matrix(socketio, verificador_de_sesion)

    # --- Conexion entre modulos a traves del bus de eventos compartido ---
    # Ningun modulo importa el dominio de otro directamente: `celebracion`
    # se suscribe aca a eventos que publica `laberinto` (ver
    # compartido/eventos.py y compartido/event_bus.py).
    registrar_suscriptores()

    return app, socketio


app, socketio = crear_app()


if __name__ == "__main__":
    host = os.environ.get("FLASK_HOST", "0.0.0.0")
    # Railway (y la mayoria de los hostings) inyectan PORT y esperan que la
    # app escuche ahi -- FLASK_PORT sigue siendo el default para desarrollo
    # local via .env.
    port = int(os.environ.get("PORT") or os.environ.get("FLASK_PORT", "5000"))
    print(f"\n[SERVER] Abre http://localhost:{port} en tu navegador")
    # Solo para correr el modulo suelto (`python -m compartido.app`) sin
    # gunicorn -- el Dockerfile (y por lo tanto Railway) usa gunicorn con
    # worker eventlet en su lugar. Con eventlet monkey-parcheado (import al
    # tope de este archivo), Flask-SocketIO detecta async_mode="eventlet" y
    # socketio.run() ya sirve con el servidor de eventlet en vez del de
    # desarrollo de Flask -- allow_unsafe_werkzeug queda de mas aca, pero no
    # molesta si algun dia se corre sin eventlet disponible.
    socketio.run(app, host=host, port=port, allow_unsafe_werkzeug=True)
