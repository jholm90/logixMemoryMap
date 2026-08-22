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
            ))

    return routines
