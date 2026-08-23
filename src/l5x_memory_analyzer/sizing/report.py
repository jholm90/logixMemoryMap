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

from l5x_memory_analyzer.parser.aoi import parse_aoi_definitions
from l5x_memory_analyzer.parser.datatypes import parse_data_types
from l5x_memory_analyzer.parser.logic import parse_rll_routines
from l5x_memory_analyzer.parser.tags import CONTROLLER_SCOPE, parse_tags
from l5x_memory_analyzer.sizing.confidence import weakest
from l5x_memory_analyzer.sizing.constants import MemoryModel
from l5x_memory_analyzer.sizing.logic import compute_routine_logic_bytes
from l5x_memory_analyzer.sizing.udt import (
    RecursiveUdtError,
    UnknownDataTypeError,
    compute_array_size,
    compute_udt_definition_cost,
    referenced_data_type_names,
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
    # Kept separate (not merged yet) so the udt_definition-cost pass below
    # can tell a real UDT from an AOI -- an AOI-typed tag still sizes
    # exactly like a UDT-typed one (merged dict below), but AOI *definition*
    # cost isn't a confirmed formula yet (see udt.py/report.py comments),
    # so only true UDTs get a definition-cost line item for now.
    udt_types = parse_data_types(root)
    aoi_types = parse_aoi_definitions(root)
    data_types = {**udt_types, **aoi_types}
    tags = parse_tags(root)

    sized: list[tuple[str, str, str, int, str]] = []
    errors: list[SizeError] = []
    # Every DECLARED UDT gets a definition-cost line, whether or not any
    # tag currently uses it -- confirmed real 2026-08-20/22 (the "def_only,
    # 0 instances" sweep specifically tests this: a UDT with zero tag
    # instances still shows a real nonzero Capacity delta from its
    # definition alone). Seeding with every udt_types key up front, not
    # just ones reachable from a tag, was a real gap caught 2026-08-22 by
    # cross-checking predictions against every real udt-category manifest
    # row -- every *_def_only row was silently predicting 0.
    referenced_udts: set[str] = set(udt_types)
    for tag in tags:
        category = "controller_tag" if tag.scope == CONTROLLER_SCOPE else "program_tag"
        if tag.is_alias:
            # An Alias tag is a pointer/rename onto another tag or module I/O
            # point -- it has no DataType of its own in the L5X. Real total
            # cost is OQ-ALIASSIZE, still open (test built, awaiting
            # capture) -- stays at 0 until that's confirmed, not tag_overhead
            # by assumption.
            sized.append((tag.path, category, "ALIAS", 0, "KNOWN"))
            continue
        try:
            size, basis = compute_array_size(tag.data_type, tag.dimensions, data_types, model)
        except (UnknownDataTypeError, RecursiveUdtError) as exc:
            errors.append(SizeError(path=tag.path, message=str(exc)))
            continue
        # tag_overhead is a per-Tag-entry cost additive with the tag's own
        # raw data size (RESOLVED_QUESTIONS.md OQ-TAGOVERHEAD) -- applies
        # regardless of data type, confirmed across atomic/UDT tags alike.
        overhead = model.tag_overhead.bytes_for(tag.name)
        size += overhead
        basis = weakest(basis, model.tag_overhead.confidence)
        sized.append((tag.path, category, tag.data_type, size, basis))
        referenced_udts |= referenced_data_type_names(tag.data_type, udt_types)

    definition_entries: list[tuple[str, str, str, int, str]] = []
    for name in sorted(referenced_udts):
        # Custom STRING types (Family="StringFamily") have their own
        # confirmed cost model (OQ-CUSTOMSTRING: total ~= maxlen + 302,
        # already fully captured by compute_udt_size's is_string_family
        # branch) -- the generic udt_definition formula was fit against
        # ordinary UDTs and doesn't apply. Applying it here was a real bug
        # caught 2026-08-22 (every customstring_* real data point was
        # over-predicted by a spurious ~224-228 blocks).
        if udt_types[name].is_string_family:
            # Custom STRING types get their own one-time definition cost
            # instead (OQ-CUSTOMSTRINGDEF, resolved 2026-08-23) -- the
            # ordinary udt_definition formula was fit against ordinary
            # UDTs and doesn't apply (confirmed: applying it over-predicted
            # every real customstring_* data point by ~224-228 blocks).
            definition_entries.append((
                f"udt_definitions/{name}", "udt_definition", name,
                model.string.custom_definition_cost, model.string.custom_definition_confidence,
            ))
            continue
        def_bytes, def_basis = compute_udt_definition_cost(name, udt_types, model)
        definition_entries.append((f"udt_definitions/{name}", "udt_definition", name, def_bytes, def_basis))

    # Compiled logic size -- ESTIMATED tier, never blurred with the EXACT
    # tag/UDT/AOI tier above (CLAUDE.md's ground-truth constraint: L5X
    # doesn't reveal how Logix compiles rungs, this is a fitted heuristic
    # model, not a formula derived from first principles). ST routines are
    # skipped entirely by parse_rll_routines, not estimated as if RLL.
    logic_entries: list[tuple[str, str, str, int, str]] = []
    for routine in parse_rll_routines(root):
        if routine.is_jsr_target:
            # Confirmed 2026-08-22 against real data: a JSR target routine's
            # own cost is already folded into the caller's
            # jsr_fixed_base_per_routine constant -- see RoutineLogic.
            # is_jsr_target's docstring. Emitting a separate entry here
            # would double-count it.
            continue
        logic_bytes, logic_basis = compute_routine_logic_bytes(routine, model.logic_instructions)
        logic_entries.append((routine.path, "routine_logic", "RLL", logic_bytes, logic_basis))

    # Fixed per-project overhead (controller/module/task/program scaffolding)
    # confirmed 2026-08-23 -- see memory_model.yaml empty_project_baseline
    # for the derivation (a literal, zero-variance 13,296-block gap between
    # every clean real Capacity reading and this engine's own total, across
    # 200+ independent real data points spanning wildly different
    # categories). Every real program has this cost regardless of content,
    # so it's emitted once per file, unconditionally.
    baseline_entry = ("project_baseline", "project_baseline", "PROJECT_BASELINE",
                       model.empty_project_baseline_bytes, model.empty_project_baseline_confidence)

    all_exact = sized + definition_entries + [baseline_entry]
    exact_total = sum(size for _, _, _, size, _ in all_exact)
    logic_total = sum(size for _, _, _, size, _ in logic_entries)
    total_bytes = exact_total + logic_total

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
        for path, category, data_type, size, basis in all_exact
    ] + [
        SizeEntry(
            path=path,
            category=category,
            data_type=data_type,
            bytes=size,
            pct_of_total=(size / total_bytes * 100) if total_bytes else 0.0,
            tier=ESTIMATED,
            basis=basis,
        )
        for path, category, data_type, size, basis in logic_entries
    ]
    return entries, errors
