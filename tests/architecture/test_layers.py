"""分层红线：绑定只在 qt.py、platform 不反向依赖业务。"""

from __future__ import annotations

import ast
from pathlib import Path

import forgecv

SRC = Path(forgecv.__file__).resolve().parent
QT_ENTRY = SRC / "platform" / "ui" / "qt.py"


def _imports(path: Path) -> set[str]:
    """收集文件的全部导入模块名。"""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


def test_binding_imported_only_in_qt_entry() -> None:
    """除入口外禁止直接 import PySide6 / PySide2。"""
    offenders = [
        path
        for path in SRC.rglob("*.py")
        if path != QT_ENTRY
        and any(name.split(".")[0] in {"PySide6", "PySide2"} for name in _imports(path))
    ]
    assert offenders == []


def test_platform_never_imports_business_layers() -> None:
    """platform 不得依赖 features 或 app。"""
    offenders: list[str] = []
    for path in (SRC / "platform").rglob("*.py"):
        for name in _imports(path):
            if name.startswith(("forgecv.features", "forgecv.app")):
                offenders.append(f"{path.name}: {name}")
    assert offenders == []


def test_features_never_import_app() -> None:
    """切片不得反向依赖组合根。"""
    offenders: list[str] = []
    for path in (SRC / "features").rglob("*.py"):
        for name in _imports(path):
            if name.startswith("forgecv.app"):
                offenders.append(f"{path.name}: {name}")
    assert offenders == []
