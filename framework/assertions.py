from __future__ import annotations

import time
from typing import Any, Callable


class UatAssertionError(AssertionError):
    def __init__(self, failure_code: str, **failure_kwargs: Any) -> None:
        self.failure_code = failure_code
        self.failure_kwargs = failure_kwargs
        super().__init__(f"{failure_code}: {failure_kwargs}")


def assert_page_contains_text(page: Any, expected_text: str) -> None:
    if page.get_by_text(expected_text).count() < 1:
        raise UatAssertionError("ASSERT_001", condition_name="页面文本", condition_value=expected_text)


def assert_element_visible(page: Any, locator_desc: str) -> None:
    locator = page.locator(locator_desc)
    if locator.count() < 1:
        raise UatAssertionError("ELEMENT_001", locator_desc=locator_desc)
    if locator.count() > 1:
        raise UatAssertionError("ELEMENT_009", locator_desc=locator_desc)
    if not locator.first.is_visible():
        raise UatAssertionError("ELEMENT_001", locator_desc=locator_desc)


def assert_table_has_record(page: Any, table_desc: str, row_match_rule: dict[str, str]) -> None:
    raise UatAssertionError("SYSTEM_006", reason=f"表格断言需要按真实页面结构补充：{table_desc} {row_match_rule}")


def assert_field_equals(page: Any, field_name: str, expected_value: str) -> None:
    actual_value = page.get_by_label(field_name).input_value()
    if actual_value != expected_value:
        raise UatAssertionError(
            "ASSERT_002",
            field_name=field_name,
            expected_value=expected_value,
            actual_value=actual_value,
        )


def assert_success_toast(page: Any, success_text: str) -> None:
    if page.get_by_text(success_text).count() < 1:
        raise UatAssertionError("ASSERT_005", success_text=success_text)


def wait_then_assert_text(page: Any, expected_text: str, wait_seconds: int) -> None:
    time.sleep(wait_seconds)
    assert_page_contains_text(page, expected_text)


def wait_for_loading_finished(page: Any, timeout_seconds: int = 30) -> None:
    page.wait_for_load_state("networkidle", timeout=timeout_seconds * 1000)


def wait_for_element_visible(page: Any, locator_desc: str, timeout_seconds: int = 30) -> None:
    page.locator(locator_desc).first.wait_for(state="visible", timeout=timeout_seconds * 1000)


def requery_and_assert_record(
    page: Any,
    query_action: Callable[[], None],
    table_desc: str,
    row_match_rule: dict[str, str],
) -> None:
    query_action()
    assert_table_has_record(page, table_desc, row_match_rule)


def poll_until_record_exists(
    page: Any,
    query_action: Callable[[], None],
    table_desc: str,
    row_match_rule: dict[str, str],
    retries: int = 3,
    interval_seconds: int = 10,
) -> None:
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            query_action()
            assert_table_has_record(page, table_desc, row_match_rule)
            return
        except UatAssertionError as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(interval_seconds)
    raise UatAssertionError(
        "ASSERT_013",
        retries=retries,
        condition_desc=f"{table_desc} 存在记录 {row_match_rule}",
    ) from last_error


def extract_table_field(
    page: Any,
    table_desc: str,
    row_match_rule: dict[str, str],
    field_name: str,
    variable_name: str,
) -> str:
    raise UatAssertionError(
        "DATA_003",
        variable_name=variable_name,
        reason=f"表格字段提取需要按真实页面结构补充：{table_desc} {row_match_rule} {field_name}",
    )


def assert_variable_exists(ctx: Any, variable_name: str) -> None:
    if not ctx.get_variable(variable_name):
        raise UatAssertionError("DATA_002", variable_name=variable_name)
