"""线程池：成功、失败、清理。"""

from __future__ import annotations

import pytest

from forgecv.platform.ui.kit.tasks import ExecutorService


def test_submit_success(qtbot, qapp) -> None:
    """结果回到主线程回调。"""
    service = ExecutorService()
    done: list[int] = []
    service.submit("serial", lambda: 7, on_done=done.append)
    qtbot.waitUntil(lambda: bool(done), timeout=3000)
    assert done == [7]
    service.shutdown()


def test_submit_failure(qtbot, qapp) -> None:
    """异常转为错误回调，不冒泡。"""
    service = ExecutorService()
    errors: list[str] = []

    def boom() -> None:
        raise RuntimeError("炸了")

    service.submit("serial", boom, on_error=errors.append)
    qtbot.waitUntil(lambda: bool(errors), timeout=3000)
    assert "RuntimeError" in errors[0]
    service.shutdown()


def test_unknown_pool_is_rejected(qapp) -> None:
    """未知线程池立即失败。"""
    with pytest.raises(KeyError):
        ExecutorService().submit("nope", lambda: None)
