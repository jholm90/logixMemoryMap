"""Estimated (not exact -- see CLAUDE.md's ground-truth constraint) compiled
logic size, from the fitted per-instruction weight table.
"""

from __future__ import annotations

import re

from l5x_memory_analyzer.parser.logic import RoutineLogic
from l5x_memory_analyzer.sizing.constants import LogicInstructionModel

# A bare tag reference -- e.g. "TD0", not "Tag.Member" or "Tag[0]" or a
# literal. Only this shape resolves against tag_types below (OQ-OPERANDTYPE
# deliberately doesn't guess member/array-index/literal operand types --
# see memory_model.yaml operand_type_surcharge for why).
_BARE_TAG = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _resolve_call_type(operands: list[str], tag_types: dict[str, str]) -> str | None:
    """The first operand that resolves to a known bare-tag type -- every
    typesweep_* calibration file uses one uniform operand type per call,
    so "first resolvable operand" is sufficient to match that data; a call
    mixing genuinely different real operand types is unconfirmed territory
    (see memory_model.yaml), not something to guess at here."""
    for operand in operands:
        if _BARE_TAG.match(operand):
            resolved = tag_types.get(operand)
            if resolved is not None:
                return resolved
    return None


def compute_routine_logic_bytes(
    routine: RoutineLogic,
    model: LogicInstructionModel,
    tag_types: dict[str, str] | None = None,
    charge_shell: bool = True,
) -> tuple[int, str]:
    """Sum of every recognized instruction's weight × its occurrence count
    in this routine, plus (if charge_shell) the routine's fixed base cost.
    Unrecognized mnemonics (an instruction not yet in the weight table, or
    an AOI/UDT instance call -- same call syntax as a built-in instruction
    in real rung text) are silently skipped, not guessed at or crashed on.

    tag_types (bare tag name -> DataType, from report.py's already-parsed
    tag table) is optional so existing callers that don't need the
    operand-type surcharge (e.g. isolated unit tests) don't have to supply
    it -- resolution just silently finds nothing and no surcharge applies,
    same as before this feature existed.

    charge_shell=False (2026-08-27, Task/Program/Routine shell decomposition,
    see memory_model.yaml task_program_overhead): a PLAIN routine (no JSR
    involvement) no longer pays its own fixed_base_per_routine here --
    report.py charges that shell exactly once per file instead, plus the
    real per-extra-Task/Program/routine marginal costs, to avoid
    over-charging a multi-routine file the old flat per-routine shell. A
    JSR-caller routine is unaffected: report.py always calls this with
    charge_shell=True for those, same jsr_fixed_base_per_routine as before
    this fix -- that pathway is separately validated and untouched."""
    has_jsr = "JSR" in routine.instruction_counts
    fixed_base = (model.jsr_fixed_base_per_routine if has_jsr else model.fixed_base_per_routine) if charge_shell else 0

    total = fixed_base
    for mnemonic, count in routine.instruction_counts.items():
        weight = model.weights.get(mnemonic)
        if weight is not None:
            total += weight * count

    # CPT costed per-call from its own expression's operators, not the flat
    # per-mnemonic weights table above (OQ-CMPCPTLAYOUT, real data: CPT's
    # cost is expression-complexity-dependent) -- see memory_model.yaml
    # cpt_expression for the derivation. "CPT" is deliberately absent from
    # `weights` now, so the loop above never double-counts it.
    for operators in routine.cpt_calls:
        total += model.cpt_expression.cost_for(operators)

    # Operand-type surcharge (OQ-OPERANDTYPE) -- additive on TOP of the
    # base DINT-rate weight already summed above via instruction_counts,
    # not a replacement for it (unlike CPT, every type-sensitive
    # instruction's own base weight is still correct and still applied).
    if tag_types:
        for mnemonic, operands in routine.typed_calls:
            resolved_type = _resolve_call_type(operands, tag_types)
            if resolved_type is not None:
                total += model.operand_type_surcharge.surcharge_for(mnemonic, resolved_type)

    # Indirect (tag-driven) array-index cost (OQ-INDIRECT) -- additive per
    # real bracket occurrence, on top of everything else above. See
    # memory_model.yaml indirect_index for the derivation.
    for kind in routine.indirect_index_kinds:
        total += model.indirect_index.cost_for(kind)

    # CMP compound-condition/float-literal surcharge -- additive on top of
    # the base CMP:76 weight already summed via instruction_counts above.
    # See memory_model.yaml cmp_surcharge for the derivation.
    for is_compound, has_float_literal in routine.cmp_calls:
        if is_compound:
            total += model.cmp_surcharge.compound_cost
        if has_float_literal:
            total += model.cmp_surcharge.float_literal_cost

    return total, model.confidence
