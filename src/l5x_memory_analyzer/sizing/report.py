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
from l5x_memory_analyzer.parser.modules import parse_modules
from l5x_memory_analyzer.parser.tags import CONTROLLER_SCOPE, parse_tags
from l5x_memory_analyzer.parser.tasks import parse_tasks
from l5x_memory_analyzer.sizing.confidence import weakest
from l5x_memory_analyzer.sizing.constants import MemoryModel
from l5x_memory_analyzer.sizing.logic import compute_routine_logic_bytes
from l5x_memory_analyzer.sizing.udt import (
    RecursiveUdtError,
    UnknownDataTypeError,
    compute_aoi_definition_cost,
    compute_array_size,
    compute_udt_definition_cost,
    custom_string_maxlen,
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
    # AOI definitions seeded in too, 2026-08-26 (OQ-AOIDEF wiring) -- every
    # declared AOI, like every declared UDT, gets a definition-cost line
    # even with 0 tag instances (same real "def_only, 0 instances still
    # shows a nonzero Capacity delta" finding this seeding already exists
    # for UDTs above).
    referenced_udts: set[str] = set(udt_types) | set(aoi_types)
    for tag in tags:
        category = "controller_tag" if tag.scope == CONTROLLER_SCOPE else "program_tag"
        if tag.is_alias:
            # An Alias tag is a pointer/rename onto another tag or module I/O
            # point -- it has no DataType/data space of its own in the L5X,
            # only a tag-table entry. Real cost confirmed 2026-08-25
            # (OQ-ALIASSIZE, RESOLVED_QUESTIONS.md): same shape as ordinary
            # tag_overhead but with its own flat_base (56 vs 84).
            alias_bytes = model.alias_overhead.bytes_for(tag.name)
            sized.append((tag.path, category, "ALIAS", alias_bytes, model.alias_overhead.confidence))
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
        # Built-in STRING tags cost 2 bytes less than the flat tag_overhead
        # formula above predicts (RESOLVED_QUESTIONS.md OQ-STRINGTAGOVERHEAD)
        # -- confirmed KNOWN, not yet extended to custom StringFamily types.
        if tag.data_type == "STRING":
            size += model.string.builtin_tag_overhead_correction
            basis = weakest(basis, model.string.builtin_tag_overhead_correction_confidence)
        # Custom StringFamily-typed tags: no separate per-tag correction
        # needed -- compute_udt_size's nearest-8 DATA-padding rule (real
        # bug fix 2026-08-25) already produces the exact real byte count.
        # The mod4==1 bucket's own +8 one-time bonus is applied at the
        # definition-cost line item below, not here.
        elif tag.data_type in udt_types and udt_types[tag.data_type].is_string_family:
            basis = weakest(basis, model.string.custom_data_padding_confidence)
        sized.append((tag.path, category, tag.data_type, size, basis))
        referenced_udts |= referenced_data_type_names(tag.data_type, data_types)

    definition_entries: list[tuple[str, str, str, int, str]] = []
    for name in sorted(referenced_udts):
        # Custom STRING types (Family="StringFamily") have their own
        # confirmed cost model (OQ-CUSTOMSTRING: total ~= maxlen + 302,
        # already fully captured by compute_udt_size's is_string_family
        # branch) -- the generic udt_definition formula was fit against
        # ordinary UDTs and doesn't apply. Applying it here was a real bug
        # caught 2026-08-22 (every customstring_* real data point was
        # over-predicted by a spurious ~224-228 blocks).
        if name in aoi_types:
            # AOI definition cost, wired 2026-08-26 (OQ-AOIDEF) -- FITTED,
            # not KNOWN, see memory_model.yaml aoi_definition for the real
            # limitation (DINT-rate confirmed exact, BOOL/LINT-heavy AOIs
            # under-predicted). Checked before the udt_types string-family
            # branch below since an AOI name is never also a udt_types key.
            def_bytes, def_basis = compute_aoi_definition_cost(name, data_types, model)
            definition_entries.append((
                f"udt_definitions/{name}", "udt_definition", name, def_bytes, def_basis,
            ))
            continue
        if udt_types[name].is_string_family:
            # Custom STRING types get their own one-time definition cost
            # instead (OQ-CUSTOMSTRINGDEF, resolved 2026-08-23) -- the
            # ordinary udt_definition formula was fit against ordinary
            # UDTs and doesn't apply (confirmed: applying it over-predicted
            # every real customstring_* data point by ~224-228 blocks).
            # maxlen mod 4 == 1 gets an extra +8 one-time definition-cost
            # bonus, confirmed 2026-08-25 (3/3 real points exact: 49, 101,
            # 501) -- paired with the "no per-tag correction" branch above.
            # The base itself depends on the TYPE's own name length --
            # SOLVED 2026-08-26, a clean step function, see
            # memory_model.yaml's custom_definition_base for the
            # derivation.
            def_cost = model.string.custom_definition_cost_for(len(name))
            if custom_string_maxlen(udt_types[name]) % 4 == 1:
                def_cost += model.string.custom_mod4eq1_definition_bonus
            definition_entries.append((
                f"udt_definitions/{name}", "udt_definition", name,
                def_cost, model.string.custom_definition_confidence,
            ))
            continue
        def_bytes, def_basis = compute_udt_definition_cost(name, udt_types, model)
        definition_entries.append((f"udt_definitions/{name}", "udt_definition", name, def_bytes, def_basis))

    # Compiled logic size -- ESTIMATED tier, never blurred with the EXACT
    # tag/UDT/AOI tier above (CLAUDE.md's ground-truth constraint: L5X
    # doesn't reveal how Logix compiles rungs, this is a fitted heuristic
    # model, not a formula derived from first principles). ST routines are
    # skipped entirely by parse_rll_routines, not estimated as if RLL.
    # Bare tag name -> DataType, for the operand-type surcharge
    # (OQ-OPERANDTYPE) to resolve a type-sensitive instruction's operands
    # against. Deliberately GLOBAL (controller-scope + every program's
    # tags merged by bare name, last one wins on a collision) rather than
    # scoped per-routine's own program -- a real simplification, not
    # something confirmed safe: two different programs each declaring
    # their own same-named tag of different types would resolve to
    # whichever one this dict saw last, not necessarily the one the
    # routine doing the actual instruction call can see. None of this
    # project's real calibration data exercises that collision, so it's
    # untested territory, not a guessed-away one -- flagged here rather
    # than silently assumed correct.
    tag_types = {t.name: t.data_type for t in tags if t.data_type}

    logic_entries: list[tuple[str, str, str, int, str]] = []
    n_plain_routines = 0
    for routine in parse_rll_routines(root):
        if routine.is_jsr_target:
            # Confirmed 2026-08-22 against real data: a JSR target routine's
            # own cost is already folded into the caller's
            # jsr_fixed_base_per_routine constant -- see RoutineLogic.
            # is_jsr_target's docstring. Emitting a separate entry here
            # would double-count it.
            continue
        # 2026-08-27, Task/Program/Routine shell decomposition (OQ-
        # TASKOVERHEAD, see memory_model.yaml task_program_overhead): a
        # JSR-caller routine keeps paying its own jsr_fixed_base_per_routine
        # here, unchanged from before this fix -- that pathway is
        # separately validated and untouched. A PLAIN routine (no JSR
        # involvement at all) no longer pays fixed_base_per_routine per
        # routine; the shell entry built below charges it once for the
        # whole file plus the real per-extra-Task/Program/routine marginal
        # costs instead.
        is_plain = "JSR" not in routine.instruction_counts
        if is_plain:
            n_plain_routines += 1
        logic_bytes, logic_basis = compute_routine_logic_bytes(
            routine, model.logic_instructions, tag_types, charge_shell=not is_plain
        )
        logic_entries.append((routine.path, "routine_logic", "RLL", logic_bytes, logic_basis))

    if n_plain_routines > 0:
        # See memory_model.yaml task_program_overhead for the full
        # derivation (5 real files, exact/near-exact). Untouched when
        # n_plain_routines == 0 -- a file whose only routines are JSR
        # callers/targets already has its shell fully accounted for by
        # jsr_fixed_base_per_routine above, adding this would double it.
        n_tasks = max(len(parse_tasks(root)), 1)
        programs_el = root.find("Controller/Programs")
        n_programs = max(len(programs_el.findall("Program")), 1) if programs_el is not None else 1
        overhead = model.logic_instructions.task_program_overhead
        shell_bytes = (
            model.logic_instructions.fixed_base_per_routine
            + overhead.task_extra * (n_tasks - 1)
            + overhead.program_extra * (n_programs - 1)
            + overhead.routine_extra * (n_plain_routines - 1)
        )
        shell_basis = weakest(model.logic_instructions.confidence, overhead.confidence)
        # Own category, NOT "routine_logic" -- this entry's path is
        # "task_program_shell", not a "program:X/Y" routine path, so it
        # can't go through hierarchy.py's per-program routine grouping (same
        # class of bug already fixed once for project_baseline/udt_definition,
        # see hierarchy.py's NON_TAG_GROUPS comment). Still ESTIMATED tier
        # (it's part of the same fitted structural-logic estimate as every
        # other routine_logic entry, just not attributable to one routine).
        logic_entries.append(
            ("task_program_shell", "task_program_shell", "SHELL", shell_bytes, shell_basis)
        )

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

    # Module I/O connection/config data (2026-08-27, first pass -- see
    # parser/modules.py docstring). Real corpus inspection confirmed L5X
    # itself states each Connection's InputSize/OutputSize and each
    # ConfigTag's ConfigSize in bytes directly -- unlike every other
    # category here, the RAW size isn't fitted, it's read straight off the
    # export. But whether that raw byte count maps 1:1 onto controller
    # Capacity-tab memory, or (like every other category in this project)
    # carries its own real per-module/per-connection overhead on top, is
    # not yet confirmed against real capture data -- so these are
    # deliberately NOT summed into total_bytes/entries, only surfaced as
    # informational SizeErrors (same non-summed treatment AXIS_CIP_DRIVE/
    # MOTION_GROUP got before their own real formulas were derived), so a
    # user can see modules exist and their stated raw sizes without this
    # engine silently claiming a controller-memory number it hasn't earned.
    for module in parse_modules(root):
        if module.stated_total_bytes == 0:
            continue
        label = module.name or module.catalog_number
        display = f"{module.name} ({module.catalog_number})" if module.name else module.catalog_number
        errors.append(SizeError(
            path=f"modules/{label}",
            message=(
                f"Module {display}: L5X states "
                f"{module.connection_input_bytes} input + {module.connection_output_bytes} "
                f"output connection bytes + {module.config_bytes} config bytes = "
                f"{module.stated_total_bytes} stated total -- controller-memory cost not yet "
                f"confirmed against real Capacity data, not included in the total above"
            ),
        ))

    return entries, errors
