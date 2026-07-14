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


class ConsultaUsuarios(Protocol):
    """Lo que necesita cualquier modulo para resolver el nombre de un usuario
    a partir de su id, sin conocer los detalles de como se persiste.

    Implementado por el modulo `autenticacion`. Usado por `laberinto` para
    mostrar nombres en la tabla de posiciones sin importar el dominio de
    `autenticacion` directamente (mismo patron que `VerificadorDeSesion`).
    """

    def nombres_por_id(self, ids: list) -> dict:
        """Devuelve un mapeo {id: nombre} para los ids dados que existan."""
        ...
