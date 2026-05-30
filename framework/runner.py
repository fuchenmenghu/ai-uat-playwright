from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from playwright.sync_api import sync_playwright

from framework.context import RunContext
from framework.error_catalog import make_failure
from framework.report_writer import write_report
from framework.step import StepMeta, failed_result
from scripts.script_registry import get_script

BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = BASE_DIR / "config" / "systems.yaml"
RUNS_DIR = BASE_DIR / "runs"
REPORTS_DIR = BASE_DIR / "reports"


def run_scenario(
    script_id: str,
    source_order_no: str,
    env: str = "UAT",
    headed: bool = False,
    cdp_url: str | None = None,
) -> RunContext:
    run_id = _make_run_id()
    run_dir = RUNS_DIR / run_id
    evidence_dir = run_dir / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    script = get_script(script_id)
    systems_config = _load_systems_config(CONFIG_PATH, env)
    ctx = RunContext(
        run_id=run_id,
        script_id=script_id,
        script_name=getattr(script, "SCRIPT_NAME", script_id),
        source_order_no=source_order_no,
        env=env,
        systems_config=systems_config,
        run_dir=run_dir,
        evidence_dir=evidence_dir,
    )

    browser = None
    should_close_browser = True
    try:
        with sync_playwright() as playwright:
            try:
                if cdp_url:
                    browser = playwright.chromium.connect_over_cdp(cdp_url)
                    should_close_browser = False
                else:
                    browser = playwright.chromium.launch(headless=not headed)
            except Exception as exc:
                _append_runner_failure(ctx, "ENV_004", reason=str(exc))
                return _finish_with_report(ctx)

            try:
                script.run(ctx, browser, headed=headed)
            except Exception as exc:
                _append_runner_failure(ctx, "SYSTEM_006", reason=str(exc))
            finally:
                if should_close_browser:
                    browser.close()
    except Exception as exc:
        _append_runner_failure(ctx, "SYSTEM_006", reason=str(exc))

    return _finish_with_report(ctx)


def _load_systems_config(config_path: Path, env: str) -> dict[str, Any]:
    if not config_path.exists():
        failure = make_failure("ENV_001", config_path=str(config_path))
        raise FileNotFoundError(failure["message"])
    with config_path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}
    if data.get("env") != env:
        data["requested_env"] = env
    if "systems" not in data:
        failure = make_failure("ENV_002", config_key="systems")
        raise KeyError(failure["message"])
    return data


def _make_run_id() -> str:
    return "RUN_" + datetime.now().strftime("%Y%m%d_%H%M%S")


def _append_runner_failure(ctx: RunContext, failure_code: str, **failure_kwargs: object) -> None:
    meta = StepMeta(
        step_no="SYSTEM",
        system="测试框架",
        module="Runner",
        operation="执行测试场景并捕获框架级异常。",
        expected="测试框架可以成功完成脚本执行并生成报告。",
    )
    ctx.add_log(failed_result(ctx.script_id, meta, failure_code, **failure_kwargs))


def _finish_with_report(ctx: RunContext) -> RunContext:
    ctx.finish()
    write_report(ctx, REPORTS_DIR)
    return ctx
