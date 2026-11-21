"""输入模型：项目与指标。"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True, slots=True, kw_only=True)
class MetricInput:
    """项目指标输入。"""

    key: str
    value: str
    unit: str = ""
    note: str = ""
    sort_order: int = 0


@dataclass(frozen=True, slots=True, kw_only=True)
class ProjectInput:
    """项目可编辑字段。"""

    name: str
    direction: str = ""
    role: str = ""
    start_date: date | None = None
    end_date: date | None = None
    status: str = "wip"
    repo_url: str = ""
    demo_url: str = ""
    summary: str = ""
    architecture: str = ""
    highlights: list[str] = field(default_factory=list)
    challenges: str = ""
    retrospective: str = ""
    ci_status: str = ""
    sort_order: int = 0
    metrics: list[MetricInput] = field(default_factory=list)
