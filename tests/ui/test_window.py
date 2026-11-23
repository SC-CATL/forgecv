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
            "market",
            "resume",
            "export",
            "snapshot",
            SETTINGS_ROUTE,
        } <= routes
        assert container.ui.pages.page("dashboard") is not None
        assert window._nav.count() == len(routes)
        container.ui.pages.navigate(SETTINGS_ROUTE)
        assert container.ui.pages.page(SETTINGS_ROUTE) is not None
    finally:
        window.close()
        container.dispose()


def test_launch_upgrades_old_schema(
    settings: Settings, qapp, monkeypatch
) -> None:
    """直接启动时也会先迁移，避免 ORM 查询旧库缺列。"""
    from forgecv.app import bootstrap
    from forgecv.features.profile.api import build_service as build_profile
    from forgecv.platform.adapters.db.engine import create_engine_for
    from forgecv.platform.adapters.db.migrate import (
        current_revision,
        head_revision,
        upgrade,
    )
    from forgecv.platform.adapters.db.session import create_session_factory
    from forgecv.platform.ui.kit.layout import ShellWindow

    upgrade(settings, "0002")
    monkeypatch.setattr(bootstrap, "create_application", lambda: qapp)
    monkeypatch.setattr(bootstrap, "exec_app", lambda _app: 0)
    monkeypatch.setattr(ShellWindow, "show", lambda _self: None)

    assert bootstrap.run(settings) == 0
    assert current_revision(settings) == head_revision(settings)
    engine = create_engine_for(settings)
    try:
        profile = build_profile(create_session_factory(engine))
        assert profile.load() is not None
    finally:
        engine.dispose()


def test_container_theme_is_switchable(settings: Settings, qapp) -> None:
    """容器内置主题服务可切换并记录当前模式。"""
    upgrade(settings)
    container = Container.create(settings)
    try:
        assert container.ui.theme.apply("dark") == "dark"
        assert container.ui.theme.current == "dark"
    finally:
        container.dispose()
