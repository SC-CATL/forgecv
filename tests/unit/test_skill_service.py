"""skill 服务：技能矩阵与证据链。"""

from __future__ import annotations

from forgecv.features.project.api import build_service as build_projects
from forgecv.features.project.schemas import ProjectInput
from forgecv.features.skill.api import build_service
from forgecv.features.skill.schemas import EvidenceInput, SkillInput
from forgecv.platform.adapters.db.session import SessionFactory


def test_level_and_score_ranges(sessions: SessionFactory, candidate: int) -> None:
    """熟练度 1-4，自评分 0-100。"""
    service = build_service(sessions)
    assert not service.add(SkillInput(name="Python", level=0)).is_ok
    assert not service.add(SkillInput(name="Python", level=5)).is_ok
    assert not service.add(SkillInput(name="Python", self_score=101)).is_ok


def test_duplicate_in_same_category_rejected(
    sessions: SessionFactory, candidate: int
) -> None:
    """同分类下名称唯一。"""
    service = build_service(sessions)
    assert service.add(SkillInput(name="Python", category="语言")).is_ok
    assert not service.add(SkillInput(name="Python", category="语言")).is_ok
    assert service.add(SkillInput(name="Python", category="工具链")).is_ok


def test_evidence_requires_a_source(sessions: SessionFactory, candidate: int) -> None:
    """证据必须挂项目或经历。"""
    service = build_service(sessions)
    skill = service.add(SkillInput(name="Python")).unwrap()
    result = service.add_evidence(EvidenceInput(skill_id=skill.id, statement="写了三年"))
    assert not result.is_ok


def test_evidence_roundtrip(sessions: SessionFactory, candidate: int) -> None:
    """证据写入后可按技能读出。"""
    skill = build_service(sessions).add(SkillInput(name="Python")).unwrap()
    project = build_projects(sessions).add(
        ProjectInput(name="网关", direction="后端")
    ).unwrap()
    service = build_service(sessions)
    result = service.add_evidence(
        EvidenceInput(
            skill_id=skill.id,
            project_id=project.id,
            statement="负责网关核心模块",
        )
    )
    assert result.is_ok
    assert service.evidence_for(skill.id)[0].project_id == project.id
