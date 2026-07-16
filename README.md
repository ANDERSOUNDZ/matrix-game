# Matrix Game

Juego de laberinto estilo Matrix, con autenticación y una pantalla final de
"ganador" con filtro de foto para compartir.

**El flujo completo ya está conectado y funcionando de punta a punta**: registro/
login → dashboard → jugar el laberinto → ganar → selfie con filtro → compartir →
volver al dashboard → cerrar sesión. Es una implementación de referencia real y
mínima en los 3 módulos (ver ADR `docs/decisiones/0002-...md`) — cada dev tiene
ahora un ejemplo concreto y funcionando sobre el cual seguir construyendo, no un
cascarón vacío.

## Arquitectura (resumen — ver `porgramas/GUIA-ARQUITECTURA-Y-CALIDAD.md` para el detalle completo)

Un único backend desplegable, organizado **por feature**, no por capa técnica. Cada
feature es un módulo independiente con su propio dominio/puertos/aplicación/
adaptadores (arquitectura hexagonal, Nivel 1 de la guía):

```
backend/
├── compartido/        # bus de eventos + puertos que cruzan módulos + composition root
│                       # TOCAR SOLO CON ACUERDO DE LOS 3 DEVS
└── modulos/
    ├── autenticacion/  # Dev 1 — registro, login, JWT
    ├── laberinto/      # Dev 2 — el juego (un jugador por partida, por ahora)
    └── celebracion/    # Dev 3 — guardar la foto con el filtro
```

Los módulos **nunca se importan el dominio entre sí**. Se comunican a través del bus
de eventos compartido (`compartido/event_bus.py`) o de puertos explícitos
(`compartido/puertos.py`). Ejemplo: cuando alguien gana el laberinto, el módulo
`laberinto` publica el evento `PartidaGanada`; el módulo `celebracion` está
suscripto a ese evento y reacciona — sin que `laberinto` sepa que `celebracion`
existe. El puerto compartido `VerificadorDeSesion` (implementado por
`autenticacion`, consumido por `laberinto` y `celebracion`) funciona igual: se
inyecta desde `compartido/app.py`, sin que esos módulos importen `autenticacion`.

## Independencia de la base de datos

Los 3 módulos comparten una sola instancia de Postgres, pero cada uno tiene:

- **Su propio esquema** (`autenticacion`, `laberinto`, `celebracion`).
- **Su propia carpeta de migraciones de Alembic** (`modulos/<nombre>/migraciones/`),
  con su propia tabla de versionado. Nadie edita la carpeta de migraciones de otro
  módulo, así que nunca hay conflictos de fusión por migraciones.

Un único script corre las migraciones de los tres, en orden:

```bash
docker compose exec backend python scripts/migrar_todo.py
```

## ¿Qué necesitas instalar?

