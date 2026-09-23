"""OQ-ALARMCONDREAL: the per-condition alarm cost at REAL condition counts.

The real-shape count sweep (alarmcond_count_real_n001..n128) prices every
condition exactly -- a flat +16 file residual at every count -- but it stops at
128, and real programs carry 200, 400 and 600. The two real readings that
disagreed with the formula came from derived files later found not to import,
so the question is simply whether the law holds at real scale.

Real shape, verified against all 18 real exports: 4,655 of their 4,663
conditions are exactly this -- TRIP, severity 500, an array-indexed input on a
BOOL array host, three associated tags (Number, Description, MoreInfo) and an
HMI group. No real program uses alarm sets or another condition type.

The host and associated arrays are sized 640 in every file, so tag storage is
identical across the family and only the condition count moves: 0 (control),
200, 400, 600.

Run: python -m sample_gen.gen_alarm_real_count
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import string_array_tag_xml, tag_xml
from sample_gen.gen_alarm_conditions import _ASSOC_ORDER, _condition_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT = Path(__file__).parent.parent.parent / "samples" / "generated" / "alarms"

SIZE = 640
COUNTS = (0, 200, 400, 600)


def _host(conditions: list[str]) -> str:
    base = tag_xml("AlarmBoolArray", "BOOL", (SIZE,))
    if not conditions:
        return base
    block = "<AlarmConditions>\n" + "\n".join(conditions) + "\n</AlarmConditions>\n"
    marker = '\n        <Data Format="Decorated">'
    assert marker in base, "tag_xml shape changed -- alarm splice point is gone"
    return base.replace(marker, "\n" + block + marker, 1)


def main() -> None:
    fixed = [
        tag_xml("AlarmNumberArray", "DINT", (SIZE,)),
        string_array_tag_xml("AlarmDescArray", SIZE),
        string_array_tag_xml("AlarmMoreInfoArray", SIZE),
        tag_xml("AlarmRealArray", "REAL", (SIZE,)),
    ]
    for n in COUNTS:
        conds = [_condition_xml(f"AlarmReal{i:03d}", i, assoc=_ASSOC_ORDER[:3], hmi_group="LineA")
                 for i in range(n)]
        l5x = build_l5x(target_name="AlarmRealCount", tags_xml="\n".join([_host(conds)] + fixed))
        out_name = f"alarmcond_realcount_n{n:03d}"
        out_path = OUT / f"{out_name}.L5X"
        bytes_ = write_sample(l5x, out_path)
        append_manifest_row(
            out_name,
            f"OQ-ALARMCONDREAL at real scale: {n} alarm conditions in the real production shape "
            f"(TRIP, 3 associated tags, HMI group) on a BOOL[{SIZE}] host; host and associated "
            f"arrays fixed at {SIZE} in every file so only the condition count moves. n=0 is the "
            f"control.",
            "alarm_condition", out_path, bytes_)
        print(f"Wrote {out_path} (predicted {bytes_} bytes)")
    print(f"\nDone. {len(COUNTS)} files.")


if __name__ == "__main__":
    main()
