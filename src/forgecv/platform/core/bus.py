"""事件总线：切片间唯一的同步解耦通道。"""

from __future__ import annotations

import logging
from collections import defaultdict
from collections.abc import Callable
from typing import Any

log = logging.getLogger(__name__)

Handler = Callable[[Any], None]


class EventBus:
    """极简发布订阅，处理器异常只记录不上抛。"""

    def __init__(self) -> None:
        """初始化空订阅表。"""
        self._handlers: dict[type[Any], list[Handler]] = defaultdict(list)

    def subscribe(self, event_type: type[Any], handler: Handler) -> None:
        """订阅某类事件。"""
        self._handlers[event_type].append(handler)

    def publish(self, event: Any) -> None:
        """发布事件，逐个调用处理器。"""
        for handler in list(self._handlers[type(event)]):
            try:
                handler(event)
            except Exception:  # 订阅方故障不拖垮发布方
                log.exception("事件处理器失败：%s", handler)

    def clear(self) -> None:
        """清空订阅，测试用。"""
        self._handlers.clear()
