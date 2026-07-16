# Matrix Game — Presentación Técnica

---

## 1. ¿Qué es Matrix Game?

Juego de laberinto 3D estilo Matrix donde el usuario:
1. Se registra con email y contraseña
2. Juega un laberinto en primera persona
3. Al ganar, se toma una selfie con filtro Matrix
4. Comparte la foto en redes sociales

---

## 2. Stack Tecnológico

### Backend
- **Lenguaje:** Python 3.12
- **Framework:** Flask 3.x
- **Tiempo real:** Flask-SocketIO + WebSocket
- **Base de datos:** PostgreSQL 16
- **ORM:** SQLAlchemy 2.x + Alembic
- **Servidor:** Gunicorn + Eventlet

### Frontend
- **Motor 3D:** Three.js 0.128
- **Sockets:** Socket.IO client 4.7.5
- **Hand tracking:** MediaPipe Tasks Vision (WASM en navegador)
- **Estilos:** Matrix rain + CSS Matrix verde clásico

### Infraestructura
- **Contenedores:** Docker Compose (3 servicios)
- **Frontend servido por:** Nginx Alpine

---

## 3. Arquitectura del Proyecto

### Organización por Features (Hexagonal)

```
backend/
├── compartido/
│   ├── event_bus.py       ← Comunicación entre módulos
│   ├── eventos.py          ← Contratos de eventos
│   └── puertos.py          ← Interfaces compartidas
│
└── modulos/
    ├── autenticacion/      ← Dev 1
    ├── laberinto/          ← Dev 2
    └── celebracion/        ← Dev 3
```

### Principio clave
Los 3 módulos NUNCA se importan entre sí.
Se comunican a través del bus de eventos (event_bus.py).
Ejemplo: laberinto publica "PartidaGanada" → celebracion reacciona.

---

## 4. Los 3 Servicios Docker

| Servicio | Imagen | Puerto | Propósito |
|----------|--------|--------|-----------|
| postgres | postgres:16-alpine | 5432 | Base de datos |
| backend | Build local (Python) | 5000 | API Flask + WebSocket |
| frontend | nginx:alpine | 8090 | Página web estática |

---

## 5. Base de Datos

PostgreSQL con 3 esquemas independientes:

### Esquema autenticacion
- `usuarios` → email, password_hash, nombre
- `sesiones` → JWT tokens

### Esquema laberinto
- `partidas` → estado del juego, posición, tiempo
- Movimiento en tiempo real vía WebSocket

### Esquema celebracion
- `fotos` → imagen con filtro Matrix aplicado
- Metadatos de la celebración

Cada esquema tiene sus propias migraciones Alembic.

---

## 6. Flujo del Usuario

```
1. Registro/Login → http://localhost:8090
2. Dashboard → ver información del perfil
3. Click "Jugar" → se abre el laberinto 3D
4. Resolver laberinto → flechas del teclado
5. ¡Ganar! → pantalla de celebración
6. Selfie → filtro Matrix automático
7. Compartir → WhatsApp, Facebook, Twitter
8. Volver al dashboard
```

---

## 7. Funcionalidades Destacadas

### Laberinto 3D
- Renderizado con Three.js
- Movimiento en primera persona
- Música ambiental (Clubbed to Death)
- Control por teclado (flechas)
- Control por cámara (MediaPipe mano)

### Autenticación
- Registro y login
- JWT para sesiones
- Protección de rutas

### Celebración
- Captura de foto con cámara web
- Filtro Matrix verde en tiempo real (OpenCV)
- Compartir en WhatsApp, Facebook, Twitter
- Descarga de imagen local

---

## 8. Despliegue (3 comandos)

```bash
git clone -b completo https://github.com/ANDERSOUNDZ/matrix-game.git
cd matrix-game
cp .env.example .env
docker compose up -d
docker compose exec backend python scripts/migrar_todo.py
```

### Requisito único
**Docker Desktop** instalado en la PC.

---

## 9. Lo que incluye el repositorio

| Componente | Tamaño | ¿Necesita internet? |
|-----------|--------|-------------------|
| Código fuente | ~15 MB | ❌ No |
| Three.js + Socket.IO + MediaPipe | ~22 MB | ❌ No |
| Python wheels (Flask, SQLAlchemy, mediapipe, opencv, etc.) | ~200 MB | ❌ No |
| Imágenes Docker base (Python, PostgreSQL, Nginx) | ~300 MB | 🌐 Solo la primera vez |

---

## 10. Comandos Útiles

```bash
# Ver estado
docker compose ps

# Logs
docker compose logs -f backend
docker compose logs -f frontend

# Detener
docker compose down

# Borrar BD
docker compose down -v

# Tests
docker compose exec backend pytest -v
```

---

## 11. Posibles Mejoras Futuras

- **Multijugador:** Varias personas en el mismo laberinto
- **Dificultad:** Laberintos generados proceduralmente con niveles
- **Más filtros:** Varios estilos de filtro para la selfie
- **Perfiles:** Roles de administrador, estadísticas de partidas
- **Mobile:** Adaptar el frontend para dispositivos móviles

---

## 12. Enlaces

- **Repositorio:** https://github.com/ANDERSOUNDZ/matrix-game
- **Rama completo:** https://github.com/ANDERSOUNDZ/matrix-game/tree/completo
- **Documentación técnica:** `docs/decisiones/` dentro del repositorio
