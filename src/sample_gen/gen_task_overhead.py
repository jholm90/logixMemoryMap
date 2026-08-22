"""OQ item 13 (roadmap 2026-08-22): per-Task overhead, isolated from logic
content. Each extra Task gets its own trivial Program (single NOP rung, no
tags) so any Capacity delta is attributable to the Task/Program/Routine
scaffolding itself, not the logic inside it -- distinct from JSR call-site
cost (already confirmed, 72 blocks/call) and from ordinary per-instruction
weight (also confirmed). Real Logix only allows one Continuous task per
controller, so extra Tasks here are Type="Periodic" (see task_xml()).

Files: 1/2/3 total Tasks (the baseline default MainTask + 0/1/2 extra
Periodic Task+Program pairs). Compare against the already-known empty-
project baseline (18,128 blocks, 1 Task) to isolate the per-Task marginal.

Run: python -m sample_gen.gen_task_overhead
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import program_xml, task_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"


def _write(l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "logic_instr", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


def main() -> None:
    for extra_task_count in [1, 2]:
        programs = []
        tasks = []
        for i in range(extra_task_count):
            prog_name = f"ExtraProgram{i}"
            programs.append(program_xml(prog_name))
            tasks.append(task_xml(f"ExtraTask{i}", prog_name, task_type="PERIODIC"))

        l5x = build_l5x(
            target_name=f"TaskOverheadN{extra_task_count}",
            tags_xml="",
            extra_programs_xml="\n".join(programs),
            extra_tasks_xml="\n".join(tasks),
        )
        total_tasks = 1 + extra_task_count
        _write(l5x, f"taskoverhead_n{total_tasks:02d}tasks",
               f"{total_tasks} total Tasks (1 Continuous + {extra_task_count} Periodic), each extra Task's "
               f"Program has only a single NOP rung -- isolates per-Task scaffolding cost from logic content")

    print("\nDone. 2 files.")


if __name__ == "__main__":
    main()
