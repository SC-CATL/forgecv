"""领域服务：附件元数据登记规则。"""

from __future__ import annotations

from string import hexdigits

from forgecv.features.attachment.models import Attachment
from forgecv.features.attachment.repository import AttachmentRepository
from forgecv.features.attachment.schemas import AttachmentInput
from forgecv.platform.core.errors import NotFoundError, ValidationError
from forgecv.platform.core.result import Result
from forgecv.platform.core.validation import clean

OWNER_TYPES = ("candidate", "education", "experience", "project", "certificate", "resume_version")
SHA256_HEX_LENGTH = 64


class AttachmentService:
    """附件元数据用例入口。"""

    def __init__(self, repository: AttachmentRepository) -> None:
        """注入仓储。"""
        self._repository = repository

    def list_for(self, owner_type: str, owner_id: int) -> list[Attachment]:
        """某个实体的附件。"""
        return self._repository.list_for(owner_type, owner_id)

    def register(self, data: AttachmentInput) -> Result[Attachment, ValidationError]:
        """校验后登记附件。"""
        if data.owner_type not in OWNER_TYPES:
            return Result.err(ValidationError(f"未知挂载类型：{data.owner_type}"))
        if data.owner_id <= 0:
            return Result.err(ValidationError("挂载对象 id 不合法"))
        file_name = clean(data.file_name)
        path = clean(data.path)
        if not file_name or not path:
            return Result.err(ValidationError("文件名与路径不能为空"))
        digest = clean(data.sha256).lower()
        if len(digest) != SHA256_HEX_LENGTH or any(char not in hexdigits for char in digest):
            return Result.err(ValidationError("sha256 必须是 64 位十六进制", field="sha256"))
        if data.size_bytes < 0:
            return Result.err(ValidationError("文件大小不能为负", field="size_bytes"))
        cleaned = AttachmentInput(
            owner_type=data.owner_type,
            owner_id=data.owner_id,
            file_name=file_name,
            path=path,
            sha256=digest,
            size_bytes=data.size_bytes,
            mime=clean(data.mime),
        )
        return Result.ok(self._repository.add(cleaned))

    def delete(self, attachment_id: int) -> Result[bool, NotFoundError]:
        """删除元数据。"""
        if self._repository.delete(attachment_id):
            return Result.ok(True)
        return Result.err(NotFoundError(f"附件不存在：{attachment_id}"))
