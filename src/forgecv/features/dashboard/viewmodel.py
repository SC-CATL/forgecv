"""视图模型：概览数据与主题颜色。"""

from __future__ import annotations

from forgecv.features.dashboard.service import DashboardService
from forgecv.platform.ui.kit.theme import ThemeService
from forgecv.platform.ui.qt import QtCore, Signal


class DashboardViewModel(QtCore.QObject):
    """概览页状态。"""

    data_changed = Signal(object)
    colors_changed = Signal(object)
    status_changed = Signal(str)

    def __init__(self, service: DashboardService, theme: ThemeService) -> None:
        """注入聚合服务与主题。"""
        super().__init__()
        self._service = service
        self._theme = theme
        self._theme.changed.connect(self._emit_colors)

    def load(self) -> None:
        """重新计算概览。"""
        data = self._service.snapshot()
        self.data_changed.emit(data)
        self._emit_colors()
        self.status_changed.emit("概览已刷新")

    def colors(self) -> dict[str, str]:
        """当前主题下雷达图需要的颜色。"""
        return {
            "border": self._theme.color("border"),
            "accent": self._theme.color("accent"),
            "muted": self._theme.color("fg_muted"),
            "surface": self._theme.color("bg_surface"),
            "fg_default": self._theme.color("fg_default"),
        }

    def _emit_colors(self, _mode: str = "") -> None:
        """主题变化时广播颜色。"""
        self.colors_changed.emit(self.colors())
