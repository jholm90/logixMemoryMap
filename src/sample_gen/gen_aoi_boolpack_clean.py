"""Clean re-test of OQ-AOIBOOLPACK. The original test (gen_aoi_sweep.py
group_bool_packing) confounded arrangement with total param count: the
"consecutive" file had 20 BOOL params only (20 total), the "interspersed"
file had 20 BOOL + 20 DINT (40 total) -- so any delta between them mixes
arrangement effect with param-count effect, not a clean isolation.

This version holds total param count AND type mix constant (10 BOOL + 10
DINT = 20 params either way) and varies only whether the BOOLs are grouped
together or alternate with the DINTs.

Run: python -m sample_gen.gen_aoi_boolpack_clean
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, aoi_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "aoi"


def _write(l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "aoi", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


def main() -> None:
    grouped = [MemberSpec(f"B{i}", "BOOL") for i in range(10)] + [MemberSpec(f"D{i}", "DINT") for i in range(10)]
    definition, _ = aoi_xml("BoolPackGrouped", grouped)
    l5x = build_l5x(target_name="BoolPackGrouped", tags_xml="", extra_aoi_xml=definition)
    _write(l5x, "aoi_boolpack_clean_grouped_def_only",
           "AOI, 10 BOOL grouped together + 10 DINT (20 total params), 0 instances -- clean OQ-AOIBOOLPACK re-test")

    interspersed = []
    for i in range(10):
        interspersed.append(MemberSpec(f"B{i}", "BOOL"))
        interspersed.append(MemberSpec(f"D{i}", "DINT"))
    definition, _ = aoi_xml("BoolPackAlternating", interspersed)
    l5x = build_l5x(target_name="BoolPackAlternating", tags_xml="", extra_aoi_xml=definition)
    _write(l5x, "aoi_boolpack_clean_alternating_def_only",
           "AOI, 10 BOOL alternating with 10 DINT (20 total params, same mix as grouped), 0 instances")

    print("\nDone. 2 files.")


if __name__ == "__main__":
    main()
