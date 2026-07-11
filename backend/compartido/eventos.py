"""Contratos de eventos compartidos entre modulos (ver
GUIA-ARQUITECTURA-Y-CALIDAD.md, Nivel 3: publicacion/suscripcion).

Cualquier cambio a este archivo (agregar un campo, cambiar un tipo) afecta a
todo el que publique o escuche estos eventos -- se acuerda entre los 3
desarrolladores antes de mergear, no se cambia por sorpresa.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class PartidaGanada:
    """Publicado por el modulo `laberinto` cuando un jugador gana una partida.

    El modulo `celebracion` esta suscripto a este evento (ver
    modulos/celebracion/aplicacion/casos_de_uso.py) y reacciona sin que
    `laberinto` sepa que `celebracion` existe.
    """

    partida_id: str
    usuario_id: str
    tiempo_segundos: float
    ocurrido_en: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class PartidaPerdida:
    """Publicado por el modulo `laberinto` cuando el enemigo atrapa al
    jugador (game over). Por ahora ningun otro modulo esta suscripto -- se
    publica igual, siguiendo el mismo patron que `PartidaGanada`, por si en
    el futuro algo (por ejemplo, estadisticas) necesita reaccionar.
    """

    partida_id: str
    usuario_id: str
    ocurrido_en: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
