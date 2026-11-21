"""resume 服务：版本、条目与快照。"""

from __future__ import annotations

from forgecv.features.project.api import build_service as build_projects
from forgecv.features.project.schemas import ProjectInput
from forgecv.features.resume.api import build_service
from forgecv.features.resume.schemas import ItemInput, VersionInput
from forgecv.platform.adapters.db.session import SessionFactory


def test_version_validation_and_default(sessions: SessionFactory, candidate: int) -> None:
    """名称必填，默认版本唯一。"""
    service = build_service(sessions)
    assert not service.create_version(VersionInput(name=" ")).is_ok
    first = service.create_version(VersionInput(name="后端版", is_default=True)).unwrap()
    service.create_version(VersionInput(name="嵌入式版", is_default=True))
    versions = service.versions()
    assert len(versions) == 2
    assert [row.is_default for row in versions].count(True) == 1
    assert first.id != versions[0].id


def test_add_item_rejects_duplicates(sessions: SessionFactory, candidate: int) -> None:
    """同一版本内不允许重复引用同一条目。"""
    service = build_service(sessions)
    version = service.create_version(VersionInput(name="后端版")).unwrap()
    item = ItemInput(item_type="project", item_id=1)
    assert service.add_item(version.id, item).is_ok
    assert not service.add_item(version.id, item).is_ok


def test_add_item_rejects_unknown_type(sessions: SessionFactory, candidate: int) -> None:
    """条目类型白名单。"""
    service = build_service(sessions)
    version = service.create_version(VersionInput(name="后端版")).unwrap()
    assert not service.add_item(version.id, ItemInput(item_type="blog", item_id=1)).is_ok


def test_snapshot_roundtrip(sessions: SessionFactory, candidate: int) -> None:
    """快照可写可读。"""
    service = build_service(sessions)
    version = service.create_version(VersionInput(name="后端版")).unwrap()
    result = service.create_snapshot(version.id, "投递前", {"name": "张三"})
    assert result.is_ok
    assert service.snapshots(version.id)[0].payload == {"name": "张三"}


def test_project_item_reference(sessions: SessionFactory, candidate: int) -> None:
    """条目可引用真实项目 id。"""
    project = build_projects(sessions).add(
        ProjectInput(name="网关", direction="后端")
    ).unwrap()
    service = build_service(sessions)
    version = service.create_version(VersionInput(name="后端版")).unwrap()
    assert service.add_item(
        version.id, ItemInput(item_type="project", item_id=project.id)
    ).is_ok
