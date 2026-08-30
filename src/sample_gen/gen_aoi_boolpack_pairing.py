"""OQ-AOIBOOLPACK-PAIRING (2026-08-30): closes the gap the previous
"confirmed exact, 15 real points" aoi_array claim never actually tested --
dense/consecutive array-instance counts. Reconciling 27 already-captured-
but-unreconciled points (aoipack_bool_array_n*, aoipack_bool_boundary_n16-96,
aoipack_bool_dense_array_n16-40, aoipack_mc10/mc20/mc60_b*_array_n01/10/25)
proved the formula wrong: real bytes for a single-packed-word (bool_count
<=32) AOI array follow `8*ceil(n/2) + B`, an odd-n array costing 4 bytes
more than the even-n prediction -- but B (20 for a 10-BOOL/all-Input AOI,
44 for 20-BOOL/all-Input, 28 for the original 30-BOOL/3-way-split shape)
does not extrapolate cleanly across bool_count, and the 60-BOOL/2-word case
doesn't fit `8*ceil(n/2)+const` at all from only 3 sparse points (n=1/10/25).
See docs/OPEN_QUESTIONS.md OQ-AOIBOOLPACK-PAIRING for the full data table.

Two things this batch adds, deliberately NOT padded to the 60-file floor
(James, 2026-08-25: "The 60-file floor is not a quota to pad toward"):

  A. group_dense_membercount -- dense/consecutive n (2,3,4,6,8,12) for each
     of bool_count=10/20/60 (all-Input, single section, matching the
     already-captured mc10/mc20/mc60 shape exactly so the new points slot
     into the same real dataset). For bc=10/20 this densifies the already-
     strong `8*ceil(n/2)+B` fit; for bc=60 (2 packed words/instance) it's
     the FIRST dense data at all -- the 3 existing points are too sparse to
     tell whether the multi-word case has its own pairing period (every 2
     instances? every word-crossing?) or is genuinely non-periodic.

  B. group_section_split_isolation -- bool_count=30 held constant, but
     ALL-INPUT (single section) instead of the original 3-way split (10 In
     + 10 Out + 10 Local, the shape group B in gen_aoi_array_packing.py
     already covers). If B changes between this and the existing 3-way
     data at the same n, that confirms the per-section split (not just
     total bool_count) drives the flat offset -- the current parser only
     tracks a flat bool_count, so this would mean a real architecture
     change (per-section bool counts) is needed to close this properly,
     not just a constant tweak.

Run: python -m sample_gen.gen_aoi_boolpack_pairing
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, aoi_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

AOI_OUT = Path(__file__).parent.parent.parent / "samples" / "generated" / "aoi"


def _write(l5x: str, out_name: str, description: str) -> int:
    out_path = AOI_OUT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "aoi_array_packing", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")
    return 1


DENSE_COUNTS = [2, 3, 4, 6, 8, 12]


def group_dense_membercount() -> int:
    n = 0
    for bool_count in [10, 20, 60]:
        aoi_name = f"AoiBpDense{bool_count}"
        inputs = [MemberSpec(f"InB{i}", "BOOL") for i in range(bool_count)]
        definition, storage = aoi_xml(aoi_name, inputs, [], [], [])
        for count in DENSE_COUNTS:
            tag = tag_xml("TestInstanceArray", aoi_name, dimensions=(count,), udt_members=storage)
            l5x = build_l5x(target_name=aoi_name, tags_xml=tag, extra_aoi_xml=definition)
            n += _write(l5x, f"aoibp_dense_bc{bool_count:02d}_n{count:02d}",
                        f"AOI, {bool_count} BOOL Input params (single section), array of {count} "
                        f"instances -- OQ-AOIBOOLPACK-PAIRING dense-n closeout, matches the existing "
                        f"mc{bool_count:02d}_b{bool_count:02d} shape at n=1/10/25 exactly")
    return n


SPLIT_COUNTS = [1, 5, 10, 16, 25]


def group_section_split_isolation() -> int:
    n = 0
    aoi_name = "AoiBpSplitAllInput30"
    inputs = [MemberSpec(f"InB{i}", "BOOL") for i in range(30)]
    definition, storage = aoi_xml(aoi_name, inputs, [], [], [])
    for count in SPLIT_COUNTS:
        tag = tag_xml("TestInstanceArray", aoi_name, dimensions=(count,), udt_members=storage)
        l5x = build_l5x(target_name=aoi_name, tags_xml=tag, extra_aoi_xml=definition)
        n += _write(l5x, f"aoibp_split_allinput30_n{count:02d}",
                    f"AOI, 30 BOOL Input params (single section, all-Input), array of {count} "
                    f"instances -- OQ-AOIBOOLPACK-PAIRING section-split isolation, same total "
                    f"bool_count=30 as the existing 3-way-split (10 In+10 Out+10 Local) shape at the "
                    f"same n, to test whether section split (not just bool_count) drives the flat "
                    f"per-array offset B")
    return n


def main() -> None:
    total = 0
    for fn in [group_dense_membercount, group_section_split_isolation]:
        count = fn()
        print(f"{fn.__name__}: {count} file(s)")
        total += count
    print(f"\nDone. {total} files.")


if __name__ == "__main__":
    main()
