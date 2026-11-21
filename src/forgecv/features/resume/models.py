"""ORM 模型：简历版本、条目编排与快照。"""

from __future__ import annotations

from typing import Any

from sqlalchemy import JSON, Boolean, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from forgecv.platform.adapters.db.base import Base, TimestampMixin

ITEM_TYPES = ("education", "experience", "project", "skill", "certificate")
TEMPLATES = ("classic", "compact")
RESUME_THEMES = ("light", "dark", "system")


class ResumeVersion(Base, TimestampMixin):
    """面向某个岗位的一份简历编排。"""

    __tablename__ = "resume_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidate.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    target_role: Mapped[str] = mapped_column(String(120), default="", nullable=False)
    target_jd: Mapped[str] = mapped_column(Text, default="", nullable=False)
    template: Mapped[str] = mapped_column(String(40), default="classic", nullable=False)
    theme: Mapped[str] = mapped_column(String(40), default="light", nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class ResumeItem(Base, TimestampMixin):
    """版本内的一条引用，多态指向其他切片的数据。"""

    __tablename__ = "resume_items"
    __table_args__ = (
        Index("ix_resume_items_version_order", "version_id", "sort_order"),
        Index("ix_resume_items_target", "item_type", "item_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    version_id: Mapped[int] = mapped_column(
        ForeignKey("resume_versions.id", ondelete="CASCADE"), nullable=False
    )
    item_type: Mapped[str] = mapped_column(String(20), nullable=False)
    item_id: Mapped[int] = mapped_column(Integer, nullable=False)
    section: Mapped[str] = mapped_column(String(20), default="main", nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    override_text: Mapped[str] = mapped_column(Text, default="", nullable=False)


class Snapshot(Base, TimestampMixin):
    """版本快照：完整渲染数据的 JSON 副本。"""

    __tablename__ = "snapshots"
    __table_args__ = (Index("ix_snapshots_version_time", "version_id", "created_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    version_id: Mapped[int] = mapped_column(
        ForeignKey("resume_versions.id", ondelete="CASCADE"), nullable=False
    )
    label: Mapped[str] = mapped_column(String(80), default="", nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
