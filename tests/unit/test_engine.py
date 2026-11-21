"""引擎构造：SQLite 目录、外键与 mock 内存库。"""

from __future__ import annotations

from pathlib import Path

from forgecv.platform.adapters.db.engine import (
    create_engine_for,
    ensure_parent_dir,
)
from forgecv.platform.config import Settings


def test_sqlite_foreign_keys_enabled(settings: Settings) -> None:
    """SQLite 连接打开外键约束。"""
    engine = create_engine_for(settings)
    try:
        with engine.connect() as connection:
            assert connection.exec_driver_sql("PRAGMA foreign_keys").scalar() == 1
    finally:
        engine.dispose()


def test_mock_mode_uses_memory_database() -> None:
    """mock 模式忽略配置里的文件地址。"""
    engine = create_engine_for(Settings(database_url="sqlite+pysqlite:///ignored.db", mock=True))
    try:
        assert engine.url.database == ":memory:"
    finally:
        engine.dispose()


def test_ensure_parent_dir_creates_folder(tmp_path: Path) -> None:
    """文件库父目录不存在时自动创建。"""
    target = tmp_path / "nested" / "app.db"
    ensure_parent_dir(f"sqlite+pysqlite:///{target.as_posix()}")
    assert target.parent.is_dir()


def test_non_sqlite_url_is_ignored(tmp_path: Path) -> None:
    """非 SQLite 地址不做本地目录处理。"""
    ensure_parent_dir("mysql+pymysql://user:pass@localhost/app")
    assert not (tmp_path / "mysql").exists()
