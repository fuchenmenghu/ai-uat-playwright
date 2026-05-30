from __future__ import annotations

from typing import Any


def open_page(page: Any, url: str, timeout_seconds: int = 30) -> None:
    page.goto(url, wait_until="domcontentloaded", timeout=timeout_seconds * 1000)


def click_by_text(page: Any, text: str, exact: bool = True) -> None:
    page.get_by_text(text, exact=exact).click()


def fill_by_label(page: Any, label: str, value: str) -> None:
    page.get_by_label(label).fill(value)


def read_text(page: Any, locator_desc: str) -> str:
    return page.locator(locator_desc).first.inner_text()
