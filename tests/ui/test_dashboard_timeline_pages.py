"""时间轴页与概览页的装配。"""

from __future__ import annotations

from datetime import date

import pytest

from forgecv.features.dashboard.api import build_service as build_dashboard
from forgecv.features.dashboard.view import DashboardPage
from forgecv.features.dashboard.viewmodel import DashboardViewModel
from forgecv.features.education.api import build_service as build_education
from forgecv.features.education.schemas import EducationInput
from forgecv.features.project.api import build_service as build_project
from forgecv.features.project.schemas import ProjectInput
from forgecv.features.timeline.api import build_service as build_timeline
from forgecv.features.timeline.view import TimelinePage
from forgecv.features.timeline.viewmodel import TimelineViewModel
from forgecv.platform.adapters.db.session import SessionFactory
from forgecv.platform.ui.kit.theme import ThemeService

pytestmark = pytest.mark.ui


def test_timeline_page_lists_events(qtbot, sessions: SessionFactory, candidate: int) -> None:
    """时间轴页把三类事件都列出来。"""
    build_education(sessions).add(
        EducationInput(
            school="浙大", start_date=date(2020, 9, 1), end_date=date(2024, 6, 1)
        )
    )
    build_project(sessions).add(ProjectInput(name="网关", direction="后端"))
    page = TimelinePage(TimelineViewModel(build_timeline(sessions)))
    qtbot.addWidget(page)
    assert page._list.count() == 2
    assert "学历" in page._list.item(0).text()


def test_dashboard_page_shows_counts(qtbot, sessions: SessionFactory, candidate: int) -> None:
    """概览页统计卡片与雷达数据被填充。"""
    build_project(sessions).add(ProjectInput(name="网关", direction="后端"))
    page = DashboardPage(
        DashboardViewModel(build_dashboard(sessions), ThemeService())
    )
    qtbot.addWidget(page)
    assert page._stat_values["项目"].text() == "1"
    assert page._latest_radar is not None
    assert page._tag_text.text() == "暂无标签"
