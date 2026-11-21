"""项目页：档案、指标与标签联动。"""

from __future__ import annotations

import pytest

from forgecv.features.project.api import build_service as build_projects
from forgecv.features.project.schemas import MetricInput, ProjectInput
from forgecv.features.project.view import ProjectPage
from forgecv.features.project.viewmodel import ProjectViewModel
from forgecv.features.tag.api import build_service as build_tags
from forgecv.features.tag.schemas import TagInput
from forgecv.platform.adapters.db.session import SessionFactory
from forgecv.platform.ui.qt import QtCore, QtWidgets

pytestmark = pytest.mark.ui


def _page(sessions: SessionFactory) -> ProjectPage:
    return ProjectPage(ProjectViewModel(build_projects(sessions), build_tags(sessions)))


def _check(page: ProjectPage, tag_id: int) -> None:
    """按标签 id 勾选。"""
    for index in range(page._tag_list.count()):
        item = page._tag_list.item(index)
        if item.data(QtCore.Qt.ItemDataRole.UserRole) == tag_id:
            item.setCheckState(QtCore.Qt.CheckState.Checked)


def test_create_project_with_metrics_and_tags(
    qtbot, sessions: SessionFactory, candidate: int
) -> None:
    """新增项目时一并写入指标并打标签。"""
    tag = build_tags(sessions).create(TagInput(name="Python")).unwrap()
    page = _page(sessions)
    qtbot.addWidget(page)
    page._name.setText("网关")
    page._direction.setCurrentText("后端")
    page._metrics.insertRow(0)
    page._metrics.setItem(0, 0, QtWidgets.QTableWidgetItem("QPS"))
    page._metrics.setItem(0, 1, QtWidgets.QTableWidgetItem("1200"))
    page._metrics.setItem(0, 2, QtWidgets.QTableWidgetItem("req/s"))
    _check(page, tag.id)
    page._save()
    project = build_projects(sessions).list_all()[0]
    assert project.name == "网关"
    assert build_projects(sessions).metrics_for(project.id)[0].key == "QPS"
    assert [row.name for row in build_tags(sessions).tags_for_project(project.id)] == ["Python"]


def test_select_project_loads_metrics(
    qtbot, sessions: SessionFactory, candidate: int
) -> None:
    """选中项目后回填档案，指标表格可刷新。"""
    project = build_projects(sessions).add(
        ProjectInput(
            name="网关",
            direction="后端",
            metrics=[MetricInput(key="P99", value="45", unit="ms")],
        )
    ).unwrap()
    page = _page(sessions)
    qtbot.addWidget(page)
    page._list.setCurrentRow(0)
    assert page._current_id == project.id
    assert page._name.text() == "网关"
    assert page._metrics.rowCount() == 1
