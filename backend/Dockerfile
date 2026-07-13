FROM python:3.12-slim

WORKDIR /app

# Dependencias de sistema para opencv/mediapipe (modulo celebracion, Matrix
# Vision) -- necesarias aun con la variante "headless" de opencv. mediapipe
# referencia simbolos de OpenGL ES/EGL al crear el FaceLandmarker (incluso
# en CPU), aunque no haya display real -- sin libgles2/libegl1 falla recien
# al procesar el primer frame, no al arrancar (el detector se crea recien
# ahi), asi que un arranque limpio no alcanza para confirmar que esto anda.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libgomp1 \
    libgles2 \
    libegl1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# mediapipe arrastra una variante de opencv que choca con
# opencv-python-headless (error de import/GL en runtime sin display). Se
# fuerza a que quede solo la headless, en la version que se probo estable.
RUN pip uninstall -y opencv-python opencv-contrib-python \
    opencv-contrib-python-headless opencv-python-headless || true \
    && pip install --no-cache-dir opencv-python-headless==4.12.0.88

COPY . .

EXPOSE 5000

# TODO: antes de un despliegue real, cambiar a un servidor WSGI de
# produccion (gunicorn + eventlet/gevent) en vez del servidor de
# desarrollo de Flask que usa compartido/app.py por ahora.
#
# Corre las migraciones de los 3 modulos antes de arrancar -- es seguro
# ejecutarlo en cada arranque/deploy: Alembic solo aplica lo que falte
# (upgrade a head), no hace nada si ya esta al dia.
CMD python scripts/migrar_todo.py && python -m compartido.app
