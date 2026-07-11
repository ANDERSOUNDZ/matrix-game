"""Adaptador de entrada HTTP del módulo `celebracion`.

Usa el puerto compartido `VerificadorDeSesion` (guardado en
`app.config["VERIFICADOR_DE_SESION"]` por compartido/app.py) para saber
quién es el usuario -- este módulo nunca importa `autenticacion`
directamente.
"""

import base64

from flask import Blueprint, current_app, jsonify, request, send_from_directory

from modulos.celebracion.adaptadores.salida.almacenamiento_disco import (
    CARPETA_FOTOS,
    AlmacenDeFotosDisco,
)
from modulos.celebracion.aplicacion.casos_de_uso import GuardarFotoUseCase

celebracion_bp = Blueprint("celebracion", __name__, url_prefix="/celebracion")

_guardar_foto_use_case = GuardarFotoUseCase(AlmacenDeFotosDisco())


@celebracion_bp.get("/salud")
def salud():
    """Endpoint de humo: confirma que el módulo está enchufado a la app."""
    return jsonify(modulo="celebracion", ok=True)


def _usuario_id_autenticado():
    verificador = current_app.config.get("VERIFICADOR_DE_SESION")
    if verificador is None:
        return None
    auth = request.headers.get("Authorization", "")
    token = auth[7:] if auth.startswith("Bearer ") else None
    usuario_id = verificador.usuario_id_desde_token(token)
    return int(usuario_id) if usuario_id is not None else None


@celebracion_bp.post("/foto")
def subir_foto():
    usuario_id = _usuario_id_autenticado()
    if usuario_id is None:
        return jsonify(ok=False, error="no autenticado"), 401

    datos = request.get_json(silent=True) or {}
    imagen_base64 = datos.get("imagen", "")
    if imagen_base64.startswith("data:"):
        imagen_base64 = imagen_base64.split(",", 1)[1]

    try:
        datos_imagen = base64.b64decode(imagen_base64)
    except (ValueError, TypeError):
        return jsonify(ok=False, error="imagen inválida"), 400

    if not datos_imagen:
        return jsonify(ok=False, error="imagen inválida"), 400

    url = _guardar_foto_use_case.ejecutar(usuario_id, datos_imagen)
    return jsonify(ok=True, url=url)


@celebracion_bp.get("/fotos/<path:nombre_archivo>")
def obtener_foto(nombre_archivo):
    return send_from_directory(CARPETA_FOTOS, nombre_archivo)
