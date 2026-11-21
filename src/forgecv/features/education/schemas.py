"""输入模型：学历。"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

DEGREE_LEVELS = ("专科", "本科", "硕士", "博士", "其他")


@dataclass(frozen=True, slots=True, kw_only=True)
class EducationInput:
    """学历可编辑字段。"""

    school: str
    degree_level: str = "本科"
    major: str = ""
    start_date: date | None = None
    end_date: date | None = None
    is_current: bool = False
    gpa: str = ""
    courses: list[str] = field(default_factory=list)
    thesis: str = ""
    notes: str = ""
    sort_order: int = 0
