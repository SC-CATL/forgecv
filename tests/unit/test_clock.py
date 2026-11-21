"""时钟实现。"""

from __future__ import annotations

from datetime import datetime, timezone

from forgecv.platform.core.clock import FrozenClock, SystemClock


def test_system_clock_is_utc_aware() -> None:
    """系统时钟必须带时区。"""
    moment = SystemClock().now()
    assert moment.tzinfo is not None
    assert moment.utcoffset() is not None


def test_frozen_clock_returns_fixed_moment() -> None:
    """固定时钟不随时间变化。"""
    moment = datetime(2026, 1, 1, tzinfo=timezone.utc)
    clock = FrozenClock(moment)
    assert clock.now() == moment
    assert clock.now() == clock.now()
