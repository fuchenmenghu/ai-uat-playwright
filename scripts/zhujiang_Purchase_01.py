from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

from framework.evidence import save_failure_screenshot
from framework.step import StepMeta, failed_result, passed_result

SCRIPT_ID = "zhujiang_Purchase_01"
SCRIPT_NAME = "采购入库-珠江仓非税品（香化）"
INVOLVED_SYSTEMS = ["CIBO", "通天晓-WMS"]


class StepFailed(Exception):
    def __init__(self, failure_code: str, **failure_kwargs: object) -> None:
        self.failure_code = failure_code
        self.failure_kwargs = failure_kwargs
        super().__init__(f"{failure_code}: {failure_kwargs}")


def run(ctx, browser, headed: bool = False) -> None:
    cibo_page = _get_system_page(ctx, browser, "supply_chain")
    _run_step(ctx, cibo_page, _step_01_open_cibo_appointment, _meta_01())
    _run_step(ctx, cibo_page, _step_02_fill_source_order, _meta_02())
    _run_step(ctx, cibo_page, _step_03_query_source_order, _meta_03())
    _run_step(ctx, cibo_page, _step_04_assert_appointment_status, _meta_04())
    _run_step(ctx, cibo_page, _step_05_extract_appointment_no, _meta_05())
    _run_step(ctx, cibo_page, _step_06_extract_inbound_no, _meta_06())
    _run_step(ctx, cibo_page, _step_07_assert_shipment_no, _meta_07())

    wms_page = _get_system_page(ctx, browser, "wms")
    _run_step(ctx, wms_page, _step_08_open_wms_purchase_order, _meta_08())
    _run_step(ctx, wms_page, _step_09_fill_ncc_no, _meta_09())
    _run_step(ctx, wms_page, _step_10_query_purchase_order, _meta_10())
    _run_step(ctx, wms_page, _step_11_open_generate_inbound_dialog, _meta_11())
    _run_step(ctx, wms_page, _step_12_add_purchase_detail, _meta_12())
    _run_step(ctx, wms_page, _step_13_generate_inbound_order, _meta_13())
    _run_step(ctx, wms_page, _step_14_open_wms_inbound_order, _meta_14())
    _run_step(ctx, wms_page, _step_16_fill_purchase_order_no, _meta_16())
    _run_step(ctx, wms_page, _step_17_query_inbound_order, _meta_17())
    _run_step(ctx, wms_page, _step_18_receive_query_inbound_order, _meta_18())
    _run_step(ctx, wms_page, _step_19_batch_confirm_receive, _meta_19())
    _run_step(ctx, wms_page, _step_20_query_putaway_task, _meta_20())
    _run_step(ctx, wms_page, _step_21_assign_confirm, _meta_21())
    _run_step(ctx, wms_page, _step_22_confirm_user_dialog, _meta_22())


def _meta_01() -> StepMeta:
    return StepMeta(
        step_no="Step 01",
        system="CIBO",
        module="履约管理 → 入库履约 → 入库预约单管理",
        operation="进入“履约管理 → 入库履约 → 入库预约单管理”页面。",
        expected="页面正常加载，展示入库预约单管理查询区和列表区。",
    )


def _meta_02() -> StepMeta:
    return StepMeta(
        step_no="Step 02",
        system="CIBO",
        module="履约管理 → 入库履约 → 入库预约单管理",
        operation="展开查询条件，在“来源单号”字段输入运行时传入的 {source_order_no}。",
        expected="来源单号字段可输入。",
    )


def _meta_03() -> StepMeta:
    return StepMeta(
        step_no="Step 03",
        system="CIBO",
        module="履约管理 → 入库履约 → 入库预约单管理",
        operation="点击“查询”，根据来源单号 {source_order_no} 查询入库预约单。",
        expected="查询结果中应存在来源单号等于 {source_order_no} 的记录。",
    )


def _meta_04() -> StepMeta:
    return StepMeta(
        step_no="Step 04",
        system="CIBO",
        module="履约管理 → 入库履约 → 入库预约单管理",
        operation="核对查询结果中的“入库预约单状态”。",
        expected="入库预约单状态值为“已发货”。",
    )


def _meta_05() -> StepMeta:
    return StepMeta(
        step_no="Step 05",
        system="CIBO",
        module="履约管理 → 入库履约 → 入库预约单管理",
        operation="横向滚动列表，查看“入库预约单号”字段是否有值，并提取该字段。",
        expected="入库预约单号字段下有值。",
    )


