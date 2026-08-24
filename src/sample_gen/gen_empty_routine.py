"""OQ-EMPTYROUTINE (2026-08-24, found while investigating James's manual
l81_v35 fw_baseline entry). A self-closing `<Routine Name="X" Type="RLL"/>`
(no RLLContent child at all) is currently silently skipped by
parse_rll_routines -- charged 0 bytes, as if it doesn't exist. l81_v35
(real Capacity 18,112 vs this engine's flat 13,296 prediction, a +4,816
gap exactly equal to fixed_base_per_routine) is the first real evidence
this might be wrong -- but it's only 1 data point, and real corpus
inspection found this exact shape in 15 of James's own production files
(up to 10 such routines in one file, samples/local/SJ_Gormley...), so
getting this right matters for real prediction accuracy, not just a
synthetic edge case.

This batch isolates it cleanly and cheaply, no firmware variable involved
(unlike l81_v35, which confounds firmware with this effect) -- pure
routine-count sweep, same 1756-L81E/35.05 every other confirmed file uses:

  1/2/3 self-closing routines in one program, no RLLContent on any of
  them. If the true cost scales the same way ordinary (non-empty)
  routines do (fixed_base_per_routine per routine, confirmed for real
  content-bearing routines throughout this project), n=1/2/3 should show
  a clean linear rate -- if it's some OTHER constant, or flat regardless
  of count, that's real and different from the naive assumption.

Run: python -m sample_gen.gen_empty_routine
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.manifest import append_manifest_row, write_sample_unmodeled
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"


def _write_unmodeled(l5x: str, out_name: str, description: str) -> None:
    # write_sample_unmodeled, not write_sample: the whole POINT of this
    # batch is that the current engine predicts 0 extra bytes for these
    # self-closing routines (that's the exact gap under investigation),
    # so there is no meaningful "predicted_bytes" to assert against yet.
    out_path = OUT_ROOT / f"{out_name}.L5X"
    write_sample_unmodeled(l5x, out_path)
    append_manifest_row(out_name, description, "logic_instr", out_path, 0)
    print(f"Wrote {out_path} (predicted N/A -- self-closing routines currently size as 0)")


def _self_closing_routine_xml(name: str) -> str:
    return f'<Routine Name="{name}" Type="RLL"/>'


def group_empty_routine_count_sweep() -> int:
    n = 0
    for count in (1, 2, 3):
        routine_names = ["EmptyMain"] + [f"Empty{i}" for i in range(1, count)]
        routines_xml = "\n".join(_self_closing_routine_xml(name) for name in routine_names)
        # Named distinctly from the wrapper's own default "MainProgram"
        # (real name-collision risk otherwise -- two Programs sharing one
        # name is a real Studio 5000 import error, same class of bug
        # already caught once in this project for AOI/UDT name collisions).
        program_xml_block = (
            '<Program Name="EmptyRoutineProg" TestEdits="false" MainRoutineName="EmptyMain" '
            'Disabled="false" UseAsFolder="false">\n'
            "<Tags>\n</Tags>\n"
            f"<Routines>\n{routines_xml}\n</Routines>\n"
            "</Program>"
        )
        # build_l5x always emits its own default MainProgram/MainRoutine
        # (with real RLLContent) unless overridden entirely -- there's no
        # "skip the default program" switch, so this passes the whole
        # custom program via extra_programs_xml/extra_scheduled_programs_xml
        # and leaves tags_xml/extra_rungs_xml empty, matching how
        # gen_xprogref.py's n-prog groups already build fully custom
        # programs alongside (never instead of) the wrapper's own.
        # Since THIS test needs ONLY the self-closing routines and no
        # confound from the wrapper's own real-content MainRoutine, the
        # wrapper's default program is intentionally left with its usual
        # single default rung -- the delta between count=1/2/3 below
        # isolates the self-closing routines' own marginal cost cleanly
        # regardless of what the fixed default program costs.
        l5x = build_l5x(
            target_name=f"EmptyRoutineN{count}",
            tags_xml="",
            extra_programs_xml=program_xml_block,
            extra_scheduled_programs_xml='<ScheduledProgram Name="EmptyRoutineProg"/>',
        )
        _write_unmodeled(
            l5x, f"emptyroutine_n{count:02d}",
            f"{count} self-closing <Routine .../> element(s) (no RLLContent at all) in one "
            f"program, alongside the wrapper's own normal default program -- OQ-EMPTYROUTINE "
            f"count sweep, isolates the real cost of a routine with no content, currently "
            f"silently sized as 0 by parse_rll_routines",
        )
        n += 1
    return n


def main() -> None:
    group_empty_routine_count_sweep()
    print("\nDone. 3 files.")


if __name__ == "__main__":
    main()
