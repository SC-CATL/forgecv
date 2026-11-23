"""布局与路由：延迟构建、导航切换、错误防御。"""

from __future__ import annotations

import pytest

from forgecv.platform.ui.kit.manager import UiManager
from forgecv.platform.ui.qt import QtWidgets


def test_navigation_builds_page_once(qapp) -> None:
    """同一路由只构建一次页面。"""
    ui = UiManager()
    shell = ui.create_shell("测试")
    builds: list[int] = []

    def factory() -> QtWidgets.QWidget:
        builds.append(1)
        return QtWidgets.QLabel("home")

    ui.pages.register("home", "首页", factory)
    first = ui.pages.navigate("home")
    second = ui.pages.navigate("home")
    assert first is second
    assert builds == [1]
    assert shell.has_route("home")
    assert ui.pages.page("home") is first
    ui.shutdown()


def test_nav_click_switches_route(qapp) -> None:
    """点击导航发出对应路由。"""
    ui = UiManager()
    shell = ui.create_shell("测试")
    ui.pages.register("a", "A", lambda: QtWidgets.QLabel("a"))
    ui.pages.register("b", "B", lambda: QtWidgets.QLabel("b"))
    ui.pages.navigate("a")
    ui.pages.navigate("b")
    seen: list[str] = []
    ui.pages.navigated.connect(seen.append)
    shell._nav.setCurrentRow(0)
    assert seen == ["a"]
    ui.shutdown()


def test_nav_lists_every_route_before_first_visit(qapp) -> None:
    """启动后导航栏应列出全部路由，而不是只显示首页。"""
    ui = UiManager()
    shell = ui.create_shell("测试")
    ui.pages.register("a", "A", lambda: QtWidgets.QLabel("a"))
    ui.pages.register("b", "B", lambda: QtWidgets.QLabel("b"))
    ui.pages.register("c", "C", lambda: QtWidgets.QLabel("c"))
    ui.pages.navigate("a")
    assert shell._nav.count() == 3
    assert [shell._nav.item(i).text() for i in range(3)] == ["A", "B", "C"]
    assert ui.pages.page("b") is None
    seen: list[str] = []
    ui.pages.navigated.connect(seen.append)
    shell._nav.setCurrentRow(2)
    assert seen == ["c"]
    assert shell._stack.currentWidget() is ui.pages.page("c")
    ui.shutdown()


def test_routes_registered_before_shell_are_mounted(qapp) -> None:
    """先注册路由、后建窗口时也要补齐导航项。"""
    ui = UiManager()
    ui.pages.register("a", "A", lambda: QtWidgets.QLabel("a"))
    ui.pages.register("b", "B", lambda: QtWidgets.QLabel("b"))
    shell = ui.create_shell("测试")
    assert shell._nav.count() == 2
    ui.shutdown()


def test_duplicate_route_is_rejected(qapp) -> None:
    """重复注册路由立即失败。"""
    ui = UiManager()
    ui.pages.register("a", "A", lambda: QtWidgets.QLabel("a"))
    with pytest.raises(ValueError):
        ui.pages.register("a", "A2", lambda: QtWidgets.QLabel("a2"))


def test_unknown_route_is_rejected(qapp) -> None:
    """访问未注册路由立即失败。"""
    ui = UiManager()
    ui.create_shell("测试")
    with pytest.raises(KeyError):
        ui.pages.navigate("nope")


def test_shell_requires_creation(qapp) -> None:
    """未创建窗口时访问 shell 给出明确错误。"""
    ui = UiManager()
    with pytest.raises(RuntimeError):
        _ = ui.layout.shell
