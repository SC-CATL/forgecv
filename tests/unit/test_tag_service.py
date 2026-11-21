"""tag 服务：四维标签与项目打标。"""

from __future__ import annotations

from forgecv.features.project.api import build_service as build_projects
from forgecv.features.project.schemas import ProjectInput
from forgecv.features.tag.api import build_service
from forgecv.features.tag.schemas import TagInput
from forgecv.platform.adapters.db.session import SessionFactory


def _project(sessions: SessionFactory) -> int:
    """建一个用于打标的项目。"""
    project = build_projects(sessions).add(ProjectInput(name="网关", direction="后端")).unwrap()
    return project.id


def test_create_rejects_unknown_dimension(sessions: SessionFactory) -> None:
    """维度必须在四维白名单内。"""
    assert not build_service(sessions).create(TagInput(name="Python", dimension="other")).is_ok


def test_create_rejects_duplicate_name(sessions: SessionFactory) -> None:
    """名称全局唯一。"""
    service = build_service(sessions)
    assert service.create(TagInput(name="Python")).is_ok
    assert not service.create(TagInput(name="Python", dimension="domain")).is_ok


def test_filter_by_dimension(sessions: SessionFactory) -> None:
    """按维度筛选。"""
    service = build_service(sessions)
    service.create(TagInput(name="Python"))
    service.create(TagInput(name="CI/CD", dimension="practice"))
    assert [tag.name for tag in service.list_all("practice")] == ["CI/CD"]


def test_set_project_tags_and_delete_tag(
    sessions: SessionFactory, candidate: int
) -> None:
    """整体重设标签，删除标签后关联一并清除。"""
    project_id = _project(sessions)
    service = build_service(sessions)
    python = service.create(TagInput(name="Python")).unwrap()
    docker = service.create(TagInput(name="Docker", dimension="toolchain")).unwrap()
    service.set_project_tags(project_id, [python.id, docker.id])
    assert {tag.name for tag in service.tags_for_project(project_id)} == {"Python", "Docker"}
    assert service.delete(python.id).is_ok
    assert {tag.name for tag in service.tags_for_project(project_id)} == {"Docker"}
