# Matrix Game

Juego de laberinto 3D estilo Matrix, con autenticación y pantalla final con filtro de foto estilo Matrix para compartir.

---

## ¿Qué necesitas instalar?

**Solo una cosa:** [Docker Desktop](https://www.docker.com/products/docker-desktop/)

No necesitas Python, Node.js, PostgreSQL, ni descargar nada a mano. Todo se ejecuta dentro de Docker.

---

## Instalación paso a paso

### Paso 1: Instalar Docker Desktop

1. Ve a https://www.docker.com/products/docker-desktop/
2. Descarga e instala Docker Desktop
3. Ábrelo y espera a que aparezca "Engine running"

### Paso 2: Descargar el proyecto

```bash
# Opción A: Con Git (recomendado)
git clone -b completo https://github.com/ANDERSOUNDZ/matrix-game.git
cd matrix-game

# Opción B: Sin Git (ZIP)
# 1. Ve a https://github.com/ANDERSOUNDZ/matrix-game/tree/completo
# 2. Botón "Code" → "Download ZIP"
# 3. Extrae y abre la carpeta
```

### Paso 3: Crear archivo .env

```bash
cp .env.example .env
```

Los valores por defecto ya funcionan, no necesitas cambiarlos.

### Paso 4: Levantar los servicios

```bash
docker compose up -d
```

Esto inicia 3 contenedores:
- **PostgreSQL** — base de datos
- **Backend** — servidor Flask + Socket.IO
- **Frontend** — Nginx con la página web

### Paso 5: Ejecutar migraciones de la base de datos

```bash
docker compose exec backend python scripts/migrar_todo.py
```

Esto crea las tablas necesarias para los 3 módulos (autenticación, laberinto, celebración).

### Paso 6: Abrir la aplicación

| Servicio | URL |
|----------|-----|
| **Frontend** (app principal) | http://localhost:8090 |
| **Backend** (API) | http://localhost:5000 |

### Paso 7: Primer uso

1. Abre http://localhost:8090
2. Haz clic en **"Crear cuenta"**
3. Regístrate con nombre, email y contraseña
4. En el dashboard, haz clic en **"Jugar"**
5. Controla el laberinto con las **flechas del teclado** hasta la celda dorada
6. Al ganar: selfie con filtro Matrix, comparte o descarga la foto
7. Vuelve al dashboard o cierra sesión

---

## ¿Qué hace cada servicio?

| Servicio | Puerto | Tecnología | Para qué sirve |
|----------|--------|-----------|---------------|
| **frontend** | http://localhost:8090 | Nginx + HTML/JS | La página web con el juego |
| **backend** | http://localhost:5000 | Flask + Socket.IO | API, autenticación, partidas, fotos |
| **postgres** | 5432 | PostgreSQL 16 | Guarda usuarios, partidas, fotos |

---

## Comandos útiles

```bash
# Verificar que todo está corriendo
docker compose ps

# Ver logs del backend
docker compose logs -f backend

# Ver logs del frontend
docker compose logs -f frontend

# Detener servicios (sin borrar datos)
docker compose down

# Detener y borrar BD
docker compose down -v

# Reconstruir después de cambios
docker compose up --build -d

# Ejecutar tests
docker compose exec backend pytest -v
```

---

## Solución de problemas

| Problema | Causa | Solución |
|----------|-------|----------|
| Puerto 8090 ocupado | Otro programa lo usa | Cambia `FRONTEND_PORT` en `.env` (ej: `FRONTEND_PORT=8091`) |
| Puerto 5432 ocupado | Otro PostgreSQL local | Detén tu PostgreSQL antes de iniciar Docker |
| "No puedo crear cuenta" | Faltan migraciones | Ejecuta `docker compose exec backend python scripts/migrar_todo.py` |
| El juego no carga | Vendor files no encontrados | Reconstruye: `docker compose build frontend` |
| El laberinto no responde | WebSocket no conecta | Revisa logs: `docker compose logs -f backend` |

---

## Lo que ya viene incluido en el repositorio

| Componente | Tamaño | ¿Necesita internet? |
|-----------|--------|-------------------|
| Código fuente (Python, HTML, JS) | ~15 MB | ❌ No |
| Librerías frontend (Three.js, Socket.IO, MediaPipe, modelo mano) | ~22 MB | ❌ No |
| Librerías Python (Flask, SQLAlchemy, mediapipe, opencv, etc.) | ~200 MB | ❌ No |
| Imágenes Docker base (Python, PostgreSQL, Nginx) | ~300 MB | 🌐 Sí, solo la primera vez |

---

## Arquitectura

El backend está organizado **por feature** (arquitectura hexagonal):

```
backend/
├── compartido/        # Bus de eventos + puertos + composition root
└── modulos/
    ├── autenticacion/  # Registro, login, JWT
    ├── laberinto/      # El juego (laberinto 3D)
    └── celebracion/    # Filtro Matrix para fotos
```

Los módulos **nunca se importan entre sí**. Se comunican a través del bus de eventos compartido.

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
