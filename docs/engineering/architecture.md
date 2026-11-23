# 架构

## 1. 技术栈

| 项 | 选择 | 版本基线 |
|---|---|---|
| 语言 | Python | 3.12 |
| GUI | PySide6 | 6.12 |
| 数据库 | SQLite（WAL），可切 MySQL | SQLAlchemy 2.1 |
| 迁移 | Alembic | 1.20 |
| 日志 | structlog | 26.1 |
| 导出 | python-docx（M5 引入） | 待定 |
| 测试 | pytest + pytest-qt | 9.x / 4.5 |

本地数据库默认位置：`%LOCALAPPDATA%/ForgeCV/app.db`。测试环境使用内存库
（`ENVIRONMENT=test`）。

## 2. 分层

```text
forgecv/
├─ app/          # 组合根：唯一同时引用所有切片与平台的地方
├─ features/     # 纵向业务切片：一个功能一个目录，自带表与服务
└─ platform/     # 横向技术平台：配置、数据库、UI Kit、日志、自检
```

依赖方向固定：`app -> features -> platform`。`platform` 不得依赖 `features`；
切片之间只允许 `from ..other.api import ...` 或事件总线。

这条规则由 `import-linter` 契约强制，`tests/architecture/test_layers.py` 也会复查：
- 除 `platform/ui/qt.py` 外任何文件不得出现 `PySide6` / `PySide2`；
- `features/*/view.py` 不得出现 `setStyleSheet` 与 `#RRGGBB`；
- `Alembic` 迁移与 ORM 表必须成对出现。

## 3. 启动链

```text
main.py                                  # 薄启动器：自动切到项目 .venv 后转发
└─ forgecv.__main__:main                 # 解析 --self-test / --migrate / --dev / --mock
   ├─ --self-test -> platform.selfcheck   # 数据库、Qt 绑定、令牌自检
   └─ app.bootstrap.run                   # 安装异常钩子 -> QApplication -> Container
      └─ app.container.Container.create   # 配置、引擎、会话工厂、事件总线、UiManager
         └─ app.window.build_window        # 注册切片路由，落到首页
            └─ ui.theme.apply              # 应用主题后进入事件循环
```

约定：
- `app.exec()` 只出现在 `platform/ui/qt.py`，由 `app/bootstrap.py` 调用；
- `QMessageBox` 只在 `platform/ui/kit/dialogs.py`；
- `QThread` / `QRunnable` 只在 `platform/ui/kit/tasks.py`；
- UI 线程不做 IO，耗时任务走 `ui.tasks.submit(..., pool="io")`。

## 4. UI Runtime

`UiManager` 聚合六个可独立测试的子服务：

| 服务 | 文件 | 职责 |
|---|---|---|
| `theme` | `platform/ui/kit/theme.py` | 令牌加载、三种模式 + 跟随系统、QSS 生成 |
| `dialogs` | `platform/ui/kit/dialogs.py` | 统一弹窗与确认框 |
| `layout` | `platform/ui/kit/layout.py` | 主窗口骨架：左导航 + 页面栈 |
| `pages` | `platform/ui/kit/pages.py` | 延迟实例化页面、路由缓存 |
| `tasks` | `platform/ui/kit/tasks.py` | 线程池与信号回传 |
| `lifecycle` | `platform/ui/kit/lifecycle.py` | 退出清理、单实例锁、引擎释放 |

页面只与 `UiManager` 交互；业务页面不直接操作 `QApplication` 或样式表。

页面复用组件放在 `platform/ui/kit/forms.py`（标题、卡片、表单、日期、滚动区）与
`format.py`（日期区间文案）。只有出现在单个切片内部、无法复用的复杂区块才留在切片里，
例如 `features/project/fragments.py` 的指标表格与标签选择器。

## 5. 切片七件套

以 `features/settings/` 为模板：

| 文件 | 职责 |
|---|---|
| `models.py` | 该切片拥有的 ORM 表，继承 `Base, TimestampMixin` |
| `repository.py` | 只做持久化，每个操作一个短事务 |
| `service.py` | 领域规则、校验，返回 `Result[T, E]`，不碰 Qt |
| `viewmodel.py` | `QObject` + 信号，把服务结果翻译成界面状态 |
| `view.py` | 只拼控件、绑信号，样式全部来自令牌 |
| `api.py` | 切片唯一对外入口：路由常量、服务构造、`register(host)` |
| `__init__.py` | 包标记 |

新增切片：`uv run python scripts/new_feature.py <name>`，然后在 `app/window.py` 注册。

## 6. 数据流

```text
view (Qt 信号)
  -> viewmodel (收集输入、状态)
     -> service (校验、业务规则，Result)
        -> repository (短事务)
           -> SQLAlchemy / SQLite
```

返回值约定：可预期失败返回 `Result.err`，异常只用于意外情况。UI 只根据
`Result` 渲染错误提示，不解析异常文本。

## 7. 持久化原则

- 每种持久化数据都有对应表；`QSettings` / JSON / 注册表只存引导信息。
- 文件本体不入库：附件放磁盘，`attachments` 表登记路径、sha256、大小、时间。
- 表结构变更必须手写 Alembic 迁移，且 `upgrade head` 与 `downgrade base` 都可执行。
- SQLite 开启外键；写操作串行化，避免 `database is locked`。

## 8. 扩展检查清单

新增一个功能切片时逐项确认：

- [ ] 表与迁移成对提交，回滚可用
- [ ] `api.py` 暴露最小契约，没有直接跨切片 import 内部模块
- [ ] 视图不含颜色与 `setStyleSheet`
- [ ] 服务层有测试，页面有离屏 UI 测试
- [ ] `ruff` / `mypy` / `lint-imports` / `pytest` 全绿
- [ ] 文档：`slices.md`、`data-model.md`、CHANGELOG 同步更新
