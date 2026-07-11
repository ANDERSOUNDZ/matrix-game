# 0001 - Arquitectura modular por feature, con un solo backend desplegable

## Contexto

Tres desarrolladores independientes van a construir en paralelo tres features del
juego (autenticación, laberinto Matrix multijugador en tiempo real, y la pantalla de
celebración con filtro de foto para compartir), y necesitan poder trabajar sin
bloquearse ni generar conflictos de fusión constantes.

## Decisión

- El backend es **un único servicio desplegable** (no microservicios), pero
  internamente organizado **por feature** (bounded context), no por capa técnica.
  Cada feature vive en `backend/modulos/<nombre>/` con su propio
  dominio/puertos/aplicación/adaptadores (arquitectura hexagonal, ver
  `GUIA-ARQUITECTURA-Y-CALIDAD.md`, Nivel 1).
- Los módulos **nunca se importan el dominio entre sí**. Toda comunicación cruzada
  pasa por `backend/compartido/`: un bus de eventos in-process (Nivel 3 de la guía) y
  puertos explícitos (ej. `VerificadorDeSesion`).
- Cada módulo tiene su **propio esquema de Postgres** y su **propia carpeta/entorno
  de migraciones de Alembic**, con tabla de versionado independiente. Un único script
  (`backend/scripts/migrar_todo.py`) aplica las migraciones de los tres módulos, en
  orden, contra la misma base de datos física.
- Backend en Flask + Flask-SocketIO (websockets), por continuidad con el stack ya
  usado en otros proyectos del equipo. Frontend en JavaScript vanilla, organizado por
  la misma convención de carpetas por feature.
- No se introduce Redis todavía (una sola instancia de backend por ahora). Si en el
  futuro se escala a múltiples instancias, Socket.IO va a necesitar un backend de
  mensajería compartido (Redis) para sincronizar el estado entre instancias — se deja
  documentado acá para no perder la razón cuando haga falta.

## Consecuencias

- Los tres desarrolladores pueden trabajar semanas en paralelo tocando solo su propia
  carpeta (`backend/modulos/<suyo>/`, `frontend/src/<suyo>/`) sin generar conflictos
  de Git entre sí, ni siquiera en las migraciones de base de datos.
- El único punto de coordinación real es `backend/compartido/` — cualquier cambio ahí
  requiere acuerdo explícito de los tres antes de mergear (ver README, sección de
  flujo de trabajo en ramas).
- Si más adelante el proyecto necesita escalar un módulo de forma independiente del
  resto (por ejemplo, el laberinto necesita muchos más recursos que los otros dos), la
  separación por carpetas ya hecha facilita partirlo en un servicio propio — recién
  ahí entrarían en juego los patrones de sistemas distribuidos (Nivel 4 de la guía:
  enrutamiento de API, saga, etc.), que hoy no aplican porque todo vive en un solo
  proceso desplegable.
