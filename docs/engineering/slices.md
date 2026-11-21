# 功能切片清单

每个切片是 `src/forgecv/features/<name>/` 下的文件组：`models / schemas / repository /
service / viewmodel / view / api / __init__`。跨切片只允许 `from ..<other>.api import ...`。

M1 阶段先落地 `models / schemas / repository / service / api`；`viewmodel` 与 `view`
随对应页面的里程碑补齐，避免提交空壳页面。

## 1. 已实现

### `settings` — 设置

| 项 | 内容 |
|---|---|
| 路由 | `settings`，标题「设置」 |
| 表 | `app_settings` |
| 对外 API | `build_service(sessions)`、`register(host)` |
| 能力 | 主题选择（system / light / dark / high_contrast），保存后下次启动生效 |
| 测试 | `tests/unit/test_settings_service.py`、`tests/unit/test_settings_viewmodel.py`、`tests/ui/test_settings_page.py` |

## 2. 数据层（M1 已完成）

| 切片 | 表 | 服务职责 | 测试 |
|---|---|---|---|
| `profile` | `candidate`、`certificates` | 候选人保存（姓名/邮箱/链接校验）、证书增删 | `tests/unit/test_profile_service.py` |
| `education` | `educations` | 学历 CRUD、时间自洽校验、排序 | `tests/unit/test_education_service.py` |
| `experience` | `experiences` | 经历 CRUD、亮点条目清洗 | `tests/unit/test_experience_service.py` |
| `project` | `projects`、`project_metrics` | 项目 CRUD、指标整体替换 | `tests/unit/test_project_service.py` |
| `tag` | `tags`、`project_tags` | 四维标签 CRUD、项目标签整体重设 | `tests/unit/test_tag_service.py` |
| `skill` | `skills`、`skill_evidence` | 技能 CRUD、证据链校验 | `tests/unit/test_skill_service.py` |
| `resume` | `resume_versions`、`resume_items`、`snapshots` | 版本 CRUD、条目编排、快照 | `tests/unit/test_resume_service.py` |
| `attachment` | `attachments` | 附件元数据登记与校验 | `tests/unit/test_attachment_service.py` |

公共校验（邮箱、链接、起止时间）在 `platform/core/validation.py`，不重复实现。

### M3 新增（只读聚合）

| 切片 | 表 | 服务职责 | 测试 |
|---|---|---|---|
| `timeline` | 无 | 合并学历 / 经历 / 项目，检测同分区时间重叠 | `tests/unit/test_timeline_service.py` |
| `dashboard` | 无 | 统计、八维雷达、标签分布与改进提示 | `tests/unit/test_dashboard_service.py` |

雷达口径见 [`scoring.md`](scoring.md)。

### M4 新增（简历编排）

| 模块 | 文件 | 职责 | 测试 |
|---|---|---|---|
| 渲染 | `features/resume/render.py`、`document.py` | 版本选择 + 七切片数据组装、纯文本预览 | `tests/unit/test_resume_render.py` |
| 健康度 | `features/resume/checks.py` | 姓名、空分区、量化、证据、标签与指标缺口 | `tests/unit/test_resume_analysis.py` |
| JD 覆盖 | `features/resume/jd.py` | 本地词表匹配，输出覆盖率与缺口 | `tests/unit/test_resume_analysis.py` |

规则文档见 [`resume-rules.md`](resume-rules.md)。

## 3. 页面计划

| 页面 | 路由 | 数据层 | 页面状态 |
|---|---|---|---|
| 个人信息 | `profile` | 已完成 | 已完成（M2） |
| 学历路径 | `education` | 已完成 | 已完成（M2） |
| 统一时间轴 | `timeline` | 只读聚合，已完成 | 已完成（M3） |
| 工作经历 | `experience` | 已完成 | 已完成（M2） |
| 项目库 | `project` | 已完成 | 已完成（M2） |
| 标签管理 | `tag` | 已完成 | 已完成（M2） |
| 技能矩阵 | `skill` | 已完成 | 已完成（M3） |
| 概览 / 雷达 | `dashboard` | 只读聚合，已完成 | 已完成（M3） |
| 简历版本 | `resume` | 已完成 | 已完成（M4） |
| Word 导出 | `export` | 已完成 | 已完成（M5） |
| 快照与 Diff | `snapshot` | 已完成 | 已完成（M5） |

## 4. 切片边界约定

| 场景 | 正确做法 | 错误做法 |
|---|---|---|
| 项目页要显示标签 | `from ..tag.api import build_service` 后调 `tags_for_project` | 直接 import `tag.repository` |
| 简历页要拿项目数据 | 调 `project.api` 的只读查询 | import `project.models` 自行查库 |
| 导出需要多个切片数据 | 组合根注入 `resume.api`，由 `resume` 聚合 | `export` 切片直接读各表 |
| 通用分页 / 日期格式化 | 下沉到 `platform/` | 切片里各写一份 |

## 5. 新增切片流程

```powershell
uv run python scripts/new_feature.py invoices
```

然后：

1. 在 `models.py` 定义表，写 Alembic 迁移并验证回滚。
2. `repository.py` 只做持久化；`service.py` 做校验并返回 `Result`。
3. `viewmodel.py` 暴露信号与状态；`view.py` 只用令牌样式。
4. `api.py` 导出路由常量与 `register(host)`，在 `app/window.py` 注册。
5. 补测试：服务单测 + 离屏 UI 测试 + 分层契约仍绿。
6. 更新本文件、`data-model.md`、CHANGELOG。
