"""Phase 4 (bit logic round 1) closeout (2026-08-26, James: "TASKS.md Phase
4 -- Logic sizing round 1 (bit logic) should be 100% complete by now... do
what it takes to make it complete now"). Audit found XIC/OTE/XIO/OTL/OTU
and comment-cost (OQ-COMMENTS, comments = 0 blocks) all genuinely CONFIRMED
already -- but two checklist items had literally never been generated:
branch depth variations, and empty rungs at scale. This batch closes both.

Branch (parallel-leg) syntax confirmed real, not guessed, from
samples/local/311DGeneratedProgram.L5X's own rung Text:
`[XIC(CmdReset) ,XIC(Inhibit) ... ]XIO(...)OTE(...);` -- square brackets,
comma-separated legs, each leg itself a plain instruction chain. This is
inline rung TEXT, not a separate XML construct -- rung_xml/rungs_xml
already support arbitrary text, no builders.py change needed.

  1. group_branch_depth -- fixed RUNG_COUNT=1000 (comparable to the
     already-confirmed 20-blocks/rung XIC marginal rate), 3 files:
     legs=1 (a plain series rung, XIC/OTE-shaped -- the no-branch control,
     should reproduce the already-known rate as an internal sanity check),
     legs=3, legs=5 (genuine `[leg,leg,leg]OTE(...)` parallel branches).
     Isolates whether the branch structure itself (the `[`/`,`/`]`
     bracket overhead) costs anything beyond the naive sum of each leg's
     own already-confirmed per-instruction weight.
  2. group_empty_rungs -- a routine of N content-free rungs, each just
     `NOP();` (real, confirmed-safe syntax -- it's the exact shape
     wrapper.py's own default template rung already uses; a literally
     bare `;`-only rung has zero real-corpus precedent anywhere in
     samples/local/'s 47 files, so it's NOT used here per this project's
     standing "never guess Rockwell syntax" rule). NOP's own weight was
     only ever inferred SINGLY before now (16 blocks/rung, backed out
     from exactly one occurrence while deriving the CAM predefined-array
     formula) -- this is its first dedicated multi-count sweep. N=10/100/
     1000, no comments (comment cost already separately confirmed zero).

Run: python -m sample_gen.gen_branch_empty_rungs
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import rung_xml, rungs_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"

BRANCH_RUNG_COUNT = 1000
EMPTY_RUNG_COUNTS = [10, 100, 1000]

# Fixed, fully-declared BOOL pool -- 6 tags covers the widest branch (5 legs
# + 1 output), reused across every rung (same fixed-pool convention as
# gen_logic_sweep.py's _POOL_TAGS, so tag-data cost stays constant across
# this whole batch and any Capacity movement is attributable to rung text).
_POOL_TAGS_XML = "\n".join(tag_xml(f"B{i}", "BOOL") for i in range(6))


def _write(l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "logic_instr", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


# ---------------------------------------------------------------------------
# 1. Branch depth: 1 (no branch, control) / 3 / 5 parallel legs.
# ---------------------------------------------------------------------------

def _series_rung(i: int) -> str:
    return "XIC(B0)OTE(B1);"


def _branch_rung(leg_count: int):
    legs = ",".join(f"XIC(B{i})" for i in range(leg_count))
    out_tag = f"B{leg_count}"  # B3 for legs=3 (B0-B2 used), B5 for legs=5 (B0-B4 used)

    def fn(i: int) -> str:
        return f"[{legs}]OTE({out_tag});"
    return fn


def group_branch_depth() -> None:
    for legs in (1, 3, 5):
        fn = _series_rung if legs == 1 else _branch_rung(legs)
        rungs = rungs_xml(BRANCH_RUNG_COUNT, fn)
        l5x = build_l5x(target_name=f"BranchDepth{legs}", tags_xml=_POOL_TAGS_XML, extra_rungs_xml=rungs)
        shape = "plain series rung (no branch, control)" if legs == 1 else f"{legs}-leg parallel branch"
        _write(
            l5x, f"branchdepth_legs{legs:02d}_n{BRANCH_RUNG_COUNT:05d}",
            f"{BRANCH_RUNG_COUNT} rungs, {shape} converging to a single OTE -- Phase 4 branch-depth "
            f"checklist item, isolates whether branch bracket structure costs anything beyond the sum "
            f"of each leg's own already-confirmed per-instruction weight",
        )


# ---------------------------------------------------------------------------
# 2. Empty rungs (no instructions at all) at scale.
# ---------------------------------------------------------------------------

def group_empty_rungs() -> None:
    for count in EMPTY_RUNG_COUNTS:
        rungs = "\n".join(rung_xml(i, "NOP();") for i in range(count))
        l5x = build_l5x(target_name=f"EmptyRungs{count}", tags_xml="", extra_rungs_xml=rungs)
        _write(
            l5x, f"emptyrungs_n{count:05d}",
            f"{count} content-free rungs (NOP() only, the same shape wrapper.py's own default rung "
            f"uses) -- Phase 4 empty-rungs-at-scale checklist item, first dedicated multi-count sweep "
            f"of NOP's own weight (previously only inferred singly, from 1 occurrence, backing out the "
            f"CAM predefined-array formula)",
        )


def main() -> None:
    group_branch_depth()
    group_empty_rungs()
    print("\nDone. 6 files.")


if __name__ == "__main__":
    main()
