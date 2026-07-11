"""Tests unitarios de la entidad de dominio Partida (sin Flask-SocketIO)."""

from modulos.laberinto.dominio.partida import POSICION_INICIAL, POSICION_META, Partida


def test_partida_arranca_en_la_posicion_inicial():
    partida = Partida(id="1", usuario_id="1")
    assert (partida.fila, partida.columna) == POSICION_INICIAL
    assert partida.ganada is False


def test_mover_a_una_celda_libre_actualiza_la_posicion():
    partida = Partida(id="1", usuario_id="1")
    aplicado = partida.mover("derecha")
    assert aplicado is True
    assert (partida.fila, partida.columna) == (0, 1)


def test_mover_contra_una_pared_no_cambia_la_posicion():
    partida = Partida(id="1", usuario_id="1")
    aplicado = partida.mover("abajo")  # (1,0) es pared en el grid fijo
    assert aplicado is False
    assert (partida.fila, partida.columna) == POSICION_INICIAL


def test_mover_fuera_del_grid_no_cambia_la_posicion():
    partida = Partida(id="1", usuario_id="1")
    aplicado = partida.mover("arriba")  # ya está en la fila 0
    assert aplicado is False
    assert (partida.fila, partida.columna) == POSICION_INICIAL


def test_llegar_a_la_meta_marca_la_partida_como_ganada():
    partida = Partida(id="1", usuario_id="1")
    partida.fila, partida.columna = 6, 5  # una celda antes de la meta
    partida.mover("derecha")
    assert (partida.fila, partida.columna) == POSICION_META
    assert partida.ganada is True
    assert partida.tiempo_segundos is not None


def test_mover_una_partida_ya_ganada_no_hace_nada():
    partida = Partida(id="1", usuario_id="1")
    partida.fila, partida.columna = POSICION_META
    partida.ganada = True
    aplicado = partida.mover("arriba")
    assert aplicado is False
