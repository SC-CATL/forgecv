"""ORM 模型：项目与项目指标。"""

from __future__ import annotations

from datetime import date

from sqlalchemy import JSON, Date, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from forgecv.platform.adapters.db.base import Base, TimestampMixin

PROJECT_STATUSES = ("online", "archived", "wip")


class Project(Base, TimestampMixin):
    """一个可被简历引用、可被标签筛选的项目。"""

    __tablename__ = "projects"
    __table_args__ = (Index("ix_projects_candidate_order", "candidate_id", "sort_order"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidate.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    direction: Mapped[str] = mapped_column(String(40), nullable=False)
    role: Mapped[str] = mapped_column(String(120), default="", nullable=False)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="wip", nullable=False)
    repo_url: Mapped[str] = mapped_column(String(300), default="", nullable=False)
    demo_url: Mapped[str] = mapped_column(String(300), default="", nullable=False)
    summary: Mapped[str] = mapped_column(Text, default="", nullable=False)
    architecture: Mapped[str] = mapped_column(Text, default="", nullable=False)
    highlights: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    challenges: Mapped[str] = mapped_column(Text, default="", nullable=False)
    retrospective: Mapped[str] = mapped_column(Text, default="", nullable=False)
    ci_status: Mapped[str] = mapped_column(String(40), default="", nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class ProjectMetric(Base, TimestampMixin):
    """项目自定义指标，键值 + 单位 + 口径说明。"""

    __tablename__ = "project_metrics"
    __table_args__ = (Index("ix_project_metrics_project_order", "project_id", "sort_order"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    key: Mapped[str] = mapped_column(String(60), nullable=False)
    value: Mapped[str] = mapped_column(String(60), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), default="", nullable=False)
    note: Mapped[str] = mapped_column(String(200), default="", nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
