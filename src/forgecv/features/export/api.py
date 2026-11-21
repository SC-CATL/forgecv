"""export 切片对外入口：装配渲染器与页面注册。"""

from __future__ import annotations

from typing import Protocol

from forgecv.features.education.api import build_service as build_education
from forgecv.features.experience.api import build_service as build_experience
from forgecv.features.export.service import ExportService
from forgecv.features.export.view import ExportPage
from forgecv.features.export.viewmodel import ExportViewModel
from forgecv.features.profile.api import build_service as build_profile
from forgecv.features.project.api import build_service as build_project
from forgecv.features.resume.api import build_service as build_resume
from forgecv.features.resume.checks import ResumeCheckService
from forgecv.features.resume.render import ResumeRenderer
from forgecv.features.skill.api import build_service as build_skill
from forgecv.features.tag.api import build_service as build_tag
from forgecv.platform.adapters.db.session import SessionFactory
from forgecv.platform.ui.kit.manager import UiManager

ROUTE = "export"
TITLE = "导出 Word"


class Host(Protocol):
    """组合根需要提供的最小接口。"""

    sessions: SessionFactory
    ui: UiManager


def build_service(sessions: SessionFactory) -> ExportService:
    """构造导出服务。"""
    skills = build_skill(sessions)
    renderer = ResumeRenderer(
        resume=build_resume(sessions),
        profile=build_profile(sessions),
        educations=build_education(sessions),
        experiences=build_experience(sessions),
        projects=build_project(sessions),
        skills=skills,
        tags=build_tag(sessions),
    )
    return ExportService(renderer, ResumeCheckService(skills))


def register(host: Host) -> None:
    """注册路由。"""
    resume = build_resume(host.sessions)
    service = build_service(host.sessions)
    host.ui.pages.register(
        ROUTE,
        TITLE,
        lambda: ExportPage(ExportViewModel(resume, service)),
    )
