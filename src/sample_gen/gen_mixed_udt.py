"""OQ-MIXEDUDT (2026-08-26, self-initiated per CLAUDE.md step 5 -- James:
"why am i having to push you to generate up these open things instead of
you adding them to the next round of tests automatically?"). The one item
from the open-questions list with ZERO test coverage: a "realistic messy/
nested UDT, arbitrary member mix," as opposed to a homogeneous array or
the axis-specific composite shape gen_axis_composite.py already covers
(that one resolved OQ-AXISDEEP's composite case specifically, per its own
docstring, but explicitly left the BROADER arbitrary-mix question open).

Deliberately mixes only constructs this project has ALREADY confirmed
safe to generate, individually, elsewhere -- no new unconfirmed XML risk
(gen_axis_composite.py already declined to guess at one unconfirmed
construct, AOI-with-InOut nested as a UDT member; same caution here):
  - 2-level-deep nested UDT (confirmed, axis_composite_udt_*)
  - custom StringFamily member (confirmed via the stringclose_udtmember_*
    batch -- real captures matched predictions exactly even though the
    tag-instance Structure body only ever renders an "unsupported member"
    placeholder comment for it; Studio 5000 fills the real content in
    from the DataType definition on import)
  - builtin STRING member (confirmed, its own real StructureMember shape)
  - BOOL bit-run, deliberately NOT grouped together but scattered between
    other member types (the "garbled" part of "mixed and garbled" --
    tests whether hidden-SINT-backing-run packing still works when BOOL
    members aren't contiguous in declaration order)
  - array-of-nested-UDT (confirmed, OQ-TAGOVERHEAD "nested array udts")
  - plain atomic array (DINT[]) and scattered SINT/INT/LINT/REAL scalars

Three files, additivity-check pattern (matches axis_composite_udt_* and
OQ-LARGEMIXED's already-proven methodology): 0/1/25 instances. If the
individually-confirmed per-member-type formulas are truly composable
regardless of ORDER and MIX (not just when cleanly separated, as every
other UDT test in this project's corpus has been so far), the real
Capacity number for all 3 should land within the same small existing
noise band, no unexplained residual specific to "messiness" itself.

Run: python -m sample_gen.gen_mixed_udt
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, collect_nested_datatypes, custom_string_type_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "mixed"

_CUSTOM_STRING_TYPE = "MixedUdtCustomStr40"
_CUSTOM_STRING_MAXLEN = 40


def _write(l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "mixed", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


def _messy_members() -> list[MemberSpec]:
    # Innermost nested level -- a small UDT of its own, referenced by the
    # middle level below (2 levels deep total, like ts_CIPAxis's own
    # AutoSpeeds/Servo members in gen_axis_composite.py).
    calib = [
        MemberSpec("Offset", "REAL"),
        MemberSpec("Gain", "REAL"),
    ]
    sensor = [
        MemberSpec("RawValue", "INT"),
        MemberSpec("Calib", "NestedCalib_Mixed", nested_members=tuple(calib)),
        MemberSpec("Fault", "BOOL"),
    ]
    # Deliberately garbled declaration order -- BOOL/bit members scattered
    # between other types rather than grouped, atomics interleaved with
    # structured members, per the "mixed and garbled" real-world shape
    # James described (not the clean same-type-grouped shape every other
    # UDT test in this corpus uses).
    return [
        MemberSpec("Name", "STRING"),
        MemberSpec("Running", "BOOL"),
        MemberSpec("Sensors", "NestedSensor_Mixed", dimension=3, nested_members=tuple(sensor)),
        MemberSpec("SerialNum", _CUSTOM_STRING_TYPE),
        MemberSpec("Faulted", "BOOL"),
        MemberSpec("Setpoints", "DINT", dimension=8),
        MemberSpec("CycleCount", "LINT"),
        MemberSpec("Enabled", "BOOL"),
        MemberSpec("Mode", "SINT"),
        MemberSpec("Ready", "BOOL"),
        MemberSpec("TotalWeight", "REAL"),
    ]


def _build(instances: int) -> None:
    members = _messy_members()
    udt_name = "MessyStation_Mixed"
    nested_datatypes = collect_nested_datatypes(udt_name, members)
    custom_string_datatype = custom_string_type_xml(_CUSTOM_STRING_TYPE, _CUSTOM_STRING_MAXLEN)
    datatypes = nested_datatypes + "\n" + custom_string_datatype

    if instances == 0:
        tags = ""
        label = "def_only"
        desc_suffix = "0 instances"
    elif instances == 1:
        tags = tag_xml("Inst1", udt_name, udt_members=members)
        label = "1_instance"
        desc_suffix = "1 instance"
    else:
        tags = tag_xml(f"Inst{instances}", udt_name, dimensions=(instances,), udt_members=members)
        label = f"{instances}_instance"
        desc_suffix = f"array of {instances} instances"

    from sample_gen.wrapper import build_l5x
    l5x = build_l5x(target_name=f"MixedUdt{instances}", tags_xml=tags, extra_datatypes_xml=datatypes)
    _write(
        l5x, f"mixedudt_messy_{label}",
        f"Realistic messy/nested UDT (OQ-MIXEDUDT): garbled-order mix of 2-level nested UDT (array-of-3), "
        f"custom StringFamily member, builtin STRING member, scattered non-contiguous BOOL members, DINT[8] "
        f"array, LINT/SINT/REAL scalars -- {desc_suffix}. Tests whether individually-confirmed per-member-type "
        f"formulas compose correctly when genuinely mixed and reordered, not just cleanly separated.",
    )


def group_messy_udt() -> None:
    for instances in (0, 1, 25):
        _build(instances)


def main() -> None:
    group_messy_udt()
    print("\nDone. 3 files.")


if __name__ == "__main__":
    main()
