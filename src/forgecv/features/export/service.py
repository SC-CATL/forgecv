"""导出服务：校验、命名、落盘。"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from forgecv.features.export.docx_writer import write_docx
from forgecv.features.resume.checks import ResumeCheckService
from forgecv.features.resume.document import ResumeDocument
from forgecv.features.resume.models import ResumeVersion
from forgecv.features.resume.render import ResumeRenderer
from forgecv.platform.core.errors import ValidationError
from forgecv.platform.core.result import Result

INVALID_CHARS = '\\/:*?"<>|'
DEFAULT_FOLDER = "ForgeCV"


def safe_name(value: str) -> str:
    """去掉文件名非法字符与首尾空白。"""
    cleaned = "".join("_" if char in INVALID_CHARS else char for char in value).strip()
    return cleaned or "未命名"


def default_output_dir() -> Path:
    """默认导出到「文档/ForgeCV」。"""
    return Path.home() / "Documents" / DEFAULT_FOLDER


def unique_path(folder: Path, stem: str) -> Path:
    """同名文件追加序号，不覆盖。"""
    candidate = folder / f"{stem}.docx"
    index = 2
    while candidate.exists():
        candidate = folder / f"{stem}-{index}.docx"
        index += 1
    return candidate


class ExportService:
    """把版本渲染成 Word 并写出。"""

    def __init__(
        self, renderer: ResumeRenderer, checks: ResumeCheckService
    ) -> None:
        """注入渲染器与检查器。"""
        self._renderer = renderer
        self._checks = checks

    def inspect(self, version: ResumeVersion) -> tuple[ResumeDocument, list[str]]:
        """返回文档与阻断原因，供界面预检。"""
        document = self._renderer.build(version)
        blocking = [
            issue.message
            for issue in self._checks.issues(document)
            if issue.level == "error"
        ]
        return document, blocking

    def export(
        self, version: ResumeVersion, output_dir: Path | None = None
    ) -> Result[Path, ValidationError]:
        """生成 docx；可预期失败用 Result 返回。"""
        document = self._renderer.build(version)
        if not document.full_name:
            return Result.err(ValidationError("缺少姓名，无法导出", field="full_name"))
        folder = output_dir or default_output_dir()
        stem = "-".join(
            (
                safe_name(document.full_name),
                safe_name(document.target_role or "通用"),
                datetime.now().strftime("%Y%m%d-%H%M"),
            )
        )
        try:
            return Result.ok(write_docx(document, unique_path(folder, stem)))
        except OSError as error:
            return Result.err(ValidationError(f"写入失败：{error}"))
