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

# Operand types that a REAL-destination CPT has to convert to float before
# it can evaluate (memory_model.yaml cpt_expression.real_dest). BOOL is
# deliberately absent -- no real corpus example of a BOOL operand inside a
# CPT expression exists to confirm it converts the same way, so it falls
# through uncharged rather than being guessed at.
_CPT_INTEGER_OPERAND_TYPES = frozenset({"SINT", "INT", "DINT", "LINT"})


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
    #
    # A CPT writing to a REAL destination is evaluated in floating point and
    # priced by a separate real_dest model (wired 2026-09-04) -- the integer
    # operator-tier costs above don't apply, and every non-float operand
    # carries a real conversion cost. Needs the file's tag types to tell a
    # REAL destination from an integer one, so a file whose types can't be
    # resolved (tag_types empty) keeps the integer path unchanged rather
    # than guessing.
    for call in routine.cpt_calls:
        dest_type = tag_types.get(call.dest) if tag_types else None
        if dest_type == "REAL":
            n_int_operands = call.int_literals + sum(
                1 for name in call.operand_names
                if tag_types.get(name) in _CPT_INTEGER_OPERAND_TYPES
            )
            total += model.cpt_expression.real_dest.cost_for(
                call.operators, n_int_operands, call.float_literals,
                model.cpt_expression.base_read,
            )
        else:
            total += model.cpt_expression.cost_for(call.operators)

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

    # JSR per-param B(n_in) surcharge (OQ-JSRPARAMCOST) -- additive per real
    # call site, on top of the flat JSR:72/rung weight already summed via
    # instruction_counts above. The one-time A(n) cost (the callee's own
    # Parameters-block declaration) is charged separately, once per
    # distinct target routine, by report.py -- not here, since it isn't a
    # property of any one calling routine or call site. output_param_cost
    # (wired 2026-08-29): the trailing return-value args a JSR call passes
    # back (`JSR(name, N_in, in_1..in_N, out_1..out_M)`) were completely
    # unmodeled until real jsr_mixedio_5in_2out/jsr_multiret_n04 capture
    # data (2026-08-23, sat unreconciled) showed ~40/call for m=2 output
    # args, matching the SAME per-param rate as input args -- see
    # memory_model.yaml jsr_param_cost.
    for _target, n_in, m_out in routine.jsr_calls:
        total += model.jsr_param_cost.b_cost(n_in) + model.jsr_param_cost.output_param_cost * m_out

    # Branch-bracket cost (OQ-BRANCHDEPTH) -- additive per real BST/NXB/BND-
    # family instruction the parser found (parser/logic.py
    # _branch_bracket_instruction_count), on top of every leg's own
    # instruction weight already summed via instruction_counts above. See
    # memory_model.yaml logic_instructions.branch_bracket_cost_per_instruction
    # for the derivation.
    total += routine.branch_bracket_instruction_count * model.branch_bracket_cost_per_instruction

    return total, model.confidence
