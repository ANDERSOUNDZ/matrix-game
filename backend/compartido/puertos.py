"""Puertos que cruzan MAS DE UN modulo (ver GUIA-ARQUITECTURA-Y-CALIDAD.md,
Nivel 1). Los puertos internos de un solo modulo viven dentro de
modulos/<nombre>/puertos/ -- estos son distintos: son contratos que varios
modulos necesitan conocer, por eso viven en compartido/.

Cualquier cambio aca se acuerda entre los 3 desarrolladores antes de
mergear.
"""

from typing import Optional, Protocol


class VerificadorDeSesion(Protocol):
    """Lo que necesita cualquier modulo para saber quien es el usuario actual,
    sin conocer los detalles de como se emite o valida el token de sesion.

    Implementado por el modulo `autenticacion` (Dev 1). Los modulos
    `laberinto` y `celebracion` dependen de ESTA interfaz, nunca del
    dominio de `autenticacion` directamente.
    """

    def usuario_id_desde_token(self, token: str) -> Optional[str]:
        """Devuelve el id del usuario si el token es valido, o None si no lo es."""
        ...
