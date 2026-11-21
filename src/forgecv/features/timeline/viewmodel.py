"""视图模型：统一时间轴。"""

from __future__ import annotations

from forgecv.features.timeline.service import TimelineService
from forgecv.platform.ui.qt import QtCore, Signal


class TimelineViewModel(QtCore.QObject):
    """时间轴页状态。"""

    data_changed = Signal(object)
    status_changed = Signal(str)

    def __init__(self, service: TimelineService) -> None:
        """注入聚合服务。"""
        super().__init__()
        self._service = service

    def load(self) -> None:
        """重新生成事件与提示。"""
        data = self._service.snapshot()
        self.data_changed.emit(data)
        self.status_changed.emit(
            f"{len(data.events)} 条事件 · {len(data.warnings)} 条时间提示"
        )
