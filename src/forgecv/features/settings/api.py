"""切片对外唯一入口：注册路由，暴露服务构造。"""

from __future__ import annotations

from typing import Protocol

from forgecv.features.settings.repository import SettingsRepository
from forgecv.features.settings.service import SettingsService
from forgecv.features.settings.view import SettingsPage
from forgecv.features.settings.viewmodel import SettingsViewModel
from forgecv.platform.adapters.db.session import SessionFactory
from forgecv.platform.ui.kit.manager import UiManager

ROUTE = "settings"
TITLE = "设置"


class Host(Protocol):
    """组合根需要提供的最小接口。"""

    sessions: SessionFactory
    ui: UiManager


def build_service(sessions: SessionFactory) -> SettingsService:
    """构造切片服务，供测试与外部调用。"""
    return SettingsService(SettingsRepository(sessions))


def register(host: Host) -> None:
    """注册路由；页面在首次访问时才实例化。"""
    service = build_service(host.sessions)
    host.ui.pages.register(
        ROUTE,
        TITLE,
        lambda: SettingsPage(SettingsViewModel(service, host.ui.theme)),
    )
