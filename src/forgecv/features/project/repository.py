"""仓储：项目与指标持久化。"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from forgecv.features.project.models import Project, ProjectMetric
from forgecv.features.project.schemas import MetricInput, ProjectInput
from forgecv.platform.adapters.db.session import SessionFactory, session_scope

CANDIDATE_ID = 1


def project_fields(data: ProjectInput) -> dict[str, Any]:
    """拆出 Project 自身字段，指标单独处理。"""
    values = asdict(data)
    values.pop("metrics", None)
    return values


def replace_metrics(session: Session, project_id: int, metrics: list[MetricInput]) -> None:
    """整体替换项目指标。"""
    session.execute(delete(ProjectMetric).where(ProjectMetric.project_id == project_id))
    for metric in metrics:
        session.add(ProjectMetric(project_id=project_id, **asdict(metric)))


class ProjectRepository:
    """projects 与 project_metrics 表的读写。"""

    def __init__(self, sessions: SessionFactory) -> None:
        """注入会话工厂。"""
        self._sessions = sessions

    def list_all(self) -> list[Project]:
        """全部项目，按排序号与开始时间倒序。"""
        with session_scope(self._sessions) as session:
            statement = select(Project).order_by(
                Project.sort_order, Project.start_date.desc(), Project.id.desc()
            )
            return list(session.scalars(statement).all())

    def get(self, project_id: int) -> Project | None:
        """按 id 读取项目。"""
        with session_scope(self._sessions) as session:
            return session.get(Project, project_id)

    def add(self, data: ProjectInput) -> Project:
        """新增项目并写入指标。"""
        with session_scope(self._sessions) as session:
            row = Project(candidate_id=CANDIDATE_ID, **project_fields(data))
            session.add(row)
            session.flush()
            replace_metrics(session, row.id, data.metrics)
            return row

    def update(self, project_id: int, data: ProjectInput) -> Project | None:
        """覆盖项目并重设指标。"""
        with session_scope(self._sessions) as session:
            row = session.get(Project, project_id)
            if row is None:
                return None
            for field, value in project_fields(data).items():
                setattr(row, field, value)
            session.flush()
            replace_metrics(session, project_id, data.metrics)
            return row

    def delete(self, project_id: int) -> bool:
        """删除项目及其指标。"""
        with session_scope(self._sessions) as session:
            row = session.get(Project, project_id)
            if row is None:
                return False
            session.execute(delete(ProjectMetric).where(ProjectMetric.project_id == project_id))
            session.delete(row)
            return True

    def metrics_for(self, project_id: int) -> list[ProjectMetric]:
        """项目指标，按排序号。"""
        with session_scope(self._sessions) as session:
            statement = (
                select(ProjectMetric)
                .where(ProjectMetric.project_id == project_id)
                .order_by(ProjectMetric.sort_order, ProjectMetric.id)
            )
            return list(session.scalars(statement).all())
