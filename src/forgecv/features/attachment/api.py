"""attachment 切片对外入口：服务构造。页面在 M2 后按需接入。"""

from __future__ import annotations

from forgecv.features.attachment.repository import AttachmentRepository
from forgecv.features.attachment.service import AttachmentService
from forgecv.platform.adapters.db.session import SessionFactory


def build_service(sessions: SessionFactory) -> AttachmentService:
    """构造切片服务。"""
    return AttachmentService(AttachmentRepository(sessions))
