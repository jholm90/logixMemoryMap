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

# Identifier (tag reference, with or without a subscript) and numeric-literal
# tokens inside a CPT expression -- needed to tell a REAL-destination CPT's
# already-float operands from the ones Logix has to convert. See
# _cpt_call_detail and memory_model.yaml cpt_real_dest.
_CPT_IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_.]*(?:\[[^\]]*\])?")
_CPT_NUMBER = re.compile(r"(?<![A-Za-z_0-9.\[])\d+\.\d+|(?<![A-Za-z_0-9.\[])\d+(?![.\d])")


@dataclass(frozen=True)
class CptCall:
    """One real CPT(...) call site.

    `operators` is the ordered list of top-level operator tokens in the
    call's expression -- e.g. 'CPT(Dest,L0+L1*L2)' -> ['+', '*']. Nesting/
    parenthesization doesn't change which operators are present (confirmed
    real 2026-08-25: 'CPT(Dest,L0+L1-L2*L3)' and 'CPT(Dest,(L0+L1)*(L2-L3))'
    cost identically), so grouping is deliberately ignored.

    The rest describes the call's DESTINATION and OPERAND COMPOSITION, added
    2026-09-04 for OQ-CMPCPTLAYOUT's REAL-destination thread: a CPT writing
    to a REAL destination is evaluated in float, which costs materially
    differently from the integer path this model was originally fitted on
    (real, exact, 29/29 captured rows -- see memory_model.yaml
    cpt_real_dest). sizing/logic.py resolves `dest` against the file's real
    tag types; the parser deliberately doesn't (same split of
    responsibility as typed_calls)."""

    operators: list[str]
    dest: str
    operand_names: tuple[str, ...]
    int_literals: int
    float_literals: int


def _cpt_call_detail(text: str, start: int) -> CptCall | None:
    """Builds one CptCall from the text right after a matched 'CPT('.
    Returns None for a malformed/truncated call (don't guess), same
    convention as _extract_cpt_expr."""
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
                if first_comma is None:
                    return None
                dest = text[start:first_comma].strip()
                expr = text[first_comma + 1:i]
                numbers = _CPT_NUMBER.findall(expr)
                return CptCall(
                    operators=_CPT_OPERATOR_TOKEN.findall(expr),
                    # Subscript stripped: an array element's type is its
                    # array's type, and that's how tag_types is keyed.
                    dest=dest.split("[")[0],
                    # MOD is a word OPERATOR, not a tag -- excluded here so
                    # it can never be miscounted as an integer operand.
                    operand_names=tuple(
                        idn.split("[")[0]
                        for idn in _CPT_IDENT.findall(expr)
                        if idn != "MOD"
                    ),
                    int_literals=sum(1 for x in numbers if "." not in x),
                    float_literals=sum(1 for x in numbers if "." in x),
                )
        elif c == "," and depth == 1 and first_comma is None:
            first_comma = i
        i += 1
    return None


def _cpt_calls(rung_texts: list[str]) -> list[CptCall]:
    """One entry per real CPT(...) call found across every rung."""
    calls: list[CptCall] = []
    for text in rung_texts:
        for m in _CPT_CALL_START.finditer(text):
            call = _cpt_call_detail(text, m.end())
            if call is not None:
                calls.append(call)
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


