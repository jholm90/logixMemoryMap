"""Per-PROGRAM and per-ROUTINE structural cost at real scale (OQ-SHELLSCALE).

Why this batch exists, 2026-09-05. Three separate fits of the "composite
AOI/JSR surcharge" (20/47 -> 52/21 -> 22/3) were all chasing the same
residual, and the isolating ladders built for the last batch have now
DISPROVED the per-instruction explanation outright:

  realscale_jsrtgt_xic_n*   the same rungs moved into a JSR target cost
                            +344 FLAT at n = 10/50/100/1000/5000
  realscale_jsrsplit_k*     exactly 344 per additional distinct target
  realscale_aoiint_n*       AOI-internal content costs 20/rung = 10/instr,
                            exactly XIC+OTE, across a 240x span

So neither AOI-internal nor JSR-target CONTENT carries any surcharge at
all. With that removed and alarms priced exactly, the 8 real programs are
left under-predicting by +0.95% to +7.93%, and that leftover residual
correlates with:

    programs      +0.871      aoi_instructions   +0.711
    routines      +0.829      jsr_instructions   +0.670
    jsr_targets   +0.816      aoi_instances      +0.602

PROGRAM and ROUTINE count, not instruction count. That is exactly what the
previous ladders could not see: every one of them held programs at 1 and
routines at 2 while scaling content, so a per-program or per-routine term
was invisible by construction and could only show up disguised as a
per-instruction one.

`task_program_overhead` (base + task_extra*(n-1) + program_extra*(n-1) +
routine_extra*(n-1)) was fitted on 5 files with single-digit counts. The
real programs run 8-39 programs and 46-301 routines, and the single-driver
slopes there come out around 4,900/program and 550/routine against the
wired 484 and 272 -- roughly 10x and 2x. That is a real extrapolation
failure, not noise, but it must NOT be refitted from 8 collinear real files
(programs, routines and targets all move together in a real project). Hence
isolation.

GROUPS
------
A. group_routine_count (8)  ONE program, N routines, N = 1/2/5/10/25/50/100/200.
   Total instruction content held CONSTANT at 200 rungs, redistributed
   across the routines, so the only variable is how many routines that
   content is split into. Spans past the real corpus max of 301.
B. group_program_count (7)  N programs x 1 routine, N = 1/2/5/10/20/30/40.
   Same constant 200 rungs redistributed. Spans past the real max of 39.
C. group_crossed (4)  100 routines reached three different ways --
   1x100, 5x20, 20x5, 50x2 -- at identical total content. If cost is
   per-routine only, all four land together; if there is a real per-program
   term, they separate in proportion to program count. This is the cell
   that decides it, and the one no real file can provide.

Every file uses the same proven XIC(Bi)OTE(Bi+1) rung text and shared tag
pool as the rest of this corpus, so nothing here re-invents an operand
shape (see docs/SAMPLE_GENERATION.md).

Run: python -m sample_gen.gen_shell_scale
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import program_xml, rung_xml
from sample_gen.gen_logic_sweep import INSTRUCTIONS, _POOL_TAGS_XML
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"

_XIC = INSTRUCTIONS["XIC"]
_TOTAL_RUNGS = 200  # held constant in EVERY file of this batch


def _routine(name: str, start: int, count: int) -> str:
    body = "".join(rung_xml(i, _XIC(start + i)) for i in range(count))
    return f'<Routine Name="{name}" Type="RLL"><RLLContent>{body}</RLLContent></Routine>'


def _split(total: int, parts: int) -> list[int]:
    """Distribute `total` rungs over `parts` containers as evenly as
    possible -- the total is what must stay constant, not the per-container
    count, or the experiment stops being controlled."""
    base, extra = divmod(total, parts)
    return [base + (1 if i < extra else 0) for i in range(parts)]


def _write(out_name: str, l5x: str, description: str) -> None:
    out_path = OUT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "shell_scale", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


_WHY = (
    "The composite AOI/JSR surcharge was fitted three times (20/47, 52/21, 22/3) against a "
    "residual that the isolating ladders have now disproved as per-instruction: JSR-target "
    "content costs +344 flat at every scale and AOI-internal content costs exactly XIC+OTE. "
    "On the 8 real programs the leftover correlates +0.871 with PROGRAM count and +0.829 with "
    "ROUTINE count, above +0.711 for AOI instructions -- and every previous ladder held "
    "programs at 1 and routines at 2, so a per-program/per-routine term was invisible by "
    "construction. task_program_overhead's program_extra=484 / routine_extra=272 were fitted "
    "on 5 files with single-digit counts; the real files imply roughly 4,900 and 550. "
    "Total rung content is held CONSTANT at 200 across this whole batch, so the only variable "
    "is how that content is divided up."
)


def group_routine_count() -> None:
    for n in (1, 2, 5, 10, 25, 50, 100, 200):
        counts = _split(_TOTAL_RUNGS, n)
        start = 0
        routines = []
        for i, c in enumerate(counts):
            routines.append(_routine(f"Rtn{i:03d}", start, c))
            start += c
        # Routine 0 is MainRoutine (build_l5x's own), the rest are extra.
        l5x = build_l5x(
            target_name=f"ShellRtn{n:03d}", tags_xml=_POOL_TAGS_XML,
            extra_rungs_xml="".join(rung_xml(i, _XIC(i)) for i in range(counts[0])),
            extra_routines_xml="".join(routines[1:]),
        )
        _write(f"shellscale_routines_n{n:03d}", l5x,
               f"ONE program containing {n} routine(s), with a constant {_TOTAL_RUNGS} rungs of "
               f"XIC(Bi)OTE(Bi+1) split evenly across them. Only the routine COUNT varies; total "
               f"logic content is identical in every file of this batch. Isolates "
               f"task_program_overhead.routine_extra at real scale -- the real corpus runs 46-301 "
               f"routines and this ladder reaches 200. " + _WHY)


def group_program_count() -> None:
    for n in (1, 2, 5, 10, 20, 30, 40):
        counts = _split(_TOTAL_RUNGS, n)
        progs = []
        sched = []
        start = 0
        for i, c in enumerate(counts[1:], start=1):
            body = "".join(rung_xml(j, _XIC(start + j)) for j in range(c))
            progs.append(program_xml(f"Prog{i:03d}", rungs_xml_body=body))
            sched.append(f'<ScheduledProgram Name="Prog{i:03d}"/>')
            start += c
        l5x = build_l5x(
            target_name=f"ShellProg{n:03d}", tags_xml=_POOL_TAGS_XML,
            extra_rungs_xml="".join(rung_xml(i, _XIC(i)) for i in range(counts[0])),
            extra_programs_xml="".join(progs),
            extra_scheduled_programs_xml="".join(sched),
        )
        _write(f"shellscale_programs_n{n:03d}", l5x,
               f"{n} program(s), one routine each, with a constant {_TOTAL_RUNGS} rungs split "
               f"evenly across them. Only the program COUNT varies. Isolates "
               f"task_program_overhead.program_extra at real scale -- the real corpus runs 8-39 "
               f"programs and this ladder reaches 40. " + _WHY)


def group_crossed() -> None:
    """100 routines reached four different ways at identical content. THE
    deciding cell: per-routine-only predicts all four identical; a real
    per-program term separates them by program count."""
    for n_prog, per_prog in ((1, 100), (5, 20), (20, 5), (50, 2)):
        counts = _split(_TOTAL_RUNGS, n_prog * per_prog)
        idx = 0
        progs, sched = [], []
        main_body = ""
        for p in range(n_prog):
            routines = []
            for r in range(per_prog):
                c = counts[idx]
                body = "".join(rung_xml(j, _XIC(idx * 7 + j)) for j in range(c))
                if p == 0 and r == 0:
                    main_body = body           # becomes MainRoutine
                else:
                    routines.append(f'<Routine Name="Rtn{p:02d}_{r:03d}" Type="RLL">'
                                    f"<RLLContent>{body}</RLLContent></Routine>")
                idx += 1
            if p == 0:
                extra_first = "".join(routines)
            else:
                progs.append(program_xml(f"Prog{p:03d}", rungs_xml_body="") .replace(
                    "<Routines>", "<Routines>" + "".join(routines), 1))
                sched.append(f'<ScheduledProgram Name="Prog{p:03d}"/>')
        l5x = build_l5x(
            target_name=f"ShellX{n_prog:02d}x{per_prog:03d}", tags_xml=_POOL_TAGS_XML,
            extra_rungs_xml=main_body, extra_routines_xml=extra_first,
            extra_programs_xml="".join(progs),
            extra_scheduled_programs_xml="".join(sched),
        )
        _write(f"shellscale_crossed_{n_prog:02d}prog_x{per_prog:03d}rtn", l5x,
               f"{n_prog} program(s) x {per_prog} routine(s) = 100 routines, with the same "
               f"constant {_TOTAL_RUNGS} rungs split across them. All four files in this group "
               f"have IDENTICAL routine count and IDENTICAL content and differ only in how many "
               f"programs those routines sit in. If the structural cost is per-routine only, all "
               f"four land on the same number; if there is a real per-program term they separate "
               f"in proportion to {n_prog}. This is the cell that decides it, and the one no real "
               f"file can provide -- in a real project program count and routine count always "
               f"move together. " + _WHY)


def main() -> None:
    group_routine_count()
    group_program_count()
    group_crossed()
    print("\nDone. 19 files.")


if __name__ == "__main__":
    main()
