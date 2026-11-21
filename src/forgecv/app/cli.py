"""开发命令入口：`dev` 先迁移再进窗口。"""

from __future__ import annotations

from dataclasses import replace

from forgecv.platform.adapters.db.migrate import upgrade
from forgecv.platform.config import load_settings


def dev_main() -> int:
    """一键开发启动：迁移到 head，再启动应用。"""
    settings = replace(load_settings(), dev=True)
    upgrade(settings)
    from forgecv.app.bootstrap import run

    return run(settings)
