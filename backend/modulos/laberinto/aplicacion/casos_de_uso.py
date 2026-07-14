"""Casos de uso del módulo laberinto.

`MoverJugadorUseCase` y `MoverEnemigoUseCase` publican los eventos
`PartidaGanada`/`PartidaPerdida` (`compartido/eventos.py`) en el bus
compartido cuando corresponde -- así el módulo `celebracion` (u otro futuro
suscriptor) reacciona sin que este módulo lo importe (ver
GUIA-ARQUITECTURA-Y-CALIDAD.md, Nivel 3).
"""

from compartido.event_bus import event_bus
from compartido.eventos import PartidaGanada, PartidaPerdida
from modulos.laberinto.dominio.partida import Partida


class CrearPartidaUseCase:
    def __init__(self, repositorio):
        self._repositorio = repositorio

    def ejecutar(self, conexion_id, usuario_id):
        partida = Partida(id=conexion_id, usuario_id=usuario_id)
        self._repositorio.guardar(partida)
        return partida


class MoverJugadorUseCase:
    def __init__(self, repositorio):
        self._repositorio = repositorio

    def ejecutar(self, conexion_id, usuario_id, direccion):
        partida = self._repositorio.obtener_por_conexion(conexion_id)
        if partida is None:
            partida = Partida(id=conexion_id, usuario_id=usuario_id)

        partida.mover(direccion)
        self._repositorio.guardar(partida)
        self._publicar_resultado_si_termino(partida, usuario_id)
        return partida

    def _publicar_resultado_si_termino(self, partida, usuario_id):
        if partida.ganada:
            event_bus.publicar(
                PartidaGanada(
                    partida_id=str(partida.id),
                    usuario_id=str(usuario_id),
                    tiempo_segundos=partida.tiempo_segundos,
                )
            )
        elif partida.perdida:
            event_bus.publicar(
                PartidaPerdida(partida_id=str(partida.id), usuario_id=str(usuario_id))
            )


class MoverEnemigoUseCase:
    """Un paso de persecución del enemigo -- lo llama el tick de fondo del
    adaptador de entrada websocket, no el jugador (ver
    adaptadores/entrada/websocket.py)."""

    def __init__(self, repositorio):
        self._repositorio = repositorio

    def ejecutar(self, conexion_id):
        partida = self._repositorio.obtener_por_conexion(conexion_id)
        if partida is None:
            return None

        partida.mover_enemigo()
        self._repositorio.guardar(partida)

        if partida.perdida:
            event_bus.publicar(
                PartidaPerdida(partida_id=str(partida.id), usuario_id=str(partida.usuario_id))
            )

        return partida
