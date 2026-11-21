"""timeline 切片对外入口：聚合服务与页面注册。"""

from __future__ import annotations

from typing import Protocol

from forgecv.features.education.api import build_service as build_education
from forgecv.features.experience.api import build_service as build_experience
from forgecv.features.project.api import build_service as build_project
from forgecv.features.timeline.service import TimelineService
from forgecv.features.timeline.view import TimelinePage
from forgecv.features.timeline.viewmodel import TimelineViewModel
from forgecv.platform.adapters.db.session import SessionFactory
from forgecv.platform.ui.kit.manager import UiManager

ROUTE = "timeline"
TITLE = "时间轴"


class Host(Protocol):
    """组合根需要提供的最小接口。"""

    sessions: SessionFactory
    ui: UiManager


def build_service(sessions: SessionFactory) -> TimelineService:
    """装配三个只读来源。"""
    return TimelineService(
        build_education(sessions),
        build_experience(sessions),
        build_project(sessions),
    )


def register(host: Host) -> None:
    """注册路由。"""
    service = build_service(host.sessions)
    host.ui.pages.register(
        ROUTE, TITLE, lambda: TimelinePage(TimelineViewModel(service))
    )
