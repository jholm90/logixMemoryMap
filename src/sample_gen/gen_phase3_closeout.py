"""Phase 3 literal-checklist closeout (James, 2026-08-24: "I want phase 3
closed now. Generate all files to make this happen as your highest
priority."). Fills the 4 remaining docs/TASKS.md Phase 3 checklist items
that genuinely had no matching generated file yet (the rest were
superseded by later, more rigorous family sweeps -- see docs/TASKS.md's
own note on each item for what actually closed it):

  A. 3-level nested UDT (A contains B contains C) -- only a 2-level
     version existed (gen_batch2.py's OuterNestedScalar/InnerUDT).
  B. Built-in STRING (82-byte) tag, x1000 instances -- confirms the flat
     per-tag overhead formula holds for STRING specifically at scale (only
     ever tested at small counts before).
  C. Custom string type (250-char), x1000 instances -- same, for a custom
     string type.
  D. AOI called 50 times vs. 1 time (array of 50 instances vs. a single
     instance) -- the existing realistic-composite AOI only went up to a
     10-instance array (gen_aoi_sweep.py's group_realistic_composite).

Run: python -m sample_gen.gen_phase3_closeout
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, aoi_xml, custom_string_type_xml, tag_xml, udt_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated"


def _write(category: str, l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / category / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, category, out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


def group_nested_udt_3level() -> None:
    # C (innermost): 2 DINT. B: contains C + 1 DINT. A (outermost): contains
    # B + 1 DINT. Same collect_nested_datatypes/nested_members machinery
    # already confirmed at 2 levels, one level deeper.
    c_members = [MemberSpec("X", "DINT"), MemberSpec("Y", "DINT")]
    b_members = [MemberSpec("InstC", "LevelC", nested_members=tuple(c_members)), MemberSpec("Flag", "DINT")]
    a_members = [MemberSpec("InstB", "LevelB", nested_members=tuple(b_members)), MemberSpec("Flag", "DINT")]
    all_datatypes = "\n".join([udt_xml("LevelC", c_members), udt_xml("LevelB", b_members), udt_xml("LevelA", a_members)])
    tag = tag_xml("TestInstance", "LevelA", udt_members=a_members)
    l5x = build_l5x(target_name="LevelA", tags_xml=tag, extra_datatypes_xml=all_datatypes)
    _write("udt", l5x, "nested_udt_3level",
           "3-level nested UDT: LevelA contains LevelB contains LevelC (2x DINT each level + 1 flag)")


def group_string_x1000() -> None:
    tags = "\n".join(tag_xml(f"Str{i:04d}", "STRING", string_max_len=82) for i in range(1000))
    l5x = build_l5x(target_name="StringX1000", tags_xml=tags)
    _write("tags", l5x, "string_builtin_x1000",
           "1000 built-in STRING (82-byte default) tag instances -- per-tag overhead at scale, STRING-specific")


def group_customstring_x1000() -> None:
    datatype = custom_string_type_xml("Str250", 250)
    tags = "\n".join(tag_xml(f"CStr{i:04d}", "Str250", string_max_len=250) for i in range(1000))
    l5x = build_l5x(target_name="CustomStringX1000", tags_xml=tags, extra_datatypes_xml=datatype)
    _write("tags", l5x, "customstring_250char_x1000",
           "1000 instances of a 250-char custom STRING type -- per-tag overhead at scale, custom-string-specific")


def group_aoi_50_instances() -> None:
    inputs = [MemberSpec(f"In{i}", "DINT") for i in range(5)] + [MemberSpec(f"InB{i}", "BOOL") for i in range(5)]
    outputs = [MemberSpec(f"Out{i}", "DINT") for i in range(5)] + [MemberSpec(f"OutB{i}", "BOOL") for i in range(5)]
    locals_ = [MemberSpec(f"Loc{i}", "REAL") for i in range(5)] + [MemberSpec(f"LocB{i}", "BOOL") for i in range(5)]
    definition, storage = aoi_xml("RealisticAOI50", inputs, outputs, [], locals_)

    tag1 = tag_xml("TestInstance", "RealisticAOI50", udt_members=storage)
    l5x = build_l5x(target_name="RealisticAOI50", tags_xml=tag1, extra_aoi_xml=definition)
    _write("aoi", l5x, "aoi_realistic_50_instance_1",
           "Realistic AOI (10 In/10 Out/10 Local), 1 SEPARATE instance (not an array) -- direct 1-vs-50 "
           "comparison point for aoi_realistic_50_instance_array")

    tag50 = tag_xml("TestInstanceArray", "RealisticAOI50", dimensions=(50,), udt_members=storage)
    l5x = build_l5x(target_name="RealisticAOI50", tags_xml=tag50, extra_aoi_xml=definition)
    _write("aoi", l5x, "aoi_realistic_50_instance_array",
           "Realistic AOI (10 In/10 Out/10 Local), array of 50 instances -- isolates per-instance cost at "
           "5x the scale of the existing 10-instance-array file")


def main() -> None:
    group_nested_udt_3level()
    group_string_x1000()
    group_customstring_x1000()
    group_aoi_50_instances()
    print("\nDone. 5 files.")


if __name__ == "__main__":
    main()
