"""ORM 模型：技术标签与项目关联。"""

from __future__ import annotations

from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from forgecv.platform.adapters.db.base import Base, TimestampMixin

TAG_DIMENSIONS = ("language", "domain", "practice", "toolchain")
DIMENSION_LABELS = {
    "language": "语言",
    "domain": "领域",
    "practice": "工程实践",
    "toolchain": "工具链",
}


class Tag(Base, TimestampMixin):
    """四维技术标签，名称全局唯一。"""

    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    dimension: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    color: Mapped[str] = mapped_column(String(16), default="", nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class ProjectTag(Base):
    """项目与标签的多对多关联。"""

    __tablename__ = "project_tags"
    __table_args__ = (Index("ix_project_tags_tag", "tag_id"),)

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True
    )
    tag_id: Mapped[int] = mapped_column(
        ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
    )
