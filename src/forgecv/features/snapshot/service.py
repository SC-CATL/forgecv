"""快照服务：保存渲染结果、对比两版文本差异。"""

from __future__ import annotations

import difflib

from forgecv.features.resume.models import ResumeVersion, Snapshot
from forgecv.features.resume.render import ResumeRenderer, render_text
from forgecv.features.resume.service import ResumeService
from forgecv.platform.core.errors import ValidationError
from forgecv.platform.core.result import Result


class SnapshotService:
    """快照与 Diff。"""

    def __init__(self, resume: ResumeService, renderer: ResumeRenderer) -> None:
        """注入版本服务与渲染器。"""
        self._resume = resume
        self._renderer = renderer

    def create(self, version: ResumeVersion, label: str) -> Result[Snapshot, ValidationError]:
        """保存当前版本的渲染文本。"""
        document = self._renderer.build(version)
        if not document.full_name:
            return Result.err(ValidationError("缺少姓名，快照内容不完整"))
        payload = {
            "text": render_text(document),
            "version": version.name,
            "target_role": version.target_role,
        }
        result = self._resume.create_snapshot(version.id, label, payload)
        if not result.is_ok:
            return Result.err(ValidationError(str(result.error())))
        return Result.ok(result.unwrap())

    def snapshots(self, version_id: int) -> list[Snapshot]:
        """版本快照列表。"""
        return self._resume.snapshots(version_id)

    @staticmethod
    def diff_text(before: Snapshot, after: Snapshot) -> str:
        """两版文本的行级差异。"""
        old = str(before.payload.get("text", "")).splitlines()
        new = str(after.payload.get("text", "")).splitlines()
        lines = difflib.unified_diff(
            old,
            new,
            fromfile=f"{before.id} · {before.label or '未命名'}",
            tofile=f"{after.id} · {after.label or '未命名'}",
            lineterm="",
        )
        return "\n".join(lines) or "两版内容一致。"
