"""组合根：唯一允许直接装配所有切片与平台适配器的地方。"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import Engine

from forgecv.platform.adapters.db.engine import create_engine_for
from forgecv.platform.adapters.db.session import SessionFactory, create_session_factory
from forgecv.platform.config import Settings, load_settings
from forgecv.platform.core.bus import EventBus
from forgecv.platform.observability.logging import configure_logging
from forgecv.platform.ui.kit.layout import ShellWindow
from forgecv.platform.ui.kit.manager import UiManager


@dataclass(slots=True)
class Container:
    """进程级依赖容器，退出时统一释放。"""

    settings: Settings
    engine: Engine
    sessions: SessionFactory
    bus: EventBus
    ui: UiManager

    @classmethod
    def create(cls, settings: Settings | None = None) -> Container:
        """按配置装配引擎、会话、事件总线与 UI。"""
        resolved = settings or load_settings()
        configure_logging(resolved.log_level)
        engine = create_engine_for(resolved)
        container = cls(
            settings=resolved,
            engine=engine,
            sessions=create_session_factory(engine),
            bus=EventBus(),
            ui=UiManager(),
        )
        container.ui.lifecycle.register_cleanup(engine.dispose, name="engine")
        return container

    def build_main_window(self) -> ShellWindow:
        """创建主窗口并挂载全部切片页面。"""
        from forgecv.app.window import build_window

        return build_window(self)

    def dispose(self) -> None:
        """释放 UI 资源；引擎由生命周期钩子关闭。"""
        self.ui.shutdown()
