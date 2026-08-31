"""OQ-TASKOVERHEAD (task_program_overhead, memory_model.yaml): James,
2026-08-31, right after the JSR distinct-target-count finding: "worth
doing something similar with programs as well." report.py's task_program_
shell formula (fixed_base_per_routine + task_extra*(n_tasks-1) +
program_extra*(n_programs-1) + routine_extra*(n_plain_routines-1)) has
program_extra=484 derived from only 5 real plain-routine files
(memory_model.yaml task_program_overhead comment) -- never validated at
real-project program COUNTS (5/10/15/20/50), and Program names carry no
name-length term at all today, exactly the same untested-name-length gap
just found for JSR target routines.

Two groups, same shape as gen_jsr_multi_distinct_targets_scale.py:

  A. group_quantity_scale -- N_PROGRAMS = 5/10/15/20/50 extra Programs
     (1 + N total), each scheduled under the same MainTask (real,
     representative shape -- one Continuous task running many programs,
     not one task per program, which was already covered by gen_task_
     overhead.py's separate OQ-TASKOVERHEAD Task-count sweep). Each extra
     Program has exactly one trivial single-NOP-rung MainRoutine (matches
     program_xml()'s default, same as gen_task_overhead.py's shape) and
     no tags, so any Capacity change across this sweep is attributable to
     Program-count scaffolding alone, not logic content. Program name
     length held fixed (16 chars) across the whole group.

  B. group_name_length -- Program count held fixed at 10 extra Programs,
     Program name length swept (4/8/16/32/40 chars -- 40 is Rockwell's
     real Logix identifier length cap) instead, isolating whether
     Program name length alone carries a real per-program cost the way
     it does for tags/UDTs/AOI definitions.

Run: python -m sample_gen.gen_program_multi_distinct_scale
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import program_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"

N_PROGRAMS_SCALE = (5, 10, 15, 20, 50)
# 40 is Rockwell's real Logix identifier length cap (tag/routine/program/AOI
# names all share it) -- NOT a round-number choice. Originally 48 here;
# James's real l5x2acd run (2026-08-31) failed to import both namelen48
# files (this one and gen_jsr_multi_distinct_targets_scale.py's) with the
# generic XMLSrv_E_IMPORT_ABORTED_NO_CHANGES wrapper, no per-file detail,
# while every other length (4/8/16/32, all <=40) converted clean --
# consistent with a silent identifier-length rejection, not a random
# flake. 40 is used as the top point instead of dropped entirely so the
# sweep still covers the real maximum a project could ever use.
NAME_LENGTHS = (4, 8, 16, 32, 40)
FIXED_COUNT_FOR_NAMELEN = 10


def _padded_name(prefix: str, i: int, total_length: int, index_width: int) -> str:
    # Same exact-length, collision-safe padding as gen_jsr_multi_distinct_
    # targets_scale.py -- see that file's docstring/comment for the real
    # bug (name truncation collapsing distinct names) this pattern avoids.
    idx = str(i).zfill(index_width)
    fill_len = max(total_length - len(prefix) - len(idx), 0)
    name = f"{prefix}{'X' * fill_len}{idx}"
    if len(name) > total_length:
        keep = max(total_length - len(idx), 1)
        name = f"{prefix[:keep]}{idx}"
    return name


def _write(out_name: str, l5x: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "logic_instr", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


def _build(prog_names: list[str]) -> str:
    programs_xml = "\n".join(program_xml(p) for p in prog_names)
    scheduled_xml = "\n".join(f'<ScheduledProgram Name="{p}"/>' for p in prog_names)
    return build_l5x(
        target_name=f"ProgScale{len(prog_names):02d}", tags_xml="",
        extra_programs_xml=programs_xml, extra_scheduled_programs_xml=scheduled_xml,
    )


def group_quantity_scale() -> None:
    for n in N_PROGRAMS_SCALE:
        prog_names = [_padded_name("ProgScale", i, 16, index_width=2) for i in range(n)]
        l5x = _build(prog_names)
        _write(
            f"program_multi_distinct_n{n:02d}",
            l5x,
            f"{n} extra Programs (1 + {n} = {n + 1} total), all scheduled under the same "
            f"MainTask (real one-task-many-programs shape), each a trivial single-NOP-rung "
            f"MainRoutine/no tags, fixed 16-char Program name length across every file in this "
            f"group -- OQ-TASKOVERHEAD Program-COUNT scale isolation, James 2026-08-31: 'worth "
            f"doing something similar with programs as well' (following the JSR distinct-target-"
            f"count gap). task_program_overhead.program_extra=484 was derived from only 5 real "
            f"plain-routine files -- never validated at this scale.",
        )


def group_name_length() -> None:
    for length in NAME_LENGTHS:
        prog_names = [
            _padded_name("P", i, length, index_width=1) for i in range(FIXED_COUNT_FOR_NAMELEN)
        ]
        l5x = _build(prog_names)
        _write(
            f"program_multi_distinct_namelen{length:02d}",
            l5x,
            f"A FIXED {FIXED_COUNT_FOR_NAMELEN} extra Programs (count held constant, unlike "
            f"group_quantity_scale), Program name length held at exactly {length} chars across "
            f"every file in this group -- OQ-TASKOVERHEAD Program-NAME-LENGTH isolation, James "
            f"2026-08-31: 'different routine name lengths in another test set for validation of "
            f"that data that was missed' (same axis, applied to Programs). report.py's "
            f"task_program_shell program_extra term has no name-length component today, unlike "
            f"tags/UDTs/AOI definitions (all confirmed real name-length bucket costs).",
        )


def main() -> None:
    group_quantity_scale()
    group_name_length()
    print("\nDone. 10 files.")


if __name__ == "__main__":
    main()
