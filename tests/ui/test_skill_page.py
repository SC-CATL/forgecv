"""技能页：技能保存与证据链。"""

from __future__ import annotations

import pytest

from forgecv.features.experience.api import build_service as build_experience
from forgecv.features.project.api import build_service as build_project
from forgecv.features.project.schemas import ProjectInput
from forgecv.features.skill.api import build_service
from forgecv.features.skill.view import SkillPage
from forgecv.features.skill.viewmodel import SkillViewModel
from forgecv.platform.adapters.db.session import SessionFactory

pytestmark = pytest.mark.ui


def _page(sessions: SessionFactory) -> SkillPage:
    return SkillPage(
        SkillViewModel(
            build_service(sessions),
            build_project(sessions),
            build_experience(sessions),
        )
    )


def test_create_skill_and_evidence(
    qtbot, sessions: SessionFactory, candidate: int
) -> None:
    """新增技能后挂一条项目证据，再删除证据与技能。"""
    project = build_project(sessions).add(
        ProjectInput(name="网关", direction="后端")
    ).unwrap()
    page = _page(sessions)
    qtbot.addWidget(page)
    page._name.setText("Python")
    page._level.setCurrentIndex(3)
    page._years.setValue(5)
    page._score.setValue(90)
    page._save()
    assert len(page._vm.rows) == 1
    assert page._vm.rows[0].level == 4

    page._source.setCurrentIndex(0)
    assert page._source.currentData() == f"project:{project.id}"
    page._statement.setText("负责网关核心模块")
    page._metric.setText("P99 45ms")
    page._add_evidence()
    assert page._evidence.count() == 1

    page._evidence.setCurrentRow(0)
    page._remove_evidence()
    assert page._evidence.count() == 0

    page._delete_current()
    assert page._vm.rows == []


def test_save_without_selection_keeps_form(
    qtbot, sessions: SessionFactory, candidate: int
) -> None:
    """新增后表单停留在新记录，可直接继续编辑。"""
    page = _page(sessions)
    qtbot.addWidget(page)
    page._name.setText("Go")
    page._save()
    page._notes.setPlainText("并发")
    page._save()
    assert len(page._vm.rows) == 1
    assert page._vm.rows[0].notes == "并发"
