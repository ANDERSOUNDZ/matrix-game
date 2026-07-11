"""Entidad de dominio: Partida de laberinto.

Laberinto generado proceduralmente (recursive backtracking, un algoritmo
genérico de dominio público) con un enemigo que persigue al jugador por el
camino más corto real (BFS) -- ver GUIA-ARQUITECTURA-Y-CALIDAD.md, Nivel 1,
sección 1.2, y `docs/decisiones/0003-laberinto-3d-con-enemigo.md`.

Cada celda tiene sus 4 paredes propias (arriba/abajo/izquierda/derecha), en
vez de un grid de celdas "pared" enteras -- es el modelo estándar para
generar laberintos y es lo que necesita el renderizado 3D del frontend (por
celda, se sabe exactamente qué paredes dibujar).
"""

import random
import time
from collections import deque

FILAS_POR_DEFECTO = 10
COLUMNAS_POR_DEFECTO = 10
POSICION_INICIAL = (0, 0)

DELTAS = {
    "arriba": (-1, 0),
    "abajo": (1, 0),
    "izquierda": (0, -1),
    "derecha": (0, 1),
}
OPUESTA = {"arriba": "abajo", "abajo": "arriba", "izquierda": "derecha", "derecha": "izquierda"}


def generar_laberinto(filas, columnas, generador_aleatorio=None):
    """Genera un laberinto "perfecto" (existe exactamente un camino entre
    dos celdas cualquiera) con el algoritmo de recursive backtracking:
    arranca con todas las paredes puestas y va "tumbando" la pared hacia
    una celda vecina sin visitar, elegida al azar, hasta recorrer todo el
    grid.
    """
    generador_aleatorio = generador_aleatorio or random
    paredes = [
        [
            {"arriba": True, "abajo": True, "izquierda": True, "derecha": True}
            for _ in range(columnas)
        ]
        for _ in range(filas)
    ]
    visitado = [[False] * columnas for _ in range(filas)]

    def vecinos_sin_visitar(fila, columna):
        opciones = []
        for direccion, (df, dc) in DELTAS.items():
            nf, nc = fila + df, columna + dc
            if 0 <= nf < filas and 0 <= nc < columnas and not visitado[nf][nc]:
                opciones.append((direccion, nf, nc))
        return opciones

    pila = [POSICION_INICIAL]
    visitado[0][0] = True

    while pila:
        fila, columna = pila[-1]
        opciones = vecinos_sin_visitar(fila, columna)
        if not opciones:
            pila.pop()
            continue
        direccion, nf, nc = generador_aleatorio.choice(opciones)
        paredes[fila][columna][direccion] = False
        paredes[nf][nc][OPUESTA[direccion]] = False
        visitado[nf][nc] = True
        pila.append((nf, nc))

    return paredes


def _bfs_distancias(paredes, origen):
    distancias = {origen: 0}
    cola = deque([origen])
    while cola:
        actual = cola.popleft()
        fila, columna = actual
        for direccion, (df, dc) in DELTAS.items():
            if paredes[fila][columna][direccion]:
                continue  # hay pared, no se puede pasar
            vecino = (fila + df, columna + dc)
            if vecino not in distancias:
                distancias[vecino] = distancias[actual] + 1
                cola.append(vecino)
    return distancias


def _celda_mas_lejana(paredes, origen):
    """Celda con mayor distancia (en pasos) desde origen -- se usa para
    ubicar al enemigo lo más lejos posible del jugador al empezar."""
    distancias = _bfs_distancias(paredes, origen)
    return max(distancias, key=distancias.get)


def _siguiente_paso_bfs(paredes, origen, destino):
    """Primera celda del camino más corto de origen a destino, o None si ya
    están en la misma celda. En un laberinto perfecto (sin ciclos) siempre
    existe un único camino entre dos celdas cualquiera."""
    if origen == destino:
        return None

    padres = {origen: None}
    cola = deque([origen])
    while cola:
        actual = cola.popleft()
        if actual == destino:
            break
        fila, columna = actual
        for direccion, (df, dc) in DELTAS.items():
            if paredes[fila][columna][direccion]:
                continue
            vecino = (fila + df, columna + dc)
            if vecino not in padres:
                padres[vecino] = actual
                cola.append(vecino)

    if destino not in padres:
        return None  # no debería pasar en un laberinto perfecto conexo

    camino = []
    paso = destino
    while paso is not None:
        camino.append(paso)
        paso = padres[paso]
    camino.reverse()  # camino[0] == origen, camino[-1] == destino

    return camino[1] if len(camino) > 1 else None


class Partida:
    """Estado y reglas de negocio de una partida de laberinto: el grid con
    paredes, la posición del jugador, la del enemigo, y la de la meta."""

    def __init__(
        self,
        id,
        usuario_id,
        filas=FILAS_POR_DEFECTO,
        columnas=COLUMNAS_POR_DEFECTO,
        generador_aleatorio=None,
    ):
        self.id = id
        self.usuario_id = usuario_id
        self.filas = filas
        self.columnas = columnas
        self.paredes = generar_laberinto(filas, columnas, generador_aleatorio)
        self.jugador = POSICION_INICIAL
        self.meta = (filas - 1, columnas - 1)
        self.enemigo = _celda_mas_lejana(self.paredes, self.jugador)
        self.ganada = False
        self.perdida = False
        self.iniciada_en = time.time()
        self.tiempo_segundos = None

    def mover(self, direccion):
        """Mueve al jugador si el movimiento es válido (no hay pared en esa
        dirección desde su celda actual). Devuelve True si se aplicó.

        Detecta victoria (llegar a la meta) y derrota (quedar en la misma
        celda que el enemigo). Chocar contra una pared es parte normal del
        juego, no un error de programación (ver GUIA-ARQUITECTURA-Y-CALIDAD.md,
        sección 0.4) -- por eso se ignora en silencio en vez de lanzar una
        excepción.
        """
        if self.ganada or self.perdida or direccion not in DELTAS:
            return False

        fila, columna = self.jugador
        if self.paredes[fila][columna][direccion]:
            return False

        df, dc = DELTAS[direccion]
        self.jugador = (fila + df, columna + dc)

        if self.jugador == self.enemigo:
            self.perdida = True
            return True

        if self.jugador == self.meta:
            self.ganada = True
            self.tiempo_segundos = time.time() - self.iniciada_en

        return True

    def mover_enemigo(self):
        """Un paso del enemigo persiguiendo al jugador por el camino más
        corto real (BFS, recalculado cada vez porque el jugador se mueve).
        Detecta si con ese paso atrapó al jugador."""
        if self.ganada or self.perdida:
            return

        siguiente = _siguiente_paso_bfs(self.paredes, self.enemigo, self.jugador)
        if siguiente is not None:
            self.enemigo = siguiente

        if self.enemigo == self.jugador:
            self.perdida = True

    def a_dict(self):
        return {
            "filas": self.filas,
            "columnas": self.columnas,
            "paredes": self.paredes,
            "jugador": list(self.jugador),
            "enemigo": list(self.enemigo),
            "meta": list(self.meta),
            "ganada": self.ganada,
            "perdida": self.perdida,
        }
