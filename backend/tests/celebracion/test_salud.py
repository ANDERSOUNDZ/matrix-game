"""Test de humo del módulo celebración: confirma que su adaptador HTTP está
bien formado y responde, sin necesitar el resto de la app ni Postgres.
"""

from flask import Flask

from modulos.celebracion.adaptadores.entrada.http import celebracion_bp


def test_salud_responde_ok():
    app = Flask(__name__)
    app.register_blueprint(celebracion_bp)
    cliente = app.test_client()

    respuesta = cliente.get("/celebracion/salud")

    assert respuesta.status_code == 200
    assert respuesta.get_json() == {"modulo": "celebracion", "ok": True}
