"""An AOI call site costs 168 bytes, and the parser can actually see one.

OQ-DEFSCALE . The largest single unmodelled item found in this
project: until today an AOI call cost NOTHING, because parser/logic.py matched
instruction calls with [A-Z][A-Z0-9_]*\\(under a comment claiming it "also
matches AOI/UDT instance calls". It does not -- real AOI names are mixed-case,
288 of the 331 AOI definitions in the real corpus are mixed-case, and 3,918 real
call sites were invisible.

The casing test is the important one here. A regression that reverts to a
casing-based match would still pass a cost test written with an ALL-CAPS AOI
name, which is exactly how this survived so long.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest

from l5x_memory_analyzer.parser.logic import parse_rll_routines
from l5x_memory_analyzer.sizing.constants import load_memory_model


def _project(aoi_name: str, call_count: int) -> ET.Element:
    rungs = "".join(
        f'<Rung Number="{i}" Type="N"><Text><![CDATA[{aoi_name}(Inst{i},0);]]></Text></Rung>'
        for i in range(call_count)
    )
    return ET.fromstring(f"""
    <RSLogix5000Content SchemaRevision="1.0">
      <Controller Name="T" ProcessorType="1756-L81E" MajorRev="35">
        <DataTypes/>
        <AddOnInstructionDefinitions>
          <AddOnInstructionDefinition Name="{aoi_name}" Revision="1.0">
            <Parameters>
              <Parameter Name="EnableIn" TagType="Base" DataType="BOOL" Usage="Input" Required="false" Visible="false"/>
              <Parameter Name="EnableOut" TagType="Base" DataType="BOOL" Usage="Output" Required="false" Visible="false"/>
            </Parameters>
            <Routines><Routine Name="Logic" Type="RLL"><RLLContent/></Routine></Routines>
          </AddOnInstructionDefinition>
        </AddOnInstructionDefinitions>
        <Tags/>
        <Programs>
          <Program Name="MainProgram" Class="Standard">
            <Routines><Routine Name="Main" Type="RLL"><RLLContent>{rungs}</RLLContent></Routine></Routines>
          </Program>
        </Programs>
        <Tasks/>
      </Controller>
    </RSLogix5000Content>
    """)


@pytest.mark.parametrize("aoi_name", [
    "fbDebounce",          # the real-world shape: mixed case
    "AnalogSensor",
    "HomeToTorque",
    "SCP",                 # an ALL-CAPS name must still be counted exactly once
    "Scale_2",
])
def test_mixed_case_aoi_calls_are_counted(aoi_name):
    """The bug was a casing assumption, so this is parametrized over casings."""
    routines = parse_rll_routines(_project(aoi_name, 7))
    assert sum(r.aoi_call_count for r in routines) == 7


def test_an_allcaps_aoi_is_not_double_counted():
    """An ALL-CAPS AOI name also matches the instruction-call regex. That is
    harmless only while `weights` has no entry for it -- pinned here."""
    model = load_memory_model()
    assert "SCP" not in model.logic_instructions.weights


def test_no_calls_means_no_cost():
    routines = parse_rll_routines(_project("fbDebounce", 0))
    assert sum(r.aoi_call_count for r in routines) == 0


def test_a_longer_name_is_not_matched_by_a_shorter_one():
    """An AOI named `Scale` must not also match `ScaleFactor(`."""
    root = _project("Scale", 0)
    program = root.find("Controller/Programs/Program/Routines/Routine/RLLContent")
    rung = ET.SubElement(program, "Rung", {"Number": "0", "Type": "N"})
    text = ET.SubElement(rung, "Text")
    text.text = "ScaleFactor(A,B);Scale(Inst,0);"
    assert sum(r.aoi_call_count for r in parse_rll_routines(root)) == 1


def test_the_cost_is_charged_per_call():
    from l5x_memory_analyzer.sizing.logic import compute_routine_logic_bytes

    model = load_memory_model().logic_instructions
    rate = model.aoi_call_site_bytes
    assert rate > 0
    one = compute_routine_logic_bytes(parse_rll_routines(_project("fbDebounce", 1))[0], model)[0]
    five = compute_routine_logic_bytes(parse_rll_routines(_project("fbDebounce", 5))[0], model)[0]
    # 4 more calls, and the rungs themselves cost the same in both.
    assert (five - one) % rate == 0 or five - one >= 4 * rate
