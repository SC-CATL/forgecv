"""根目录启动器：优先切换到项目 .venv，再转发到 forgecv.__main__:main。"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NO_REEXEC_ENV = "FORGECV_NO_REEXEC"


def _venv_python() -> Path | None:
    """返回项目虚拟环境解释器，找不到时为 None。"""
    for relative in (".venv/Scripts/python.exe", ".venv/bin/python"):
        candidate = ROOT / relative
        if candidate.is_file():
            return candidate
    return None


def _ensure_venv() -> None:
    """系统 Python 启动时自动切换到项目 .venv，避免依赖缺失。"""
    if os.environ.get(NO_REEXEC_ENV):
        return
    target = _venv_python()
    if target is None:
        return
    try:
        if Path(sys.executable).samefile(target):
            return
    except OSError:
        pass
    try:
        os.execv(  # noqa: S606 - 这里必须替换为项目解释器
            str(target), [str(target), str(ROOT / "main.py"), *sys.argv[1:]]
        )
    except OSError:
        return


def _ensure_src_on_path() -> None:
    """未安装包时把 src/ 加入导入路径。"""
    src = ROOT / "src"
    if src.is_dir() and str(src) not in sys.path:
        sys.path.insert(0, str(src))


def main() -> int:
    """启动应用并返回退出码。"""
    _ensure_venv()
    _ensure_src_on_path()
    try:
        from forgecv.__main__ import main as app_main
    except ImportError as exc:  # 路径兜底需要延迟导入
        print(f"无法导入 forgecv，请先执行 uv sync：{exc}", file=sys.stderr)
        return 2
    return app_main()


if __name__ == "__main__":
    raise SystemExit(main())
