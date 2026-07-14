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
    ObtenerTablaDePosicionesUseCase,
)
from modulos.laberinto.dominio.partida import COLUMNAS_POR_DEFECTO, FILAS_POR_DEFECTO


class PuntajeRepositoryFake:
    """Cumple modulos.laberinto.puertos.puntaje_repository.PuntajeRepository
    en memoria, sin Postgres real."""

    def __init__(self):
        self._mejores_por_usuario = {}

    def guardar_si_es_mejor(self, usuario_id, tiempo_segundos):
        actual = self._mejores_por_usuario.get(usuario_id)
        if actual is None or tiempo_segundos < actual:
            self._mejores_por_usuario[usuario_id] = tiempo_segundos

    def mejores(self, limite):
        ordenados = sorted(self._mejores_por_usuario.items(), key=lambda par: par[1])
        return ordenados[:limite]


class ConsultaUsuariosFake:
    """Cumple compartido.puertos.ConsultaUsuarios en memoria."""

    def __init__(self, nombres_por_id):
        self._nombres_por_id = nombres_por_id

    def nombres_por_id(self, ids):
        return {id_: self._nombres_por_id[id_] for id_ in ids if id_ in self._nombres_por_id}


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

    MoverJugadorUseCase(repositorio, PuntajeRepositoryFake()).ejecutar(
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
    repositorio_puntajes = PuntajeRepositoryFake()

    MoverJugadorUseCase(repositorio, repositorio_puntajes).ejecutar(
        conexion_id="sid-1", usuario_id="usuario-1", direccion="derecha"
    )

    assert len(recibidos) == 1
    assert recibidos[0].usuario_id == "usuario-1"
    assert repositorio_puntajes.mejores(10) == [("usuario-1", recibidos[0].tiempo_segundos)]


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
    MoverJugadorUseCase(repositorio, PuntajeRepositoryFake()).ejecutar(
        conexion_id="sid-1", usuario_id="usuario-1", direccion=direccion_abierta
    )

    # Mover la partida de sid-1 no debe afectar en nada a la de sid-2.
    assert repositorio.obtener_por_conexion("sid-2").jugador == partida_2.jugador


def test_eliminar_libera_la_partida_de_esa_conexion():
    """Sin esto, cada conexion que alguna vez jugo queda para siempre en el
    repositorio (ver adaptadores/entrada/websocket.py, on_disconnect)."""
    repositorio = PartidaRepositoryEnMemoria()
    CrearPartidaUseCase(repositorio).ejecutar(conexion_id="sid-1", usuario_id="usuario-1")

    repositorio.eliminar("sid-1")

    assert repositorio.obtener_por_conexion("sid-1") is None


def test_guardar_si_es_mejor_conserva_el_tiempo_mas_rapido():
    repositorio_puntajes = PuntajeRepositoryFake()

    repositorio_puntajes.guardar_si_es_mejor("usuario-1", 20.0)
    repositorio_puntajes.guardar_si_es_mejor("usuario-1", 35.0)  # mas lento, no reemplaza
    repositorio_puntajes.guardar_si_es_mejor("usuario-1", 12.5)  # mas rapido, si reemplaza

    assert repositorio_puntajes.mejores(10) == [("usuario-1", 12.5)]


def test_tabla_de_posiciones_ordena_por_tiempo_y_resuelve_nombres():
    repositorio_puntajes = PuntajeRepositoryFake()
    repositorio_puntajes.guardar_si_es_mejor("usuario-1", 30.0)
    repositorio_puntajes.guardar_si_es_mejor("usuario-2", 15.0)
    repositorio_puntajes.guardar_si_es_mejor("usuario-3", 45.0)
    consulta_usuarios = ConsultaUsuariosFake(
        {"usuario-1": "Ana", "usuario-2": "Beto", "usuario-3": "Caro"}
    )

    posiciones = ObtenerTablaDePosicionesUseCase(repositorio_puntajes, consulta_usuarios).ejecutar(
        limite=10
    )

    assert posiciones == [
        {"nombre": "Beto", "tiempo_segundos": 15.0},
        {"nombre": "Ana", "tiempo_segundos": 30.0},
        {"nombre": "Caro", "tiempo_segundos": 45.0},
    ]


def test_tabla_de_posiciones_respeta_el_limite():
    repositorio_puntajes = PuntajeRepositoryFake()
    for i in range(5):
        repositorio_puntajes.guardar_si_es_mejor(f"usuario-{i}", float(i))
    consulta_usuarios = ConsultaUsuariosFake({f"usuario-{i}": f"Jugador{i}" for i in range(5)})

    posiciones = ObtenerTablaDePosicionesUseCase(repositorio_puntajes, consulta_usuarios).ejecutar(
        limite=2
    )

    assert len(posiciones) == 2


def test_tabla_de_posiciones_usa_nombre_por_defecto_si_no_se_resuelve():
    repositorio_puntajes = PuntajeRepositoryFake()
    repositorio_puntajes.guardar_si_es_mejor("usuario-fantasma", 10.0)
    consulta_usuarios = ConsultaUsuariosFake({})

    posiciones = ObtenerTablaDePosicionesUseCase(repositorio_puntajes, consulta_usuarios).ejecutar()

    assert posiciones == [{"nombre": "Jugador", "tiempo_segundos": 10.0}]
