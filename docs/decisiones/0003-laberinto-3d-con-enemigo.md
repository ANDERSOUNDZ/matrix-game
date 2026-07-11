# 0003 - Laberinto 3D en primera persona con enemigo que persigue

## Contexto

Trabajo exclusivo del Dev 2 dentro de `backend/modulos/laberinto/` y
`frontend/src/laberinto/` (ningún otro módulo se tocó, salvo el agregado puntual
descrito abajo). Dos pedidos:

1. Un enemigo que persigue de verdad al jugador y provoca game over al atraparlo (en
   vez del laberinto estático de ADR 0002, sin enemigo).
2. Renderizar el laberinto en 3D en primera persona, inspirado en el screensaver
   *Windows 95 3D Maze* (`ibid-11962/Windows-95-3D-Maze-Screensaver`).

Ese repositorio se revisó (`gh repo view` / `gh api`) y no tiene un archivo LICENSE
explícito — solo menciona librerías de terceros con licencia MIT. Por eso **no se
copió ningún código ni asset de ahí**: se reimplementó el concepto general
(laberinto generado proceduralmente, cámara en primera persona) con código propio, y
se cambió deliberadamente la estética (paredes de wireframe verde neón, tema
"Matrix", en vez de las texturas de ladrillo de Windows 95).

## Decisión

- **Laberinto procedural** (recursive backtracking, algoritmo genérico de dominio
  público) en vez del grid fijo 7x7 de ADR 0002. Tamaño por defecto 10x10.
- **Modelo de celda cambia**: de "grid de celdas 0/1 bloqueadas" a **celdas con 4
  paredes propias** (`arriba`/`abajo`/`izquierda`/`derecha`). Es el modelo estándar
  para generar laberintos y es lo que necesita el render 3D (por celda se sabe
  exactamente qué paredes dibujar). Esto reemplaza la forma de `Partida.a_dict()`;
  no se mantuvo compatibilidad con el formato viejo porque el frontend 2D se
  reescribió por completo junto con este cambio.
- **Enemigo con persecución real vía BFS**: en cada paso, se recalcula el camino más
  corto real desde la celda del enemigo hasta la del jugador (BFS sobre el grafo de
  celdas conectadas). En un laberinto perfecto (recursive backtracking genera un
  árbol de expansión, sin ciclos) existe un único camino entre dos celdas
  cualquiera, así que "más corto" es también "el único".
- **El enemigo se mueve solo, en tiempo real**, no solo en respuesta al jugador: un
  hilo de fondo por conexión (`socketio.start_background_task`, `async_mode` por
  defecto de Flask-SocketIO) llama a `MoverEnemigoUseCase` cada
  `INTERVALO_ENEMIGO_SEGUNDOS` (1.1s) y emite el `estado` actualizado a ese cliente.
  El hilo se detiene (marcando un flag, no forzando la baja del hilo) al
  desconectar, ganar o perder — ver `_conexiones_activas` en
  `adaptadores/entrada/websocket.py`.
- **Nuevo evento `PartidaPerdida`** en `compartido/eventos.py` (mismo patrón que
  `PartidaGanada`), publicado cuando el enemigo atrapa al jugador. Es la única
  edición fuera de `modulos/laberinto/` en este ADR — se avisó al resto del equipo
  por ser un cambio al contrato compartido.
- **Three.js (r128, build no-módulo vía CDN)** en vez de WebGL puro, para no
  reescribir a mano la matemática de cámara/matrices que el screensaver original sí
  implementó desde cero. Mismo patrón que ya se usa con `socket.io-client`: sin paso
  de build, cargado directo por `<script src=...>`.
- **Controles relativos a la cámara, no absolutos** (corrección post-prueba
  manual): la primera versión mapeaba las 4 flechas 1:1 a las 4 direcciones
  absolutas del dominio (arriba/abajo/izquierda/derecha = norte/sur/este/oeste
  fijos) y hacía saltar la rotación de la cámara a esa dirección al moverse.
  Eso se sentía roto: girar a la izquierda/derecha en realidad *caminaba* hacia
  esa celda (si no había pared) en vez de solo mirar hacia allá, y avanzar podía
  no hacer nada si la celda de esa dirección absoluta estaba tapiada, aunque
  visualmente "el camino de enfrente" estuviera libre. Se corrigió separando
  **girar** (↑/↓ = avanzar/retroceder en la dirección absoluta a la que se está
  mirando actualmente; ←/→ = rotar la orientación local un cuarto de vuelta,
  sin llamar al servidor) -- el dominio sigue recibiendo únicamente
  direcciones absolutas (`Partida.mover()` no cambia), la traducción
  relativo→absoluto vive enteramente en el frontend (`direccionActual`,
  `ORDEN_HORARIO`, `girar()` en `frontend/src/laberinto/index.html`).

## Consecuencias

- `Partida.a_dict()` ya no es compatible con el frontend anterior (2D, grid 0/1) —
  intencional, ese frontend se reemplazó entero en el mismo cambio.
- Los tests de `backend/tests/laberinto/` se reescribieron para el nuevo modelo:
  usan un `random.Random(semilla)` inyectado para reproducibilidad y verifican
  propiedades generales del algoritmo (conectividad, BFS, colisión) en vez de un
  layout de paredes exacto — más robusto ante cambios futuros del generador.
- Cada conexión Socket.IO activa ahora mantiene un hilo de fondo vivo mientras dure
  la partida; se limpia solo (el `while` revisa el flag) sin necesitar matarlo a la
  fuerza.
- Pendiente explícito para el Dev 2: cuando se retome la sincronización
  multijugador (pendiente de ADR 0002), el tick del enemigo deberá emitir a todos
  los jugadores de una misma partida compartida, no solo al `sid` que la creó.
