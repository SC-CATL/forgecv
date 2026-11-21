"""引擎构造：SQLite 自动建目录并开启外键，MySQL 直接连接。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sqlalchemy import Engine, create_engine, event

from forgecv.platform.config import Settings

MEMORY_URL = "sqlite+pysqlite:///:memory:"


def ensure_parent_dir(database_url: str) -> None:
    """SQLite 文件库先建父目录，避免首次启动失败。"""
    if not database_url.startswith("sqlite"):
        return
    _, _, path = database_url.partition("///")
    if not path or path.startswith(":memory:"):
        return
    Path(path).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)


def _enable_foreign_keys(engine: Engine) -> None:
    """SQLite 默认关闭外键约束，这里逐连接打开。"""

    @event.listens_for(engine, "connect")
    def _set_pragma(dbapi_connection: Any, _record: Any) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def create_engine_for(settings: Settings) -> Engine:
    """按配置创建引擎；mock 模式使用内存库。"""
    url = MEMORY_URL if settings.mock else settings.database_url
    ensure_parent_dir(url)
    kwargs: dict[str, Any] = {"pool_pre_ping": True}
    if url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
    engine = create_engine(url, **kwargs)
    if url.startswith("sqlite"):
        _enable_foreign_keys(engine)
    return engine
