# 数据字典

> 状态：M1 已实现（迁移 `0002_core_schema`）。表结构与本文件同 PR 更新。
> 唯一事实源是 `src/forgecv/features/*/models.py` 与 `alembic/versions/`。

## 1. 约定

- 主键统一为自增整数 `id`。
- 所有表继承 `TimestampMixin`，含 `created_at` / `updated_at`（UTC）。
- 日期使用 `DATE`，时间使用带时区 `DATETIME`。
- 列表类字段用 JSON 数组（SQLite 以 TEXT 存储），不拆成「逗号分隔字符串」。
- 外键默认 `ON DELETE CASCADE`；SQLite 已开启 `PRAGMA foreign_keys=ON`。
- 当前只支持单个候选人（业务上固定 `candidate.id = 1`），多版本在简历层实现，不复制人。

## 2. 关系总览

```text
candidate 1 ─── n educations
          1 ─── n experiences
          1 ─── n projects ─── n project_metrics
           │         └── n project_tags ─── n tags
          1 ─── n skills ─── n skill_evidence ──> projects / experiences
          1 ─── n certificates
          1 ─── n resume_versions ─── n resume_items
                                └── n snapshots
attachments（按 owner_type + owner_id 挂到任意实体）
app_settings（键值配置）
```

## 3. 表定义

### 3.1 `candidate` — 候选人

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | INTEGER | PK | 固定为 1 |
| `full_name` | TEXT(80) | NOT NULL | 姓名 |
| `headline` | TEXT(120) | 可空 | 求职意向，如「后端工程师」 |
| `email` | TEXT(120) | 可空 | 邮箱 |
| `phone` | TEXT(40) | 可空 | 电话 |
| `city` | TEXT(60) | 可空 | 所在城市 |
| `github_url` | TEXT(300) | 可空 | GitHub |
| `blog_url` | TEXT(300) | 可空 | 博客 |
| `website_url` | TEXT(300) | 可空 | 个人主页 |
| `summary` | TEXT | 可空 | 自我评价 |

### 3.2 `educations` — 学历节点

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | INTEGER | PK | |
| `candidate_id` | INTEGER | FK → candidate, index | |
| `school` | TEXT(120) | NOT NULL | 院校 |
| `degree_level` | TEXT(20) | NOT NULL | 专科 / 本科 / 硕士 / 博士 / 其他 |
| `major` | TEXT(120) | 可空 | 专业 |
| `start_date` | DATE | NOT NULL | 入学 |
| `end_date` | DATE | 可空 | 毕业；在读为空 |
| `is_current` | BOOLEAN | NOT NULL, 默认 false | 是否在读 |
| `gpa` | TEXT(32) | 可空 | 如 `3.8/4.0`，保留原始写法 |
| `courses` | JSON | 可空 | 主修课程列表 |
| `thesis` | TEXT(300) | 可空 | 论文 / 毕设 |
| `notes` | TEXT | 可空 | 备注 |
| `sort_order` | INTEGER | NOT NULL, 默认 0 | 时间轴排序 |

### 3.3 `experiences` — 工作 / 实习

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | INTEGER | PK | |
| `candidate_id` | INTEGER | FK, index | |
| `company` | TEXT(120) | NOT NULL | 公司 |
| `role` | TEXT(120) | NOT NULL | 职位 |
| `location` | TEXT(60) | 可空 | 城市 |
| `start_date` | DATE | NOT NULL | |
| `end_date` | DATE | 可空 | |
| `is_current` | BOOLEAN | NOT NULL | 是否在职 |
| `summary` | TEXT | 可空 | 职责概述 |
| `highlights` | JSON | 可空 | 量化成果条目列表 |
| `sort_order` | INTEGER | NOT NULL | |

### 3.4 `projects` — 项目

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | INTEGER | PK | |
| `candidate_id` | INTEGER | FK, index | |
| `name` | TEXT(120) | NOT NULL | 项目名 |
| `direction` | TEXT(40) | NOT NULL | 方向：后端 / 嵌入式 / 算法 / 客户端 / 工具链 / 其他 |
| `role` | TEXT(120) | 可空 | 我的角色 |
| `start_date` / `end_date` | DATE | 可空 | 起止 |
| `status` | TEXT(20) | NOT NULL | online / archived / wip |
| `repo_url` / `demo_url` | TEXT(300) | 可空 | 仓库 / 演示 |
| `summary` | TEXT | 可空 | 一句话说明 |
| `architecture` | TEXT | 可空 | 架构与模块划分 |
| `highlights` | JSON | 可空 | 亮点条目 |
| `challenges` | TEXT | 可空 | 难点 |
| `retrospective` | TEXT | 可空 | 复盘与改进 |
| `ci_status` | TEXT(40) | 可空 | 如 `passing` |
| `sort_order` | INTEGER | NOT NULL | |

### 3.5 `project_metrics` — 项目指标（自定义键值）

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | INTEGER | PK | |
| `project_id` | INTEGER | FK, index | |
| `key` | TEXT(60) | NOT NULL | 如 `QPS`、`覆盖率` |
| `value` | TEXT(60) | NOT NULL | 原始值 |
| `unit` | TEXT(20) | 可空 | 单位 |
| `note` | TEXT(200) | 可空 | 口径说明 |
| `sort_order` | INTEGER | NOT NULL | |

### 3.6 `tags` — 技术标签

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | INTEGER | PK | |
| `name` | TEXT(40) | UNIQUE, NOT NULL | 如 `Python`、`CI/CD` |
| `dimension` | TEXT(20) | NOT NULL, index | language / domain / practice / toolchain |
| `color` | TEXT(16) | 可空 | `#RRGGBB`（数据层允许，视图层仍用令牌） |
| `description` | TEXT(200) | 可空 | |
| `sort_order` | INTEGER | NOT NULL | |

