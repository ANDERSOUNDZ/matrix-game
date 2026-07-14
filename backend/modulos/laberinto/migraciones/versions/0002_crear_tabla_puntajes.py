"""crear tabla de puntajes (mejor tiempo por usuario)

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-13
"""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "puntajes",
        sa.Column("usuario_id", sa.String(64), primary_key=True),
        sa.Column("mejor_tiempo_segundos", sa.Float, nullable=False),
        sa.Column("actualizado_en", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="laberinto",
    )


def downgrade():
    op.drop_table("puntajes", schema="laberinto")
