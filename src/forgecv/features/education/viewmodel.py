"""视图模型：学历列表与编辑。"""

from __future__ import annotations

from forgecv.features.education.models import Education
from forgecv.features.education.schemas import EducationInput
from forgecv.features.education.service import EducationService
from forgecv.platform.ui.qt import QtCore, Signal


class EducationViewModel(QtCore.QObject):
    """学历页状态。"""

    rows_changed = Signal(object)
    status_changed = Signal(str)

    def __init__(self, service: EducationService) -> None:
        """注入服务。"""
        super().__init__()
        self._service = service
        self._rows: list[Education] = []

    @property
    def rows(self) -> list[Education]:
        """当前缓存。"""
        return self._rows

    def load(self) -> None:
        """重新加载列表。"""
        self._rows = self._service.list_all()
        self.rows_changed.emit(self._rows)
        self.status_changed.emit(f"共 {len(self._rows)} 段学历")

    def add(self, data: EducationInput) -> int | None:
        """新增并刷新，返回新记录 id。"""
        result = self._service.add(data)
        if not result.is_ok:
            self.status_changed.emit(f"新增失败：{result.error()}")
            return None
        row = result.unwrap()
        self.load()
        self.status_changed.emit("学历已新增")
        return row.id

    def update(self, education_id: int, data: EducationInput) -> bool:
        """覆盖并刷新。"""
        result = self._service.update(education_id, data)
        if not result.is_ok:
            self.status_changed.emit(f"保存失败：{result.error()}")
            return False
        self.load()
        self.status_changed.emit("学历已保存")
        return True

    def delete(self, education_id: int) -> bool:
        """删除并刷新。"""
        result = self._service.delete(education_id)
        if not result.is_ok:
            self.status_changed.emit(f"删除失败：{result.error()}")
            return False
        self.load()
        self.status_changed.emit("学历已删除")
        return True

    def move(self, index: int, delta: int) -> None:
        """按列表位置上移或下移一条。"""
        target = index + delta
        if index < 0 or target < 0 or target >= len(self._rows):
            return
        ordered = [row.id for row in self._rows]
        ordered[index], ordered[target] = ordered[target], ordered[index]
        self._service.reorder(ordered)
        self.load()
