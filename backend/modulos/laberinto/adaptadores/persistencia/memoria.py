"""Adaptador de salida: partidas activas en memoria, una por usuario.

Alcanza para esta etapa (un jugador por partida, ver ADR 0002). Cuando se
agregue sincronización multijugador real, es probable que esto pase a un
almacén compartido entre conexiones (o Redis si hay más de una instancia
de backend -- ver ADR 0001).
"""

from modulos.laberinto.dominio.partida import Partida


class PartidaRepositoryEnMemoria:
    def __init__(self):
        self._partidas_por_usuario = {}

    def obtener_por_usuario(self, usuario_id):
        return self._partidas_por_usuario.get(usuario_id)

    def guardar(self, partida: Partida) -> None:
        self._partidas_por_usuario[partida.usuario_id] = partida
