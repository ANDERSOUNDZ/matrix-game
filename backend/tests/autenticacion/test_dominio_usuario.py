"""Tests unitarios de la entidad de dominio Usuario (sin Flask ni Postgres)."""

import pytest

from modulos.autenticacion.dominio.errores import CredencialesInvalidasError
from modulos.autenticacion.dominio.usuario import Usuario


def test_registrar_hashea_la_password_en_vez_de_guardarla_en_claro():
    usuario = Usuario.registrar("ana@mail.com", "clave1234")
    assert usuario.password_hash != "clave1234"


def test_verificar_password_correcta_no_lanza_error():
    usuario = Usuario.registrar("ana@mail.com", "clave1234")
    usuario.verificar_password("clave1234")  # no debe lanzar


def test_verificar_password_incorrecta_lanza_credenciales_invalidas():
    usuario = Usuario.registrar("ana@mail.com", "clave1234")
    with pytest.raises(CredencialesInvalidasError):
        usuario.verificar_password("otra-clave")
