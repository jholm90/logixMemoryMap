"""Parses RLL rung text out of Controller/Programs/Program/Routines.

Only RLL (ladder) routines are handled -- 22% of real routines in James's
corpus are Structured Text (OQ, see docs/TASKS.md Phase 4 note), which uses
a completely different syntax and has its own unmeasured compiled-size
characteristics. ST routines are skipped here, not guessed at.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

# An instruction call is an all-caps mnemonic immediately followed by "(" --
# e.g. "XIC(A)OTE(B);" or "CPT(Dest,(A+B)*C);". Also matches AOI/UDT
# instance calls (same call syntax as a built-in instruction in real Logix
# rung text) -- those aren't in WEIGHTS so they're silently skipped by the
# caller, not double-counted or crashed on.
_INSTRUCTION_CALL = re.compile(r"\b([A-Z][A-Z0-9_]*)\(")

# JSR's own target-routine name (first argument) -- see JSR_TARGET_ROUTINES
# below for why this needs its own extraction, not just an instruction count.
_JSR_TARGET = re.compile(r"\bJSR\(\s*([A-Za-z_][A-Za-z0-9_]*)")

# JSR's own 2nd argument is the real declared param count -- confirmed
# real shape (samples/local/ corpus, e.g. "JSR(_525_OutputMapping_TS,1,
# IncisorTop_AxisOutput,EM203_IncisorTop:O)"): target routine name, then a
# literal integer Studio 5000 itself writes as the number of params
# following, then the params themselves. OQ-JSRPARAMCOST's per-call cost
# depends on this count, wired 2026-08-25.
_JSR_CALL_START = re.compile(r"\bJSR\(")

# CPT's own expression argument needs real parsing, not a flat per-call
# weight (OQ-CMPCPTLAYOUT, wired 2026-08-26) -- real capture data shows
# CPT's cost is expression-complexity-dependent (operator count/type), not
# a constant. "**" must be tried before the single "*"/"/" alternatives or
# it would match as two separate "*" tokens. MOD is a word operator in real
# Logix syntax ("L0 MOD L1"), not a symbol, hence \b...\b. Unary +/- (e.g.
# leading "-L0") is NOT distinguished from a binary operator -- no real
# corpus example of unary sign inside a CPT expression has turned up, and
# guessing its cost would violate this project's "never guess Rockwell
# syntax" rule; flagged as a known limitation, not silently handled.
_CPT_OPERATOR_TOKEN = re.compile(r"\*\*|[+\-*/]|\bMOD\b")


def _extract_cpt_expr(text: str, start: int) -> str | None:
    """text[start] is the character right after a matched 'CPT('. Returns
    the expression argument (CPT's 2nd argument, after the first top-level
    comma) by scanning for the call's real balanced-paren close -- a naive
    "up to the next ')'" regex would stop early on a nested-parens
    expression like 'CPT(Dest,(A+B)*(C-D))'. Returns None if the text runs
    out before the parens balance (malformed/truncated, don't guess)."""
    depth = 1
    first_comma = None
    i = start
    while i < len(text):
        c = text[i]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return text[first_comma + 1:i] if first_comma is not None else None
        elif c == "," and depth == 1 and first_comma is None:
            first_comma = i
        i += 1
    return None


_CPT_CALL_START = re.compile(r"\bCPT\(")


def _cpt_calls(rung_texts: list[str]) -> list[list[str]]:
    """One entry per real CPT(...) call found across every rung, each the
    ordered list of top-level operator tokens in that call's expression --
    e.g. 'CPT(Dest,L0+L1*L2)' -> ['+', '*']. Nesting/parenthesization
    doesn't change which operators are present (confirmed real 2026-08-25:
    'CPT(Dest,L0+L1-L2*L3)' and 'CPT(Dest,(L0+L1)*(L2-L3))' cost
    identically), so this deliberately ignores grouping and just collects
    the flat operator-token stream."""
    calls: list[list[str]] = []
    for text in rung_texts:
        for m in _CPT_CALL_START.finditer(text):
            expr = _extract_cpt_expr(text, m.end())
            if expr is None:
                continue
            calls.append(_CPT_OPERATOR_TOKEN.findall(expr))
    return calls


# Instructions whose real cost varies by OPERAND data type (OQ-OPERANDTYPE,
# wired 2026-08-26) -- confirmed real via the typesweep_* corpus (69 real
# captures, error_count=0, DINT/LINT/SINT/INT/REAL/STRING operands at
# matched shape). Every instruction here already has a DINT-rate weight in
# `weights` for the base case; sizing/logic.py adds a per-type surcharge on
# top when it can resolve the operand's real type, instead of applying the
# flat DINT-rate weight unconditionally the way it used to.
_TYPE_SENSITIVE_INSTRUCTIONS = frozenset({
    "ADD", "SUB", "MUL", "DIV", "MOD", "EQU", "GEQ", "GRT", "LEQ", "LES", "NEQ", "MOV", "LIM",
})


def _extract_call_args(text: str, start: int) -> list[str] | None:
    """text[start] is the character right after a matched 'MNEMONIC('.
    Returns EVERY top-level comma-separated argument (unlike
    _extract_cpt_expr, which only wants the 2nd), via the same real
    balanced-paren scan -- an operand can itself contain parens in
    principle (not seen in this project's real corpus for these
    instructions, but handled correctly regardless). Returns None if the
    parens never balance (malformed/truncated, don't guess)."""
    depth = 1
    args: list[str] = []
    arg_start = start
    i = start
    while i < len(text):
        c = text[i]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                args.append(text[arg_start:i])
                return args
        elif c == "," and depth == 1:
            args.append(text[arg_start:i])
            arg_start = i + 1
        i += 1
    return None


_TYPED_CALL_START = re.compile(
    r"\b(" + "|".join(sorted(_TYPE_SENSITIVE_INSTRUCTIONS)) + r")\("
)


def _typed_instruction_calls(rung_texts: list[str]) -> list[tuple[str, list[str]]]:
    """One entry per real call to a type-sensitive instruction, each the
    (mnemonic, [operand_token, ...]) pair -- e.g. 'ADD(TD0,TD1,TD2)' ->
    ('ADD', ['TD0', 'TD1', 'TD2']). Operand tokens are returned as raw
    text (whitespace-stripped) -- resolving a token to an actual data type
    needs the tag table, which this structural parser deliberately doesn't
    have access to; that resolution happens at the sizing layer (see
    sizing/logic.py), same split of responsibility as _cpt_calls above."""
    calls: list[tuple[str, list[str]]] = []
    for text in rung_texts:
        for m in _TYPED_CALL_START.finditer(text):
            args = _extract_call_args(text, m.end())
            if args is None:
                continue
            calls.append((m.group(1), [a.strip() for a in args]))
    return calls


def _jsr_calls(rung_texts: list[str]) -> list[tuple[str, int]]:
    """One entry per real JSR(...) call, (target_routine_name, param_count)
    -- param_count read directly off the call's own 2nd argument (see
    _JSR_CALL_START above), the authoritative source rather than counting
    the trailing argument tokens ourselves. Skips a call whose 2nd argument
    isn't a plain integer literal (malformed/unexpected, don't guess) --
    no real corpus example has ever shown anything else there."""
    calls: list[tuple[str, int]] = []
    for text in rung_texts:
        for m in _JSR_CALL_START.finditer(text):
            args = _extract_call_args(text, m.end())
            if args is None or len(args) < 2:
                continue
            target = args[0].strip()
            count_text = args[1].strip()
            if not count_text.isdigit():
                continue
            calls.append((target, int(count_text)))
    return calls


# Indirect (tag-driven) array addressing (OQ-INDIRECT, wired 2026-08-26).
# Real data (indirect_tag_index_n*/indirect_tag_offset_index_n*, 4 count
# points each 10/50/100/1000, ALL exact once the tiny universal +4 flat
# baseline noise is set aside): a DIRECT/literal index ("Arr[5]") costs
# nothing extra over the carrier instruction's own base weight; a
# TAG-DRIVEN index ("Arr[Idx]") costs +84/occurrence; a tag-driven index
# WITH an arithmetic literal offset ("Arr[Idx+1]") costs +108/occurrence.
# Scans the WHOLE rung text, not scoped to a specific mnemonic -- the real
# mechanism this is charging for (computing an indirect address) is
# presumably a property of the ARRAY OPERAND itself, not of which
# instruction happens to read/write it, but only MOV-carried indexing was
# ever actually captured -- generalizing to other instructions' indexed
# operands (including inside a CPT expression) is an assumption, not
# independently confirmed. A bracket expression this can't classify (more
# than one tag, a nested index, a non-arithmetic expression) is left
# unresolved -- 0 cost, not a guess.
_ARRAY_INDEX = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\[([^\[\]]+)\]")
_PURE_LITERAL_INDEX = re.compile(r"^\d+$")
_TAG_INDEX = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_TAG_OFFSET_INDEX = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*[+\-]\d+$")


def _indirect_index_kinds(rung_texts: list[str]) -> list[str]:
    """One entry per real array-index bracket expression found, classified
    as 'tag' or 'tag_offset' -- direct/literal indices and anything this
    can't confidently classify are simply not included (0 cost)."""
    kinds: list[str] = []
    for text in rung_texts:
        for m in _ARRAY_INDEX.finditer(text):
            content = m.group(1).strip()
            if _PURE_LITERAL_INDEX.match(content):
                continue
            if _TAG_INDEX.match(content):
                kinds.append("tag")
            elif _TAG_OFFSET_INDEX.match(content):
                kinds.append("tag_offset")
            # else: unresolved shape, deliberately not guessed at
    return kinds


# CMP's own surcharges (wired 2026-08-26, real data confirms the existing
# flat CMP:76 weight is exact for a SINGLE simple condition -- the
# "inconsistency" flagged in an earlier pass was a manual-arithmetic
# error, not a real bug, corrected here). A COMPOUND condition (2+ clauses
# joined by && or ||) costs a real, clean +64/rung on top of the base 76,
# confirmed exact at both n=100 and n=1000 (zero residual, no large-file
# anomaly at either point, unlike several CPT cases). A condition compared
# against a FLOAT literal costs +72/rung -- only one count point (n=1000),
# FITTED not KNOWN. An int literal costs nothing extra (matches CPT's own
# int-literal finding). Both surcharges are only ever confirmed
# INDEPENDENTLY (never a compound expression that ALSO has a float
# literal) -- applied additively if both are present, an assumption, not
# a confirmed combination.
_CMP_CALL_START = re.compile(r"\bCMP\(")
_CMP_COMPOUND_OPERATOR = re.compile(r"&&|\|\|")
_CMP_FLOAT_LITERAL = re.compile(r"\d+\.\d+")


def _extract_single_arg(text: str, start: int) -> str | None:
    """text[start] is the character right after a matched 'MNEMONIC(' for
    a single-argument call like CMP(...). Balanced-paren scan to the real
    close, same method as _extract_cpt_expr/_extract_call_args above, just
    returning the whole (single) argument rather than splitting on commas."""
    depth = 1
    i = start
    while i < len(text):
        c = text[i]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return text[start:i]
        i += 1
    return None


def _cmp_calls(rung_texts: list[str]) -> list[tuple[bool, bool]]:
    """One entry per real CMP(...) call, (is_compound, has_float_literal)."""
    calls: list[tuple[bool, bool]] = []
    for text in rung_texts:
        for m in _CMP_CALL_START.finditer(text):
            expr = _extract_single_arg(text, m.end())
            if expr is None:
                continue
            calls.append((
                bool(_CMP_COMPOUND_OPERATOR.search(expr)),
                bool(_CMP_FLOAT_LITERAL.search(expr)),
            ))
    return calls


@dataclass(frozen=True)
class RoutineLogic:
    program_name: str
    routine_name: str
    rung_count: int
    # mnemonic -> number of times it appears across every rung in this
    # routine (a rung with "XIC(A)XIC(B)OTE(C);" counts XIC twice, OTE once).
    instruction_counts: dict[str, int] = field(default_factory=dict)
    # True if some OTHER routine in the same program JSRs to this one.
    # Confirmed 2026-08-22 against real data (instr_jsr_n*.L5X): the target
    # routine's own fixed-base-and-content cost is already fully absorbed
    # into the calling routine's jsr_fixed_base_per_routine constant (that
    # constant was fit while the target's content stayed fixed across the
    # whole sweep) -- charging it AGAIN as an independent routine
    # double-counts. sizing/logic.py uses this flag to skip such routines
    # entirely when computing the program's total. Only confirmed for a
    # trivial (1-NOP-rung) target; a substantial JSR target routine's real
    # behavior is unconfirmed, see docs/MEMORY_MODEL.md.
    is_jsr_target: bool = False
    # One entry per real CPT(...) call in this routine, each the ordered
    # list of top-level operator tokens found in that call's expression --
    # see _cpt_calls above. sizing/logic.py costs these individually
    # instead of via the flat instruction_counts["CPT"] path (real data:
    # CPT's cost is expression-complexity-dependent, OQ-CMPCPTLAYOUT).
    cpt_calls: list[list[str]] = field(default_factory=list)
    # One entry per real call to a type-sensitive instruction (see
    # _TYPE_SENSITIVE_INSTRUCTIONS), each (mnemonic, [operand_tokens]) --
    # sizing/logic.py resolves each operand's real type against the tag
    # table and applies a per-type surcharge on top of the base DINT-rate
    # weight (OQ-OPERANDTYPE). Every call here ALSO still counts once in
    # instruction_counts above (needed for is_jsr_target etc elsewhere) --
    # sizing/logic.py applies the base weight from `weights` as before and
    # ADDS the surcharge separately, it does not re-derive the base cost
    # from this list.
    typed_calls: list[tuple[str, list[str]]] = field(default_factory=list)
    # One entry per real indirect (tag-driven) array-index bracket found in
    # this routine, each 'tag' or 'tag_offset' -- see _indirect_index_kinds
    # above (OQ-INDIRECT). Direct/literal indices cost nothing extra and
    # are not represented here at all.
    indirect_index_kinds: list[str] = field(default_factory=list)
    # One entry per real CMP(...) call, (is_compound, has_float_literal) --
    # see _cmp_calls above (OQ-CMPCPTLAYOUT's CMP piece, wired 2026-08-26).
    cmp_calls: list[tuple[bool, bool]] = field(default_factory=list)
    # Every routine name THIS routine JSRs to (2026-08-27, Phase 5 call-
    # tree UI) -- distinct from is_jsr_target above, which only says
    # whether some OTHER routine calls this one, not who calls whom. Byte
    # totals already correctly avoid double-counting via is_jsr_target
    # (confirmed 2026-08-22); this field exists purely so the UI can show
    # the real call structure, not to change any sizing.
    jsr_target_names: frozenset[str] = field(default_factory=frozenset)
    # One entry per real JSR(...) call THIS routine makes, (target_name,
    # param_count) -- see _jsr_calls above (OQ-JSRPARAMCOST, wired
    # 2026-08-25). sizing/logic.py charges the confirmed per-call B(n) cost
    # for each entry here; report.py separately charges A(n) once per
    # distinct target routine (a one-time cost of the callee's own
    # Parameters-block declaration, not the caller's).
    jsr_calls: list[tuple[str, int]] = field(default_factory=list)

    @property
    def path(self) -> str:
        return f"program:{self.program_name}/{self.routine_name}"


def _count_instructions(rung_texts: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for text in rung_texts:
        for mnemonic in _INSTRUCTION_CALL.findall(text):
            counts[mnemonic] = counts.get(mnemonic, 0) + 1
    return counts


def _jsr_targets(rung_texts: list[str]) -> set[str]:
    targets: set[str] = set()
    for text in rung_texts:
        targets.update(_JSR_TARGET.findall(text))
    return targets


def parse_rll_routines(root: ET.Element) -> list[RoutineLogic]:
    routines: list[RoutineLogic] = []
    programs_el = root.find("Controller/Programs")
    if programs_el is None:
        return routines

    for program_el in programs_el.findall("Program"):
        program_name = program_el.get("Name")
        routines_el = program_el.find("Routines")
        if routines_el is None:
            continue

        # Two passes: first collect every RLL routine's rung text (need the
        # whole program's JSR targets before deciding is_jsr_target for any
        # one routine), then build the RoutineLogic list.
        per_routine_rung_texts: dict[str, list[str]] = {}
        for routine_el in routines_el.findall("Routine"):
            if routine_el.get("Type") != "RLL":
                continue
            routine_name = routine_el.get("Name")
            rll_content = routine_el.find("RLLContent")
            rung_texts = []
            # 2026-08-27, OQ-EMPTYROUTINE: a self-closing <Routine Type="RLL"/>
            # (no RLLContent child at all) is a real, common shape -- 15+ real
            # corpus files have one -- and was being silently dropped here
            # entirely, so it never got a RoutineLogic entry and never
            # contributed to n_plain_routines in report.py's Task/Program/
            # Routine shell decomposition. That's wrong: real data (emptyroutine_
            # n01/n02/n03, captured 2026-08-27) shows a self-closing routine
            # still pays the same real per-extra-routine shell cost as an
            # ordinary one (272-ish/routine, matching the already-wired
            # task_program_overhead.routine_extra exactly, within the usual
            # small-N noise) -- it just has zero content cost, which falls out
            # naturally once it's counted as a routine with 0 rungs instead of
            # not counted at all. Emitting it here (rung_texts=[]) rather than
            # skipping lets the existing shell-decomposition math handle it
            # for free, no new constant needed.
            if rll_content is not None:
                for rung_el in rll_content.findall("Rung"):
                    text_el = rung_el.find("Text")
                    if text_el is not None and text_el.text:
                        rung_texts.append(text_el.text)
            per_routine_rung_texts[routine_name] = rung_texts

        program_jsr_targets: set[str] = set()
        for rung_texts in per_routine_rung_texts.values():
            program_jsr_targets |= _jsr_targets(rung_texts)

        for routine_name, rung_texts in per_routine_rung_texts.items():
            routines.append(RoutineLogic(
                program_name=program_name,
                routine_name=routine_name,
                rung_count=len(rung_texts),
                instruction_counts=_count_instructions(rung_texts),
                is_jsr_target=routine_name in program_jsr_targets,
                cpt_calls=_cpt_calls(rung_texts),
                typed_calls=_typed_instruction_calls(rung_texts),
                indirect_index_kinds=_indirect_index_kinds(rung_texts),
                cmp_calls=_cmp_calls(rung_texts),
                jsr_target_names=frozenset(_jsr_targets(rung_texts)),
                jsr_calls=_jsr_calls(rung_texts),
            ))

    return routines
