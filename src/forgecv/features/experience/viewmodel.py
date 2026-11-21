"""视图模型：工作经历列表与编辑。"""

from __future__ import annotations

from forgecv.features.experience.models import Experience
from forgecv.features.experience.schemas import ExperienceInput
from forgecv.features.experience.service import ExperienceService
from forgecv.platform.ui.qt import QtCore, Signal


class ExperienceViewModel(QtCore.QObject):
    """工作经历页状态。"""

    rows_changed = Signal(object)
    status_changed = Signal(str)

    def __init__(self, service: ExperienceService) -> None:
        """注入服务。"""
        super().__init__()
        self._service = service
        self._rows: list[Experience] = []

    @property
    def rows(self) -> list[Experience]:
        """当前缓存。"""
        return self._rows

    def load(self) -> None:
        """重新加载。"""
        self._rows = self._service.list_all()
        self.rows_changed.emit(self._rows)
        self.status_changed.emit(f"共 {len(self._rows)} 段经历")

    def add(self, data: ExperienceInput) -> int | None:
        """新增，返回新记录 id。"""
        result = self._service.add(data)
        if not result.is_ok:
            self.status_changed.emit(f"新增失败：{result.error()}")
            return None
        row = result.unwrap()
        self.load()
        self.status_changed.emit("经历已新增")
        return row.id

    def update(self, experience_id: int, data: ExperienceInput) -> bool:
        """覆盖。"""
        result = self._service.update(experience_id, data)
        if not result.is_ok:
            self.status_changed.emit(f"保存失败：{result.error()}")
            return False
        self.load()
        self.status_changed.emit("经历已保存")
        return True

    def delete(self, experience_id: int) -> bool:
        """删除。"""
        result = self._service.delete(experience_id)
        if not result.is_ok:
            self.status_changed.emit(f"删除失败：{result.error()}")
            return False
        self.load()
        self.status_changed.emit("经历已删除")
        return True
