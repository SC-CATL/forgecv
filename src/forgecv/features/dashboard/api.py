"""dashboard 切片对外入口：聚合服务与页面注册。"""

from __future__ import annotations

from typing import Protocol

from forgecv.features.dashboard.service import DashboardService
from forgecv.features.dashboard.view import DashboardPage
from forgecv.features.dashboard.viewmodel import DashboardViewModel
from forgecv.features.education.api import build_service as build_education
from forgecv.features.experience.api import build_service as build_experience
from forgecv.features.project.api import build_service as build_project
from forgecv.features.skill.api import build_service as build_skill
from forgecv.features.tag.api import build_service as build_tag
from forgecv.platform.adapters.db.session import SessionFactory
from forgecv.platform.ui.kit.manager import UiManager

ROUTE = "dashboard"
TITLE = "概览"


class Host(Protocol):
    """组合根需要提供的最小接口。"""

    sessions: SessionFactory
    ui: UiManager


def build_service(sessions: SessionFactory) -> DashboardService:
    """装配五个只读来源。"""
    return DashboardService(
        build_education(sessions),
        build_experience(sessions),
        build_project(sessions),
        build_skill(sessions),
        build_tag(sessions),
    )


def register(host: Host) -> None:
    """注册路由。"""
    service = build_service(host.sessions)
    host.ui.pages.register(
        ROUTE,
        TITLE,
        lambda: DashboardPage(DashboardViewModel(service, host.ui.theme)),
    )
