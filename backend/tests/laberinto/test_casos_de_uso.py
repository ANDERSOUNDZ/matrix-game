"""Tests de los casos de uso de laberinto, usando el repositorio real en
memoria (ya es rápido y aislado, no hace falta un fake) y verificando que
ganar/perder publican los eventos correspondientes en el bus compartido --
ver GUIA-ARQUITECTURA-Y-CALIDAD.md, Nivel 1 sección 1.4 y Nivel 3.
"""

from compartido.event_bus import event_bus
from compartido.eventos import PartidaGanada, PartidaPerdida
from modulos.laberinto.adaptadores.persistencia.memoria import PartidaRepositoryEnMemoria
from modulos.laberinto.aplicacion.casos_de_uso import (
    CrearPartidaUseCase,
    MoverEnemigoUseCase,
    MoverJugadorUseCase,
)
from modulos.laberinto.dominio.partida import COLUMNAS_POR_DEFECTO, FILAS_POR_DEFECTO


def test_crear_partida_arranca_en_la_posicion_inicial():
    repositorio = PartidaRepositoryEnMemoria()
    caso_de_uso = CrearPartidaUseCase(repositorio)

    partida = caso_de_uso.ejecutar(conexion_id="sid-1", usuario_id="usuario-1")

    assert partida.jugador == (0, 0)
    assert partida.enemigo != partida.jugador


def test_mover_jugador_persiste_la_nueva_posicion():
    repositorio = PartidaRepositoryEnMemoria()
    partida = CrearPartidaUseCase(repositorio).ejecutar(conexion_id="sid-1", usuario_id="usuario-1")
    fila, columna = partida.jugador
    direccion_abierta = next(
        direccion
        for direccion in ("abajo", "derecha")
        if not partida.paredes[fila][columna][direccion]
    )

    MoverJugadorUseCase(repositorio).ejecutar(
        conexion_id="sid-1", usuario_id="usuario-1", direccion=direccion_abierta
    )

    partida_actualizada = repositorio.obtener_por_conexion("sid-1")
    assert partida_actualizada.jugador != (fila, columna)


def test_ganar_publica_partida_ganada_en_el_bus_compartido():
    repositorio = PartidaRepositoryEnMemoria()
    partida = CrearPartidaUseCase(repositorio).ejecutar(conexion_id="sid-1", usuario_id="usuario-1")

    fila_meta, columna_meta = FILAS_POR_DEFECTO - 1, COLUMNAS_POR_DEFECTO - 1
    partida.jugador = (fila_meta, columna_meta - 1)
    partida.paredes[fila_meta][columna_meta - 1]["derecha"] = False
    partida.enemigo = (0, 0)  # lejos, para que no interfiera con este test
    repositorio.guardar(partida)

    recibidos = []
    event_bus.suscribirse(PartidaGanada, recibidos.append)

    MoverJugadorUseCase(repositorio).ejecutar(
        conexion_id="sid-1", usuario_id="usuario-1", direccion="derecha"
    )

    assert len(recibidos) == 1
    assert recibidos[0].usuario_id == "usuario-1"


def test_mover_enemigo_publica_partida_perdida_al_atrapar_al_jugador():
    repositorio = PartidaRepositoryEnMemoria()
    partida = CrearPartidaUseCase(repositorio).ejecutar(conexion_id="sid-1", usuario_id="usuario-1")

    partida.jugador = (0, 0)
    partida.enemigo = (0, 1)
    partida.paredes[0][0]["derecha"] = False
    partida.paredes[0][1]["izquierda"] = False
    # sin esto, el margen de error del enemigo (ver dominio/partida.py) podria
    # hacer que "dude" y el test saliera intermitente
    partida._probabilidad_error_enemigo = 0
    repositorio.guardar(partida)

    recibidos = []
    event_bus.suscribirse(PartidaPerdida, recibidos.append)

    MoverEnemigoUseCase(repositorio).ejecutar(conexion_id="sid-1")

    partida_actualizada = repositorio.obtener_por_conexion("sid-1")
    assert partida_actualizada.perdida is True
    assert len(recibidos) == 1
    assert recibidos[0].usuario_id == "usuario-1"


def test_mover_enemigo_sin_partida_existente_no_falla():
    repositorio = PartidaRepositoryEnMemoria()

    resultado = MoverEnemigoUseCase(repositorio).ejecutar(conexion_id="sid-no-existe")

    assert resultado is None


def test_dos_partidas_distintas_no_interfieren_entre_si():
    repositorio = PartidaRepositoryEnMemoria()
    CrearPartidaUseCase(repositorio).ejecutar(conexion_id="sid-a", usuario_id="usuario-a")
    CrearPartidaUseCase(repositorio).ejecutar(conexion_id="sid-b", usuario_id="usuario-b")

    partida_a = repositorio.obtener_por_conexion("sid-a")
    partida_b = repositorio.obtener_por_conexion("sid-b")

    assert partida_a.usuario_id == "usuario-a"
    assert partida_b.usuario_id == "usuario-b"


def test_misma_cuenta_con_dos_conexiones_no_interfiere_entre_si():
    """Regresion: antes la partida se indexaba por usuario_id, asi que la
    misma cuenta conectada dos veces (dos pestañas, dos computadoras)
    terminaba compartiendo un unico objeto Partida -- la segunda conexion
    pisaba el estado de la primera, y ambos hilos de tick del enemigo
    quedaban moviendo el mismo objeto. Ver adaptadores/persistencia/memoria.py.
    """
    repositorio = PartidaRepositoryEnMemoria()
    partida_1 = CrearPartidaUseCase(repositorio).ejecutar(conexion_id="sid-1", usuario_id="usuario-1")
    partida_2 = CrearPartidaUseCase(repositorio).ejecutar(conexion_id="sid-2", usuario_id="usuario-1")

    assert repositorio.obtener_por_conexion("sid-1") is partida_1
    assert repositorio.obtener_por_conexion("sid-2") is partida_2
    assert partida_1 is not partida_2

    fila, columna = partida_1.jugador
    direccion_abierta = next(
        direccion
        for direccion in ("abajo", "derecha")
        if not partida_1.paredes[fila][columna][direccion]
    )
    MoverJugadorUseCase(repositorio).ejecutar(
        conexion_id="sid-1", usuario_id="usuario-1", direccion=direccion_abierta
    )

    # Mover la partida de sid-1 no debe afectar en nada a la de sid-2.
    assert repositorio.obtener_por_conexion("sid-2").jugador == partida_2.jugador
