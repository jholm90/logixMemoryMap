"""Separate alarm-definition cost from UDT BIT-member cost.

The first alarm batch measured cleanly and still cannot identify what it
measured, because its two groups confound every candidate term.

In `alarmdef_*_d{02,04,08}_m1` the UDT count, the BIT-member count, the
hidden backing-SINT count and the DatatypeAlarmDefinition count are ALL
equal to N. The residual is 8N, so "8 per UDT", "8 per definition", "8 per
BIT member" and "8 per backing SINT" fit that group identically. Nothing
in it can tell them apart.

The `d1_*` group has a different shape -- 1 UDT, 16 BIT members, 2 backing
SINTs, 1 definition -- and its residual of +72 fits NONE of them:

    8 per UDT           -> 8      8 per definition -> 8
    8 per BIT member    -> 128    8 per backing SINT -> 16    actual 72

So the cost is a function of at least two of those variables, and one
more single file cannot resolve a two-variable surface. This batch varies
them independently and, critically, adds the control the first batch
never had.

GROUP A -- alarmsep_u{U}_b{B}_alarm / _noalarm (30 files, 15 pairs)
    U UDTs of B BOOL members each, crossed U in {1,2,4} against B in
    {1,2,4,8,16}, and each point built TWICE: once with a
    DatatypeAlarmDefinition on every UDT, once with the identical
    DataTypes and no <AlarmDefinitions> element at all.

    The paired control is the whole point. Differencing a pair cancels
    the UDT cost, the backing-SINT packing, the baseline and the shell
    exactly -- whatever remains IS the alarm cost, with nothing else left
    in it. The first batch had no such control, which is why its clean
    numbers are unusable.

    The same pairs read the other way -- along the _noalarm arm alone --
    measure how a UDT's BIT members and their hidden backing SINTs are
    priced, with no alarm content present. B spans 1, 2, 4, 8, 16 so the
    8-bits-per-backing-SINT boundary is crossed twice (B=8 fills one
    backing SINT exactly, B=16 fills two), which is where a packing term
    shows itself if there is one.

GROUP B -- alarmsep_u4_b4_def{1,2,3} (3 files)
    Definition count decoupled from UDT count: four identical UDTs, but
    only D of them carry a definition. Against the U=4/B=4 pair from
    group A (which supplies D=0 and D=4), this gives five points on the
    definition axis with every other variable frozen. If the cost is per
    definition, these are a straight line; if it is per UDT, they are
    flat.

Built on v35, the project standard. The already-captured alarm files are
v38, but nothing here differences against them -- every comparison is
within a pair or within group B, so the firmware only has to be constant,
and the standard decides which constant.

Run: python -m sample_gen.gen_alarm_separation
"""

from __future__ import annotations

from .builders import MemberSpec, udt_xml
from .gen_alarm_definitions import (
    _alarm_definitions_xml,
    _build_xml,
    _member_alarm_xml,
    _target_name,
    _write,
)

_CATALOG = "1756-L81E"
_MAJOR_REV = "35"
_SOFTWARE_REVISION = "35.05"

UDT_COUNTS = (1, 2, 4)
# Spans the 8-bits-per-backing-SINT boundary twice: B=8 fills exactly one
# hidden SINT, B=16 exactly two.
MEMBER_COUNTS = (1, 2, 4, 8, 16)


def _udt_name(index: int) -> str:
    return f"AlmSepType{index:02d}"


def _members(count: int) -> list[MemberSpec]:
    return [MemberSpec(f"Sts_A{i:02d}", "BOOL") for i in range(count)]


def _datatypes_xml(udt_count: int, member_count: int) -> str:
    return "\n".join(
        udt_xml(_udt_name(u), _members(member_count)) for u in range(udt_count)
    )


def _definitions_for(udt_count: int, member_count: int, definition_count: int) -> str:
    """A DatatypeAlarmDefinition on the first `definition_count` UDTs."""
    return _alarm_definitions_xml([
        (_udt_name(u), [_member_alarm_xml(i) for i in range(member_count)])
        for u in range(definition_count)
    ])


def _emit(out_name: str, udt_count: int, member_count: int, definition_count: int,
          description: str) -> int:
    l5x = _build_xml(
        _CATALOG, _target_name(out_name), _MAJOR_REV, _SOFTWARE_REVISION,
        datatypes_xml=_datatypes_xml(udt_count, member_count),
        alarm_definitions_xml=_definitions_for(udt_count, member_count, definition_count),
    )
    _write(l5x, out_name, description)
    return 1


def group_a_paired_control() -> int:
    """Every point built with and without alarms, so a pair self-differences."""
    n = 0
    for udts in UDT_COUNTS:
        for members in MEMBER_COUNTS:
            stem = f"alarmsep_u{udts:02d}_b{members:02d}"
            shared = (
                f"{udts} UDT(s) of {members} BOOL member(s) each, 1756-L81E v35"
            )
            n += _emit(
                f"{stem}_alarm", udts, members, udts,
                f"{shared}, WITH a DatatypeAlarmDefinition on every UDT ({members} "
                f"MemberAlarmDefinitions each). Pairs with {stem}_noalarm: differencing "
                f"the two cancels the UDT cost, the hidden backing-SINT packing, the "
                f"baseline and the shell exactly, leaving only the alarm cost. The first "
                f"alarm batch had no such control, which is why its clean 8N residual "
                f"cannot distinguish per-UDT from per-definition from per-BIT-member",
            )
            n += _emit(
                f"{stem}_noalarm", udts, members, 0,
                f"{shared}, with NO <AlarmDefinitions> element at all -- the paired "
                f"control for {stem}_alarm. Read along the _noalarm arm on its own, the "
                f"B sweep also measures how a UDT's BOOL members and their hidden "
                f"backing SINTs are priced with no alarm content present; B=8 fills one "
                f"backing SINT exactly and B=16 fills two, so a packing term shows itself",
            )
    return n


def group_b_definition_axis() -> int:
    """Definition count varied with UDT count frozen."""
    n = 0
    for defs in (1, 2, 3):
        n += _emit(
            f"alarmsep_u04_b04_def{defs}", 4, 4, defs,
            f"Four identical UDTs of 4 BOOL members, but only {defs} of them carrying a "
            f"DatatypeAlarmDefinition -- definition count decoupled from UDT count. With "
            f"alarmsep_u04_b04_noalarm (0 definitions) and _alarm (4) this gives five "
            f"points on the definition axis with every other variable frozen: a straight "
            f"line means the cost is per definition, flat means it is per UDT",
        )
    return n


def main() -> None:
    total = 0
    for fn in (group_a_paired_control, group_b_definition_axis):
        count = fn()
        print(f"{fn.__name__}: {count} file(s)")
        total += count
    print(f"\nDone. {total} files.")


if __name__ == "__main__":
    main()
