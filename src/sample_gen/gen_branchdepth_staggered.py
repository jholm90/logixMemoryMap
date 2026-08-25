"""OQ-BRANCHDEPTH staggered/nested-branch sweep (James, 2026-08-25):
"factor in staggered branches where root has two elements, 1st branch has
two elements over the root 1st, 2nd branch has 2 elements over 1st branch
1st item etc.." -- a genuinely different axis from the existing flat
leg-count sweep (`gen_branchdepth_closeout.py`, WIDTH: 1 level, N legs).
This is DEPTH: always exactly 2 legs per level, but each level's first leg
recurses into another 2-leg branch, cascading down one side -- a staircase
of nested brackets, not a wide flat branch.

Real syntax confirmed 2026-08-25 by grepping the full samples/local/
corpus for genuine nested brackets (a `[` opening before its enclosing
`]` closes) -- 624 real rungs found using this pattern, e.g.
311DGeneratedProgram.L5X: `[XIC(RequestEnterMem) [XIC(ClearEntry)
,XIC(UnlockSV) ] ,XIC(ForceEnterMem) ]OTE(UnlockSV);` -- exactly the
depth=2 shape this generator builds (root 2 legs, leg 1 itself contains a
nested 2-leg branch). Depth=3+ is the same real rule applied recursively
(a nested branch's own first leg containing a further nested branch) --
not a new construct, the same bracket-nesting grammar already confirmed
real, just staggered one more level down.

Shape at depth D (D=1 is the trivial 2-leg case, matching
`branchdepthc_legs02` as an internal cross-check):
  D=1: [XIC(B0),XIC(B1)]OTE(Out);
  D=2: [XIC(B0)[XIC(B1),XIC(B2)],XIC(B3)]OTE(Out);
  D=3: [XIC(B0)[XIC(B1)[XIC(B2),XIC(B3)],XIC(B4)],XIC(B5)]OTE(Out);
  ... each level adds 2 more BOOL tags and one more nested bracket pair,
  always recursing into the FIRST leg of the previous level (the
  "staggered"/cascading shape James described, not a balanced tree).

Fixed RUNG_COUNT=1000 (comparable to the flat leg-count sweep), depths
1-6 tested (12 BOOL tags at the deepest level).

Run: python -m sample_gen.gen_branchdepth_staggered
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import rungs_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"

RUNG_COUNT = 1000
DEPTHS = [1, 2, 3, 4, 5, 6]

# Deepest depth (6) uses 2*6=12 BOOL tags + 1 output tag.
_POOL_TAGS_XML = "\n".join(tag_xml(f"B{i}", "BOOL") for i in range(2 * max(DEPTHS) + 1))


def _write(l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "logic_instr", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


def _staggered_branch(depth: int) -> tuple[str, int]:
    """Returns (bracket text, next unused tag index), recursing depth-1
    more times into the first leg."""
    counter = [0]

    def build(level: int) -> str:
        a_tag = f"B{counter[0]}"
        counter[0] += 1
        if level < depth:
            nested = build(level + 1)
            leg_a = f"XIC({a_tag}){nested}"
        else:
            leg_a = f"XIC({a_tag})"
        b_tag = f"B{counter[0]}"
        counter[0] += 1
        leg_b = f"XIC({b_tag})"
        return f"[{leg_a},{leg_b}]"

    text = build(1)
    return text, counter[0]


def group_branchdepth_staggered() -> None:
    for depth in DEPTHS:
        branch_text, next_idx = _staggered_branch(depth)
        out_tag = f"B{next_idx}"

        def fn(i: int, branch_text=branch_text, out_tag=out_tag) -> str:
            return f"{branch_text}OTE({out_tag});"

        rungs = rungs_xml(RUNG_COUNT, fn)
        l5x = build_l5x(target_name=f"BranchDepthStag{depth}", tags_xml=_POOL_TAGS_XML,
                         extra_rungs_xml=rungs)
        _write(
            l5x, f"branchdepthstag_d{depth:02d}_n{RUNG_COUNT:05d}",
            f"{RUNG_COUNT} rungs, staggered/nested branch depth={depth} (always 2 legs per level, "
            f"recursing into the first leg each time -- root[2] -> leg1 contains nested[2] -> "
            f"nested's leg1 contains nested-nested[2] -> ...) converging to a single OTE -- "
            f"OQ-BRANCHDEPTH nested-branch axis, distinct from the flat leg-count (WIDTH) sweep, "
            f"real bracket-nesting syntax confirmed against samples/local/ corpus",
        )


def main() -> None:
    group_branchdepth_staggered()
    print(f"\nDone. {len(DEPTHS)} files.")


if __name__ == "__main__":
    main()
