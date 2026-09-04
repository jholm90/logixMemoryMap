"""Tag-based alarm conditions must be found and reported, not silently zeroed.

James, 2026-09-04: *"see the alarms prefixed by 'Alarm1_' as they could be
holding back some of your calcuations from being accurate."* They were:
3,463 real AlarmCondition elements across samples/local/, every one priced
at zero, 200-600 in each of the 8 real programs whose Capacity readings the
composite surcharge was just fitted against.

Nothing here asserts a BYTE COST -- there is no capture data yet and
inventing a number would be worse than a visible hole. These pin that the
conditions are parsed correctly and surfaced loudly.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from l5x_memory_analyzer.parser.alarms import parse_alarm_conditions
from l5x_memory_analyzer.sizing.constants import load_memory_model
from l5x_memory_analyzer.sizing.coverage import audit_coverage
from l5x_memory_analyzer.sizing.report import build_report

GEN = Path(__file__).resolve().parent.parent / "samples" / "generated" / "alarms"
MODEL = load_memory_model()
_gen = pytest.mark.skipif(not GEN.is_dir(), reason="alarm batch not generated")


def _root(name: str) -> ET.Element:
    return ET.parse(GEN / f"{name}.L5X").getroot()


@_gen
def test_alarm_conditions_are_parsed_out_of_their_host_tag():
    """They are children of the <Tag> being alarmed, not of a top-level
    container -- the reason a tag-walking parser missed them entirely."""
    alarms = parse_alarm_conditions(_root("alarmcond_count_real_n128"))

    assert len(alarms) == 128
    assert {a.host_tag for a in alarms} == {"AlarmBoolArray"}
    assert all(a.host_data_type == "BOOL" and a.host_dimensions == "128" for a in alarms)
    # The real production shape: 3 associated tags + an HMIGroup, which is
    # what 3,455 of the 3,463 real corpus conditions look like.
    assert all(len(a.assoc_tags) == 3 for a in alarms)
    assert all(a.hmi_group == "LineA" for a in alarms)


@_gen
@pytest.mark.parametrize("k", [0, 1, 2, 3, 4])
def test_associated_tag_count_is_read_exactly(k):
    """AssocTag1..4 is the axis no real file can provide -- every real
    program on file has exactly 3 on every alarm, so assoc-count and
    alarm-count are perfectly collinear there."""
    alarms = parse_alarm_conditions(_root(f"alarmcond_assoc_k{k}"))
    assert len(alarms) == 32
    assert all(len(a.assoc_tags) == k for a in alarms)


@_gen
def test_alarms_are_priced_and_no_longer_reported_as_a_gap():
    """Solved exactly 2026-09-05. From 2026-09-04 until then these were
    reported as an unpriced coverage gap; now they are a real sized entry,
    and flagging them would be a false alarm -- the gap list has to shrink
    when a hole is actually closed or it stops meaning anything."""
    root = _root("alarmcond_count_real_n128")
    entries, errors = build_report(root, MODEL)

    assert not [g for g in audit_coverage(root, MODEL.logic_instructions.weights)
                if g.kind == "alarm_condition"]
    assert not [e for e in errors if e.path == "coverage/alarm_condition"]

    priced = [e for e in entries if e.category == "alarm_condition"]
    assert [e.path for e in priced] == ["alarms/AlarmBoolArray"]
    # 128 alarms x (500 + DINT 92 + STRING 256 + STRING 256) + 800 file base
    assert priced[0].bytes == 800 + 128 * (500 + 92 + 256 + 256)


@_gen
@pytest.mark.parametrize("n", [1, 2, 4, 8, 16, 32, 64, 128])
def test_bare_and_real_alarm_ladders_reproduce_exactly(n):
    """The formula is not a fit with small error -- it reconstructs every
    captured point in both ladders with ZERO residual, so these assert the
    engine total against the arithmetic, not against a tolerance."""
    cfg = MODEL.alarm_conditions
    bare = [e for e in build_report(_root(f"alarmcond_count_bare_n{n:03d}"), MODEL)[0]
            if e.category == "alarm_condition"]
    assert bare[0].bytes == cfg.file_base + n * cfg.per_condition

    real = [e for e in build_report(_root(f"alarmcond_count_real_n{n:03d}"), MODEL)[0]
            if e.category == "alarm_condition"]
    assert real[0].bytes == cfg.file_base + n * (cfg.per_condition + 92 + 256 + 256)


@_gen
@pytest.mark.parametrize("type_name,rate", [("bool", 88), ("dint", 92), ("real", 92), ("string", 256)])
def test_associated_tag_rate_is_keyed_on_the_referenced_type(type_name, rate):
    """Measured at 32 alarms x 1 associated tag. This is the axis no real
    file can provide -- every real program has exactly 3 associated tags on
    every alarm, so count and type are perfectly collinear there."""
    cfg = MODEL.alarm_conditions
    e = [x for x in build_report(_root(f"alarmcond_assoc_type_{type_name}"), MODEL)[0]
         if x.category == "alarm_condition"]
    assert e[0].bytes == cfg.file_base + 32 * (cfg.per_condition + rate)


@_gen
@pytest.mark.parametrize("name", [
    "alarmcond_hmigroup_none", "alarmcond_hmigroup_len04", "alarmcond_hmigroup_len16",
    "alarmcond_namelen_08", "alarmcond_namelen_40",
    "alarmcond_attr_severity_low", "alarmcond_attr_severity_high",
    "alarmcond_attr_ondelay", "alarmcond_attr_latched_noack",
])
def test_everything_except_count_and_associated_tags_is_free(name):
    """HMIGroup, alarm name length, Severity, OnDelay, Latched and
    AckRequired all captured byte-identical to the 32-alarm control. Alarm
    cost depends ONLY on how many alarms there are and what their
    associated tags point at -- pinned because it is exactly the kind of
    thing that gets quietly re-assumed later."""
    cfg = MODEL.alarm_conditions
    e = [x for x in build_report(_root(name), MODEL)[0] if x.category == "alarm_condition"]
    assert e[0].bytes == cfg.file_base + 32 * cfg.per_condition

@_gen
def test_placeholder_tags_are_identical_across_the_batch():
    """James: "the controller tags are placeholders and could be any tags so
    you should mute them in your calculations." Muted by construction rather
    than by subtraction -- if this ever fails, the batch has stopped being a
    controlled experiment and every difference read off it is suspect."""
    import re

    def placeholders(name: str) -> str:
        text = (GEN / f"{name}.L5X").read_text(encoding="utf-8")
        # Strip the alarmed host tag's own AlarmConditions block -- that is
        # the variable under test. Also normalise the export/creation
        # timestamps, which differ between any two files written in
        # different seconds and are not part of the experiment (a
        # long-standing property of this project's generators: ExportDate
        # changes on every regeneration regardless of content).
        text = re.sub(r"<AlarmConditions>.*?</AlarmConditions>", "", text, flags=re.S)
        text = re.sub(r"(ExportDate|ProjectCreationDate|LastModifiedDate)=\"[^\"]*\"",
                      r"\1=\"X\"", text)
        return "\n".join(line for line in text.splitlines() if line.strip())

    baseline = placeholders("alarmcond_count_bare_n000")
    for name in ("alarmcond_count_bare_n128", "alarmcond_count_real_n064",
                 "alarmcond_assoc_k4", "alarmcond_namelen_40", "alarmcond_hmigroup_len40"):
        assert placeholders(name) == baseline, name
