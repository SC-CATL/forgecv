"""JD 覆盖分析与健康度检查。"""

from __future__ import annotations

from forgecv.features.resume.checks import ResumeCheckService
from forgecv.features.resume.document import ProjectView, ResumeDocument
from forgecv.features.resume.jd import analyze
from forgecv.features.skill.api import build_service as build_skill
from forgecv.platform.adapters.db.session import SessionFactory


def test_jd_matches_and_reports_gaps() -> None:
    """已掌握词算匹配，词表内未掌握算缺口。"""
    report = analyze("要求 Python 与 Kubernetes，了解 FastAPI", ["Python", "FastAPI"])
    assert report.coverage == 67
    assert "Python" in report.matched
    assert "Kubernetes" in report.missing


def test_jd_empty_and_unknown() -> None:
    """空 JD 与无词表命中都有说明。"""
    assert analyze("   ", []).message
    report = analyze("负责团队沟通与协作", ["Python"])
    assert report.coverage == 0
    assert "没有识别" in report.message


def _document(**overrides: object) -> ResumeDocument:
    """构造最小文档，按需覆盖字段。"""
    values: dict[str, object] = {
        "version_name": "后端版",
        "target_role": "后端工程师",
        "full_name": "张三",
        "headline": "后端",
        "city": "杭州",
        "email": "",
        "phone": "",
        "links": [],
        "educations": [],
        "experiences": [],
        "projects": [],
        "skill_groups": {},
        "certificates": [],
    }
    values.update(overrides)
    return ResumeDocument(**values)  # type: ignore[arg-type]


def test_checks_report_missing_sections(sessions: SessionFactory) -> None:
    """缺姓名、教育、项目都会给出对应级别。"""
    issues = ResumeCheckService(build_skill(sessions)).issues(
        _document(full_name="", target_role="")
    )
    levels = {issue.level for issue in issues}
    assert "error" in levels
    assert any("教育" in issue.message for issue in issues)
    assert any("项目" in issue.message for issue in issues)


def test_checks_flag_unquantified_projects(sessions: SessionFactory) -> None:
    """项目亮点没有数字时提示量化。"""
    document = _document(
        projects=[
            ProjectView(
                name="网关",
                direction="后端",
                role="开发",
                period="2023.01 – 至今",
                highlights=["做了网关"],
                metrics=["QPS 1200"],
            )
        ]
    )
    issues = ResumeCheckService(build_skill(sessions)).issues(document)
    assert any("量化" in issue.message for issue in issues)


def test_checks_clean_document(sessions: SessionFactory) -> None:
    """完整文档不报硬性问题。"""
    document = _document(
        educations=[],  # 仍会提示教育，但不应有 error
        projects=[
            ProjectView(
                name="网关",
                direction="后端",
                role="开发",
                period="2023.01 – 至今",
                highlights=["QPS 提升 30%"],
                metrics=["QPS 1200"],
                tags=["Python"],
            )
        ],
    )
    issues = ResumeCheckService(build_skill(sessions)).issues(document)
    assert all(issue.level != "error" for issue in issues)
