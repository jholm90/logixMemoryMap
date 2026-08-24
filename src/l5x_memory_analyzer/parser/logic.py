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
            if rll_content is None:
                continue
            rung_texts = []
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
            ))

    return routines
