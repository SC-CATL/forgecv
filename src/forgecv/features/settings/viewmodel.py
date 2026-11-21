"""视图模型：把服务结果翻译成界面状态，可脱离窗口测试。"""

from __future__ import annotations

from forgecv.features.settings.service import SettingsService
from forgecv.platform.config import THEMES
from forgecv.platform.ui.kit.theme import ThemeService
from forgecv.platform.ui.qt import QtCore, Signal


class SettingsViewModel(QtCore.QObject):
    """主题选择与保存提示。"""

    themes_changed = Signal(object)
    status_changed = Signal(str)

    def __init__(self, service: SettingsService, theme: ThemeService) -> None:
        """注入服务与主题，加载当前值。"""
        super().__init__()
        self._service = service
        self._theme = theme
        self._selected = service.theme()

    @property
    def themes(self) -> tuple[str, ...]:
        """可选主题列表。"""
        return THEMES

    @property
    def selected(self) -> str:
        """当前选中主题。"""
        return self._selected

    def load(self) -> None:
        """加载并立即应用主题。"""
        self._selected = self._service.theme()
        self._theme.apply(self._selected)
        self.themes_changed.emit(list(self.themes))
        self.status_changed.emit("已加载当前主题")

    def select(self, mode: str) -> None:
        """预览所选主题，不落库。"""
        self._selected = mode
        self._theme.apply(mode)
        self.status_changed.emit(f"预览：{mode}")

    def save(self) -> bool:
        """保存主题，成功返回 True。"""
        result = self._service.save_theme(self._selected)
        if not result.is_ok:
            error = result.error()
            self.status_changed.emit(f"保存失败：{error}")
            return False
        self.status_changed.emit("主题已保存")
        return True
