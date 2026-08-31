"""OQ-JSRPARAMCOST: are multiple DISTINCT subroutines called from the same
caller routine simply additive (sum of each target's own A(n)), or is
there a real, currently-unmodeled marginal cost for having more than one?
(2026-08-31, James: "Just confirming that you did multiple subroutines
per program in your testing" -- direct check confirms no.)

Every JSR calibration file this project has ever built (old corpus and
today's target-content-scale/mid-chain files alike) calls exactly ONE
distinct target routine -- varied by param count, rung count, RET-point
count, or content size, but always a single target name. report.py's
`jsr_target_param_counts` mechanism assumes each distinct target's own
A(n) declaration cost is simply additive across a file (a dict keyed by
target name, summed independently) -- a real, reasonable, but NEVER
empirically confirmed assumption.

Real AccuTally data (confidential, not committed) has real examples of
one caller routine invoking several different subroutines --
`DataToDataBase_K` alone makes 5 distinct JSR calls in the same routine.

3 files, DISTINCT target COUNT as the only variable (1/3/5 different
target routines, all called from the same MainRoutine, each target a
trivial 0-param leaf with no SBR/RET per the real corpus norm for 0-param
targets -- see gen_jsr_target_content_scale.py), everything else held
minimal and fixed. Predicted total should be exactly baseline + n *
A(0) if the current additive-by-name assumption is right; any real
Capacity delta from that straight line proves a real per-additional-
distinct-target cost this project has never modeled.

Run: python -m sample_gen.gen_jsr_multi_distinct_targets
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import rung_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"

N_TARGETS = (1, 3, 5)


def _target_xml(name: str) -> str:
    # 0-param leaf target, no SBR/RET -- the real, representative shape
    # for a 0-param subroutine (James, 2026-08-31, confirmed against the
    # real corpus in samples/local/, see gen_jsr_target_content_scale.py).
    return (
        f'<Routine Name="{name}" Type="RLL">'
        f"<RLLContent>{rung_xml(0, 'NOP();')}</RLLContent>"
        "</Routine>"
    )


def _write(out_name: str, l5x: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "jsr_sbr_ret", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


def main() -> None:
    for n in N_TARGETS:
        target_names = [f"JsrMultiTarget{n:02d}_{i:02d}" for i in range(n)]
        targets_xml = "\n".join(_target_xml(t) for t in target_names)
        call_rungs = "\n".join(rung_xml(i, f"JSR({t},0);") for i, t in enumerate(target_names))
        l5x = build_l5x(
            target_name=f"JsrMultiTarget{n:02d}", tags_xml="",
            extra_rungs_xml=call_rungs, extra_routines_xml=targets_xml,
        )
        _write(
            f"jsr_multi_distinct_targets_{n:02d}",
            l5x,
            f"MainRoutine calls {n} genuinely DISTINCT 0-param subroutines (one JSR rung each, "
            f"no SBR/RET per the real 0-param norm) -- OQ-JSRPARAMCOST distinct-target-count "
            f"isolation: is each target's A(0) declaration cost simply additive across a file "
            f"(report.py's current, never-confirmed assumption), or is there a real per-"
            f"additional-distinct-target marginal cost this project has never tested (every "
            f"prior JSR calibration file, old and new, has called exactly ONE distinct target)?",
        )


if __name__ == "__main__":
    main()
