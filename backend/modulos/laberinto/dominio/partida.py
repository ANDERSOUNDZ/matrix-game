"""Entidad de dominio: Partida de laberinto.

Grid fijo, un jugador por partida (todavía sin sincronización multijugador
-- ver docs/decisiones/0002-flujo-conectado-de-punta-a-punta.md), reglas de
movimiento y condición de victoria como lógica pura, sin Flask-SocketIO.

Ver GUIA-ARQUITECTURA-Y-CALIDAD.md, Nivel 1, sección 1.2.
"""

import time

# 0 = camino libre, 1 = pared. Hay un camino garantizado de (0,0) a (6,6).
GRID = [
    [0, 0, 0, 1, 0, 0, 0],
    [1, 1, 0, 1, 0, 1, 0],
    [0, 0, 0, 0, 0, 1, 0],
    [0, 1, 1, 1, 0, 1, 0],
    [0, 0, 0, 1, 0, 0, 0],
    [0, 1, 0, 0, 0, 1, 0],
    [0, 1, 0, 1, 0, 0, 0],
]
FILAS = len(GRID)
COLUMNAS = len(GRID[0])
POSICION_INICIAL = (0, 0)
POSICION_META = (FILAS - 1, COLUMNAS - 1)

DELTAS = {
    "arriba": (-1, 0),
    "abajo": (1, 0),
    "izquierda": (0, -1),
    "derecha": (0, 1),
}


class Partida:
    def __init__(self, id, usuario_id):
        self.id = id
        self.usuario_id = usuario_id
        self.fila, self.columna = POSICION_INICIAL
        self.ganada = False
        self.iniciada_en = time.time()
        self.tiempo_segundos = None

    def mover(self, direccion):
        """Aplica un movimiento si es válido (dentro del grid y sin pared).

        Devuelve True si se aplicó, False si fue inválido. Chocar contra
        una pared o el borde es parte normal del juego, no un error de
        programación (ver GUIA-ARQUITECTURA-Y-CALIDAD.md, sección 0.4) --
        por eso se ignora en silencio en vez de lanzar una excepción.
        """
        if self.ganada or direccion not in DELTAS:
            return False

        dfila, dcolumna = DELTAS[direccion]
        nueva_fila, nueva_columna = self.fila + dfila, self.columna + dcolumna

        dentro_del_grid = 0 <= nueva_fila < FILAS and 0 <= nueva_columna < COLUMNAS
        if not dentro_del_grid or GRID[nueva_fila][nueva_columna] == 1:
            return False

        self.fila, self.columna = nueva_fila, nueva_columna

        if (self.fila, self.columna) == POSICION_META:
            self.ganada = True
            self.tiempo_segundos = time.time() - self.iniciada_en

        return True

    def a_dict(self):
        return {
            "grid": GRID,
            "jugador": [self.fila, self.columna],
            "meta": list(POSICION_META),
            "ganada": self.ganada,
        }
