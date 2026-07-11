# 0002 - Flujo conectado de punta a punta (walking skeleton)

## Contexto

El cascarón inicial (ADR 0001) dejó la estructura, la conexión entre módulos y los
endpoints de salud funcionando, pero sin lógica de negocio real. Se necesitaba ver el
flujo completo funcionando: login → dashboard → jugar el laberinto → ganar → pantalla
de celebración con selfie → compartir → volver al dashboard → cerrar sesión.

## Decisión

- **Token de sesión:** JWT devuelto en el cuerpo de `/auth/login` y `/auth/registro`,
  guardado en `localStorage` del navegador. Se envía como header
  `Authorization: Bearer <token>` en peticiones HTTP y como `auth: {token}` al
  conectar por Socket.IO. Se prefirió esto sobre una cookie httpOnly porque frontend
  (`:8090`) y backend (`:5000`) están en orígenes distintos, y las cookies
  `SameSite=None` requieren `Secure` (HTTPS), que no aplica en desarrollo local sobre
  HTTP simple.
  - **Trade-off aceptado:** un ataque XSS podría leer el token de `localStorage`. Para
    producción, considerar servir frontend y backend detrás del mismo dominio/proxy
    inverso y pasar a cookie httpOnly + `SameSite=Strict`.
- **Laberinto de un jugador por partida:** se implementó el juego real (grid fijo,
  movimiento, condición de victoria) pero sin sincronización entre varios jugadores
  todavía. Es el paso más grande que falta para el objetivo original de "multijugador
  en tiempo real" — se dejó así intencionalmente para poder entregar el flujo
  completo de punta a punta primero, y abordar la sincronización multijugador como
  incremento posterior sobre una base ya funcionando.
- **Filtro de foto en el navegador:** el filtro "Matrix" se aplica con `<canvas>` del
  lado del cliente (tinte verde, sin procesamiento de imagen en el servidor). El
  backend solo persiste el resultado final (`POST /celebracion/foto`).
- **Compartir:** Web Share API (`navigator.share`) con una descarga como respaldo si
  el navegador no la soporta.
- **Dashboard como página compartida:** vive en `frontend/src/dashboard/`, no
  pertenece a un solo dev (igual que `compartido/` en el backend) porque conecta
  información de `autenticacion` con el botón hacia `laberinto`.

## Consecuencias

- Los 3 módulos ahora tienen una implementación de referencia real y funcionando, no
  solo cascarones con un endpoint de salud — cada dev puede seguir profundizando su
  módulo con un ejemplo concreto delante, en vez de partir de cero.
- El puerto compartido `VerificadorDeSesion` (declarado desde el cascarón en
  `compartido/puertos.py`) ahora tiene una implementación real
  (`modulos/autenticacion/adaptadores/entrada/jwt_sesion.py`) inyectada desde el
  composition root hacia `laberinto` y `celebracion` — la demostración concreta de
  por qué sirve declarar el puerto antes de tener la implementación.
- Pendiente explícito para el Dev 2: sincronización multijugador real. La arquitectura
  (namespace de Socket.IO, bus de eventos) ya está pensada para soportarlo sin
  rediseñar el resto del sistema.
