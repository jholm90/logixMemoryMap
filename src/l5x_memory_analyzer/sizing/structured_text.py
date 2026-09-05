"""Structured Text routine sizing.

Until 2026-09-04 ST contributed exactly ZERO to every prediction:
`parse_rll_routines` filters to RLL, and nothing else looked at an ST
routine. That is not a small hole -- across the 23 real files in
samples/local/ there are 297 ST routines and 24,017 ST lines, and one real
program (AccuTally) carries 1,894 ST lines across 10 ST routines.

The `realscale_st_*` / `st_*` capture batch settled the cost model, and the
headline result is that ST is NOT a separate cost universe:

  **An instruction inside ST costs exactly what the same instruction costs
  in a rung.** Four pairs were built operand-for-operand identical, ST
  against RLL, and every pair came back separated by exactly +432 -- the
  one-time ST routine shell -- with no per-instruction difference at all:

      st_instr_cop_n01000       135,376   instr_cop_n01000     134,944   +432
      st_instr_dtos_n01000       95,376   instr_dtos_n01000     94,944   +432
      st_instr_size_n01000      151,376   instr_size_n01000    150,944   +432
      st_expr_cpt_mirror_n01000 475,376   instr_cpt_n01000     474,944   +432

  The last pair matters most: it means the tier-aware CPT expression model
  transfers to an ST arithmetic assignment unchanged, rather than needing a
  parallel ST expression parser.

So this module deliberately does NOT re-price instructions. It charges the
ST-specific part only -- routine shell, per statement, per control-flow
construct -- and hands any instruction-style call found in the text back to
the SAME weight table the rung sizer uses.

Comments and blank lines are FREE, which was James's explicit question
(2026-09-04: *"one thing not modelled is st comments and if a comment line
or block takes up data memory or is like tag and rung comments and does not
count towards data usage"*). Answer: they do not count, and it was worth
testing rather than assuming -- an RLL rung comment is a separate <Comment>
element beside the logic, whereas an ST comment lives inside the routine's
own compiled source CDATA, so the RLL result genuinely did not transfer.
Five variants against the same 100 executable statements all landed
byte-identical on 27,376, equal to the no-comment control:

    100 short leading //     100 long leading // (110 chars)
    400 short leading //     100 trailing //  (zero added lines)
    400 genuinely blank lines

Comment COUNT, comment LENGTH, leading vs trailing, and blank lines are all
free.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

from l5x_memory_analyzer.parser.logic import CptCall, routine_language

# A line is comment-only/blank if, once a trailing "// ..." or a whole
# "(* ... *)" is stripped, nothing executable remains.
_LINE_COMMENT = re.compile(r"//.*$")
_BLOCK_COMMENT = re.compile(r"\(\*.*?\*\)", re.DOTALL)

# Control-flow keywords, counted on the code with comments already removed
# so a keyword mentioned inside a comment is never charged.
_IF = re.compile(r"\bIF\b", re.I)
_ELSIF = re.compile(r"\bELSIF\b", re.I)
_CASE = re.compile(r"\bCASE\b", re.I)
_FOR = re.compile(r"\bFOR\b", re.I)
_WHILE = re.compile(r"\bWHILE\b", re.I)
# A CASE selector is "<literal or range> :" at the start of a line -- ":="
# is an assignment and must not match, hence the negative lookahead.
_CASE_SELECTOR = re.compile(r"^\s*[\w.,\s]+:(?!=)", re.M)
# An ASSIGNMENT statement: "<lhs> := <rhs>;". Counting these rather than
# counting ";" terminators is deliberate and was a real bug when first
# written the naive way: END_IF; END_FOR; END_WHILE; END_CASE; all end in a
# semicolon too, so terminator-counting charged st_ctl_if 200 statements
# instead of 100 and over-predicted it by 12.40%. A block terminator is not
# a statement -- the construct it closes is already charged by its own
# if_block/for_block/while_block/case_block term.
_ASSIGNMENT = re.compile(r"(?P<lhs>[A-Za-z_][\w.\[\]]*)\s*:=\s*(?P<rhs>[^;]*);")
# A right-hand side that is nothing but a numeric/boolean literal.
_BARE_LITERAL_RHS = re.compile(r"^\s*(?:-?\d+(?:\.\d+)?|TRUE|FALSE)\s*$", re.I)
_OPERATOR_TOKEN = re.compile(r"\*\*|[+\-*/]|\bMOD\b|\bAND\b|\bOR\b|\bXOR\b", re.I)
_IDENT = re.compile(r"[A-Za-z_][\w.]*")
_NUMBER = re.compile(r"\d+\.\d+|\d+")


@dataclass
class StructuredTextRoutine:
    program_name: str
    routine_name: str
    statements: int = 0
    literal_statements: int = 0
    # One CptCall per assignment with a non-trivial right-hand side. An ST
    # assignment IS a CPT on its RHS -- see the module docstring's
    # st_expr_cpt_mirror pair -- so these go through the very same
    # tier-aware CPT expression model, rather than a parallel ST one.
    cpt_calls: list = field(default_factory=list)
    if_blocks: int = 0
    elsif_branches: int = 0
    case_selectors: int = 0
    for_blocks: int = 0
    while_blocks: int = 0
    instruction_counts: dict[str, int] = field(default_factory=dict)
    # Executable text with comments stripped, for the caller to hand to the
    # shared instruction/CPT sizer -- ST does not re-price instructions.
    code_text: str = ""


def strip_comments(text: str) -> str:
    """Removes (* block *) and // line comments, leaving executable code.

    Done before any counting so that a keyword or ";" inside a comment is
    never charged -- 29% of real ST lines are comments, so this is not a
    corner case."""
    text = _BLOCK_COMMENT.sub(" ", text)
    return "\n".join(_LINE_COMMENT.sub("", line) for line in text.splitlines())


def parse_st_routines(root: ET.Element) -> list[StructuredTextRoutine]:
    """Every ST routine in the file -- inside Programs AND inside AOIs.

    The AOI half was missed in the first wiring (2026-09-04) and James
    caught it immediately: "most of the st code is inside AOIs". Measured
    across the real corpus, 1,513 of 4,103 real ST lines -- **37%** -- live
    inside an AddOnInstructionDefinition rather than a Program, and all of
    them contributed exactly zero.
    """
    routines: list[StructuredTextRoutine] = []
    owners: list[tuple[str, ET.Element]] = []

    programs_el = root.find("Controller/Programs")
    if programs_el is not None:
        for program_el in programs_el.findall("Program"):
            owners.append((program_el.get("Name") or "?", program_el))

    # AOI internal routines. Named "aoi:<Name>" so the report path cannot
    # collide with a real Program of the same name, and so an ST routine's
    # cost is attributable to the definition it belongs to.
    for aoi_el in root.iter("AddOnInstructionDefinition"):
        owners.append((f"aoi:{aoi_el.get('Name') or '?'}", aoi_el))

    for program_name, owner_el in owners:
        routines_el = owner_el.find("Routines")
        if routines_el is None:
            continue
        for routine_el in routines_el.findall("Routine"):
            if routine_language(routine_el) != "ST":
                continue
            st = routine_el.find("STContent")
            raw = "\n".join(
                (line.text or "") for line in (st.iter("Line") if st is not None else [])
            )
            code = strip_comments(raw)
            assignments = list(_ASSIGNMENT.finditer(code))
            literal = [a for a in assignments if _BARE_LITERAL_RHS.match(a.group("rhs"))]
            routines.append(StructuredTextRoutine(
                program_name=program_name,
                routine_name=routine_el.get("Name") or "?",
                statements=len(assignments),
                literal_statements=len(literal),
                # EVERY assignment, literal-RHS included -- a bare literal
                # is simply the 0-operator shape in the measured table, so
                # it needs no special case here.
                cpt_calls=[
                    _cpt_call_for(a.group("lhs"), a.group("rhs"))
                    for a in assignments
                ],
                if_blocks=len(_IF.findall(code)),
                elsif_branches=len(_ELSIF.findall(code)),
                case_selectors=len(_CASE_SELECTOR.findall(code)),
                for_blocks=len(_FOR.findall(code)),
                while_blocks=len(_WHILE.findall(code)),
                code_text=code,
            ))
    return routines


def size_st_assignments(routine: StructuredTextRoutine, model, tag_types=None):
    """Cost of every assignment in the routine, plus the shapes we cannot price.

    Returns (bytes, unmeasured_shapes) where unmeasured_shapes lists
    "<n_operators>|<dest_is_real>" keys this routine used that the measured
    table does not cover. Those fall back to the CPT model, which is known
    to be wrong for at least the 1-operator cases, so the caller surfaces
    them as a coverage gap rather than letting a bad number pass silently.
    """
    st = model.structured_text
    total = 0
    unmeasured: list[str] = []
    for call in routine.cpt_calls:
        dest_is_real = bool(tag_types) and tag_types.get(call.dest) == "REAL"
        measured = st.assignment_cost(len(call.operators), dest_is_real)
        if measured is not None:
            total += measured
        else:
            # Fall back to the RLL CPT model. It is known to be wrong for
            # the simple shapes (it over-predicts a 1-operator assignment
            # roughly 3x), so this is a placeholder that keeps the number in
            # the right order of magnitude rather than silently contributing
            # ZERO -- which is what an early version did, and it turned a
            # 452-byte-per-statement file into a -95% under-prediction.
            # The shape is reported as a coverage gap either way.
            total += model.logic_instructions.cpt_expression.cost_for(call.operators)
            unmeasured.append(f"{len(call.operators)}|{str(dest_is_real).lower()}")
    return total, unmeasured


def size_st_control_flow(routine: StructuredTextRoutine, model) -> int:
    """Control-flow constructs and bare-literal assignments only.

    Everything else an ST routine costs -- instruction calls and assignment
    right-hand sides -- is charged through the SHARED rung sizer, because
    the ST/RLL pairs proved those cost identically in both languages.
    Duplicating them here is what produced the first wiring's +29% to +42%
    over-prediction on the st_instr_* files: every instruction line was
    charged both its real instruction weight AND a per-statement fee that
    an instruction call does not actually pay.

    A bare-literal assignment ("Dn := 0;") is the one assignment shape with
    no expression for the CPT model to price, so it keeps its own flat
    rate: st_assign_literal_n01000 measures exactly 36.000/statement over
    1,000 statements, against 40.000 for a one-operator RHS."""
    st = model.structured_text
    return (
        routine.if_blocks * st.if_block
        + routine.elsif_branches * st.elsif_branch
        + routine.case_selectors * st.case_block
        + routine.for_blocks * st.for_block
        + routine.while_blocks * st.while_block
    )


def _cpt_call_for(lhs: str, rhs: str) -> CptCall:
    """Represents one ST assignment as the CPT call it costs like.

    Built to the same shape sizing/logic.py already consumes for a real
    CPT(...) rung, so the REAL-destination float path, the operator tiers
    and the literal handling all apply to ST for free rather than being
    reimplemented (and drifting)."""
    numbers = _NUMBER.findall(rhs)
    return CptCall(
        operators=_OPERATOR_TOKEN.findall(rhs),
        dest=lhs.split("[")[0],
        operand_names=tuple(
            idn.split("[")[0] for idn in _IDENT.findall(rhs)
            if idn.upper() not in {"MOD", "AND", "OR", "XOR", "TRUE", "FALSE"}
        ),
        int_literals=sum(1 for x in numbers if "." not in x),
        float_literals=sum(1 for x in numbers if "." in x),
    )
