"""时间轴事件模型。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class TimelineEvent:
    """统一时间轴上的一条事件。"""

    kind: str
    title: str
    subtitle: str
    start: date | None
    end: date | None
    is_current: bool


@dataclass(frozen=True, slots=True)
class TimelineData:
    """事件与冲突提示。"""

    events: list[TimelineEvent]
    warnings: list[str]
