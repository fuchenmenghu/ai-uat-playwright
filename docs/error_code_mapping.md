# 失败编码与失败信息映射

失败信息由 `framework/error_catalog.py` 统一维护，并通过 `make_failure(code, **kwargs)` 生成。

## ENV：环境与依赖类

| 编码 | 默认说明 |
|---|---|
| ENV_001 | 配置文件缺失 |
| ENV_002 | 配置项缺失 |
| ENV_003 | 依赖包缺失 |
| ENV_004 | 浏览器启动失败 |
| ENV_006 | 测试脚本不存在 |

## AUTH：登录与权限类

| 编码 | 默认说明 |
|---|---|
| AUTH_001 | 未进入登录后页面 |
| AUTH_004 | 登录态失效 |
| AUTH_005 | 权限不足 |

## NAV：页面导航类

| 编码 | 默认说明 |
|---|---|
| NAV_001 | 页面打开失败 |
| NAV_002 | 菜单路径不存在 |
| NAV_003 | 页面加载超时 |
| NAV_004 | 目标页面不匹配 |

## ELEMENT：页面元素定位类

| 编码 | 默认说明 |
|---|---|
| ELEMENT_001 | 输入框未找到 |
| ELEMENT_002 | 按钮未找到 |
| ELEMENT_003 | 表格未找到 |
| ELEMENT_004 | 表格列未找到 |
| ELEMENT_006 | 元素不可点击 |
| ELEMENT_009 | 元素定位不唯一 |

## DATA：数据与变量类

| 编码 | 默认说明 |
|---|---|
| DATA_001 | 输入参数缺失 |
| DATA_002 | 前序变量缺失 |
| DATA_003 | 变量提取失败 |
| DATA_005 | 提取到多个候选值 |

## ACTION：页面操作类

| 编码 | 默认说明 |
|---|---|
| ACTION_001 | 点击失败 |
| ACTION_002 | 输入失败 |
| ACTION_003 | 查询失败 |
| ACTION_004 | 保存或提交失败 |
| ACTION_009 | 操作成功提示缺失 |

## ASSERT：页面断言类

| 编码 | 默认说明 |
|---|---|
| ASSERT_001 | 查询无结果 |
| ASSERT_002 | 字段值不一致 |
| ASSERT_003 | 状态不符合预期 |
| ASSERT_004 | 数量不一致 |
| ASSERT_005 | 成功提示未出现 |
| ASSERT_006 | 异常提示出现 |
| ASSERT_013 | 轮询超时 |

## SYSTEM：系统异常类

| 编码 | 默认说明 |
|---|---|
| SYSTEM_001 | 前端系统异常 |
| SYSTEM_002 | 接口请求失败 |
| SYSTEM_003 | 页面空白 |
| SYSTEM_004 | 页面长时间无响应 |
| SYSTEM_006 | 未知系统异常 |

## REPORT：报告生成类

| 编码 | 默认说明 |
|---|---|
| REPORT_001 | 报告模板缺失 |
| REPORT_002 | 报告写入失败 |
| REPORT_003 | 操作日志写入失败 |
| REPORT_005 | 汇总统计失败 |

## 示例

```python
from framework.error_catalog import make_failure

failure = make_failure(
    code="ASSERT_001",
    condition_name="NCC单号",
    condition_value="G01500120260527367",
)
print(failure["message"])
```

输出：

```text
[ASSERT_001] 查询无结果：使用查询条件 NCC单号=G01500120260527367 未查询到记录。
```
