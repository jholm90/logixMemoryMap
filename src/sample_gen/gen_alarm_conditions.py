"""Tag-based alarm conditions: the unpriced cost sitting in every real file.

James, 2026-09-04: *"Another thing to look at is Controller Alarms that we
use. Ive split them out a bit here and you can generate up some code to test
for them and generate them. Keep in mind that there are controller tags:
AlarmBoolArray BOOL[128], AlarmNumberArray DINT[128], AlarmDescArray
STRING[128], AlarmMoreInfoArray STRING[128] ... the controller tags are
placeholders and could be any tags so you should mute them in your
calculations. see the alarms prefixed by "Alarm1_" as they could be holding
back some of your calcuations from being accurate."*

He is right, measurably. **3,463 real AlarmCondition elements across
samples/local/, every one priced at zero.** All 8 real programs fitted on
2026-09-04 carry 200-600 each, and after the composite surcharge was
refitted their leftover residual correlates **+0.583 with alarm count** --
the strongest remaining identified driver (AOI-internal instructions -0.236,
JSR-target -0.094). This is the most likely single explanation for why those
files still sit at 3.29% instead of <1%.

WHY REAL FILES ALONE CANNOT FIT IT
----------------------------------
Real usage is essentially one shape (measured, not assumed): TRIP on a BOOL
array element, Severity 500, Expression "= 1", EvaluationPeriod "500
millisecond", and **exactly 3 associated tags on 3,455 of the 3,463**, each
with an HMIGroup. Assoc-tag count never varies independently of alarm count
in any real program on file, so the two are perfectly collinear and no
regression on real data can separate "cost per alarm" from "cost per
associated tag". That is exactly what James's four `Alarm1_*` probe files
break apart, and what this batch extends into a full sweep.

MUTING THE PLACEHOLDERS
-----------------------
James's instruction is handled structurally rather than arithmetically: the
four placeholder arrays are byte-identical in EVERY file this generator
writes, whatever the alarm content. Their storage therefore cancels exactly
in any file-to-file difference, so no subtraction, assumption or "mute this
tag" flag is needed anywhere in the analysis -- the experiment design does
it. `alarmcond_count_n000` (the same four arrays, zero alarms) is the
control every other file differences against.

GROUPS
------
A. group_count_bare (9)   alarms 0/1/2/4/8/16/32/64/128, NO assoc tags, empty
   AlarmConfig -- James's `Alarm1_NoAssociatedTagsOnlyInput` shape scaled up.
   Gives the base per-alarm cost with nothing else varying.
B. group_count_real (8)   the same ladder at the REAL shape (3 assoc tags +
   HMIGroup). Read against A, the gap is what the real-world trimmings cost,
   at every scale rather than at one point.
C. group_assoc_count (5)  32 alarms x 0/1/2/3/4 associated tags. The axis
   real data physically cannot provide.
D. group_assoc_type (4)   32 alarms x 1 assoc tag of DINT / STRING / REAL /
   BOOL. James probed DINT and STRING at n=1; this repeats them at n=32
   where a per-alarm difference is 32x easier to read, and adds the two
   types he did not.
E. group_hmigroup (4)     32 alarms, HMIGroup absent / 4 / 16 / 40 chars.
   Every other name-ish string in this model costs real bytes by length
   (alias names, AOI type names, JSR target names), so this is a live
   hypothesis, not a formality.
F. group_name_length (4)  32 alarms at name length 8/16/32/40. Same reason.
   Real names are 10-17 chars, so 8 and 16 bracket reality and 32/40 extend
   it far enough to see a step if there is one.
G. (removed -- see the comment above group_attributes: the analog
   ConditionType names were invented and Studio 5000 rejected all four.)
H. group_attributes (4)   32 alarms varying Severity, OnDelay, Latched and
   AckRequired. Probably free; cheap to prove rather than assume.

Run: python -m sample_gen.gen_alarm_conditions
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import string_array_tag_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT = Path(__file__).parent.parent.parent / "samples" / "generated" / "alarms"

# James's own placeholder set, verbatim, in EVERY file -- see "muting" above.
_PLACEHOLDER_N = 128
_NUMBER_TAG = tag_xml("AlarmNumberArray", "DINT", (_PLACEHOLDER_N,))
_DESC_TAG = string_array_tag_xml("AlarmDescArray", _PLACEHOLDER_N)
_MOREINFO_TAG = string_array_tag_xml("AlarmMoreInfoArray", _PLACEHOLDER_N)
# Extra hosts/operands used only by groups D and G; present in every file so
# they cancel there too.
_REAL_ARRAY = tag_xml("AlarmRealArray", "REAL", (_PLACEHOLDER_N,))
_BOOL_OPERAND = tag_xml("AlarmBoolOperand", "BOOL", (_PLACEHOLDER_N,))

_ASSOC_BY_TYPE = {
    "DINT": "AlarmNumberArray", "STRING": "AlarmDescArray",
    "REAL": "AlarmRealArray", "BOOL": "AlarmBoolOperand",
}
# Real order, from the corpus: Number, Description, MoreInfo.
_ASSOC_ORDER = ["AlarmNumberArray", "AlarmDescArray", "AlarmMoreInfoArray", "AlarmRealArray"]


def _condition_xml(name: str, index: int, *, assoc: list[str], hmi_group: str | None,
                   condition_type: str = "TRIP", severity: str = "500",
                   on_delay: str = "0", latched: str = "false",
                   ack_required: str = "true", limit: str = "0.0",
                   deadband: str = "0.0", expression: str = "= 1") -> str:
    """One <AlarmCondition>, attribute for attribute in the real order and
    with the real defaults, copied from James's Alarm1_* exports rather than
    composed from the schema -- the same discipline the ST batch had to be
    rebuilt under."""
    assoc_attrs = "".join(
        f' AssocTag{i}="{ref}[{index}]"' for i, ref in enumerate(assoc, start=1)
    )
    config = (
        f"<AlarmConfig>\n<HMIGroup>\n<![CDATA[{hmi_group}]]>\n</HMIGroup>\n</AlarmConfig>"
        if hmi_group is not None else "<AlarmConfig/>"
    )
    return (
        f'<AlarmCondition Name="{name}" Input="[{index}]" ConditionType="{condition_type}" '
        f'Limit="{limit}" Severity="{severity}" OnDelay="{on_delay}" OffDelay="0" '
        f'ShelveDuration="0" MaxShelveDuration="0" Deadband="{deadband}" Used="true"\n'
        f' AlarmSetOperIncluded="true" AlarmSetRollupIncluded="true" InFault="false" '
        f'AckRequired="{ack_required}" Latched="{latched}" ProgAck="false" OperAck="false" '
        f'ProgReset="false" OperReset="false" ProgSuppress="false" OperSuppress="false"\n'
        f' ProgUnsuppress="false" OperUnsuppress="false" OperShelve="false" '
        f'ProgUnshelve="false" OperUnshelve="false" ProgDisable="false" OperDisable="false" '
        f'ProgEnable="false" OperEnable="false" AlarmCountReset="false" '
        f'EvaluationPeriod="500 millisecond"\n'
        f' Expression="{expression}"{assoc_attrs}>\n{config}\n</AlarmCondition>'
    )


def _host_tag_xml(name: str, data_type: str, conditions: list[str]) -> str:
    """The alarmed tag with its <AlarmConditions> block spliced in ahead of
    <Data>, which is where real exports put it."""
    base = tag_xml(name, data_type, (_PLACEHOLDER_N,))
    if not conditions:
        return base
    block = "<AlarmConditions>\n" + "\n".join(conditions) + "\n</AlarmConditions>\n"
    marker = '\n        <Data Format="Decorated">'
    assert marker in base, "tag_xml shape changed -- alarm splice point is gone"
    return base.replace(marker, "\n" + block + marker, 1)


def _write(out_name: str, host_tag: str, description: str) -> None:
    tags = "\n".join([host_tag, _NUMBER_TAG, _DESC_TAG, _MOREINFO_TAG,
                      _REAL_ARRAY, _BOOL_OPERAND])
    l5x = build_l5x(target_name="AlarmCond", tags_xml=tags)
    out_path = OUT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "alarm_condition", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


_MUTED = ("The four placeholder arrays James named (AlarmBoolArray BOOL[128], AlarmNumberArray "
          "DINT[128], AlarmDescArray STRING[128], AlarmMoreInfoArray STRING[128]) plus a REAL "
          "and a BOOL operand array are byte-identical in EVERY file of this batch, so their "
          "storage cancels exactly in any file-to-file difference -- his 'mute them in your "
          "calculations' handled by the experiment design rather than by a subtraction. "
          "alarmcond_count_bare_n000 (same tags, zero alarms) is the control.")

_COUNTS = (0, 1, 2, 4, 8, 16, 32, 64, 128)
_FIXED_N = 32  # every non-ladder group holds alarm count here


def group_count_bare() -> None:
    for n in _COUNTS:
        conds = [_condition_xml(f"AlarmBare{i:03d}", i, assoc=[], hmi_group=None)
                 for i in range(n)]
        _write(f"alarmcond_count_bare_n{n:03d}",
               _host_tag_xml("AlarmBoolArray", "BOOL", conds),
               f"{n} tag-based alarm condition(s) on a BOOL[128] controller tag, NO associated "
               f"tags and an empty <AlarmConfig> -- James's Alarm1_NoAssociatedTagsOnlyInput "
               f"shape scaled into a ladder. Gives the BASE per-alarm cost with nothing else "
               f"varying. Alarm conditions are currently priced at ZERO by this engine and "
               f"there are 3,463 of them across the real corpus, 200-600 in every real "
               f"program measured (OQ-ALARMCOND). " + _MUTED)


def group_count_real() -> None:
    for n in (1, 2, 4, 8, 16, 32, 64, 128):
        conds = [
            _condition_xml(f"AlarmReal{i:03d}", i, assoc=_ASSOC_ORDER[:3], hmi_group="LineA")
            for i in range(n)
        ]
        _write(f"alarmcond_count_real_n{n:03d}",
               _host_tag_xml("AlarmBoolArray", "BOOL", conds),
               f"{n} alarm condition(s) at the REAL production shape -- 3 associated tags "
               f"(Number/Desc/MoreInfo, the real order) plus an HMIGroup, which is what "
               f"3,455 of the 3,463 real corpus conditions look like. Differenced against "
               f"alarmcond_count_bare_n{n:03d} at the same n, the gap is exactly what the "
               f"associated tags and HMIGroup cost, measured at every scale rather than at "
               f"one point. " + _MUTED)


def group_assoc_count() -> None:
    for k in range(5):
        conds = [_condition_xml(f"AlarmAssoc{i:03d}", i, assoc=_ASSOC_ORDER[:k], hmi_group=None)
                 for i in range(_FIXED_N)]
        _write(f"alarmcond_assoc_k{k}",
               _host_tag_xml("AlarmBoolArray", "BOOL", conds),
               f"{_FIXED_N} alarm conditions, each with exactly {k} associated tag(s), no "
               f"HMIGroup, everything else fixed. THE axis real data physically cannot "
               f"provide: every real program on file has exactly 3 associated tags on every "
               f"alarm, so assoc-count and alarm-count are perfectly collinear there and no "
               f"regression can separate cost-per-alarm from cost-per-associated-tag. " + _MUTED)


def group_assoc_type() -> None:
    for type_name, ref in _ASSOC_BY_TYPE.items():
        conds = [_condition_xml(f"AlarmType{i:03d}", i, assoc=[ref], hmi_group=None)
                 for i in range(_FIXED_N)]
        _write(f"alarmcond_assoc_type_{type_name.lower()}",
               _host_tag_xml("AlarmBoolArray", "BOOL", conds),
               f"{_FIXED_N} alarm conditions, each with ONE associated tag of type {type_name} "
               f"({ref}[i]), no HMIGroup. James probed DINT and STRING at n=1 "
               f"(Alarm1_OneAssociatedDINT / Alarm1_OneAssociatedSTRING); this repeats both at "
               f"n={_FIXED_N}, where a per-alarm difference is {_FIXED_N}x easier to read out "
               f"of a Capacity number, and adds REAL and BOOL which he did not have. If an "
               f"associated tag is a fixed-size reference the four land identically; if the "
               f"referenced type matters, STRING should stand out. " + _MUTED)


def group_hmigroup() -> None:
    for label, group in (("none", None), ("len04", "Grp1"), ("len16", "LineA_Station12"),
                         ("len40", "LineAStation12UpperDeckInfeedConveyr40")):
        conds = [_condition_xml(f"AlarmHmi{i:03d}", i, assoc=[], hmi_group=group)
                 for i in range(_FIXED_N)]
        _write(f"alarmcond_hmigroup_{label}",
               _host_tag_xml("AlarmBoolArray", "BOOL", conds),
               f"{_FIXED_N} alarm conditions with HMIGroup "
               f"{'absent (empty <AlarmConfig/>)' if group is None else f'= {len(group)} characters'}"
               f", no associated tags. Every other name-ish string this project has measured "
               f"costs real bytes by LENGTH -- alias names (56+8*floor(len/8)), AOI type names, "
               f"JSR target names (+80 per 8 chars) -- so an HMIGroup string plausibly does too, "
               f"and 3,455 real conditions carry one. " + _MUTED)


def group_name_length() -> None:
    for length in (8, 16, 32, 40):
        conds = []
        for i in range(_FIXED_N):
            suffix = f"{i:03d}"
            name = ("A" * (length - len(suffix)) + suffix)
            conds.append(_condition_xml(name, i, assoc=[], hmi_group=None))
        _write(f"alarmcond_namelen_{length:02d}",
               _host_tag_xml("AlarmBoolArray", "BOOL", conds),
               f"{_FIXED_N} alarm conditions whose Name is exactly {length} characters, "
               f"nothing else varying. Real alarm names run 10-17 characters (mean 13.9), so 8 "
               f"and 16 bracket reality and 32/40 extend far enough to expose a step. Same "
               f"hypothesis as the HMIGroup group and the same precedent behind it: name "
               f"length is a real, measured cost everywhere else in this model. " + _MUTED)


# group_condition_type REMOVED 2026-09-04 -- real Studio 5000 rejected all
# four files. TRIP_HIGH / TRIP_LOW / DEVIATION: "Failed to set the
# 'ConditionType' property (Invalid condition type.)"; and plain TRIP on a
# REAL host: "Failed to set the 'Expression' property (Condition expression
# is not compatible with condition type or the data type of the input.)".
#
# Those three type names were INVENTED. 100% of the 3,463 real corpus
# conditions are TRIP on a BOOL, so this project has zero evidence for what
# any other ConditionType is called or what expression form an analog input
# requires -- exactly the situation where the ST batch had to be rebuilt for
# guessing instead of measuring. Not re-guessed here. The analog side stays
# unmeasured until James supplies the real ConditionType list from the
# Studio 5000 dropdown and one working analog example; see OQ-ALARMCOND.


def group_attributes() -> None:
    for label, kwargs, why in (
        ("severity_low", {"severity": "1"}, "Severity 1 instead of the universal real 500"),
        ("severity_high", {"severity": "1000"}, "Severity 1000 instead of the real 500"),
        ("ondelay", {"on_delay": "1000"}, "OnDelay 1000ms, which 3,449 of 3,463 real conditions use"),
        ("latched_noack", {"latched": "true", "ack_required": "false"},
         "Latched=true / AckRequired=false, the inverse of every real condition on file"),
    ):
        conds = [_condition_xml(f"AlarmAttr{i:03d}", i, assoc=[], hmi_group=None, **kwargs)
                 for i in range(_FIXED_N)]
        _write(f"alarmcond_attr_{label}",
               _host_tag_xml("AlarmBoolArray", "BOOL", conds),
               f"{_FIXED_N} alarm conditions varying one behavioural attribute: {why}. Read "
               f"against alarmcond_count_bare_n{_FIXED_N:03d}, which is identical except for "
               f"this attribute. Expected to be FREE (these look like flags in a fixed-size "
               f"record, not stored strings) -- generated to prove that rather than assume it, "
               f"since assuming it is what left 3,463 real alarm conditions priced at zero in "
               f"the first place. " + _MUTED)


def main() -> None:
    group_count_bare()
    group_count_real()
    group_assoc_count()
    group_assoc_type()
    group_hmigroup()
    group_name_length()
    group_attributes()
    print("\nDone. 38 files.")


if __name__ == "__main__":
    main()
