"""展示用格式化：日期区间与空值占位。"""

from __future__ import annotations

from datetime import date

PLACEHOLDER = "—"


def short_date(value: date | None) -> str:
    """日期转 yyyy.MM，空值用占位符。"""
    if value is None:
        return PLACEHOLDER
    return f"{value.year:04d}.{value.month:02d}"


def period(start: date | None, end: date | None, *, is_current: bool = False) -> str:
    """时间区间文案，当前态显示「至今」。"""
    tail = "至今" if is_current else short_date(end)
    return f"{short_date(start)} – {tail}"
