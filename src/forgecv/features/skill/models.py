"""ORM 模型：技术技能与证据链。"""

from __future__ import annotations

from sqlalchemy import Float, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from forgecv.platform.adapters.db.base import Base, TimestampMixin

SKILL_CATEGORIES = ("语言", "框架", "数据库", "工具链", "运维", "软技能")


class Skill(Base, TimestampMixin):
    """一条技术能力，熟练度与自评分分开记录。"""

    __tablename__ = "skills"
    __table_args__ = (
        UniqueConstraint("candidate_id", "category", "name", name="uq_skills_candidate_name"),
        Index("ix_skills_candidate_order", "candidate_id", "category", "sort_order"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidate.id", ondelete="CASCADE"), nullable=False
    )
    category: Mapped[str] = mapped_column(String(40), nullable=False)
    name: Mapped[str] = mapped_column(String(60), nullable=False)
    level: Mapped[int] = mapped_column(Integer, default=2, nullable=False)
    years: Mapped[float | None] = mapped_column(Float, nullable=True)
    self_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="", nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class SkillEvidence(Base, TimestampMixin):
    """技能到项目或经历的举证，至少有一个来源。"""

    __tablename__ = "skill_evidence"
    __table_args__ = (Index("ix_skill_evidence_project", "project_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    skill_id: Mapped[int] = mapped_column(
        ForeignKey("skills.id", ondelete="CASCADE"), index=True, nullable=False
    )
    project_id: Mapped[int | None] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=True
    )
    experience_id: Mapped[int | None] = mapped_column(
        ForeignKey("experiences.id", ondelete="CASCADE"), nullable=True
    )
    statement: Mapped[str] = mapped_column(Text, nullable=False)
    metric_note: Mapped[str] = mapped_column(String(200), default="", nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
