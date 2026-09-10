"""Datatype-level alarm definitions must be surfaced, not silently zeroed.

Found 2026-09-08 in the real 1756-L9xTS v38 exports: a stock P_PID
`<DatatypeAlarmDefinition>` with six member alarms was priced at zero and
reported nothing at all. Nothing here asserts a BYTE COST -- there is no
capture data yet and inventing a number would be worse than a visible hole.
These pin that the content is found and reported loudly. See OQ-ALARMDEF.

Files are named by firmware arm (l81_v35 / l81_v38). v35 is the project's
standard baseline and the primary arm; the v38 arm is the firmware control.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from l5x_memory_analyzer.sizing.constants import load_memory_model
from l5x_memory_analyzer.sizing.coverage import audit_coverage

GEN = Path(__file__).resolve().parent.parent / "samples" / "generated" / "alarmdefs"
MODEL = load_memory_model()
_gen = pytest.mark.skipif(not GEN.is_dir(), reason="alarmdef batch not generated")


def _gaps(name: str):
    root = ET.parse(GEN / f"{name}.L5X").getroot()
    return [g for g in audit_coverage(root, MODEL.logic_instructions.weights)
            if g.kind == "alarm_definition"]


@_gen
@pytest.mark.parametrize("name,members,definitions", [
    ("alarmdef_l81_v35_d1_m01", 1, 1),
    ("alarmdef_l81_v35_d1_m08", 8, 1),
    ("alarmdef_l81_v35_d08_m1", 8, 8),
])
def test_definitions_are_reported_as_an_unpriced_gap(name, members, definitions):
    gaps = _gaps(name)
    assert len(gaps) == 1
    assert gaps[0].count == members
    assert f"{definitions} DatatypeAlarmDefinition" in gaps[0].message


@_gen
def test_a_definition_with_no_members_is_still_reported():
    """Keying the notice on member count alone reproduced the same silence
    one level up: an empty definition is unpriced content too."""
    gaps = _gaps("alarmdef_l81_v35_d1_m00")
    assert len(gaps) == 1
    assert gaps[0].count == 1
    assert "0 MemberAlarmDefinition across 1 DatatypeAlarmDefinition" in gaps[0].message


@_gen
def test_tags_alone_are_not_reported():
    """The group B control carries tags of the type but no definition --
    flagging it would be a false alarm."""
    assert _gaps("alarmdef_l81_v35_noinst_t04") == []
