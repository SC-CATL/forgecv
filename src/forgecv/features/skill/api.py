"""skill 切片对外入口：服务构造与页面注册。"""

from __future__ import annotations

from typing import Protocol

from forgecv.features.experience.api import build_service as build_experience
from forgecv.features.project.api import build_service as build_project
from forgecv.features.skill.repository import SkillRepository
from forgecv.features.skill.service import SkillService
from forgecv.features.skill.view import SkillPage
from forgecv.features.skill.viewmodel import SkillViewModel
from forgecv.platform.adapters.db.session import SessionFactory
from forgecv.platform.ui.kit.manager import UiManager

ROUTE = "skill"
TITLE = "技能矩阵"


class Host(Protocol):
    """组合根需要提供的最小接口。"""

    sessions: SessionFactory
    ui: UiManager


def build_service(sessions: SessionFactory) -> SkillService:
    """构造切片服务。"""
    return SkillService(SkillRepository(sessions))


def register(host: Host) -> None:
    """注册路由，并注入项目与经历查询服务。"""
    service = build_service(host.sessions)
    projects = build_project(host.sessions)
    experiences = build_experience(host.sessions)
    host.ui.pages.register(
        ROUTE,
        TITLE,
        lambda: SkillPage(SkillViewModel(service, projects, experiences)),
    )
