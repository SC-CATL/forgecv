"""声明基类与公共列：所有表共享的时间戳语义在此定义。"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """所有 ORM 模型的声明基类。"""


def utc_now() -> datetime:
    """统一使用 UTC 时间，避免本地时区漂移。"""
    return datetime.now(timezone.utc)


class TimestampMixin:
    """创建与更新时间，由应用写入而非数据库默认值。"""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )
