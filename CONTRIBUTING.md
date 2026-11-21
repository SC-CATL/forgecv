# 贡献指南

## 开发环境

```powershell
uv sync
uv run dev            # 建库 -> 迁移 -> 启动
uv run pytest -q      # 全量测试（离屏 Qt）
```

网络慢时：

```powershell
$env:UV_DEFAULT_INDEX = "https://pypi.tuna.tsinghua.edu.cn/simple"
uv sync
```

## 改动约定

1. 先在 `features/<name>/` 内完成端到端切片，再考虑是否上移到 `platform/`。
2. 切片之间只经 `api.py` 或事件总线通信。
3. 页面不写颜色与 `setStyleSheet`，样式只加在 `resources/tokens.toml` 与 `platform/ui/kit/qss.py`。
4. 新增表必须同时提交 Alembic 迁移与回滚验证。
5. 提交前跑：`uv run ruff check . && uv run mypy src && uv run lint-imports && uv run pytest -q`。
6. 函数不超过 30 行，文件不超过 300 行，类不超过 200 行；参数超过 3 个用 keyword-only。
7. 可预期失败返回 `Result`，不用异常表达业务错误。

## 新切片

```powershell
uv run python scripts/new_feature.py invoices
```

生成七件套与一个服务测试，然后在 `app/window.py` 注册路由。

## 文档纪律

文档与代码同 PR 更新，不攒到最后补：

1. **数据字典同步**：模型或迁移变了，`docs/engineering/data-model.md` 必须同 PR 修改。
2. **状态透明**：功能只标「已完成 / 开发中 / 计划」，README、功能地图、文档首页口径一致。
3. **里程碑收尾**：CHANGELOG 条目 + 受影响文档 + 门禁结果三项齐全才算完成。
4. **决策留痕**：影响架构、依赖、数据格式或导出契约的选择，写 `docs/decisions/` 的 ADR。
5. **中文正文**：命令、表名、字段名、代码标识符保持英文。
6. **可验证**：只写字段、路径、命令与限制，不写宣传语。

## 提交信息

采用 Conventional Commits：`feat:`、`fix:`、`docs:`、`refactor:`、`test:`、`chore:`。
一个提交只做一件事；迁移与模型放同一个提交。
