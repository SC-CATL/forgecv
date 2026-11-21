# 质量门禁与验收

## 1. 指标

| 指标 | 门槛 | 当前 |
|---|---|---|
| 核心覆盖率 | ≥ 85% | 90.94% |
| 整体覆盖率 | ≥ 75% | 90.94% |
| 冷启动时间 | ≤ 2.5s（P95） | 0.35s（离屏，建窗口 + 12 页） |
| idle 内存 | ≤ 250MB | 未测基线 |
| 崩溃率 | ≤ 0.5% | 未收集 |
| 数据丢失 | 0 | 0 |
| 重复代码率 | ≤ 3% | 未测 |
| 劣化回归 | 超基线 5% 失败 | 未建基线 |

M1 的覆盖率数字来自 113 项测试（脚手架 66 项 + 业务 47 项）；M5 后为 153 项。
加入页面后按功能同步补齐，不允许下滑。覆盖率口径为本仓库整体 `src`。

## 2. 必过命令

```powershell
uv run ruff check .
uv run mypy src
uv run lint-imports
uv run pytest -q --cov=src
uv run app --self-test
```

离屏环境需要：

```powershell
$env:ENVIRONMENT = "test"
$env:QT_QPA_PLATFORM = "offscreen"
```

未安装 `uv` 时可用 `.venv\Scripts\python.exe -m <module>` 等价执行。

## 3. 分层契约（自动校验）

| 契约 | 工具 | 检查内容 |
|---|---|---|
| `app -> features -> platform` | import-linter | 依赖方向 |
| `platform` 不得依赖 `features` | import-linter | 反向依赖 |
| Qt 绑定只在 `platform/ui/qt.py` | pytest 架构测试 | 其他文件出现 `PySide6` 即失败 |
| 视图不写样式 | pytest 架构测试 | `setStyleSheet` / `#RRGGBB` |
| 表与迁移成对 | 人工 + 迁移测试 | `upgrade head` / `downgrade base` |

## 4. 验收清单

### M0（已完成）

- [x] `main.py --self-test` 退出码 0，输出 `{"ok": true}`
- [x] pytest 全绿（66 项）
- [x] 覆盖率 94.59%
- [x] ruff / mypy / import-linter 零错误
- [x] 文档骨架与 ADR 首批落地
- [x] SQLite 默认路径、内存测试库可用

### M1（已完成）

- [x] 15 张表、`0002_core_schema` 迁移，`upgrade head` / `downgrade base` 通过
- [x] 8 个业务切片的数据层：models / schemas / repository / service / api
- [x] 公共校验下沉到 `platform/core/validation.py`
- [x] `scripts/seed.py` 可写入演示数据，重复执行自动跳过
- [x] pytest 113 项通过，覆盖率 93.34%
- [x] ruff / mypy / import-linter 零错误
- [x] `data-model.md`、`slices.md`、CHANGELOG 同步

### M2（已完成）

- [x] 个人信息、学历路径、工作经历、项目库、标签管理五个页面可用
- [x] 学历与经历支持排序 / 在读（在职）状态
- [x] 项目支持自定义指标与四维标签联动保存
- [x] 公共 UI 组件下沉到 `platform/ui/kit/forms.py`，复杂区块用切片内 `fragments.py`
- [x] 124 项测试通过，覆盖率 92.46%
- [x] ruff / mypy / import-linter 零错误
- [x] 离屏启动并逐个导航全部路由通过

### M3（已完成）

- [x] 技能矩阵页：分类、熟练度、年限、自评分与证据链维护
- [x] 统一时间轴：三类事件排序、同分区重叠提示
- [x] 概览页：统计卡片、八维雷达、标签分布、改进提示
- [x] 雷达口径写入 `docs/engineering/scoring.md`，标注自评
- [x] 134 项测试通过，覆盖率 91.90%
- [x] ruff / mypy / import-linter 零错误
- [x] 离屏导航全部 9 个路由通过

### M4（已完成）

- [x] 简历版本：新建、删除、默认版本、目标岗位与模板设置
- [x] 条目编排：跨切片勾选、已选排序（上移 / 下移）
- [x] 实时预览：与 Word 导出共用 `ResumeDocument` 渲染数据
- [x] 健康度检查：姓名、空分区、量化、证据、标签与指标缺口
- [x] JD 覆盖：本地词表匹配，展示覆盖率、已匹配与缺口
- [x] 143 项测试通过，覆盖率 91.18%
- [x] ruff / mypy / import-linter 零错误
- [x] 离屏导航全部 10 个路由通过

### M5（已完成）

- [x] Word 导出：A4 版式、中文 eastAsia 字体、分区标题、项目标签 / 指标
- [x] 文件名规则 `姓名-岗位-时间戳.docx`，同名追加序号，不覆盖
- [x] 页脚 PAGE / NUMPAGES 域
- [x] 导出前预检：缺姓名阻断，其余提示
- [x] 版本快照：保存渲染文本、列表、两份快照 Diff
- [x] 153 项测试通过，覆盖率 90.94%
- [x] 真实数据导出 docx 并用 `python-docx` 重新读取验证
- [x] ruff / mypy / import-linter 零错误

### M6（已完成）

- [x] 153 项测试通过，覆盖率 90.94%
- [x] ruff / mypy strict / import-linter 零错误
- [x] `main.py --self-test` 退出码 0
- [x] 离屏冷启动 0.246s，建完 12 页共 0.352s
- [x] 真实演示数据导出 docx，`python-docx` 回读验证
- [x] 12 个路由离屏逐个导航通过
- [x] README、文档首页、功能地图、CHANGELOG 状态一致
- [x] 新增 `run.bat` 一键启动（自动迁移）
- [x] 示例产物 `docs/assets/samples/forgecv-sample.docx`

### 每个新改动

- [ ] 新增表有迁移，upgrade / downgrade 均通过
- [ ] 新增服务有单测，页面有离屏 UI 测试
- [ ] 覆盖率不低于上一里程碑
- [ ] 无 UI 线程 IO，无 `platform -> features` 导入
- [ ] CHANGELOG、`data-model.md`、`slices.md` 同步
- [ ] 已知偏差与豁免写入本文件第 6 节

## 5. 发布（0.1.0）

1. [x] 全部门禁命令通过，覆盖率 90.94%，离屏冷启动 0.35s。
2. [x] 主流程以自动化替代：建库、12 页导航、真实数据导出 docx 并回读。
3. [ ] 人工备份 / 恢复演练待在有图形会话的机器上补做。
4. [x] CHANGELOG 使用 `0.1.0` 与发布日期。
5. [x] 不打包 exe；需要分发时再开 `include_packaging`。
6. [ ] 人工视觉验收（字重、间距、深浅主题）待补做。

## 6. 已知偏差与豁免

| 项 | 说明 | 补救 |
|---|---|---|
| 依赖版本高于模板验证基线 | 实际安装 PySide6 6.12 / SQLAlchemy 2.1 / mypy 2.4 / ruff 0.17 | 每次升级后重跑全部门禁；出现不兼容时锁定到模板基线 |
| 冷启动与内存门槛 | 冷启动已测（0.35s）；idle 内存尚未采样 | 发布后补一次进程内存采样 |
| 重复代码率 | 未接入工具测量 | 后续加 jscpd 或类似检查 |
| 未配置 CI 远端 | 仓库本地初始化，GitHub Actions 未跑 | 推送到 GitHub 后跑一次 `ci.yml` |
| 未打包 | 用户明确暂不需要 exe | 需要分发时再开 `include_packaging` |
| 文档站未启用 | 选择纯 Markdown | 需要时再生成 mkdocs |
