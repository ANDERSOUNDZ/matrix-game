"""Bus de eventos in-process (ver GUIA-ARQUITECTURA-Y-CALIDAD.md, Nivel 3:
publicacion/suscripcion).

Sincrono y en memoria: alcanza para un solo proceso de backend (ver ADR
0001 en docs/decisiones/). Si en el futuro hace falta escalar a mas de una
instancia de backend, este es el lugar donde se reemplazaria la
implementacion por algo respaldado en Redis/una cola real -- el resto del
codigo no deberia notar la diferencia, porque solo conoce la interfaz
publicar()/suscribirse().
"""

from collections import defaultdict
from typing import Callable, DefaultDict, List, Type, TypeVar

E = TypeVar("E")
Suscriptor = Callable[[object], None]


class EventBus:
    def __init__(self) -> None:
        self._suscriptores: DefaultDict[type, List[Suscriptor]] = defaultdict(list)

    def suscribirse(self, tipo_evento: Type[E], manejador: Callable[[E], None]) -> None:
        self._suscriptores[tipo_evento].append(manejador)

    def publicar(self, evento: object) -> None:
        for manejador in self._suscriptores[type(evento)]:
            manejador(evento)


# Instancia unica compartida por todo el proceso de backend. Los modulos la
# usan para publicar eventos propios y suscribirse a eventos de otros --
# ver compartido/app.py, donde cada modulo registra sus suscriptores al
# arrancar la aplicacion.
event_bus = EventBus()
