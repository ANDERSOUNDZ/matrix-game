# puertos/ — módulo autenticación

Ya hay una implementación de referencia: `usuario_repository.py`
(`UsuarioRepository`, implementado en `adaptadores/persistencia/postgres.py`).

Este módulo también **implementa** el puerto compartido `VerificadorDeSesion`
(definido en `backend/compartido/puertos.py`) en
`adaptadores/entrada/jwt_sesion.py` — porque otros módulos lo necesitan.

Ver `GUIA-ARQUITECTURA-Y-CALIDAD.md`, Nivel 1, secciones 1.2 y 1.5.
