"""领域服务：标签校验与项目打标。"""

from __future__ import annotations

from forgecv.features.tag.models import DIMENSION_LABELS, TAG_DIMENSIONS, Tag
from forgecv.features.tag.repository import TagRepository
from forgecv.features.tag.schemas import TagInput
from forgecv.platform.core.errors import NotFoundError, ValidationError
from forgecv.platform.core.result import Result
from forgecv.platform.core.validation import clean


class TagService:
    """标签库用例入口。"""

    def __init__(self, repository: TagRepository) -> None:
        """注入仓储。"""
        self._repository = repository

    def list_all(self, dimension: str | None = None) -> list[Tag]:
        """按维度筛选标签。"""
        return self._repository.list_all(dimension)

    def dimensions(self) -> dict[str, str]:
        """维度英文名到中文名的映射。"""
        return dict(DIMENSION_LABELS)

    def create(self, data: TagInput) -> Result[Tag, ValidationError]:
        """校验后新增标签。"""
        validated = self._validate(data)
        if isinstance(validated, ValidationError):
            return Result.err(validated)
        if self._repository.find_by_name(validated.name) is not None:
            return Result.err(ValidationError("标签已存在", field="name"))
        return Result.ok(self._repository.add(validated))

    def update(self, tag_id: int, data: TagInput) -> Result[Tag, ValidationError]:
        """校验后覆盖标签。"""
        validated = self._validate(data)
        if isinstance(validated, ValidationError):
            return Result.err(validated)
        existing = self._repository.find_by_name(validated.name)
        if existing is not None and existing.id != tag_id:
            return Result.err(ValidationError("标签已存在", field="name"))
        row = self._repository.update(tag_id, validated)
        if row is None:
            return Result.err(ValidationError(f"标签不存在：{tag_id}"))
        return Result.ok(row)

    def delete(self, tag_id: int) -> Result[bool, NotFoundError]:
        """删除标签。"""
        if self._repository.delete(tag_id):
            return Result.ok(True)
        return Result.err(NotFoundError(f"标签不存在：{tag_id}"))

    def tags_for_project(self, project_id: int) -> list[Tag]:
        """项目已打标签。"""
        return self._repository.tags_for_project(project_id)

    def set_project_tags(self, project_id: int, tag_ids: list[int]) -> None:
        """整体重设项目标签。"""
        self._repository.replace_project_tags(project_id, tag_ids)

    @staticmethod
    def _validate(data: TagInput) -> TagInput | ValidationError:
        """清洗并校验标签输入。"""
        name = clean(data.name)
        if not name:
            return ValidationError("标签名称不能为空", field="name")
        if data.dimension not in TAG_DIMENSIONS:
            return ValidationError(f"未知标签维度：{data.dimension}")
        color = clean(data.color)
        if color and not color.startswith("#"):
            return ValidationError("颜色需以 # 开头", field="color")
        return TagInput(
            name=name,
            dimension=data.dimension,
            color=color,
            description=data.description.strip(),
            sort_order=data.sort_order,
        )
