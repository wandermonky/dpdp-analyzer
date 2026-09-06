"""DPDP rule pack schema and loader."""
from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field

Category = Literal["consent", "notice", "rights", "breach", "sdf"]
Severity = Literal["low", "medium", "high", "critical"]
Status = Literal["draft", "verified"]


class Check(BaseModel):
    field: str | list[str]
    condition: str


class Rule(BaseModel):
    id: str
    category: Category
    section_ref: str = Field(min_length=1)
    description: str
    check: Check
    severity: Severity
    remediation: str
    effective_from: date
    status: Status = "draft"


def load_rules(path: str | Path) -> list[Rule]:
    """Parse a YAML rule pack into validated Rule objects.

    Raises pydantic.ValidationError on any malformed rule (including a
    missing/blank section_ref) rather than silently skipping it.
    """
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return [Rule(**item) for item in raw["rules"]]
