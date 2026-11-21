"""视图模型：候选人表单与证书列表。"""

from __future__ import annotations

from forgecv.features.profile.models import Candidate
from forgecv.features.profile.schemas import CandidateInput, CertificateInput
from forgecv.features.profile.service import ProfileService
from forgecv.platform.ui.qt import QtCore, Signal


class ProfileViewModel(QtCore.QObject):
    """个人信息页状态。"""

    status_changed = Signal(str)
    candidate_changed = Signal(object)
    certificates_changed = Signal(object)

    def __init__(self, service: ProfileService) -> None:
        """注入服务。"""
        super().__init__()
        self._service = service
        self._candidate: Candidate | None = None

    @property
    def candidate(self) -> Candidate | None:
        """当前已加载的候选人。"""
        return self._candidate

    def load(self) -> None:
        """加载档案与证书。"""
        self._candidate = self._service.load()
        self.candidate_changed.emit(self._candidate)
        self.certificates_changed.emit(self._service.certificates())
        if self._candidate is None:
            self.status_changed.emit("尚未建档，填写后点击保存")
            return
        self.status_changed.emit("已加载个人信息")

    def save(self, data: CandidateInput) -> bool:
        """保存档案。"""
        result = self._service.save(data)
        if not result.is_ok:
            self.status_changed.emit(f"保存失败：{result.error()}")
            return False
        self._candidate = result.unwrap()
        self.candidate_changed.emit(self._candidate)
        self.status_changed.emit("个人信息已保存")
        return True

    def add_certificate(self, data: CertificateInput) -> bool:
        """新增证书并刷新列表。"""
        result = self._service.add_certificate(data)
        if not result.is_ok:
            self.status_changed.emit(f"新增证书失败：{result.error()}")
            return False
        self.certificates_changed.emit(self._service.certificates())
        self.status_changed.emit("证书已添加")
        return True

    def delete_certificate(self, certificate_id: int) -> bool:
        """删除证书并刷新列表。"""
        result = self._service.delete_certificate(certificate_id)
        if not result.is_ok:
            self.status_changed.emit(f"删除证书失败：{result.error()}")
            return False
        self.certificates_changed.emit(self._service.certificates())
        self.status_changed.emit("证书已删除")
        return True