def _meta_06() -> StepMeta:
    return StepMeta(
        step_no="Step 06",
        system="CIBO",
        module="履约管理 → 入库履约 → 入库预约单管理",
        operation="横向滚动列表，查看“Inbound No”字段是否有值，并提取该字段。",
        expected="Inbound No 字段下有值。",
    )


def _meta_07() -> StepMeta:
    return StepMeta(
        step_no="Step 07",
        system="CIBO",
        module="履约管理 → 入库履约 → 入库预约单管理",
        operation="横向滚动列表，查看“中免发运号”字段是否有值。",
        expected="中免发运号字段下有值。",
    )


def _meta_08() -> StepMeta:
    return StepMeta(
        step_no="Step 08",
        system="通天晓-WMS",
        module="采购 → 采购单",
        operation="进入“采购 → 采购单”页面。",
        expected="页面正常加载，展示采购单模块的查询区和列表区。",
    )


def _meta_09() -> StepMeta:
    return StepMeta(
        step_no="Step 09",
        system="通天晓-WMS",
        module="采购 → 采购单",
        operation="展开查询条件，在“NCC单号”字段输入提取的变量 {inbound_appointment_no}。",
        expected="NCC单号字段可输入。",
    )


def _meta_10() -> StepMeta:
    return StepMeta(
        step_no="Step 10",
        system="通天晓-WMS",
        module="采购 → 采购单",
        operation="点击“查询”，根据NCC单号中输入的 {inbound_appointment_no} 查询采购单。",
        expected="查询结果中应存在 NCC 单号等于 {inbound_appointment_no} 的记录，并提取采购单号。",
    )


def _meta_11() -> StepMeta:
    return StepMeta(
        step_no="Step 11",
        system="通天晓-WMS",
        module="采购 → 采购单",
        operation="选中列表中 NCC 单号等于 {inbound_appointment_no} 的记录，点击“生成入库单”按钮。",
        expected="系统弹出“生成入库单”窗口，并展示可生成入库单的采购明细。",
    )


def _meta_12() -> StepMeta:
    return StepMeta(
        step_no="Step 12",
        system="通天晓-WMS",
        module="采购 → 采购单",
        operation="在“生成入库单”窗口中选择采购明细，点击“加入入库单”按钮。",
        expected="采购明细被加入下方待生成入库单区域。",
    )


def _meta_13() -> StepMeta:
    return StepMeta(
        step_no="Step 13",
        system="通天晓-WMS",
        module="采购 → 采购单",
        operation="在当前窗口点击“生成入库单”按钮。",
        expected="系统提示 Success，窗口自动关闭。",
    )


def _meta_14() -> StepMeta:
    return StepMeta(
        step_no="Step 14",
        system="通天晓-WMS",
        module="入库 → 入库单",
        operation="进入“入库 → 入库单”页面。",
        expected="页面正常加载，展示入库单模块的查询区和列表区。",
    )


def _meta_16() -> StepMeta:
    return StepMeta(
        step_no="Step 16",
        system="通天晓-WMS",
        module="入库 → 入库单",
        operation="展开查询条件，在“采购单号”字段输入提取的变量 {wms_purchase_order_no}。",
        expected="采购单号字段可输入。",
    )


def _meta_17() -> StepMeta:
    return StepMeta(
        step_no="Step 17",
        system="通天晓-WMS",
        module="入库 → 入库单",
        operation="点击“查询”，根据采购单号 {wms_purchase_order_no} 查询入库单。",
        expected="页面应查询到入库单记录，并提取入库单号。",
    )


def _meta_18() -> StepMeta:
    return StepMeta(
        step_no="Step 18",
        system="通天晓-WMS",
        module="入库 → 收货",
        operation="在查询区域的入库单号处输入提取的变量 {wms_inbound_order_no}，然后回车。",
        expected="入库单号查询框可输入，回车后在“单据明细”处查询到信息。",
    )


def _meta_19() -> StepMeta:
    return StepMeta(
        step_no="Step 19",
        system="通天晓-WMS",
        module="入库 → 收货",
        operation="在单据明细处选中单据，点击“批量确认”按钮。",
        expected="系统提示 Success。",
    )


def _meta_20() -> StepMeta:
    return StepMeta(
        step_no="Step 20",
        system="通天晓-WMS",
        module="任务 → 上架任务",
        operation="查询区域，在“参考单号”字段输入提取的变量 {wms_inbound_order_no}，回车。",
        expected="页面应查询到上架任务记录。",
    )


