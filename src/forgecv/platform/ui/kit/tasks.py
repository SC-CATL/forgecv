"""线程池服务：io / serial / cpu 三个命名池，结果回到 UI 线程。"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from forgecv.platform.ui.qt import QtCore, Signal

log = logging.getLogger(__name__)

Job = Callable[[], Any]
Done = Callable[[Any], None]
Failed = Callable[[str], None]

POOL_SIZES = {"io": 4, "serial": 1, "cpu": 2}


class _Signals(QtCore.QObject):
    """工作线程到 UI 线程的回传信号。"""

    done = Signal(object)
    failed = Signal(str)


class _Job(QtCore.QRunnable):
    """在池中执行可调用对象，异常转为 failed 信号。"""

    def __init__(self, fn: Job, signals: _Signals) -> None:
        super().__init__()
        self._fn = fn
        self._signals = signals

    def run(self) -> None:
        """执行任务，绝不向线程池抛异常。"""
        try:
            self._signals.done.emit(self._fn())
        except Exception as exc:  # 边界处统一转信号
            log.exception("后台任务失败")
            self._signals.failed.emit(f"{type(exc).__name__}: {exc}")


class ExecutorService(QtCore.QObject):
    """提交后台任务并保持信号对象存活。"""

    def __init__(self) -> None:
        """创建三个线程池并设置容量。"""
        super().__init__()
        self._pools = {name: QtCore.QThreadPool() for name in POOL_SIZES}
        for name, size in POOL_SIZES.items():
            self._pools[name].setMaxThreadCount(size)
        self._pending: set[_Signals] = set()

    def submit(self, pool: str, fn: Job, *, on_done: Done | None = None,
               on_error: Failed | None = None) -> None:
        """提交任务；回调在 UI 线程执行。"""
        if pool not in self._pools:
            raise KeyError(f"未知线程池：{pool}")
        signals = _Signals()
        self._pending.add(signals)
        signals.done.connect(lambda value: self._finish(signals, on_done, value))
        signals.failed.connect(lambda message: self._finish(signals, on_error, message))
        self._pools[pool].start(_Job(fn, signals))

    def shutdown(self, wait_ms: int = 3000) -> None:
        """等待在跑任务结束，关闭时调用一次。"""
        for thread_pool in self._pools.values():
            thread_pool.waitForDone(wait_ms)
        self._pending.clear()

    def _finish(self, signals: _Signals, callback: Callable[[Any], None] | None,
                payload: Any) -> None:
        """清理引用后调用用户回调。"""
        self._pending.discard(signals)
        if callback is not None:
            callback(payload)
