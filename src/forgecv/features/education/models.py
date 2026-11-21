"""ORM 模型：学历节点。"""

from __future__ import annotations

from datetime import date

from sqlalchemy import JSON, Boolean, Date, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from forgecv.platform.adapters.db.base import Base, TimestampMixin


class Education(Base, TimestampMixin):
    """一段学历经历，按 sort_order 与时间组成时间轴。"""

    __tablename__ = "educations"
    __table_args__ = (Index("ix_educations_candidate_order", "candidate_id", "sort_order"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidate.id", ondelete="CASCADE"), index=True, nullable=False
    )
    school: Mapped[str] = mapped_column(String(120), nullable=False)
    degree_level: Mapped[str] = mapped_column(String(20), nullable=False)
    major: Mapped[str] = mapped_column(String(120), default="", nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    gpa: Mapped[str] = mapped_column(String(32), default="", nullable=False)
    courses: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    thesis: Mapped[str] = mapped_column(String(300), default="", nullable=False)
    notes: Mapped[str] = mapped_column(Text, default="", nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
