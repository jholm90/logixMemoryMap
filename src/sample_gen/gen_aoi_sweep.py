"""Big AOI data-sizing sweep (James, 2026-08-20: "based on all of this extra
stuff with the AOIs i expect another 10+ tests... totally nail off the data
sizer estimation process"). Extends the confirmed UDT-definition-cost
findings (168 + 16*member_count, type-independent except BOOL) to AOI
definitions, and directly targets OQ-AOIBOOLPACK (do AOI BOOL Parameters
pack the way UDT BOOL members do, despite the flat un-hidden-SINT XML
shape?).

Run: python -m sample_gen.gen_aoi_sweep
"""

from __future__ import annotations

from sample_gen.builders import MemberSpec, aoi_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

from pathlib import Path

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "aoi"
ATOMIC_TYPES = ["SINT", "INT", "DINT", "LINT", "REAL", "BOOL"]


def _write(l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "aoi", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


def _def_and_instance(aoi_name: str, inputs, outputs, inouts, locals_, out_prefix: str, desc: str) -> None:
    definition, storage = aoi_xml(aoi_name, inputs, outputs, inouts, locals_)
    l5x = build_l5x(target_name=aoi_name, tags_xml="", extra_aoi_xml=definition)
    _write(l5x, f"{out_prefix}_def_only", f"{desc}, 0 instances")
    tag = tag_xml("TestInstance", aoi_name, udt_members=storage)
    l5x = build_l5x(target_name=aoi_name, tags_xml=tag, extra_aoi_xml=definition)
    _write(l5x, f"{out_prefix}_1_instance", f"{desc}, 1 instance")


# ---------------------------------------------------------------------------
# A. Input-parameter count sweep, definition-only -- does AOI definition
#    cost scale the same way UDT definition cost did (168 + 16*count)?
# ---------------------------------------------------------------------------

def group_param_count() -> None:
    for n in [1, 2, 4, 8, 16, 32]:
        params = [MemberSpec(f"P{i}", "DINT") for i in range(n)]
        aoi_name = f"ParamCountN{n:02d}"
        definition, _ = aoi_xml(aoi_name, params, [], [], [])
        l5x = build_l5x(target_name=aoi_name, tags_xml="", extra_aoi_xml=definition)
        _write(l5x, f"paramcount_n{n:02d}_def_only", f"AOI with {n} DINT Input params, 0 instances")


# ---------------------------------------------------------------------------
# B. LocalTag count sweep, definition-only.
# ---------------------------------------------------------------------------

def group_localtag_count() -> None:
    for n in [1, 2, 4, 8, 16, 32]:
        locals_ = [MemberSpec(f"L{i}", "DINT") for i in range(n)]
        aoi_name = f"LocalCountN{n:02d}"
        definition, _ = aoi_xml(aoi_name, [], [], [], locals_)
        l5x = build_l5x(target_name=aoi_name, tags_xml="", extra_aoi_xml=definition)
        _write(l5x, f"localcount_n{n:02d}_def_only", f"AOI with {n} DINT LocalTags, 0 instances")


# ---------------------------------------------------------------------------
# C. Input-parameter TYPE sweep, fixed count=4, definition-only -- does
#    type matter for AOI definition cost, the way it didn't for UDTs
#    (except BOOL)?
# ---------------------------------------------------------------------------

def group_param_type() -> None:
    for t in ATOMIC_TYPES:
        params = [MemberSpec(f"P{i}", t) for i in range(4)]
        aoi_name = f"ParamType{t}"
        definition, _ = aoi_xml(aoi_name, params, [], [], [])
        l5x = build_l5x(target_name=aoi_name, tags_xml="", extra_aoi_xml=definition)
        _write(l5x, f"paramtype_{t.lower()}_n4_def_only", f"AOI with 4 {t} Input params, 0 instances")


# ---------------------------------------------------------------------------
# E. OQ-AOIBOOLPACK: do BOOL Input params pack the way UDT BOOL members do?
#    Consecutive run of 20 BOOLs vs the same 20 BOOLs interspersed with a
#    DINT so no run of 2+ BOOLs ever forms -- if AOI params pack like UDT
#    members despite the flat (no hidden-SINT) XML shape, the interspersed
#    version should cost noticeably more per BOOL than the consecutive one.
# ---------------------------------------------------------------------------

def group_bool_packing() -> None:
    consecutive = [MemberSpec(f"B{i}", "BOOL") for i in range(20)]
    _def_and_instance("BoolPackConsecutive", consecutive, [], [], [],
                       "aoi_boolpack_consecutive20", "AOI with 20 consecutive BOOL Input params")

    interspersed = []
    for i in range(20):
        interspersed.append(MemberSpec(f"B{i}", "BOOL"))
        interspersed.append(MemberSpec(f"Break{i}", "DINT"))
    _def_and_instance("BoolPackInterspersed", interspersed, [], [], [],
                       "aoi_boolpack_interspersed20", "AOI with 20 BOOL Input params each separated by a DINT")


# ---------------------------------------------------------------------------
# F. Deep nesting: AOI C nested in AOI B nested in AOI A (3 levels) --
#    extends the already-confirmed 2-level nested-AOI-as-LocalTag pattern.
# ---------------------------------------------------------------------------

def group_deep_nested() -> None:
    def_c, storage_c = aoi_xml("DeepC", [MemberSpec("X", "DINT")], [], [], [])
    b_locals = [MemberSpec("InstC", "DeepC", nested_members=tuple(storage_c))]
    def_b, storage_b = aoi_xml("DeepB", [MemberSpec("Y", "DINT")], [], [], b_locals)
    a_locals = [MemberSpec("InstB", "DeepB", nested_members=tuple(storage_b))]
    def_a, storage_a = aoi_xml("DeepA", [MemberSpec("Z", "DINT")], [], [], a_locals)
    all_defs = "\n".join([def_c, def_b, def_a])

    l5x = build_l5x(target_name="DeepA", tags_xml="", extra_aoi_xml=all_defs)
    _write(l5x, "aoi_deepnest3_def_only", "3-level nested AOI (A contains B contains C), 0 instances")
    tag = tag_xml("TestInstance", "DeepA", udt_members=storage_a)
    l5x = build_l5x(target_name="DeepA", tags_xml=tag, extra_aoi_xml=all_defs)
    _write(l5x, "aoi_deepnest3_1_instance", "3-level nested AOI (A contains B contains C), 1 instance")


# ---------------------------------------------------------------------------
# G. Array of a nested-AOI LocalTag -- combines the confirmed nested-AOI
#    pattern with the confirmed array-of-nested-UDT-member pattern.
# ---------------------------------------------------------------------------

def group_nested_array_localtag() -> None:
    def_inner, storage_inner = aoi_xml("ArrInner", [MemberSpec("V", "DINT")], [], [], [])
    outer_locals = [MemberSpec("InnerArray", "ArrInner", dimension=10, nested_members=tuple(storage_inner))]
    def_outer, storage_outer = aoi_xml("ArrOuter", [], [], [], outer_locals)
    both = def_inner + "\n" + def_outer

    l5x = build_l5x(target_name="ArrOuter", tags_xml="", extra_aoi_xml=both)
    _write(l5x, "aoi_nested_array_localtag_def_only", "AOI with a 10-element array-of-nested-AOI LocalTag, 0 instances")
    tag = tag_xml("TestInstance", "ArrOuter", udt_members=storage_outer)
    l5x = build_l5x(target_name="ArrOuter", tags_xml=tag, extra_aoi_xml=both)
    _write(l5x, "aoi_nested_array_localtag_1_instance", "AOI with a 10-element array-of-nested-AOI LocalTag, 1 instance")


# ---------------------------------------------------------------------------
# I. Realistic composite AOI (10 In + 10 Out + 10 Local), matching the
#    scale of James's real Template AOIs (AnalogSensor_AOI etc: 10-30
#    params/locals each) -- at 0/1/10 instances.
# ---------------------------------------------------------------------------

def group_realistic_composite() -> None:
    inputs = [MemberSpec(f"In{i}", "DINT") for i in range(5)] + [MemberSpec(f"InB{i}", "BOOL") for i in range(5)]
    outputs = [MemberSpec(f"Out{i}", "DINT") for i in range(5)] + [MemberSpec(f"OutB{i}", "BOOL") for i in range(5)]
    locals_ = [MemberSpec(f"Loc{i}", "REAL") for i in range(5)] + [MemberSpec(f"LocB{i}", "BOOL") for i in range(5)]

    definition, storage = aoi_xml("RealisticAOI", inputs, outputs, [], locals_)
    l5x = build_l5x(target_name="RealisticAOI", tags_xml="", extra_aoi_xml=definition)
    _write(l5x, "aoi_realistic_composite_def_only", "Realistic AOI (10 In/10 Out/10 Local, mixed DINT/BOOL/REAL), 0 instances")

    tag = tag_xml("TestInstance", "RealisticAOI", udt_members=storage)
    l5x = build_l5x(target_name="RealisticAOI", tags_xml=tag, extra_aoi_xml=definition)
    _write(l5x, "aoi_realistic_composite_1_instance", "Realistic AOI (10 In/10 Out/10 Local, mixed DINT/BOOL/REAL), 1 instance")

    tag = tag_xml("TestInstanceArray", "RealisticAOI", dimensions=(10,), udt_members=storage)
    l5x = build_l5x(target_name="RealisticAOI", tags_xml=tag, extra_aoi_xml=definition)
    _write(l5x, "aoi_realistic_composite_10_instance_array", "Realistic AOI (10 In/10 Out/10 Local, mixed DINT/BOOL/REAL), array of 10 instances")


def main() -> None:
    for group_fn in [
        group_param_count, group_localtag_count, group_param_type,
        group_bool_packing, group_deep_nested, group_nested_array_localtag,
        group_realistic_composite,
    ]:
        group_fn()
    print("Done.")


if __name__ == "__main__":
    main()
