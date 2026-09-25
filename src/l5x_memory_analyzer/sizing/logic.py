"""Compiled logic size, from the fitted per-instruction weight table.

ESTIMATED, not exact, and every number this module produces must be flagged that
way in any output. L5X does not reveal how Logix compiles a rung to its internal
execution format, so these weights are regressed against real controller readings
rather than derived. See CLAUDE.md's ground-truth constraint.
"""

from __future__ import annotations

import re

from l5x_memory_analyzer.parser.logic import _DESTINATION_ARG, RoutineLogic
from l5x_memory_analyzer.sizing.constants import LogicInstructionModel

# A bare tag reference -- e.g. "TD0". The legacy resolution path, used only
# when a caller passes no operand_types (sizing/operand_types.py resolves every
# spelling; see memory_model.yaml operand_type_surcharge).
_BARE_TAG = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
# Literal operands (OQ-LITREAL): an integer literal is typed DINT and a float
# literal REAL when a call's operand types are mixed, so it pays the measured
# OQ-MIXEDTYPE conversion against a REAL or INT operand.
_INT_LITERAL = re.compile(r"^[-+]?\d+$")
_FLOAT_LITERAL = re.compile(r"^[-+]?(\d+\.\d*|\.\d+|\d+(\.\d*)?[eE][-+]?\d+)$")


def _operand_type(op: str, operand_types, literal_types: dict[str, str]) -> str | None:
    op = op.strip()
    if literal_types:
        if _INT_LITERAL.match(op):
            return literal_types.get("integer")
        if _FLOAT_LITERAL.match(op):
            return literal_types.get("float")
    return operand_types.resolve(op)

# Operand types that a REAL-destination CPT has to convert to float before
# it can evaluate (memory_model.yaml cpt_expression.real_dest). BOOL is
# deliberately absent -- no real corpus example of a BOOL operand inside a
# CPT expression exists to confirm it converts the same way, so it falls
# through uncharged rather than being guessed at.
# Integer operand types that cost a conversion in a REAL-destination CPT.
# LINT is deliberately ABSENT: cptrd_operand_lint, which is the
# all-REAL control with only the operand type swapped, measures 244/rung --
# byte-identical to that control. A LINT operand costs nothing extra, and
# charging it per_int_operand over-predicted that file by 26.79%.
_CPT_INTEGER_OPERAND_TYPES = frozenset({"SINT", "INT", "DINT"})

# Narrow integers, widened to DINT before evaluation --:
# "ints will use a behind the scenes conversion to dint". This is what makes
# SINT cost +256/rung against that same control while LINT costs nothing.
_CPT_NARROW_OPERAND_TYPES = frozenset({"SINT", "INT"})


_ATOMIC_TYPES = frozenset({
    "BOOL", "SINT", "INT", "DINT", "LINT", "USINT", "UINT", "UDINT", "ULINT",
    "REAL", "LREAL",
})


def resolve_arg_type(arg: str, tag_types: dict[str, str],
                     udt_members: dict[str, dict[str, str]] | None = None) -> str | None:
    """DataType of a call argument: the base tag's type, then each `.Member`
    step followed through the file's UDT definitions. An `[index]` on an array
    tag selects one element, whose type is the tag's type. None when a step
    cannot be followed."""
    arg = re.sub(r"\[[^\]]*\]", "", arg.strip())
    parts = arg.split(".")
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", parts[0]):
        return None
    current = tag_types.get(parts[0])
    for step in parts[1:]:
        if current is None or step.isdigit():
            return None
        current = (udt_members or {}).get(current, {}).get(step)
    return current


def is_structured(arg: str, tag_types: dict[str, str],
                  udt_members: dict[str, dict[str, str]] | None = None) -> bool:
    data_type = resolve_arg_type(arg, tag_types, udt_members)
    return bool(data_type) and data_type not in _ATOMIC_TYPES and data_type != "BIT"


