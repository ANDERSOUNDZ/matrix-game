"""Conexion compartida a Postgres (ver GUIA-ARQUITECTURA-Y-CALIDAD.md,
seccion 0.5: la configuracion se lee y se valida una sola vez, aca, en vez
de fallar mas tarde en un lugar confuso).

Cada modulo usa este mismo engine para conectarse a SU PROPIO esquema
dentro de la misma base de datos fisica -- ver README.md, seccion
"Independencia de la base de datos", para el porque de este diseño.
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise SystemExit(
        "[CONFIG] Falta la variable de entorno DATABASE_URL "
        "(ver .env.example en la raiz del proyecto)."
    )

engine: Engine = create_engine(DATABASE_URL, pool_pre_ping=True)
