"""Puerto de salida: lo que el módulo laberinto necesita para guardar el
estado de una partida en curso, sin decir cómo. Ver
GUIA-ARQUITECTURA-Y-CALIDAD.md, Nivel 1, secciones 1.2/1.3.
"""

from typing import Optional, Protocol

from modulos.laberinto.dominio.partida import Partida


class PartidaRepository(Protocol):
    def obtener_por_usuario(self, usuario_id) -> Optional[Partida]: ...

    def guardar(self, partida: Partida) -> None: ...
