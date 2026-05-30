from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from framework.step import StepResult


@dataclass
class RunContext:
    run_id: str
    script_id: str
    script_name: str
    source_order_no: str
    env: str
    systems_config: dict[str, Any]
    run_dir: Path
    evidence_dir: Path
    report_path: Path | None = None
    variables: dict[str, Any] = field(default_factory=dict)
    logs: list[StepResult] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    ended_at: datetime | None = None

    def add_log(self, result: StepResult) -> None:
        self.logs.append(result)

    def set_variable(self, name: str, value: Any) -> None:
        self.variables[name] = value

    def get_variable(self, name: str, default: Any = None) -> Any:
        return self.variables.get(name, default)

    def finish(self) -> None:
        self.ended_at = datetime.now()

    @property
    def involved_system_names(self) -> str:
        systems = self.systems_config.get("systems", {})
        names = [item.get("name", key) for key, item in systems.items()]
        return "、".join(names)
