"""An unmeasured one-operator ST shape is reported as a coverage gap, not a crash."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from l5x_memory_analyzer.sizing.constants import load_memory_model
from l5x_memory_analyzer.sizing.report import build_report

SAMPLE = Path(__file__).parent.parent / "samples" / "generated" / "streal" / "streal_mixed400.L5X"


@pytest.mark.skipif(not SAMPLE.exists(), reason="streal batch not generated")
def test_one_operator_real_gap_is_reported():
    _, errors = build_report(ET.parse(SAMPLE).getroot(), load_memory_model())
    gaps = [e for e in errors if e.path.startswith("coverage/st_expression/")]
    assert gaps and "one" in gaps[0].message and "REAL destination" in gaps[0].message
