"""工作经历页：新增、编辑与删除。"""

from __future__ import annotations

import pytest

from forgecv.features.experience.api import build_service
from forgecv.features.experience.view import ExperiencePage
from forgecv.features.experience.viewmodel import ExperienceViewModel
from forgecv.platform.adapters.db.session import SessionFactory

pytestmark = pytest.mark.ui


def _page(sessions: SessionFactory) -> ExperiencePage:
    return ExperiencePage(ExperienceViewModel(build_service(sessions)))


def test_create_edit_delete(qtbot, sessions: SessionFactory, candidate: int) -> None:
    """一条经历走完新增、选中回填、保存与删除。"""
    page = _page(sessions)
    qtbot.addWidget(page)
    page._company.setText("某公司")
    page._role.setText("后端")
    page._highlights.setPlainText("降低延迟\n提升覆盖率")
    page._save()
    assert len(page._vm.rows) == 1
    assert page._vm.rows[0].highlights == ["降低延迟", "提升覆盖率"]

    page._list.setCurrentRow(0)
    page._role.setText("高级后端")
    page._save()
    assert page._vm.rows[0].role == "高级后端"

    page._delete_current()
    assert page._vm.rows == []


def test_current_disables_end(qtbot, sessions: SessionFactory, candidate: int) -> None:
    """勾选在职后结束日期禁用。"""
    page = _page(sessions)
    qtbot.addWidget(page)
    page._current.setChecked(True)
    assert not page._end.isEnabled()
