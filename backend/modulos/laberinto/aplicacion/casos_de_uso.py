"""Casos de uso del módulo laberinto.

`MoverJugadorUseCase` publica el evento `PartidaGanada`
(`compartido/eventos.py`) en el bus compartido cuando el movimiento
resulta en victoria -- así el módulo `celebracion` reacciona sin que este
módulo lo importe (ver GUIA-ARQUITECTURA-Y-CALIDAD.md, Nivel 3).
"""

from compartido.event_bus import event_bus
from compartido.eventos import PartidaGanada
from modulos.laberinto.dominio.partida import Partida


class CrearPartidaUseCase:
    def __init__(self, repositorio):
        self._repositorio = repositorio

    def ejecutar(self, usuario_id):
        partida = Partida(id=usuario_id, usuario_id=usuario_id)
        self._repositorio.guardar(partida)
        return partida


class MoverJugadorUseCase:
    def __init__(self, repositorio):
        self._repositorio = repositorio

    def ejecutar(self, usuario_id, direccion):
        partida = self._repositorio.obtener_por_usuario(usuario_id)
        if partida is None:
            partida = Partida(id=usuario_id, usuario_id=usuario_id)

        partida.mover(direccion)
        self._repositorio.guardar(partida)

        if partida.ganada:
            event_bus.publicar(
                PartidaGanada(
                    partida_id=str(partida.id),
                    usuario_id=str(usuario_id),
                    tiempo_segundos=partida.tiempo_segundos,
                )
            )

        return partida
