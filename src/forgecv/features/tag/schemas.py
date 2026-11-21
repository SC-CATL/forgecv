"""输入模型：标签。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class TagInput:
    """标签可编辑字段。"""

    name: str
    dimension: str = "language"
    color: str = ""
    description: str = ""
    sort_order: int = 0
