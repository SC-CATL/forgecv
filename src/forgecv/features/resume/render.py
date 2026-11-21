"""把版本与各切片数据组装成与格式无关的简历文档。"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Protocol

from forgecv.features.education.service import EducationService
from forgecv.features.experience.service import ExperienceService
from forgecv.features.profile.service import ProfileService
from forgecv.features.project.service import ProjectService
from forgecv.features.resume.document import (
    LEVEL_LABELS,
    CertificateView,
    EducationView,
    ExperienceView,
    ProjectView,
    ResumeDocument,
    SkillView,
    range_text,
)
from forgecv.features.resume.models import ResumeVersion
from forgecv.features.resume.service import ResumeService
from forgecv.features.skill.service import SkillService
from forgecv.features.tag.service import TagService

ITEM_TYPES = ("education", "experience", "project", "skill", "certificate")


class HasId(Protocol):
    """选择条目需要一个稳定 id。"""

    id: int


class ResumeRenderer:
    """只读组装器；不写库。"""

    def __init__(
        self,
        *,
        resume: ResumeService,
        profile: ProfileService,
        educations: EducationService,
        experiences: ExperienceService,
        projects: ProjectService,
        skills: SkillService,
        tags: TagService,
    ) -> None:
        """注入七个切片服务。"""
        self._resume = resume
        self._profile = profile
        self._educations = educations
        self._experiences = experiences
        self._projects = projects
        self._skills = skills
        self._tags = tags

    def build(self, version: ResumeVersion) -> ResumeDocument:
        """按版本选择组装文档。"""
        items = self._resume.items(version.id)
        selected = {(item.item_type, item.item_id) for item in items}
        order = {
            (item.item_type, item.item_id): item.sort_order
            for item in items
        }
        selected_all = not selected
        candidate = self._profile.load()
        links = []
        if candidate is not None:
            links = [
                value
                for value in (candidate.github_url, candidate.blog_url, candidate.website_url)
                if value
            ]
        return ResumeDocument(
            version_name=version.name,
            target_role=version.target_role,
            full_name="" if candidate is None else candidate.full_name,
            headline="" if candidate is None else candidate.headline,
            city="" if candidate is None else candidate.city,
            email="" if candidate is None else candidate.email,
            phone="" if candidate is None else candidate.phone,
            links=links,
            educations=self._education_views(
                self._select(self._educations.list_all(), "education", selected, order)
            ),
            experiences=self._experience_views(
                self._select(self._experiences.list_all(), "experience", selected, order)
            ),
            projects=self._project_views(
                self._select(self._projects.list_all(), "project", selected, order)
            ),
            skill_groups=self._skill_groups(
                self._select(self._skills.list_all(), "skill", selected, order)
            ),
            certificates=self._certificate_views(
                self._select(self._profile.certificates(), "certificate", selected, order)
            ),
            selected_all=selected_all,
        )

    @staticmethod
    def _select[T: HasId](
        rows: Sequence[T],
        kind: str,
        selected: set[tuple[str, int]],
        order: dict[tuple[str, int], int],
    ) -> list[T]:
        """按版本选择过滤并排序；未选择任何条目时返回全部。"""
        if not selected:
            return list(rows)
        chosen = [row for row in rows if (kind, row.id) in selected]
        return sorted(chosen, key=lambda row: order.get((kind, row.id), 0))

    @staticmethod
    def _education_views(rows: Sequence[Any]) -> list[EducationView]:
        """教育条目视图。"""
        return [
            EducationView(
                school=row.school,
                degree=row.degree_level,
                major=row.major,
                period=range_text(row.start_date, row.end_date, row.is_current),
                gpa=row.gpa,
                courses=list(row.courses),
                thesis=row.thesis,
            )
            for row in rows
        ]

    @staticmethod
    def _experience_views(rows: Sequence[Any]) -> list[ExperienceView]:
        """经历条目视图。"""
        return [
            ExperienceView(
                company=row.company,
                role=row.role,
                period=range_text(row.start_date, row.end_date, row.is_current),
                highlights=list(row.highlights),
            )
            for row in rows
        ]

    def _project_views(self, rows: Sequence[Any]) -> list[ProjectView]:
        """项目条目视图，带标签与指标。"""
        views: list[ProjectView] = []
        for row in rows:
            metrics = [
                f"{metric.key} {metric.value}{metric.unit}"
                for metric in self._projects.metrics_for(row.id)
            ]
            tags = [tag.name for tag in self._tags.tags_for_project(row.id)]
            views.append(
                ProjectView(
                    name=row.name,
                    direction=row.direction,
                    role=row.role,
                    period=range_text(row.start_date, row.end_date, False),
                    tags=tags,
                    highlights=list(row.highlights),
                    metrics=metrics,
                )
            )
        return views

    @staticmethod
    def _skill_groups(rows: Sequence[Any]) -> dict[str, list[SkillView]]:
        """技能按分类分组。"""
        groups: dict[str, list[SkillView]] = {}
        for row in rows:
            groups.setdefault(row.category, []).append(
                SkillView(
                    name=row.name,
                    level=LEVEL_LABELS.get(row.level, str(row.level)),
                    years=row.years,
                )
            )
        return groups

    @staticmethod
    def _certificate_views(rows: Sequence[Any]) -> list[CertificateView]:
        """证书条目视图。"""
        return [
            CertificateView(name=row.name, issuer=row.issuer, issued_on=row.issued_on)
            for row in rows
        ]


def render_text(document: ResumeDocument) -> str:
    """把文档渲染成纯文本预览；排版细节留给 Word 导出。"""
    lines: list[str] = []
    headline = f" · {document.headline}" if document.headline else ""
    lines.append(f"{document.full_name or '未填写姓名'}{headline}")
    contact = [part for part in (document.city, document.email, document.phone) if part]
    if contact:
        lines.append(" | ".join(contact))
    if document.links:
        lines.append(" | ".join(document.links))
    lines.append("")
    _education_block(document, lines)
    _experience_block(document, lines)
    _project_block(document, lines)
    _skill_block(document, lines)
    _certificate_block(document, lines)
    if document.selected_all:
        lines.append("")
        lines.append("（当前版本未勾选条目，预览包含全部内容）")
    return "\n".join(lines).strip()


def _education_block(document: ResumeDocument, lines: list[str]) -> None:
    """教育分区。"""
    if not document.educations:
        return
    lines.append("【教育经历】")
    for row in document.educations:
        lines.append(f"{row.period}  {row.school} · {row.degree} · {row.major}")
        if row.gpa:
            lines.append(f"  GPA {row.gpa}")
        if row.courses:
            lines.append(f"  主修：{'、'.join(row.courses)}")
        if row.thesis:
            lines.append(f"  论文：{row.thesis}")
    lines.append("")


def _experience_block(document: ResumeDocument, lines: list[str]) -> None:
    """工作分区。"""
    if not document.experiences:
        return
    lines.append("【工作经历】")
    for row in document.experiences:
        lines.append(f"{row.period}  {row.company} · {row.role}")
        lines.extend(f"  · {item}" for item in row.highlights)
    lines.append("")


def _project_block(document: ResumeDocument, lines: list[str]) -> None:
    """项目分区。"""
    if not document.projects:
        return
    lines.append("【项目经历】")
    for row in document.projects:
        lines.append(f"{row.period}  {row.name} · {row.direction} · {row.role}")
        if row.tags:
            lines.append(f"  标签：{' · '.join(row.tags)}")
        lines.extend(f"  · {item}" for item in row.highlights)
        if row.metrics:
            lines.append(f"  指标：{' · '.join(row.metrics)}")
    lines.append("")


def _skill_block(document: ResumeDocument, lines: list[str]) -> None:
    """技能分区。"""
    if not document.skill_groups:
        return
    lines.append("【技术能力】")
    for category, skills in document.skill_groups.items():
        parts = []
        for skill in skills:
            years = f"，{skill.years:g} 年" if skill.years else ""
            parts.append(f"{skill.name}（{skill.level}{years}）")
        lines.append(f"{category}：{' · '.join(parts)}")
    lines.append("")


def _certificate_block(document: ResumeDocument, lines: list[str]) -> None:
    """证书分区。"""
    if not document.certificates:
        return
    lines.append("【证书与荣誉】")
    for row in document.certificates:
        issued = f" · {row.issued_on.isoformat()}" if row.issued_on else ""
        lines.append(f"{row.name} · {row.issuer}{issued}")
