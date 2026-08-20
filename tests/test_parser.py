import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from l5x_memory_analyzer.parser.datatypes import parse_data_types
from l5x_memory_analyzer.parser.load import L5XFormatError, load_l5x
from l5x_memory_analyzer.parser.tags import parse_tags

FIXTURE = Path(__file__).parent.parent / "samples/generated/misc/sample_0000_minimal_baseline.L5X"

# A UDT with a BOOL member -- exercises the hidden-SINT + BIT-alias shape
# Logix Designer itself emits, per docs/MEMORY_MODEL.md UDT packing.
_UDT_XML = """
<RSLogix5000Content SchemaRevision="1.0">
  <Controller Name="Test">
    <DataTypes>
      <DataType Name="MyUdt" Family="NoFamily" Class="User">
        <Members>
          <Member Name="Count" DataType="DINT" Dimension="0" Hidden="false"/>
          <Member Name="ZZZZZZZZZZBoolMember01" DataType="SINT" Dimension="0" Hidden="true"/>
          <Member Name="FlagA" DataType="BIT" Dimension="0" Hidden="false" Target="ZZZZZZZZZZBoolMember01" BitNumber="0"/>
        </Members>
      </DataType>
    </DataTypes>
    <Tags>
      <Tag Name="ScalarDint" TagType="Base" DataType="DINT"/>
      <Tag Name="ArrayDint" TagType="Base" DataType="DINT" Dimensions="10"/>
      <Tag Name="UdtTag" TagType="Base" DataType="MyUdt"/>
      <Tag Name="AliasedIO" TagType="Alias" AliasFor="Local:2:I.Ch0Data"/>
    </Tags>
    <Programs>
      <Program Name="MainProgram">
        <Tags>
          <Tag Name="LocalBool" TagType="Base" DataType="BOOL"/>
        </Tags>
      </Program>
    </Programs>
  </Controller>
</RSLogix5000Content>
"""


def test_load_l5x_smoke_fixture():
    doc = load_l5x(FIXTURE)
    assert doc.root.tag == "RSLogix5000Content"
    assert doc.schema_revision == "1.0"


def test_load_l5x_rejects_wrong_root():
    with tempfile.NamedTemporaryFile("w", suffix=".L5X", delete=False) as f:
        f.write("<NotL5X/>")
        path = f.name
    try:
        with pytest.raises(L5XFormatError):
            load_l5x(path)
    finally:
        Path(path).unlink()


def test_parse_data_types_bit_alias():
    root = ET.fromstring(_UDT_XML)
    data_types = parse_data_types(root)
    udt = data_types["MyUdt"]
    assert [m.name for m in udt.members] == ["Count", "ZZZZZZZZZZBoolMember01", "FlagA"]
    assert udt.members[2].is_bit_alias is True
    assert udt.members[0].is_bit_alias is False


def test_parse_tags_controller_and_program_scope():
    root = ET.fromstring(_UDT_XML)
    tags = parse_tags(root)
    by_name = {t.name: t for t in tags}

    assert by_name["ScalarDint"].scope == "controller"
    assert by_name["ScalarDint"].dimensions == ()
    assert by_name["ArrayDint"].dimensions == (10,)
    assert by_name["LocalBool"].scope == "program:MainProgram"


def test_parse_alias_tag():
    root = ET.fromstring(_UDT_XML)
    tags = parse_tags(root)
    by_name = {t.name: t for t in tags}

    alias = by_name["AliasedIO"]
    assert alias.is_alias is True
    assert alias.data_type is None
    assert alias.alias_for == "Local:2:I.Ch0Data"
    assert by_name["ScalarDint"].is_alias is False
