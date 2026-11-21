"""project 切片对外入口：服务构造与页面注册。"""

from __future__ import annotations

from typing import Protocol

from forgecv.features.project.repository import ProjectRepository
from forgecv.features.project.service import ProjectService
from forgecv.features.project.view import ProjectPage
from forgecv.features.project.viewmodel import ProjectViewModel
from forgecv.features.tag.api import build_service as build_tags
from forgecv.platform.adapters.db.session import SessionFactory
from forgecv.platform.ui.kit.manager import UiManager

ROUTE = "project"
TITLE = "项目库"


class Host(Protocol):
    """组合根需要提供的最小接口。"""

    sessions: SessionFactory
    ui: UiManager


def build_service(sessions: SessionFactory) -> ProjectService:
    """构造切片服务。"""
    return ProjectService(ProjectRepository(sessions))


def register(host: Host) -> None:
    """注册路由，并注入标签服务。"""
    service = build_service(host.sessions)
    tags = build_tags(host.sessions)
    host.ui.pages.register(
        ROUTE,
        TITLE,
        lambda: ProjectPage(ProjectViewModel(service, tags)),
    )
