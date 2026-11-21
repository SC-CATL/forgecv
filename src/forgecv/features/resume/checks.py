"""简历健康度检查：只给建议，不阻断导出（硬性缺失除外）。"""

from __future__ import annotations

from dataclasses import dataclass

from forgecv.features.resume.document import ResumeDocument
from forgecv.features.skill.service import SkillService

LEVELS = {"error": "必须处理", "warn": "建议处理", "hint": "可选优化"}


@dataclass(frozen=True, slots=True)
class CheckIssue:
    """一条检查结果。"""

    level: str
    message: str


def _has_number(lines: list[str]) -> bool:
    """描述里是否含数字。"""
    return any(char.isdigit() for char in "".join(lines))


class ResumeCheckService:
    """基于渲染文档做规则检查。"""

    def __init__(self, skills: SkillService) -> None:
        """注入技能服务，用于证据完整性检查。"""
        self._skills = skills

    def issues(self, document: ResumeDocument) -> list[CheckIssue]:
        """返回按严重程度排序的问题列表。"""
        issues: list[CheckIssue] = []
        if not document.full_name:
            issues.append(CheckIssue("error", "个人信息缺少姓名，无法导出。"))
        if not document.educations:
            issues.append(CheckIssue("warn", "还没有教育经历。"))
        if not document.projects:
            issues.append(CheckIssue("warn", "还没有项目经历，工程能力缺少载体。"))
        if not document.target_role:
            issues.append(CheckIssue("hint", "未填写目标岗位，JD 覆盖分析会缺少方向。"))
        issues.extend(self._quantified(document))
        issues.extend(self._evidence())
        issues.extend(self._project_completeness(document))
        if document.selected_all:
            issues.append(
                CheckIssue("hint", "当前版本未勾选条目，预览包含全部内容。")
            )
        return issues

    @staticmethod
    def _quantified(document: ResumeDocument) -> list[CheckIssue]:
        """无数字的成果条目提示量化。"""
        issues: list[CheckIssue] = []
        weak_experiences = [
            row.company for row in document.experiences if not _has_number(row.highlights)
        ]
        if weak_experiences:
            issues.append(
                CheckIssue("warn", f"{len(weak_experiences)} 段工作经历没有量化成果。")
            )
        weak_projects = [
            row.name for row in document.projects if not _has_number(row.highlights)
        ]
        if weak_projects:
            issues.append(
                CheckIssue("warn", f"{len(weak_projects)} 个项目没有量化亮点。")
            )
        return issues

    def _evidence(self) -> list[CheckIssue]:
        """无证据技能提示。"""
        skills = self._skills.list_all()
        missing = [skill for skill in skills if not self._skills.evidence_for(skill.id)]
        if not skills:
            return []
        if missing:
            return [CheckIssue("warn", f"{len(missing)} 项技能还没有证据。")]
        return []

    @staticmethod
    def _project_completeness(document: ResumeDocument) -> list[CheckIssue]:
        """项目标签、指标缺口。"""
        issues: list[CheckIssue] = []
        if any(not project.tags for project in document.projects):
            issues.append(CheckIssue("hint", "部分项目没有技术标签。"))
        if any(not project.metrics for project in document.projects):
            issues.append(CheckIssue("hint", "部分项目没有量化指标。"))
        return issues
