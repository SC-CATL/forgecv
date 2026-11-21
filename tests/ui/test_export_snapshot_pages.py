"""导出页与快照页的装配与交互。"""

from __future__ import annotations

from pathlib import Path

import pytest

from forgecv.features.export.api import build_service as build_export
from forgecv.features.export.view import ExportPage
from forgecv.features.export.viewmodel import ExportViewModel
from forgecv.features.project.api import build_service as build_project
from forgecv.features.project.schemas import ProjectInput
from forgecv.features.resume.api import build_service as build_resume
from forgecv.features.resume.schemas import VersionInput
from forgecv.features.snapshot.api import build_service as build_snapshot
from forgecv.features.snapshot.view import SnapshotPage
from forgecv.features.snapshot.viewmodel import SnapshotViewModel
from forgecv.platform.adapters.db.session import SessionFactory

pytestmark = pytest.mark.ui


def test_export_page_writes_docx(
    qtbot, sessions: SessionFactory, candidate: int, tmp_path: Path
) -> None:
    """选择版本、指定目录并导出。"""
    build_project(sessions).add(ProjectInput(name="网关", direction="后端"))
    resume = build_resume(sessions)
    resume.create_version(VersionInput(name="后端版", target_role="后端工程师")).unwrap()
    page = ExportPage(ExportViewModel(resume, build_export(sessions)))
    qtbot.addWidget(page)
    assert page._version.count() == 1
    page._folder.setText(str(tmp_path))
    page._export()
    files = list(tmp_path.glob("*.docx"))
    assert len(files) == 1
    assert "已导出" in page._status.text()


def test_snapshot_page_compares(
    qtbot, sessions: SessionFactory, candidate: int
) -> None:
    """保存两份快照并对比。"""
    build_project(sessions).add(ProjectInput(name="网关", direction="后端"))
    resume = build_resume(sessions)
    resume.create_version(VersionInput(name="后端版")).unwrap()
    page = SnapshotPage(SnapshotViewModel(resume, build_snapshot(sessions)))
    qtbot.addWidget(page)
    assert page._version.count() == 1
    page._label.setText("初版")
    page._create()
    page._label.setText("第二版")
    page._create()
    assert page._list.count() == 2
    page._before.setCurrentIndex(0)
    page._after.setCurrentIndex(1)
    page._compare()
    assert "快照" in page._diff.toPlainText() or "两版" in page._diff.toPlainText()
