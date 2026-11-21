"""UI 门面：聚合六个可独立测试的子服务。"""

from __future__ import annotations

from forgecv.platform.ui.kit.dialogs import DialogService
from forgecv.platform.ui.kit.layout import LayoutService, ShellWindow
from forgecv.platform.ui.kit.lifecycle import LifecycleService
from forgecv.platform.ui.kit.pages import PageRouter
from forgecv.platform.ui.kit.tasks import ExecutorService
from forgecv.platform.ui.kit.theme import ThemeService


class UiManager:
    """业务代码只与这个门面交互。"""

    def __init__(self) -> None:
        """按依赖顺序装配子服务。"""
        self.theme = ThemeService()
        self.dialogs = DialogService()
        self.layout = LayoutService()
        self.pages = PageRouter(self.layout)
        self.tasks = ExecutorService()
        self.lifecycle = LifecycleService()

    def create_shell(self, title: str) -> ShellWindow:
        """创建主窗口并接好导航。"""
        shell = self.layout.create_shell(title)
        self.dialogs.set_parent(shell)
        self.pages.bind_shell()
        return shell

    def shutdown(self) -> None:
        """退出前释放线程池与清理钩子。"""
        self.lifecycle.shutdown()
        self.tasks.shutdown()
