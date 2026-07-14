"""Adaptador de salida: partidas activas en memoria, una por conexion.

Se indexa por conexion (el sid de Socket.IO), no por usuario: si la misma
cuenta tiene dos conexiones activas a la vez (dos pestañas, dos
computadoras), cada una necesita su propio laberinto e hilo de enemigo
independientes -- indexar por usuario_id hacia que ambas conexiones
terminaran compartiendo la misma Partida (la segunda pisaba el estado de la
primera en el repositorio, y los dos hilos de tick del enemigo quedaban
moviendo el mismo objeto).

Alcanza para esta etapa (un jugador por partida, ver ADR 0002). Cuando se
agregue sincronización multijugador real, es probable que esto pase a un
almacén compartido entre conexiones (o Redis si hay más de una instancia
de backend -- ver ADR 0001).
"""

from modulos.laberinto.dominio.partida import Partida


class PartidaRepositoryEnMemoria:
    def __init__(self):
        self._partidas_por_conexion = {}

    def obtener_por_conexion(self, conexion_id):
        return self._partidas_por_conexion.get(conexion_id)

    def guardar(self, partida: Partida) -> None:
        self._partidas_por_conexion[partida.id] = partida

    def eliminar(self, conexion_id) -> None:
        self._partidas_por_conexion.pop(conexion_id, None)
