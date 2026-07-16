FROM nginx:alpine

# Sirve archivos estaticos + vendor (descargados en el repo)
COPY . /usr/share/nginx/html

# vendor/ se copia con el resto del frontend
RUN chmod -R a+r /usr/share/nginx/html

EXPOSE 80
