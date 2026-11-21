"""输入模型：简历版本与条目。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class VersionInput:
    """简历版本可编辑字段。"""

    name: str
    target_role: str = ""
    target_jd: str = ""
    template: str = "classic"
    theme: str = "light"
    is_default: bool = False


@dataclass(frozen=True, slots=True, kw_only=True)
class ItemInput:
    """版本内条目引用。"""

    item_type: str
    item_id: int
    section: str = "main"
    sort_order: int = 0
    override_text: str = ""


@dataclass(frozen=True, slots=True)
class ItemOption:
    """可加入版本的条目。"""

    key: str
    label: str
    item_type: str
    ref_id: int


@dataclass(frozen=True, slots=True)
class SelectedItem:
    """版本内已选条目。"""

    row_id: int
    key: str
    label: str
    item_type: str
    ref_id: int


@dataclass(frozen=True, slots=True)
class ItemCatalog:
    """可选与已选条目快照。"""

    available: list[ItemOption]
    selected: list[SelectedItem]
