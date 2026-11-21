"""概览服务：统计、雷达与提示。"""

from __future__ import annotations

from datetime import date

from forgecv.features.dashboard.api import build_service
from forgecv.features.education.api import build_service as build_education
from forgecv.features.education.schemas import EducationInput
from forgecv.features.experience.api import build_service as build_experience
from forgecv.features.experience.schemas import ExperienceInput
from forgecv.features.project.api import build_service as build_project
from forgecv.features.project.schemas import MetricInput, ProjectInput
from forgecv.features.skill.api import build_service as build_skill
from forgecv.features.skill.schemas import EvidenceInput, SkillInput
from forgecv.features.tag.api import build_service as build_tag
from forgecv.features.tag.schemas import TagInput
from forgecv.platform.adapters.db.session import SessionFactory


def test_empty_snapshot(sessions: SessionFactory) -> None:
    """空库返回全 0，不报错。"""
    data = build_service(sessions).snapshot()
    assert data.counts["项目"] == 0
    assert set(data.radar.values()) == {0}
    assert data.hints == []


def test_snapshot_with_full_data(sessions: SessionFactory, candidate: int) -> None:
    """有完整数据时关键维度拉满，标签按维度聚合。"""
    project = build_project(sessions).add(
        ProjectInput(
            name="网关",
            direction="后端",
            status="online",
            repo_url="https://github.com/example/gateway",
            architecture="控制面 / 数据面分离",
            retrospective="复盘",
            ci_status="passing",
            highlights=["QPS 提升"],
            metrics=[MetricInput(key="QPS", value="1200")],
        )
    ).unwrap()
    tag = build_tag(sessions).create(TagInput(name="Python", dimension="language")).unwrap()
    build_tag(sessions).set_project_tags(project.id, [tag.id])
    skill = build_skill(sessions).add(SkillInput(name="Python", level=4)).unwrap()
    build_skill(sessions).add_evidence(
        EvidenceInput(skill_id=skill.id, project_id=project.id, statement="核心开发")
    )
    build_education(sessions).add(
        EducationInput(
            school="浙大", start_date=date(2020, 9, 1), end_date=date(2024, 6, 1)
        )
    )
    build_experience(sessions).add(
        ExperienceInput(
            company="某公司",
            role="后端",
            start_date=date(2024, 7, 1),
            is_current=True,
            highlights=["降延迟"],
        )
    )
    data = build_service(sessions).snapshot()
    assert data.counts == {"学历": 1, "经历": 1, "项目": 1, "技能": 1, "标签": 1}
    assert data.radar["编码"] == 100
    assert data.radar["交付"] == 100
    assert data.radar["文档"] == 100
    assert data.tags["语言"][0].name == "Python"
    assert data.hints == []


def test_hints_report_missing_evidence(sessions: SessionFactory, candidate: int) -> None:
    """无证据技能、无标签项目、无指标项目都会提示。"""
    build_skill(sessions).add(SkillInput(name="Go"))
    build_project(sessions).add(ProjectInput(name="工具", direction="工具链"))
    hints = build_service(sessions).snapshot().hints
    assert any("技能" in hint for hint in hints)
    assert any("标签" in hint for hint in hints)
    assert any("指标" in hint for hint in hints)
