"""领域服务：简历版本编排规则。"""

from __future__ import annotations

from typing import Any

from forgecv.features.resume.models import (
    ITEM_TYPES,
    RESUME_THEMES,
    TEMPLATES,
    ResumeItem,
    ResumeVersion,
    Snapshot,
)
from forgecv.features.resume.repository import ResumeRepository
from forgecv.features.resume.schemas import ItemInput, VersionInput
from forgecv.platform.core.errors import NotFoundError, ValidationError
from forgecv.platform.core.result import Result
from forgecv.platform.core.validation import clean


class ResumeService:
    """简历版本用例入口。"""

    def __init__(self, repository: ResumeRepository) -> None:
        """注入仓储。"""
        self._repository = repository

    def versions(self) -> list[ResumeVersion]:
        """全部版本。"""
        return self._repository.versions()

    def create_version(self, data: VersionInput) -> Result[ResumeVersion, ValidationError]:
        """校验后新建版本。"""
        validated = self._validate_version(data)
        if isinstance(validated, ValidationError):
            return Result.err(validated)
        return Result.ok(self._repository.add_version(validated))

    def update_version(
        self, version_id: int, data: VersionInput
    ) -> Result[ResumeVersion, ValidationError]:
        """校验后覆盖版本。"""
        validated = self._validate_version(data)
        if isinstance(validated, ValidationError):
            return Result.err(validated)
        row = self._repository.update_version(version_id, validated)
        if row is None:
            return Result.err(ValidationError(f"版本不存在：{version_id}"))
        return Result.ok(row)

    def delete_version(self, version_id: int) -> Result[bool, NotFoundError]:
        """删除版本。"""
        if self._repository.delete_version(version_id):
            return Result.ok(True)
        return Result.err(NotFoundError(f"版本不存在：{version_id}"))

    def items(self, version_id: int) -> list[ResumeItem]:
        """版本内条目。"""
        return self._repository.items(version_id)

    def add_item(
        self, version_id: int, data: ItemInput
    ) -> Result[ResumeItem, ValidationError]:
        """向版本追加条目引用。"""
        if self._repository.get_version(version_id) is None:
            return Result.err(ValidationError(f"版本不存在：{version_id}"))
        if data.item_type not in ITEM_TYPES:
            return Result.err(ValidationError(f"未知条目类型：{data.item_type}"))
        if data.item_id <= 0:
            return Result.err(ValidationError("条目 id 不合法"))
        for existing in self._repository.items(version_id):
            if existing.item_type == data.item_type and existing.item_id == data.item_id:
                return Result.err(ValidationError("该条目已加入此版本"))
        cleaned = ItemInput(
            item_type=data.item_type,
            item_id=data.item_id,
            section=clean(data.section) or "main",
            sort_order=data.sort_order,
            override_text=data.override_text.strip(),
        )
        return Result.ok(self._repository.add_item(version_id, cleaned))

    def remove_item(self, item_id: int) -> Result[bool, NotFoundError]:
        """移除条目引用。"""
        if self._repository.remove_item(item_id):
            return Result.ok(True)
        return Result.err(NotFoundError(f"条目不存在：{item_id}"))

    def reorder_items(self, version_id: int, ordered_ids: list[int]) -> None:
        """重排版本条目。"""
        self._repository.reorder_items(version_id, ordered_ids)

    def create_snapshot(
        self, version_id: int, label: str, payload: dict[str, Any]
    ) -> Result[Snapshot, ValidationError]:
        """保存快照。"""
        if self._repository.get_version(version_id) is None:
            return Result.err(ValidationError(f"版本不存在：{version_id}"))
        return Result.ok(self._repository.add_snapshot(version_id, clean(label), payload))

    def snapshots(self, version_id: int) -> list[Snapshot]:
        """版本快照。"""
        return self._repository.snapshots(version_id)

    @staticmethod
    def _validate_version(data: VersionInput) -> VersionInput | ValidationError:
        """清洗并校验版本输入。"""
        name = clean(data.name)
        if not name:
            return ValidationError("版本名称不能为空", field="name")
        if data.template not in TEMPLATES:
            return ValidationError(f"未知导出模板：{data.template}")
        if data.theme not in RESUME_THEMES:
            return ValidationError(f"未知主题：{data.theme}")
        return VersionInput(
            name=name,
            target_role=clean(data.target_role),
            target_jd=data.target_jd.strip(),
            template=data.template,
            theme=data.theme,
            is_default=data.is_default,
        )
