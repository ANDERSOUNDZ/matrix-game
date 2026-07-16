FROM nginx:alpine

# MIME types para vendor (vision_bundle.mjs, vision_wasm_internal.wasm)
COPY nginx.conf /etc/nginx/conf.d/mime-mediapipe.conf

# Sirve archivos estaticos + vendor (descargados en el repo)
COPY . /usr/share/nginx/html

# vendor/ se copia con el resto del frontend
RUN chmod -R a+r /usr/share/nginx/html

EXPOSE 80
