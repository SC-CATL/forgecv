"""生命周期：逆序清理、幂等、故障隔离。"""

from __future__ import annotations

import pytest

from forgecv.platform.ui.kit.lifecycle import LifecycleService


def test_cleanup_runs_in_reverse_order(qapp) -> None:
    """后注册的清理先执行，且只执行一次。"""
    service = LifecycleService()
    order: list[str] = []
    service.register_cleanup(lambda: order.append("first"), name="first")
    service.register_cleanup(lambda: order.append("second"), name="second")
    service.shutdown()
    service.shutdown()
    assert order == ["second", "first"]
    assert service.shutting_down


def test_register_after_shutdown_is_rejected(qapp) -> None:
    """退出流程开始后拒绝新钩子。"""
    service = LifecycleService()
    service.shutdown()
    with pytest.raises(RuntimeError):
        service.register_cleanup(lambda: None)


def test_failing_cleanup_does_not_stop_others(qapp) -> None:
    """单个钩子异常不影响其余钩子。"""
    service = LifecycleService()
    order: list[str] = []

    def boom() -> None:
        raise RuntimeError("boom")

    service.register_cleanup(lambda: order.append("kept"), name="kept")
    service.register_cleanup(boom, name="boom")
    service.shutdown()
    assert order == ["kept"]
