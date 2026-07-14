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

# Corre las migraciones de los 3 modulos antes de arrancar -- es seguro
# ejecutarlo en cada arranque/deploy: Alembic solo aplica lo que falte
# (upgrade a head), no hace nada si ya esta al dia.
#
# gunicorn con worker eventlet en vez del servidor de desarrollo de Flask:
# ese servidor no sostiene un upgrade real a WebSocket (el sintoma real fue
# el laberinto quedando con pantalla negra -- el socket nunca terminaba de
# conectar, asi que el evento "estado" que dispara el primer render nunca
# llegaba). Un solo worker (-w 1): el estado de las partidas activas vive
# en memoria del proceso (PartidaRepositoryEnMemoria) -- con mas de un
# worker cada uno tendria su propia copia. Si se necesita escalar a mas de
# una instancia, hace falta antes un almacen compartido (Redis) para el
# estado de partidas y para el message queue de Socket.IO entre workers.
CMD python scripts/migrar_todo.py && gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:${PORT:-${FLASK_PORT:-5000}} compartido.app:app
