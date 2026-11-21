"""开发工具命令行：环境体检。"""

from __future__ import annotations


def doctor_main() -> int:
    """输出环境检查结果，失败返回非零。"""
    from forgecv.platform.devtools.doctor import run_doctor

    return run_doctor()
