"""Adaptador de salida: implementa UsuarioRepository contra Postgres
(esquema `autenticacion`, tabla `usuarios`, creada por la migración 0001).

También implementa el puerto compartido `ConsultaUsuarios`
(compartido/puertos.py) -- misma tabla, otra consulta, no amerita una clase
aparte.
"""

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from compartido.db import engine
from modulos.autenticacion.dominio.errores import EmailYaRegistradoError
from modulos.autenticacion.dominio.usuario import Usuario


class UsuarioRepositoryPostgres:
    def obtener_por_email(self, email):
        with engine.connect() as conexion:
            fila = conexion.execute(
                text(
                    "SELECT id, email, password_hash, nombre FROM autenticacion.usuarios "
                    "WHERE email = :email"
                ),
                {"email": email},
            ).fetchone()
        if fila is None:
            return None
        return Usuario(id=fila.id, email=fila.email, password_hash=fila.password_hash, nombre=fila.nombre)

    def obtener_por_id(self, id):
        with engine.connect() as conexion:
            fila = conexion.execute(
                text(
                    "SELECT id, email, password_hash, nombre FROM autenticacion.usuarios "
                    "WHERE id = :id"
                ),
                {"id": id},
            ).fetchone()
        if fila is None:
            return None
        return Usuario(id=fila.id, email=fila.email, password_hash=fila.password_hash, nombre=fila.nombre)

    def nombres_por_id(self, ids):
        """Implementa compartido.puertos.ConsultaUsuarios."""
        if not ids:
            return {}
        ids_enteros = [int(id_) for id_ in ids]
        with engine.connect() as conexion:
            filas = conexion.execute(
                text("SELECT id, nombre FROM autenticacion.usuarios WHERE id = ANY(:ids)"),
                {"ids": ids_enteros},
            ).fetchall()
        return {str(fila.id): fila.nombre for fila in filas}

    def guardar(self, usuario):
        with engine.begin() as conexion:
            if usuario.id is None:
                try:
                    fila = conexion.execute(
                        text(
                            "INSERT INTO autenticacion.usuarios (email, password_hash, nombre) "
                            "VALUES (:email, :password_hash, :nombre) RETURNING id"
                        ),
                        {
                            "email": usuario.email,
                            "password_hash": usuario.password_hash,
                            "nombre": usuario.nombre,
                        },
                    ).fetchone()
                except IntegrityError as error:
                    raise EmailYaRegistradoError(usuario.email) from error
                usuario.id = fila.id
            else:
                conexion.execute(
                    text(
                        "UPDATE autenticacion.usuarios SET email = :email, "
                        "password_hash = :password_hash, nombre = :nombre WHERE id = :id"
                    ),
                    {
                        "email": usuario.email,
                        "password_hash": usuario.password_hash,
                        "nombre": usuario.nombre,
                        "id": usuario.id,
                    },
                )
        return usuario
