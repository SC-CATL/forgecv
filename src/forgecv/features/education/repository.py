"""仓储：学历节点持久化。"""

from __future__ import annotations

from dataclasses import asdict

from sqlalchemy import select

from forgecv.features.education.models import Education
from forgecv.features.education.schemas import EducationInput
from forgecv.platform.adapters.db.session import SessionFactory, session_scope

CANDIDATE_ID = 1


class EducationRepository:
    """educations 表的读写。"""

    def __init__(self, sessions: SessionFactory) -> None:
        """注入会话工厂。"""
        self._sessions = sessions

    def list_all(self) -> list[Education]:
        """全部学历，按排序号与入学时间。"""
        with session_scope(self._sessions) as session:
            statement = select(Education).order_by(
                Education.sort_order, Education.start_date.desc()
            )
            return list(session.scalars(statement).all())

    def get(self, education_id: int) -> Education | None:
        """按 id 读取。"""
        with session_scope(self._sessions) as session:
            return session.get(Education, education_id)

    def add(self, data: EducationInput) -> Education:
        """新增一条学历。"""
        if data.start_date is None:
            raise ValueError("start_date 必须由服务层校验后传入")
        with session_scope(self._sessions) as session:
            row = Education(candidate_id=CANDIDATE_ID, **asdict(data))
            session.add(row)
            session.flush()
            return row

    def update(self, education_id: int, data: EducationInput) -> Education | None:
        """覆盖一条学历，不存在返回 None。"""
        with session_scope(self._sessions) as session:
            row = session.get(Education, education_id)
            if row is None:
                return None
            for field, value in asdict(data).items():
                setattr(row, field, value)
            session.flush()
            return row

    def delete(self, education_id: int) -> bool:
        """删除一条学历。"""
        with session_scope(self._sessions) as session:
            row = session.get(Education, education_id)
            if row is None:
                return False
            session.delete(row)
            return True

    def reorder(self, ordered_ids: list[int]) -> None:
        """按给定顺序重写 sort_order。"""
        with session_scope(self._sessions) as session:
            for index, education_id in enumerate(ordered_ids):
                row = session.get(Education, education_id)
                if row is not None:
                    row.sort_order = index
