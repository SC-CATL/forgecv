"""Alembic 迁移：从仓库根定位配置，升级到 head。"""

from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import inspect

from forgecv.platform.adapters.db.engine import create_engine_for
from forgecv.platform.config import Settings


def find_repo_root(start: Path | None = None) -> Path:
    """向上查找 alembic.ini，找不到说明不在源码仓库中。"""
    current = (start or Path(__file__)).resolve()
    for candidate in (current, *current.parents):
        if (candidate / "alembic.ini").is_file():
            return candidate
    raise FileNotFoundError("未找到 alembic.ini，请从项目根目录运行")


def alembic_config(settings: Settings, root: Path | None = None) -> Config:
    """构造 Alembic 配置，URL 从应用配置注入。"""
    base = root or find_repo_root()
    config = Config(str(base / "alembic.ini"))
    config.set_main_option("script_location", str(base / "alembic"))
    config.set_main_option("sqlalchemy.url", settings.database_url.replace("%", "%%"))
    return config


def upgrade(settings: Settings, revision: str = "head") -> None:
    """升级到指定版本，默认 head。"""
    command.upgrade(alembic_config(settings), revision)


def downgrade(settings: Settings, revision: str) -> None:
    """回滚到指定版本。"""
    command.downgrade(alembic_config(settings), revision)


def head_revision(settings: Settings) -> str | None:
    """脚本目录中的最新版本号。"""
    script = ScriptDirectory.from_config(alembic_config(settings))
    return script.get_current_head()


def current_revision(settings: Settings) -> str | None:
    """数据库当前版本号，未建表时为 None。"""
    engine = create_engine_for(settings)
    try:
        with engine.connect() as connection:
            if not inspect(connection).has_table("alembic_version"):
                return None
            return MigrationContext.configure(connection).get_current_revision()
    finally:
        engine.dispose()
