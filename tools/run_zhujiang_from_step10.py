from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys

import yaml
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from framework.context import RunContext
from framework.report_writer import write_report
from scripts import zhujiang_Purchase_01 as script


def main() -> int:
    systems_config = yaml.safe_load((BASE_DIR / "config" / "systems.yaml").read_text(encoding="utf-8"))
    run_id = "RUN_" + datetime.now().strftime("%Y%m%d_%H%M%S") + "_STEP11_ONLY"
    run_dir = BASE_DIR / "runs" / run_id
    evidence_dir = run_dir / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    ctx = RunContext(
        run_id=run_id,
        script_id=script.SCRIPT_ID,
        script_name=script.SCRIPT_NAME,
        source_order_no="CD26053011003",
        env="UAT",
        systems_config=systems_config,
        run_dir=run_dir,
        evidence_dir=evidence_dir,
    )
    ctx.set_variable("inbound_appointment_no", "G01500120260530986")

    with sync_playwright() as playwright:
        browser = playwright.chromium.connect_over_cdp("http://127.0.0.1:9222")
        page = script._get_system_page(ctx, browser, "wms")
        script._run_step(ctx, page, script._step_11_open_generate_inbound_dialog, script._meta_11())

    ctx.finish()
    write_report(ctx, BASE_DIR / "reports")
    failed_count = sum(1 for item in ctx.logs if item.result == "不通过")
    conclusion = "不通过" if failed_count else "通过"
    print(f"run_id: {ctx.run_id}")
    print(f"脚本编号: {ctx.script_id}")
    print(f"最终测试结论: {conclusion}")
    print(f"测试报告: {ctx.report_path}")
    return 1 if failed_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
