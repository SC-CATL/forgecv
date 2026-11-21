"""仓储：附件元数据持久化。"""

from __future__ import annotations

from dataclasses import asdict

from sqlalchemy import select

from forgecv.features.attachment.models import Attachment
from forgecv.features.attachment.schemas import AttachmentInput
from forgecv.platform.adapters.db.session import SessionFactory, session_scope


class AttachmentRepository:
    """attachments 表的读写。"""

    def __init__(self, sessions: SessionFactory) -> None:
        """注入会话工厂。"""
        self._sessions = sessions

    def list_for(self, owner_type: str, owner_id: int) -> list[Attachment]:
        """某个实体挂载的附件。"""
        with session_scope(self._sessions) as session:
            statement = (
                select(Attachment)
                .where(Attachment.owner_type == owner_type, Attachment.owner_id == owner_id)
                .order_by(Attachment.id)
            )
            return list(session.scalars(statement).all())

    def add(self, data: AttachmentInput) -> Attachment:
        """登记一个已落盘的文件。"""
        with session_scope(self._sessions) as session:
            row = Attachment(**asdict(data))
            session.add(row)
            session.flush()
            return row

    def delete(self, attachment_id: int) -> bool:
        """删除元数据，不删除磁盘文件。"""
        with session_scope(self._sessions) as session:
            row = session.get(Attachment, attachment_id)
            if row is None:
                return False
            session.delete(row)
            return True
