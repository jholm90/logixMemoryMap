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

**2026-08-23 fix, after all 3 files here failed Build:** James hand-built
and Studio-5000-verified 3 trial files that exposed the real gaps (not
guessed, diffed byte-for-byte against what this generator was producing):
  1. The wrapper UDT's "AOI" member needs `Radix="NullType"
     ExternalAccess="Read/Write"` on its <Member> declaration -- a plain
     nested UDT member doesn't carry these (confirmed: gen_axis_composite.
     py's composite-UDT tests already passed real Build without them), but
     a nested AOI member does. Fixed via MemberSpec.is_aoi_member in
     builders.py (see that file's _udt_members_xml).
  2. The AOI-with-InOut instance's required InOut parameter was never
     actually wired to anything -- no rung called the AOI, and there
     wasn't even a real AXIS_CIP_DRIVE tag in the file to wire it to.
     James's real files always: (a) declare a real Axis+MotionGroup tag
     pair (reused from gen_axis_composite.py's _AXIS_TAG_XML, same shape
     confirmed there), (b) call the AOI from an actual rung with the axis
     wired into the InOut slot, e.g. for the array case:
     `DriveAxisTest(Wrapper_UDT[0].AOI,Wrapper_UDT[0].AOI.FaultReset,Axis);`
     -- bracket-subscript on the array element, same rule as CPS/COP/FLL/
     BTD.
  3. The 0-instance ("def_only") variant doesn't actually make sense for
     this construct -- there's nothing to wire a required InOut parameter
     to without an instance to call, and James's own real trial files
     don't test it (his "def_only" file has a real single instance + a
     call, not zero instances). Dropped in favor of just 1/10.

Run: python -m sample_gen.gen_aoi_nested_inout
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, aoi_xml, collect_nested_datatypes, rung_xml, tag_xml
from sample_gen.gen_axis_composite import _AXIS_TAG_XML
from sample_gen.manifest import append_manifest_row, write_sample_unmodeled
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "aoi"


def _write(l5x: str, out_name: str, description: str) -> None:
    # Contains a real AXIS_CIP_DRIVE/MOTION_GROUP tag (needed to wire the
    # AOI's required InOut parameter to something real) -- unmodeled
    # predefined structure, same as gen_axis_composite.py's axis files, so
    # this uses the unmodeled path instead of write_sample()'s strict
    # predicted_bytes requirement.
    out_path = OUT_ROOT / f"{out_name}.L5X"
    write_sample_unmodeled(l5x, out_path)
    append_manifest_row(out_name, f"{description} (unmodeled predefined structure)", "aoi", out_path, 0)
    print(f"Wrote {out_path} (predicted N/A -- unmodeled axis structure)")


def main() -> None:
    # REAL BUG FOUND 2026-08-31 (James's real Studio 5000 verify errors +
    # lint.py's new aoi_call_arg_count_mismatch check, same root cause as
    # gen_aoi_orphaned_def.py/gen_composite_realistic.py): required=False/
    # visible=False (the MemberSpec default) makes a param HIDDEN from
    # the instruction's own call signature, but both rungs below wire a
    # real tag into FaultReset's slot anyway. Fixed with required=True.
    fault_reset = MemberSpec("FaultReset", "BOOL", required=True)
    drive_axis = MemberSpec("Drive_Axis", "AXIS_CIP_DRIVE")
    definition, storage = aoi_xml("DriveAxisNestTest", input_params=[fault_reset], inout_params=[drive_axis])

    wrapper_members = [
        MemberSpec("AOI", "DriveAxisNestTest", nested_members=tuple(storage), is_aoi_member=True),
        MemberSpec("Enabled", "BOOL"),
        MemberSpec("RunCond", "DINT"),
    ]
    datatypes = collect_nested_datatypes("WrapperUdt", wrapper_members)

    for n in [1, 10]:
        if n == 1:
            wrapper_tag = tag_xml("WrapperInst", "WrapperUdt", udt_members=wrapper_members)
            rung = rung_xml(0, "DriveAxisNestTest(WrapperInst.AOI,WrapperInst.AOI.FaultReset,Axis_Cip_Drive);")
            l5x = build_l5x(target_name="AoiNestedInout1", tags_xml="\n".join([_AXIS_TAG_XML, wrapper_tag]),
                             extra_datatypes_xml=datatypes, extra_aoi_xml=definition, extra_rungs_xml=rung)
            _write(l5x, "aoi_nested_inout_1_instance",
                   "UDT nesting an AOI-with-InOut-param as a member (real ts_CIPAxis/DriveAxis pattern), "
                   "1 instance, called from a rung with a real axis wired into the InOut slot")
        else:
            wrapper_tag = tag_xml("WrapperArr", "WrapperUdt", dimensions=(n,), udt_members=wrapper_members)
            rung = rung_xml(0, "DriveAxisNestTest(WrapperArr[0].AOI,WrapperArr[0].AOI.FaultReset,Axis_Cip_Drive);")
            l5x = build_l5x(target_name=f"AoiNestedInoutN{n}", tags_xml="\n".join([_AXIS_TAG_XML, wrapper_tag]),
                             extra_datatypes_xml=datatypes, extra_aoi_xml=definition, extra_rungs_xml=rung)
            _write(l5x, f"aoi_nested_inout_{n}_instance",
                   f"Same UDT, array of {n} instances, element [0] called from a rung with a real axis wired in")

    print("\nDone. 2 files.")


if __name__ == "__main__":
    main()
