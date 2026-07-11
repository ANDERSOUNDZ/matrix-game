"""Adaptador de entrada HTTP del módulo `autenticacion`.

Cada ruta traduce la petición HTTP a una llamada de caso de uso; no
contiene reglas de negocio (ver GUIA-ARQUITECTURA-Y-CALIDAD.md, Nivel 1,
sección 1.3).
"""

from flask import Blueprint, jsonify, request

from modulos.autenticacion.adaptadores.entrada.jwt_sesion import JWTVerificadorDeSesion, emitir_token
from modulos.autenticacion.adaptadores.persistencia.postgres import UsuarioRepositoryPostgres
from modulos.autenticacion.aplicacion.casos_de_uso import IniciarSesionUseCase, RegistrarUsuarioUseCase
from modulos.autenticacion.dominio.errores import CredencialesInvalidasError, EmailYaRegistradoError

autenticacion_bp = Blueprint("autenticacion", __name__, url_prefix="/auth")

_repositorio = UsuarioRepositoryPostgres()
_verificador = JWTVerificadorDeSesion()

registrar_usuario_use_case = RegistrarUsuarioUseCase(_repositorio)
iniciar_sesion_use_case = IniciarSesionUseCase(_repositorio, emitir_token)


@autenticacion_bp.get("/salud")
def salud():
    """Endpoint de humo: confirma que el módulo está enchufado a la app."""
    return jsonify(modulo="autenticacion", ok=True)


@autenticacion_bp.post("/registro")
def registro():
    datos = request.get_json(silent=True) or {}
    email = (datos.get("email") or "").strip().lower()
    password = datos.get("password") or ""

    if not email or "@" not in email or len(password) < 4:
        return jsonify(ok=False, error="email o password inválidos"), 400

    try:
        usuario = registrar_usuario_use_case.ejecutar(email, password)
    except EmailYaRegistradoError:
        return jsonify(ok=False, error="ya existe una cuenta con ese email"), 409

    token = emitir_token(usuario.id)
    return jsonify(ok=True, token=token, usuario={"id": usuario.id, "email": usuario.email})


@autenticacion_bp.post("/login")
def login():
    datos = request.get_json(silent=True) or {}
    email = (datos.get("email") or "").strip().lower()
    password = datos.get("password") or ""

    try:
        usuario, token = iniciar_sesion_use_case.ejecutar(email, password)
    except CredencialesInvalidasError:
        return jsonify(ok=False, error="email o password incorrectos"), 401

    return jsonify(ok=True, token=token, usuario={"id": usuario.id, "email": usuario.email})


def _usuario_id_del_request():
    auth = request.headers.get("Authorization", "")
    token = auth[7:] if auth.startswith("Bearer ") else None
    return _verificador.usuario_id_desde_token(token)


@autenticacion_bp.get("/yo")
def yo():
    usuario_id = _usuario_id_del_request()
    if usuario_id is None:
        return jsonify(ok=False, error="no autenticado"), 401
    return jsonify(ok=True, usuario_id=usuario_id)


@autenticacion_bp.post("/logout")
def logout():
    # JWT es stateless: no hay nada que invalidar del lado del servidor en
    # esta implementación. El cliente simplemente borra el token guardado
    # (ver frontend/src/dashboard). Si más adelante hace falta poder revocar
    # tokens antes de que expiren, acá es donde se agregaría una lista negra.
    return jsonify(ok=True)
