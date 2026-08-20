"""Loads per-processor memory budgets from controller_budgets.yaml.

James (2026-08-20): the UI's budget denominator was hardcoded to a flat
4MB regardless of ProcessorType -- wrong, capacity is genuinely part-number
specific and, per Rockwell's own docs, some controller generations divide
memory into separate I/O vs. Data/Logic pools rather than one number. See
controller_budgets.yaml for full sourcing notes and confidence tagging.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

_DEFAULT_PATH = Path(__file__).with_name("controller_budgets.yaml")

UNIFIED = "unified"
DIVIDED = "divided"


@dataclass(frozen=True)
class ProcessorBudget:
    catalog_prefix: str
    architecture: str  # UNIFIED | DIVIDED
    confidence: str
    total_bytes: int | None = None  # set when architecture == UNIFIED
    data_logic_bytes: int | None = None  # set when architecture == DIVIDED
    io_bytes: int | None = None  # set when architecture == DIVIDED

    @property
    def display_total_bytes(self) -> int:
        """Single number for the UI's budget bar -- for divided-memory
        controllers this sums both pools, which is what's usually quoted
        as a model's "memory size" even though they're not fungible."""
        if self.architecture == UNIFIED:
            return self.total_bytes
        return self.data_logic_bytes + self.io_bytes


@dataclass(frozen=True)
class ControllerBudgetTable:
    entries: dict[str, ProcessorBudget]

    def lookup(self, processor_type: str | None) -> ProcessorBudget | None:
        """Matches by catalog PREFIX, longest match first, since L5X
        ProcessorType values carry suffix modifiers (motion/safety/
        conformal-coat, e.g. "1756-L81ES") that don't change the memory
        tier a part is built on."""
        if not processor_type:
            return None
        candidates = [
            budget for prefix, budget in self.entries.items()
            if processor_type.startswith(prefix)
        ]
        if not candidates:
            return None
        return max(candidates, key=lambda b: len(b.catalog_prefix))


def load_controller_budgets(path: str | Path | None = None) -> ControllerBudgetTable:
    path = Path(path) if path else _DEFAULT_PATH
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    default_architecture = raw.get("architecture", UNIFIED)
    entries = {}
    for prefix, v in raw["processors"].items():
        architecture = v.get("architecture", default_architecture)
        entries[prefix] = ProcessorBudget(
            catalog_prefix=prefix,
            architecture=architecture,
            confidence=v["confidence"],
            total_bytes=v.get("bytes"),
            data_logic_bytes=v.get("data_logic_bytes"),
            io_bytes=v.get("io_bytes"),
        )
    return ControllerBudgetTable(entries=entries)
