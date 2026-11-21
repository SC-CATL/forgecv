"""概览数据结构。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TagCount:
    """标签使用次数。"""

    name: str
    count: int


@dataclass(frozen=True, slots=True)
class DashboardData:
    """概览页一次性快照。"""

    counts: dict[str, int]
    radar: dict[str, int]
    tags: dict[str, list[TagCount]]
    hints: list[str]
