import xml.etree.ElementTree as ET

from l5x_memory_analyzer.parser.aoi import parse_aoi_definitions
from l5x_memory_analyzer.sizing.constants import load_memory_model
from l5x_memory_analyzer.sizing.udt import RecursiveUdtError, compute_array_size

MODEL = load_memory_model()

_XML = """
<RSLogix5000Content SchemaRevision="1.0">
  <Controller Name="Test">
    <AddOnInstructionDefinitions>
      <AddOnInstructionDefinition Name="DI_V4" Class="None">
        <Parameters>
          <Parameter Name="EnableIn" DataType="BOOL" Usage="Input" Dimension="0"/>
          <Parameter Name="EnableOut" DataType="BOOL" Usage="Output" Dimension="0"/>
          <Parameter Name="OnDel" DataType="DINT" Usage="Input" Dimension="0"/>
          <Parameter Name="RawTag" DataType="DINT" Usage="InOut" Dimension="0"/>
        </Parameters>
        <LocalTags>
          <LocalTag Name="OnDelay" DataType="TIMER"/>
          <LocalTag Name="OneShot" DataType="DINT"/>
        </LocalTags>
      </AddOnInstructionDefinition>
      <AddOnInstructionDefinition Name="fbWrapper" Class="None">
        <Parameters>
          <Parameter Name="EnableIn" DataType="BOOL" Usage="Input" Dimension="0"/>
        </Parameters>
        <LocalTags>
          <LocalTag Name="Inner" DataType="DI_V4"/>
        </LocalTags>
      </AddOnInstructionDefinition>
      <AddOnInstructionDefinition Name="Cycle" Class="None">
        <LocalTags>
          <LocalTag Name="Self" DataType="Cycle"/>
        </LocalTags>
      </AddOnInstructionDefinition>
    </AddOnInstructionDefinitions>
  </Controller>
</RSLogix5000Content>
"""


def _parse():
    return parse_aoi_definitions(ET.fromstring(_XML))


def test_parses_aoi_names():
    aois = _parse()
    assert set(aois) == {"DI_V4", "fbWrapper", "Cycle"}


def test_inout_parameter_excluded_from_members():
    aois = _parse()
    member_names = [m.name for m in aois["DI_V4"].members]
    assert "RawTag" not in member_names
    assert "OnDel" in member_names


def test_aoi_instance_sizes_like_a_udt():
    aois = _parse()
    # EnableIn(BOOL,4) + EnableOut(BOOL,4) + OnDel(DINT,4) + OnDelay(TIMER,12)
    # + OneShot(DINT,4) = 28, InOut RawTag excluded entirely
    bytes_, confidence = compute_array_size("DI_V4", (), aois, MODEL)
    assert bytes_ == 28
    # UDT-alignment is now KNOWN (OQ-ALIGN resolved); standalone BOOL's own
    # ASSUMED tag (OQ-BOOLPACK's raw-data-size question, distinct from its
    # confirmed tag_overhead finding) is now the weakest remaining link.
    assert confidence == "ASSUMED"


def test_nested_aoi_local_tag_recurses():
    aois = _parse()
    # fbWrapper: EnableIn(4) + Inner(DI_V4, 28) = 32
    bytes_, _ = compute_array_size("fbWrapper", (), aois, MODEL)
    assert bytes_ == 32


def test_self_referential_aoi_raises():
    aois = _parse()
    try:
        compute_array_size("Cycle", (), aois, MODEL)
        assert False, "expected RecursiveUdtError"
    except RecursiveUdtError:
        pass
