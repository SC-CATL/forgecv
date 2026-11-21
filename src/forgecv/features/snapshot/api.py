"""snapshot 切片对外入口：装配与页面注册。"""

from __future__ import annotations

from typing import Protocol

from forgecv.features.education.api import build_service as build_education
from forgecv.features.experience.api import build_service as build_experience
from forgecv.features.profile.api import build_service as build_profile
from forgecv.features.project.api import build_service as build_project
from forgecv.features.resume.api import build_service as build_resume
from forgecv.features.resume.render import ResumeRenderer
from forgecv.features.skill.api import build_service as build_skill
from forgecv.features.snapshot.service import SnapshotService
from forgecv.features.snapshot.view import SnapshotPage
from forgecv.features.snapshot.viewmodel import SnapshotViewModel
from forgecv.features.tag.api import build_service as build_tag
from forgecv.platform.adapters.db.session import SessionFactory
from forgecv.platform.ui.kit.manager import UiManager

ROUTE = "snapshot"
TITLE = "版本快照"


class Host(Protocol):
    """组合根需要提供的最小接口。"""

    sessions: SessionFactory
    ui: UiManager


def build_service(sessions: SessionFactory) -> SnapshotService:
    """构造快照服务。"""
    resume = build_resume(sessions)
    renderer = ResumeRenderer(
        resume=resume,
        profile=build_profile(sessions),
        educations=build_education(sessions),
        experiences=build_experience(sessions),
        projects=build_project(sessions),
        skills=build_skill(sessions),
        tags=build_tag(sessions),
    )
    return SnapshotService(resume, renderer)


def register(host: Host) -> None:
    """注册路由。"""
    resume = build_resume(host.sessions)
    service = build_service(host.sessions)
    host.ui.pages.register(
        ROUTE,
        TITLE,
        lambda: SnapshotPage(SnapshotViewModel(resume, service)),
    )
