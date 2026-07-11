FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# TODO: antes de un despliegue real, cambiar a un servidor WSGI de
# produccion (gunicorn + eventlet/gevent) en vez del servidor de
# desarrollo de Flask que usa compartido/app.py por ahora.
CMD ["python", "-m", "compartido.app"]
