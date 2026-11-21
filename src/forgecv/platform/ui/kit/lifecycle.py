"""生命周期服务：退出前按注册逆序清理，保证只执行一次。"""

from __future__ import annotations

import logging
from collections.abc import Callable

from forgecv.platform.ui.qt import QtCore

log = logging.getLogger(__name__)


class LifecycleService(QtCore.QObject):
    """管理启动、退出钩子。"""

    def __init__(self) -> None:
        """初始化空钩子表。"""
        super().__init__()
        self._cleanups: list[tuple[str, Callable[[], None]]] = []
        self._shutdown_done = False

    @property
    def shutting_down(self) -> bool:
        """是否已进入退出流程。"""
        return self._shutdown_done

    def register_cleanup(self, fn: Callable[[], None], *, name: str = "") -> None:
        """注册清理函数，按后进先出执行。"""
        if self._shutdown_done:
            raise RuntimeError("已进入退出流程，拒绝注册清理函数")
        self._cleanups.append((name or getattr(fn, "__name__", "cleanup"), fn))

    def shutdown(self) -> None:
        """逆序执行清理，单个失败不影响其余。"""
        if self._shutdown_done:
            return
        self._shutdown_done = True
        for name, fn in reversed(self._cleanups):
            try:
                fn()
            except Exception:  # 退出阶段只记录
                log.exception("清理失败：%s", name)
        self._cleanups.clear()

    def bind(self, app: QtCore.QCoreApplication) -> None:
        """挂到 aboutToQuit，避免重复连接。"""
        app.aboutToQuit.connect(self.shutdown)
