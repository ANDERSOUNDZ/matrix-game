"""Aplica las migraciones de Alembic de los 3 modulos, en orden.

Es el UNICO lugar que "conoce" a los 3 modulos desde el lado de la base de
datos (ver README.md, seccion "Independencia de la base de datos"). Cada
modulo tiene su propio esquema y su propia tabla de version, asi que este
script simplemente corre `alembic upgrade head` en cada carpeta de
migraciones, en el orden de dependencia acordado (autenticacion antes que
laberinto, porque laberinto podria referenciar usuarios; celebracion al
final porque podria referenciar usuarios tambien).
"""

import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
MODULOS_EN_ORDEN = ["autenticacion", "laberinto", "celebracion"]


def migrar(modulo: str) -> None:
    carpeta = RAIZ / "modulos" / modulo / "migraciones"
    print(f"\n[MIGRAR] {modulo} ({carpeta})")
    resultado = subprocess.run(
        ["alembic", "-c", "alembic.ini", "upgrade", "head"],
        cwd=carpeta,
    )
    if resultado.returncode != 0:
        print(f"[MIGRAR] Fallo la migracion de {modulo}")
        sys.exit(resultado.returncode)


def main() -> None:
    for modulo in MODULOS_EN_ORDEN:
        migrar(modulo)
    print("\n[MIGRAR] Listo: los 3 modulos migrados.")


if __name__ == "__main__":
    main()
