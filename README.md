# ForgeCV · 工程师简历工坊

本地优先的工程师简历工具：把学历路径、工作经历、项目与技术能力放进一套结构化数据里，
再用「项目标签 + 技能证据链」证明能力，最后导出为 Word。

数据只存在本机 SQLite，不联网、不上传。

## 当前状态

| 里程碑 | 内容 | 状态 |
|---|---|---|
| M0 | 脚手架、文档骨架、质量门禁基线 | 已完成 |
| M1 | 核心数据模型与迁移、仓储、示例数据 | 已完成 |
| M2 | 个人信息、学历时间轴、工作经历、项目库 | 已完成 |
| M3 | 技能矩阵、证据链、能力雷达 | 已完成 |
| M4 | 简历版本编排、预览、健康度检查、JD 匹配 | 已完成 |
| M5 | Word 导出、版本快照与 Diff | 已完成 |
| M6 | 测试补齐、门禁验收、首个可用版本 | 已完成 |

## 快速开始

要求 Windows 10/11、Python 3.12、[uv](https://docs.astral.sh/uv/)。

```powershell
git clone https://github.com/SC-CATL/forgecv.git
cd forgecv
uv sync
uv run dev          # 建库 -> 迁移 -> 启动窗口
uv run pytest -q    # 测试
```

也可以双击根目录的 `run.bat`（使用已同步的 `.venv`，自动迁移后启动）。

网络慢时可先切镜像再执行：

```powershell
$env:UV_DEFAULT_INDEX = "https://pypi.tuna.tsinghua.edu.cn/simple"
```

## 功能范围

- **学历变迁路径**：时间轴展示院校、学历层次、专业、GPA、课程与论文。
- **工作 / 项目库**：经历条目化，项目带方向、角色、技术栈、指标与复盘。
- **项目技术标签**：语言 / 领域 / 工程实践 / 工具链四个维度，可筛选与统计。
- **技能矩阵与证据链**：每条技能必须能挂到具体项目或经历，避免空口「精通」。
- **工程能力雷达**：由技能与项目指标聚合，权重固定，口径见 `docs/engineering/scoring.md`。
- **简历版本**：同一套数据按岗位组合条目，带快照与差异对比。
- **简历健康度与 JD 覆盖**：时间冲突、无证据技能、无量化描述、岗位关键词缺口。
- **Word 导出**：`python-docx`，中文字体与时间轴排版规范见导出文档。

## 使用示例

1. `uv run dev` 启动，打开「个人信息」填姓名、求职意向与联系方式并保存；
2. 在「学历路径」添加学历，在「工作经历」录入带数字的成果条目；
3. 在「标签管理」建标签，再到「项目库」录项目、指标并勾选标签；
4. 在「技能矩阵」添加技能，挂到具体项目或经历作为证据；
5. 到「概览」看雷达与改进提示，再到「简历版本」勾选条目并预览；
6. 打开「导出 Word」选择输出目录，生成 `姓名-岗位-日期.docx`。

想先看效果，可以跑 `uv run python scripts/seed.py` 写入一份演示数据。

## 结构

```text
src/forgecv/
├─ app/          # 组合根：bootstrap / cli / container / window
├─ platform/     # 横向技术平台层：配置、数据库、UI Kit、观测
├─ features/     # 纵向业务切片：每个切片独立七件套
└─ resources/    # 设计令牌
```

依赖方向：`app/ -> features/ -> platform/`；`platform/` 不得反向依赖 `features/`；
切片之间只经 `api.py` 或事件总线。页面不写颜色与 `setStyleSheet`，样式只来自
`resources/tokens.toml`。

## 常用命令

| 命令 | 作用 |
|---|---|
| `uv run dev` | 建库、迁移、启动窗口 |
| `uv run doctor` | 环境自检 |
| `uv run app --self-test` | 自检并退出 |
| `uv run python scripts/dev.py` | 开发模式 + 源码变更自动重启 |
| `uv run python scripts/new_feature.py <name>` | 生成新切片七件套 |
| `uv run ruff check .` | 静态检查 |
| `uv run mypy src` | 严格类型检查 |
| `uv run lint-imports` | 分层契约检查 |
| `uv run pytest -q` | 测试 |

## 文档

从 [`docs/index.md`](docs/index.md) 进入：

- 工程文档：架构、数据字典、切片、导出规范、质量门禁、开发体验
- 用户文档：快速上手、功能地图
- 决策记录：`docs/decisions/`

## 贡献

- 开发约定与提交规范：见 [`CONTRIBUTING.md`](CONTRIBUTING.md)
- 行为准则：见 [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md)
- 安全问题请走私密渠道，不要开公开 issue：见 [`SECURITY.md`](SECURITY.md)

提交前请跑：`uv run ruff check .`、`uv run mypy src`、`uv run lint-imports`、`uv run pytest -q`。

## 许可证

MIT，见 [`LICENSE`](LICENSE)。
