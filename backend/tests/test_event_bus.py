"""Prueba que el bus de eventos compartido conecta módulos sin que se
importen el dominio entre sí (ver GUIA-ARQUITECTURA-Y-CALIDAD.md, Nivel 3:
publicación/suscripción).

No levanta Flask, no abre Postgres, no necesita Docker: corre en
milisegundos, como cualquier test unitario.
"""

import logging

from compartido.event_bus import EventBus, event_bus
from compartido.eventos import PartidaGanada


def test_un_suscriptor_recibe_el_evento_publicado():
    bus = EventBus()
    recibidos = []

    bus.suscribirse(PartidaGanada, recibidos.append)

    evento = PartidaGanada(partida_id="1", usuario_id="42", tiempo_segundos=12.5)
    bus.publicar(evento)

    assert recibidos == [evento]


def test_publicar_sin_suscriptores_no_lanza_error():
    bus = EventBus()
    bus.publicar(PartidaGanada(partida_id="1", usuario_id="42", tiempo_segundos=1.0))


def test_celebracion_reacciona_a_partida_ganada_sin_importar_laberinto(caplog):
    """Prueba de integración mínima entre módulos: usa el módulo real
    `celebracion`, publicando en la instancia real `event_bus` (la misma
    que usa compartido/app.py), y confirma que reacciona -- sin que este
    test, ni el módulo celebración, importen nada del módulo laberinto."""
    from modulos.celebracion.aplicacion.casos_de_uso import registrar_suscriptores

    registrar_suscriptores()

    with caplog.at_level(logging.INFO):
        event_bus.publicar(
            PartidaGanada(partida_id="99", usuario_id="7", tiempo_segundos=42.0)
        )

    assert any("partida 99" in mensaje for mensaje in caplog.messages)
