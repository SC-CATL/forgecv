"""自检：数据库可迁移、Qt 可加载、令牌可读；输出 JSON 并以退出码表态。"""

from __future__ import annotations

import json
import os
import sys
from collections.abc import Callable

from sqlalchemy import text

from forgecv.platform.adapters.db.engine import create_engine_for
from forgecv.platform.adapters.db.migrate import upgrade
from forgecv.platform.config import Settings
from forgecv.platform.observability.logging import configure_logging

Check = tuple[str, Callable[[Settings], str]]


def _check_database(settings: Settings) -> str:
    """迁移到 head 并执行一次查询。"""
    upgrade(settings)
    engine = create_engine_for(settings)
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1")).scalar_one()
    finally:
        engine.dispose()
    return "ok"


def _check_qt(_settings: Settings) -> str:
    """离屏创建 QApplication，验证绑定与插件可用。"""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from forgecv.platform.ui.qt import BINDING, QtWidgets

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    app.setApplicationName("forgecv-self-test")
    return BINDING


def _check_tokens(_settings: Settings) -> str:
    """令牌文件可解析且至少有一种模式。"""
    from forgecv.platform.ui.kit.theme import load_tokens

    tokens = load_tokens()
    return f"{len(tokens['light'])} tokens"


def checks() -> tuple[Check, ...]:
    """自检项清单，新增能力时在此追加。"""
    return (
        ("database", _check_database),
        ("qt", _check_qt),
        ("tokens", _check_tokens),
    )


def run_self_test(settings: Settings) -> int:
    """逐项执行，任一失败即返回 1。"""
    configure_logging(settings.log_level)
    results: dict[str, str] = {}
    failures = 0
    for name, check in checks():
        try:
            results[name] = check(settings)
        except Exception as exc:  # 自检需要汇总全部失败
            results[name] = f"fail: {type(exc).__name__}: {exc}"
            failures += 1
    payload = {"ok": failures == 0, "python": sys.version.split()[0], "checks": results}
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if failures == 0 else 1
