"""Tests de los casos de uso de autenticación, con un repositorio fake en
memoria en vez de Postgres real -- ver GUIA-ARQUITECTURA-Y-CALIDAD.md,
Nivel 1, sección 1.4.
"""

import pytest

from modulos.autenticacion.aplicacion.casos_de_uso import (
    IniciarSesionUseCase,
    RegistrarUsuarioUseCase,
)
from modulos.autenticacion.dominio.errores import CredencialesInvalidasError


class RepositorioUsuarioFake:
    def __init__(self):
        self._usuarios = {}
        self._siguiente_id = 1

    def obtener_por_email(self, email):
        for usuario in self._usuarios.values():
            if usuario.email == email:
                return usuario
        return None

    def obtener_por_id(self, id):
        return self._usuarios.get(id)

    def guardar(self, usuario):
        if usuario.id is None:
            usuario.id = self._siguiente_id
            self._siguiente_id += 1
        self._usuarios[usuario.id] = usuario
        return usuario


def test_registrar_usuario_lo_persiste_con_id_asignado():
    repositorio = RepositorioUsuarioFake()
    caso_de_uso = RegistrarUsuarioUseCase(repositorio)

    usuario = caso_de_uso.ejecutar("ana@mail.com", "clave1234")

    assert usuario.id is not None
    assert repositorio.obtener_por_email("ana@mail.com") is usuario


def test_iniciar_sesion_con_credenciales_correctas_devuelve_token():
    repositorio = RepositorioUsuarioFake()
    RegistrarUsuarioUseCase(repositorio).ejecutar("ana@mail.com", "clave1234")
    caso_de_uso = IniciarSesionUseCase(
        repositorio, emisor_de_tokens=lambda usuario_id: f"token-{usuario_id}"
    )

    usuario, token = caso_de_uso.ejecutar("ana@mail.com", "clave1234")

    assert token == f"token-{usuario.id}"


def test_iniciar_sesion_con_password_incorrecta_lanza_credenciales_invalidas():
    repositorio = RepositorioUsuarioFake()
    RegistrarUsuarioUseCase(repositorio).ejecutar("ana@mail.com", "clave1234")
    caso_de_uso = IniciarSesionUseCase(repositorio, emisor_de_tokens=lambda usuario_id: "token")

    with pytest.raises(CredencialesInvalidasError):
        caso_de_uso.ejecutar("ana@mail.com", "clave-incorrecta")


def test_iniciar_sesion_con_email_inexistente_lanza_credenciales_invalidas():
    repositorio = RepositorioUsuarioFake()
    caso_de_uso = IniciarSesionUseCase(repositorio, emisor_de_tokens=lambda usuario_id: "token")

    with pytest.raises(CredencialesInvalidasError):
        caso_de_uso.ejecutar("no-existe@mail.com", "clave1234")
