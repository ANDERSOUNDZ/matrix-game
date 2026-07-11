"""Entidad de dominio: Usuario.

Reglas de negocio puras sobre la identidad y credenciales del usuario, sin
Flask, SQLAlchemy ni JWT. `werkzeug.security` es una utilidad de hashing
pura (no depende de un request HTTP), por eso se considera aceptable acá
dentro; si algún día se quiere cero dependencias de terceros en el
dominio, se puede envolver detrás de un puerto propio.

Ver GUIA-ARQUITECTURA-Y-CALIDAD.md, Nivel 1, sección 1.2.
"""

from werkzeug.security import check_password_hash, generate_password_hash

from modulos.autenticacion.dominio.errores import CredencialesInvalidasError


class Usuario:
    def __init__(self, id, email, password_hash, nombre=None):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.nombre = nombre

    @classmethod
    def registrar(cls, email, password_en_claro, nombre):
        """Crea un Usuario nuevo (sin id todavía -- lo asigna la persistencia
        al guardarlo) con la contraseña ya hasheada; nunca se guarda en
        texto plano."""
        return cls(
            id=None,
            email=email,
            password_hash=generate_password_hash(password_en_claro),
            nombre=nombre,
        )

    def verificar_password(self, password_en_claro):
        """Lanza CredencialesInvalidasError si la contraseña no coincide."""
        if not check_password_hash(self.password_hash, password_en_claro):
            raise CredencialesInvalidasError()
