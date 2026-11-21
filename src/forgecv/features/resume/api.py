"""resume 切片对外入口：服务构造、渲染器与页面注册。"""

from __future__ import annotations

from typing import Protocol

from forgecv.features.education.api import build_service as build_education
from forgecv.features.experience.api import build_service as build_experience
from forgecv.features.profile.api import build_service as build_profile
from forgecv.features.project.api import build_service as build_project
from forgecv.features.resume.checks import ResumeCheckService
from forgecv.features.resume.render import ResumeRenderer
from forgecv.features.resume.repository import ResumeRepository
from forgecv.features.resume.service import ResumeService
from forgecv.features.resume.view import ResumePage
from forgecv.features.resume.viewmodel import ResumeViewModel
from forgecv.features.skill.api import build_service as build_skill
from forgecv.features.tag.api import build_service as build_tag
from forgecv.platform.adapters.db.session import SessionFactory
from forgecv.platform.ui.kit.manager import UiManager

ROUTE = "resume"
TITLE = "简历版本"


class Host(Protocol):
    """组合根需要提供的最小接口。"""

    sessions: SessionFactory
    ui: UiManager


def build_service(sessions: SessionFactory) -> ResumeService:
    """构造切片服务。"""
    return ResumeService(ResumeRepository(sessions))


def register(host: Host) -> None:
    """注册路由，并注入渲染所需的其他切片。"""
    sessions = host.sessions
    resume = build_service(sessions)
    profile = build_profile(sessions)
    educations = build_education(sessions)
    experiences = build_experience(sessions)
    projects = build_project(sessions)
    skills = build_skill(sessions)
    tags = build_tag(sessions)
    renderer = ResumeRenderer(
        resume=resume,
        profile=profile,
        educations=educations,
        experiences=experiences,
        projects=projects,
        skills=skills,
        tags=tags,
    )
    checks = ResumeCheckService(skills)
    host.ui.pages.register(
        ROUTE,
        TITLE,
        lambda: ResumePage(
            ResumeViewModel(
                resume=resume,
                renderer=renderer,
                checks=checks,
                educations=educations,
                experiences=experiences,
                projects=projects,
                skills=skills,
                profile=profile,
                tags=tags,
            )
        ),
    )
