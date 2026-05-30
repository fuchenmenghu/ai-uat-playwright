# 断言 / 等待规则说明

本文档用于填写自然语言测试用例 Excel 时选择“判断方式”，并说明每种方式的适用场景、判断逻辑和失败编码建议。

## 选择总原则

- 页面结果立即可见时，选择“立即断言”。
- 点击后有 loading、弹窗、toast 或短暂前端渲染延迟时，选择“等待后判断”。
- 列表页不会自动刷新，需要再次点击“查询”才更新结果时，选择“重新查询判断”。
- 跨系统下发、状态回写、后台异步处理有不固定延迟时，选择“轮询判断”。
- 需要把页面字段保存给后续步骤使用时，配合“变量提取断言”。

## 判断方式可选项

| 判断方式 | 适用场景 | 判断逻辑 | 常用失败编码 |
|---|---|---|---|
| 立即断言 | 页面打开后元素已存在；查询后结果立即返回；字段值即时可见 | 执行操作后立即检查目标元素、文本、表格记录、字段值或成功提示 | `ASSERT_001`、`ASSERT_002`、`ASSERT_003`、`ASSERT_005`、`ELEMENT_001` |
| 等待后判断 | 点击后需要等待 loading 消失、toast 出现、弹窗渲染或页面短暂刷新 | 先等待固定秒数或等待 loading 结束，再执行断言 | `NAV_003`、`ASSERT_005`、`ACTION_009` |
| 重新查询判断 | 页面数据不会自动刷新；状态或记录需要再次点击查询才更新 | 执行一次查询；失败时按用例说明重新点击查询；再次断言记录或字段 | `ASSERT_001`、`ASSERT_002`、`ACTION_003` |
| 轮询判断 | 跨系统单据生成、WMS 下发、状态回写等异步场景 | 按最大查询次数循环执行查询动作，每次间隔固定秒数；任一次满足条件即通过；全部失败则不通过 | `ASSERT_013`、`ASSERT_001`、`ASSERT_003` |
| 变量提取断言 | 需要提取单据号、状态、数量等字段给后续步骤使用 | 定位唯一记录或字段；读取目标字段；非空且唯一则写入变量；为空或多候选则失败 | `DATA_002`、`DATA_003`、`DATA_005` |

## 立即断言

适用：

- 页面中应出现指定文本；
- 指定输入框、按钮、字段或表格可见；
- 查询结果中应存在目标记录；
- 某字段值应等于预期值；
- 成功提示应出现。

填写建议：

```text
判断方式：立即断言
最大查询次数：1
每次间隔秒数：0
通过条件：采购单列表存在 NCC单号 = {source_order_no} 的记录
失败条件：未查询到目标记录
```

框架 helper 建议：

- `assert_page_contains_text(page, expected_text)`
- `assert_element_visible(page, locator_desc)`
- `assert_table_has_record(page, table_desc, row_match_rule)`
- `assert_field_equals(page, field_name, expected_value)`
- `assert_success_toast(page, success_text)`

## 等待后判断

适用：

- 点击按钮后有 loading；
- 成功提示不是立即出现；
- 弹窗、页面内容或状态有短暂刷新延迟。

填写建议：

```text
判断方式：等待后判断
最大查询次数：1
每次间隔秒数：3
通过条件：页面 loading 消失后出现“保存成功”
失败条件：等待后仍未出现成功提示
```

框架 helper 建议：

- `wait_then_assert_text(page, expected_text, wait_seconds)`
- `wait_for_loading_finished(page, timeout_seconds)`
- `wait_for_element_visible(page, locator_desc, timeout_seconds)`

## 重新查询判断

适用：

- 列表页需要重新点击“查询”才会刷新；
- 第一次查询没有结果，但业务允许立即再查一次；
- 状态刷新依赖再次查询。

填写建议：

```text
判断方式：重新查询判断
最大查询次数：2
每次间隔秒数：0
通过条件：重新点击查询后，列表存在源头单号 = {source_order_no} 的记录
失败条件：重新查询后仍无记录
```

框架 helper 建议：

- `requery_and_assert_record(page, query_action, table_desc, row_match_rule)`
- `requery_and_assert_field(page, query_action, field_name, expected_value)`

## 轮询判断

适用：

- CIBO 下发 WMS 有延迟；
- WMS 单据生成有延迟；
- 单据状态回写有延迟；
- 后台异步处理时间不固定。

默认建议：

- 最大查询次数：3
- 每次间隔秒数：10
- 任一次满足条件即通过
- 达到最大次数仍不满足则不通过

填写建议：

```text
判断方式：轮询判断
最大查询次数：3
每次间隔秒数：10
通过条件：WMS采购单列表存在 NCC单号 = {source_order_no} 的记录
失败条件：轮询 3 次后仍未查询到目标记录
```

框架 helper 建议：

- `poll_until_record_exists(page, query_action, table_desc, row_match_rule, retries, interval_seconds)`
- `poll_until_field_equals(page, query_action, field_name, expected_value, retries, interval_seconds)`
- `poll_until_status(page, query_action, status_field, expected_status, retries, interval_seconds)`

## 变量提取断言

适用：

- 从列表中提取采购单号、入库预约单号、WMS 单号等；
- 后续步骤依赖前序步骤提取的变量；
- 页面可能出现多个候选值，需要唯一确认。

填写建议：

```text
需要提取的页面字段：采购单号
变量名：wms_purchase_order_no
```

如果“需要提取的页面字段”或“变量名”任一为空，表示本步骤不需要提取变量，应忽略变量提取处理。

通过条件：

- 能定位到唯一目标记录；
- 目标字段非空；
- 变量成功保存到运行上下文。

失败条件：

- 字段为空；
- 查到多个候选值且无法唯一确认；
- 后续步骤依赖变量但变量不存在。

框架 helper 建议：

- `extract_table_field(page, table_desc, row_match_rule, field_name, variable_name)`
- `extract_page_field(page, field_name, variable_name)`
- `assert_variable_exists(ctx, variable_name)`

## 填写注意事项

- `预期结果` 用来描述本步骤应该达到的业务结果，并写入测试报告。
- 表格类断言必须在“行匹配规则”中写清楚用于匹配目标行的字段名和值。
- 通过“行匹配规则”定位到目标行后，如果需要核对行内某列的值，在“预期结果”中写清楚字段名、期望值来源和比较方式。
- 跨系统场景优先选择“轮询判断”，不要用固定长等待替代轮询。
- 如果页面定位信息不完整，应先补充用例，不应让脚本猜测元素。
