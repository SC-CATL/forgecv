"""输入模型：附件。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class AttachmentInput:
    """附件元数据输入。"""

    owner_type: str
    owner_id: int
    file_name: str
    path: str
    sha256: str
    size_bytes: int
    mime: str = ""
