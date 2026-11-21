"""tag 切片对外入口：服务构造与页面注册。"""

from __future__ import annotations

from typing import Protocol

from forgecv.features.tag.repository import TagRepository
from forgecv.features.tag.service import TagService
from forgecv.features.tag.view import TagPage
from forgecv.features.tag.viewmodel import TagViewModel
from forgecv.platform.adapters.db.session import SessionFactory
from forgecv.platform.ui.kit.manager import UiManager

ROUTE = "tag"
TITLE = "标签管理"


class Host(Protocol):
    """组合根需要提供的最小接口。"""

    sessions: SessionFactory
    ui: UiManager


def build_service(sessions: SessionFactory) -> TagService:
    """构造切片服务。"""
    return TagService(TagRepository(sessions))


def register(host: Host) -> None:
    """注册路由。"""
    service = build_service(host.sessions)
    host.ui.pages.register(ROUTE, TITLE, lambda: TagPage(TagViewModel(service)))
