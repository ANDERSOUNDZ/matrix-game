"""Puerto de salida: lo que el módulo celebración necesita para guardar una
foto y obtener una URL para compartirla, sin decir dónde se guarda
realmente. Ver GUIA-ARQUITECTURA-Y-CALIDAD.md, Nivel 1, secciones 1.2/1.3.
"""

from typing import Protocol


class AlmacenDeFotos(Protocol):
    def guardar(self, usuario_id, datos_imagen: bytes, extension: str = "png") -> str:
        """Guarda los bytes de la imagen y devuelve una URL para acceder a ella."""
        ...
