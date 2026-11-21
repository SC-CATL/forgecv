"""概览服务：统计、能力雷达与标签分布。

雷达分值的口径是启发式自评，规则写在 docs/engineering/scoring.md：
用技能等级、项目档案完整度、指标、标签与交付状态做加权，不做任何联网判断。
"""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Callable, Mapping, Sequence
from typing import Protocol

from forgecv.features.dashboard.schemas import DashboardData, TagCount
from forgecv.features.education.service import EducationService
from forgecv.features.experience.service import ExperienceService
from forgecv.features.project.service import ProjectService
from forgecv.features.skill.service import SkillService
from forgecv.features.tag.service import TagService

DIMENSIONS = ("编码", "架构", "测试", "性能", "运维", "协作", "文档", "交付")
TEST_TAGS = {"CI/CD", "测试", "单元测试", "集成测试", "TDD"}
PERF_TAGS = {"性能优化", "压测", "可观测性"}
OPS_TAGS = {"Docker", "Kubernetes", "GitHub Actions", "CI/CD", "Linux", "运维"}
PERF_KEYS = ("QPS", "P99", "延迟", "耗时", "吞吐", "内存")


class ProjectLike(Protocol):
    """雷达只关心项目档案字段。"""

    id: int
    architecture: str
    retrospective: str
    ci_status: str
    status: str
    repo_url: str


class SkillLike(Protocol):
    """雷达只关心技能等级。"""

    id: int
    category: str
    level: int


class ExperienceLike(Protocol):
    """雷达只关心成果条目。"""

    highlights: list[str]


class TagLike(Protocol):
    """雷达只关心标签名与维度。"""

    name: str
    dimension: str


class DashboardService:
    """只读聚合：不写库，不缓存。"""

    def __init__(
        self,
        educations: EducationService,
        experiences: ExperienceService,
        projects: ProjectService,
        skills: SkillService,
        tags: TagService,
    ) -> None:
        """注入五个来源切片。"""
        self._educations = educations
        self._experiences = experiences
        self._projects = projects
        self._skills = skills
        self._tags = tags

    def snapshot(self) -> DashboardData:
        """生成概览快照。"""
        educations = self._educations.list_all()
        experiences = self._experiences.list_all()
        projects = self._projects.list_all()
        skills = self._skills.list_all()
        tags = self._tags.list_all()
        tag_map = {project.id: self._tags.tags_for_project(project.id) for project in projects}
        counts = {
            "学历": len(educations),
            "经历": len(experiences),
            "项目": len(projects),
            "技能": len(skills),
            "标签": len(tags),
        }
        radar = self._radar(experiences, projects, skills, tag_map)
        distribution = self._distribution(tag_map)
        hints = self._hints(projects, skills, tag_map)
        return DashboardData(counts=counts, radar=radar, tags=distribution, hints=hints)

    def _radar(
        self,
        experiences: Sequence[ExperienceLike],
        projects: Sequence[ProjectLike],
        skills: Sequence[SkillLike],
        tag_map: Mapping[int, Sequence[TagLike]],
    ) -> dict[str, int]:
        """八维启发式评分。"""
        levels = [skill.level / 4 * 100 for skill in skills]
        coding = self._average(levels)
        arch = self._ratio(projects, lambda project: bool(project.architecture.strip()))
        testing = self._ratio(
            projects,
            lambda project: bool(project.ci_status.strip())
            or any(tag.name in TEST_TAGS for tag in tag_map.get(project.id, [])),
        )
        perf = self._ratio(
            projects,
            lambda project: any(tag.name in PERF_TAGS for tag in tag_map.get(project.id, []))
            or any(key in PERF_KEYS for key in self._metric_keys(project.id)),
        )
        ops = self._ratio(
            projects,
            lambda project: any(
                tag.dimension == "toolchain" or tag.name in OPS_TAGS
                for tag in tag_map.get(project.id, [])
            ),
        )
        if not projects:
            ops = self._average([100 for skill in skills if skill.category == "运维"])
        collab = self._ratio(experiences, lambda row: bool(row.highlights))
        docs = self._ratio(
            projects,
            lambda project: bool(project.architecture.strip() or project.retrospective.strip()),
        )
        delivery = self._ratio(
            projects,
            lambda project: project.status == "online" or bool(project.repo_url.strip()),
        )
        return {
            "编码": coding,
            "架构": arch,
            "测试": testing,
            "性能": perf,
            "运维": ops,
            "协作": collab,
            "文档": docs,
            "交付": delivery,
        }

    def _metric_keys(self, project_id: int) -> list[str]:
        """项目指标键列表。"""
        return [metric.key for metric in self._projects.metrics_for(project_id)]

    def _distribution(
        self, tag_map: Mapping[int, Sequence[TagLike]]
    ) -> dict[str, list[TagCount]]:
        """按维度统计标签使用次数。"""
        labels = self._tags.dimensions()
        counters: dict[str, Counter[str]] = defaultdict(Counter)
        for tags in tag_map.values():
            for tag in tags:
                counters[tag.dimension][tag.name] += 1
        return {
            labels[dimension]: [
                TagCount(name=name, count=count)
                for name, count in counter.most_common(6)
            ]
            for dimension, counter in counters.items()
        }

    def _hints(
        self,
        projects: Sequence[ProjectLike],
        skills: Sequence[SkillLike],
        tag_map: Mapping[int, Sequence[TagLike]],
    ) -> list[str]:
        """可执行的改进提示。"""
        hints: list[str] = []
        no_evidence = [skill for skill in skills if not self._skills.evidence_for(skill.id)]
        if no_evidence:
            hints.append(f"{len(no_evidence)} 项技能还没有证据，去技能页补项目或经历。")
        no_tags = [project for project in projects if not tag_map.get(project.id)]
        if no_tags:
            hints.append(f"{len(no_tags)} 个项目还没有技术标签。")
        no_metrics = [
            project for project in projects if not self._projects.metrics_for(project.id)
        ]
        if no_metrics:
            hints.append(f"{len(no_metrics)} 个项目没有量化指标。")
        return hints

    @staticmethod
    def _average(values: Sequence[float]) -> int:
        """空列表返回 0，否则取平均并取整。"""
        if not values:
            return 0
        return round(sum(values) / len(values))

    @staticmethod
    def _ratio[T](rows: Sequence[T], predicate: Callable[[T], bool]) -> int:
        """满足条件的占比，说明雷达是「完成度」而非绝对能力。"""
        if not rows:
            return 0
        matched = sum(1 for row in rows if predicate(row))
        return round(matched / len(rows) * 100)
