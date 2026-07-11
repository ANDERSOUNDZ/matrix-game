"""Tests de los casos de uso de laberinto, usando el repositorio real en
memoria (ya es rápido y aislado, no hace falta un fake) y verificando que
ganar publica `PartidaGanada` en el bus de eventos compartido -- ver
GUIA-ARQUITECTURA-Y-CALIDAD.md, Nivel 1 sección 1.4 y Nivel 3.
"""

from compartido.event_bus import event_bus
from compartido.eventos import PartidaGanada
from modulos.laberinto.adaptadores.persistencia.memoria import PartidaRepositoryEnMemoria
from modulos.laberinto.aplicacion.casos_de_uso import CrearPartidaUseCase, MoverJugadorUseCase


def test_crear_partida_arranca_en_la_posicion_inicial():
    repositorio = PartidaRepositoryEnMemoria()
    caso_de_uso = CrearPartidaUseCase(repositorio)

    partida = caso_de_uso.ejecutar(usuario_id="usuario-1")

    assert (partida.fila, partida.columna) == (0, 0)


def test_mover_jugador_persiste_la_nueva_posicion():
    repositorio = PartidaRepositoryEnMemoria()
    CrearPartidaUseCase(repositorio).ejecutar(usuario_id="usuario-1")
    caso_de_uso = MoverJugadorUseCase(repositorio)

    caso_de_uso.ejecutar(usuario_id="usuario-1", direccion="derecha")

    partida = repositorio.obtener_por_usuario("usuario-1")
    assert (partida.fila, partida.columna) == (0, 1)


def test_ganar_publica_partida_ganada_en_el_bus_compartido():
    repositorio = PartidaRepositoryEnMemoria()
    partida = CrearPartidaUseCase(repositorio).ejecutar(usuario_id="usuario-1")
    partida.fila, partida.columna = 6, 5
    repositorio.guardar(partida)

    recibidos = []
    event_bus.suscribirse(PartidaGanada, recibidos.append)

    MoverJugadorUseCase(repositorio).ejecutar(usuario_id="usuario-1", direccion="derecha")

    assert len(recibidos) == 1
    assert recibidos[0].usuario_id == "usuario-1"