def _jsr_calls(rung_texts: list[str]) -> list[tuple[str, int, int]]:
    """One entry per real JSR(...) call, (target_routine_name,
    input_param_count, output_param_count) -- input_param_count read
    directly off the call's own 2nd argument (see _JSR_CALL_START above),
    the authoritative source rather than counting the trailing argument
    tokens ourselves. Skips a call whose 2nd argument isn't a plain
    integer literal (malformed/unexpected, don't guess) -- no real corpus
    example has ever shown anything else there.

    output_param_count (OQ-JSRPARAMCOST, wired 2026-08-29) is every
    remaining tag argument after the declared input count -- real syntax
    confirmed against the corpus (see gen_jsr_sbr_ret.py's module
    docstring): `JSR(name, N_in, in_1..in_N, out_1..out_M)`, so
    len(args) - 2 (target + count) - N_in gives M. Real capture data
    (jsr_mixedio_5in_2out, jsr_multiret_n04) showed this project's
    original OQ-JSRPARAMCOST fit (input args only, from group_param_count's
    always-empty RET()) completely missed this cost -- ~40,000/1,000 calls
    unmodeled for 2 return args."""
    calls: list[tuple[str, int, int]] = []
    for text in rung_texts:
        for m in _JSR_CALL_START.finditer(text):
            args = _extract_call_args(text, m.end())
            if args is None or len(args) < 2:
                continue
            target = args[0].strip()
            count_text = args[1].strip()
            if not count_text.isdigit():
                continue
            n_in = int(count_text)
            m_out = max(0, len(args) - 2 - n_in)
            calls.append((target, n_in, m_out))
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
    # 2026-08-22: confirmed the target's own fixed shell cost (fixed_base_
    # per_routine) is already absorbed into the caller's jsr_fixed_base_
    # per_routine, so sizing/report.py never charges it again for a JSR
    # target -- that part still holds. The target's own CONTENT cost is a
    # separate matter: 2026-08-22's finding only ever tested a trivial
    # 1-NOP-rung stub target, and real data at real scale (2026-08-31,
    # jsr_target_content_scale_{010,050,100,150}, see OPEN_QUESTIONS.md
    # OQ-JSRPARAMCOST) disproved the "content is free too" part of the old
    # claim -- report.py now weighs a JSR target's own instructions with
    # the normal per-instruction model (charge_shell=False, so only its
    # fixed shell stays excluded).
    is_jsr_target: bool = False
    # 2026-09-03, OQ-SAFETYSCOPE-SIZING (James: "they are safety tasks and
    # safety programs therefore they need separate sizing calculations").
    # True when this routine's owning <Program> carries Class="Safety" --
    # real, unambiguous marker (confirmed on samples/generated/fw_catalog_
    # matrix/fwmatrix_v31_1756_l81es.L5X's real SafetyProgram), not the
    # Type="PERIODIC" schedule-type attribute (shared with ordinary
    # periodic programs/tasks). sizing/report.py's Task/Program/Routine
    # shell decomposition excludes Safety routines from the ordinary
    # n_plain_routines count and charges a separate, smaller, real
    # safety_task_program_shell constant instead.
    is_safety_program: bool = False
    # One entry per real CPT(...) call in this routine -- see CptCall and
    # _cpt_calls above. sizing/logic.py costs these individually instead of
    # via the flat instruction_counts["CPT"] path (real data: CPT's cost is
    # expression-complexity-dependent, OQ-CMPCPTLAYOUT).
    cpt_calls: list[CptCall] = field(default_factory=list)
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
    # input_param_count, output_param_count) -- see _jsr_calls above
    # (OQ-JSRPARAMCOST, wired 2026-08-25, output params added 2026-08-29).
    # sizing/logic.py charges the confirmed per-call B(n_in) cost plus the
    # per-output-param cost for each entry here; report.py separately
    # charges A(n_in) once per distinct target routine (a one-time cost of
    # the callee's own Parameters-block declaration, not the caller's) --
    # A(n) is NOT yet adjusted for output param count, see
    # OPEN_QUESTIONS.md OQ-JSRPARAMCOST.
    jsr_calls: list[tuple[str, int, int]] = field(default_factory=list)
    # Total real BST/NXB/BND-family branch-bracket instructions across this
    # routine's rungs (OQ-BRANCHDEPTH, wired 2026-08-30) -- see
    # _branch_bracket_instruction_count above. A single-level branch with L
    # legs compiles to L+1 of these; nested/staggered branches recurse.
    # sizing/logic.py charges this count x the confirmed flat per-
    # instruction rate (memory_model.yaml branch_bracket_cost_per_
    # instruction), additive on top of every leg's own instruction weight
    # (already counted normally via instruction_counts above).
    branch_bracket_instruction_count: int = 0

    @property
    def path(self) -> str:
        return f"program:{self.program_name}/{self.routine_name}"


def _parse_branch_group(text: str, start: int) -> tuple[int, int]:
    """text[start] == '[', a real branch-open (see _branch_bracket_
    instruction_count below for how that's distinguished from an array-
    index '['). Returns (total real BST/NXB/BND-family instruction count
    for this group INCLUDING every nested branch inside it, index right
    after this group's matching ']'). A group with L top-level legs
    (comma-separated at paren-depth 0, not counting legs inside a nested
    branch) compiles to 1 BST + (L-1) NXB + 1 BND = L+1 real instructions
    -- confirmed exact against 16/16 real capture points (OQ-BRANCHDEPTH,
    see memory_model.yaml branch_bracket_cost_per_instruction)."""
    i = start + 1
    n = len(text)
    paren_depth = 0
    legs = 1
    nested_total = 0
    while i < n:
        c = text[i]
        if c == "(":
            paren_depth += 1
            i += 1
        elif c == ")":
            paren_depth -= 1
            i += 1
        elif c == "[" and paren_depth == 0 and not (text[i - 1].isalnum() or text[i - 1] == "_"):
            sub_total, next_i = _parse_branch_group(text, i)
            nested_total += sub_total
            i = next_i
        elif c == "]" and paren_depth == 0:
            return legs + 1 + nested_total, i + 1
        elif c == "," and paren_depth == 0:
            legs += 1
            i += 1
        else:
            i += 1
    # Unterminated group (malformed text) -- return what's been scanned
    # rather than crash; report.py's own lint layer catches real structural
    # errors upstream of sizing.
    return legs + 1 + nested_total, i


