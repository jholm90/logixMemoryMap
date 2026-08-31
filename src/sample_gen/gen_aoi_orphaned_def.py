"""Orphaned AOI definition cost -- James, 2026-08-30, real open question found
while reviewing a real confidential customer project (not committed, never
named here): 12 of that project's 39 declared AddOnInstructionDefinitions
had ZERO real tag anywhere (even transitively, through another AOI's own
LocalTags) that instantiated them -- confirmed by direct grep of the raw
L5X, independent of this project's own parser. report.py's own definition-
cost pass only computes a cost for a UDT/AOI name if it's reachable from
some actually-SIZED tag (`referenced_udts`, see report.py's `definition_
entries` loop) -- an AOI declared in the project but never instantiated
anywhere gets $0 predicted, no error, nothing flagged.

Whether that's correct is a real, empirical, currently-UNKNOWN question --
not something derivable from the L5X alone (same class of question as
everything else in docs/MEMORY_MODEL.md's "estimated" bucket): does Logix
Designer's compiler still reserve real controller memory for an AOI
definition's own Parameters/LocalTags structure even when the AOI is never
instantiated anywhere in the project, or does it get dropped entirely
(dead-code-eliminated) before download?

This file builds the one clean, minimal test that isolates it: two files,
byte-identical except one has a live instance+call of the AOI and the
other has the SAME AOI defined but never instantiated or called anywhere.
If real Capacity for the "referenced" file minus real Capacity for the
"orphaned" file equals this project's already-wired AOI definition+instance
formula, orphaned AOI defs really do cost nothing extra beyond baseline
(current behavior is right). If the orphaned file's real Capacity is
close to the referenced file's (not baseline), orphaned AOI definitions DO
cost real memory and `referenced_udts`-gating the definition-cost pass is
a real, systemic under-count bug -- worth checking given how common
imported/library AOIs that aren't all actively used are in real projects.

The AOI itself is deliberately moderate, not trivial (5 DINT LocalTags + 2
DINT Input params + 1 BOOL Output param), matching the rough shape/scale
of the real orphaned AOIs found in the source project (small date-math/
utility AOIs, not empty shells) -- a single-DINT-param AOI's definition
cost might round-trip too cleanly to be a meaningful test of this
specific question.

Run: python -m sample_gen.gen_aoi_orphaned_def
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, aoi_xml, rung_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "aoi"


def _write(l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "aoi", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


def _utility_aoi() -> tuple[str, list[MemberSpec]]:
    """A moderate-complexity utility AOI -- 2 DINT inputs, 1 BOOL output,
    5 DINT local scratch tags. Rough scale-match to the real orphaned AOIs
    found in the source review (small date/utility helpers), not a
    trivial single-param stub."""
    # REAL BUG FOUND 2026-08-31 (James, real Studio 5000 verify error
    # class found via composite_realistic_02/03.ACD, same root cause
    # found here by lint.py's new aoi_call_arg_count_mismatch check):
    # these params defaulted required=False/visible=False (MemberSpec's
    # own default), which real Logix treats as HIDDEN from the
    # instruction's own call signature entirely -- but group_referenced
    # below calls UtilOrphanTest with 3 real arguments anyway
    # ("UtilOrphanTest(UtilInstance,0,0,OutBit);"), a genuine argument-
    # count mismatch. Fixed with required=True (accepts either a
    # hardcoded value or a tag, matching this file's own call args).
    return aoi_xml(
        "UtilOrphanTest",
        input_params=[MemberSpec("InA", "DINT", required=True), MemberSpec("InB", "DINT", required=True)],
        output_params=[MemberSpec("OutFlag", "BOOL", required=True)],
        local_tags=[
            MemberSpec("Wrk1", "DINT"), MemberSpec("Wrk2", "DINT"), MemberSpec("Wrk3", "DINT"),
            MemberSpec("Wrk4", "DINT"), MemberSpec("Wrk5", "DINT"),
        ],
    )


def group_referenced() -> None:
    aoi_def, storage_members = _utility_aoi()
    instance_tag = tag_xml("UtilInstance", "UtilOrphanTest", udt_members=storage_members)
    call_rung = rung_xml(0, "UtilOrphanTest(UtilInstance,0,0,OutBit);")
    out_bit_tag = tag_xml("OutBit", "BOOL")
    l5x = build_l5x(
        target_name="AoiOrphanReferenced", tags_xml=instance_tag + "\n" + out_bit_tag,
        extra_aoi_xml=aoi_def, extra_rungs_xml=call_rung,
    )
    _write(
        l5x, "aoi_orphaned_referenced",
        "Baseline half of the orphaned-AOI-definition pair (OQ-AOIORPHAN): UtilOrphanTest AOI "
        "(2 DINT In + 1 BOOL Out + 5 DINT LocalTags) DECLARED, instantiated as UtilInstance, and "
        "CALLED from a rung -- the normal, referenced case. Byte-identical to "
        "aoi_orphaned_unreferenced except for the instance tag + call rung, isolating whether an "
        "AOI definition that's never instantiated anywhere still costs real memory.",
    )


def group_unreferenced() -> None:
    aoi_def, _storage_members = _utility_aoi()
    l5x = build_l5x(
        target_name="AoiOrphanUnreferenced", tags_xml="",
        extra_aoi_xml=aoi_def,
    )
    _write(
        l5x, "aoi_orphaned_unreferenced",
        "Orphaned half of the orphaned-AOI-definition pair (OQ-AOIORPHAN): the SAME UtilOrphanTest "
        "AOI definition (2 DINT In + 1 BOOL Out + 5 DINT LocalTags) as aoi_orphaned_referenced, "
        "DECLARED but never instantiated as a tag or called anywhere in this file -- current engine "
        "predicts this identically to an empty baseline (0 extra bytes for the AOI), since "
        "report.py's definition-cost pass only counts a UDT/AOI reachable from an actually-sized "
        "tag. Real Capacity delta between this file and aoi_orphaned_referenced answers whether "
        "that's correct.",
    )


def main() -> None:
    group_referenced()
    group_unreferenced()


if __name__ == "__main__":
    main()
