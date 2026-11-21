"""简历渲染模型：与格式无关，供预览与 Word 导出共用。"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

LEVEL_LABELS = {1: "了解", 2: "熟悉", 3: "熟练", 4: "精通"}


def short_date(value: date | None) -> str:
    """yyyy.MM，空值显示至今。"""
    return "至今" if value is None else f"{value.year:04d}.{value.month:02d}"


def range_text(start: date | None, end: date | None, is_current: bool) -> str:
    """时间区间文案。"""
    return f"{short_date(start)} – {'至今' if is_current else short_date(end)}"


@dataclass(frozen=True, slots=True)
class EducationView:
    """教育条目。"""

    school: str
    degree: str
    major: str
    period: str
    gpa: str = ""
    courses: list[str] = field(default_factory=list)
    thesis: str = ""


@dataclass(frozen=True, slots=True)
class ExperienceView:
    """工作条目。"""

    company: str
    role: str
    period: str
    highlights: list[str] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class ProjectView:
    """项目条目。"""

    name: str
    direction: str
    role: str
    period: str
    tags: list[str] = field(default_factory=list)
    highlights: list[str] = field(default_factory=list)
    metrics: list[str] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class SkillView:
    """技能条目。"""

    name: str
    level: str
    years: float | None = None


@dataclass(frozen=True, slots=True)
class CertificateView:
    """证书条目。"""

    name: str
    issuer: str
    issued_on: date | None = None


@dataclass(frozen=True, slots=True)
class ResumeDocument:
    """一份可直接渲染的简历。"""

    version_name: str
    target_role: str
    full_name: str
    headline: str
    city: str
    email: str
    phone: str
    links: list[str]
    educations: list[EducationView]
    experiences: list[ExperienceView]
    projects: list[ProjectView]
    skill_groups: dict[str, list[SkillView]]
    certificates: list[CertificateView]
    selected_all: bool = False
