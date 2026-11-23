"""仓储：候选人与证书的持久化。"""

from __future__ import annotations

from dataclasses import asdict

from sqlalchemy import select

from forgecv.features.profile.models import Candidate, Certificate
from forgecv.features.profile.schemas import CandidateInput, CertificateInput
from forgecv.platform.adapters.db.session import SessionFactory, session_scope

CANDIDATE_ID = 1


class ProfileRepository:
    """candidate 与 certificates 表的读写。"""

    def __init__(self, sessions: SessionFactory) -> None:
        """注入会话工厂。"""
        self._sessions = sessions

    def get_candidate(self) -> Candidate | None:
        """读取候选人，未建档返回 None。"""
        with session_scope(self._sessions) as session:
            return session.get(Candidate, CANDIDATE_ID)

    def ensure_candidate(self) -> Candidate:
        """确保单候选人占位行存在，供其他切片写入外键。"""
        with session_scope(self._sessions) as session:
            row = session.get(Candidate, CANDIDATE_ID)
            if row is None:
                row = Candidate(id=CANDIDATE_ID, full_name="")
                session.add(row)
                session.flush()
            return row

    def save_candidate(self, data: CandidateInput) -> Candidate:
        """按固定 id 新建或覆盖候选人。"""
        with session_scope(self._sessions) as session:
            row = session.get(Candidate, CANDIDATE_ID)
            if row is None:
                row = Candidate(id=CANDIDATE_ID, full_name=data.full_name)
                session.add(row)
            for field, value in asdict(data).items():
                setattr(row, field, value)
            session.flush()
            return row

    def list_certificates(self) -> list[Certificate]:
        """全部证书，按排序号与颁发日期倒序。"""
        with session_scope(self._sessions) as session:
            statement = select(Certificate).order_by(
                Certificate.sort_order, Certificate.issued_on.desc()
            )
            return list(session.scalars(statement).all())

    def add_certificate(self, data: CertificateInput) -> Certificate:
        """新增证书。"""
        with session_scope(self._sessions) as session:
            row = Certificate(candidate_id=CANDIDATE_ID, **asdict(data))
            session.add(row)
            session.flush()
            return row

    def delete_certificate(self, certificate_id: int) -> bool:
        """删除证书，返回是否存在。"""
        with session_scope(self._sessions) as session:
            row = session.get(Certificate, certificate_id)
            if row is None:
                return False
            session.delete(row)
            return True
