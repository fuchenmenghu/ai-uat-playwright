from __future__ import annotations

import argparse
import sys

from framework.error_catalog import make_failure
from framework.runner import run_scenario
from framework.step import RESULT_FAIL


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI-UAT 双系统自动化测试助手")
    parser.add_argument("--script", required=True, help="脚本编号，例如 SC_PUR_IN_001")
    parser.add_argument("--source-order", required=True, help="源头单号，例如 CD26052621001")
    parser.add_argument("--env", default="UAT", help="测试环境，默认 UAT")
    parser.add_argument("--headed", action="store_true", help="使用有头浏览器运行")
    parser.add_argument(
        "--cdp-url",
        help="接管已通过 remote-debugging-port 启动并登录的 Chrome，例如 http://127.0.0.1:9222",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.source_order.strip():
        failure = make_failure("DATA_001", param_name="source_order_no")
        print(failure["message"])
        return 2

    try:
        ctx = run_scenario(
            script_id=args.script,
            source_order_no=args.source_order.strip(),
            env=args.env,
            headed=args.headed,
            cdp_url=args.cdp_url,
        )
    except Exception as exc:
        print(str(exc))
        return 1

    failed_count = sum(1 for item in ctx.logs if item.result == RESULT_FAIL)
    conclusion = RESULT_FAIL if failed_count else "通过"
    print(f"run_id: {ctx.run_id}")
    print(f"脚本编号: {ctx.script_id}")
    print(f"最终测试结论: {conclusion}")
    print(f"测试报告: {ctx.report_path}")
    return 1 if failed_count else 0


if __name__ == "__main__":
    sys.exit(main())
