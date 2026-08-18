from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[2]


def load_yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


@dataclass
class Target:
    name: str
    company: str = ""
    title: str = ""

    @property
    def text(self) -> str:
        return f"{self.name}\n{self.company}\n{self.title}".lower()


@dataclass
class RankedBridge:
    contact_id: str
    name: str
    score: float
    types: list[str]
    signals: list[str]
    strength: str
    mode: str
    rationale: str
    contact: dict[str, Any] = field(default_factory=dict)
