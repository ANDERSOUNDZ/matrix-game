FROM nginx:alpine

# Cascaron: sirve archivos estaticos tal cual. El dia que se sume un
# framework de frontend con build step (React/Vue/etc.), este Dockerfile
# pasa a tener una etapa de build antes de copiar a nginx.
COPY . /usr/share/nginx/html

EXPOSE 80
