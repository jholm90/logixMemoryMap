"""The safety partition (OQ-SAFETYPARTITION): what a safety controller's safety tags and
safety logic cost in the memory Capacity reports as safety used memory.

A separate number from the standard total in sizing/report.py, which already leaves
this content out. Laws and constants: memory_model.yaml safety_partition and
MEMORY_MODEL.md, "Safety memory is a separate partition".

  base           File > New's SafetyTask/SafetyProgram/MainRoutine, no rungs
  tags           controller scope Class="Safety": the data block only (its name entry
                 is standard memory); a safety program's tags: name entry + data block;
                 an alias in a safety program: its name entry
  shells         each safety program and routine beyond the first
  logic          each safety instruction its measured per-rung cost; any other its
                 standard engine cost plus a cost per tag operand
  AOIs           a safety AOI's logic and its moved definition share, and its calls; one
                 exported encoded (sealed, safety-locked) from its visible parameters
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import replace

from l5x_memory_analyzer.parser.aoi import parse_aoi_definitions
from l5x_memory_analyzer.parser.datatypes import parse_data_types
from l5x_memory_analyzer.parser.logic import parse_rll_routines
from l5x_memory_analyzer.parser.protected import add_protected_aoi_standins, protected_aoi_elements
from l5x_memory_analyzer.parser.tags import CONTROLLER_SCOPE, parse_tags
from l5x_memory_analyzer.sizing.confidence import weakest
from l5x_memory_analyzer.sizing.constants import MemoryModel
from l5x_memory_analyzer.sizing.logic import compute_routine_logic_bytes
from l5x_memory_analyzer.sizing.operand_types import FileOperandTypes
from l5x_memory_analyzer.sizing.report import EXACT, ESTIMATED, SizeEntry, SizeError, build_report
from l5x_memory_analyzer.sizing.udt import RecursiveUdtError, UnknownDataTypeError, compute_array_size


def has_safety_partition(root: ET.Element) -> bool:
    """A project with a safety program has a safety partition to size."""
    return any(p.get("Class") == "Safety" for p in root.findall("Controller/Programs/Program"))


def build_safety_report(root: ET.Element, model: MemoryModel) -> tuple[list[SizeEntry], list[SizeError]]:
    """Every safety-partition line item, or nothing for a project without a safety program."""
    if not has_safety_partition(root):
        return [], []
    sp = model.safety_partition
    # A protected AOI's stand-in (its visible parameters) lets its instances and calls
    # be priced; idempotent, so the standard pass finds it already in place.
    add_protected_aoi_standins(root)
    data_types = {**parse_data_types(root), **parse_aoi_definitions(root)}
    tags = parse_tags(root)
    rows: list[tuple[str, str, str, int, str]] = [
        ("safety/base", "project_baseline", "", sp.base_bytes, sp.base_confidence)]
    errors: list[SizeError] = []

    # Tags: a name entry and a data block, split by scope (the controller-scope name
    # entry is standard memory and priced by report.py); an alias is its name entry.
    for tag in tags:
        if not tag.is_safety:
            continue
        if tag.is_alias:
            if tag.scope != CONTROLLER_SCOPE:
                rows.append((tag.path, "program_tag", "ALIAS", model.alias_overhead.bytes_for(tag.name),
                             model.alias_overhead.confidence))
            continue
        try:
            data, basis = compute_array_size(tag.data_type, tag.dimensions, data_types, model)
        except (UnknownDataTypeError, RecursiveUdtError) as exc:
            errors.append(SizeError(path=tag.path, message=str(exc)))
            continue
        tag_def = data_types.get(tag.data_type)
        if tag_def is not None and tag_def.is_aoi and not tag.dimensions:
            data += model.aoi_instance_extra
        size = sp.data_block(data, is_array=bool(tag.dimensions))
        basis = weakest(basis, sp.data_block_confidence)
        if tag.scope == CONTROLLER_SCOPE:
            rows.append((tag.path, "controller_tag", tag.data_type, size, basis))
        else:
            rows.append((tag.path, "program_tag", tag.data_type,
                         size + model.alias_overhead.bytes_for(tag.name), basis))

    # Shells: the first safety program and its MainRoutine are inside the base.
    safety_programs = [p for p in root.findall("Controller/Programs/Program") if p.get("Class") == "Safety"]
    safety_routines = [r for r in parse_rll_routines(root) if r.is_safety_program]
    if len(safety_programs) > 1:
        rows.append(("safety/programs", "task_program_shell", "", sp.program_bytes * (len(safety_programs) - 1),
                     sp.shell_confidence))
    first = safety_programs[0] if safety_programs else None
    extra_routines = [r for r in safety_routines
                      if not (first is not None and r.program_name == first.get("Name")
                              and r.routine_name == first.get("MainRoutineName"))]
    if extra_routines:
        rows.append(("safety/routines", "task_program_shell", "",
                     sum(sp.routine_shell(r.routine_name or "") for r in extra_routines),
                     weakest(sp.shell_confidence, sp.routine_name_confidence)))

    # Logic: a safety instruction its measured rung cost; any other its standard engine
    # cost plus a cost per tag operand.
    tag_types = {t.name: t.data_type for t in tags if t.data_type}
    operand_types = FileOperandTypes(root)
    controller_names = {t.name for t in tags if t.scope == CONTROLLER_SCOPE}
    program_names: dict[str, set[str]] = {}
    for t in tags:
        if t.scope != CONTROLLER_SCOPE:
            program_names.setdefault(t.scope[len("program:"):], set()).add(t.name)
    calls_an_aoi = False
    for routine in safety_routines:
        own = {mn: c for mn, c in routine.instruction_counts.items() if mn in sp.rung_bytes}
        size = sum(sp.rung_bytes[mn] * c for mn, c in own.items())
        basis = "KNOWN"
        for mn in own:
            basis = weakest(basis, sp.rung_confidence(mn))
        ordinary = {mn: c for mn, c in routine.instruction_counts.items() if mn not in sp.rung_bytes}
        if ordinary or routine.aoi_call_count:
            std, std_basis = compute_routine_logic_bytes(
                replace(routine, instruction_counts=ordinary), model.logic_instructions, tag_types,
                charge_shell=False, operand_types=operand_types.for_program(routine.program_name))
            names = controller_names | program_names.get(routine.program_name or "", set())
            size += std + sum(sp.operand_cost(kind) for mn, root_name, kind in routine.operand_refs
                              if mn not in sp.rung_bytes and root_name in names)
            basis = weakest(basis, weakest(std_basis, sp.ordinary_instruction_confidence))
            delta = sum(sp.ordinary_delta_bytes.get(mn, 0) * c for mn, c in ordinary.items())
            if delta:
                size += delta
                basis = weakest(basis, sp.ordinary_delta_confidence)
            if routine.aoi_call_count:
                size += sp.aoi_call_extra_bytes * routine.aoi_call_count
                basis = weakest(basis, sp.aoi_confidence)
                calls_an_aoi = True
        rows.append((routine.path, "routine_logic", "RLL", size, basis))
    if calls_an_aoi:
        rows.append(("safety/aoi_call_routine", "routine_logic", "RLL",
                     model.structured_text.st_aoi_call_routine_bytes, sp.aoi_confidence))

    # Safety AOIs: the standard pass prices them whole and hands over the safety share.
    if any(a.get("Class") == "Safety" for a in root.iter("AddOnInstructionDefinition")):
        out: dict = {}
        build_report(root, model, safety_out=out)
        protected = {e.get("Name") for e in protected_aoi_elements(root)}
        for name, (moved, logic, basis) in sorted(out.get("aoi", {}).items()):
            rows.append((f"aoi_definitions/{name}", "udt_definition", name, moved, basis))
            rows.append((f"aoi_definitions/{name}/Logic", "routine_logic", "RLL", logic, basis))
            if name in protected:
                errors.append(SizeError(
                    path=f"aoi_definitions/{name}",
                    message=(f"Safety AOI {name} is exported encoded (sealed or safety-locked): its logic is "
                             f"not readable and is priced at a minimum, so the safety figure is a minimum "
                             f"for it (OQ-SAFETYPARTITION)."),
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
