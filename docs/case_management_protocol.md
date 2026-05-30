# 测试用例脚本增删改查交互协议

本文档定义“小虎”在 Codex 对话中处理测试用例脚本新增、删除、覆盖更新和查询时的固定交互方式。

## 固定存储位置

- 原始测试用例 Excel 固定存储在 `test_cases/` 目录。
- 文件命名固定为 `test_cases/{脚本编号}.xlsx`。
- 自动化脚本固定存储在 `scripts/{脚本编号}.py`。
- 脚本目录注册表固定维护在 `scripts/script_registry.py`。

## 新增用例

触发语：

```text
小虎，新增这个用例
```

并上传测试用例 Excel。

处理规则：

1. 根据上传的 Excel 编写自动化测试脚本。
2. 将上传的 Excel 保存到 `test_cases/{脚本编号}.xlsx`。
3. 将脚本保存到 `scripts/{脚本编号}.py`。
4. 在 `scripts/script_registry.py` 注册脚本编号和业务场景。
5. 完成后回复：

```text
脚本编号xxx，自动化测试脚本代码已写好
```

## 删除用例

触发语：

```text
小虎，请删除这个用例，脚本编号：xxx
```

处理规则：

1. 删除 `scripts/{脚本编号}.py`。
2. 删除 `test_cases/{脚本编号}.xlsx`，如果该文件存在。
3. 从 `scripts/script_registry.py` 移除该脚本编号。
4. 完成后回复：

```text
脚本编号xxx，删除成功
```

## 覆盖更新用例

触发语：

```text
小虎，请更新这个用例，脚本编号：xxx
```

并上传最新测试用例 Excel。

处理规则：

1. 删除原 `scripts/{脚本编号}.py`。
2. 使用上传的最新 Excel 覆盖保存到 `test_cases/{脚本编号}.xlsx`。
3. 根据最新 Excel 重新生成 `scripts/{脚本编号}.py`。
4. 更新 `scripts/script_registry.py` 中的业务场景信息。
5. 完成后回复：

```text
脚本编号xxx，已完成更新
```

## 查询用例

触发语：

```text
小虎，请提供最新的用例目录
```

处理规则：

1. 读取 `scripts/script_registry.py` 获取最新全量脚本编号和业务场景。
2. 展示脚本编号、业务场景、原始 Excel 和脚本文件。
3. 原始 Excel 链接指向 `test_cases/{脚本编号}.xlsx`；如果文件不存在，明确标记“未存储”。

展示格式：

| 脚本编号 | 业务场景 | 原始 Excel | 脚本文件 |
|---|---|---|---|
