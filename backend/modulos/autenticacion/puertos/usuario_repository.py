"""Puerto de salida: lo que el módulo autenticación necesita para persistir
un Usuario, sin decir cómo. Ver GUIA-ARQUITECTURA-Y-CALIDAD.md, Nivel 1,
secciones 1.2/1.3.
"""

from typing import Optional, Protocol

from modulos.autenticacion.dominio.usuario import Usuario


class UsuarioRepository(Protocol):
    def obtener_por_email(self, email: str) -> Optional[Usuario]: ...

    def obtener_por_id(self, id: int) -> Optional[Usuario]: ...

    def guardar(self, usuario: Usuario) -> Usuario:
        """Inserta si usuario.id es None, actualiza si no. Devuelve el
        usuario con el id ya asignado."""
        ...
