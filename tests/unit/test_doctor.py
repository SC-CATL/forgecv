"""环境体检：结构完整，迁移后全绿。"""

from __future__ import annotations

from forgecv.platform.adapters.db.migrate import upgrade
from forgecv.platform.config import Settings
from forgecv.platform.devtools.doctor import collect, run_doctor


def test_collect_returns_all_checks(settings: Settings, monkeypatch) -> None:
    """体检项齐全且不抛异常。"""
    monkeypatch.setenv("DATABASE_URL", settings.database_url)
    rows = collect()
    assert len(rows) == 5
    assert all(isinstance(label, str) and label for label, _ok in rows)


def test_doctor_passes_after_migration(settings: Settings, monkeypatch, capsys) -> None:
    """迁移到 head 后体检全绿。"""
    monkeypatch.setenv("DATABASE_URL", settings.database_url)
    upgrade(settings)
    assert run_doctor() == 0
    assert "全部通过" in capsys.readouterr().out
