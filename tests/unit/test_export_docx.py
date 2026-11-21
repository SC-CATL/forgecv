"""Word 导出：版式、命名与落盘。"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn

from forgecv.features.education.api import build_service as build_education
from forgecv.features.education.schemas import EducationInput
from forgecv.features.experience.api import build_service as build_experience
from forgecv.features.export.docx_writer import write_docx
from forgecv.features.export.service import ExportService, safe_name, unique_path
from forgecv.features.profile.api import build_service as build_profile
from forgecv.features.profile.schemas import CandidateInput
from forgecv.features.project.api import build_service as build_project
from forgecv.features.project.schemas import MetricInput, ProjectInput
from forgecv.features.resume.api import build_service as build_resume
from forgecv.features.resume.checks import ResumeCheckService
from forgecv.features.resume.document import (
    EducationView,
    ProjectView,
    ResumeDocument,
    SkillView,
)
from forgecv.features.resume.render import ResumeRenderer
from forgecv.features.resume.schemas import VersionInput
from forgecv.features.skill.api import build_service as build_skill
from forgecv.features.skill.schemas import SkillInput
from forgecv.features.tag.api import build_service as build_tag
from forgecv.platform.adapters.db.session import SessionFactory


def _document() -> ResumeDocument:
    """一份覆盖主要分区的最小文档。"""
    return ResumeDocument(
        version_name="后端版",
        target_role="后端工程师",
        full_name="张三",
        headline="后端工程师",
        city="杭州",
        email="a@b.com",
        phone="00000000000",
        links=["https://github.com/example"],
        educations=[
            EducationView(
                school="浙江大学",
                degree="本科",
                major="软件工程",
                period="2020.09 – 2024.06",
                gpa="3.8/4.0",
                courses=["操作系统"],
                thesis="调度优化",
            )
        ],
        experiences=[],
        projects=[
            ProjectView(
                name="网关",
                direction="后端",
                role="核心开发",
                period="2023.01 – 至今",
                tags=["Python"],
                highlights=["QPS 提升 3 倍"],
                metrics=["QPS 1200req/s"],
            )
        ],
        skill_groups={"语言": [SkillView(name="Python", level="熟练", years=4)]},
        certificates=[],
    )


def test_writer_sets_cjk_fonts(tmp_path: Path) -> None:
    """导出文件包含姓名、分区，且正文显式写入 eastAsia 字体。"""
    target = write_docx(_document(), tmp_path / "out.docx")
    document = Document(str(target))
    text = "\n".join(paragraph.text for paragraph in document.paragraphs)
    assert "张三" in text
    assert "教育经历" in text
    assert "项目经历" in text
    assert "技术能力" in text
    first = document.paragraphs[0].runs[0]
    assert first._element.rPr.rFonts.get(qn("w:eastAsia")) == "微软雅黑"


def test_safe_name_and_unique_path(tmp_path: Path) -> None:
    """非法字符被替换，重名追加序号。"""
    assert safe_name('a/b:c*?"<>|') == "a_b_c______"
    first = tmp_path / "x.docx"
    first.write_text("x", encoding="utf-8")
    assert unique_path(tmp_path, "x").name == "x-2.docx"


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


def test_export_service_writes_file(sessions: SessionFactory, tmp_path: Path) -> None:
    """从完整数据导出 docx，文件名符合规范。"""
    build_profile(sessions).save(CandidateInput(full_name="张三", city="杭州"))
    project = build_project(sessions).add(
        ProjectInput(
            name="网关",
            direction="后端",
            metrics=[MetricInput(key="QPS", value="1200")],
        )
    ).unwrap()
    build_tag(sessions).set_project_tags(project.id, [])
    build_education(sessions).add(
        EducationInput(
            school="浙大", start_date=date(2020, 9, 1), end_date=date(2024, 6, 1)
        )
    )
    build_skill(sessions).add(SkillInput(name="Python", level=3, years=4))
    version = build_resume(sessions).create_version(
        VersionInput(name="后端版", target_role="后端工程师")
    ).unwrap()
    renderer = _renderer(sessions)
    service = ExportService(renderer, ResumeCheckService(build_skill(sessions)))
    result = service.export(version, tmp_path)
    assert result.is_ok
    path = result.unwrap()
    assert path.exists()
    assert "张三-后端工程师-" in path.name


def test_export_requires_name(sessions: SessionFactory, tmp_path: Path) -> None:
    """没有姓名时拒绝导出。"""
    version = build_resume(sessions).create_version(VersionInput(name="空版本")).unwrap()
    service = ExportService(
        _renderer(sessions), ResumeCheckService(build_skill(sessions))
    )
    assert not service.export(version, tmp_path).is_ok
