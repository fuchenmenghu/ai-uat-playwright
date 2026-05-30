# AI-UAT 双系统自动化测试助手

这是一个面向供应链系统与 WMS 系统 UAT 页面的 Python + Playwright 自动化测试 MVP。第一阶段目标是最小可运行闭环：按脚本编号执行固定 Playwright 脚本，记录步骤日志，并生成 Excel 测试报告。

## 安装依赖

```bash
cd ai-uat-playwright
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

## 运行样例脚本

```bash
python run_scenario.py --script SC_PUR_IN_001 --source-order CD26052621001 --env UAT
```

如需看到浏览器窗口：

```bash
python run_scenario.py --script SC_PUR_IN_001 --source-order CD26052621001 --env UAT --headed
```

## 接管已登录的 Chrome

如果目标系统登录存在安全验证，可以先用远程调试端口启动 Chrome，手动登录系统后，再让脚本接管当前浏览器。

启动 Chrome：

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/ai-uat-chrome-profile
```

在这个 Chrome 窗口里打开并登录 CIBO。登录完成后运行：

```bash
python run_scenario.py \
  --script zhujiang_Purchase_01 \
  --source-order 你的来源单号 \
  --env UAT \
  --cdp-url http://127.0.0.1:9222
```

注意：普通方式已经打开的 Chrome 无法被 Playwright 稳定接管，需要使用上面的 `--remote-debugging-port` 启动方式。

样例脚本默认不访问真实业务页面，只验证框架闭环：

1. 校验源头单号已传入；
2. 校验供应链系统与 WMS 系统配置存在；
3. 写入一个样例变量，模拟页面字段提取。

## 报告位置

每次执行会生成一个 Excel 报告：

```text
reports/{run_id}_{script_id}_Test_Report.xlsx
```

报告只包含两个 Sheet：

- `summary_report`
- `operation_log`

失败步骤的截图会保存在：

```text
runs/{run_id}/evidence/
```

## 配置文件

系统配置位于：

```text
config/systems.yaml
```

不要把 URL、租户、账号、密码写进测试脚本。新增系统时，优先扩展该 YAML 文件。

## 如何补充真实页面元素

先按 `docs/natural_language_case_template.md` 补齐自然语言测试用例，尤其是：

- 菜单路径
- 输入框 label
- 按钮文本
- 表格名称
- 表格列名
- 行匹配规则
- 等待、重新查询或轮询规则

通过“行匹配规则”定位到目标行后，如果需要核对行内某列的值，在“预期结果”中自然语言说明字段名、期望值来源和比较方式；如果需要提取变量，在步骤中填写“需要提取的页面字段”和“变量名”。若这两个字段任一为空，则忽略变量提取处理。

然后在具体脚本的 Step 函数中使用：

- `framework.playwright_helpers`
- `framework.assertions`
- `framework.evidence`
- `framework.step`

脚本不得自行猜测按钮名称、字段名称或表格列名。缺少定位信息时，应先让用例补充。

## 如何新增脚本编号

1. 新建脚本文件，例如：

```text
scripts/SC_PUR_IN_002.py
```

2. 将原始测试用例 Excel 保存为：

```text
test_cases/SC_PUR_IN_002.xlsx
```

新增或覆盖更新用例时，必须同步保存用户上传的原始 Excel。详见 `docs/case_management_protocol.md`。

3. 在脚本中声明：

```python
SCRIPT_ID = "SC_PUR_IN_002"
SCRIPT_NAME = "采购入库-真实业务场景"
INVOLVED_SYSTEMS = ["供应链系统", "WMS系统"]
```

4. 每个 Step 写成独立函数，并保留中文注释：

- 步骤编号
- 系统
- 模块
- 操作描述
- 预期结果

5. 在 `scripts/script_registry.py` 注册：

```python
SCRIPT_REGISTRY = {
    "SC_PUR_IN_002": {
        "module": "scripts.SC_PUR_IN_002",
        "script_name": "采购入库-真实业务场景",
    }
}
```

6. 执行：

```bash
python run_scenario.py --script SC_PUR_IN_002 --source-order 真实源头单号 --env UAT
```

## 第一阶段边界

- 不接数据库
- 不做接口校验
- 不做 Web 管理后台
- 不生成 `issue_list`
- 不使用大模型生成每一步问题描述
- 大模型建议字段第一阶段留空
