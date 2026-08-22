"""Estimated (not exact -- see CLAUDE.md's ground-truth constraint) compiled
logic size, from the fitted per-instruction weight table.
"""

from __future__ import annotations

from l5x_memory_analyzer.parser.logic import RoutineLogic
from l5x_memory_analyzer.sizing.constants import LogicInstructionModel


def compute_routine_logic_bytes(routine: RoutineLogic, model: LogicInstructionModel) -> tuple[int, str]:
    """Sum of every recognized instruction's weight × its occurrence count
    in this routine, plus the routine's fixed base cost. Unrecognized
    mnemonics (an instruction not yet in the weight table, or an AOI/UDT
    instance call -- same call syntax as a built-in instruction in real
    rung text) are silently skipped, not guessed at or crashed on."""
    has_jsr = "JSR" in routine.instruction_counts
    fixed_base = model.jsr_fixed_base_per_routine if has_jsr else model.fixed_base_per_routine

    total = fixed_base
    for mnemonic, count in routine.instruction_counts.items():
        weight = model.weights.get(mnemonic)
        if weight is not None:
            total += weight * count

    return total, model.confidence
