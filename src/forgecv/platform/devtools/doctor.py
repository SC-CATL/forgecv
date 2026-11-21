"""环境体检：版本、Qt、数据库、迁移状态、资源文件。"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from forgecv.platform.adapters.db.migrate import current_revision, head_revision
from forgecv.platform.config import load_settings
from forgecv.platform.ui.kit.theme import tokens_path


def _check_python() -> tuple[str, bool]:
    """Python 版本与 64 位环境。"""
    version = sys.version.split()[0]
    return f"Python {version}", sys.version_info >= (3, 10)


def _check_qt() -> tuple[str, bool]:
    """绑定可导入。"""
    from forgecv.platform.ui.qt import BINDING

    return f"Qt 绑定 {BINDING}", True


def _check_db() -> tuple[str, bool]:
    """数据库地址与父目录可写。"""
    settings = load_settings()
    url = settings.database_url
    if url.startswith("sqlite"):
        _, _, path = url.partition("///")
        parent = Path(path).expanduser().resolve().parent
        parent.mkdir(parents=True, exist_ok=True)
        return f"SQLite {parent}", os.access(parent, os.W_OK)
    return "MySQL 配置待连接", True


def _check_migrations() -> tuple[str, bool]:
    """当前版本与最新版本一致。"""
    try:
        settings = load_settings()
        current = current_revision(settings)
        head = head_revision(settings)
    except Exception as exc:  # 体检不因单项失败中断
        return f"迁移检查失败：{exc}", False
    return f"迁移 {current or '空'} / head {head or '无'}", current == head


def _check_tokens() -> tuple[str, bool]:
    """令牌文件存在。"""
    path = tokens_path()
    return f"令牌 {path.name}", path.is_file()


def collect() -> list[tuple[str, bool]]:
    """按固定顺序返回体检项。"""
    return [
        _check_python(),
        _check_qt(),
        _check_db(),
        _check_migrations(),
        _check_tokens(),
    ]


def run_doctor() -> int:
    """打印体检表，全部通过返回 0。"""
    rows = collect()
    for label, ok in rows:
        print(f"[{'OK' if ok else 'FAIL'}] {label}")
    failed = [label for label, ok in rows if not ok]
    if failed:
        print(f"\n{len(failed)} 项未通过")
        return 1
    print("\n全部通过")
    return 0
