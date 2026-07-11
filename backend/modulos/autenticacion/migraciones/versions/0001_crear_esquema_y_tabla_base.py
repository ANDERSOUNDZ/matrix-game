"""crear esquema autenticacion y tabla base de usuarios

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
    op.execute("CREATE SCHEMA IF NOT EXISTS autenticacion")
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="autenticacion",
    )


def downgrade():
    op.drop_table("usuarios", schema="autenticacion")
    op.execute("DROP SCHEMA IF EXISTS autenticacion")
