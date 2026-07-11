"""Casos de uso del módulo autenticación.

Ver GUIA-ARQUITECTURA-Y-CALIDAD.md, Nivel 1, sección 1.3. `emisor_de_tokens`
se recibe inyectado (una función `usuario_id -> token`) en vez de importarse
directamente, para no acoplar el caso de uso a un adaptador concreto.
"""

from modulos.autenticacion.dominio.errores import CredencialesInvalidasError
from modulos.autenticacion.dominio.usuario import Usuario


class RegistrarUsuarioUseCase:
    def __init__(self, repositorio):
        self._repositorio = repositorio

    def ejecutar(self, email, password, nombre):
        usuario = Usuario.registrar(email, password, nombre)
        return self._repositorio.guardar(usuario)  # puede lanzar EmailYaRegistradoError


class IniciarSesionUseCase:
    def __init__(self, repositorio, emisor_de_tokens):
        self._repositorio = repositorio
        self._emisor_de_tokens = emisor_de_tokens

    def ejecutar(self, email, password):
        usuario = self._repositorio.obtener_por_email(email)
        if usuario is None:
            raise CredencialesInvalidasError()
        usuario.verificar_password(password)  # lanza CredencialesInvalidasError si no coincide
        token = self._emisor_de_tokens(usuario.id)
        return usuario, token
