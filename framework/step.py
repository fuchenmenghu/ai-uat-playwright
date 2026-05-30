from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from framework.error_catalog import make_failure

RESULT_PASS = "通过"
RESULT_FAIL = "不通过"


@dataclass(frozen=True)
class StepMeta:
    step_no: str
    system: str
    module: str
    operation: str
    expected: str


@dataclass
class StepResult:
    script_id: str
    step_no: str
    system: str
    module: str
    operation: str
    expected: str
    result: str
    failure_code: str = ""
    failure_type: str = ""
    raw_failure_message: str = ""
    screenshot_path: str = ""
    trace_path: str = ""
    executed_at: str = ""

    def __post_init__(self) -> None:
        if self.result not in {RESULT_PASS, RESULT_FAIL}:
            raise ValueError("Step result must be '通过' or '不通过'.")
        if not self.executed_at:
            self.executed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_operation_log_row(self) -> dict[str, str]:
        return {
            "脚本编号": self.script_id,
            "步骤编号": self.step_no,
            "系统": self.system,
            "模块": self.module,
            "操作描述": self.operation,
            "预期结果": self.expected,
            "执行结果": self.result,
            "失败编码": self.failure_code,
            "失败类型": self.failure_type,
            "原始失败信息": self.raw_failure_message,
            "截图路径": self.screenshot_path,
            "trace路径": self.trace_path,
            "执行时间": self.executed_at,
        }


def passed_result(script_id: str, meta: StepMeta) -> StepResult:
    return StepResult(
        script_id=script_id,
        step_no=meta.step_no,
        system=meta.system,
        module=meta.module,
        operation=meta.operation,
        expected=meta.expected,
        result=RESULT_PASS,
    )


def failed_result(
    script_id: str,
    meta: StepMeta,
    failure_code: str,
    screenshot_path: str = "",
    trace_path: str = "",
    **failure_kwargs: object,
) -> StepResult:
    failure = make_failure(failure_code, **failure_kwargs)
    return StepResult(
        script_id=script_id,
        step_no=meta.step_no,
        system=meta.system,
        module=meta.module,
        operation=meta.operation,
        expected=meta.expected,
        result=RESULT_FAIL,
        failure_code=failure["code"],
        failure_type=failure["failure_type"],
        raw_failure_message=failure["message"],
        screenshot_path=screenshot_path,
        trace_path=trace_path,
    )
