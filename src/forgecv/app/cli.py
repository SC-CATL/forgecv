"""开发命令入口：`dev` 迁移与窗口启动都交给 bootstrap。"""

from __future__ import annotations

from dataclasses import replace

from forgecv.platform.config import load_settings


def dev_main() -> int:
    """一键开发启动：标记开发模式后启动应用。"""
    settings = replace(load_settings(), dev=True)
    from forgecv.app.bootstrap import run

    return run(settings)
