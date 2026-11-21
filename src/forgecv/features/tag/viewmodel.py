"""视图模型：标签库。"""

from __future__ import annotations

from forgecv.features.tag.models import Tag
from forgecv.features.tag.schemas import TagInput
from forgecv.features.tag.service import TagService
from forgecv.platform.ui.qt import QtCore, Signal


class TagViewModel(QtCore.QObject):
    """标签页状态。"""

    rows_changed = Signal(object)
    status_changed = Signal(str)

    def __init__(self, service: TagService) -> None:
        """注入服务。"""
        super().__init__()
        self._service = service
        self._rows: list[Tag] = []

    @property
    def rows(self) -> list[Tag]:
        """当前缓存。"""
        return self._rows

    @property
    def dimensions(self) -> dict[str, str]:
        """维度代码到中文名。"""
        return self._service.dimensions()

    def load(self) -> None:
        """重新加载。"""
        self._rows = self._service.list_all()
        self.rows_changed.emit(self._rows)
        self.status_changed.emit(f"共 {len(self._rows)} 个标签")

    def create(self, data: TagInput) -> int | None:
        """新增，返回新标签 id。"""
        result = self._service.create(data)
        if not result.is_ok:
            self.status_changed.emit(f"新增失败：{result.error()}")
            return None
        row = result.unwrap()
        self.load()
        self.status_changed.emit("标签已新增")
        return row.id

    def update(self, tag_id: int, data: TagInput) -> bool:
        """覆盖。"""
        result = self._service.update(tag_id, data)
        if not result.is_ok:
            self.status_changed.emit(f"保存失败：{result.error()}")
            return False
        self.load()
        self.status_changed.emit("标签已保存")
        return True

    def delete(self, tag_id: int) -> bool:
        """删除。"""
        result = self._service.delete(tag_id)
        if not result.is_ok:
            self.status_changed.emit(f"删除失败：{result.error()}")
            return False
        self.load()
        self.status_changed.emit("标签已删除")
        return True
