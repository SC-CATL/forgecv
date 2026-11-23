"""迁移链：升级建表、回滚删表、版本对齐。"""

from __future__ import annotations

import pytest
from sqlalchemy import inspect

from forgecv.platform.adapters.db.engine import create_engine_for
from forgecv.platform.adapters.db.migrate import (
    current_revision,
    downgrade,
    head_revision,
    upgrade,
)
from forgecv.platform.config import Settings

pytestmark = pytest.mark.integration


def _tables(settings: Settings) -> set[str]:
    """当前库中的表名集合。"""
    engine = create_engine_for(settings)
    try:
        return set(inspect(engine).get_table_names())
    finally:
        engine.dispose()


def _columns(settings: Settings, table: str) -> set[str]:
    """指定表的列名集合。"""
    engine = create_engine_for(settings)
    try:
        return {column["name"] for column in inspect(engine).get_columns(table)}
    finally:
        engine.dispose()


def test_upgrade_reaches_head(settings: Settings) -> None:
    """升级后版本与脚本目录一致。"""
    upgrade(settings)
    tables = _tables(settings)
    assert "app_settings" in tables
    assert {"candidate", "educations", "projects", "skills", "resume_versions"} <= tables
    assert {"market_key", "market_tag"} <= _columns(settings, "skills")
    assert current_revision(settings) == head_revision(settings)


def test_downgrade_drops_table(settings: Settings) -> None:
    """回滚到 base 后业务表消失。"""
    upgrade(settings)
    downgrade(settings, "base")
    assert "app_settings" not in _tables(settings)


def test_upgrade_is_idempotent(settings: Settings) -> None:
    """重复升级不报错。"""
    upgrade(settings)
    upgrade(settings)
    assert current_revision(settings) == head_revision(settings)
