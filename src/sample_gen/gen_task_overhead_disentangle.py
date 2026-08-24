"""Per-Task overhead disentangling, missing axis (James, 2026-08-26: "touch
these and finalize them now").

docs/OPEN_QUESTIONS.md's per-Task overhead item needed a way to separate
per-Task, per-Program, and per-Routine-within-a-program scaffolding cost --
every real calibration file to date had exactly one Task/one Program/one
Routine, so the three were indistinguishable. `taskoverhead_n0Xtasks`
(N tasks, N programs, N routines -- 1:1:1 scaling) and
`programoverhead_n02progs_1task` (1 task, 2 programs, 2 routines) together
cleanly isolate the per-Task marginal cost (+700, holding program/routine
count fixed via direct comparison of those two files) -- a real result,
verified 2026-08-26.

But program count and routine count still move together in EVERY existing
file (each extra program always brings exactly one extra routine with it)
-- there is still no real data point with 2 ROUTINES under ONE Program
under ONE Task, so "per-Program" and "per-additional-routine-within-a-
program" remain confounded. This file closes exactly that one remaining
gap: a single program, single task, with a SECOND trivial (NOP-only)
routine added directly to MainProgram's own Routines block (not a new
Program) -- mirroring the JSR generator's own "extra routine in the same
program" mechanism (`extra_routines_xml`), but with a plain NOP body
instead of an SBR/RET subroutine, so it isolates pure per-extra-routine
cost with no JSR-specific scaffolding mixed in.

Run: python -m sample_gen.gen_task_overhead_disentangle
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import rung_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"


def _write(l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "task_overhead", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


def group_second_routine_same_program() -> int:
    # A second RLL routine, empty NOP content, added directly to
    # MainProgram alongside the wrapper's own MainRoutine -- 1 Program,
    # 1 Task, 2 Routines. Real Logix requires every routine name be
    # unique within its Program; "SecondRoutine" is never referenced by
    # anything (no JSR to it) so it's pure dead-but-declared scaffolding,
    # the same real-world shape as an unused/legacy routine left in a
    # program.
    second_routine = (
        '<Routine Name="SecondRoutine" Type="RLL">'
        f'<RLLContent>{rung_xml(0, "NOP();")}</RLLContent>'
        "</Routine>"
    )
    l5x = build_l5x(target_name="TaskOverheadSameProgram2Routine", tags_xml="", extra_routines_xml=second_routine)
    _write(
        l5x, "taskoverhead_n02routines_1program_1task",
        "1 Task, 1 Program, 2 Routines (both NOP-only, no JSR relationship) -- isolates pure "
        "per-extra-routine-within-a-program cost from per-Program/per-Task scaffolding "
        "(taskoverhead_n02tasks and programoverhead_n02progs_1task each always moved routine "
        "count together with task or program count; this is the missing 3rd axis)",
    )
    return 1


if __name__ == "__main__":
    total = group_second_routine_same_program()
    print(f"\nTotal files: {total}")
