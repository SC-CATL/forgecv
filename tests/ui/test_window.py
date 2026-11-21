"""主窗口装配：容器可用、路由已注册、主题可切换。"""

from __future__ import annotations

import pytest

from forgecv.app.container import Container
from forgecv.features.settings.api import ROUTE as SETTINGS_ROUTE
from forgecv.platform.adapters.db.migrate import upgrade
from forgecv.platform.config import Settings

pytestmark = pytest.mark.ui


def test_container_builds_window(settings: Settings, qapp) -> None:
    """组合根能建出主窗口并挂载全部切片。"""
    upgrade(settings)
    container = Container.create(settings)
    window = container.build_main_window()
    try:
        assert window.windowTitle() == settings.app_title
        routes = set(container.ui.pages.routes())
        assert {
            "dashboard",
            "profile",
            "education",
            "timeline",
            "experience",
            "project",
            "tag",
            "skill",
            "resume",
            "export",
            "snapshot",
            SETTINGS_ROUTE,
        } <= routes
        assert container.ui.pages.page("dashboard") is not None
        container.ui.pages.navigate(SETTINGS_ROUTE)
        assert container.ui.pages.page(SETTINGS_ROUTE) is not None
    finally:
        window.close()
        container.dispose()


def test_container_theme_is_switchable(settings: Settings, qapp) -> None:
    """容器内置主题服务可切换并记录当前模式。"""
    upgrade(settings)
    container = Container.create(settings)
    try:
        assert container.ui.theme.apply("dark") == "dark"
        assert container.ui.theme.current == "dark"
    finally:
        container.dispose()
