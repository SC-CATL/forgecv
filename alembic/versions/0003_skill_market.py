"""skill market tag

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-23 00:00:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """给技能表补市场来源与认证标签。"""
    with op.batch_alter_table("skills") as batch:
        batch.add_column(
            sa.Column("market_key", sa.String(length=60), nullable=False, server_default="")
        )
        batch.add_column(
            sa.Column("market_tag", sa.String(length=40), nullable=False, server_default="")
        )
        batch.create_index("ix_skills_market_key", ["market_key"])


def downgrade() -> None:
    """移除市场字段与索引。"""
    with op.batch_alter_table("skills") as batch:
        batch.drop_index("ix_skills_market_key")
        batch.drop_column("market_tag")
        batch.drop_column("market_key")
