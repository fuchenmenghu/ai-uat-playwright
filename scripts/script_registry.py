from __future__ import annotations

import importlib
from types import ModuleType

from framework.error_catalog import make_failure


SCRIPT_REGISTRY = {
    "zhujiang_Purchase_01": {
        "module": "scripts.zhujiang_Purchase_01",
        "script_name": "采购入库-珠江仓非税品（香化）",
    }
}


def get_script(script_id: str) -> ModuleType:
    script_info = SCRIPT_REGISTRY.get(script_id)
    if not script_info:
        failure = make_failure("ENV_006", script_id=script_id)
        raise LookupError(failure["message"])
    return importlib.import_module(script_info["module"])
