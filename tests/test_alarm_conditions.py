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
def test_alarms_are_reported_as_a_coverage_gap_not_silently_dropped():
    root = _root("alarmcond_count_real_n128")
    gaps = [g for g in audit_coverage(root, MODEL.logic_instructions.weights)
            if g.kind == "alarm_condition"]

    assert len(gaps) == 1
    assert gaps[0].count == 128
    assert "384 associated-tag" in gaps[0].message
    assert "ZERO" in gaps[0].message
    # ...and it reaches the ordinary errors channel, so the CLI, the UI and
    # the CSV/XLSX export all show it without per-caller work.
    _entries, errors = build_report(root, MODEL)
    assert [e for e in errors if e.path == "coverage/alarm_condition"]


@_gen
def test_alarm_content_is_currently_free_which_is_the_whole_point():
    """0 alarms and 128 alarms predict IDENTICALLY today. That is the
    diagnostic property this batch exists to exploit: the placeholder tags
    are byte-identical across the ladder, so once real Capacity readings
    land, the entire difference is alarm cost with nothing to subtract."""
    zero = sum(e.bytes for e in build_report(_root("alarmcond_count_bare_n000"), MODEL)[0])
    many = sum(e.bytes for e in build_report(_root("alarmcond_count_real_n128"), MODEL)[0])
    assert zero == many


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
                 "alarmcond_assoc_k4", "alarmcond_namelen_40", "alarmcond_hmigroup_len64"):
        assert placeholders(name) == baseline, name
