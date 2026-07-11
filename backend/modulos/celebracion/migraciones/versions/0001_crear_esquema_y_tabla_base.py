"""crear esquema celebracion y tabla base de fotos compartidas

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
    op.execute("CREATE SCHEMA IF NOT EXISTS celebracion")
    op.create_table(
        "fotos_compartidas",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("usuario_id", sa.Integer, nullable=False),
        sa.Column("url", sa.String(500), nullable=True),
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="celebracion",
    )


def downgrade():
    op.drop_table("fotos_compartidas", schema="celebracion")
    op.execute("DROP SCHEMA IF EXISTS celebracion")
