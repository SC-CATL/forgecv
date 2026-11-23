# 变更记录

格式遵循 Keep a Changelog，版本遵循 SemVer。

## [Unreleased]

### Added

- 技能市场页（`market`）：按分类浏览项目认可的技能，一键学习后写入技能矩阵。
- 技能新增 `market_key` / `market_tag` 字段（迁移 `0003`），市场技能在矩阵中显示「市场认证」。
- 学习市场技能复用技能切片校验：重复学习幂等，同名技能保留原熟练度并补认证标签。

### Fixed

- 图形启动统一在 `bootstrap.run` 中执行迁移，修复直接运行 `main.py` / `uv run app`
  时旧库缺列（如 `skills.market_key`）导致的启动崩溃。
- 启动时确保单候选人占位行存在，修复空数据库首次学习市场技能或新增技能时
  外键 `candidate_id = 1` 失败（`FOREIGN KEY constraint failed`）。

## [0.1.0] - 2026-11-21

### Added

- 横纵分层骨架：`app/` 组合根、`platform/` 技术平台、`features/` 业务切片。
- 六服务 UI Runtime：主题、弹窗、布局、路由、线程池、生命周期。
- 设置切片（七件套）与 `app_settings` 初始迁移。
- `uv run dev` 一键启动、`uv run doctor` 环境体检、`scripts/dev.py` 热重启。
- 质量门禁：ruff / mypy / import-linter / pytest / coverage / pip-audit。
- M0 工程文档：架构、数据字典、切片清单、Word 导出规范、质量门禁、DX。
- M0 用户文档：快速上手、功能地图。
- ADR 0001 本地优先 SQLite、ADR 0002 仅 Word 导出、ADR 0003 四维项目标签。
- `README.md` 项目定位、里程碑状态与文档入口。
- M1 核心数据层：15 张表、迁移 `0002_core_schema`、8 个业务切片
  （profile / education / experience / project / tag / skill / resume / attachment）。
- 公共输入校验 `platform/core/validation.py`（邮箱、链接、起止时间）。
- `scripts/seed.py` 演示数据写入，重复执行自动跳过。
- M2 五个业务页面：个人信息与证书、学历路径、工作经历、项目库、标签管理。
- 项目页支持自定义指标表格与四维标签勾选，保存时联动 `project_tags`。
- 公共 UI 组件 `platform/ui/kit/forms.py`、展示格式化 `format.py`；
  项目指标与标签选择器拆到 `features/project/fragments.py`。
- M3 技能矩阵页：熟练度、年限、自评分与技能证据链维护。
- M3 统一时间轴：学历 / 经历 / 项目合并排序，同分区重叠提示。
- M3 概览页：统计卡片、八维能力雷达（`platform/ui/kit/charts.py`）、标签分布、改进提示。
- 雷达口径文档 `docs/engineering/scoring.md`。
- M4 简历版本页：版本管理、跨切片条目勾选与排序、实时预览。
- M4 渲染模型 `features/resume/document.py` + 七切片组装器，供预览与 Word 导出共用。
- M4 健康度检查与 JD 覆盖分析（本地词表），规则文档 `docs/engineering/resume-rules.md`。
- M5 Word 导出：`python-docx`、A4 版式、中文字体 eastAsia、页脚页码域、命名与查重。
- M5 导出页与预检：缺姓名阻断，其余提示。
- M5 版本快照页：保存渲染文本、列表查看、两份快照行级 Diff。
- M6 发布收尾：`run.bat` 一键启动、示例 docx、启动耗时基线、文档状态校准。

### Changed

- 窗口标题改为「ForgeCV 工程师简历工坊」，数据目录仍为 `%LOCALAPPDATA%/ForgeCV`。
- `__main__.py` 帮助文本换行，满足 100 列行宽。
- 数据字典从设计稿更新为已实现，切片清单标注各页面数据层状态。

### Verified

- `main.py --self-test` 退出码 0。
- python -m pytest 153 项通过，覆盖率 90.94%。
- ruff / mypy / import-linter 全绿。
- `alembic upgrade head` 与 `downgrade base` 均可执行。
- 离屏启动后逐个导航 dashboard / profile / education / timeline / experience /
  project / tag / skill / resume / export / snapshot / settings 通过。