**Solo una cosa:** [Docker Desktop](https://www.docker.com/products/docker-desktop/)

No necesitas Python, Node.js, PostgreSQL, ni descargar nada a mano.

## Cómo levantar todo (2 comandos)

```bash
cp .env.example .env
docker compose up -d
docker compose exec backend python scripts/migrar_todo.py
```

> **Nota:** Las librerías frontend (Three.js, Socket.IO, MediaPipe, ~22 MB) y
> las librerías Python (Flask, SQLAlchemy, mediapipe, ~200 MB) ya vienen
> incluidas en el repositorio. Docker solo necesita internet la primera vez
> para descargar las imágenes base (Python, PostgreSQL, Nginx).

- **Frontend:** http://localhost:8080
- **Backend:** http://localhost:5000
- **Postgres:** localhost:5432

### Para usuarios sin internet

Si la PC destino no tiene internet, primero en tu PC (con internet) guardá las imágenes:

```bash
docker pull python:3.12-slim postgres:16-alpine nginx:alpine
docker save python:3.12-slim postgres:16-alpine nginx:alpine -o docker-images.tar
```

Llevá `docker-images.tar` en un USB. En la PC destino:

```bash
docker load -i docker-images.tar
docker compose up -d
docker compose exec backend python scripts/migrar_todo.py
```

## Probarlo en el navegador

1. Abrí `http://localhost:8090` — redirige automáticamente al login.
2. Creá una cuenta (botón "Crear cuenta").
3. En el dashboard, tocá "Jugar".
4. Resolvé el laberinto con las flechas del teclado hasta llegar a la celda dorada.
5. Al ganar, pasás automáticamente a la pantalla de celebración: dale permiso de
   cámara, sacate la selfie (se aplica el filtro verde estilo Matrix), y probá
   "Compartir con amigos" (usa la Web Share API si tu navegador la soporta; si no,
   descarga la imagen).
6. Volvé al dashboard y cerrá sesión.

## Tests

```bash
docker compose exec backend pytest -v
docker compose exec backend ruff check .
```

Incluyen tests de dominio y de casos de uso de los 3 módulos (con repositorios
fake/en memoria, sin Postgres real) y `tests/test_event_bus.py`, que prueba que un
módulo puede reaccionar a un evento publicado por otro sin importarlo directamente.

## Flujo de trabajo en ramas (para los 3 desarrolladores)

1. **Antes de separarse a trabajar solos:** los contratos compartidos
   (`compartido/eventos.py`, `compartido/puertos.py`) y el composition root
   (`compartido/app.py`) ya están armados como punto de partida. Cualquier cambio a
   esos archivos después debe acordarse entre los 3 antes de mergear — no se cambian
   por sorpresa en medio de una feature de otro.
2. Cada dev trabaja **solo** dentro de su carpeta:
   - Dev 1 → `backend/modulos/autenticacion/` y `frontend/src/autenticacion/`
   - Dev 2 → `backend/modulos/laberinto/` y `frontend/src/laberinto/`
   - Dev 3 → `backend/modulos/celebracion/` y `frontend/src/celebracion/`

   `frontend/src/dashboard/` es, igual que `compartido/`, una carpeta compartida
   (conecta info de `autenticacion` con el botón hacia `laberinto`) — cambios ahí
   también se acuerdan entre los 3.

   Nunca se importa el dominio de otro módulo directamente. Si hace falta algo de
   otro módulo, es a través de un puerto o evento ya definido en `compartido/`, o se
   propone agregarlo ahí primero (ver punto 4).
3. Ramas **cortas y por tarea**, no una rama gigante por persona durante semanas:
   `feature/auth-recuperar-password`, `feature/laberinto-multijugador`,
   `feature/celebracion-filtros`, etc.
4. Si hace falta tocar `compartido/`, `docker-compose.yml`, el CI, o las migraciones
   de otro módulo: PR chico y aislado, avisar a los otros dos antes de mergear —
   nunca mezclado con el resto de la feature propia.
5. Merge a `main` frecuente (idealmente diario) vía Pull Request, con al menos 1
   revisor de los otros dos. Activar en GitHub la protección de la rama `main`
   (requerir PR + review antes de mergear).

## Qué le queda a cada dev (próximos pasos reales, no un cascarón vacío)

- **Dev 1 (autenticación):** validaciones más estrictas (formato de email, fuerza de
  contraseña), recuperación de contraseña, expiración/renovación de JWT, roles y
  permisos.
- **Dev 2 (laberinto):** el paso grande pendiente es la **sincronización
  multijugador real** (varias personas en la misma partida, verse mover entre sí,
  condición de quién llega primero) — hoy es un jugador por partida. También:
  laberintos generados proceduralmente, dificultad creciente.
- **Dev 3 (celebración):** filtros visuales más elaborados, integración con redes
  sociales concretas más allá del Web Share API genérico, galería de fotos
  compartidas.

Ver `docs/decisiones/` para el razonamiento completo detrás de estas decisiones.