`project_tags`：`project_id` + `tag_id` 复合主键，双向索引。

### 3.7 `skills` — 技术能力

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | INTEGER | PK | |
| `candidate_id` | INTEGER | FK, index | |
| `category` | TEXT(40) | NOT NULL | 语言 / 框架 / 数据库 / 工具链 / 运维 / 软技能 |
| `name` | TEXT(60) | NOT NULL | |
| `level` | INTEGER | NOT NULL | 1 了解 / 2 熟悉 / 3 熟练 / 4 精通 |
| `years` | REAL | 可空 | 使用年限 |
| `self_score` | INTEGER | 可空 | 0–100，自评；雷达图标注「自评」 |
| `notes` | TEXT | 可空 | |
| `sort_order` | INTEGER | NOT NULL | |

唯一约束：`(candidate_id, category, name)`。

### 3.8 `skill_evidence` — 技能证据链

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | INTEGER | PK | |
| `skill_id` | INTEGER | FK, index | |
| `project_id` | INTEGER | FK, 可空, index | 证据来源之一 |
| `experience_id` | INTEGER | FK, 可空 | 证据来源之二 |
| `statement` | TEXT | NOT NULL | 这条证据说明了什么 |
| `metric_note` | TEXT(200) | 可空 | 量化口径 |
| `sort_order` | INTEGER | NOT NULL | |

业务规则：`project_id` 与 `experience_id` 至少有一个；两者都为空视为无效证据，
由服务层拦截并进入简历健康度检查。

### 3.9 `certificates` — 证书与荣誉

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | INTEGER | PK | |
| `candidate_id` | INTEGER | FK | |
| `name` | TEXT(120) | NOT NULL | |
| `issuer` | TEXT(120) | 可空 | 颁发机构 |
| `issued_on` / `expires_on` | DATE | 可空 | |
| `credential_id` | TEXT(120) | 可空 | |
| `url` | TEXT(300) | 可空 | 验证链接 |
| `notes` | TEXT | 可空 | |
| `sort_order` | INTEGER | NOT NULL | |

### 3.10 `resume_versions` — 简历版本

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | INTEGER | PK | |
| `candidate_id` | INTEGER | FK | |
| `name` | TEXT(80) | NOT NULL | 如「后端版」 |
| `target_role` | TEXT(120) | 可空 | 目标岗位 |
| `target_jd` | TEXT | 可空 | 粘贴的 JD 原文，用于覆盖分析 |
| `template` / `theme` | TEXT(40) | NOT NULL | 导出模板与主题 |
| `is_default` | BOOLEAN | NOT NULL | 默认打开哪一版 |

### 3.11 `resume_items` — 版本条目编排

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | INTEGER | PK | |
| `version_id` | INTEGER | FK, index | |
| `item_type` | TEXT(20) | NOT NULL | education / experience / project / skill / certificate |
| `item_id` | INTEGER | NOT NULL | 指向对应表的 id（应用层校验） |
| `section` | TEXT(20) | NOT NULL | 导出时的分区 |
| `sort_order` | INTEGER | NOT NULL | |
| `override_text` | TEXT | 可空 | 面向该岗位的改写文案 |

多态引用不建数据库外键，删除实体时由服务层清理 `resume_items`。

### 3.12 `snapshots` — 版本快照

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | INTEGER | PK | |
| `version_id` | INTEGER | FK, index | |
| `label` | TEXT(80) | 可空 | 如「投递 A 公司前」 |
| `payload` | JSON | NOT NULL | 该版本完整渲染数据 |
| `created_at` | DATETIME | NOT NULL | 快照时间 |

### 3.13 `attachments` — 附件元数据

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | INTEGER | PK | |
| `owner_type` / `owner_id` | TEXT(20) / INTEGER | NOT NULL, index | 挂载对象 |
| `file_name` | TEXT(200) | NOT NULL | 原文件名 |
| `path` | TEXT(500) | NOT NULL | 磁盘相对路径 |
| `sha256` | TEXT(64) | NOT NULL | 去重与完整性 |
| `size_bytes` | INTEGER | NOT NULL | |
| `mime` | TEXT(80) | 可空 | |

文件本体只放磁盘，不入库。

### 3.14 `app_settings` — 键值配置（已存在）

`key` 主键 + `value`，当前仅存 UI 主题（`ui.theme`）。新增设置项一律落这张表，
不用 `QSettings`。

## 4. 索引清单

- `educations(candidate_id, sort_order)`
- `experiences(candidate_id, sort_order)`
- `projects(candidate_id, sort_order)`
- `project_metrics(project_id, sort_order)`
- `tags(dimension)`
- `project_tags(tag_id)`（主键已覆盖 project_id 前缀）
- `skills(candidate_id, category, sort_order)`
- `skill_evidence(skill_id)`、`skill_evidence(project_id)`
- `resume_items(version_id, sort_order)`
- `snapshots(version_id, created_at)`
- `attachments(owner_type, owner_id)`

## 5. 迁移策略

| 版本 | 内容 | 状态 |
|---|---|---|
| `0001` | `app_settings` | 已完成 |
| `0002` | 候选人 / 学历 / 经历 / 项目 / 标签 / 技能 / 简历 / 快照 / 附件 | 已完成（M1） |

规则：
1. 一次迁移只做一件事，必须提供 `downgrade`。
2. 删列、改名走「新建列 → 回填 → 删旧列」三步，禁止直接 `drop_column`。
3. 迁移在测试里必须跑通 `upgrade head` 与 `downgrade base`。
