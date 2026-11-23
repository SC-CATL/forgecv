"""写入一份演示数据：建档 -> 学历 -> 经历 -> 项目 -> 标签 -> 技能 -> 简历版本。"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from forgecv.features.education.api import build_service as build_education
from forgecv.features.education.schemas import EducationInput
from forgecv.features.experience.api import build_service as build_experience
from forgecv.features.experience.schemas import ExperienceInput
from forgecv.features.market.api import build_service as build_market
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
from forgecv.platform.adapters.db.engine import create_engine_for
from forgecv.platform.adapters.db.migrate import upgrade
from forgecv.platform.adapters.db.session import SessionFactory, create_session_factory
from forgecv.platform.config import load_settings
from forgecv.platform.core.result import Result


def take[T](result: Result[T, Any], label: str) -> T:
    """失败即中止，避免写入半套演示数据。"""
    if not result.is_ok:
        raise SystemExit(f"演示数据写入失败（{label}）：{result.error()}")
    return result.unwrap()


def seed_candidate(sessions: SessionFactory) -> None:
    """候选人、两段学历与一段经历。"""
    profile = build_profile(sessions)
    take(
        profile.save(
            CandidateInput(
                full_name="张三",
                headline="后端工程师",
                email="zhangsan@example.com",
                phone="00000000000",
                city="杭州",
                github_url="https://github.com/example",
                summary="关注高并发服务与工程效率。",
            )
        ),
        "candidate",
    )
    education = build_education(sessions)
    take(
        education.add(
            EducationInput(
                school="浙江大学",
                degree_level="本科",
                major="软件工程",
                start_date=date(2016, 9, 1),
                end_date=date(2020, 6, 30),
                gpa="3.8/4.0",
                courses=["操作系统", "数据库", "编译原理"],
            )
        ),
        "education.bachelor",
    )
    take(
        education.add(
            EducationInput(
                school="浙江大学",
                degree_level="硕士",
                major="计算机技术",
                start_date=date(2020, 9, 1),
                end_date=date(2023, 6, 30),
                thesis="面向高并发网关的调度优化",
            )
        ),
        "education.master",
    )
    experience = build_experience(sessions)
    take(
        experience.add(
            ExperienceInput(
                company="某互联网公司",
                role="后端工程师",
                location="杭州",
                start_date=date(2023, 7, 1),
                is_current=True,
                summary="负责 API 网关与内部工具链。",
                highlights=["网关 P99 从 120ms 降到 45ms", "推动 CI 覆盖率门禁落地"],
            )
        ),
        "experience",
    )


def seed_projects(sessions: SessionFactory) -> tuple[int, int]:
    """两个项目及指标。"""
    projects = build_project(sessions)
    gateway = take(
        projects.add(
            ProjectInput(
                name="高并发 API 网关",
                direction="后端",
                role="核心开发",
                start_date=date(2023, 8, 1),
                status="online",
                repo_url="https://github.com/example/gateway",
                summary="多租户 API 网关，支持限流与灰度。",
                architecture="控制面 / 数据面分离，规则热加载。",
                highlights=["限流规则热更新零重启", "压测 QPS 提升 3 倍"],
                metrics=[
                    MetricInput(key="QPS", value="1200", unit="req/s"),
                    MetricInput(key="P99", value="45", unit="ms"),
                ],
            )
        ),
        "project.gateway",
    )
    tool = take(
        projects.add(
            ProjectInput(
                name="ForgeCV 简历工坊",
                direction="工具链",
                role="独立开发",
                status="wip",
                summary="结构化简历与工程能力举证工具。",
                highlights=["技能证据链模型", "Word 导出与健康度检查"],
            )
        ),
        "project.forgecv",
    )
    return gateway.id, tool.id


def seed_taxonomy(sessions: SessionFactory, project_id: int) -> None:
    """标签、技能与证据。"""
    tags = build_tag(sessions)
    python = take(tags.create(TagInput(name="Python", dimension="language")), "tag.python")
    take(tags.create(TagInput(name="FastAPI", dimension="toolchain")), "tag.fastapi")
    take(tags.create(TagInput(name="CI/CD", dimension="practice")), "tag.ci")
    take(tags.create(TagInput(name="性能优化", dimension="practice")), "tag.perf")
    take(tags.create(TagInput(name="后端", dimension="domain")), "tag.backend")
    tags.set_project_tags(project_id, [python.id])
    skills = build_skill(sessions)
    python_skill = take(
        skills.add(SkillInput(name="Python", category="语言", level=4, years=5, self_score=90)),
        "skill.python",
    )
    take(
        skills.add(SkillInput(name="SQL", category="数据库", level=3, years=4, self_score=75)),
        "skill.sql",
    )
    take(
        skills.add_evidence(
            EvidenceInput(
                skill_id=python_skill.id,
                project_id=project_id,
                statement="用 Python 实现网关控制面与规则热加载。",
            )
        ),
        "skill.evidence",
    )
    take(build_market(sessions).learn("python"), "market.python")


def seed_resume(sessions: SessionFactory, project_id: int) -> None:
    """默认简历版本与条目。"""
    resume = build_resume(sessions)
    version = take(
        resume.create_version(
            VersionInput(name="后端版", target_role="后端工程师", is_default=True)
        ),
        "resume.version",
    )
    take(
        resume.add_item(version.id, ItemInput(item_type="project", item_id=project_id)),
        "resume.item",
    )


def main() -> int:
    """建库、迁移并写入演示数据。"""
    settings = load_settings()
    upgrade(settings)
    engine = create_engine_for(settings)
    try:
        sessions = create_session_factory(engine)
        if build_profile(sessions).load() is not None:
            print("已存在候选人数据，跳过演示数据写入。")
            return 0
        seed_candidate(sessions)
        gateway_id, tool_id = seed_projects(sessions)
        seed_taxonomy(sessions, gateway_id)
        seed_resume(sessions, tool_id)
        print("演示数据已写入。启动：uv run dev")
        return 0
    finally:
        engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
