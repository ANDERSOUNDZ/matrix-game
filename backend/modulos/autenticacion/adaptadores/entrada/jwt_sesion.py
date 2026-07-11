"""Adaptador que implementa el puerto compartido `VerificadorDeSesion`
(ver compartido/puertos.py) usando JWT, y provee la emisión de tokens que
usa `IniciarSesionUseCase`.

Es el ÚNICO lugar del proyecto que sabe cómo está armado el token -- los
demás módulos (laberinto, celebración) solo reciben una instancia que
cumple `VerificadorDeSesion` (inyectada desde compartido/app.py) y llaman a
`usuario_id_desde_token`, sin saber que hay JWT detrás.
"""

import os
import time

import jwt

SECRETO = os.environ.get("JWT_SECRET", "cambiar-esto-en-produccion")
ALGORITMO = "HS256"
EXPIRACION_SEGUNDOS = 60 * 60 * 12  # 12 horas


def emitir_token(usuario_id) -> str:
    ahora = int(time.time())
    payload = {"sub": str(usuario_id), "iat": ahora, "exp": ahora + EXPIRACION_SEGUNDOS}
    return jwt.encode(payload, SECRETO, algorithm=ALGORITMO)


class JWTVerificadorDeSesion:
    """Implementa compartido.puertos.VerificadorDeSesion."""

    def usuario_id_desde_token(self, token):
        if not token:
            return None
        try:
            payload = jwt.decode(token, SECRETO, algorithms=[ALGORITMO])
        except jwt.PyJWTError:
            return None
        return payload.get("sub")
