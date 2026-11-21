"""领域服务：技能与证据链规则。"""

from __future__ import annotations

from forgecv.features.skill.models import SKILL_CATEGORIES, Skill, SkillEvidence
from forgecv.features.skill.repository import SkillRepository
from forgecv.features.skill.schemas import EvidenceInput, SkillInput
from forgecv.platform.core.errors import NotFoundError, ValidationError
from forgecv.platform.core.result import Result
from forgecv.platform.core.validation import clean

LEVEL_MIN, LEVEL_MAX = 1, 4
SCORE_MIN, SCORE_MAX = 0, 100


class SkillService:
    """技能矩阵用例入口。"""

    def __init__(self, repository: SkillRepository) -> None:
        """注入仓储。"""
        self._repository = repository

    def list_all(self, category: str | None = None) -> list[Skill]:
        """按分类筛选技能。"""
        return self._repository.list_all(category)

    def categories(self) -> tuple[str, ...]:
        """可选技能分类。"""
        return SKILL_CATEGORIES

    def add(self, data: SkillInput) -> Result[Skill, ValidationError]:
        """校验后新增技能。"""
        validated = self._validate(data)
        if isinstance(validated, ValidationError):
            return Result.err(validated)
        if self._repository.find(validated.category, validated.name) is not None:
            return Result.err(ValidationError("该分类下已存在同名技能", field="name"))
        return Result.ok(self._repository.add(validated))

    def update(self, skill_id: int, data: SkillInput) -> Result[Skill, ValidationError]:
        """校验后覆盖技能。"""
        validated = self._validate(data)
        if isinstance(validated, ValidationError):
            return Result.err(validated)
        existing = self._repository.find(validated.category, validated.name)
        if existing is not None and existing.id != skill_id:
            return Result.err(ValidationError("该分类下已存在同名技能", field="name"))
        row = self._repository.update(skill_id, validated)
        if row is None:
            return Result.err(ValidationError(f"技能不存在：{skill_id}"))
        return Result.ok(row)

    def delete(self, skill_id: int) -> Result[bool, NotFoundError]:
        """删除技能。"""
        if self._repository.delete(skill_id):
            return Result.ok(True)
        return Result.err(NotFoundError(f"技能不存在：{skill_id}"))

    def evidence_for(self, skill_id: int) -> list[SkillEvidence]:
        """技能证据。"""
        return self._repository.evidence_for(skill_id)

    def add_evidence(self, data: EvidenceInput) -> Result[SkillEvidence, ValidationError]:
        """校验后新增证据。"""
        statement = clean(data.statement)
        if not statement:
            return Result.err(ValidationError("证据说明不能为空", field="statement"))
        if data.project_id is None and data.experience_id is None:
            return Result.err(ValidationError("证据必须关联项目或经历"))
        if self._repository.get(data.skill_id) is None:
            return Result.err(ValidationError(f"技能不存在：{data.skill_id}"))
        cleaned = EvidenceInput(
            skill_id=data.skill_id,
            statement=statement,
            project_id=data.project_id,
            experience_id=data.experience_id,
            metric_note=clean(data.metric_note),
            sort_order=data.sort_order,
        )
        return Result.ok(self._repository.add_evidence(cleaned))

    def delete_evidence(self, evidence_id: int) -> Result[bool, NotFoundError]:
        """删除证据。"""
        if self._repository.delete_evidence(evidence_id):
            return Result.ok(True)
        return Result.err(NotFoundError(f"证据不存在：{evidence_id}"))

    @staticmethod
    def _validate(data: SkillInput) -> SkillInput | ValidationError:
        """清洗并校验技能输入。"""
        name = clean(data.name)
        if not name:
            return ValidationError("技能名称不能为空", field="name")
        if data.category not in SKILL_CATEGORIES:
            return ValidationError(f"未知技能分类：{data.category}")
        if not LEVEL_MIN <= data.level <= LEVEL_MAX:
            return ValidationError("熟练度必须在 1-4 之间", field="level")
        if data.self_score is not None and not SCORE_MIN <= data.self_score <= SCORE_MAX:
            return ValidationError("自评分必须在 0-100 之间", field="self_score")
        if data.years is not None and data.years < 0:
            return ValidationError("使用年限不能为负", field="years")
        return SkillInput(
            name=name,
            category=data.category,
            level=data.level,
            years=data.years,
            self_score=data.self_score,
            notes=data.notes.strip(),
            sort_order=data.sort_order,
        )
