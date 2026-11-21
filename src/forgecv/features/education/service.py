"""领域服务：学历校验与用例。"""

from __future__ import annotations

from forgecv.features.education.models import Education
from forgecv.features.education.repository import EducationRepository
from forgecv.features.education.schemas import DEGREE_LEVELS, EducationInput
from forgecv.platform.core.errors import NotFoundError, ValidationError
from forgecv.platform.core.result import Result
from forgecv.platform.core.validation import clean, period_error


class EducationService:
    """学历节点用例入口。"""

    def __init__(self, repository: EducationRepository) -> None:
        """注入仓储。"""
        self._repository = repository

    def list_all(self) -> list[Education]:
        """全部学历。"""
        return self._repository.list_all()

    def add(self, data: EducationInput) -> Result[Education, ValidationError]:
        """校验后新增。"""
        validated = self._validate(data)
        if isinstance(validated, ValidationError):
            return Result.err(validated)
        return Result.ok(self._repository.add(validated))

    def update(self, education_id: int, data: EducationInput) -> Result[Education, ValidationError]:
        """校验后覆盖。"""
        validated = self._validate(data)
        if isinstance(validated, ValidationError):
            return Result.err(validated)
        row = self._repository.update(education_id, validated)
        if row is None:
            return Result.err(ValidationError(f"学历不存在：{education_id}"))
        return Result.ok(row)

    def delete(self, education_id: int) -> Result[bool, NotFoundError]:
        """删除学历。"""
        if self._repository.delete(education_id):
            return Result.ok(True)
        return Result.err(NotFoundError(f"学历不存在：{education_id}"))

    def reorder(self, ordered_ids: list[int]) -> None:
        """按给定 id 顺序重排。"""
        self._repository.reorder(ordered_ids)

    @staticmethod
    def _validate(data: EducationInput) -> EducationInput | ValidationError:
        """把输入清洗成可入库的值，或返回错误。"""
        school = clean(data.school)
        if not school:
            return ValidationError("院校名称不能为空", field="school")
        if data.degree_level not in DEGREE_LEVELS:
            return ValidationError(f"未知学历层次：{data.degree_level}")
        if data.start_date is None:
            return ValidationError("请填写入学时间", field="start_date")
        message = period_error(data.start_date, data.end_date, is_current=data.is_current)
        if message is not None:
            return ValidationError(message)
        courses = [course.strip() for course in data.courses if course.strip()]
        return EducationInput(
            school=school,
            degree_level=data.degree_level,
            major=clean(data.major),
            start_date=data.start_date,
            end_date=data.end_date,
            is_current=data.is_current,
            gpa=clean(data.gpa),
            courses=courses,
            thesis=clean(data.thesis),
            notes=data.notes.strip(),
            sort_order=data.sort_order,
        )
