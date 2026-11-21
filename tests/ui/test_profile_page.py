"""个人信息页：保存、证书新增与删除。"""

from __future__ import annotations

import pytest

from forgecv.features.profile.api import build_service
from forgecv.features.profile.view import ProfilePage
from forgecv.features.profile.viewmodel import ProfileViewModel
from forgecv.platform.adapters.db.session import SessionFactory
from forgecv.platform.ui.qt import QtWidgets

pytestmark = pytest.mark.ui


def _page(sessions: SessionFactory) -> ProfilePage:
    page = ProfilePage(ProfileViewModel(build_service(sessions)))
    QtWidgets.QApplication.instance().processEvents()
    return page


def test_save_profile(qtbot, sessions: SessionFactory) -> None:
    """填写姓名并保存后能读回。"""
    page = _page(sessions)
    qtbot.addWidget(page)
    page._edits["full_name"].setText("李四")
    page._edits["city"].setText("上海")
    page._save()
    loaded = build_service(sessions).load()
    assert loaded is not None
    assert loaded.full_name == "李四"
    assert loaded.city == "上海"


def test_add_and_delete_certificate(qtbot, sessions: SessionFactory) -> None:
    """证书快速新增与删除。"""
    page = _page(sessions)
    qtbot.addWidget(page)
    page._cert_name.setText("CET-6")
    page._cert_issuer.setText("教育部")
    page._add_certificate()
    assert page._certificates.count() == 1
    page._certificates.setCurrentRow(0)
    page._delete_certificate()
    assert page._certificates.count() == 0


def test_empty_profile_shows_hint(qtbot, sessions: SessionFactory) -> None:
    """未建档时表单为空并提示。"""
    page = _page(sessions)
    qtbot.addWidget(page)
    assert page._edits["full_name"].text() == ""
    assert "尚未建档" in page._status.text()
