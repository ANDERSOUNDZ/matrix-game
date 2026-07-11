"""Adaptador de salida: implementa AlmacenDeFotos guardando en disco.

En desarrollo, esta carpeta está dentro del volumen que ya monta
`./backend:/app` en docker-compose.yml, así que las fotos persisten entre
reinicios del contenedor. En un despliegue real (sin ese bind mount), esta
carpeta sería efímera -- ahí hace falta un volumen persistente dedicado o
almacenamiento de objetos (S3 o similar).
"""

import os
import uuid

CARPETA_FOTOS = os.environ.get("CARPETA_FOTOS", "/app/almacenamiento/fotos")
os.makedirs(CARPETA_FOTOS, exist_ok=True)


class AlmacenDeFotosDisco:
    def guardar(self, usuario_id, datos_imagen, extension="png"):
        nombre_archivo = f"{usuario_id}-{uuid.uuid4().hex}.{extension}"
        ruta = os.path.join(CARPETA_FOTOS, nombre_archivo)
        with open(ruta, "wb") as archivo:
            archivo.write(datos_imagen)
        return f"/celebracion/fotos/{nombre_archivo}"