def structured_arg_count(args, tag_types: dict[str, str],
                         udt_members: dict[str, dict[str, str]] | None = None) -> int:
    """How many of these call arguments are a whole structure or STRING -- a
    bare tag, an array element, or a member path whose type is non-atomic.
    `jsredge_in_member_*` measured a UDT member argument (`W.S0`) at exactly
    the rate of a bare UDT tag."""
    return sum(1 for arg in args if is_structured(arg, tag_types, udt_members))


def jsr_structured_call_bytes(routine, model, tag_types: dict[str, str],
                              udt_members: dict[str, dict[str, str]] | None = None) -> int:
    """Per-call cost of structured JSR arguments: each structured INPUT is
    copied in like COP (structured_arg_call_extra), each structured RETURN is
    copied back (structured_ret_call_extra). See memory_model.yaml
    jsr_param_cost."""
    total = 0
    for (_t, n_in, _m), (_t2, args) in zip(routine.jsr_calls, routine.jsr_call_args):
        total += model.structured_arg_call_extra * structured_arg_count(
            args[:n_in], tag_types, udt_members)
        total += model.structured_ret_call_extra * structured_arg_count(
            args[n_in:], tag_types, udt_members)
    return total


def _resolve_call_type(operands: list[str], tag_types: dict[str, str],
                       operand_types=None) -> str | None:
    """The first operand that resolves to a known bare-tag type -- every
    typesweep_* calibration file uses one uniform operand type per call,
    so "first resolvable operand" is sufficient to match that data; a call
    mixing genuinely different real operand types is unconfirmed territory
    (see memory_model.yaml), not something to guess at here.

    With `operand_types` (sizing/operand_types.py) every operand spelling is
    followed to its type -- member paths, array elements, aliases, the routine's
    own program scope, an AOI's own parameters -- because a member path costs
    what a plain tag of the same type costs (OQ-OPERANDSHAPE). The first operand
    that resolves still decides, as before."""
    if operand_types is not None:
        for operand in operands:
            resolved = operand_types.resolve(operand)
            if resolved is not None:
                return resolved
        return None
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
    operand_types=None,
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

    charge_shell=False (Task/Program/Routine shell decomposition,
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
    # priced by a separate real_dest model (wired) -- the integer
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
            has_narrow = any(
                tag_types.get(name) in _CPT_NARROW_OPERAND_TYPES
                for name in call.operand_names
            )
            total += model.cpt_expression.real_dest.cost_for(
                call.operators, n_int_operands, call.float_literals,
                model.cpt_expression.base_read, has_narrow,
            )
        else:
            total += model.cpt_expression.cost_for(call.operators)

    # Operand-type surcharge (OQ-OPERANDTYPE) -- additive on TOP of the
    # base DINT-rate weight already summed above via instruction_counts,
    # not a replacement for it (unlike CPT, every type-sensitive
    # instruction's own base weight is still correct and still applied).
    if tag_types or operand_types is not None:
        for mnemonic, operands in routine.typed_calls:
            if operand_types is not None:
                # A call mixing DINT with REAL or INT pays conversions
                # (OQ-MIXEDTYPE); any other shape keeps the first-operand rule.
                literal_types = model.operand_type_surcharge.literal_types
                types = [_operand_type(op, operand_types, literal_types) for op in operands]
                dest = _DESTINATION_ARG.get(mnemonic)
                dest_index = None if dest is None else dest % len(operands) if operands else None
                mixed = model.operand_type_surcharge.mixed_surcharge_for(mnemonic, types, dest_index)
                if mixed is not None:
                    total += mixed
                    continue
            resolved_type = _resolve_call_type(operands, tag_types or {}, operand_types)
            if resolved_type is not None:
                total += model.operand_type_surcharge.surcharge_for(mnemonic, resolved_type)

    # Indirect (tag-driven) array-index cost (OQ-INDIRECT) -- additive per
    # real bracket occurrence, on top of everything else above. See
    # memory_model.yaml indirect_index for the derivation.
    # What the index selects adds to that (OQ-INDIRECTUDT): a member after the
    # index, or an indexed BOOL / STRING element.
    for kind, array_path, follows in routine.indirect_index_sites:
        total += model.indirect_index.cost_for(kind)
        element_type = None
        if not follows:
            if operand_types is not None:
                element_type = operand_types.resolve(array_path)
            elif tag_types and _BARE_TAG.match(array_path):
                element_type = tag_types.get(array_path)
        total += model.indirect_index.element_cost_for(follows, element_type)

    # CMP compound-condition/float-literal surcharge -- additive on top of
    # the base CMP:76 weight already summed via instruction_counts above.
    # See memory_model.yaml cmp_surcharge for the derivation.
    #
    # a CMP whose operands are themselves ARITHMETIC expressions
    # is charged the same operator-tier cost CPT uses, minus CPT's own
    # base_read (CMP already carries its own 76-byte base weight). CMP and
    # CPT share one expression law -- the tier table that was fitted on CPT
    # lands on CMP's measured residuals without refitting anything. See
    # docs/OPEN_QUESTIONS.md OQ-CMPCPTLAYOUT for the per-shape table.
    for call in routine.cmp_calls:
        if call.is_compound:
            total += model.cmp_surcharge.compound_cost
        if call.has_float_literal:
            total += model.cmp_surcharge.float_literal_cost
        if call.operators:
            total += (model.cpt_expression.cost_for(call.operators)
                      - model.cpt_expression.base_read)

    # JSR per-param B(n_in) surcharge (OQ-JSRPARAMCOST) -- additive per real
    # call site, on top of the flat JSR:72/rung weight already summed via
    # instruction_counts above. The one-time A(n) cost (the callee's own
    # Parameters-block declaration) is charged separately, once per
    # distinct target routine, by report.py -- not here, since it isn't a
    # property of any one calling routine or call site. output_param_cost
    # (wired): the trailing return-value args a JSR call passes
    # back (`JSR(name, N_in, in_1..in_N, out_1..out_M)`) were completely
    # unmodeled until real jsr_mixedio_5in_2out/jsr_multiret_n04 capture
    # data (sat unreconciled) showed ~40/call for m=2 output
    # args, matching the SAME per-param rate as input args -- see
    # memory_model.yaml jsr_param_cost.
    for _target, n_in, m_out in routine.jsr_calls:
        total += (model.jsr_param_cost.b_cost(n_in, m_out)
                  + model.jsr_param_cost.output_param_cost * m_out)
    # Structured JSR arguments (COP-style copies) are charged by report.py,
    # which has the UDT member types needed to resolve a member-path argument;
    # see jsr_structured_call_bytes.

    # Branch-bracket cost (OQ-BRANCHDEPTH) -- additive per real BST/NXB/BND-
    # family instruction the parser found (parser/logic.py
    # _branch_bracket_instruction_count), on top of every leg's own
    # instruction weight already summed via instruction_counts above. See
    # memory_model.yaml logic_instructions.branch_bracket_cost_per_instruction
    # for the derivation.
    total += routine.branch_bracket_instruction_count * model.branch_bracket_cost_per_instruction

    # Every AOI call site (OQ-DEFSCALE). These cost nothing before
    # The instruction-count regex is all-caps-only and real AOI names are
    # mixed-case, so 3,918 real call sites were invisible. See memory_model.yaml
    # aoi_call_site -- 168 bytes, from a 1/5/20/60-call sweep whose four files
    # agree on one intercept, cross-checked against a second sweep over instance
    # count that returns the same number.
    total += (routine.aoi_call_count * model.aoi_call_site_bytes
              + routine.aoi_call_param_count * model.aoi_call_site_per_param_bytes
              + routine.aoi_call_input_ref_count * model.aoi_call_site_input_ref_extra_bytes)

    # OQ-SERIESOUTPUT, wired: every writing instruction beyond the
    # first in a rung costs 12 LESS than the sum of its own weights. Subtracted
    # once here rather than folded into any weight, because the weights are
    # correct for a one-output rung and it is the second output onward that is
    # cheap. Exact on all 16 srout_* rows across 8 output counts; invariant to
    # type, tag uniqueness and series-versus-branch. See memory_model.yaml
    # series_output.
    total -= routine.series_output_extras * model.series_output_extra_discount

    return total, model.confidence
