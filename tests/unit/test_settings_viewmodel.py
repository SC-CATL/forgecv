"""设置视图模型：预览、保存与状态提示。"""

from __future__ import annotations

from forgecv.features.settings.api import build_service
from forgecv.features.settings.viewmodel import SettingsViewModel
from forgecv.platform.adapters.db.session import SessionFactory
from forgecv.platform.core.errors import ValidationError
from forgecv.platform.core.result import Result
from forgecv.platform.ui.kit.theme import ThemeService


class _FailingService:
    """总是拒绝保存的服务替身。"""

    def theme(self) -> str:
        return "system"

    def save_theme(self, mode: str) -> Result[str, ValidationError]:
        return Result.err(ValidationError(f"拒绝：{mode}"))


def test_load_applies_saved_theme(sessions: SessionFactory, qapp) -> None:
    """加载时立即应用已保存主题。"""
    service = build_service(sessions)
    service.save_theme("dark")
    theme = ThemeService()
    view_model = SettingsViewModel(service, theme)
    view_model.load()
    assert view_model.selected == "dark"
    assert theme.current == "dark"


def test_select_previews_without_persisting(sessions: SessionFactory, qapp) -> None:
    """选择只预览，不写库。"""
    service = build_service(sessions)
    theme = ThemeService()
    view_model = SettingsViewModel(service, theme)
    view_model.select("light")
    assert theme.current == "light"
    assert service.theme() == "system"


def test_save_persists_selection(sessions: SessionFactory, qapp) -> None:
    """保存后值落库。"""
    service = build_service(sessions)
    view_model = SettingsViewModel(service, ThemeService())
    view_model.select("high_contrast")
    assert view_model.save()
    assert service.theme() == "high_contrast"


def test_save_failure_reports_status(qapp) -> None:
    """保存失败时给出状态文本而非抛异常。"""
    view_model = SettingsViewModel(_FailingService(), ThemeService())  # type: ignore[arg-type]
    messages: list[str] = []
    view_model.status_changed.connect(messages.append)
    assert not view_model.save()
    assert "保存失败" in messages[-1]
