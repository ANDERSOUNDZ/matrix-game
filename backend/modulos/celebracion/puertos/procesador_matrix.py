"""Puerto de procesamiento visual para Matrix Vision."""

from typing import Protocol


class ProcesadorMatrix(Protocol):
    def procesar_jpeg(self, datos_jpeg: bytes) -> bytes:
        """Recibe un JPEG y devuelve otro JPEG con el efecto Matrix."""
        ...
