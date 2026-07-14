"""Puerto de salida: mejor tiempo por jugador para la tabla de posiciones.

Distinto de `PartidaRepository` (estado de una partida EN CURSO, en
memoria): esto es historico, un registro por usuario que sobrevive a la
partida y al reinicio del proceso, asi que vive en Postgres.
"""

from typing import Protocol


class PuntajeRepository(Protocol):
    def guardar_si_es_mejor(self, usuario_id, tiempo_segundos: float) -> None:
        """Guarda tiempo_segundos como el mejor tiempo de usuario_id, salvo
        que ya tenga uno mejor (mas bajo) registrado."""
        ...

    def mejores(self, limite: int) -> list:
        """Los `limite` mejores tiempos, ordenados de mas rapido a mas lento.
        Devuelve una lista de tuplas (usuario_id, tiempo_segundos)."""
        ...
