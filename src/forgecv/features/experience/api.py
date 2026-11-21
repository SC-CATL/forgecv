"""experience 切片对外入口：服务构造与页面注册。"""

from __future__ import annotations

from typing import Protocol

from forgecv.features.experience.repository import ExperienceRepository
from forgecv.features.experience.service import ExperienceService
from forgecv.features.experience.view import ExperiencePage
from forgecv.features.experience.viewmodel import ExperienceViewModel
from forgecv.platform.adapters.db.session import SessionFactory
from forgecv.platform.ui.kit.manager import UiManager

ROUTE = "experience"
TITLE = "工作经历"


class Host(Protocol):
    """组合根需要提供的最小接口。"""

    sessions: SessionFactory
    ui: UiManager


def build_service(sessions: SessionFactory) -> ExperienceService:
    """构造切片服务。"""
    return ExperienceService(ExperienceRepository(sessions))


def register(host: Host) -> None:
    """注册路由。"""
    service = build_service(host.sessions)
    host.ui.pages.register(
        ROUTE, TITLE, lambda: ExperiencePage(ExperienceViewModel(service))
    )
