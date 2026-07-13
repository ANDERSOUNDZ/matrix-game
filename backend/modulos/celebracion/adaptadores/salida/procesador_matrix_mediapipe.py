"""Adaptador OpenCV + MediaPipe para transformar frames en retratos Matrix."""

from __future__ import annotations

import os
from pathlib import Path
from threading import Lock

import cv2
import mediapipe as mp
import numpy as np


class ProcesadorMatrixMediaPipe:
    CARACTERES = " .,:-=+*#%@"
    CODIGO = (
        "0123456789"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "@#$%&*+=<>[]{}"
        "¦|/\\^~"
    )

    def __init__(self) -> None:
        base_modulo = Path(__file__).resolve().parents[2]
        ruta_por_defecto = base_modulo / "modelos" / "face_landmarker.task"
        self._ruta_modelo = Path(os.environ.get("FACE_LANDMARKER_MODEL", ruta_por_defecto))

        self._ancho_celda = int(os.environ.get("MATRIX_CELL_WIDTH", "6"))
        self._alto_celda = int(os.environ.get("MATRIX_CELL_HEIGHT", "8"))
        self._umbral = int(os.environ.get("MATRIX_BLACK_THRESHOLD", "5"))
        self._calidad_jpeg = int(os.environ.get("MATRIX_JPEG_QUALITY", "80"))
        self._escala_fuente = float(os.environ.get("MATRIX_FONT_SCALE", "0.32"))

        self._detector = None
        self._lock = Lock()
        self._numero_frame = 0

    def _obtener_detector(self):
        if self._detector is not None:
            return self._detector

        if not self._ruta_modelo.exists():
            raise FileNotFoundError(
                "No se encontró face_landmarker.task en "
                f"{self._ruta_modelo}. Copia el modelo en "
                "backend/modulos/celebracion/modelos/."
            )

        opciones = mp.tasks.vision.FaceLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(
                model_asset_path=str(self._ruta_modelo),
            ),
            running_mode=mp.tasks.vision.RunningMode.IMAGE,
            num_faces=1,
        )
        self._detector = mp.tasks.vision.FaceLandmarker.create_from_options(opciones)
        return self._detector

    def procesar_jpeg(self, datos_jpeg: bytes) -> bytes:
        buffer = np.frombuffer(datos_jpeg, dtype=np.uint8)
        frame = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
        if frame is None:
            raise ValueError("no fue posible decodificar el frame JPEG")

        # Evita que dos eventos Socket.IO usen simultáneamente el detector.
        with self._lock:
            self._numero_frame += 1
            puntos = self._detectar_puntos(frame)
            salida = self._crear_retrato_matrix(frame, puntos, self._numero_frame)

        correcto, jpeg = cv2.imencode(
            ".jpg",
            salida,
            [cv2.IMWRITE_JPEG_QUALITY, self._calidad_jpeg],
        )
        if not correcto:
            raise RuntimeError("no fue posible codificar el resultado")
        return jpeg.tobytes()

    def _detectar_puntos(self, frame: np.ndarray) -> list[tuple[int, int]]:
        detector = self._obtener_detector()
        alto, ancho = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        imagen_mp = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        resultado = detector.detect(imagen_mp)

        if not resultado.face_landmarks:
            return []

        return [
            (int(punto.x * ancho), int(punto.y * alto))
            for punto in resultado.face_landmarks[0]
        ]

    @staticmethod
    def _mascara_rostro(
            shape,
            puntos: list[tuple[int, int]],
    ) -> np.ndarray:
        alto, ancho = shape[:2]

        mascara = np.zeros(
            (alto, ancho),
            dtype=np.uint8,
        )

        if len(puntos) < 3:
            return mascara

        contorno = cv2.convexHull(
            np.asarray(
                puntos,
                dtype=np.int32,
            )
        )

        cv2.fillConvexPoly(
            mascara,
            contorno,
            255,
        )

        mascara = cv2.dilate(
            mascara,
            np.ones(
                (21, 21),
                dtype=np.uint8,
            ),
            iterations=2,
        )

        return cv2.GaussianBlur(
            mascara,
            (31, 31),
            0,
        )

    def _crear_retrato_matrix(
            self,
            frame: np.ndarray,
            puntos: list[tuple[int, int]],
            numero_frame: int,
    ) -> np.ndarray:
        alto, ancho = frame.shape[:2]

        # Convertir a escala de grises.
        gris = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY,
        )

        # Mejorar contraste local sin quemar las zonas claras.
        gris = cv2.createCLAHE(
            clipLimit=2.4,
            tileGridSize=(8, 8),
        ).apply(gris)

        # Antes estaba en beta=-35 y eliminaba demasiados tonos medios.
        gris = cv2.convertScaleAbs(
            gris,
            alpha=1.22,
            beta=-15,
        )

        mascara = self._mascara_rostro(
            frame.shape,
            puntos,
        )

        columnas = max(
            1,
            ancho // self._ancho_celda,
        )

        filas = max(
            1,
            alto // self._alto_celda,
        )

        mini = cv2.resize(
            gris,
            (columnas, filas),
            interpolation=cv2.INTER_AREA,
        )

        mini_mascara = cv2.resize(
            mascara,
            (columnas, filas),
            interpolation=cv2.INTER_AREA,
        )

        salida = np.zeros_like(frame)

        aleatorio = np.random.default_rng(
            numero_frame // 3
        )

        for fila in range(filas):
            y = (
                    fila * self._alto_celda
                    + self._alto_celda
            )

            for columna in range(columnas):
                brillo = int(
                    mini[fila, columna]
                )

                if brillo < self._umbral:
                    continue

                es_rostro = (
                        mini_mascara[fila, columna] > 80
                )

                indice = min(
                    len(self.CARACTERES) - 1,
                    int(
                        brillo
                        / 256
                        * len(self.CARACTERES)
                    ),
                )

                caracter = self.CARACTERES[indice]

                probabilidad_codigo = (
                    0.02
                    if es_rostro
                    else 0.14
                )

                if aleatorio.random() < probabilidad_codigo:
                    caracter = self.CODIGO[
                        int(
                            aleatorio.integers(
                                0,
                                len(self.CODIGO),
                            )
                        )
                    ]

                variacion = int(
                    aleatorio.integers(-12, 13)
                )

                verde = max(
                    35,
                    min(
                        220,
                        int(brillo * 1.14) + 18 + variacion,
                    )
                )

                azul = 0
                rojo = 0

                x = (
                        columna
                        * self._ancho_celda
                )

                cv2.putText(
                    salida,
                    caracter,
                    (x, y),
                    cv2.FONT_HERSHEY_PLAIN,
                    self._escala_fuente,
                    (
                        azul,
                        verde,
                        rojo,
                    ),
                    1,
                    cv2.LINE_AA,
                )

        return salida
