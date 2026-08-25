"""OQ-AOIDEF closeout batch 2 (2026-08-25, James: "Generate enough new
samples now to close this... I haven't seen any AOI L5X files today").
Two of the three remaining OQ-AOIDEF threads get new generated files here;
the third (Required/Visible/Hidden flag combos) turned out to already have
real captured data on hand (`reqvis_*_n4_def_only`, captured 2026-08-23)
that was never reconciled into a conclusion -- see docs/AOI_KNOWLEDGE_MAP.md,
no new files needed for that one.

  A. group_name_length_closeout -- AOI type-name-length sweep
     (aoiname_len08/13/20/30, gen_aoi_sweep2.py) shows a non-uniform step
     (+8, +16, +16) that does NOT match the 8*ceil(len/8) rule the UDT-name
     and tag_overhead formulas both follow. Adds len=9 (does the very next
     char past 8 jump immediately?), len=16 (bisects the 13->20 gap), and
     len=25 (bisects the 20->30 gap) to find where the real step boundaries
     actually sit, same 4-DINT-param shape held constant throughout.

  B. group_boolpack_closeout -- OQ-AOIBOOLPACK's array-of-instances
     finding (gen_aoi_array_packing.py) has two real open threads:
     (1) pure-BOOL shape's ~4/instance rate is NOT cleanly linear across
     the existing 1/5/10/25/50 count points -- consistent with a bit-
     packing effect crossing an unresolved n=32 boundary, but the existing
     points only bracket it between 25 and 50. Adds 16/24/28/30/32/34/40 to
     pin the boundary precisely.
     (2) the 64/instance mixed-shape rate was only ever tested at one
     BOOL:non-BOOL ratio (50/50, 5 BOOL + 5 non-BOOL per section). Adds two
     more ratios (25/75 and 75/25) swept across the same 1/5/10/25/50
     counts already used for the 50/50 case, to see whether 64/instance is
     a fixed per-BOOL-member rate or something that shifts with the mix.

Run: python -m sample_gen.gen_aoi_closeout2
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, aoi_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "aoi"


def _write(l5x: str, out_name: str, description: str, category: str = "aoi") -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, category, out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


# ---------------------------------------------------------------------------
# A. AOI type-name-length closeout: fill the two big gaps (13->20, 20->30)
#    plus one point immediately past the first confirmed length (8->9).
# ---------------------------------------------------------------------------

def _name_of_length(n: int) -> str:
    base = "A"
    filler = ("OINAME" * (n // 6 + 1))[: n - len(base)]
    return base + filler


def group_name_length_closeout() -> None:
    for n in [9, 16, 25]:
        name = _name_of_length(n)
        assert len(name) == n
        params = [MemberSpec(f"P{i}", "DINT") for i in range(4)]
        definition, _ = aoi_xml(name, params, [], [], [])
        l5x = build_l5x(target_name=name, tags_xml="", extra_aoi_xml=definition)
        _write(l5x, f"aoiname_len{n:02d}_def_only",
               f"AOI (4 DINT params) with AOI type name length={n}, 0 instances -- "
               f"OQ-AOIDEF name-length closeout, fills the gap between the existing "
               f"len=8/13/20/30 points to find the real step boundary")


# ---------------------------------------------------------------------------
# B1. Pure-BOOL array-of-instances, dense count points bracketing n=32.
# ---------------------------------------------------------------------------

BOOL_DENSE_COUNTS = [16, 24, 28, 30, 32, 34, 40]


def group_pure_bool_dense() -> None:
    inputs = [MemberSpec(f"In{i}", "BOOL") for i in range(10)]
    outputs = [MemberSpec(f"Out{i}", "BOOL") for i in range(10)]
    locals_ = [MemberSpec(f"Loc{i}", "BOOL") for i in range(10)]
    aoi_name = "AoiPureBoolDense"
    definition, storage = aoi_xml(aoi_name, inputs, outputs, [], locals_)
    for n in BOOL_DENSE_COUNTS:
        tag = tag_xml("TestInstanceArray", aoi_name, dimensions=(n,), udt_members=storage)
        l5x = build_l5x(target_name=aoi_name, tags_xml=tag, extra_aoi_xml=definition)
        _write(l5x, f"aoipack_bool_dense_array_n{n:02d}",
               f"AOI, 10 BOOL In / 10 BOOL Out / 10 BOOL Local, array of {n} instances -- "
               f"OQ-AOIBOOLPACK closeout, dense count points bracketing the n=32 boundary "
               f"the existing 1/5/10/25/50 sweep only straddled",
               category="aoi_array_packing")


# ---------------------------------------------------------------------------
# B2. Mixed BOOL:non-BOOL ratio, two new ratios beyond the existing 50/50.
# ---------------------------------------------------------------------------

MIXED_COUNTS = [1, 5, 10, 25, 50]


def _mixed_sweep(bool_count: int, nonbool_count: int, out_prefix: str, ratio_desc: str) -> None:
    inputs = ([MemberSpec(f"In{i}", "DINT") for i in range(nonbool_count // 3)]
              + [MemberSpec(f"InB{i}", "BOOL") for i in range(bool_count // 3)])
    outputs = ([MemberSpec(f"Out{i}", "DINT") for i in range(nonbool_count // 3)]
               + [MemberSpec(f"OutB{i}", "BOOL") for i in range(bool_count // 3)])
    locals_ = ([MemberSpec(f"Loc{i}", "REAL") for i in range(nonbool_count - 2 * (nonbool_count // 3))]
               + [MemberSpec(f"LocB{i}", "BOOL") for i in range(bool_count - 2 * (bool_count // 3))])
    aoi_name = f"Aoi{out_prefix.title().replace('_', '')}"
    definition, storage = aoi_xml(aoi_name, inputs, outputs, [], locals_)
    l5x = build_l5x(target_name=aoi_name, tags_xml="", extra_aoi_xml=definition)
    _write(l5x, f"{out_prefix}_def_only", f"AOI, {ratio_desc} BOOL:non-BOOL ratio, 0 instances",
           category="aoi_array_packing")
    for n in MIXED_COUNTS:
        tag = tag_xml("TestInstanceArray", aoi_name, dimensions=(n,), udt_members=storage)
        l5x = build_l5x(target_name=aoi_name, tags_xml=tag, extra_aoi_xml=definition)
        _write(l5x, f"{out_prefix}_array_n{n:02d}",
               f"AOI, {ratio_desc} BOOL:non-BOOL ratio, array of {n} instances -- "
               f"OQ-AOIBOOLPACK closeout, tests whether the confirmed 64/instance mixed-shape "
               f"rate holds at a different BOOL:non-BOOL ratio than the original 50/50",
               category="aoi_array_packing")


def group_mixed_ratios() -> None:
    # 15 members per section (5 In/5 Out/5 Local before splitting BOOL:non-BOOL),
    # same total member count as the original 50/50 shape, different ratio.
    _mixed_sweep(bool_count=4, nonbool_count=11, out_prefix="aoipack_mix25_75", ratio_desc="25:75")
    _mixed_sweep(bool_count=11, nonbool_count=4, out_prefix="aoipack_mix75_25", ratio_desc="75:25")


def main() -> None:
    group_name_length_closeout()
    group_pure_bool_dense()
    group_mixed_ratios()
    total = 3 + len(BOOL_DENSE_COUNTS) + 2 * (1 + len(MIXED_COUNTS))
    print(f"\nDone. {total} files.")


if __name__ == "__main__":
    main()
