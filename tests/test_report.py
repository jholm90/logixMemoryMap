import xml.etree.ElementTree as ET

from l5x_memory_analyzer.sizing.constants import load_memory_model
from l5x_memory_analyzer.sizing.report import build_report

MODEL = load_memory_model()

_XML = """
<RSLogix5000Content SchemaRevision="1.0">
  <Controller Name="Test">
    <DataTypes/>
    <Tags>
      <Tag Name="RealDint" TagType="Base" DataType="DINT"/>
      <Tag Name="AliasedIO" TagType="Alias" AliasFor="Local:2:I.Ch0Data"/>
      <Tag Name="RunTmr" TagType="Base" DataType="TIMER"/>
    </Tags>
    <Programs/>
  </Controller>
</RSLogix5000Content>
"""


def test_alias_tags_size_zero_known_not_error():
    root = ET.fromstring(_XML)
    entries, errors = build_report(root, MODEL)

    assert errors == []
    by_path = {e.path: e for e in entries}

    alias = by_path["controller/AliasedIO"]
    assert alias.bytes == 0
    assert alias.data_type == "ALIAS"
    assert alias.basis == "KNOWN"

    timer = by_path["controller/RunTmr"]
    assert timer.bytes == 12
    assert timer.basis == "KNOWN"

    # total_bytes / pct_of_total shouldn't be thrown off by the alias's 0 bytes
    real_dint = by_path["controller/RealDint"]
    assert real_dint.bytes == 4
    assert real_dint.pct_of_total == (4 / 16) * 100
