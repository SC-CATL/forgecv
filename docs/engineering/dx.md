# 开发体验（DX）

## 1. 环境准备

| 项 | 要求 |
|---|---|
| 系统 | Windows 10/11 x64 |
| Python | 3.12（`.python-version` 锁定） |
| 包管理 | uv ≥ 0.13 |
| 显示 | 桌面会话；测试用 offscreen |

安装 uv（任选其一）：

```powershell
winget install astral-sh.uv
# 或
python -m pip install --user uv
```

若 `uv` 不在 PATH，可把 `%APPDATA%\Python\Python312\Scripts` 加入用户 PATH。

## 2. 国内网络加速

脚手架与依赖下载慢时，给 uv 指定镜像（只影响当前终端，不写进仓库）：

```powershell
$env:UV_DEFAULT_INDEX = "https://pypi.tuna.tsinghua.edu.cn/simple"
$env:UV_INDEX_URL = "https://pypi.tuna.tsinghua.edu.cn/simple"
uv sync
```

pip 同理：

```powershell
python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple <包名>
```

不建议把镜像地址提交到 `pyproject.toml`，避免污染开源仓库与 CI。

## 3. 日常命令

| 目的 | 命令 |
|---|---|
| 同步依赖 | `uv sync` |
| 建库 + 迁移 + 启动 | `uv run dev` |
| 源码变更自动重启 | `uv run python scripts/dev.py` |
| 只跑迁移 | `uv run app --migrate` |
| 自检 | `uv run app --self-test` |
| 环境体检 | `uv run doctor` |
| 写入演示数据 | `uv run python scripts/seed.py` |
| 新增切片 | `uv run python scripts/new_feature.py <name>` |
| 测试 | `uv run pytest -q` |
| 覆盖率 | `uv run pytest -q --cov=src --cov-report=term` |
| 静态检查 | `uv run ruff check .` |
| 类型检查 | `uv run mypy src` |
| 分层契约 | `uv run lint-imports` |

未安装 uv 时，脚本可改用虚拟环境解释器：

```powershell
.\.venv\Scripts\python.exe main.py --self-test
.\.venv\Scripts\python.exe -m pytest -q
```

## 3.1 VS Code

仓库自带 `.vscode/settings.json` 与 `.vscode/launch.json`：

- 默认解释器固定为 `${workspaceFolder}/.venv/Scripts/python.exe`；
- 运行 / 调试选 **ForgeCV (venv)**，不要用系统 Python；
- 选 **ForgeCV 自检 (venv)** 可离屏跑 `--self-test`；
- 已推荐 Python / debugpy / Ruff / mypy 扩展。

修改配置后执行一次 `Developer: Reload Window` 生效。

## 4. 数据库

| 环境 | 位置 |
|---|---|
| 默认 | `%LOCALAPPDATA%\ForgeCV\app.db` |
| 测试（`ENVIRONMENT=test`） | 内存 SQLite |
| 自定义 | `$env:DATABASE_URL = "sqlite+pysqlite:///D:/data/forgecv.db"` |

- 重置开发库：关闭程序后删除 `app.db`，再 `uv run app --migrate`。
- 备份：直接复制 `app.db`；WAL 模式下同时复制 `app.db-wal` 与 `app.db-shm`，或先退出程序。
- 迁移回滚：`uv run alembic downgrade base`（需先设置相同的 `DATABASE_URL`）。

## 5. 新增功能切片

```powershell
uv run python scripts/new_feature.py invoices
```

生成后：

1. `models.py` 加表 → 手写 Alembic 迁移 → 验证 `upgrade head` / `downgrade base`。
2. 在 `service.py` 写业务规则，用 `Result` 表达预期失败。
3. 在 `app/window.py` 调 `register(host)` 注册路由。
4. 补单测与离屏 UI 测试，跑全部门禁。

## 6. 排错

| 现象 | 原因 | 处理 |
|---|---|---|
| `uv: 无法识别` | 未安装或不在 PATH | 装 uv 或把 Scripts 目录加入 PATH |
| `ModuleNotFoundError: forgecv` | 未同步依赖 | `uv sync`；必要时 `uv run python -m forgecv` |
| `ModuleNotFoundError: structlog` / `PySide6` | 启动器未成功切换解释器 | `main.py` 会自动切到 `.venv`；失败时用 `.venv\Scripts\python.exe main.py` 或 `run.bat` |
| 下载卡住 | 默认 PyPI 慢 | 按第 2 节切镜像 |
| 启动报 `could not find or load the Qt platform plugin "windows"` | 环境变量干扰或缺少 VC 运行库 | 清掉 `QT_PLUGIN_PATH`，安装 VC++ 2015-2022 运行库 |
| 测试报无 `QApplication` | 未用离屏 | `$env:QT_QPA_PLATFORM="offscreen"` |
| `database is locked` | 并发写 | 写操作串行，确认 WAL 与 `busy_timeout` 生效 |
| git 提交报 `Author identity unknown` | 未配置身份 | `git config user.name/user.email`（本仓库或全局） |
| 主题不生效 | 页面写了内联样式 | 只改 `resources/tokens.toml` |
| 改了模型但库没变 | 没写迁移 | 新增 Alembic 迁移并执行 `upgrade head` |
