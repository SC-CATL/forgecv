"""事件总线的订阅、发布与故障隔离。"""

from __future__ import annotations

from dataclasses import dataclass

from forgecv.platform.core.bus import EventBus


@dataclass(frozen=True)
class Ping:
    """测试事件。"""

    value: int


def test_publish_reaches_all_handlers() -> None:
    """同一事件的所有订阅者都会收到。"""
    bus = EventBus()
    seen: list[int] = []
    bus.subscribe(Ping, lambda event: seen.append(event.value))
    bus.subscribe(Ping, lambda event: seen.append(event.value * 10))
    bus.publish(Ping(2))
    assert seen == [2, 20]


def test_handler_failure_does_not_block_others() -> None:
    """单个处理器异常不影响其余订阅者。"""
    bus = EventBus()
    seen: list[str] = []

    def boom(_event: Ping) -> None:
        raise RuntimeError("boom")

    bus.subscribe(Ping, boom)
    bus.subscribe(Ping, lambda _event: seen.append("ok"))
    bus.publish(Ping(1))
    assert seen == ["ok"]


def test_unknown_event_is_ignored() -> None:
    """没有订阅者时发布是空操作。"""
    EventBus().publish(Ping(1))