def _meta_21() -> StepMeta:
    return StepMeta(
        step_no="Step 21",
        system="通天晓-WMS",
        module="任务 → 上架任务",
        operation="在列表处选中单据，点击“指派确认”按钮。",
        expected="页面弹出“选择用户”窗口。",
    )


def _meta_22() -> StepMeta:
    return StepMeta(
        step_no="Step 22",
        system="通天晓-WMS",
        module="任务 → 上架任务",
        operation="在“选择用户窗口”处点击“确定”按钮。",
        expected="系统提示 Success，窗口自动关闭。",
    )


def _run_step(ctx, page, step_func, meta: StepMeta) -> None:
    try:
        step_func(ctx, page)
    except StepFailed as exc:
        screenshot_path = save_failure_screenshot(page, ctx, meta.step_no.replace(" ", "_"))
        ctx.add_log(
            failed_result(
                SCRIPT_ID,
                meta,
                exc.failure_code,
                screenshot_path=screenshot_path,
                **exc.failure_kwargs,
            )
        )
    except Exception as exc:
        screenshot_path = save_failure_screenshot(page, ctx, meta.step_no.replace(" ", "_"))
        ctx.add_log(
            failed_result(
                SCRIPT_ID,
                meta,
                "SYSTEM_006",
                screenshot_path=screenshot_path,
                reason=str(exc),
            )
        )
    else:
        ctx.add_log(passed_result(SCRIPT_ID, meta))


def _step_01_open_cibo_appointment(ctx, page) -> None:
    _ensure_page_loaded(ctx, page, "supply_chain")
    _click_menu_path(page, ["履约管理", "入库履约", "入库预约单管理"])
    _wait_for_any_text(page, ["入库预约单管理", "来源单号"], timeout_ms=15000)


def _step_02_fill_source_order(ctx, page) -> None:
    if not ctx.source_order_no:
        raise StepFailed("DATA_001", param_name="source_order_no")
    _try_expand_filters(page)
    _fill_input_by_label(page, "来源单号", ctx.source_order_no, ["input[placeholder='请输入']"])


def _step_03_query_source_order(ctx, page) -> None:
    _retry_query_until(
        page,
        query_action=lambda: _click_button(page, ["查询"]),
        assertion=lambda: _has_table_row_by_column(page, "来源单号", ctx.source_order_no),
        retries=2,
        interval_seconds=0,
        condition_desc=f"来源单号={ctx.source_order_no}",
    )


def _step_04_assert_appointment_status(ctx, page) -> None:
    actual_status = _read_table_cell(page, "来源单号", ctx.source_order_no, "入库预约单状态")
    if actual_status != "已发货":
        raise StepFailed(
            "ASSERT_003",
            status_field="入库预约单状态",
            expected_status="已发货",
            actual_status=actual_status,
        )


def _step_05_extract_appointment_no(ctx, page) -> None:
    value = _read_table_cell(page, "来源单号", ctx.source_order_no, "入库预约单号")
    _set_required_variable(ctx, "inbound_appointment_no", value)


def _step_06_extract_inbound_no(ctx, page) -> None:
    value = _read_table_cell(page, "来源单号", ctx.source_order_no, "Inbound No")
    _set_required_variable(ctx, "inbound_no", value)


def _step_07_assert_shipment_no(ctx, page) -> None:
    value = _read_table_cell(page, "来源单号", ctx.source_order_no, "中免发运号")
    if not value:
        raise StepFailed("ASSERT_002", field_name="中免发运号", expected_value="非空", actual_value=value)


def _step_08_open_wms_purchase_order(ctx, page) -> None:
    _ensure_page_loaded(ctx, page, "wms")
    _click_menu_path(page, ["採購", "採購單"], aliases={"採購": ["采购"], "採購單": ["采购单"]})
    _wait_for_any_text(page, ["採購單", "采购单", "NCC单号", "NCC單號"], timeout_ms=15000)


def _step_09_fill_ncc_no(ctx, page) -> None:
    inbound_appointment_no = _required_variable(ctx, "inbound_appointment_no")
    _try_expand_filters(page)
    _fill_input_by_label(
        page,
        "NCC单号",
        inbound_appointment_no,
        [
            "input#ttx_dijit_TextareaDialogTextBox_0",
            "div[widgetid='ttx_dijit_TextareaDialogTextBox_0'] input.dijitInputInner",
            ".ttxDialogTextBox input.dijitInputInner",
            "input[name='erpOrderCode']",
        ],
    )


