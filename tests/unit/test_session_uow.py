"""工作单元：提交、回滚、未进入保护。"""

from __future__ import annotations

import pytest

from forgecv.features.settings.models import AppSetting
from forgecv.platform.adapters.db.session import (
    SessionFactory,
    SessionUnitOfWork,
    session_scope,
)


def test_commit_persists_changes(sessions: SessionFactory) -> None:
    """正常退出即提交。"""
    with SessionUnitOfWork(sessions) as uow:
        uow.session.add(AppSetting(key="k", value="v"))
    with session_scope(sessions) as session:
        assert session.get(AppSetting, "k") is not None


def test_exception_rolls_back(sessions: SessionFactory) -> None:
    """异常退出即回滚。"""
    with pytest.raises(RuntimeError), SessionUnitOfWork(sessions) as uow:
        uow.session.add(AppSetting(key="k", value="v"))
        raise RuntimeError("回滚")
    with session_scope(sessions) as session:
        assert session.get(AppSetting, "k") is None


def test_session_before_enter_is_rejected(sessions: SessionFactory) -> None:
    """未进入工作单元时取会话立即失败。"""
    uow = SessionUnitOfWork(sessions)
    with pytest.raises(RuntimeError):
        _ = uow.session
