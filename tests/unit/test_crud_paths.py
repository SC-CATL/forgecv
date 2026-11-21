"""补充 CRUD 分支：更新、删除、重排与错误路径。"""

from __future__ import annotations

from datetime import date

from forgecv.features.attachment.api import build_service as build_attachment
from forgecv.features.attachment.schemas import AttachmentInput
from forgecv.features.education.api import build_service as build_education
from forgecv.features.education.schemas import EducationInput
from forgecv.features.experience.api import build_service as build_experience
from forgecv.features.experience.schemas import ExperienceInput
from forgecv.features.profile.api import build_service as build_profile
from forgecv.features.profile.schemas import CandidateInput
from forgecv.features.project.api import build_service as build_project
from forgecv.features.project.schemas import MetricInput, ProjectInput
from forgecv.features.resume.api import build_service as build_resume
from forgecv.features.resume.schemas import ItemInput, VersionInput
from forgecv.features.skill.api import build_service as build_skill
from forgecv.features.skill.schemas import EvidenceInput, SkillInput
from forgecv.features.tag.api import build_service as build_tag
from forgecv.features.tag.schemas import TagInput
from forgecv.platform.adapters.db.session import SessionFactory


def test_profile_rejects_bad_url_and_missing_certificate(sessions: SessionFactory) -> None:
    """链接校验与非空失败分支。"""
    service = build_profile(sessions)
    assert not service.save(CandidateInput(full_name="张三", github_url="github.com")).is_ok
    assert not service.delete_certificate(999).is_ok


def test_education_update_missing_and_reorder_skips_unknown(
    sessions: SessionFactory, candidate: int
) -> None:
    """更新不存在报错，排序忽略未知 id。"""
    service = build_education(sessions)
    row = service.add(
        EducationInput(school="浙大", start_date=date(2020, 9, 1), end_date=date(2024, 6, 1))
    ).unwrap()
    assert not service.update(999, EducationInput(school="浙大", start_date=date(2020, 9, 1))).is_ok
    service.reorder([row.id, 999])
    assert service.list_all()[0].sort_order == 0


def test_experience_update_list_delete(sessions: SessionFactory, candidate: int) -> None:
    """经历更新、列表与删除。"""
    service = build_experience(sessions)
    row = service.add(
        ExperienceInput(
            company="A 公司", role="开发", start_date=date(2023, 1, 1), is_current=True
        )
    ).unwrap()
    updated = service.update(
        row.id,
        ExperienceInput(company="B 公司", role="SRE", start_date=date(2023, 1, 1), is_current=True),
    )
    assert updated.is_ok
    assert service.list_all()[0].company == "B 公司"
    assert service.delete(row.id).is_ok
    assert not service.delete(row.id).is_ok
    assert not service.update(row.id, ExperienceInput(company="C", role="D")).is_ok


def test_project_update_replaces_metrics(sessions: SessionFactory, candidate: int) -> None:
    """更新项目时指标整体替换，且清理不存在的项目。"""
    service = build_project(sessions)
    project = service.add(
        ProjectInput(
            name="网关",
            direction="后端",
            metrics=[MetricInput(key="QPS", value="1000")],
        )
    ).unwrap()
    updated = service.update(
        project.id,
        ProjectInput(
            name="网关 v2",
            direction="后端",
            status="online",
            metrics=[MetricInput(key="P99", value="45", unit="ms")],
        ),
    )
    assert updated.is_ok
    metrics = service.metrics_for(project.id)
    assert [metric.key for metric in metrics] == ["P99"]
    assert service.delete(project.id).is_ok
    assert not service.delete(project.id).is_ok
    assert service.list_all() == []


def test_tag_update_delete_and_dimensions(sessions: SessionFactory) -> None:
    """标签更新、维度映射与删除失败分支。"""
    service = build_tag(sessions)
    tag = service.create(TagInput(name="Python")).unwrap()
    updated = service.update(
        tag.id, TagInput(name="Python3", dimension="language", color="#123456")
    )
    assert updated.is_ok
    assert updated.unwrap().name == "Python3"
    assert set(service.dimensions()) == {"language", "domain", "practice", "toolchain"}
    assert service.delete(tag.id).is_ok
    assert not service.delete(tag.id).is_ok
    assert not service.create(TagInput(name="X", color="red")).is_ok


def test_skill_update_delete_and_evidence_removal(
    sessions: SessionFactory, candidate: int
) -> None:
    """技能更新、证据删除与非法输入。"""
    service = build_skill(sessions)
    assert not service.add(SkillInput(name="X", category="未知")).is_ok
    skill = service.add(SkillInput(name="Python")).unwrap()
    updated = service.update(skill.id, SkillInput(name="Python", level=4, self_score=90))
    assert updated.is_ok and updated.unwrap().level == 4
    evidence = service.add_evidence(
        EvidenceInput(skill_id=skill.id, experience_id=1, statement="线上优化")
    ).unwrap()
    assert service.delete_evidence(evidence.id).is_ok
    assert not service.delete_evidence(evidence.id).is_ok
    assert service.delete(skill.id).is_ok
    assert not service.add_evidence(
        EvidenceInput(skill_id=skill.id, project_id=1, statement="已删除的技能")
    ).is_ok


def test_resume_update_remove_reorder_and_snapshot(
    sessions: SessionFactory, candidate: int
) -> None:
    """版本更新、条目移除重排与快照列表。"""
    service = build_resume(sessions)
    first = service.create_version(VersionInput(name="后端版")).unwrap()
    second = service.create_version(VersionInput(name="嵌入式版")).unwrap()
    assert service.update_version(second.id, VersionInput(name="嵌入式版", is_default=True)).is_ok
    assert service.versions()[0].id == second.id
    item = service.add_item(first.id, ItemInput(item_type="project", item_id=1)).unwrap()
    service.reorder_items(first.id, [item.id])
    assert service.remove_item(item.id).is_ok
    assert not service.remove_item(item.id).is_ok
    assert service.create_snapshot(first.id, "投递前", {"x": 1}).is_ok
    assert not service.create_snapshot(999, "无版本", {}).is_ok
    assert service.delete_version(first.id).is_ok
    assert not service.delete_version(first.id).is_ok


def test_attachment_rejects_empty_and_missing(
    sessions: SessionFactory,
) -> None:
    """附件空字段、负大小与删除失败。"""
    service = build_attachment(sessions)
    base: dict[str, object] = {
        "owner_type": "project",
        "owner_id": 1,
        "sha256": "b" * 64,
        "size_bytes": 1,
    }
    assert not service.register(AttachmentInput(file_name=" ", path="x", **base)).is_ok  # type: ignore[arg-type]
    assert not service.register(
        AttachmentInput(file_name="a", path="x", **{**base, "size_bytes": -1})  # type: ignore[arg-type]
    ).is_ok
    assert not service.delete(999).is_ok
