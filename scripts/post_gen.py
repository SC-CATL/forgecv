"""生成后收尾：有 uv 就同步依赖，否则打印手动步骤。"""

from __future__ import annotations

import shutil
import subprocess

MANUAL = """未检测到 uv。请先安装：https://docs.astral.sh/uv/
然后执行：
    uv sync
    uv run dev
"""


def main() -> int:
    """同步依赖；失败不阻断生成，只提示。"""
    if shutil.which("uv") is None:
        print(MANUAL)
        return 0
    print("检测到 uv，开始同步依赖 ...")
    result = subprocess.run(["uv", "sync"], check=False)
    if result.returncode != 0:
        print("依赖同步失败，请手动执行：uv sync")
        return 0
    print("完成。启动：uv run dev")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
