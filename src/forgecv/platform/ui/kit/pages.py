"""页面路由：延迟实例化页面，首次访问才构建控件。"""

from __future__ import annotations

from collections.abc import Callable

from forgecv.platform.ui.kit.layout import LayoutService
from forgecv.platform.ui.qt import QtCore, QtWidgets, Signal

PageFactory = Callable[[], QtWidgets.QWidget]


class PageRouter(QtCore.QObject):
    """路由表 + 页面缓存，导航到未访问页面时才构建。"""

    navigated = Signal(str)

    def __init__(self, layout: LayoutService) -> None:
        """绑定主窗口布局服务。"""
        super().__init__()
        self._layout = layout
        self._factories: dict[str, tuple[str, PageFactory]] = {}
        self._widgets: dict[str, QtWidgets.QWidget] = {}
        self._bound = False

    def register(self, route: str, title: str, factory: PageFactory) -> None:
        """注册路由与页面工厂；窗口已就绪时立即挂导航项。"""
        if route in self._factories:
            raise ValueError(f"重复路由：{route}")
        self._factories[route] = (title, factory)
        if self._bound:
            self._layout.add_route(route, title)

    def routes(self) -> tuple[str, ...]:
        """已注册的全部路由。"""
        return tuple(self._factories)

    def navigate(self, route: str) -> QtWidgets.QWidget:
        """切到目标页面，必要时先构建。"""
        if route not in self._factories:
            raise KeyError(f"未知路由：{route}")
        widget = self._widgets.get(route)
        if widget is None:
            title, factory = self._factories[route]
            widget = factory()
            self._widgets[route] = widget
            if not self._layout.shell.has_route(route):
                self._layout.add_route(route, title)
            self._layout.set_page(route, widget)
        self._layout.set_route(route)
        self.navigated.emit(route)
        return widget

    def page(self, route: str) -> QtWidgets.QWidget | None:
        """已构建的页面，未访问时为 None。"""
        return self._widgets.get(route)

    def bind_shell(self) -> None:
        """挂载已注册导航项，并把点击接到路由，只连一次。"""
        if self._bound:
            return
        shell = self._layout.shell
        for route, (title, _) in self._factories.items():
            if not shell.has_route(route):
                self._layout.add_route(route, title)
        shell.nav_requested.connect(self.navigate)
        self._bound = True
