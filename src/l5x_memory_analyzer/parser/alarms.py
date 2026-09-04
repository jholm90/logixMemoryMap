"""Tag-based alarm conditions (Logix "alarm definitions" on a tag).

James, 2026-09-04: *"Another thing to look at is Controller Alarms that we
use... see the alarms prefixed by 'Alarm1_' as they could be holding back
some of your calculations from being accurate."*

He was right, and it is not a small corner. Measured across every real L5X
in samples/local/: **3,463 real AlarmCondition elements**, and the sizing
engine charges every one of them **zero bytes**. All 8 of the real programs
whose Capacity readings were fitted on 2026-09-04 carry 200-600 of them.
After the composite surcharge was refitted, the leftover residual on those
8 correlates **+0.583 with alarm count** -- the strongest remaining
identified driver (AOI-internal instructions -0.236, JSR-target -0.094).

WHERE THEY LIVE
---------------
Not in a top-level container: `<AlarmConditions>` is a child of the `<Tag>`
element being alarmed, so a parser that walks Controller/Tags/Tag and reads
only the Tag's own attributes misses them completely, which is exactly what
happened here.

    <Tag Name="AlarmBoolArray" DataType="BOOL" Dimensions="128" ...>
      <AlarmConditions>
        <AlarmCondition Name="..." Input="[1]" ConditionType="TRIP"
                        Severity="500" ... Expression="= 1"
                        AssocTag1="..." AssocTag2="..." AssocTag3="...">
          <AlarmConfig><HMIGroup><![CDATA[Edger1]]></HMIGroup></AlarmConfig>
        </AlarmCondition>
      </AlarmConditions>
      <Data .../>
    </Tag>

REAL USAGE PROFILE (all 3,463, measured not assumed)
----------------------------------------------------
    host tag        BOOL[224] 3,400 | BOOL[256] 55 | UDT scalar 8
    assoc tags      exactly 3 on 3,455 | 0 on 8
    AlarmConfig     HMIGroup on 3,455 | empty on 8
    ConditionType   TRIP on all 3,463
    Severity        500 on all | Expression "= 1" on all
    EvaluationPeriod "500 millisecond" on all | Latched false on all
    OnDelay         1000 on 3,449 | 0 on 14
    name length     10-17, mean 13.9

So real usage is essentially ONE shape, which is good news for modelling it
and bad news for fitting it from real files alone -- assoc-tag count never
varies independently of alarm count in any real program on file (every one
is exactly 3 per alarm), so the two cannot be separated from real data. That
is precisely what James's four `Alarm1_*` probe files vary, and what the
generated `alarmcond_*` batch extends.

NOTHING IS PRICED HERE. This module parses and reports; there is no byte
value for an alarm condition yet because no capture data exists. Inventing
one would be worse than a visible hole -- see sizing/coverage.py, which
surfaces the count so no total can quietly omit 600 alarms again.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass

_MAX_ASSOC_TAGS = 4  # Logix allows AssocTag1..AssocTag4


@dataclass(frozen=True)
class AlarmCondition:
    name: str
    host_tag: str
    host_data_type: str
    host_dimensions: str | None
    input_ref: str
    condition_type: str
    severity: str
    assoc_tags: tuple[str, ...]
    hmi_group: str | None
    used: bool

    @property
    def path(self) -> str:
        return f"alarms/{self.host_tag}/{self.name}"


def parse_alarm_conditions(root: ET.Element) -> list[AlarmCondition]:
    """Every tag-based alarm condition in the file, controller- and
    program-scoped alike (both are `<Tag>` elements with the same shape)."""
    out: list[AlarmCondition] = []
    for tag_el in root.iter("Tag"):
        conditions = tag_el.find("AlarmConditions")
        if conditions is None:
            continue
        host = tag_el.get("Name") or "?"
        host_type = tag_el.get("DataType") or "?"
        dims = tag_el.get("Dimensions")
        for ac in conditions.findall("AlarmCondition"):
            assoc = tuple(
                v for v in (ac.get(f"AssocTag{i}") for i in range(1, _MAX_ASSOC_TAGS + 1))
                if v
            )
            cfg = ac.find("AlarmConfig")
            group_el = cfg.find("HMIGroup") if cfg is not None else None
            out.append(AlarmCondition(
                name=ac.get("Name") or "?", host_tag=host, host_data_type=host_type,
                host_dimensions=dims, input_ref=ac.get("Input") or "",
                condition_type=ac.get("ConditionType") or "?",
                severity=ac.get("Severity") or "", assoc_tags=assoc,
                hmi_group=(group_el.text or "").strip() if group_el is not None else None,
                used=(ac.get("Used") or "").lower() == "true",
            ))
    return out
