"""命令行入口：解析参数并分派到迁移、自检或图形启动。"""

from __future__ import annotations

import argparse
import sys
from dataclasses import replace

from forgecv import __version__
from forgecv.platform.config import Settings, load_settings


def build_parser() -> argparse.ArgumentParser:
    """构造参数解析器。"""
    parser = argparse.ArgumentParser(
        prog="forgecv",
        description="工程师简历工坊：学历时间轴、技能举证、项目标签与 Word 导出",
    )
    parser.add_argument("--version", action="store_true", help="打印版本并退出")
    parser.add_argument("--self-test", action="store_true", help="自检后退出")
    parser.add_argument("--migrate", action="store_true", help="执行数据库迁移后退出")
    parser.add_argument("--mock", action="store_true", help="使用内存适配器，不连数据库")
    parser.add_argument("--dev", action="store_true", help="开发模式：启用热重载与开发面板")
    return parser


def _resolve_settings(args: argparse.Namespace) -> Settings:
    """按命令行开关调整配置。"""
    settings = load_settings()
    return replace(settings, dev=args.dev, mock=args.mock)


def main(argv: list[str] | None = None) -> int:
    """进程入口，返回退出码。"""
    args = build_parser().parse_args(argv)
    if args.version:
        print(__version__)
        return 0

    settings = _resolve_settings(args)
    if args.migrate:
        from forgecv.platform.adapters.db.migrate import upgrade

        upgrade(settings)
        return 0
    if args.self_test:
        from forgecv.platform.selfcheck import run_self_test

        return run_self_test(settings)

    from forgecv.app.bootstrap import run

    return run(settings)


if __name__ == "__main__":
    sys.exit(main())
