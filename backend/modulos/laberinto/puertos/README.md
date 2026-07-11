# puertos/ — módulo laberinto

Ya hay una implementación de referencia: `partida_repository.py`
(`PartidaRepository`, implementado en `adaptadores/persistencia/memoria.py`).

Este módulo **consume** el puerto compartido `VerificadorDeSesion`
(`backend/compartido/puertos.py`, implementado por `autenticacion`) —
inyectado en `adaptadores/entrada/websocket.py`, sin importar el módulo
`autenticacion` directamente.

Ver GUIA-ARQUITECTURA-Y-CALIDAD.md, Nivel 1, secciones 1.2 y 1.5.
