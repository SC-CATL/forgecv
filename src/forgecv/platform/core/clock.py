"""时钟：时间从外部注入，便于测试。"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Protocol


class Clock(Protocol):
    """时间来源契约。"""

    def now(self) -> datetime:
        """返回当前 UTC 时间。"""
        ...


class SystemClock:
    """系统时钟，返回带时区的 UTC。"""

    def now(self) -> datetime:
        """返回当前 UTC 时间。"""
        return datetime.now(timezone.utc)


class FrozenClock:
    """测试用固定时钟。"""

    def __init__(self, moment: datetime) -> None:
        """固定到指定时刻。"""
        self._moment = moment

    def now(self) -> datetime:
        """返回固定时刻。"""
        return self._moment
