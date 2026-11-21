"""时间轴聚合与重叠检测。"""

from __future__ import annotations

from datetime import date

from forgecv.features.education.api import build_service as build_education
from forgecv.features.education.schemas import EducationInput
from forgecv.features.experience.api import build_service as build_experience
from forgecv.features.experience.schemas import ExperienceInput
from forgecv.features.project.api import build_service as build_project
from forgecv.features.project.schemas import ProjectInput
from forgecv.features.timeline.api import build_service
from forgecv.platform.adapters.db.session import SessionFactory


def test_events_are_sorted(sessions: SessionFactory, candidate: int) -> None:
    """学历、工作、项目按开始时间升序。"""
    build_project(sessions).add(
        ProjectInput(name="网关", direction="后端", start_date=date(2023, 3, 1))
    )
    build_education(sessions).add(
        EducationInput(
            school="浙大",
            start_date=date(2020, 9, 1),
            end_date=date(2024, 6, 1),
        )
    )
    build_experience(sessions).add(
        ExperienceInput(
            company="某公司",
            role="后端",
            start_date=date(2022, 7, 1),
            is_current=True,
        )
    )
    events = build_service(sessions).snapshot().events
    assert [event.kind for event in events] == ["学历", "工作", "项目"]


def test_overlapping_experiences_warn(sessions: SessionFactory, candidate: int) -> None:
    """同分区重叠会给出提示。"""
    experience = build_experience(sessions)
    for company in ("A", "B"):
        experience.add(
            ExperienceInput(
                company=company,
                role="后端",
                start_date=date(2023, 1, 1),
                end_date=date(2023, 12, 1),
            )
        )
    data = build_service(sessions).snapshot()
    assert len(data.warnings) == 1
    assert "重叠" in data.warnings[0]


def test_empty_timeline(sessions: SessionFactory) -> None:
    """空库返回空事件。"""
    data = build_service(sessions).snapshot()
    assert data.events == []
    assert data.warnings == []
