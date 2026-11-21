"""project 服务：项目、指标与标签无关的校验。"""

from __future__ import annotations

from forgecv.features.project.api import build_service
from forgecv.features.project.schemas import MetricInput, ProjectInput
from forgecv.platform.adapters.db.session import SessionFactory


def test_add_requires_name_and_direction(sessions: SessionFactory, candidate: int) -> None:
    """名称与方向必填。"""
    service = build_service(sessions)
    assert not service.add(ProjectInput(name="", direction="后端")).is_ok
    assert not service.add(ProjectInput(name="项目", direction=" ")).is_ok


def test_add_rejects_unknown_status(sessions: SessionFactory, candidate: int) -> None:
    """状态只接受白名单。"""
    result = build_service(sessions).add(
        ProjectInput(name="项目", direction="后端", status="unknown")
    )
    assert not result.is_ok


def test_add_stores_metrics(sessions: SessionFactory, candidate: int) -> None:
    """指标随项目写入并能读回。"""
    service = build_service(sessions)
    result = service.add(
        ProjectInput(
            name="网关",
            direction="后端",
            highlights=[" 压测提升 3 倍 ", ""],
            metrics=[MetricInput(key=" QPS ", value=" 1200 ", unit="req/s")],
        )
    )
    assert result.is_ok
    project = result.unwrap()
    assert project.highlights == ["压测提升 3 倍"]
    metrics = service.metrics_for(project.id)
    assert metrics[0].key == "QPS"
    assert metrics[0].unit == "req/s"


def test_metric_requires_key_and_value(sessions: SessionFactory, candidate: int) -> None:
    """不完整的指标直接报错。"""
    result = build_service(sessions).add(
        ProjectInput(
            name="网关",
            direction="后端",
            metrics=[MetricInput(key="QPS", value=" ")],
        )
    )
    assert not result.is_ok


def test_delete_removes_project(sessions: SessionFactory, candidate: int) -> None:
    """删除项目后列表为空。"""
    service = build_service(sessions)
    project = service.add(ProjectInput(name="网关", direction="后端")).unwrap()
    assert service.delete(project.id).is_ok
    assert service.list_all() == []
