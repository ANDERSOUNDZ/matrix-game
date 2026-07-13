"""Servicio de aplicación para procesar frames de Matrix Vision."""


class ProcesarFrameMatrixUseCase:
    def __init__(self, procesador_matrix):
        self._procesador_matrix = procesador_matrix

    def ejecutar(self, datos_jpeg: bytes) -> bytes:
        if not datos_jpeg:
            raise ValueError("frame vacío")
        return self._procesador_matrix.procesar_jpeg(datos_jpeg)
