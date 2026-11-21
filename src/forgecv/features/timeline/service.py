"""领域服务：把学历、经历、项目合并成统一时间轴。"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date
from itertools import pairwise
from typing import Protocol

from forgecv.features.education.service import EducationService
from forgecv.features.experience.service import ExperienceService
from forgecv.features.project.service import ProjectService
from forgecv.features.timeline.schemas import TimelineData, TimelineEvent


class EducationLike(Protocol):
    """时间轴只需要学历的展示字段。"""

    school: str
    degree_level: str
    major: str
    start_date: date
    end_date: date | None
    is_current: bool


class ExperienceLike(Protocol):
    """时间轴只需要经历的展示字段。"""

    company: str
    role: str
    start_date: date
    end_date: date | None
    is_current: bool


class ProjectLike(Protocol):
    """时间轴只需要项目的展示字段。"""

    name: str
    direction: str
    start_date: date | None
    end_date: date | None


class TimelineService:
    """只读聚合，不写任何表。"""

    def __init__(
        self,
        educations: EducationService,
        experiences: ExperienceService,
        projects: ProjectService,
    ) -> None:
        """注入三个来源切片。"""
        self._educations = educations
        self._experiences = experiences
        self._projects = projects

    def snapshot(self) -> TimelineData:
        """生成按开始时间升序的事件与重叠提示。"""
        educations = self._educations.list_all()
        experiences = self._experiences.list_all()
        projects = self._projects.list_all()
        events = [
            *self._education_events(educations),
            *self._experience_events(experiences),
            *self._project_events(projects),
        ]
        events.sort(key=lambda event: (event.start is None, event.start or date.min))
        warnings = [
            *self._overlaps(
                [(row.start_date, row.end_date, row.school) for row in educations], "学历"
            ),
            *self._overlaps(
                [(row.start_date, row.end_date, row.company) for row in experiences], "工作"
            ),
        ]
        return TimelineData(events=events, warnings=warnings)

    @staticmethod
    def _education_events(rows: Sequence[EducationLike]) -> list[TimelineEvent]:
        """学历事件。"""
        return [
            TimelineEvent(
                kind="学历",
                title=row.school,
                subtitle=f"{row.degree_level} · {row.major or '未填专业'}",
                start=row.start_date,
                end=row.end_date,
                is_current=row.is_current,
            )
            for row in rows
        ]

    @staticmethod
    def _experience_events(rows: Sequence[ExperienceLike]) -> list[TimelineEvent]:
        """工作事件。"""
        return [
            TimelineEvent(
                kind="工作",
                title=row.company,
                subtitle=row.role,
                start=row.start_date,
                end=row.end_date,
                is_current=row.is_current,
            )
            for row in rows
        ]

    @staticmethod
    def _project_events(rows: Sequence[ProjectLike]) -> list[TimelineEvent]:
        """项目事件。"""
        return [
            TimelineEvent(
                kind="项目",
                title=row.name,
                subtitle=row.direction,
                start=row.start_date,
                end=row.end_date,
                is_current=row.end_date is None,
            )
            for row in rows
        ]

    @staticmethod
    def _overlaps(
        rows: list[tuple[date, date | None, str]], kind: str
    ) -> list[str]:
        """同一分区内时间区间重叠提示。"""
        intervals = sorted(
            (start, end or date.today(), name) for start, end, name in rows
        )
        warnings: list[str] = []
        for previous, current in pairwise(intervals):
            if current[0] < previous[1]:
                warnings.append(
                    f"{kind}时间重叠：{previous[2]} 与 {current[2]}"
                )
        return warnings
