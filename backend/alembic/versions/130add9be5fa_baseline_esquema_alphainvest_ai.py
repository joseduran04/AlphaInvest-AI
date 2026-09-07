"""Baseline del esquema PostgreSQL de AlphaInvest AI.

Esta revisión representa el estado estable inicial construido mediante los
scripts SQL oficiales del proyecto. No crea ni elimina objetos por sí misma.

Revision ID: 130add9be5fa
Revises:
Create Date: 2026-08-31 23:00:43.189252
"""

from collections.abc import Sequence

revision: str = "130add9be5fa"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Marca el esquema existente como baseline sin ejecutar DDL."""
    pass


def downgrade() -> None:
    """El baseline no revierte los scripts SQL que construyeron el esquema."""
    pass