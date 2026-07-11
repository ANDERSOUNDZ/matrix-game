"""Tests unitarios de la entidad de dominio Partida: laberinto procedural
con paredes por celda y un enemigo que persigue por el camino más corto
real (BFS) -- ver docs/decisiones/0003-laberinto-3d-con-enemigo.md.

Se usa un `random.Random(semilla)` inyectado para que la generación del
laberinto sea reproducible, pero las aserciones se apoyan en propiedades
generales del algoritmo (no en el layout exacto de paredes) para no quedar
frágiles ante cualquier cambio de implementación del generador.
"""

import random
from collections import deque

from modulos.laberinto.dominio.partida import DELTAS, POSICION_INICIAL, Partida, generar_laberinto


def _todas_las_celdas_alcanzables(paredes):
    filas = len(paredes)
    columnas = len(paredes[0])
    visitadas = {(0, 0)}
    pila = [(0, 0)]
    while pila:
        fila, columna = pila.pop()
        for direccion, (df, dc) in DELTAS.items():
            if paredes[fila][columna][direccion]:
                continue
            vecino = (fila + df, columna + dc)
            if vecino not in visitadas:
                visitadas.add(vecino)
                pila.append(vecino)
    return len(visitadas) == filas * columnas


def _distancia(paredes, origen, destino):
    visitadas = {origen: 0}
    cola = deque([origen])
    while cola:
        actual = cola.popleft()
        if actual == destino:
            return visitadas[actual]
        fila, columna = actual
        for direccion, (df, dc) in DELTAS.items():
            if paredes[fila][columna][direccion]:
                continue
            vecino = (fila + df, columna + dc)
            if vecino not in visitadas:
                visitadas[vecino] = visitadas[actual] + 1
                cola.append(vecino)
    return None


def test_generar_laberinto_conecta_todas_las_celdas():
    paredes = generar_laberinto(6, 6, random.Random(1))
    assert _todas_las_celdas_alcanzables(paredes)


def test_partida_arranca_en_la_posicion_inicial_sin_ganar_ni_perder():
    partida = Partida(id="1", usuario_id="1", generador_aleatorio=random.Random(1))
    assert partida.jugador == POSICION_INICIAL
    assert partida.ganada is False
    assert partida.perdida is False
    assert partida.enemigo != partida.jugador


def test_mover_contra_una_pared_no_cambia_la_posicion():
    # la celda (0,0) siempre tiene pared "arriba" e "izquierda" (es la
    # esquina del grid), sin importar cómo salga la generación aleatoria
    partida = Partida(id="1", usuario_id="1", generador_aleatorio=random.Random(1))
    aplicado = partida.mover("arriba")
    assert aplicado is False
    assert partida.jugador == POSICION_INICIAL


def test_mover_hacia_una_salida_abierta_actualiza_la_posicion():
    # la celda (0,0) siempre tiene al menos una salida (abajo o derecha),
    # porque es parte del árbol de expansión que genera un laberinto perfecto
    partida = Partida(id="1", usuario_id="1", generador_aleatorio=random.Random(1))
    fila, columna = partida.jugador
    for direccion, (df, dc) in DELTAS.items():
        if not partida.paredes[fila][columna][direccion]:
            aplicado = partida.mover(direccion)
            assert aplicado is True
            assert partida.jugador == (fila + df, columna + dc)
            return
    raise AssertionError("la celda inicial no tenía ninguna salida para probar")


def test_llegar_a_la_meta_marca_la_partida_como_ganada():
    partida = Partida(id="1", usuario_id="1", filas=3, columnas=3, generador_aleatorio=random.Random(1))
    fila_meta, columna_meta = partida.meta
    partida.jugador = (fila_meta, columna_meta - 1)
    partida.paredes[fila_meta][columna_meta - 1]["derecha"] = False
    partida.enemigo = (0, 0)  # lejos, para que no interfiera con este test

    partida.mover("derecha")

    assert partida.jugador == partida.meta
    assert partida.ganada is True
    assert partida.tiempo_segundos is not None


def test_chocar_con_el_enemigo_al_moverse_marca_la_partida_como_perdida():
    partida = Partida(id="1", usuario_id="1", filas=3, columnas=3, generador_aleatorio=random.Random(1))
    partida.jugador = (1, 1)
    partida.enemigo = (1, 2)
    partida.paredes[1][1]["derecha"] = False

    partida.mover("derecha")

    assert partida.jugador == (1, 2)
    assert partida.perdida is True


def test_mover_una_partida_ya_perdida_no_hace_nada():
    partida = Partida(id="1", usuario_id="1", generador_aleatorio=random.Random(1))
    partida.perdida = True
    posicion_previa = partida.jugador

    aplicado = partida.mover("derecha")

    assert aplicado is False
    assert partida.jugador == posicion_previa


def test_mover_enemigo_se_acerca_al_jugador_por_el_camino_mas_corto():
    partida = Partida(id="1", usuario_id="1", filas=5, columnas=5, generador_aleatorio=random.Random(1))
    distancia_inicial = _distancia(partida.paredes, partida.enemigo, partida.jugador)

    partida.mover_enemigo()

    distancia_final = _distancia(partida.paredes, partida.enemigo, partida.jugador)
    assert distancia_final == distancia_inicial - 1


def test_mover_enemigo_hasta_atrapar_al_jugador_marca_la_partida_como_perdida():
    partida = Partida(id="1", usuario_id="1", filas=5, columnas=5, generador_aleatorio=random.Random(1))
    # en un laberinto perfecto hay un único camino: perseguir lo suficiente
    # siempre termina en captura
    for _ in range(partida.filas * partida.columnas):
        partida.mover_enemigo()
        if partida.perdida:
            break

    assert partida.perdida is True
    assert partida.enemigo == partida.jugador


def test_mover_enemigo_en_partida_ya_ganada_no_hace_nada():
    partida = Partida(id="1", usuario_id="1", generador_aleatorio=random.Random(1))
    partida.ganada = True
    posicion_previa = partida.enemigo

    partida.mover_enemigo()

    assert partida.enemigo == posicion_previa
    assert partida.perdida is False
