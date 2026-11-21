"""视图模型：Word 导出。"""

from __future__ import annotations

from pathlib import Path

from forgecv.features.export.service import ExportService, default_output_dir
from forgecv.features.resume.models import ResumeVersion
from forgecv.features.resume.service import ResumeService
from forgecv.platform.ui.qt import QtCore, Signal


class ExportViewModel(QtCore.QObject):
    """导出页状态。"""

    versions_changed = Signal(object)
    checks_changed = Signal(object)
    path_changed = Signal(str)
    status_changed = Signal(str)

    def __init__(self, resume: ResumeService, service: ExportService) -> None:
        """注入版本服务与导出服务。"""
        super().__init__()
        self._resume = resume
        self._service = service
        self._versions: list[ResumeVersion] = []

    @property
    def versions(self) -> list[ResumeVersion]:
        """版本缓存。"""
        return self._versions

    def load(self) -> None:
        """加载版本并做一次预检。"""
        self._versions = self._resume.versions()
        self.versions_changed.emit(self._versions)
        if self._versions:
            self.select(self._versions[0].id)
        else:
            self.checks_changed.emit(["还没有简历版本，请先在「简历版本」页创建。"])
            self.status_changed.emit("共 0 个版本")

    def select(self, version_id: int) -> None:
        """切换版本并预检。"""
        version = next((row for row in self._versions if row.id == version_id), None)
        if version is None:
            return
        _document, blocking = self._service.inspect(version)
        self.checks_changed.emit(blocking or ["预检通过，可以导出。"])

    def export(self, version_id: int, output_dir: str) -> bool:
        """执行导出。"""
        version = next((row for row in self._versions if row.id == version_id), None)
        if version is None:
            self.status_changed.emit("请选择一个版本")
            return False
        folder = Path(output_dir).expanduser() if output_dir.strip() else None
        result = self._service.export(version, folder)
        if not result.is_ok:
            self.status_changed.emit(f"导出失败：{result.error()}")
            return False
        path = result.unwrap()
        self.path_changed.emit(str(path))
        self.status_changed.emit(f"已导出：{path.name}")
        return True

    @staticmethod
    def folder_hint() -> str:
        """默认导出目录。"""
        return str(default_output_dir())
