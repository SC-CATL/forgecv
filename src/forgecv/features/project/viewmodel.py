"""视图模型：项目库、指标与标签。"""

from __future__ import annotations

from forgecv.features.project.models import Project, ProjectMetric
from forgecv.features.project.schemas import ProjectInput
from forgecv.features.project.service import ProjectService
from forgecv.features.tag.service import TagService
from forgecv.platform.ui.qt import QtCore, Signal


class ProjectViewModel(QtCore.QObject):
    """项目库页状态。"""

    rows_changed = Signal(object)
    tags_changed = Signal(object)
    metrics_changed = Signal(object)
    project_tags_changed = Signal(object)
    status_changed = Signal(str)

    def __init__(self, projects: ProjectService, tags: TagService) -> None:
        """注入项目与标签服务。"""
        super().__init__()
        self._projects = projects
        self._tags = tags
        self._rows: list[Project] = []

    @property
    def rows(self) -> list[Project]:
        """当前项目缓存。"""
        return self._rows

    @property
    def dimension_labels(self) -> dict[str, str]:
        """标签维度中文名。"""
        return self._tags.dimensions()

    def load(self) -> None:
        """加载项目与标签库。"""
        self._rows = self._projects.list_all()
        self.rows_changed.emit(self._rows)
        self.tags_changed.emit(self._tags.list_all())
        self.status_changed.emit(f"共 {len(self._rows)} 个项目")

    def select(self, project_id: int) -> None:
        """选中项目时加载指标与标签。"""
        self.metrics_changed.emit(self._projects.metrics_for(project_id))
        self.project_tags_changed.emit(self._tags.tags_for_project(project_id))

    def add(self, data: ProjectInput) -> int | None:
        """新增项目，返回 id 以便继续打标签。"""
        result = self._projects.add(data)
        if not result.is_ok:
            self.status_changed.emit(f"新增失败：{result.error()}")
            return None
        row = result.unwrap()
        self.load()
        self.status_changed.emit("项目已新增")
        return row.id

    def update(self, project_id: int, data: ProjectInput) -> bool:
        """覆盖项目。"""
        result = self._projects.update(project_id, data)
        if not result.is_ok:
            self.status_changed.emit(f"保存失败：{result.error()}")
            return False
        self.load()
        self.status_changed.emit("项目已保存")
        return True

    def delete(self, project_id: int) -> bool:
        """删除项目。"""
        result = self._projects.delete(project_id)
        if not result.is_ok:
            self.status_changed.emit(f"删除失败：{result.error()}")
            return False
        self.load()
        self.status_changed.emit("项目已删除")
        return True

    def set_tags(self, project_id: int, tag_ids: list[int]) -> None:
        """整体重设项目标签。"""
        self._tags.set_project_tags(project_id, tag_ids)
        self.project_tags_changed.emit(self._tags.tags_for_project(project_id))
        self.tags_changed.emit(self._tags.list_all())
        self.status_changed.emit("项目标签已更新")

    def metrics_for(self, project_id: int) -> list[ProjectMetric]:
        """项目指标。"""
        return self._projects.metrics_for(project_id)
