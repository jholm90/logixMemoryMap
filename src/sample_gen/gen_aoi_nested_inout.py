"""OQ item 15 (roadmap 2026-08-22): nested AOI-with-required-InOut-param as
a UDT member. Previously declined in gen_axis_composite.py as an unconfirmed
Studio 5000 construct -- resolved 2026-08-22 by checking a REAL working
instance, not just the AOI/UDT *definitions*: `BedRolls` (DataType=
"ts_CIPAxis") in samples/local/BaillieLeitchField_Edger_20260812_r00.L5X
has a real `StructureMember Name="AOI" DataType="DriveAxis"` member, and its
InOut parameters (Drive_Axis: AXIS_CIP_DRIVE, Udt_Servo) are completely
absent from that member's body -- exactly matching the already-confirmed
"InOut params carry zero storage" rule. This construct is real and
importable, not a guess.

Uses aoi_xml()'s existing storage_members (already excludes InOut) nested
into a UDT via MemberSpec(nested_members=...), same machinery
gen_axis_composite.py's ts_CIPAxis-style test already uses for ordinary
nested UDTs -- this just does it with an InOut-having AOI specifically.

Run: python -m sample_gen.gen_aoi_nested_inout
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, aoi_xml, collect_nested_datatypes, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "aoi"


def _write(l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "aoi", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


def main() -> None:
    fault_reset = MemberSpec("FaultReset", "BOOL")
    drive_axis = MemberSpec("Drive_Axis", "AXIS_CIP_DRIVE")
    definition, storage = aoi_xml("DriveAxisNestTest", input_params=[fault_reset], inout_params=[drive_axis])

    wrapper_members = [
        MemberSpec("AOI", "DriveAxisNestTest", nested_members=tuple(storage)),
        MemberSpec("Enabled", "BOOL"),
        MemberSpec("RunCond", "DINT"),
    ]
    datatypes = collect_nested_datatypes("WrapperUdt", wrapper_members)

    for n in [0, 1, 10]:
        if n == 0:
            l5x = build_l5x(target_name="AoiNestedInoutDefOnly", tags_xml="", extra_datatypes_xml=datatypes,
                             extra_aoi_xml=definition)
            _write(l5x, "aoi_nested_inout_def_only",
                   "UDT nesting an AOI-with-InOut-param as a member (real ts_CIPAxis/DriveAxis pattern), 0 instances")
        elif n == 1:
            tag = tag_xml("WrapperInst", "WrapperUdt", udt_members=wrapper_members)
            l5x = build_l5x(target_name="AoiNestedInout1", tags_xml=tag, extra_datatypes_xml=datatypes,
                             extra_aoi_xml=definition)
            _write(l5x, "aoi_nested_inout_1_instance", "Same UDT, 1 instance")
        else:
            tag = tag_xml("WrapperArr", "WrapperUdt", dimensions=(n,), udt_members=wrapper_members)
            l5x = build_l5x(target_name=f"AoiNestedInoutN{n}", tags_xml=tag, extra_datatypes_xml=datatypes,
                             extra_aoi_xml=definition)
            _write(l5x, f"aoi_nested_inout_{n}_instance", f"Same UDT, array of {n} instances")

    print("\nDone. 3 files.")


if __name__ == "__main__":
    main()
