"""education 切片对外入口：服务构造与页面注册。"""

from __future__ import annotations

from typing import Protocol

from forgecv.features.education.repository import EducationRepository
from forgecv.features.education.service import EducationService
from forgecv.features.education.view import EducationPage
from forgecv.features.education.viewmodel import EducationViewModel
from forgecv.platform.adapters.db.session import SessionFactory
from forgecv.platform.ui.kit.manager import UiManager

ROUTE = "education"
TITLE = "学历路径"


class Host(Protocol):
    """组合根需要提供的最小接口。"""

    sessions: SessionFactory
    ui: UiManager


def build_service(sessions: SessionFactory) -> EducationService:
    """构造切片服务。"""
    return EducationService(EducationRepository(sessions))


def register(host: Host) -> None:
    """注册路由。"""
    service = build_service(host.sessions)
    host.ui.pages.register(
        ROUTE, TITLE, lambda: EducationPage(EducationViewModel(service))
    )
