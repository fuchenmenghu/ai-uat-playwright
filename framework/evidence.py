from __future__ import annotations

from pathlib import Path
from typing import Any


def save_failure_screenshot(page: Any, ctx: Any, step_no: str) -> str:
    if page is None:
        return ""

    screenshot_path = Path(ctx.evidence_dir) / f"{ctx.script_id}_{step_no}_failure.png"
    try:
        page.screenshot(path=str(screenshot_path), full_page=True)
        return str(screenshot_path)
    except Exception as exc:
        return f"截图保存失败：{exc}"
