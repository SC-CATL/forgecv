"""简历版本页：创建、勾选、预览与 JD 分析。"""

from __future__ import annotations

import pytest

from forgecv.features.education.api import build_service as build_education
from forgecv.features.experience.api import build_service as build_experience
from forgecv.features.profile.api import build_service as build_profile
from forgecv.features.project.api import build_service as build_project
from forgecv.features.project.schemas import ProjectInput
from forgecv.features.resume.api import build_service as build_resume
from forgecv.features.resume.checks import ResumeCheckService
from forgecv.features.resume.render import ResumeRenderer
from forgecv.features.resume.view import ResumePage
from forgecv.features.resume.viewmodel import ResumeViewModel
from forgecv.features.skill.api import build_service as build_skill
from forgecv.features.tag.api import build_service as build_tag
from forgecv.platform.adapters.db.session import SessionFactory
from forgecv.platform.ui.qt import QtCore

pytestmark = pytest.mark.ui


def _page(sessions: SessionFactory) -> ResumePage:
    """装配完整版本页。"""
    resume = build_resume(sessions)
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
    view_model = ResumeViewModel(
        resume=resume,
        renderer=renderer,
        checks=ResumeCheckService(skills),
        educations=educations,
        experiences=experiences,
        projects=projects,
        skills=skills,
        profile=profile,
        tags=tags,
    )
    return ResumePage(view_model)


def test_create_version_and_toggle_item(
    qtbot, sessions: SessionFactory, candidate: int
) -> None:
    """新建版本、勾选项目、预览包含项目、再取消。"""
    project = build_project(sessions).add(
        ProjectInput(name="网关", direction="后端", highlights=["QPS 提升 3 倍"])
    ).unwrap()
    page = _page(sessions)
    qtbot.addWidget(page)
    page._name.setText("后端版")
    page._create()
    assert page._versions.count() == 1
    assert "网关" in page._preview.toPlainText()

    key = f"project:{project.id}"
    for index in range(page._available.count()):
        item = page._available.item(index)
        if item.data(QtCore.Qt.ItemDataRole.UserRole) == key:
            item.setCheckState(QtCore.Qt.CheckState.Checked)
            break
    assert page._selected.count() == 1
    assert "后端版" in page._vm.current.name

    for index in range(page._available.count()):
        item = page._available.item(index)
        if item.data(QtCore.Qt.ItemDataRole.UserRole) == key:
            item.setCheckState(QtCore.Qt.CheckState.Unchecked)
            break
    assert page._selected.count() == 0


def test_analyze_jd_and_save_settings(
    qtbot, sessions: SessionFactory, candidate: int
) -> None:
    """JD 覆盖率写入标签，保存设置后目标岗位更新。"""
    page = _page(sessions)
    qtbot.addWidget(page)
    page._name.setText("后端版")
    page._create()
    page._target.setText("后端工程师")
    page._save_settings()
    assert page._vm.current is not None
    assert page._vm.current.target_role == "后端工程师"

    page._jd_text.setPlainText("要求 Python 与 Kubernetes")
    page._analyze()
    assert "覆盖率" in page._jd_result.text()
    assert "Kubernetes" in page._jd_result.text()
