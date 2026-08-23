"""AOI-instance-array packing resolution sweep (James, 2026-08-25):
"Your final notes on strings and aois need more work. Generate as many
l5x files as needed to resolve all possible scenarios for 100% accuracy."

Follows up the 2026-08-24 OQ-AOIDEF finding: a BOOL-heavy AOI shape ("
RealisticAOI"/"RealisticAOI50", 5 DINT+5 BOOL In / 5 DINT+5 BOOL Out /
5 REAL+5 BOOL Local) showed real per-element cost inside an ARRAY of
instances (~64 bytes/element, solved from 2 real count points: n=10 and
n=50) at roughly HALF the engine's own already-confirmed per-instance
size for that shape (128 bytes, matching the n=1 standalone-tag case
exactly). Leading hypothesis: AOI BOOL Parameters/LocalTags pack 8-per-
byte specifically once inside an array of instances (OQ-AOIBOOLPACK's
real answer, surfacing only in the array context) -- but only 2 array
data points existed, both using the same BOOL-heavy shape, so "BOOL-
specific" couldn't be distinguished from "arrays of AOI instances are
just cheaper per-element in general."

Three AOI shapes, each with a real per-instance-array count sweep dense
enough to solve base+per-element cleanly AND catch a small-N anomaly
(matching this project's own established pattern -- see udt_definition's
n=1,2 anomaly, arraypack_odd3b's n=1 anomaly):

  A. group_pure_atomic -- 10 DINT In + 10 DINT Out + 10 REAL Local, ZERO
     BOOL anywhere. If this shape's array per-element rate matches the
     engine's own UDT-style prediction exactly (unlike the BOOL-heavy
     case), that CONFIRMS the ~50% array discount is BOOL-specific, not a
     general array-of-AOI effect.
  B. group_pure_bool -- 10 BOOL In + 10 BOOL Out + 10 BOOL Local, nothing
     else. Cleanest possible read on the BOOL-array-packing question, no
     DINT/REAL confounding the per-element math.
  C. group_mixed_expanded -- same composition as the original "
     RealisticAOI" (5 DINT+5 BOOL In/Out, 5 REAL+5 BOOL Local) that
     surfaced this finding, but with MORE count points (the original only
     had def_only/1/10/50) to firm up the 64-byte/element reading with a
     real multi-point linear fit instead of 2 points.

Each shape gets: def_only (0 instances, isolates definition cost), then
array counts 1/5/10/25/50 (1 is a single-element array, not a standalone
tag -- deliberately different from the existing "_1_instance" separate-
tag files, to keep this sweep apples-to-apples as "array of N" throughout
rather than mixing array-vs-standalone-tag shapes).

Run: python -m sample_gen.gen_aoi_array_packing
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, aoi_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "aoi"

COUNTS = [1, 5, 10, 25, 50]


def _write(l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "aoi_array_packing", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


def _sweep(aoi_name: str, inputs: list[MemberSpec], outputs: list[MemberSpec], locals_: list[MemberSpec],
           out_prefix: str, shape_desc: str) -> None:
    definition, storage = aoi_xml(aoi_name, inputs, outputs, [], locals_)

    l5x = build_l5x(target_name=aoi_name, tags_xml="", extra_aoi_xml=definition)
    _write(l5x, f"{out_prefix}_def_only", f"{shape_desc}, 0 instances")

    for n in COUNTS:
        tag = tag_xml("TestInstanceArray", aoi_name, dimensions=(n,), udt_members=storage)
        l5x = build_l5x(target_name=aoi_name, tags_xml=tag, extra_aoi_xml=definition)
        _write(l5x, f"{out_prefix}_array_n{n:02d}", f"{shape_desc}, array of {n} instances")


def group_pure_atomic() -> None:
    inputs = [MemberSpec(f"In{i}", "DINT") for i in range(10)]
    outputs = [MemberSpec(f"Out{i}", "DINT") for i in range(10)]
    locals_ = [MemberSpec(f"Loc{i}", "REAL") for i in range(10)]
    _sweep("AoiPureAtomic", inputs, outputs, locals_, "aoipack_atomic",
           "AOI, 10 DINT In / 10 DINT Out / 10 REAL Local, zero BOOL")


def group_pure_bool() -> None:
    inputs = [MemberSpec(f"In{i}", "BOOL") for i in range(10)]
    outputs = [MemberSpec(f"Out{i}", "BOOL") for i in range(10)]
    locals_ = [MemberSpec(f"Loc{i}", "BOOL") for i in range(10)]
    _sweep("AoiPureBool", inputs, outputs, locals_, "aoipack_bool",
           "AOI, 10 BOOL In / 10 BOOL Out / 10 BOOL Local, all BOOL")


def group_mixed_expanded() -> None:
    inputs = [MemberSpec(f"In{i}", "DINT") for i in range(5)] + [MemberSpec(f"InB{i}", "BOOL") for i in range(5)]
    outputs = [MemberSpec(f"Out{i}", "DINT") for i in range(5)] + [MemberSpec(f"OutB{i}", "BOOL") for i in range(5)]
    locals_ = [MemberSpec(f"Loc{i}", "REAL") for i in range(5)] + [MemberSpec(f"LocB{i}", "BOOL") for i in range(5)]
    _sweep("AoiMixedExpand", inputs, outputs, locals_, "aoipack_mixed",
           "AOI, 5 DINT+5 BOOL In / 5 DINT+5 BOOL Out / 5 REAL+5 BOOL Local -- same shape as the original "
           "RealisticAOI finding, expanded count sweep")


def main() -> None:
    group_pure_atomic()
    group_pure_bool()
    group_mixed_expanded()
    total = 3 * (1 + len(COUNTS))
    print(f"\nDone. {total} files.")


if __name__ == "__main__":
    main()
