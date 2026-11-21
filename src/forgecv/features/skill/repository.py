"""仓储：技能与证据持久化。"""

from __future__ import annotations

from dataclasses import asdict

from sqlalchemy import select

from forgecv.features.skill.models import Skill, SkillEvidence
from forgecv.features.skill.schemas import EvidenceInput, SkillInput
from forgecv.platform.adapters.db.session import SessionFactory, session_scope

CANDIDATE_ID = 1


class SkillRepository:
    """skills 与 skill_evidence 表的读写。"""

    def __init__(self, sessions: SessionFactory) -> None:
        """注入会话工厂。"""
        self._sessions = sessions

    def list_all(self, category: str | None = None) -> list[Skill]:
        """按分类筛选技能。"""
        with session_scope(self._sessions) as session:
            statement = select(Skill).order_by(Skill.category, Skill.sort_order, Skill.name)
            if category is not None:
                statement = statement.where(Skill.category == category)
            return list(session.scalars(statement).all())

    def get(self, skill_id: int) -> Skill | None:
        """按 id 读取技能。"""
        with session_scope(self._sessions) as session:
            return session.get(Skill, skill_id)

    def find(self, category: str, name: str) -> Skill | None:
        """按分类 + 名称查找，用于重复校验。"""
        with session_scope(self._sessions) as session:
            statement = select(Skill).where(
                Skill.candidate_id == CANDIDATE_ID,
                Skill.category == category,
                Skill.name == name,
            )
            return session.scalar(statement)

    def add(self, data: SkillInput) -> Skill:
        """新增技能。"""
        with session_scope(self._sessions) as session:
            row = Skill(candidate_id=CANDIDATE_ID, **asdict(data))
            session.add(row)
            session.flush()
            return row

    def update(self, skill_id: int, data: SkillInput) -> Skill | None:
        """覆盖技能。"""
        with session_scope(self._sessions) as session:
            row = session.get(Skill, skill_id)
            if row is None:
                return None
            for field, value in asdict(data).items():
                setattr(row, field, value)
            session.flush()
            return row

    def delete(self, skill_id: int) -> bool:
        """删除技能及证据。"""
        with session_scope(self._sessions) as session:
            row = session.get(Skill, skill_id)
            if row is None:
                return False
            session.delete(row)
            return True

    def add_evidence(self, data: EvidenceInput) -> SkillEvidence:
        """新增一条证据。"""
        with session_scope(self._sessions) as session:
            row = SkillEvidence(**asdict(data))
            session.add(row)
            session.flush()
            return row

    def evidence_for(self, skill_id: int) -> list[SkillEvidence]:
        """技能的全部证据。"""
        with session_scope(self._sessions) as session:
            statement = (
                select(SkillEvidence)
                .where(SkillEvidence.skill_id == skill_id)
                .order_by(SkillEvidence.sort_order, SkillEvidence.id)
            )
            return list(session.scalars(statement).all())

    def delete_evidence(self, evidence_id: int) -> bool:
        """删除一条证据。"""
        with session_scope(self._sessions) as session:
            row = session.get(SkillEvidence, evidence_id)
            if row is None:
                return False
            session.delete(row)
            return True