def _branch_bracket_instruction_count(rung_texts: list[str]) -> int:
    """Total real BST/NXB/BND-family branch-bracket instructions across
    every rung -- a '[' is a real branch-open only when NOT immediately
    preceded by an identifier character (that shape is an array index,
    e.g. "Tag[5]", handled entirely separately by _ARRAY_INDEX/
    _indirect_index_kinds above, not a branch)."""
    total = 0
    for text in rung_texts:
        i = 0
        n = len(text)
        while i < n:
            if text[i] == "[" and not (i > 0 and (text[i - 1].isalnum() or text[i - 1] == "_")):
                group_total, next_i = _parse_branch_group(text, i)
                total += group_total
                i = next_i
            else:
                i += 1
    return total


def _count_instructions(rung_texts: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for text in rung_texts:
        for mnemonic in _INSTRUCTION_CALL.findall(text):
            counts[mnemonic] = counts.get(mnemonic, 0) + 1
    return counts


def count_instructions_in_text(rung_texts: list[str]) -> dict[str, int]:
    """Public wrapper over the same mnemonic scanner the sizer itself uses --
    so sizing/coverage.py counts instructions exactly the way size_routine()
    does, rather than re-implementing the regex and drifting from it."""
    return _count_instructions(rung_texts)


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
        is_safety_program = program_el.get("Class") == "Safety"
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
                is_safety_program=is_safety_program,
                cpt_calls=_cpt_calls(rung_texts),
                typed_calls=_typed_instruction_calls(rung_texts),
                indirect_index_kinds=_indirect_index_kinds(rung_texts),
                cmp_calls=_cmp_calls(rung_texts),
                jsr_target_names=frozenset(_jsr_targets(rung_texts)),
                jsr_calls=_jsr_calls(rung_texts),
                branch_bracket_instruction_count=_branch_bracket_instruction_count(rung_texts),
            ))

    return routines


def parse_aoi_internal_logic(root: ET.Element) -> dict[str, RoutineLogic]:
    """AOI definition name -> ONE aggregate RoutineLogic combining the rung
    text of every internal RLL routine that AOI declares (its Logic routine
    plus any additional ones, e.g. a real AOI like HomeToTorque has both
    Logic and EnableInFalse).

    Real data (2026-08-31, aoi_multiroutine_control vs aoi_multiroutine_real,
    see OPEN_QUESTIONS.md OQ-AOIINTERNALLOGIC) confirms splitting the SAME
    content across 2 internal routines instead of 1 costs identically to
    keeping it in one -- so this deliberately aggregates all of an AOI's
    internal routines into a single pseudo-routine rather than tracking them
    separately; the per-routine-count dimension doesn't matter, only total
    content does. sizing/udt.py weighs this the same way as ordinary routine
    logic via compute_routine_logic_bytes(charge_shell=False) -- an AOI's
    internal routine doesn't pay its own fixed_base_per_routine; that's a
    separate, already-confirmed cost the aoi_definition formula's base
    already covers.

    Not JSR-aware (is_jsr_target/jsr_calls/jsr_target_names left at their
    defaults) -- an AOI calling JSR internally, or being itself invoked
    in a way that interacts with the JSR-target machinery, is untested
    territory, not something this function guesses at."""
    result: dict[str, RoutineLogic] = {}
    aois_el = root.find("Controller/AddOnInstructionDefinitions")
    if aois_el is None:
        return result

    for aoi_el in aois_el.findall("AddOnInstructionDefinition"):
        name = aoi_el.get("Name")
        routines_el = aoi_el.find("Routines")
        if routines_el is None:
            continue
        rung_texts: list[str] = []
        for routine_el in routines_el.findall("Routine"):
            if routine_el.get("Type") != "RLL":
                continue
            rll_content = routine_el.find("RLLContent")
            if rll_content is None:
                continue
            for rung_el in rll_content.findall("Rung"):
                text_el = rung_el.find("Text")
                if text_el is not None and text_el.text:
                    rung_texts.append(text_el.text)
        if not rung_texts:
            continue
        result[name] = RoutineLogic(
            program_name="",
            routine_name=name,
            rung_count=len(rung_texts),
            instruction_counts=_count_instructions(rung_texts),
            cpt_calls=_cpt_calls(rung_texts),
            typed_calls=_typed_instruction_calls(rung_texts),
            indirect_index_kinds=_indirect_index_kinds(rung_texts),
            cmp_calls=_cmp_calls(rung_texts),
            branch_bracket_instruction_count=_branch_bracket_instruction_count(rung_texts),
        )
    return result
