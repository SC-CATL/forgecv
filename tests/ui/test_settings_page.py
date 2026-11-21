"""设置页控件装配与交互。"""

from __future__ import annotations

import pytest

from forgecv.features.settings.api import build_service
from forgecv.features.settings.view import SettingsPage
from forgecv.features.settings.viewmodel import SettingsViewModel
from forgecv.platform.adapters.db.session import SessionFactory
from forgecv.platform.ui.kit.theme import ThemeService

pytestmark = pytest.mark.ui


def _page(sessions: SessionFactory) -> SettingsPage:
    view_model = SettingsViewModel(build_service(sessions), ThemeService())
    return SettingsPage(view_model)


def test_page_lists_all_themes(qtbot, sessions: SessionFactory) -> None:
    """下拉框包含全部主题。"""
    page = _page(sessions)
    qtbot.addWidget(page)
    assert page._combo.count() == 4


def test_save_updates_status(qtbot, sessions: SessionFactory) -> None:
    """点击保存后状态栏文本更新。"""
    page = _page(sessions)
    qtbot.addWidget(page)
    page._on_save()
    assert "已保存" in page._status.text()