def _step_10_query_purchase_order(ctx, page) -> None:
    inbound_appointment_no = _required_variable(ctx, "inbound_appointment_no")
    _retry_query_until(
        page,
        query_action=lambda: _click_button(page, ["查詢", "查询"]),
        assertion=lambda: _has_table_row_by_column(page, "NCC单号", inbound_appointment_no),
        retries=2,
        interval_seconds=0,
        condition_desc=f"NCC单号={inbound_appointment_no}",
    )
    value = _read_table_cell(page, "NCC单号", inbound_appointment_no, "采购单号")
    _set_required_variable(ctx, "wms_purchase_order_no", value)


def _step_11_open_generate_inbound_dialog(ctx, page) -> None:
    inbound_appointment_no = _required_variable(ctx, "inbound_appointment_no")
    _select_table_row(page, "NCC单号", inbound_appointment_no)
    _click_button(page, ["生成入庫單", "生成入库单"])
    _wait_for_any_text(page, ["加入入庫單", "加入入库单"], timeout_ms=15000)


def _step_12_add_purchase_detail(ctx, page) -> None:
    _select_first_detail_row(page)
    _click_button(page, ["加入入庫單", "加入入库单"])
    _wait_table_settled(page)
    _assert_any_text(page, ["待生成入庫單", "待生成入库单", "入庫單明細", "入库单明细", "采购明细"])


def _step_13_generate_inbound_order(ctx, page) -> None:
    _click_button(page, ["生成入庫單", "生成入库单"])
    _wait_for_success(page)


def _step_14_open_wms_inbound_order(ctx, page) -> None:
    _click_menu_path(page, ["入庫", "入庫單"], aliases={"入庫": ["入库"], "入庫單": ["入库单"]})
    _wait_for_any_text(page, ["入庫單", "入库单", "采购单号", "採購單號"], timeout_ms=15000)


def _step_16_fill_purchase_order_no(ctx, page) -> None:
    purchase_order_no = _required_variable(ctx, "wms_purchase_order_no")
    _try_expand_filters(page)
    _fill_input_by_label(page, "采购单号", purchase_order_no, ["input[name='purchaseOrderCode']"])


def _step_17_query_inbound_order(ctx, page) -> None:
    purchase_order_no = _required_variable(ctx, "wms_purchase_order_no")
    _click_button(page, ["查詢", "查询"])
    _wait_table_settled(page)
    if not _has_table_row_by_column(page, "采购单号", purchase_order_no):
        raise StepFailed("ASSERT_001", condition_name="采购单号", condition_value=purchase_order_no)
    value = _read_table_cell(page, "采购单号", purchase_order_no, "入库单号")
    _set_required_variable(ctx, "wms_inbound_order_no", value)


def _step_18_receive_query_inbound_order(ctx, page) -> None:
    inbound_order_no = _required_variable(ctx, "wms_inbound_order_no")
    _click_menu_path(page, ["入庫", "收貨"], aliases={"入庫": ["入库"], "收貨": ["收货"]})
    _wait_for_any_text(page, ["收貨", "收货", "入库单号", "入庫單號"], timeout_ms=15000)
    _fill_input_by_label(page, "入库单号", inbound_order_no)
    _press_enter_on_focused_or_label(page, "入库单号")
    _wait_table_settled(page)
    if not _page_contains_text(page, inbound_order_no):
        raise StepFailed("ASSERT_001", condition_name="入库单号", condition_value=inbound_order_no)


def _step_19_batch_confirm_receive(ctx, page) -> None:
    _select_first_detail_row(page)
    _click_button(page, ["批量確認", "批量确认"])
    _wait_for_success(page)


def _step_20_query_putaway_task(ctx, page) -> None:
    inbound_order_no = _required_variable(ctx, "wms_inbound_order_no")
    _click_menu_path(page, ["任務", "上架任務"], aliases={"任務": ["任务"], "上架任務": ["上架任务"]})
    _wait_for_any_text(page, ["上架任務", "上架任务", "参考单号", "參考單號"], timeout_ms=15000)
    _fill_input_by_label(page, "参考单号", inbound_order_no)
    _press_enter_on_focused_or_label(page, "参考单号")
    _wait_table_settled(page)
    if not _has_table_row_by_column(page, "参考单号", inbound_order_no):
        raise StepFailed("ASSERT_001", condition_name="参考单号", condition_value=inbound_order_no)


