"""Errores propios del módulo autenticación (ver GUIA-ARQUITECTURA-Y-CALIDAD.md,
sección 0.4: excepciones con nombre propio en vez de errores genéricos).
"""


class CredencialesInvalidasError(Exception):
    """El email no existe o la contraseña no coincide."""


class EmailYaRegistradoError(Exception):
    def __init__(self, email):
        self.email = email
        super().__init__(f"Ya existe una cuenta con el email {email!r}")
