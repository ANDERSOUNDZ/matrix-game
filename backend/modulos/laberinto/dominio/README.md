# dominio/ — módulo laberinto

Ya hay una implementación de referencia en `partida.py`: un grid fijo 7x7,
posición del jugador, `mover(direccion)` y condición de victoria — un
jugador por partida. El paso grande pendiente es la **sincronización
multijugador real** (varios jugadores en la misma partida, verse mover
entre sí, condición de quién llega primero) — ver ADR
`docs/decisiones/0002-flujo-conectado-de-punta-a-punta.md`.

Ver GUIA-ARQUITECTURA-Y-CALIDAD.md, Nivel 1, sección 1.2.
