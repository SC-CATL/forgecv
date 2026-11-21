"""设置切片的仓储与服务。"""

from __future__ import annotations

import pytest

from forgecv.features.settings.api import build_service
from forgecv.features.settings.repository import SettingsRepository
from forgecv.features.settings.service import DEFAULT_THEME, THEME_KEY
from forgecv.platform.adapters.db.session import SessionFactory


def test_missing_setting_returns_default(sessions: SessionFactory) -> None:
    """空表时返回默认主题。"""
    assert build_service(sessions).theme() == DEFAULT_THEME


def test_save_then_read_back(sessions: SessionFactory) -> None:
    """保存后能读回同一值。"""
    service = build_service(sessions)
    result = service.save_theme("dark")
    assert result.is_ok
    assert result.unwrap() == "dark"
    assert service.theme() == "dark"


def test_invalid_theme_is_rejected(sessions: SessionFactory) -> None:
    """非法主题返回错误且不落库。"""
    service = build_service(sessions)
    result = service.save_theme("neon")
    assert not result.is_ok
    assert service.theme() == DEFAULT_THEME


def test_corrupted_value_falls_back(sessions: SessionFactory) -> None:
    """历史脏数据不让界面崩溃。"""
    SettingsRepository(sessions).put(THEME_KEY, "neon")
    assert build_service(sessions).theme() == DEFAULT_THEME


def test_repository_reads_all_rows(sessions: SessionFactory) -> None:
    """all() 返回全部键值。"""
    repository = SettingsRepository(sessions)
    repository.put("a", "1")
    repository.put("b", "2")
    repository.put("a", "3")
    assert repository.all() == {"a": "3", "b": "2"}


def test_put_updates_existing_row(sessions: SessionFactory) -> None:
    """重复写入是更新而非插入。"""
    repository = SettingsRepository(sessions)
    repository.put("k", "v1")
    repository.put("k", "v2")
    assert repository.get("k") == "v2"


@pytest.mark.parametrize("mode", ["system", "light", "dark", "high_contrast"])
def test_every_supported_theme_is_accepted(sessions: SessionFactory, mode: str) -> None:
    """配置里声明的主题都能保存。"""
    assert build_service(sessions).save_theme(mode).is_ok
