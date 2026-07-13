"""Socket.IO de Matrix Vision para la pantalla de celebración."""

import base64
import logging

from flask import request, session
from flask_socketio import Namespace, disconnect

from modulos.celebracion.adaptadores.salida.procesador_matrix_mediapipe import (
    ProcesadorMatrixMediaPipe,
)
from modulos.celebracion.aplicacion.servicio_matrix import ProcesarFrameMatrixUseCase

logger = logging.getLogger(__name__)

_procesador = ProcesadorMatrixMediaPipe()
_procesar_frame = ProcesarFrameMatrixUseCase(_procesador)


class CelebracionMatrixNamespace(Namespace):
    def __init__(self, namespace, verificador_de_sesion):
        super().__init__(namespace)
        self._verificador_de_sesion = verificador_de_sesion

    def on_connect(self, auth):
        token = (auth or {}).get("token")
        usuario_id = self._verificador_de_sesion.usuario_id_desde_token(token)
        if usuario_id is None:
            disconnect()
            return
        session["usuario_id"] = int(usuario_id)
        self.emit("matrix_estado", {"ok": True, "mensaje": "procesador conectado"})

    def on_matrix_frame(self, datos):
        if session.get("usuario_id") is None:
            disconnect()
            return

        try:
            # Socket.IO puede entregar ArrayBuffer como bytes o una lista de enteros.
            if isinstance(datos, bytes):
                frame = datos
            elif isinstance(datos, bytearray):
                frame = bytes(datos)
            elif isinstance(datos, list):
                frame = bytes(datos)
            elif isinstance(datos, dict) and datos.get("imagen"):
                valor = datos["imagen"]
                if isinstance(valor, str) and "," in valor:
                    valor = valor.split(",", 1)[1]
                frame = base64.b64decode(valor)
            else:
                raise ValueError("formato de frame no soportado")

            resultado = _procesar_frame.ejecutar(frame)
            # Flask-SocketIO transmite bytes como binario real.
            self.emit("matrix_resultado", resultado)
        except Exception as error:
            logger.exception("Error procesando frame Matrix")
            self.emit("matrix_error", {"error": str(error)})


def registrar_namespace_celebracion_matrix(socketio, verificador_de_sesion) -> None:
    socketio.on_namespace(
        CelebracionMatrixNamespace("/celebracion-matrix", verificador_de_sesion)
    )
