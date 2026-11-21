"""视图模型：版本快照与差异。"""

from __future__ import annotations

from forgecv.features.resume.models import ResumeVersion, Snapshot
from forgecv.features.resume.service import ResumeService
from forgecv.features.snapshot.service import SnapshotService
from forgecv.platform.ui.qt import QtCore, Signal


class SnapshotViewModel(QtCore.QObject):
    """快照页状态。"""

    versions_changed = Signal(object)
    snapshots_changed = Signal(object)
    diff_changed = Signal(str)
    status_changed = Signal(str)

    def __init__(self, resume: ResumeService, service: SnapshotService) -> None:
        """注入版本与快照服务。"""
        super().__init__()
        self._resume = resume
        self._service = service
        self._versions: list[ResumeVersion] = []
        self._current: ResumeVersion | None = None
        self._snapshots: list[Snapshot] = []

    @property
    def versions(self) -> list[ResumeVersion]:
        """版本缓存。"""
        return self._versions

    def load(self) -> None:
        """加载版本并选中第一个。"""
        self._versions = self._resume.versions()
        self.versions_changed.emit(self._versions)
        if not self._versions:
            self._snapshots = []
            self.snapshots_changed.emit([])
            self.status_changed.emit("还没有简历版本")
            return
        self._current = self._versions[0]
        self._reload_snapshots()

    def select(self, version_id: int) -> None:
        """切换版本。"""
        version = next((row for row in self._versions if row.id == version_id), None)
        if version is None:
            return
        self._current = version
        self._reload_snapshots()

    def create(self, label: str) -> bool:
        """为当前版本创建快照。"""
        if self._current is None:
            self.status_changed.emit("请先选择版本")
            return False
        result = self._service.create(self._current, label)
        if not result.is_ok:
            self.status_changed.emit(f"快照失败：{result.error()}")
            return False
        self._reload_snapshots()
        self.status_changed.emit("快照已保存")
        return True

    def compare(self, before_id: int, after_id: int) -> None:
        """对比两份快照。"""
        before = self._find(before_id)
        after = self._find(after_id)
        if before is None or after is None:
            self.diff_changed.emit("请选择两份快照")
            return
        self.diff_changed.emit(self._service.diff_text(before, after))

    def _reload_snapshots(self) -> None:
        """刷新快照列表。"""
        if self._current is None:
            return
        self._snapshots = self._service.snapshots(self._current.id)
        self.snapshots_changed.emit(self._snapshots)
        self.status_changed.emit(f"{len(self._snapshots)} 份快照")

    def _find(self, snapshot_id: int) -> Snapshot | None:
        """按 id 找快照。"""
        return next((row for row in self._snapshots if row.id == snapshot_id), None)