def _step_21_assign_confirm(ctx, page) -> None:
    inbound_order_no = _required_variable(ctx, "wms_inbound_order_no")
    _select_table_row(page, "参考单号", inbound_order_no)
    _click_button(page, ["指派確認", "指派确认"])
    _wait_for_any_text(page, ["选择用户", "選擇用戶", "选择用戶", "確定", "确定"], timeout_ms=15000)


def _step_22_confirm_user_dialog(ctx, page) -> None:
    _click_button(page, ["確定", "确定"])
    _wait_for_success(page)


def _get_system_page(ctx, browser, system_key: str):
    systems = ctx.systems_config.get("systems", {})
    system = systems.get(system_key)
    if not system:
        raise StepFailed("ENV_002", config_key=f"systems.{system_key}")
    target_url = system.get("url", "")
    target_host = urlparse(target_url).netloc

    pages = [page for context in browser.contexts for page in context.pages]
    for page in pages:
        if target_host and target_host in page.url:
            return page

    if pages:
        page = pages[0]
    else:
        context = browser.contexts[0] if browser.contexts else browser.new_context()
        page = context.new_page()
    if target_url and target_host not in page.url:
        page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
    return page


def _ensure_page_loaded(ctx, page, system_key: str) -> None:
    system = ctx.systems_config["systems"][system_key]
    target_url = system.get("url", "")
    target_host = urlparse(target_url).netloc
    if target_url and target_host not in page.url:
        page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_load_state("domcontentloaded", timeout=30000)


def _click_menu_path(page, menu_path: list[str], aliases: dict[str, list[str]] | None = None) -> None:
    for menu_text in menu_path:
        options = [menu_text] + (aliases or {}).get(menu_text, [])
        _click_first_visible_text(page, options, failure_text=menu_text)
        page.wait_for_timeout(300)


def _click_first_visible_text(page, texts: list[str], failure_text: str) -> None:
    last_error: Exception | None = None
    for text in texts:
        candidates = [
            page.get_by_text(text, exact=True),
            page.locator(f"span[title='{text}']"),
            page.locator(f"li:has-text('{text}')"),
            page.locator(f"div:has-text('{text}')"),
        ]
        for locator in candidates:
            try:
                if locator.count() > 0:
                    item = locator.first
                    item.scroll_into_view_if_needed(timeout=3000)
                    item.click(timeout=5000)
                    return
            except Exception as exc:
                last_error = exc
    raise StepFailed("NAV_002", menu_path=failure_text) from last_error


