"""OQ-BRANCHDEPTH closeout (2026-08-25, James: "Please do what it takes to
close this. Does bst/bnd ([,]) branches take memory? If I have 30 deep or
condition in ladder logic it must cost more than 30 xio").

The 3 existing branchdepth_legs01/03/05 points already ANSWER James's first
question with real data, no new capture needed: legs01 (no branch) is an
exact 0.00% match to the plain per-instruction sum, but legs03 is
under-predicted by +16/rung and legs05 by +24/rung -- the branch bracket
structure itself (compiled internally to BST/NXB/BND, not modeled at all by
this project's regex-based per-instruction-mnemonic parser) DOES cost real
memory beyond the sum of each leg's own instruction weight. Confirmed, not
hypothesized.

What's still open is the SHAPE of that cost as leg count grows -- only 2
non-trivial points existed (legs03=+16/rung, legs05=+24/rung, a dropping
per-leg marginal rate: +8/leg then +4/leg, not linear). This batch adds 8
more leg-count points (2/4/6/8/10/15/20/30) to actually nail the curve,
including legs=30 as a literal real data point for James's own "if I have
30 deep" example rather than an extrapolation from n=5.

Same isolation shape as gen_branch_empty_rungs.py's group_branch_depth:
fixed RUNG_COUNT=1000, each rung `[XIC(B0),XIC(B1),...]OTE(Bn);` with one
leg per declared BOOL tag, converging to a single OTE. BOOL tag pool
extended to 31 tags (30 legs + 1 shared output) to cover the widest branch
tested here.

Run: python -m sample_gen.gen_branchdepth_closeout
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import rungs_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"

RUNG_COUNT = 1000
LEG_COUNTS = [2, 4, 6, 8, 10, 15, 20, 30]

# 30 legs + 1 shared output tag = 31 tags, enough for the widest branch here.
_POOL_TAGS_XML = "\n".join(tag_xml(f"B{i}", "BOOL") for i in range(max(LEG_COUNTS) + 1))


def _write(l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "logic_instr", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


def _branch_rung(leg_count: int):
    legs = ",".join(f"XIC(B{i})" for i in range(leg_count))
    out_tag = f"B{leg_count}"

    def fn(i: int) -> str:
        return f"[{legs}]OTE({out_tag});"
    return fn


def group_branch_depth_closeout() -> None:
    for legs in LEG_COUNTS:
        rungs = rungs_xml(RUNG_COUNT, _branch_rung(legs))
        l5x = build_l5x(target_name=f"BranchDepthC{legs}", tags_xml=_POOL_TAGS_XML, extra_rungs_xml=rungs)
        _write(
            l5x, f"branchdepthc_legs{legs:02d}_n{RUNG_COUNT:05d}",
            f"{RUNG_COUNT} rungs, {legs}-leg parallel branch converging to a single OTE -- "
            f"OQ-BRANCHDEPTH closeout, one of 8 new leg-count points (2/4/6/8/10/15/20/30) "
            f"added to the existing legs01/03/05 set to fit the real per-leg cost curve "
            f"(confirmed non-linear: +8/leg then +4/leg between the first 2 non-trivial points)",
        )


def main() -> None:
    group_branch_depth_closeout()
    print(f"\nDone. {len(LEG_COUNTS)} files.")


if __name__ == "__main__":
    main()
