"""输入模型：技能与证据。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class SkillInput:
    """技能可编辑字段。"""

    name: str
    category: str = "语言"
    level: int = 2
    years: float | None = None
    self_score: int | None = None
    notes: str = ""
    sort_order: int = 0


@dataclass(frozen=True, slots=True, kw_only=True)
class EvidenceInput:
    """技能证据输入。"""

    skill_id: int
    statement: str
    project_id: int | None = None
    experience_id: int | None = None
    metric_note: str = ""
    sort_order: int = 0
