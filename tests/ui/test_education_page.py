"""学历页：新增、编辑、选中与删除。"""

from __future__ import annotations

import pytest

from forgecv.features.education.api import build_service
from forgecv.features.education.view import EducationPage
from forgecv.features.education.viewmodel import EducationViewModel
from forgecv.platform.adapters.db.session import SessionFactory

pytestmark = pytest.mark.ui


def _page(sessions: SessionFactory) -> EducationPage:
    return EducationPage(EducationViewModel(build_service(sessions)))


def test_create_edit_delete(qtbot, sessions: SessionFactory, candidate: int) -> None:
    """一条学历走完新增、选中回填、保存与删除。"""
    page = _page(sessions)
    qtbot.addWidget(page)
    page._school.setText("浙江大学")
    page._major.setText("软件工程")
    page._courses.setText("操作系统、数据库")
    page._save()
    assert len(page._vm.rows) == 1
    assert page._vm.rows[0].courses == ["操作系统", "数据库"]

    page._list.setCurrentRow(0)
    page._major.setText("计算机科学")
    page._save()
    assert page._vm.rows[0].major == "计算机科学"

    page._delete_current()
    assert page._vm.rows == []


def test_current_disables_end_date(qtbot, sessions: SessionFactory, candidate: int) -> None:
    """勾选在读时结束日期不可编辑。"""
    page = _page(sessions)
    qtbot.addWidget(page)
    page._current.setChecked(True)
    assert not page._end.isEnabled()


def test_move_reorders_rows(qtbot, sessions: SessionFactory, candidate: int) -> None:
    """上移下移会重写排序号。"""
    page = _page(sessions)
    qtbot.addWidget(page)
    page._school.setText("A 大学")
    page._save()
    page._new()
    page._school.setText("B 大学")
    page._save()
    assert len(page._vm.rows) == 2
    page._list.setCurrentRow(1)
    page._move(-1)
    assert page._vm.rows[0].school == "B 大学"
