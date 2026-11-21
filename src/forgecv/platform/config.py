"""配置：环境变量优先，缺省值保证零配置可跑。"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

APP_DIR_NAME = "ForgeCV"
THEMES = ("system", "light", "dark", "high_contrast")


@dataclass(frozen=True, slots=True)
class Settings:
    """运行期配置。"""

    database_url: str
    app_title: str = "ForgeCV 工程师简历工坊"
    log_level: str = "INFO"
    environment: str = "dev"
    theme: str = "system"
    update_channel: str = "stable"
    dev: bool = False
    mock: bool = False


def _default_database_url() -> str:
    """本地默认库放在 %LOCALAPPDATA%，测试环境用内存库。"""
    if os.environ.get("ENVIRONMENT") == "test":
        return "sqlite+pysqlite:///:memory:"
    base = Path(os.environ.get("LOCALAPPDATA", Path.home())) / APP_DIR_NAME
    base.mkdir(parents=True, exist_ok=True)
    return f"sqlite+pysqlite:///{(base / 'app.db').as_posix()}"


def load_settings() -> Settings:
    """读取环境变量，未设置时用默认值。"""
    return Settings(
        database_url=os.environ.get("DATABASE_URL") or _default_database_url(),
        log_level=os.environ.get("LOG_LEVEL", "INFO"),
        environment=os.environ.get("ENVIRONMENT", "dev"),
        theme=os.environ.get("THEME", "system"),
        update_channel=os.environ.get("UPDATE_CHANNEL", "stable"),
    )
