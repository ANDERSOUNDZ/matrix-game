"""Test de humo del módulo autenticación: confirma que su adaptador HTTP
está bien formado y responde, sin necesitar el resto de la app ni Postgres.
"""

from flask import Flask

from modulos.autenticacion.adaptadores.entrada.http import autenticacion_bp


def test_salud_responde_ok():
    app = Flask(__name__)
    app.register_blueprint(autenticacion_bp)
    cliente = app.test_client()

    respuesta = cliente.get("/auth/salud")

    assert respuesta.status_code == 200
    assert respuesta.get_json() == {"modulo": "autenticacion", "ok": True}
