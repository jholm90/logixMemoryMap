"""The 2 bytes per tag left over once the alarm terms are removed.

Written 2026-09-12, reconciling the 68 `alarmdef_*` and 33 `alarmsep_*` rows
that had been captured and never read together. Read together they collapse to
ONE law that fits 64 of the 68 and all 33 with zero residual:

    deficit = SUM over UDTs of (8 + 8 x floor(BIT_members / 2))

`alarmdef_l81_d1_*` sits at -72 because its UDT has 16 BIT members and
8 + 8x8 = 72 exactly; the d02/d04/d08 rows sit at -16/-32/-64 because each of
their 2/4/8 UDTs has one BIT member and 8 + 0 = 8 apiece. Four processor and
firmware variants (l81, l81 v35, l81 v38, l902ts) give the identical numbers,
so the law is platform-invariant across the active set.

WHAT THAT DISPROVES. OQ-ALARMDEF recorded "definition count is linear at
exactly 8 bytes per DatatypeAlarmDefinition, zero residual" off the d0N ladder.
That ladder has definition count and UDT count both equal to N -- perfectly
collinear -- and `alarmsep_u04_b04_def{1,2,3}` breaks it: four UDTs held fixed
while the definition count runs 1, 2, 3, 4, and all four files are
BYTE-IDENTICAL. The 8 belongs to the UDT, not to the alarm definition. Alarm
definitions cost exactly ZERO, now confirmed 19 ways (15 matched
`_alarm`/`_noalarm` pairs plus the def1/2/3/4 quadruple). Message text and
member-alarm count were already known free and are re-confirmed here.

WHAT IS LEFT, and it is this batch. Exactly four of the 68 rows carry a
residual beyond the law, and they are the tag ladders:

    alarmdef_*_inst_t01   -2      alarmdef_*_noinst_t01   -2
    alarmdef_*_inst_t04   -8      alarmdef_*_noinst_t04   -8
    alarmdef_*_inst_t16  -32      alarmdef_*_noinst_t16  -32

**2 bytes per tag**, and identical with and without an alarm definition, so it
is a TAG term and not an alarm term at all. The UDT in those files has 16 BIT
members -- and 16 bits is exactly 2 bytes. So the hypothesis with a mechanism
behind it is that a BIT-member UDT tag's own backing storage is not being
charged: `ceil(BIT_members / 8)` bytes per tag.

That predicts a per-tag deficit of 1, 2, 4 and 8 bytes at 8, 16, 32 and 64 BIT
members. The existing data cannot test it: every file in the tag ladder has the
same 16-member UDT, so "2 per tag" and "bits/8 per tag" fit it identically --
the same one-variable trap the disproved 8-per-definition claim fell into.

    alarmbits_b{08,16,32,64}_t{01,04,16}   12 files

BIT-member count crossed with tag count. Under `ceil(bits/8)` per tag the
deficit beyond the law runs 1/4/16, 2/8/32, 4/16/64, 8/32/128 across the grid;
under a flat 2 per tag every row of the grid reads 2/8/32 regardless of member
count. Those are far apart at b64/t16 -- 128 against 32 -- on files whose other
terms cancel exactly.

No alarm definitions anywhere in this batch. They are now known to cost zero,
so including them would add a term this batch does not need and cannot see.

Run: python -m sample_gen.gen_alarm_bitbacking
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, tag_xml, udt_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT = Path(__file__).parent.parent.parent / "samples" / "generated" / "alarms"

BIT_COUNTS = (8, 16, 32, 64)
TAG_COUNTS = (1, 4, 16)

UDT_NAME = "AlarmSrcType"


def _members(count: int) -> list[MemberSpec]:
    """`count` BOOL members, which Logix stores as BIT members over hidden
    backing SINTs -- the same shape the alarmdef/alarmsep UDTs use, so this
    batch differences straight against both."""
    return [MemberSpec(f"Sts_A{i:02d}", "BOOL") for i in range(count)]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    written = 0
    for bits in BIT_COUNTS:
        members = _members(bits)
        udt = udt_xml(UDT_NAME, members)
        law = 8 + 8 * (bits // 2)
        for tags in TAG_COUNTS:
            tags_xml = "\n".join(
                tag_xml(f"AlarmSrc{i:02d}", UDT_NAME, udt_members=members)
                for i in range(tags)
            )
            name = f"alarmbits_b{bits:02d}_t{tags:02d}"
            l5x = build_l5x(target_name=f"AlarmBits{bits:02d}T{tags:02d}",
                            tags_xml=tags_xml, extra_datatypes_xml=udt)
            out = OUT / f"{name}.L5X"
            bytes_ = write_sample(l5x, out)
            append_manifest_row(
                name,
                f"ONE UDT of {bits} BOOL (BIT) members with {tags} tag(s) of it, and NO alarm "
                f"definition anywhere. Reconciling the 68 alarmdef_* and 33 alarmsep_* rows "
                f"together collapses them to one law -- deficit = sum over UDTs of "
                f"(8 + 8 x floor(BIT_members/2)), here {law} for the single UDT -- which fits 64 of "
                f"the 68 and all 33 with zero residual, and which DISPROVES the recorded "
                f"'8 bytes per DatatypeAlarmDefinition' (that ladder had definition count and UDT "
                f"count both equal to N; alarmsep_u04_b04_def1/2/3 holds UDTs at 4, varies "
                f"definitions, and is byte-identical). The only rows left over are the tag ladders, "
                f"at exactly 2 bytes per tag with AND without a definition -- so a tag term, not an "
                f"alarm term. Their UDT has 16 BIT members and 16 bits is 2 bytes, so the "
                f"hypothesis with a mechanism is that a BIT-member UDT tag's own backing storage "
                f"goes uncharged: ceil(bits/8) per tag. Every existing file in that ladder has the "
                f"same 16-member UDT, so 'flat 2 per tag' and 'bits/8 per tag' fit it identically "
                f"-- the same one-variable trap the 8-per-definition claim fell into. This grid "
                f"separates them: ceil(bits/8) predicts {-(bits + 7) // 8 * tags:+d} beyond the law "
                f"here, a flat rate predicts {-2 * tags:+d}. OQ-ALARMDEF.",
                "alarms", out, bytes_,
            )
            written += 1
    print(f"Total: {written}")


if __name__ == "__main__":
    main()
