"""输入模型：工作经历。"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True, slots=True, kw_only=True)
class ExperienceInput:
    """工作经历可编辑字段。"""

    company: str
    role: str
    location: str = ""
    start_date: date | None = None
    end_date: date | None = None
    is_current: bool = False
    summary: str = ""
    highlights: list[str] = field(default_factory=list)
    sort_order: int = 0
