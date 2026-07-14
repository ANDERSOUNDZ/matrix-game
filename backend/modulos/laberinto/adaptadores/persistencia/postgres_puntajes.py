"""Adaptador de salida: implementa PuntajeRepository contra Postgres
(esquema `laberinto`, tabla `puntajes`, creada por la migración 0002).
"""

from sqlalchemy import text

from compartido.db import engine


class PuntajeRepositoryPostgres:
    def guardar_si_es_mejor(self, usuario_id, tiempo_segundos: float) -> None:
        with engine.begin() as conexion:
            conexion.execute(
                text(
                    "INSERT INTO laberinto.puntajes (usuario_id, mejor_tiempo_segundos) "
                    "VALUES (:usuario_id, :tiempo) "
                    "ON CONFLICT (usuario_id) DO UPDATE "
                    "SET mejor_tiempo_segundos = EXCLUDED.mejor_tiempo_segundos, "
                    "    actualizado_en = now() "
                    "WHERE laberinto.puntajes.mejor_tiempo_segundos > EXCLUDED.mejor_tiempo_segundos"
                ),
                {"usuario_id": str(usuario_id), "tiempo": tiempo_segundos},
            )

    def mejores(self, limite: int) -> list:
        with engine.connect() as conexion:
            filas = conexion.execute(
                text(
                    "SELECT usuario_id, mejor_tiempo_segundos FROM laberinto.puntajes "
                    "ORDER BY mejor_tiempo_segundos ASC LIMIT :limite"
                ),
                {"limite": limite},
            ).fetchall()
        return [(fila.usuario_id, fila.mejor_tiempo_segundos) for fila in filas]
