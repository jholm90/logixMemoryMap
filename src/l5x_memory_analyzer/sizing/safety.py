"""The safety partition (OQ-SAFETYPARTITION): what a safety controller's safety tags and
safety logic cost in the memory Capacity reports as safety used memory.

A separate number from the standard total in sizing/report.py, which already leaves
this content out. Laws and constants: memory_model.yaml safety_partition and
MEMORY_MODEL.md, "Safety memory is a separate partition".

  base           File > New's SafetyTask/SafetyProgram/MainRoutine, no rungs
  tags           controller scope Class="Safety": the data block only (its name entry
                 is standard memory); a safety program's tags: name entry + data block
  logic          each safety instruction its measured per-rung cost; any other
                 instruction its standard weight, ASSUMED until safe_std_*_r2 is read
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import replace

from l5x_memory_analyzer.parser.aoi import parse_aoi_definitions
from l5x_memory_analyzer.parser.datatypes import parse_data_types
from l5x_memory_analyzer.parser.logic import parse_rll_routines
from l5x_memory_analyzer.parser.tags import CONTROLLER_SCOPE, parse_tags
from l5x_memory_analyzer.sizing.confidence import weakest
from l5x_memory_analyzer.sizing.constants import MemoryModel
from l5x_memory_analyzer.sizing.logic import compute_routine_logic_bytes
from l5x_memory_analyzer.sizing.report import EXACT, ESTIMATED, SizeEntry, SizeError
from l5x_memory_analyzer.sizing.udt import RecursiveUdtError, UnknownDataTypeError, compute_array_size


def has_safety_partition(root: ET.Element) -> bool:
    """A project with a safety program has a safety partition to size."""
    return any(p.get("Class") == "Safety" for p in root.findall("Controller/Programs/Program"))


def build_safety_report(root: ET.Element, model: MemoryModel) -> tuple[list[SizeEntry], list[SizeError]]:
    """Every safety-partition line item, or nothing for a project without a safety program."""
    if not has_safety_partition(root):
        return [], []
    sp = model.safety_partition
    data_types = {**parse_data_types(root), **parse_aoi_definitions(root)}
    rows: list[tuple[str, str, str, int, str]] = [
        ("safety/base", "project_baseline", "", sp.base_bytes, sp.base_confidence)]
    errors: list[SizeError] = []

    for tag in parse_tags(root):
        if not tag.is_safety or tag.is_alias:
            continue
        try:
            data, basis = compute_array_size(tag.data_type, tag.dimensions, data_types, model)
        except (UnknownDataTypeError, RecursiveUdtError) as exc:
            errors.append(SizeError(path=tag.path, message=str(exc)))
            continue
        size = sp.data_block(data)
        if tag.scope == CONTROLLER_SCOPE:
            rows.append((tag.path, "controller_tag", tag.data_type, size, weakest(basis, sp.data_block_confidence)))
        else:
            size += model.alias_overhead.bytes_for(tag.name)
            rows.append((tag.path, "program_tag", tag.data_type, size, weakest(basis, sp.data_block_confidence)))

    safety_routines = [r for r in parse_rll_routines(root) if r.is_safety_program]
    for routine in safety_routines:
        own = {mn: c for mn, c in routine.instruction_counts.items() if mn in sp.rung_bytes}
        size = sum(sp.rung_bytes[mn] * c for mn, c in own.items())
        basis = "KNOWN"
        for mn in own:
            basis = weakest(basis, sp.rung_confidence(mn))
        ordinary = {mn: c for mn, c in routine.instruction_counts.items() if mn not in sp.rung_bytes}
        if ordinary:
            ordinary_bytes, _ = compute_routine_logic_bytes(
                replace(routine, instruction_counts=ordinary), model.logic_instructions, charge_shell=False)
            size += ordinary_bytes
            basis = weakest(basis, sp.ordinary_instruction_confidence)
        rows.append((routine.path, "routine_logic", "RLL", size, basis))
    if len(safety_routines) > 1:
        errors.append(SizeError(
            path="safety/base",
            message=(f"{len(safety_routines)} safety routines: the shell of each one past the first is not "
                     f"measured and is not charged (OQ-SAFETYPARTITION)."),
        ))

    total = sum(size for _, _, _, size, _ in rows)
    entries = [
        SizeEntry(path=path, category=category, data_type=data_type, bytes=size,
                  pct_of_total=(size / total * 100) if total else 0.0,
                  tier=ESTIMATED if category == "routine_logic" or basis != "KNOWN" else EXACT,
                  basis=basis)
        for path, category, data_type, size, basis in rows
    ]
    return entries, errors
