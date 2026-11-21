"""仓储：简历版本、条目与快照持久化。"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from sqlalchemy import select, update

from forgecv.features.resume.models import ResumeItem, ResumeVersion, Snapshot
from forgecv.features.resume.schemas import ItemInput, VersionInput
from forgecv.platform.adapters.db.session import SessionFactory, session_scope

CANDIDATE_ID = 1


class ResumeRepository:
    """resume_versions / resume_items / snapshots 表的读写。"""

    def __init__(self, sessions: SessionFactory) -> None:
        """注入会话工厂。"""
        self._sessions = sessions

    def versions(self) -> list[ResumeVersion]:
        """全部版本，默认版本优先。"""
        with session_scope(self._sessions) as session:
            statement = select(ResumeVersion).order_by(
                ResumeVersion.is_default.desc(), ResumeVersion.id
            )
            return list(session.scalars(statement).all())

    def get_version(self, version_id: int) -> ResumeVersion | None:
        """按 id 读取版本。"""
        with session_scope(self._sessions) as session:
            return session.get(ResumeVersion, version_id)

    def add_version(self, data: VersionInput) -> ResumeVersion:
        """新增版本，默认版本唯一。"""
        with session_scope(self._sessions) as session:
            if data.is_default:
                session.execute(update(ResumeVersion).values(is_default=False))
            row = ResumeVersion(candidate_id=CANDIDATE_ID, **asdict(data))
            session.add(row)
            session.flush()
            return row

    def update_version(self, version_id: int, data: VersionInput) -> ResumeVersion | None:
        """覆盖版本信息。"""
        with session_scope(self._sessions) as session:
            row = session.get(ResumeVersion, version_id)
            if row is None:
                return None
            if data.is_default:
                session.execute(update(ResumeVersion).values(is_default=False))
            for field, value in asdict(data).items():
                setattr(row, field, value)
            session.flush()
            return row

    def delete_version(self, version_id: int) -> bool:
        """删除版本及其条目与快照。"""
        with session_scope(self._sessions) as session:
            row = session.get(ResumeVersion, version_id)
            if row is None:
                return False
            session.delete(row)
            return True

    def items(self, version_id: int) -> list[ResumeItem]:
        """版本内条目，按分区与排序号。"""
        with session_scope(self._sessions) as session:
            statement = (
                select(ResumeItem)
                .where(ResumeItem.version_id == version_id)
                .order_by(ResumeItem.section, ResumeItem.sort_order, ResumeItem.id)
            )
            return list(session.scalars(statement).all())

    def add_item(self, version_id: int, data: ItemInput) -> ResumeItem:
        """向版本追加一条引用。"""
        with session_scope(self._sessions) as session:
            row = ResumeItem(version_id=version_id, **asdict(data))
            session.add(row)
            session.flush()
            return row

    def remove_item(self, item_id: int) -> bool:
        """移除一条引用。"""
        with session_scope(self._sessions) as session:
            row = session.get(ResumeItem, item_id)
            if row is None:
                return False
            session.delete(row)
            return True

    def reorder_items(self, version_id: int, ordered_ids: list[int]) -> None:
        """按给定 id 顺序重写 sort_order。"""
        with session_scope(self._sessions) as session:
            for index, item_id in enumerate(ordered_ids):
                row = session.get(ResumeItem, item_id)
                if row is not None and row.version_id == version_id:
                    row.sort_order = index

    def add_snapshot(
        self, version_id: int, label: str, payload: dict[str, Any]
    ) -> Snapshot:
        """保存一份渲染数据快照。"""
        with session_scope(self._sessions) as session:
            row = Snapshot(version_id=version_id, label=label, payload=payload)
            session.add(row)
            session.flush()
            return row

    def snapshots(self, version_id: int) -> list[Snapshot]:
        """版本快照，最新在前。"""
        with session_scope(self._sessions) as session:
            statement = (
                select(Snapshot)
                .where(Snapshot.version_id == version_id)
                .order_by(Snapshot.created_at.desc(), Snapshot.id.desc())
            )
            return list(session.scalars(statement).all())
