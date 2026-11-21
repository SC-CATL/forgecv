"""标签页：新增、编辑与删除。"""

from __future__ import annotations

import pytest

from forgecv.features.tag.api import build_service
from forgecv.features.tag.view import TagPage
from forgecv.features.tag.viewmodel import TagViewModel
from forgecv.platform.adapters.db.session import SessionFactory

pytestmark = pytest.mark.ui


def test_create_edit_delete(qtbot, sessions: SessionFactory) -> None:
    """一个标签走完新增、选中回填、改名与删除。"""
    page = TagPage(TagViewModel(build_service(sessions)))
    qtbot.addWidget(page)
    page._name.setText("Python")
    page._save()
    assert len(page._vm.rows) == 1
    assert page._vm.rows[0].dimension == "language"

    page._list.setCurrentRow(0)
    page._name.setText("Python3")
    page._dimension.setCurrentIndex(1)
    page._save()
    assert page._vm.rows[0].name == "Python3"
    assert page._vm.rows[0].dimension == "domain"

    page._delete_current()
    assert page._vm.rows == []
