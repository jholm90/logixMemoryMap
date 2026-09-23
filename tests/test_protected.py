"""Source-protected content is priced at a minimum, never at zero."""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from l5x_memory_analyzer.sizing.constants import load_memory_model  # noqa: E402
from l5x_memory_analyzer.sizing.report import build_report  # noqa: E402

MODEL = load_memory_model()

_XML = """
<RSLogix5000Content SchemaRevision="1.0">
  <Controller Name="T" ProcessorType="1756-L81E">
    <DataTypes/>
    <AddOnInstructionDefinitions>
      <EncodedData EncodedType="AddOnInstructionDefinition" Name="Locked" Revision="1.0">
        <Parameters>
          <Parameter Name="EnableIn" TagType="Base" DataType="BOOL" Usage="Input" Required="false" Visible="false"/>
          <Parameter Name="EnableOut" TagType="Base" DataType="BOOL" Usage="Output" Required="false" Visible="false"/>
          <Parameter Name="Setpoint" TagType="Base" DataType="REAL" Usage="Input" Required="true" Visible="true"/>
          <Parameter Name="Count" TagType="Base" DataType="DINT" Usage="Output" Required="true" Visible="true"/>
        </Parameters>
        ENCRYPTEDPAYLOAD
      </EncodedData>
    </AddOnInstructionDefinitions>
    <Tags>
      <Tag Name="Inst" TagType="Base" DataType="Locked"/>
    </Tags>
    <Programs>
      <Program Name="MainProgram">
        <Tags/>
        <Routines>
          <Routine Name="MainRoutine" Type="RLL">
            <RLLContent><Rung Number="0" Type="N"><Text><![CDATA[NOP();]]></Text></Rung></RLLContent>
          </Routine>
          <EncodedData EncodedType="Routine" Name="Hidden" Type="RLL">PAYLOAD</EncodedData>
        </Routines>
      </Program>
    </Programs>
  </Controller>
</RSLogix5000Content>
"""


def test_protected_aoi_instance_is_priced_and_flagged():
    entries, errors = build_report(ET.fromstring(_XML), MODEL)
    inst = [e for e in entries if e.path.endswith("/Inst") or e.path.endswith("Inst")]
    assert inst and sum(e.bytes for e in inst) > 0
    assert any(e.path == "coverage/source_protected" and "MINIMUM" in e.message for e in errors)


def test_protected_routine_pays_a_routine_shell():
    with_routine = build_report(ET.fromstring(_XML), MODEL)[0]
    without = build_report(ET.fromstring(_XML.replace(
        '<EncodedData EncodedType="Routine" Name="Hidden" Type="RLL">PAYLOAD</EncodedData>', "")), MODEL)[0]
    assert sum(e.bytes for e in with_routine) > sum(e.bytes for e in without)
