"""领域服务：工作经历校验与用例。"""

from __future__ import annotations

from forgecv.features.experience.models import Experience
from forgecv.features.experience.repository import ExperienceRepository
from forgecv.features.experience.schemas import ExperienceInput
from forgecv.platform.core.errors import NotFoundError, ValidationError
from forgecv.platform.core.result import Result
from forgecv.platform.core.validation import clean, period_error


class ExperienceService:
    """工作经历用例入口。"""

    def __init__(self, repository: ExperienceRepository) -> None:
        """注入仓储。"""
        self._repository = repository

    def list_all(self) -> list[Experience]:
        """全部经历。"""
        return self._repository.list_all()

    def add(self, data: ExperienceInput) -> Result[Experience, ValidationError]:
        """校验后新增。"""
        validated = self._validate(data)
        if isinstance(validated, ValidationError):
            return Result.err(validated)
        return Result.ok(self._repository.add(validated))

    def update(
        self, experience_id: int, data: ExperienceInput
    ) -> Result[Experience, ValidationError]:
        """校验后覆盖。"""
        validated = self._validate(data)
        if isinstance(validated, ValidationError):
            return Result.err(validated)
        row = self._repository.update(experience_id, validated)
        if row is None:
            return Result.err(ValidationError(f"经历不存在：{experience_id}"))
        return Result.ok(row)

    def delete(self, experience_id: int) -> Result[bool, NotFoundError]:
        """删除经历。"""
        if self._repository.delete(experience_id):
            return Result.ok(True)
        return Result.err(NotFoundError(f"经历不存在：{experience_id}"))

    @staticmethod
    def _validate(data: ExperienceInput) -> ExperienceInput | ValidationError:
        """清洗并校验输入。"""
        company = clean(data.company)
        role = clean(data.role)
        if not company:
            return ValidationError("公司名称不能为空", field="company")
        if not role:
            return ValidationError("职位不能为空", field="role")
        if data.start_date is None:
            return ValidationError("请填写开始时间", field="start_date")
        message = period_error(data.start_date, data.end_date, is_current=data.is_current)
        if message is not None:
            return ValidationError(message)
        highlights = [item.strip() for item in data.highlights if item.strip()]
        return ExperienceInput(
            company=company,
            role=role,
            location=clean(data.location),
            start_date=data.start_date,
            end_date=data.end_date,
            is_current=data.is_current,
            summary=data.summary.strip(),
            highlights=highlights,
            sort_order=data.sort_order,
        )
