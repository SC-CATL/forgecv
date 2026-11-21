"""视图模型：简历版本编排、预览、健康度与 JD 分析。"""

from __future__ import annotations

from forgecv.features.education.service import EducationService
from forgecv.features.experience.service import ExperienceService
from forgecv.features.profile.service import ProfileService
from forgecv.features.project.service import ProjectService
from forgecv.features.resume.checks import ResumeCheckService
from forgecv.features.resume.jd import analyze
from forgecv.features.resume.models import ResumeItem, ResumeVersion
from forgecv.features.resume.render import ResumeRenderer, render_text
from forgecv.features.resume.schemas import (
    ItemCatalog,
    ItemInput,
    ItemOption,
    SelectedItem,
    VersionInput,
)
from forgecv.features.resume.service import ResumeService
from forgecv.features.skill.service import SkillService
from forgecv.features.tag.service import TagService
from forgecv.platform.ui.qt import QtCore, Signal


class ResumeViewModel(QtCore.QObject):
    """简历版本页状态。"""

    versions_changed = Signal(object)
    version_changed = Signal(object)
    catalog_changed = Signal(object)
    preview_changed = Signal(str)
    checks_changed = Signal(object)
    jd_changed = Signal(object)
    status_changed = Signal(str)

    def __init__(
        self,
        *,
        resume: ResumeService,
        renderer: ResumeRenderer,
        checks: ResumeCheckService,
        educations: EducationService,
        experiences: ExperienceService,
        projects: ProjectService,
        skills: SkillService,
        profile: ProfileService,
        tags: TagService,
    ) -> None:
        """注入版本服务、渲染器与条目来源。"""
        super().__init__()
        self._resume = resume
        self._renderer = renderer
        self._checks = checks
        self._educations = educations
        self._experiences = experiences
        self._projects = projects
        self._skills = skills
        self._profile = profile
        self._tags = tags
        self._versions: list[ResumeVersion] = []
        self._current: ResumeVersion | None = None

    @property
    def current(self) -> ResumeVersion | None:
        """当前版本。"""
        return self._current

    def load(self) -> None:
        """加载版本列表并选中第一个。"""
        self._versions = self._resume.versions()
        self.versions_changed.emit(self._versions)
        if not self._versions:
            self._current = None
            self.preview_changed.emit("还没有简历版本，先新建一个。")
            self.catalog_changed.emit(ItemCatalog([], []))
            self.status_changed.emit("共 0 个版本")
            return
        keep = self._current.id if self._current is not None else None
        target = next(
            (row for row in self._versions if row.id == keep), self._versions[0]
        )
        self.select(target.id)

    def select(self, version_id: int) -> None:
        """切换版本并刷新全部面板。"""
        version = next((row for row in self._versions if row.id == version_id), None)
        if version is None:
            version = self._resume.versions()[0]
        self._current = version
        self.version_changed.emit(version)
        self._emit_catalog(version)
        self.refresh()

    def create(self, data: VersionInput) -> bool:
        """新建版本并选中。"""
        result = self._resume.create_version(data)
        if not result.is_ok:
            self.status_changed.emit(f"新建版本失败：{result.error()}")
            return False
        self._current = result.unwrap()
        self.load()
        self.status_changed.emit("版本已创建")
        return True

    def update(self, data: VersionInput) -> bool:
        """更新当前版本。"""
        if self._current is None:
            return False
        result = self._resume.update_version(self._current.id, data)
        if not result.is_ok:
            self.status_changed.emit(f"保存失败：{result.error()}")
            return False
        self.load()
        self.status_changed.emit("版本已保存")
        return True

    def delete_current(self) -> bool:
        """删除当前版本。"""
        if self._current is None:
            return False
        result = self._resume.delete_version(self._current.id)
        if not result.is_ok:
            self.status_changed.emit(f"删除失败：{result.error()}")
            return False
        self._current = None
        self.load()
        self.status_changed.emit("版本已删除")
        return True

    def toggle_item(self, key: str, checked: bool) -> None:
        """勾选或取消一条可用条目。"""
        if self._current is None:
            return
        item_type, _, raw_id = key.partition(":")
        if checked:
            result = self._resume.add_item(
                self._current.id,
                ItemInput(item_type=item_type, item_id=int(raw_id)),
            )
            if not result.is_ok:
                self.status_changed.emit(f"{result.error()}")
                return
        else:
            row = self._find_selected(item_type, int(raw_id))
            if row is not None:
                self._resume.remove_item(row.id)
        self._emit_catalog(self._current)
        self.refresh()

    def move_item(self, row_id: int, delta: int) -> None:
        """在已选列表内上移或下移。"""
        if self._current is None:
            return
        rows = self._resume.items(self._current.id)
        index = next((pos for pos, row in enumerate(rows) if row.id == row_id), -1)
        target = index + delta
        if index < 0 or target < 0 or target >= len(rows):
            return
        ordered = [row.id for row in rows]
        ordered[index], ordered[target] = ordered[target], ordered[index]
        self._resume.reorder_items(self._current.id, ordered)
        self._emit_catalog(self._current)
        self.refresh()

    def refresh(self) -> None:
        """重建预览、健康度与 JD 报告。"""
        if self._current is None:
            return
        document = self._renderer.build(self._current)
        self.preview_changed.emit(render_text(document))
        self.checks_changed.emit(self._checks.issues(document))
        self.jd_changed.emit(analyze(self._current.target_jd, self._known_terms()))

    def analyze_jd(self, jd_text: str) -> None:
        """保存 JD 并重新分析。"""
        if self._current is None:
            return
        self._current = self._resume.update_version(
            self._current.id, self._version_input(self._current, jd_text)
        ).unwrap_or(self._current)
        report = analyze(jd_text, self._known_terms())
        self.jd_changed.emit(report)
        self.status_changed.emit("JD 分析已更新")

    def _emit_catalog(self, version: ResumeVersion) -> None:
        """组装可选/已选条目。"""
        available = self._available_items()
        labels = {option.key: option.label for option in available}
        selected: list[SelectedItem] = []
        for row in self._resume.items(version.id):
            key = f"{row.item_type}:{row.item_id}"
            selected.append(
                SelectedItem(
                    row_id=row.id,
                    key=key,
                    label=labels.get(key, key),
                    item_type=row.item_type,
                    ref_id=row.item_id,
                )
            )
        self.catalog_changed.emit(ItemCatalog(available=available, selected=selected))

    def _available_items(self) -> list[ItemOption]:
        """全部可加入版本的条目。"""
        options: list[ItemOption] = []
        for edu_row in self._educations.list_all():
            options.append(
                ItemOption(
                    key=f"education:{edu_row.id}",
                    label=f"[学历] {edu_row.school} · {edu_row.degree_level}",
                    item_type="education",
                    ref_id=edu_row.id,
                )
            )
        for exp_row in self._experiences.list_all():
            options.append(
                ItemOption(
                    key=f"experience:{exp_row.id}",
                    label=f"[经历] {exp_row.company} · {exp_row.role}",
                    item_type="experience",
                    ref_id=exp_row.id,
                )
            )
        for project_row in self._projects.list_all():
            options.append(
                ItemOption(
                    key=f"project:{project_row.id}",
                    label=f"[项目] {project_row.name} · {project_row.direction}",
                    item_type="project",
                    ref_id=project_row.id,
                )
            )
        for skill_row in self._skills.list_all():
            options.append(
                ItemOption(
                    key=f"skill:{skill_row.id}",
                    label=f"[技能] {skill_row.category} · {skill_row.name}",
                    item_type="skill",
                    ref_id=skill_row.id,
                )
            )
        for cert_row in self._profile.certificates():
            options.append(
                ItemOption(
                    key=f"certificate:{cert_row.id}",
                    label=f"[证书] {cert_row.name}",
                    item_type="certificate",
                    ref_id=cert_row.id,
                )
            )
        return options

    def _find_selected(self, item_type: str, ref_id: int) -> ResumeItem | None:
        """按类型与引用 id 找已选行。"""
        if self._current is None:
            return None
        for row in self._resume.items(self._current.id):
            if row.item_type == item_type and row.item_id == ref_id:
                return row
        return None

    def _known_terms(self) -> list[str]:
        """JD 分析时的已有能力词。"""
        terms = [row.name for row in self._skills.list_all()]
        terms.extend(row.name for row in self._tags.list_all())
        terms.extend(row.direction for row in self._projects.list_all())
        return terms

    @staticmethod
    def _version_input(version: ResumeVersion, jd_text: str) -> VersionInput:
        """版本记录转输入模型。"""
        return VersionInput(
            name=version.name,
            target_role=version.target_role,
            target_jd=jd_text,
            template=version.template,
            theme=version.theme,
            is_default=version.is_default,
        )
