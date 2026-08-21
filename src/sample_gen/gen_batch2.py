"""Second big test batch (James, 2026-08-20): nested UDTs, nested array
UDTs, custom-length STRING validation, AOI generation (including nested
AOIs and arrays inside AOIs), and large realistic multi-tag/UDT
combination files at 100+ and 1000+ tag scale with no logic.

Run: python -m sample_gen.gen_batch2
"""

from __future__ import annotations

from sample_gen.builders import (
    MemberSpec, aoi_xml, collect_nested_datatypes, custom_string_type_xml,
    tag_xml, udt_xml,
)
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

from pathlib import Path

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated"


def _write(l5x: str, category: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / category / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, category, out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


# ---------------------------------------------------------------------------
# Nested UDT / nested array UDT (James: "nested UDTs need to be tested.
# nested array udts need to be tested.")
# ---------------------------------------------------------------------------

def group_nested_udt() -> None:
    # Inner UDT: 2 DINT members.
    inner_members = [MemberSpec("A", "DINT"), MemberSpec("B", "DINT")]

    # Outer UDT: one scalar nested-UDT member + one atomic member.
    outer_scalar = [
        MemberSpec("Inner", "InnerUDT", nested_members=tuple(inner_members)),
        MemberSpec("Flag", "DINT"),
    ]
    datatypes = collect_nested_datatypes("OuterNestedScalar", outer_scalar)
    tag = tag_xml("TestInstance", "OuterNestedScalar", udt_members=outer_scalar)
    l5x = build_l5x(target_name="OuterNestedScalar", tags_xml=tag, extra_datatypes_xml=datatypes)
    _write(l5x, "udt", "nested_udt_scalar", "Outer UDT with one nested-UDT scalar member (Inner: 2 DINT)")

    # Nested array UDT: outer UDT's member is an ARRAY of the inner UDT.
    outer_array = [
        MemberSpec("InnerArray", "InnerUDT", dimension=10, nested_members=tuple(inner_members)),
        MemberSpec("Flag", "DINT"),
    ]
    datatypes = collect_nested_datatypes("OuterNestedArray", outer_array)
    tag = tag_xml("TestInstance", "OuterNestedArray", udt_members=outer_array)
    l5x = build_l5x(target_name="OuterNestedArray", tags_xml=tag, extra_datatypes_xml=datatypes)
    _write(l5x, "udt", "nested_udt_array_member", "Outer UDT with a 10-element array-of-nested-UDT member")

    # Nested array UDT, the OTHER shape: an array-of-UDT TAG where each
    # element's UDT itself contains a nested UDT member.
    array_of_nested = [MemberSpec("Inner", "InnerUDT", nested_members=tuple(inner_members)), MemberSpec("Flag", "DINT")]
    datatypes = collect_nested_datatypes("ArrayOfNested", array_of_nested)
    tag = tag_xml("TestInstance", "ArrayOfNested", dimensions=(100,), udt_members=array_of_nested)
    l5x = build_l5x(target_name="ArrayOfNested", tags_xml=tag, extra_datatypes_xml=datatypes)
    _write(l5x, "udt", "array_of_nested_udt_100", "100-element array of a UDT that itself contains a nested-UDT member")


# ---------------------------------------------------------------------------
# Custom STRING length validation, spot checks especially 500+ chars
# (James: "custom length strings need to be validated. just a few spot
# checks, especially in the 500+ char range")
# ---------------------------------------------------------------------------

def group_custom_string() -> None:
    for max_len in [10, 82, 100, 250, 500, 1000, 2000]:
        type_name = f"Str{max_len}"
        datatype = custom_string_type_xml(type_name, max_len)
        tag = tag_xml("TestString", type_name, string_max_len=max_len)
        l5x = build_l5x(target_name=type_name, tags_xml=tag, extra_datatypes_xml=datatype)
        out_name = f"customstring_len{max_len:04d}"
        _write(l5x, "tags", out_name, f"Custom STRING type, max_len={max_len}, 1 tag")


# ---------------------------------------------------------------------------
# AOI generation: basic, array-in-AOI, nested-AOI-in-AOI (James: "compile/
# update the udt generator to make up the nested aois and arrays inside
# the aois")
# ---------------------------------------------------------------------------

def group_aoi() -> None:
    # Basic AOI: 2 Input, 1 Output, 1 InOut (no storage), 2 LocalTags.
    inputs = [MemberSpec("SetPoint", "REAL"), MemberSpec("Enable", "BOOL")]
    outputs = [MemberSpec("Status", "DINT")]
    inouts = [MemberSpec("RefTag", "DINT")]
    locals_ = [MemberSpec("Accum", "REAL"), MemberSpec("Temp", "DINT")]
    definition, storage = aoi_xml("BasicAOI", inputs, outputs, inouts, locals_)

    l5x_def_only = build_l5x(target_name="BasicAOI", tags_xml="", extra_aoi_xml=definition)
    _write(l5x_def_only, "aoi", "basic_aoi_def_only", "Basic AOI (2 In/1 Out/1 InOut/2 Local), 0 instances")

    tag = tag_xml("TestInstance", "BasicAOI", udt_members=storage)
    l5x_1inst = build_l5x(target_name="BasicAOI", tags_xml=tag, extra_aoi_xml=definition)
    _write(l5x_1inst, "aoi", "basic_aoi_1_instance", "Basic AOI (2 In/1 Out/1 InOut/2 Local), 1 instance")

    # AOI with an array LocalTag ("arrays inside the aois").
    array_locals = [MemberSpec("Buffer", "DINT", dimension=100)]
    definition2, storage2 = aoi_xml("ArrayLocalAOI", [], [], [], array_locals)
    l5x = build_l5x(target_name="ArrayLocalAOI", tags_xml="", extra_aoi_xml=definition2)
    _write(l5x, "aoi", "aoi_array_localtag_def_only", "AOI with a 100-element array LocalTag, 0 instances")
    tag = tag_xml("TestInstance", "ArrayLocalAOI", udt_members=storage2)
    l5x = build_l5x(target_name="ArrayLocalAOI", tags_xml=tag, extra_aoi_xml=definition2)
    _write(l5x, "aoi", "aoi_array_localtag_1_instance", "AOI with a 100-element array LocalTag, 1 instance")

    # AOI with an array Input Parameter.
    array_inputs = [MemberSpec("InputBuffer", "DINT", dimension=50)]
    definition3, storage3 = aoi_xml("ArrayParamAOI", array_inputs, [], [], [])
    l5x = build_l5x(target_name="ArrayParamAOI", tags_xml="", extra_aoi_xml=definition3)
    _write(l5x, "aoi", "aoi_array_param_def_only", "AOI with a 50-element array Input Parameter, 0 instances")

    # Nested AOI: outer AOI has a LocalTag whose type is the inner AOI
    # (James: "nested aois need to be tested"). Data-space only -- the
    # outer AOI's logic doesn't actually call the inner one (that's Phase
    # 4c/logic territory), this tests whether an AOI-typed LocalTag sizes
    # the same way an AOI-typed *tag* does (already confirmed, see
    # PROJECT_PLAN.md Phase 4c).
    inner_def, inner_storage = aoi_xml("InnerAOI", [MemberSpec("X", "DINT")], [], [], [])
    outer_locals = [MemberSpec("NestedInstance", "InnerAOI", nested_members=tuple(inner_storage))]
    outer_def, outer_storage = aoi_xml("OuterAOI", [], [], [], outer_locals)
    both_defs = inner_def + "\n" + outer_def
    l5x = build_l5x(target_name="OuterAOI", tags_xml="", extra_aoi_xml=both_defs)
    _write(l5x, "aoi", "nested_aoi_def_only", "Outer AOI with a LocalTag of type InnerAOI (nested AOI), 0 instances")
    tag = tag_xml("TestInstance", "OuterAOI", udt_members=outer_storage)
    l5x = build_l5x(target_name="OuterAOI", tags_xml=tag, extra_aoi_xml=both_defs)
    _write(l5x, "aoi", "nested_aoi_1_instance", "Outer AOI with a LocalTag of type InnerAOI (nested AOI), 1 instance")


# ---------------------------------------------------------------------------
# Large realistic multi-tag/UDT combination files, no logic (James: "start
# adding in a couple of multiple UDT/tag combinations ... a couple tests
# with 100+ tags and a couple tests with 1000+ tags")
# ---------------------------------------------------------------------------

def _mixed_tags(count_each: int, udt_members: list[MemberSpec], udt_name: str) -> tuple[str, str]:
    """Returns (tags_xml, datatypes_xml) for a realistic mix: DINT/BOOL/REAL/
    SINT scalars and small arrays, plus UDT instances, count_each of each
    tag-shape category so the total scales with count_each."""
    tags = []
    for i in range(count_each):
        tags.append(tag_xml(f"Dint_{i:04d}", "DINT"))
    for i in range(count_each):
        tags.append(tag_xml(f"Bool_{i:04d}", "BOOL"))
    for i in range(count_each):
        tags.append(tag_xml(f"Real_{i:04d}", "REAL"))
    for i in range(count_each):
        tags.append(tag_xml(f"Sint_{i:04d}", "SINT"))
    for i in range(count_each):
        tags.append(tag_xml(f"UdtInst_{i:04d}", udt_name, udt_members=udt_members))
    return "\n".join(tags), udt_xml(udt_name, udt_members)


def group_large_mixed() -> None:
    udt_members = [MemberSpec("Speed", "DINT"), MemberSpec("Running", "BOOL"), MemberSpec("Setpoint", "REAL")]

    # ~100+ tags total: 20 of each of 5 shapes = 100 tags.
    tags_xml, datatype_xml = _mixed_tags(20, udt_members, "MixUdt100")
    l5x = build_l5x(target_name="LargeMixed100", tags_xml=tags_xml, extra_datatypes_xml=datatype_xml)
    _write(l5x, "mixed", "large_mixed_100tags", "Realistic mix: 20x each of DINT/BOOL/REAL/SINT scalar + 20x 3-member UDT = 100 tags, no logic")

    # 1000+ tags total: 220 of each of 5 shapes = 1100 tags.
    tags_xml, datatype_xml = _mixed_tags(220, udt_members, "MixUdt1000")
    l5x = build_l5x(target_name="LargeMixed1000", tags_xml=tags_xml, extra_datatypes_xml=datatype_xml)
    _write(l5x, "mixed", "large_mixed_1100tags", "Realistic mix: 220x each of DINT/BOOL/REAL/SINT scalar + 220x 3-member UDT = 1100 tags, no logic")

    # Second large-scale point at a different composition (arrays instead
    # of scalars) so there are two independent 1000+-tag validation points,
    # not just one repeated shape.
    tags2 = []
    for i in range(200):
        tags2.append(tag_xml(f"DintArr_{i:04d}", "DINT", dimensions=(10,)))
    for i in range(200):
        tags2.append(tag_xml(f"BoolArr_{i:04d}", "BOOL", dimensions=(32,)))
    for i in range(200):
        tags2.append(tag_xml(f"RealArr_{i:04d}", "REAL", dimensions=(10,)))
    for i in range(400):
        tags2.append(tag_xml(f"UdtInst2_{i:04d}", "MixUdt1000b", udt_members=udt_members))
    l5x = build_l5x(
        target_name="LargeMixed1000b", tags_xml="\n".join(tags2),
        extra_datatypes_xml=udt_xml("MixUdt1000b", udt_members),
    )
    _write(l5x, "mixed", "large_mixed_1000tags_arrays", "Realistic mix v2: 200x DINT[10]/BOOL[32]/REAL[10] array tags + 400x 3-member UDT = 1000 tags, no logic")


def main() -> None:
    group_nested_udt()
    group_custom_string()
    group_aoi()
    group_large_mixed()


if __name__ == "__main__":
    main()
