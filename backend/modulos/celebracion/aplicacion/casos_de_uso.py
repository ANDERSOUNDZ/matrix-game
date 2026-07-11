"""Casos de uso del módulo `celebracion`.

`registrar_suscriptores()` conecta este módulo al bus de eventos
compartido -- funcional desde el cascarón inicial. `GuardarFotoUseCase` es
la implementación real: guarda la imagen vía el puerto `AlmacenDeFotos` e
inserta la fila en `celebracion.fotos_compartidas` (tabla creada por la
migración 0001).
"""

import logging

from sqlalchemy import text

from compartido.db import engine
from compartido.event_bus import event_bus
from compartido.eventos import PartidaGanada

logger = logging.getLogger(__name__)


def _al_ganar_partida(evento: PartidaGanada) -> None:
    # El dominio/aplicación de este módulo reacciona al hecho de que
    # alguien ganó; el frontend, al recibir "ganaste" del namespace de
    # laberinto, ya redirige a la pantalla de celebración por su cuenta.
    logger.info(
        "celebracion: partida %s ganada por usuario %s en %.1fs",
        evento.partida_id,
        evento.usuario_id,
        evento.tiempo_segundos,
    )


def registrar_suscriptores() -> None:
    """Se llama una única vez al arrancar la app (ver compartido/app.py)."""
    event_bus.suscribirse(PartidaGanada, _al_ganar_partida)


class GuardarFotoUseCase:
    def __init__(self, almacen_de_fotos):
        self._almacen_de_fotos = almacen_de_fotos

    def ejecutar(self, usuario_id, datos_imagen, extension="png"):
        url = self._almacen_de_fotos.guardar(usuario_id, datos_imagen, extension)
        with engine.begin() as conexion:
            conexion.execute(
                text(
                    "INSERT INTO celebracion.fotos_compartidas (usuario_id, url) "
                    "VALUES (:usuario_id, :url)"
                ),
                {"usuario_id": usuario_id, "url": url},
            )
        return url
