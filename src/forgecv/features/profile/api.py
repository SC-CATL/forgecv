"""profile 切片对外入口：服务构造与页面注册。"""

from __future__ import annotations

from typing import Protocol

from forgecv.features.profile.repository import ProfileRepository
from forgecv.features.profile.service import ProfileService
from forgecv.features.profile.view import ProfilePage
from forgecv.features.profile.viewmodel import ProfileViewModel
from forgecv.platform.adapters.db.session import SessionFactory
from forgecv.platform.ui.kit.manager import UiManager

ROUTE = "profile"
TITLE = "个人信息"


class Host(Protocol):
    """组合根需要提供的最小接口。"""

    sessions: SessionFactory
    ui: UiManager


def build_service(sessions: SessionFactory) -> ProfileService:
    """构造切片服务。"""
    return ProfileService(ProfileRepository(sessions))


def register(host: Host) -> None:
    """注册路由，首次访问时才构建页面。"""
    service = build_service(host.sessions)
    host.ui.pages.register(
        ROUTE, TITLE, lambda: ProfilePage(ProfileViewModel(service))
    )
