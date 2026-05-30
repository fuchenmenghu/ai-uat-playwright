# 执行测试任务交互协议

本文档定义后续在 Codex 对话中触发 UAT 自动化测试任务的固定交互方式。

## 触发格式

用户按以下格式发送：

```text
小虎，执行任务
脚本编号：zhujiang_Purchase_01
上游订单号：XXXXXXXX
```

## 默认规则

- 未提供环境时，默认使用 `UAT`。
- `上游订单号` 会映射为运行参数 `source_order_no`。
- `脚本编号` 必须已在 `scripts/script_registry.py` 中注册。
- 执行前根据脚本的 `INVOLVED_SYSTEMS` 判断需要登录的系统；该字段来自用例模板 `scenario_info.涉及系统`。
- 登录动作由用户手动完成，自动化脚本只负责登录后的页面操作、断言、截图和报告生成。

## 执行流程

1. Codex 校验脚本编号是否存在。
2. Codex 校验上游订单号是否为空。
3. Codex 使用 `--remote-debugging-port` 启动 Chrome。
4. Codex 读取脚本涉及系统，自动打开对应系统地址；如果涉及 `cibo,wms`，则打开 CIBO 和 WMS 两个页签。
5. Codex 提示用户：

```text
浏览器已启动，请在打开的 Chrome 中完成相关系统登录。
若系统登录完成，请回复：已登录
```

6. 用户在 Chrome 中完成登录后回复：

```text
已登录
```

7. Codex 使用 CDP 接管已登录 Chrome，并执行测试脚本。
8. Codex 输出执行结论、报告路径、首个失败步骤、失败编码、原始失败信息和截图路径。

## 执行命令映射

用户输入：

```text
小虎，执行任务
脚本编号：zhujiang_Purchase_01
上游订单号：ABC123
```

等价于登录完成后执行：

```bash
python run_scenario.py \
  --script zhujiang_Purchase_01 \
  --source-order ABC123 \
  --env UAT \
  --cdp-url http://127.0.0.1:9222
```

## 注意事项

- 普通方式已经打开的 Chrome 不能稳定被 Playwright 接管。
- Chrome 必须通过 `--remote-debugging-port` 启动。
- 建议使用独立 Chrome 用户目录，避免影响日常浏览器配置。
- 在用户回复 `已登录` 前，不执行测试脚本。
- 测试过程中如果步骤切换到 WMS，脚本应复用已打开的 WMS 页签；切回 CIBO 时同理。
