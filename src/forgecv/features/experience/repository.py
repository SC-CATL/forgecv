"""仓储：工作经历持久化。"""

from __future__ import annotations

from dataclasses import asdict

from sqlalchemy import select

from forgecv.features.experience.models import Experience
from forgecv.features.experience.schemas import ExperienceInput
from forgecv.platform.adapters.db.session import SessionFactory, session_scope

CANDIDATE_ID = 1


class ExperienceRepository:
    """experiences 表的读写。"""

    def __init__(self, sessions: SessionFactory) -> None:
        """注入会话工厂。"""
        self._sessions = sessions

    def list_all(self) -> list[Experience]:
        """全部经历，按排序号与开始时间倒序。"""
        with session_scope(self._sessions) as session:
            statement = select(Experience).order_by(
                Experience.sort_order, Experience.start_date.desc()
            )
            return list(session.scalars(statement).all())

    def get(self, experience_id: int) -> Experience | None:
        """按 id 读取。"""
        with session_scope(self._sessions) as session:
            return session.get(Experience, experience_id)

    def add(self, data: ExperienceInput) -> Experience:
        """新增一段经历。"""
        if data.start_date is None:
            raise ValueError("start_date 必须由服务层校验后传入")
        with session_scope(self._sessions) as session:
            row = Experience(candidate_id=CANDIDATE_ID, **asdict(data))
            session.add(row)
            session.flush()
            return row

    def update(self, experience_id: int, data: ExperienceInput) -> Experience | None:
        """覆盖一段经历。"""
        with session_scope(self._sessions) as session:
            row = session.get(Experience, experience_id)
            if row is None:
                return None
            for field, value in asdict(data).items():
                setattr(row, field, value)
            session.flush()
            return row

    def delete(self, experience_id: int) -> bool:
        """删除一段经历。"""
        with session_scope(self._sessions) as session:
            row = session.get(Experience, experience_id)
            if row is None:
                return False
            session.delete(row)
            return True
