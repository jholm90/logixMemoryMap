"""Flat {path, category, bytes, pct_of_total, tier, basis} report -- the data
contract the UI (Phase 2+) will consume.

Two separate confidence concepts, kept deliberately distinct per CLAUDE.md's
ground-truth constraint:
  - tier: "exact" (tag/UDT/AOI data space) vs "estimated" (compiled logic,
    not implemented until Phase 4+) -- the big one, never to be blurred.
  - basis: the weakest MEMORY_MODEL.md confidence tag (KNOWN/ASSUMED/FITTED/
    UNKNOWN) that went into this number -- fine-grained provenance within
    the "exact" tier, for whether a given constant is still pending Phase 3
    validation.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass

from l5x_memory_analyzer.parser.datatypes import parse_data_types
from l5x_memory_analyzer.parser.tags import CONTROLLER_SCOPE, parse_tags
from l5x_memory_analyzer.sizing.constants import MemoryModel
from l5x_memory_analyzer.sizing.udt import (
    RecursiveUdtError,
    UnknownDataTypeError,
    compute_array_size,
)

EXACT = "exact"
ESTIMATED = "estimated"


@dataclass(frozen=True)
class SizeEntry:
    path: str
    category: str  # "controller_tag" | "program_tag"
    data_type: str
    bytes: int
    pct_of_total: float
    tier: str  # EXACT | ESTIMATED
    basis: str  # KNOWN | ASSUMED | FITTED | UNKNOWN


@dataclass(frozen=True)
class SizeError:
    path: str
    message: str


def build_report(root: ET.Element, model: MemoryModel) -> tuple[list[SizeEntry], list[SizeError]]:
    data_types = parse_data_types(root)
    tags = parse_tags(root)

    sized: list[tuple[str, str, str, int, str]] = []
    errors: list[SizeError] = []
    for tag in tags:
        category = "controller_tag" if tag.scope == CONTROLLER_SCOPE else "program_tag"
        try:
            size, basis = compute_array_size(tag.data_type, tag.dimensions, data_types, model)
        except (UnknownDataTypeError, RecursiveUdtError) as exc:
            errors.append(SizeError(path=tag.path, message=str(exc)))
            continue
        sized.append((tag.path, category, tag.data_type, size, basis))

    total_bytes = sum(size for _, _, _, size, _ in sized)
    entries = [
        SizeEntry(
            path=path,
            category=category,
            data_type=data_type,
            bytes=size,
            pct_of_total=(size / total_bytes * 100) if total_bytes else 0.0,
            tier=EXACT,
            basis=basis,
        )
        for path, category, data_type, size, basis in sized
    ]
    return entries, errors
