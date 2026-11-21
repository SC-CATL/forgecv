"""配置加载与环境变量优先级。"""

from __future__ import annotations

from forgecv.platform.config import THEMES, load_settings


def test_defaults_are_usable(monkeypatch) -> None:
    """无环境变量时也能构造出可用配置。"""
    for name in ("DATABASE_URL", "LOG_LEVEL", "ENVIRONMENT", "THEME"):
        monkeypatch.delenv(name, raising=False)
    settings = load_settings()
    assert settings.database_url.startswith("sqlite")
    assert settings.log_level == "INFO"
    assert settings.theme in THEMES


def test_env_overrides_defaults(monkeypatch) -> None:
    """环境变量优先于默认值。"""
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:///:memory:")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("THEME", "dark")
    settings = load_settings()
    assert settings.database_url == "sqlite+pysqlite:///:memory:"
    assert settings.log_level == "DEBUG"
    assert settings.theme == "dark"
