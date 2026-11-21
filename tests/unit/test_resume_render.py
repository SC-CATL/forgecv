"""简历渲染：条目选择与纯文本预览。"""

from __future__ import annotations

from datetime import date

from forgecv.features.education.api import build_service as build_education
from forgecv.features.education.schemas import EducationInput
from forgecv.features.experience.api import build_service as build_experience
from forgecv.features.experience.schemas import ExperienceInput
from forgecv.features.profile.api import build_service as build_profile
from forgecv.features.project.api import build_service as build_project
from forgecv.features.project.schemas import MetricInput, ProjectInput
from forgecv.features.resume.api import build_service as build_resume
from forgecv.features.resume.render import ResumeRenderer, render_text
from forgecv.features.resume.schemas import ItemInput, VersionInput
from forgecv.features.skill.api import build_service as build_skill
from forgecv.features.skill.schemas import SkillInput
from forgecv.features.tag.api import build_service as build_tag
from forgecv.features.tag.schemas import TagInput
from forgecv.platform.adapters.db.session import SessionFactory


def _renderer(sessions: SessionFactory) -> ResumeRenderer:
    """装配七切片渲染器。"""
    return ResumeRenderer(
        resume=build_resume(sessions),
        profile=build_profile(sessions),
        educations=build_education(sessions),
        experiences=build_experience(sessions),
        projects=build_project(sessions),
        skills=build_skill(sessions),
        tags=build_tag(sessions),
    )


def test_render_all_when_nothing_selected(sessions: SessionFactory, candidate: int) -> None:
    """未勾选条目时渲染全部，并标注 selected_all。"""
    build_education(sessions).add(
        EducationInput(
            school="浙大", start_date=date(2020, 9, 1), end_date=date(2024, 6, 1)
        )
    )
    project = build_project(sessions).add(
        ProjectInput(
            name="网关",
            direction="后端",
            highlights=["QPS 提升 3 倍"],
            metrics=[MetricInput(key="QPS", value="1200")],
        )
    ).unwrap()
    build_tag(sessions).set_project_tags(
        project.id,
        [build_tag(sessions).create(TagInput(name="Python")).unwrap().id],
    )
    build_experience(sessions).add(
        ExperienceInput(
            company="某公司",
            role="后端",
            start_date=date(2024, 7, 1),
            is_current=True,
            highlights=["降延迟 40%"],
        )
    )
    build_skill(sessions).add(SkillInput(name="Python", level=3, years=4))
    version = build_resume(sessions).create_version(VersionInput(name="后端版")).unwrap()
    document = _renderer(sessions).build(version)
    assert document.selected_all
    assert len(document.educations) == 1
    assert len(document.projects) == 1
    text = render_text(document)
    assert "测试候选人" in text
    assert "网关" in text
    assert "QPS 1200" in text


def test_render_selected_project_only(sessions: SessionFactory, candidate: int) -> None:
    """只勾选项目时，其他分区为空。"""
    build_education(sessions).add(
        EducationInput(
            school="浙大", start_date=date(2020, 9, 1), end_date=date(2024, 6, 1)
        )
    )
    project = build_project(sessions).add(
        ProjectInput(name="网关", direction="后端", role="核心开发")
    ).unwrap()
    version = build_resume(sessions).create_version(VersionInput(name="后端版")).unwrap()
    build_resume(sessions).add_item(
        version.id, ItemInput(item_type="project", item_id=project.id)
    )
    document = _renderer(sessions).build(version)
    assert not document.selected_all
    assert document.educations == []
    assert [row.name for row in document.projects] == ["网关"]
    assert "项目经历" in render_text(document)
