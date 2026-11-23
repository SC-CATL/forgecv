"""视图模型：技能矩阵与证据链。"""

from __future__ import annotations

from forgecv.features.experience.service import ExperienceService
from forgecv.features.project.service import ProjectService
from forgecv.features.skill.models import SKILL_CATEGORIES, Skill
from forgecv.features.skill.schemas import EvidenceInput, SkillInput
from forgecv.features.skill.service import SkillService
from forgecv.platform.ui.kit.format import LEVEL_LABELS
from forgecv.platform.ui.qt import QtCore, Signal


class SkillViewModel(QtCore.QObject):
    """技能页状态。"""

    rows_changed = Signal(object)
    evidence_changed = Signal(object)
    sources_changed = Signal(object)
    status_changed = Signal(str)

    def __init__(
        self,
        skills: SkillService,
        projects: ProjectService,
        experiences: ExperienceService,
    ) -> None:
        """注入技能、项目与经历服务。"""
        super().__init__()
        self._skills = skills
        self._projects = projects
        self._experiences = experiences
        self._rows: list[Skill] = []

    @property
    def rows(self) -> list[Skill]:
        """当前缓存。"""
        return self._rows

    @property
    def categories(self) -> tuple[str, ...]:
        """技能分类。"""
        return SKILL_CATEGORIES

    @property
    def levels(self) -> dict[int, str]:
        """熟练度文案。"""
        return dict(LEVEL_LABELS)

    def load(self) -> None:
        """加载技能与证据可选来源。"""
        self._rows = self._skills.list_all()
        self.rows_changed.emit(self._rows)
        sources: list[tuple[str, str]] = []
        for project in self._projects.list_all():
            sources.append((f"project:{project.id}", f"项目 · {project.name}"))
        for experience in self._experiences.list_all():
            sources.append(
                (f"experience:{experience.id}", f"经历 · {experience.company} · {experience.role}")
            )
        self.sources_changed.emit(sources)
        self.status_changed.emit(f"共 {len(self._rows)} 项技能")

    def select(self, skill_id: int) -> None:
        """选中技能时刷新证据。"""
        self.evidence_changed.emit(self._skills.evidence_for(skill_id))

    def add(self, data: SkillInput) -> int | None:
        """新增技能，返回 id。"""
        result = self._skills.add(data)
        if not result.is_ok:
            self.status_changed.emit(f"新增失败：{result.error()}")
            return None
        row = result.unwrap()
        self.load()
        self.status_changed.emit("技能已新增")
        return row.id

    def update(self, skill_id: int, data: SkillInput) -> bool:
        """覆盖技能。"""
        result = self._skills.update(skill_id, data)
        if not result.is_ok:
            self.status_changed.emit(f"保存失败：{result.error()}")
            return False
        self.load()
        self.status_changed.emit("技能已保存")
        return True

    def delete(self, skill_id: int) -> bool:
        """删除技能。"""
        result = self._skills.delete(skill_id)
        if not result.is_ok:
            self.status_changed.emit(f"删除失败：{result.error()}")
            return False
        self.load()
        self.status_changed.emit("技能已删除")
        return True

    def add_evidence(
        self, skill_id: int, statement: str, metric_note: str, source: str
    ) -> bool:
        """按来源字符串新增证据。"""
        kind, _, raw_id = source.partition(":")
        try:
            source_id = int(raw_id)
        except ValueError:
            self.status_changed.emit("证据来源不合法")
            return False
        data = EvidenceInput(
            skill_id=skill_id,
            statement=statement,
            metric_note=metric_note,
            project_id=source_id if kind == "project" else None,
            experience_id=source_id if kind == "experience" else None,
        )
        result = self._skills.add_evidence(data)
        if not result.is_ok:
            self.status_changed.emit(f"新增证据失败：{result.error()}")
            return False
        self.select(skill_id)
        self.status_changed.emit("证据已添加")
        return True

    def delete_evidence(self, skill_id: int, evidence_id: int) -> bool:
        """删除证据后刷新。"""
        result = self._skills.delete_evidence(evidence_id)
        if not result.is_ok:
            self.status_changed.emit(f"删除证据失败：{result.error()}")
            return False
        self.select(skill_id)
        self.status_changed.emit("证据已删除")
        return True
