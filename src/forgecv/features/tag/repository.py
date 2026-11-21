"""仓储：标签与项目关联。"""

from __future__ import annotations

from dataclasses import asdict

from sqlalchemy import delete, select

from forgecv.features.tag.models import ProjectTag, Tag
from forgecv.features.tag.schemas import TagInput
from forgecv.platform.adapters.db.session import SessionFactory, session_scope


class TagRepository:
    """tags 与 project_tags 表的读写。"""

    def __init__(self, sessions: SessionFactory) -> None:
        """注入会话工厂。"""
        self._sessions = sessions

    def list_all(self, dimension: str | None = None) -> list[Tag]:
        """按维度筛选标签。"""
        with session_scope(self._sessions) as session:
            statement = select(Tag).order_by(Tag.dimension, Tag.sort_order, Tag.name)
            if dimension is not None:
                statement = statement.where(Tag.dimension == dimension)
            return list(session.scalars(statement).all())

    def find_by_name(self, name: str) -> Tag | None:
        """按名称精确查找。"""
        with session_scope(self._sessions) as session:
            return session.scalar(select(Tag).where(Tag.name == name))

    def add(self, data: TagInput) -> Tag:
        """新增标签。"""
        with session_scope(self._sessions) as session:
            row = Tag(**asdict(data))
            session.add(row)
            session.flush()
            return row

    def update(self, tag_id: int, data: TagInput) -> Tag | None:
        """覆盖标签。"""
        with session_scope(self._sessions) as session:
            row = session.get(Tag, tag_id)
            if row is None:
                return None
            for field, value in asdict(data).items():
                setattr(row, field, value)
            session.flush()
            return row

    def delete(self, tag_id: int) -> bool:
        """删除标签及其项目关联。"""
        with session_scope(self._sessions) as session:
            row = session.get(Tag, tag_id)
            if row is None:
                return False
            session.execute(delete(ProjectTag).where(ProjectTag.tag_id == tag_id))
            session.delete(row)
            return True

    def tags_for_project(self, project_id: int) -> list[Tag]:
        """项目已打的标签。"""
        with session_scope(self._sessions) as session:
            statement = (
                select(Tag)
                .join(ProjectTag, ProjectTag.tag_id == Tag.id)
                .where(ProjectTag.project_id == project_id)
                .order_by(Tag.dimension, Tag.name)
            )
            return list(session.scalars(statement).all())

    def attach(self, project_id: int, tag_id: int) -> bool:
        """建立项目-标签关联，已存在返回 False。"""
        with session_scope(self._sessions) as session:
            if session.get(ProjectTag, (project_id, tag_id)) is not None:
                return False
            session.add(ProjectTag(project_id=project_id, tag_id=tag_id))
            return True

    def detach(self, project_id: int, tag_id: int) -> bool:
        """解除关联，不存在返回 False。"""
        with session_scope(self._sessions) as session:
            row = session.get(ProjectTag, (project_id, tag_id))
            if row is None:
                return False
            session.delete(row)
            return True

    def replace_project_tags(self, project_id: int, tag_ids: list[int]) -> None:
        """整体重设项目标签。"""
        with session_scope(self._sessions) as session:
            session.execute(delete(ProjectTag).where(ProjectTag.project_id == project_id))
            for tag_id in dict.fromkeys(tag_ids):
                session.add(ProjectTag(project_id=project_id, tag_id=tag_id))
