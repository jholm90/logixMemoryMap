"""An unmeasured one-operator ST shape is reported as a coverage gap, not a crash."""

from __future__ import annotations

import xml.etree.ElementTree as ET

from l5x_memory_analyzer.sizing.constants import load_memory_model
from l5x_memory_analyzer.sizing.report import build_report

def test_one_operator_real_gap_is_reported(regenerate):
    sample = regenerate("gen_st_realism") / "streal" / "streal_mixed400.L5X"
    _, errors = build_report(ET.parse(sample).getroot(), load_memory_model())
    gaps = [e for e in errors if e.path.startswith("coverage/st_expression/")]
    # A one-operator REAL multiply is measured (stshape_real_mul400 = stshape_real400), so the
    # file that once carried this flag carries none; an unmeasured class still reports itself.
    assert not gaps
    from l5x_memory_analyzer.sizing.constants import load_memory_model as _m
    assert _m().structured_text.unmeasured_one_operator_class(["**"], dest_is_real=True)
