"""应用启动：装配依赖、创建窗口、进入事件循环。"""

from __future__ import annotations

import sys
from typing import cast

from forgecv.app.container import Container
from forgecv.platform.config import Settings
from forgecv.platform.ui.qt import QtWidgets, enable_high_dpi, exec_app


def ensure_candidate(container: Container) -> None:
    """单候选人应用中，首次启动就建好外键宿主行。"""
    from forgecv.features.profile.api import build_service as build_profile

    build_profile(container.sessions).ensure()


def create_application() -> QtWidgets.QApplication:
    """创建 QApplication，重复调用时复用已有实例。"""
    enable_high_dpi()
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("forgecv")
    app.setApplicationVersion("0.1.0")
    return cast(QtWidgets.QApplication, app)


def run(settings: Settings) -> int:
    """迁移到最新结构后启动主窗口，阻塞到退出。"""
    from forgecv.platform.adapters.db.migrate import upgrade
    from forgecv.platform.observability.crash import install_excepthook

    install_excepthook()
    upgrade(settings)
    app = create_application()
    container = Container.create(settings)
    ensure_candidate(container)
    container.ui.lifecycle.bind(app)
    window = container.build_main_window()
    container.ui.theme.apply(settings.theme)
    window.show()
    try:
        return exec_app(app)
    finally:
        container.dispose()