def _wait_for_any_text(page, texts: list[str], timeout_ms: int) -> None:
    last_error: Exception | None = None
    for text in texts:
        try:
            page.get_by_text(text, exact=False).first.wait_for(state="visible", timeout=timeout_ms)
            return
        except Exception as exc:
            last_error = exc
    raise StepFailed("NAV_003", page_name="/".join(texts), timeout_seconds=timeout_ms // 1000) from last_error


def _assert_any_text(page, texts: list[str]) -> None:
    if not any(_page_contains_text(page, text) for text in texts):
        raise StepFailed("ASSERT_001", condition_name="页面文本", condition_value="/".join(texts))


def _page_contains_text(page, text: str) -> bool:
    try:
        return page.get_by_text(text, exact=False).count() > 0
    except Exception:
        return False


def _try_expand_filters(page) -> None:
    for text in ["展开", "更多", "更多查询", "高级查询", "展開", "更多查詢"]:
        try:
            locator = page.get_by_text(text, exact=True)
            if locator.count() > 0 and locator.first.is_visible():
                locator.first.click(timeout=2000)
                return
        except Exception:
            continue


def _fill_input_by_label(
    page,
    label: str,
    value: str,
    extra_selectors: list[str] | None = None,
) -> None:
    aliases = _text_aliases(label)
    selectors = list(extra_selectors or [])
    selectors.extend(
        [
            f".el-form-item:has(label:has-text('{item}')) input"
            for item in aliases
        ]
    )
    selectors.extend(
        [
            f"xpath=//*[contains(normalize-space(.), '{item}')]/following::input[not(@type='hidden')][1]"
            for item in aliases
        ]
    )

    last_error: Exception | None = None
    for selector in selectors:
        locator = page.locator(selector)
        try:
            if locator.count() == 0:
                continue
            candidate = locator.first
            candidate.scroll_into_view_if_needed(timeout=3000)
            candidate.click(timeout=3000)
            candidate.fill(value, timeout=5000)
            actual_value = candidate.input_value(timeout=3000)
            if actual_value != value:
                raise StepFailed("ASSERT_002", field_name=label, expected_value=value, actual_value=actual_value)
            return
        except StepFailed:
            raise
        except Exception as exc:
            last_error = exc
            continue
    raise StepFailed("ELEMENT_001", locator_desc=f"{label}输入框") from last_error


def _press_enter_on_focused_or_label(page, label: str) -> None:
    try:
        page.keyboard.press("Enter")
        return
    except Exception:
        pass
    locator = page.locator(
        f"xpath=//*[contains(normalize-space(.), '{label}')]/following::input[not(@type='hidden')][1]"
    ).first
    try:
        locator.press("Enter", timeout=3000)
    except Exception as exc:
        raise StepFailed("ACTION_002", target=f"{label}输入框") from exc


def _click_button(page, texts: list[str]) -> None:
    last_error: Exception | None = None
    for text in texts:
        locators = [
            page.locator("#dijit_form_Button_19_label").filter(has_text=text).first,
            page.get_by_role("button", name=re.compile(rf"^\s*{re.escape(text)}\s*$")).first,
            page.locator(f"button:has-text('{text}')").first,
            page.locator(f"span.dijitButtonText:has-text('{text}')").first,
            page.locator(f"span:has-text('{text}')").first,
        ]
        for locator in locators:
            try:
                locator.wait_for(state="visible", timeout=5000)
                locator.scroll_into_view_if_needed(timeout=3000)
                locator.click(timeout=5000)
                return
            except Exception as exc:
                last_error = exc
    raise StepFailed("ELEMENT_002", locator_desc="/".join(texts)) from last_error


def _retry_query_until(
    page,
    query_action,
    assertion,
    retries: int,
    interval_seconds: int,
    condition_desc: str,
) -> None:
    for attempt in range(1, retries + 1):
        query_action()
        _wait_table_settled(page)
        if assertion():
            return
        if attempt < retries and interval_seconds:
            page.wait_for_timeout(interval_seconds * 1000)
    raise StepFailed("ASSERT_013", retries=retries, condition_desc=condition_desc)


def _wait_table_settled(page) -> None:
    try:
        page.wait_for_load_state("networkidle", timeout=10000)
    except Exception:
        pass
    for selector in [".el-loading-mask", ".vxe-loading", ".dijitContentPaneLoading", ".loading"]:
        try:
            page.locator(selector).first.wait_for(state="hidden", timeout=10000)
        except Exception:
            pass


def _wait_for_success(page) -> None:
    try:
        _wait_for_any_text(page, ["Success", "success", "成功", "操作成功"], timeout_ms=15000)
    except StepFailed as exc:
        raise StepFailed("ASSERT_005", success_text="Success") from exc


def _has_table_row_by_column(page, match_column: str, match_value: str) -> bool:
    try:
        _read_table_cell(page, match_column, match_value, match_column)
        return True
    except StepFailed:
        return False


def _read_table_cell(page, match_column: str, match_value: str, target_column: str) -> str:
    payload = _read_table_payload(page, match_column, match_value, target_column)
    if not payload.get("found_table"):
        raise StepFailed("ELEMENT_003", table_desc="业务列表")
    if payload.get("multi"):
        raise StepFailed("DATA_005", variable_name=f"{match_column}={match_value}")
    if not payload.get("found_row"):
        raise StepFailed("ASSERT_001", condition_name=match_column, condition_value=match_value)
    if not payload.get("found_column"):
        raise StepFailed("ELEMENT_004", table_desc="业务列表", column_name=target_column)
    return _normalize_text(payload.get("value"))


def _select_table_row(page, match_column: str, match_value: str) -> None:
    payload = _read_table_payload(page, match_column, match_value, match_column)
    if not payload.get("found_row"):
        raise StepFailed("ASSERT_001", condition_name=match_column, condition_value=match_value)
    checkbox_rect = _gridx_row_checkbox_rect(page, match_value)
    if not checkbox_rect:
        raise StepFailed("ACTION_001", target=f"{match_column}={match_value} 行复选框")
    if not checkbox_rect.get("checked"):
        page.mouse.click(checkbox_rect["x"], checkbox_rect["y"])


def _read_table_payload(
    page,
    match_column: str,
    match_value: str,
    target_column: str,
    click_row: bool = False,
) -> dict[str, Any]:
    return page.evaluate(
        """({ matchColumn, matchValue, targetColumn, clickRow }) => {
          const normalize = (value) => String(value || '').replace(/\\s+/g, ' ').trim();
          const aliases = (text) => {
            const base = normalize(text).replace(/列$/, '');
            const variants = new Set([base]);
            const pairs = [
              ['采购', '採購'], ['单', '單'], ['号', '號'], ['入库', '入庫'],
              ['收货', '收貨'], ['任务', '任務'], ['参考', '參考']
            ];
            for (const [simp, trad] of pairs) {
              for (const item of [...variants]) {
                if (item.includes(simp)) variants.add(item.replaceAll(simp, trad));
                if (item.includes(trad)) variants.add(item.replaceAll(trad, simp));
              }
            }
            return [...variants].filter(Boolean);
          };
          const sameColumn = (actual, expected) => {
            const actualAliases = aliases(actual);
            const expectedAliases = aliases(expected);
            return actualAliases.some((a) => expectedAliases.some((e) => a === e || a.includes(e) || e.includes(a)));
          };
          const tables = [...document.querySelectorAll('table')];
          const tablePairs = [];
          const tableHeaders = (table) => [...table.querySelectorAll('th,[role=columnheader]')].map((th) => normalize(th.innerText));
          const tableRows = (table) => [...table.querySelectorAll('tbody tr,[role=row]')].filter((row) => normalize(row.innerText));
          const rowCells = (row) => [...row.querySelectorAll('td,[role=gridcell],.dojoxGridCell')].map((td) => normalize(td.innerText));
          for (let i = 0; i < tables.length; i += 1) {
            const className = String(tables[i].className || '');
            if (className.includes('vxe-table--header')) {
              const body = tables.slice(i + 1).find((table) => String(table.className || '').includes('vxe-table--body'));
              if (body) tablePairs.push({ header: tables[i], body });
            }
          }
          for (let i = 0; i < tables.length; i += 1) {
            const table = tables[i];
            if (tablePairs.some((pair) => pair.header === table || pair.body === table)) continue;
            const headers = tableHeaders(table);
            if (headers.length === 0) continue;
            const ownRows = tableRows(table).filter((row) => rowCells(row).join('\\t') !== headers.join('\\t'));
            let body = ownRows.length > 0 ? table : null;
            if (!body) {
              body = tables.slice(i + 1).find((candidate) => {
                if (tableHeaders(candidate).length > 0) return false;
                const rows = tableRows(candidate).map(rowCells).filter((cells) => cells.some(Boolean));
                return rows.some((cells) => cells.length >= Math.min(headers.length, 4));
              });
            }
            if (body) tablePairs.push({ header: table, body });
          }

          for (const pair of tablePairs) {
            const headers = tableHeaders(pair.header);
            const matchIndex = headers.findIndex((text) => sameColumn(text, matchColumn));
            const targetIndex = headers.findIndex((text) => sameColumn(text, targetColumn));
            if (matchIndex < 0) continue;

            const rows = tableRows(pair.body).filter((row) => rowCells(row).join('\\t') !== headers.join('\\t'));
            const matches = [];
            for (const row of rows) {
              const cells = rowCells(row);
              const cellText = cells[matchIndex] || '';
              if (cellText === matchValue || cellText.includes(matchValue)) {
                matches.push({ row, cells });
              }
            }
            if (matches.length === 0) continue;
            const uniqueRows = [...new Set(matches.map((item) => item.cells.join('\\t')))];
            if (uniqueRows.length > 1) {
              return { found_table: true, found_row: true, found_column: targetIndex >= 0, multi: true, value: '' };
            }
            return {
              found_table: true,
              found_row: true,
              found_column: targetIndex >= 0,
              multi: false,
              value: targetIndex >= 0 ? (matches[0].cells[targetIndex] || '') : ''
            };
          }
          return { found_table: tablePairs.length > 0, found_row: false, found_column: false, multi: false, value: '' };
        }""",
        {
            "matchColumn": match_column,
            "matchValue": match_value,
            "targetColumn": target_column,
            "clickRow": click_row,
        },
    )


def _gridx_row_checkbox_rect(page, match_value: str) -> dict[str, Any] | None:
    return page.evaluate(
        """(matchValue) => {
          const normalize = (value) => String(value || '').replace(/\\s+/g, ' ').trim();
          const rows = [...document.querySelectorAll('.gridxRow[role="row"], [role="row"], tbody tr')]
            .filter((row) => normalize(row.innerText).includes(matchValue));
          const visibleRows = rows.filter((row) => {
            const rect = row.getBoundingClientRect();
            return rect.width > 0 && rect.height > 0;
          });
          const row = visibleRows[0];
          if (!row) return null;

          const rowRect = row.getBoundingClientRect();
          const rowMidY = rowRect.top + rowRect.height / 2;
          const rowHeaders = [...document.querySelectorAll('.gridxRowHeaderCell[role="rowheader"]')]
            .filter((cell) => {
              const rect = cell.getBoundingClientRect();
              return rect.width > 0 && rect.height > 0 && rowMidY >= rect.top - 2 && rowMidY <= rect.bottom + 2;
            });
          const header = rowHeaders[0];
          if (!header) return null;
          const checkbox = header.querySelector('.gridxIndirectSelectionCheckBox[role="checkbox"], span[role="checkbox"]');
          if (!checkbox) return null;
          const rect = checkbox.getBoundingClientRect();
          return {
            x: rect.left + rect.width / 2,
            y: rect.top + rect.height / 2,
            checked: checkbox.getAttribute('aria-checked') === 'true' || String(checkbox.className || '').includes('Checked'),
          };
        }""",
        match_value,
    )


def _wait_gridx_row_selected(page, match_value: str) -> None:
    try:
        page.wait_for_function(
            """(matchValue) => {
              const normalize = (value) => String(value || '').replace(/\\s+/g, ' ').trim();
              if (/已選取\\s*[：:]\\s*[1-9]/.test(normalize(document.body.innerText))) return true;
              const rows = [...document.querySelectorAll('.gridxRow[role="row"], [role="row"], tbody tr')]
                .filter((row) => normalize(row.innerText).includes(matchValue));
              const row = rows.find((item) => {
                const rect = item.getBoundingClientRect();
                return rect.width > 0 && rect.height > 0;
              });
              if (!row) return false;
              const rowRect = row.getBoundingClientRect();
              const rowMidY = rowRect.top + rowRect.height / 2;
              const header = [...document.querySelectorAll('.gridxRowHeaderCell[role="rowheader"]')]
                .find((cell) => {
                  const rect = cell.getBoundingClientRect();
                  return rect.width > 0 && rect.height > 0 && rowMidY >= rect.top - 2 && rowMidY <= rect.bottom + 2;
                });
              const checkbox = header && header.querySelector('.gridxIndirectSelectionCheckBox[role="checkbox"], span[role="checkbox"]');
              return Boolean(checkbox && (checkbox.getAttribute('aria-checked') === 'true' || String(checkbox.className || '').includes('Checked')));
            }""",
            match_value,
            timeout=5000,
        )
    except Exception as exc:
        raise StepFailed("ACTION_001", target=f"NCC单号={match_value} 行复选框") from exc


def _select_first_detail_row(page) -> None:
    clicked = page.evaluate(
        """() => {
          const normalize = (value) => String(value || '').replace(/\\s+/g, ' ').trim();
          const rows = [...document.querySelectorAll('tbody tr,[role=row]')]
            .filter((row) => normalize(row.innerText));
          const row = rows.find((item) => item.querySelector('input[type=checkbox]')) || rows[0];
          if (!row) return false;
          const checkbox = row.querySelector('input[type=checkbox]');
          if (checkbox) checkbox.click();
          else row.click();
          return true;
        }"""
    )
    if not clicked:
        raise StepFailed("ELEMENT_003", table_desc="明细列表")


def _required_variable(ctx, variable_name: str) -> str:
    value = _normalize_text(ctx.get_variable(variable_name))
    if not value:
        raise StepFailed("DATA_002", variable_name=variable_name)
    return value


def _set_required_variable(ctx, variable_name: str, value: str) -> None:
    normalized = _normalize_text(value)
    if not normalized:
        raise StepFailed("DATA_003", variable_name=variable_name)
    ctx.set_variable(variable_name, normalized)
    if not ctx.get_variable(variable_name):
        raise StepFailed("DATA_003", variable_name=variable_name)


def _text_aliases(text: str) -> list[str]:
    pairs = [
        ("采购", "採購"),
        ("单", "單"),
        ("号", "號"),
        ("入库", "入庫"),
        ("收货", "收貨"),
        ("任务", "任務"),
        ("参考", "參考"),
    ]
    result = {text}
    for simplified, traditional in pairs:
        current = list(result)
        for item in current:
            if simplified in item:
                result.add(item.replace(simplified, traditional))
            if traditional in item:
                result.add(item.replace(traditional, simplified))
    return list(result)


def _normalize_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()
