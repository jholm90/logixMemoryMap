import xml.etree.ElementTree as ET

from l5x_memory_analyzer.parser.modules import parse_modules

# Structurally mirrors real corpus module XML (samples/local/, gitignored --
# not copied here, hand-built to match the same shape: Connections carrying
# real InputSize/OutputSize attributes, ConfigTag carrying ConfigSize).
_MODULES_XML = """
<RSLogix5000Content SchemaRevision="1.0">
  <Controller Name="Test">
    <Modules>
      <Module Name="Local" CatalogNumber="5069-L330ERMS2">
        <Ports>
          <Port Id="1" Address="0" Type="5069" Upstream="false"/>
        </Ports>
      </Module>
      <Module Name="IB16_1" CatalogNumber="5069-IB16/A">
        <Ports>
          <Port Id="1" Address="1" Type="5069" Upstream="true"/>
        </Ports>
        <Communications>
          <ConfigTag ConfigSize="64" ExternalAccess="Read/Write">
            <Data Format="L5K"><![CDATA[[68,160]]]></Data>
          </ConfigTag>
          <Connections>
            <Connection Name="Standard" RPI="10000" Type="Input" InputSize="4" OutputSize="0"/>
          </Connections>
        </Communications>
      </Module>
      <Module Name="Safety_1" CatalogNumber="5069-IB8S/A">
        <Communications>
          <Connections>
            <Connection Name="SafetyInput" RPI="10000" Type="SafetyInputDataDriven" InputSize="52" OutputSize="0"/>
            <Connection Name="Standard" RPI="10000" Type="Output" InputSize="4" OutputSize="4"/>
          </Connections>
        </Communications>
      </Module>
    </Modules>
  </Controller>
</RSLogix5000Content>
"""


def _root(xml: str) -> ET.Element:
    return ET.fromstring(xml)


def test_module_with_no_communications_has_zero_sizes():
    modules = parse_modules(_root(_MODULES_XML))
    local = next(m for m in modules if m.name == "Local")
    assert local.catalog_number == "5069-L330ERMS2"
    assert local.connection_input_bytes == 0
    assert local.connection_output_bytes == 0
    assert local.config_bytes == 0
    assert local.stated_total_bytes == 0


def test_module_config_and_connection_sizes_parsed_from_real_attributes():
    modules = parse_modules(_root(_MODULES_XML))
    ib16 = next(m for m in modules if m.name == "IB16_1")
    assert ib16.config_bytes == 64
    assert ib16.connection_input_bytes == 4
    assert ib16.connection_output_bytes == 0
    assert ib16.stated_total_bytes == 68


def test_module_with_multiple_connections_sums_all_of_them():
    # Real safety-module shape: a Standard connection AND a SafetyInput
    # connection both exist under the same Module -- both must be summed,
    # not just the first Connection found.
    modules = parse_modules(_root(_MODULES_XML))
    safety = next(m for m in modules if m.name == "Safety_1")
    assert safety.connection_input_bytes == 52 + 4
    assert safety.connection_output_bytes == 4


def test_no_modules_element_returns_empty_list():
    root = ET.fromstring('<RSLogix5000Content><Controller Name="Test"/></RSLogix5000Content>')
    assert parse_modules(root) == []


def test_three_modules_all_parsed():
    modules = parse_modules(_root(_MODULES_XML))
    assert len(modules) == 3
    assert {m.name for m in modules} == {"Local", "IB16_1", "Safety_1"}
