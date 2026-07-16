FROM nginx:alpine

# Sirve archivos estaticos + vendor (descargados en el repo)
COPY . /usr/share/nginx/html

# Copia vision_bundle.mjs como .js para evitar MIME type .mjs
RUN cp /usr/share/nginx/html/vendor/mediapipe/vision_bundle.mjs \
      /usr/share/nginx/html/vendor/mediapipe/vision_bundle.js \
    && chmod -R a+r /usr/share/nginx/html

EXPOSE 80
