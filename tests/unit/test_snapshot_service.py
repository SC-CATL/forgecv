"""快照：保存、列表与文本 Diff。"""

from __future__ import annotations

from forgecv.features.education.api import build_service as build_education
from forgecv.features.experience.api import build_service as build_experience
from forgecv.features.profile.api import build_service as build_profile
from forgecv.features.profile.schemas import CandidateInput
from forgecv.features.project.api import build_service as build_project
from forgecv.features.project.schemas import ProjectInput
from forgecv.features.resume.api import build_service as build_resume
from forgecv.features.resume.render import ResumeRenderer
from forgecv.features.resume.schemas import VersionInput
from forgecv.features.skill.api import build_service as build_skill
from forgecv.features.snapshot.api import build_service
from forgecv.features.tag.api import build_service as build_tag
from forgecv.platform.adapters.db.session import SessionFactory


def _version(sessions: SessionFactory) -> int:
    """建一个含项目的版本。"""
    build_profile(sessions).save(CandidateInput(full_name="张三"))
    build_project(sessions).add(ProjectInput(name="网关", direction="后端"))
    version = build_resume(sessions).create_version(VersionInput(name="后端版")).unwrap()
    return version.id


def _renderer(sessions: SessionFactory) -> ResumeRenderer:
    """装配渲染器。"""
    return ResumeRenderer(
        resume=build_resume(sessions),
        profile=build_profile(sessions),
        educations=build_education(sessions),
        experiences=build_experience(sessions),
        projects=build_project(sessions),
        skills=build_skill(sessions),
        tags=build_tag(sessions),
    )


def test_create_snapshot_and_diff(sessions: SessionFactory) -> None:
    """两次快照之间有内容变化时，Diff 包含增删行。"""
    version_id = _version(sessions)
    resume = build_resume(sessions)
    service = build_service(sessions)
    version = resume.versions()[0]
    assert service.create(version, "初版").is_ok
    build_project(sessions).add(ProjectInput(name="工具", direction="工具链"))
    assert service.create(version, "加项目").is_ok
    snapshots = service.snapshots(version_id)
    assert len(snapshots) == 2
    diff = service.diff_text(snapshots[1], snapshots[0])
    assert "+" in diff
    assert "-" in diff


def test_identical_snapshots_message(sessions: SessionFactory) -> None:
    """内容未变时给出明确提示。"""
    _version(sessions)
    service = build_service(sessions)
    version = build_resume(sessions).versions()[0]
    first = service.create(version, "A").unwrap()
    second = service.create(version, "B").unwrap()
    assert service.diff_text(first, second) == "两版内容一致。"


def test_snapshot_requires_name(sessions: SessionFactory) -> None:
    """没有候选人时拒绝创建。"""
    version = build_resume(sessions).create_version(VersionInput(name="空版本")).unwrap()
    assert not build_service(sessions).create(version, "空").is_ok


def test_renderer_is_available(sessions: SessionFactory) -> None:
    """防止装配函数被误删。"""
    assert _renderer(sessions) is not None
