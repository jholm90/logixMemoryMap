"""OQ-IDENTNAMELEN closeout (2026-09-12).

The law is derived and WIRED. Two independent sweeps -- JSR target routine
names and Program names, 10 identifiers per file at name lengths 4/8/16/32/40
-- return the IDENTICAL per-identifier cost relative to a 4-character name:

    name length     4    8   16   32   40
    JSR targets     0   +8  +16  +32  +40
    Programs        0   +8  +16  +32  +40

so above 8 characters the cost is exactly the character count (1 byte/char, no
bucketing) and at 4 characters it is zero, not 4. Wired as the shared
memory_model.yaml `identifier_name_length`, used by both the JSR-target
declaration and the Program shell: all 5 `program_multi_distinct_namelen*`
rows went from 0/-80/-160/-320/-400 to exactly 0, and all 5
`jsr_multi_distinct_targets_namelen*` rows collapsed onto a uniform +200
(previously +240 at len=4), leaving no name-length signal in that residual at
all. The len=40 capture the entry was held open waiting for had already landed.

Two things the entry names that the wired law does NOT rest on measurements
for. 36 files, one group each, nothing padded.

  A. group_dense_length -- the 4 < len < 8 interval.

     The law is two pieces that meet at 8 characters, and the sub-8 piece is a
     straight line drawn between two measured anchors (0 bytes at 4 chars, 8
     bytes at 8 chars) with NO data of its own. Real Logix names that short
     are common, so a fitted line there is not good enough: this sweeps every
     length from 1 to 12 directly, 10 Programs per file, which reads the floor
     shape point by point instead of assuming it is linear.

     Programs rather than JSR targets on purpose: the Program sweep's residual
     is exactly 0 across its whole measured range, so any deviation here is
     pure name-length signal. The JSR sweep carries a separate flat +200
     per-target under-charge (OQ-JSRPARAMCOST) that would have to be
     subtracted first.

  B. group_routine_names -- whether the law generalizes to plain ROUTINE
     names, which the entry flags as untested.

     `task_program_overhead.routine_extra` has no name-length term, exactly as
     `program_extra` had none before this. If plain routines follow the same
     law they need the same wiring; if they do not, then the law belongs to
     identifiers that are SCHEDULING or CALL targets (Programs, JSR targets)
     rather than to every named object, which is a materially different rule
     and would change where else it should be applied. 10 extra plain routines
     per file (no JSR to them -- an uncalled routine, so the JSR-target
     declaration path cannot contribute), name length swept over the same
     4/8/16/32/40 points the two confirmed sweeps used plus the dense 1..12
     range's endpoints.

  C. group_task_names -- Tasks are the third identifier in the same shell
     formula (`task_extra`), also with no name-length term, and no sweep has
     ever varied a Task name. One Periodic task per extra program (real Logix
     allows only one Continuous task), name length swept over the confirmed
     points. Cheap, same generator, and it completes the shell formula's three
     identifier classes instead of leaving one untested.

Run: python -m sample_gen.gen_identname_closeout
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import program_xml, rung_xml, task_xml
from sample_gen.lint import lint_or_raise
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"

# 40 is Rockwell's real Logix identifier cap, shared by tag/routine/program/
# task/AOI names. A namelen48 variant in an earlier batch failed to import,
# which is how the cap was confirmed rather than assumed.
MAX_IDENT = 40
FIXED_COUNT = 10


def _write(out_name: str, l5x: str, description: str) -> int:
    lint_or_raise(l5x, out_name)
    out_path = OUT_ROOT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "logic_instr", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")
    return 1


def _padded_name(prefix: str, i: int, total_length: int, index_width: int = 2) -> str:
    """Distinct names all of EXACTLY total_length characters.

    The index goes at the END and the padding in the middle: truncating a
    common prefix instead collapses distinct names into one, which is the real
    bug the two existing namelen generators document.
    """
    idx = str(i).zfill(index_width)
    if total_length <= len(idx):
        # Lengths below the index width cannot carry a 2-digit suffix and
        # still be distinct; fall back to a single letter cycled by index.
        return chr(ord("A") + (i % 26)) * total_length
    fill = max(total_length - len(prefix) - len(idx), 0)
    name = f"{prefix}{'X' * fill}{idx}"
    if len(name) > total_length:
        keep = max(total_length - len(idx), 1)
        name = f"{prefix[:keep]}{idx}"
    return name


def _programs_l5x(prog_names: list[str]) -> str:
    programs_xml = "\n".join(program_xml(p) for p in prog_names)
    scheduled_xml = "\n".join(f'<ScheduledProgram Name="{p}"/>' for p in prog_names)
    return build_l5x(
        target_name="IdentNameClose", tags_xml="",
        extra_programs_xml=programs_xml, extra_scheduled_programs_xml=scheduled_xml,
    )


# ---------------------------------------------------------------------------
# A. Every length 1..12, to measure the sub-crossover floor directly
# ---------------------------------------------------------------------------

DENSE_LENGTHS = tuple(range(1, 13))


def group_dense_length() -> int:
    n = 0
    for length in DENSE_LENGTHS:
        names = [_padded_name("P", i, length, index_width=(1 if length <= 2 else 2))
                 for i in range(FIXED_COUNT)]
        if len(set(names)) != FIXED_COUNT:
            # At length 1 ten distinct single-character names still exist
            # (A..J), but never ship a file whose identifiers silently
            # collapsed -- that is the exact failure the padding scheme above
            # was written to avoid.
            names = [chr(ord("A") + i) * length for i in range(FIXED_COUNT)]
        assert len(set(names)) == FIXED_COUNT and all(len(x) == length for x in names)
        n += _write(
            f"identnamelen_prog_c{length:02d}", _programs_l5x(names),
            f"{FIXED_COUNT} extra Programs, every Program name exactly {length} character(s) "
            f"-- OQ-IDENTNAMELEN dense-floor closeout. The wired law is two pieces meeting at "
            f"8 characters, and the sub-8 piece is a straight line between two measured anchors "
            f"(0 bytes at 4 chars, 8 bytes at 8) with no data of its own; real Logix names that "
            f"short are common. Programs not JSR targets because the Program sweep reconciles at "
            f"exactly 0 across its whole range, so any deviation here is pure name-length signal, "
            f"whereas the JSR sweep carries a separate flat +200 per-target under-charge")
    return n


# ---------------------------------------------------------------------------
# B. Plain (uncalled) routine names
# ---------------------------------------------------------------------------

ROUTINE_LENGTHS = (1, 4, 8, 12, 16, 32, MAX_IDENT)


def _routine_xml(name: str) -> str:
    return (f'<Routine Name="{name}" Type="RLL">'
            f"<RLLContent>{rung_xml(0, 'NOP();')}</RLLContent></Routine>")


def group_routine_names() -> int:
    n = 0
    for length in ROUTINE_LENGTHS:
        names = [_padded_name("R", i, length, index_width=(1 if length <= 2 else 2))
                 for i in range(FIXED_COUNT)]
        if len(set(names)) != FIXED_COUNT:
            names = [chr(ord("A") + i) * length for i in range(FIXED_COUNT)]
        assert len(set(names)) == FIXED_COUNT and all(len(x) == length for x in names)
        l5x = build_l5x(target_name="IdentNameRoutine", tags_xml="",
                        extra_routines_xml="\n".join(_routine_xml(x) for x in names))
        n += _write(
            f"identnamelen_rtn_c{length:02d}", l5x,
            f"{FIXED_COUNT} extra plain RLL routines, none of them called by a JSR, every "
            f"routine name exactly {length} character(s) -- OQ-IDENTNAMELEN routine-name "
            f"generalization. task_program_overhead.routine_extra has no name-length term, "
            f"exactly as program_extra had none before this was wired. If plain routines follow "
            f"the same law they need the same wiring; if they do not, the law belongs to "
            f"SCHEDULING and CALL targets (Programs, JSR targets) rather than to every named "
            f"object, which is a different rule and changes where else it applies. Uncalled on "
            f"purpose so the JSR-target declaration path cannot contribute")
    return n


# ---------------------------------------------------------------------------
# C. Task names
# ---------------------------------------------------------------------------

TASK_LENGTHS = (4, 8, 16, 32, MAX_IDENT)
N_EXTRA_TASKS = 5


def group_task_names() -> int:
    n = 0
    for length in TASK_LENGTHS:
        task_names = [_padded_name("T", i, length) for i in range(N_EXTRA_TASKS)]
        # Each extra task needs its own program to schedule; those program
        # names are held at a FIXED 16 characters so only the task name moves.
        prog_names = [_padded_name("TaskProgHost", i, 16) for i in range(N_EXTRA_TASKS)]
        assert len(set(task_names)) == N_EXTRA_TASKS
        assert all(len(x) == length for x in task_names)
        # Periodic, not Continuous: real Logix allows exactly one Continuous
        # task per controller and the wrapper's MainTask already is one.
        tasks_xml = "\n".join(
            task_xml(t, p, task_type="Periodic") for t, p in zip(task_names, prog_names))
        l5x = build_l5x(
            target_name="IdentNameTask", tags_xml="",
            extra_programs_xml="\n".join(program_xml(p) for p in prog_names),
            extra_tasks_xml=tasks_xml,
        )
        n += _write(
            f"identnamelen_task_c{length:02d}", l5x,
            f"{N_EXTRA_TASKS} extra Periodic Tasks, every Task name exactly {length} "
            f"characters, each scheduling one Program whose own name is held at a fixed 16 "
            f"characters so only the TASK name varies -- OQ-IDENTNAMELEN task-name closeout. "
            f"Tasks are the third identifier class in the same shell formula (task_extra) and "
            f"the only one no sweep has ever varied the name of. Periodic because real Logix "
            f"allows exactly one Continuous task and the wrapper's MainTask already is one")
    return n


def main() -> None:
    total = 0
    for fn in (group_dense_length, group_routine_names, group_task_names):
        count = fn()
        print(f"{fn.__name__}: {count} file(s)")
        total += count
    print(f"\nDone. {total} files.")


if __name__ == "__main__":
    main()
