"""内置技能市场目录：这些技能被本项目认可，可一键加入技能矩阵。"""

from __future__ import annotations

from forgecv.features.market.schemas import MarketSkill

MARKET_SKILLS: tuple[MarketSkill, ...] = (
    MarketSkill(
        key="python",
        name="Python",
        category="语言",
        level=2,
        description="用 Python 编写后端服务、自动化脚本与数据处理流程。",
    ),
    MarketSkill(
        key="sql",
        name="SQL",
        category="数据库",
        level=2,
        description="能独立完成查询、索引设计与慢查询定位。",
    ),
    MarketSkill(
        key="fastapi",
        name="FastAPI",
        category="框架",
        level=2,
        description="用 FastAPI 构建带校验、依赖注入与 OpenAPI 文档的接口。",
    ),
    MarketSkill(
        key="docker",
        name="Docker",
        category="工具链",
        level=2,
        description="编写可复现镜像与容器编排，覆盖本地开发到部署。",
    ),
    MarketSkill(
        key="ci-cd",
        name="CI/CD",
        category="工具链",
        level=2,
        description="用流水线完成静态检查、测试、构建与发布门禁。",
    ),
    MarketSkill(
        key="unit-testing",
        name="单元测试",
        category="工具链",
        level=2,
        description="为核心模块补齐可维护的测试，并覆盖边界与失败路径。",
    ),
    MarketSkill(
        key="observability",
        name="可观测性",
        category="运维",
        level=2,
        description="通过日志、指标与追踪定位线上问题并建立告警。",
    ),
    MarketSkill(
        key="performance-tuning",
        name="性能优化",
        category="运维",
        level=2,
        description="用压测与火焰图定位瓶颈，给出可验证的优化收益。",
    ),
    MarketSkill(
        key="system-design",
        name="系统设计",
        category="软技能",
        level=3,
        description="拆解需求边界，完成模块划分、容量评估与取舍说明。",
    ),
    MarketSkill(
        key="technical-writing",
        name="技术写作",
        category="软技能",
        level=2,
        description="把架构、复盘与使用说明写成别人能直接上手的文档。",
    ),
)
