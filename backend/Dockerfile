FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

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
