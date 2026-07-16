FROM nginx:alpine

# MIME types para vendor (vision_bundle.mjs, vision_wasm_internal.wasm)
RUN sed -i '/application\/javascript/s/;/ mjs;/' /etc/nginx/mime.types \
    && sed -i '/application\/wasm/s/;/ wasm;/' /etc/nginx/mime.types || true

# Sirve archivos estaticos + vendor (descargados en el repo)
COPY . /usr/share/nginx/html

# vendor/ se copia con el resto del frontend
RUN chmod -R a+r /usr/share/nginx/html

EXPOSE 80
