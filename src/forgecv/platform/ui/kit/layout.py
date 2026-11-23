"""布局服务：主窗口骨架（左侧导航 + 右侧页面栈）。"""

from __future__ import annotations

from forgecv.platform.ui.qt import QtCore, QtWidgets, Signal


class ShellWindow(QtWidgets.QMainWindow):
    """主窗口骨架，只关心容器与切换，不含业务。"""

    nav_requested = Signal(str)

    def __init__(self, title: str) -> None:
        """构建导航与页面栈。"""
        super().__init__()
        self.setWindowTitle(title)
        self.resize(1120, 720)
        self._routes: list[str] = []

        central = QtWidgets.QWidget(self)
        row = QtWidgets.QHBoxLayout(central)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)

        self._nav = QtWidgets.QListWidget(central)
        self._nav.setObjectName("NavList")
        self._nav.setFixedWidth(220)
        self._stack = QtWidgets.QStackedWidget(central)
        row.addWidget(self._nav)
        row.addWidget(self._stack, 1)
        self.setCentralWidget(central)
        self.statusBar().showMessage("就绪")
        self._nav.currentRowChanged.connect(self._emit_route)

    def add_route(self, route: str, title: str) -> None:
        """只挂导航项与占位页，真实页面按需替换。"""
        if route in self._routes:
            raise ValueError(f"重复路由：{route}")
        self._routes.append(route)
        self._nav.blockSignals(True)
        self._nav.addItem(title)
        self._nav.blockSignals(False)
        self._stack.addWidget(QtWidgets.QWidget())

    def add_page(self, route: str, title: str, widget: QtWidgets.QWidget) -> None:
        """注册页面，导航与栈同步增长。"""
        self.add_route(route, title)
        self.set_page(route, widget)

    def set_page(self, route: str, widget: QtWidgets.QWidget) -> None:
        """用真实页面替换占位页，保持导航与页面栈下标一致。"""
        index = self._routes.index(route)
        placeholder = self._stack.widget(index)
        self._stack.insertWidget(index, widget)
        if placeholder is not None:
            self._stack.removeWidget(placeholder)
            placeholder.deleteLater()
        self._stack.setCurrentIndex(index)

    def has_route(self, route: str) -> bool:
        """路由是否已注册。"""
        return route in self._routes

    def set_route(self, route: str) -> None:
        """切换页面，不触发导航信号。"""
        index = self._routes.index(route)
        self._nav.blockSignals(True)
        self._nav.setCurrentRow(index)
        self._nav.blockSignals(False)
        self._stack.setCurrentIndex(index)

    def _emit_route(self, row: int) -> None:
        """把导航行号翻译为路由名。"""
        if 0 <= row < len(self._routes):
            self.nav_requested.emit(self._routes[row])


class LayoutService(QtCore.QObject):
    """持有主窗口并在创建时统一挂载父子关系。"""

    def __init__(self) -> None:
        """延迟到第一次请求时创建窗口。"""
        super().__init__()
        self._shell: ShellWindow | None = None

    @property
    def shell(self) -> ShellWindow:
        """已创建的主窗口。"""
        if self._shell is None:
            raise RuntimeError("主窗口尚未创建")
        return self._shell

    def create_shell(self, title: str) -> ShellWindow:
        """幂等创建主窗口。"""
        if self._shell is None:
            self._shell = ShellWindow(title)
        return self._shell

    def add_route(self, route: str, title: str) -> None:
        """把导航项与占位页加入主窗口。"""
        self.shell.add_route(route, title)

    def add_page(self, route: str, title: str, widget: QtWidgets.QWidget) -> None:
        """把页面加入主窗口。"""
        self.shell.add_page(route, title, widget)

    def set_page(self, route: str, widget: QtWidgets.QWidget) -> None:
        """用真实页面替换占位页。"""
        self.shell.set_page(route, widget)

    def set_route(self, route: str) -> None:
        """切换当前页面。"""
        self.shell.set_route(route)
