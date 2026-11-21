"""attachment 服务：元数据登记规则。"""

from __future__ import annotations

from forgecv.features.attachment.api import build_service
from forgecv.features.attachment.schemas import AttachmentInput
from forgecv.platform.adapters.db.session import SessionFactory

DIGEST = "a" * 64


def _input(**overrides: object) -> AttachmentInput:
    """构造一条合法附件元数据。"""
    values: dict[str, object] = {
        "owner_type": "project",
        "owner_id": 1,
        "file_name": "arch.png",
        "path": "files/arch.png",
        "sha256": DIGEST,
        "size_bytes": 1024,
        "mime": "image/png",
    }
    values.update(overrides)
    return AttachmentInput(**values)  # type: ignore[arg-type]


def test_register_rejects_bad_digest(sessions: SessionFactory) -> None:
    """sha256 必须是 64 位十六进制。"""
    assert not build_service(sessions).register(_input(sha256="xyz")).is_ok


def test_register_rejects_unknown_owner(sessions: SessionFactory) -> None:
    """挂载类型白名单。"""
    assert not build_service(sessions).register(_input(owner_type="unknown")).is_ok


def test_register_list_and_delete(sessions: SessionFactory) -> None:
    """登记后按对象列出，删除只影响元数据。"""
    service = build_service(sessions)
    result = service.register(_input())
    assert result.is_ok
    rows = service.list_for("project", 1)
    assert rows[0].file_name == "arch.png"
    assert service.delete(rows[0].id).is_ok
    assert service.list_for("project", 1) == []
