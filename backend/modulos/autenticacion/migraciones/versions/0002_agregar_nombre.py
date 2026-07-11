"""agregar columna nombre a usuarios

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-11
"""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "usuarios",
        sa.Column("nombre", sa.String(255), nullable=False, server_default=""),
        schema="autenticacion",
    )
    op.alter_column("usuarios", "nombre", server_default=None, schema="autenticacion")


def downgrade():
    op.drop_column("usuarios", "nombre", schema="autenticacion")
