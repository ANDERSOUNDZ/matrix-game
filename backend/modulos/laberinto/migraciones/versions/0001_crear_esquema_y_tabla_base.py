"""crear esquema laberinto y tabla base de partidas

Revision ID: 0001
Revises:
Create Date: 2026-07-10
"""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE SCHEMA IF NOT EXISTS laberinto")
    op.create_table(
        "partidas",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("estado", sa.String(50), nullable=False, server_default="creada"),
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="laberinto",
    )


def downgrade():
    op.drop_table("partidas", schema="laberinto")
    op.execute("DROP SCHEMA IF EXISTS laberinto")
