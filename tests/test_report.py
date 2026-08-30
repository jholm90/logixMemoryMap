import xml.etree.ElementTree as ET

from l5x_memory_analyzer.sizing.constants import load_memory_model
from l5x_memory_analyzer.sizing.report import build_report

MODEL = load_memory_model()

_XML = """
<RSLogix5000Content SchemaRevision="1.0">
  <Controller Name="Test">
    <DataTypes/>
    <AddOnInstructionDefinitions>
      <AddOnInstructionDefinition Name="fbDebounce" Class="None">
        <Parameters>
          <Parameter Name="EnableIn" DataType="BOOL" Usage="Input" Dimension="0"/>
          <Parameter Name="RawTag" DataType="DINT" Usage="InOut" Dimension="0"/>
        </Parameters>
        <LocalTags>
          <LocalTag Name="DebTmr" DataType="TIMER"/>
        </LocalTags>
      </AddOnInstructionDefinition>
    </AddOnInstructionDefinitions>
    <Tags>
      <Tag Name="RealDint" TagType="Base" DataType="DINT"/>
      <Tag Name="AliasedIO" TagType="Alias" AliasFor="Local:2:I.Ch0Data"/>
      <Tag Name="RunTmr" TagType="Base" DataType="TIMER"/>
      <Tag Name="DebSensor1" TagType="Base" DataType="fbDebounce"/>
    </Tags>
    <Programs/>
  </Controller>
</RSLogix5000Content>
"""


def test_alias_tags_size_not_error():
    root = ET.fromstring(_XML)
    entries, errors = build_report(root, MODEL)

    assert errors == []
    by_path = {e.path: e for e in entries}

    # Alias tags carry their own overhead shape (RESOLVED_QUESTIONS.md
    # OQ-ALIASSIZE): 56 + 8*(len(name)//8), no separate data-space term.
    alias = by_path["controller/AliasedIO"]
    assert alias.bytes == 56 + 8  # "AliasedIO", 9 chars -> floor(9/8)=1
    assert alias.data_type == "ALIAS"
    assert alias.basis == "KNOWN"

    # Every real tag's own raw data size now also carries tag_overhead
    # (RESOLVED_QUESTIONS.md OQ-TAGOVERHEAD): 84 + 8*(len(name)//8).
    timer = by_path["controller/RunTmr"]
    assert timer.bytes == 12 + 84  # TIMER(12) + tag_overhead("RunTmr", 6 chars)
    assert timer.basis == "KNOWN"

    # total_bytes / pct_of_total shouldn't be thrown off by the alias entry
    real_dint = by_path["controller/RealDint"]
    assert real_dint.bytes == 4 + 92  # DINT(4) + tag_overhead("RealDint", 8 chars)

    aoi_instance = by_path["controller/DebSensor1"]
    # EnableIn(BOOL,4) + DebTmr(TIMER,12), InOut excluded, + tag_overhead("DebSensor1", 10 chars)
    assert aoi_instance.bytes == 16 + 92
    # UDT-alignment is KNOWN now; standalone BOOL's own ASSUMED tag is the
    # weakest remaining link for this AOI instance.
    assert aoi_instance.basis == "ASSUMED"

    # AOI *definition* cost (2026-08-26, OQ-AOIDEF wiring; name-length term
    # added 2026-08-29) -- separate line item from the instance above, one
    # per declared AOI regardless of instance count. fbDebounce's only
    # counted declared item is DebTmr (EnableIn excluded by name, RawTag
    # excluded already at parse time since it's InOut): base(1184) + 20*1
    # + name_length_bytes("fbDebounce"). "fbDebounce" is 10 chars ->
    # bucket=max(0,(10-7)//4)=0 -> 8*0 + (-8) = -8.
    aoi_def = by_path["udt_definitions/fbDebounce"]
    assert aoi_def.bytes == 1184 + 20 - 8
    assert aoi_def.basis == "FITTED"

    # total now also includes the project_baseline entry (2026-08-23,
    # empty_project_baseline) -- present on every real report, not just
    # this fixture's 3 sized tags.
    baseline = by_path["project_baseline"]
    assert baseline.bytes == MODEL.empty_project_baseline_bytes
    grand_total = (
        real_dint.bytes + timer.bytes + aoi_instance.bytes + alias.bytes + aoi_def.bytes + baseline.bytes
    )
    assert real_dint.pct_of_total == (real_dint.bytes / grand_total) * 100


def test_udt_definition_cost_appears_once_per_type_used_by_multiple_instances():
    xml = """
    <RSLogix5000Content SchemaRevision="1.0">
      <Controller Name="Test">
        <DataTypes>
          <DataType Name="Point3D" Family="NoFamily" Class="User">
            <Members>
              <Member Name="X" DataType="DINT" Dimension="0"/>
              <Member Name="Y" DataType="DINT" Dimension="0"/>
              <Member Name="Z" DataType="DINT" Dimension="0"/>
            </Members>
          </DataType>
        </DataTypes>
        <AddOnInstructionDefinitions/>
        <Tags>
          <Tag Name="PointA" TagType="Base" DataType="Point3D"/>
          <Tag Name="PointB" TagType="Base" DataType="Point3D"/>
        </Tags>
        <Programs/>
      </Controller>
    </RSLogix5000Content>
    """
    root = ET.fromstring(xml)
    entries, errors = build_report(root, MODEL)
    assert errors == []

    definition_entries = [e for e in entries if e.category == "udt_definition"]
    assert len(definition_entries) == 1  # once per distinct type, not once per instance
    definition = definition_entries[0]
    assert definition.data_type == "Point3D"
    # base(160) + per_member(16)*3 + name_per_8_chars(8)*ceil(7/8)=1 = 216
    assert definition.bytes == 160 + 16 * 3 + 8 * 1

    by_path = {e.path: e for e in entries}
    point_a = by_path["controller/PointA"]
    # 3*DINT(4) = 12 tight-packed + tag_overhead("PointA", 6 chars) = 84
    assert point_a.bytes == 12 + 84


def test_udt_definition_counted_even_when_only_used_as_a_nested_member():
    xml = """
    <RSLogix5000Content SchemaRevision="1.0">
      <Controller Name="Test">
        <DataTypes>
          <DataType Name="Inner" Family="NoFamily" Class="User">
            <Members>
              <Member Name="V" DataType="DINT" Dimension="0"/>
            </Members>
          </DataType>
          <DataType Name="Outer" Family="NoFamily" Class="User">
            <Members>
              <Member Name="Nested" DataType="Inner" Dimension="0"/>
            </Members>
          </DataType>
        </DataTypes>
        <AddOnInstructionDefinitions/>
        <Tags>
          <Tag Name="OuterTag" TagType="Base" DataType="Outer"/>
        </Tags>
        <Programs/>
      </Controller>
    </RSLogix5000Content>
    """
    root = ET.fromstring(xml)
    entries, errors = build_report(root, MODEL)
    assert errors == []

    definition_names = {e.data_type for e in entries if e.category == "udt_definition"}
    # Inner is never a top-level tag's own DataType, only reachable via
    # Outer's member -- still needs its own definition cost counted.
    assert definition_names == {"Inner", "Outer"}


def test_udt_definition_cost_counts_bool_members_correctly():
    # Regression test for the 2026-08-22 fix: declared_member_count must
    # exclude only the HIDDEN backing SINT, not the visible BIT-alias
    # members it backs -- an all-BOOL UDT was computing 0 declared members
    # (its only non-bit-alias member IS the hidden one), undercounting.
    xml = """
    <RSLogix5000Content SchemaRevision="1.0">
      <Controller Name="Test">
        <DataTypes>
          <DataType Name="SweepTypeBOOL" Family="NoFamily" Class="User">
            <Members>
              <Member Name="ZZZZZZZZZZBoolMember00" DataType="SINT" Dimension="0" Hidden="true"/>
              <Member Name="M0" DataType="BIT" Dimension="0" Hidden="false" Target="ZZZZZZZZZZBoolMember00" BitNumber="0"/>
              <Member Name="M1" DataType="BIT" Dimension="0" Hidden="false" Target="ZZZZZZZZZZBoolMember00" BitNumber="1"/>
              <Member Name="M2" DataType="BIT" Dimension="0" Hidden="false" Target="ZZZZZZZZZZBoolMember00" BitNumber="2"/>
              <Member Name="M3" DataType="BIT" Dimension="0" Hidden="false" Target="ZZZZZZZZZZBoolMember00" BitNumber="3"/>
            </Members>
          </DataType>
        </DataTypes>
        <AddOnInstructionDefinitions/>
        <Tags/>
        <Programs/>
      </Controller>
    </RSLogix5000Content>
    """
    root = ET.fromstring(xml)
    from l5x_memory_analyzer.sizing.udt import compute_udt_definition_cost
    from l5x_memory_analyzer.parser.datatypes import parse_data_types
    data_types = parse_data_types(root)
    bytes_, confidence = compute_udt_definition_cost("SweepTypeBOOL", data_types, MODEL)
    # Real Capacity delta for this exact real corpus shape (4 BOOL members,
    # 13-char name "SweepTypeBOOL") is 272: base(160) + per_member(16)*4 +
    # name_per_8_chars(8)*ceil(13/8)=2 + bool_run_bonus(32) = 272.
    assert bytes_ == 160 + 16 * 4 + 8 * 2 + 32
    assert bytes_ == 272


def _blank_root(software_revision: str, processor_type: str) -> ET.Element:
    xml = f"""
    <RSLogix5000Content SchemaRevision="1.0" SoftwareRevision="{software_revision}">
      <Controller Name="Test" ProcessorType="{processor_type}">
        <DataTypes/>
        <AddOnInstructionDefinitions/>
        <Tags/>
        <Programs/>
      </Controller>
    </RSLogix5000Content>
    """
    return ET.fromstring(xml)


def test_firmware_baseline_delta_applies_for_confirmed_major_version():
    # OQ-BASELINE-PROCFW, wired 2026-08-29: v31 real capture shows a real
    # +11,240 over the v34/v35 baseline (see memory_model.yaml
    # firmware_baseline_delta) -- confirmed against 1756-L81E.
    root = _blank_root("31.02", "1756-L81E")
    entries, errors = build_report(root, MODEL)
    assert errors == []
    by_path = {e.path: e for e in entries}
    fw_entry = by_path["firmware_baseline_delta"]
    assert fw_entry.bytes == 11240
    assert fw_entry.data_type == "FW_V31_BASELINE"
    assert "safety_capable_baseline_delta" not in by_path


def test_firmware_baseline_delta_absent_for_confirmed_v34_v35():
    # v34/v35 is the already-confirmed reference baseline itself -- no
    # correction, no extra entry emitted at all.
    for rev in ("34.01", "35.05"):
        root = _blank_root(rev, "1756-L81E")
        entries, _ = build_report(root, MODEL)
        assert "firmware_baseline_delta" not in {e.path for e in entries}


def test_firmware_baseline_delta_absent_for_unconfirmed_major_version():
    # v38's only real capture is WINDOW-TITLE-MISMATCH-contaminated (see
    # OPEN_QUESTIONS.md OQ-BASELINE-PROCFW) -- not trusted, stays
    # unadjusted until a real capture lands.
    root = _blank_root("38.02", "1756-L81E")
    entries, _ = build_report(root, MODEL)
    assert "firmware_baseline_delta" not in {e.path for e in entries}


def test_safety_capable_baseline_delta_applies_to_5069_safety_suffix():
    root = _blank_root("35.05", "5069-L330ERMS2")
    entries, errors = build_report(root, MODEL)
    assert errors == []
    by_path = {e.path: e for e in entries}
    safety_entry = by_path["safety_capable_baseline_delta"]
    assert safety_entry.bytes == 296
    assert "firmware_baseline_delta" not in by_path


def test_safety_capable_baseline_delta_absent_for_non_safety_5069():
    root = _blank_root("35.05", "5069-L330ER")
    entries, _ = build_report(root, MODEL)
    assert "safety_capable_baseline_delta" not in {e.path for e in entries}


def test_firmware_and_safety_baseline_deltas_stack_additively():
    # v31 + safety-suffix catalog: both real, independent effects (see
    # OPEN_QUESTIONS.md OQ-BASELINE-PROCFW -- the +296 safety gap
    # reproduces identically at v31/v32/v33, confirming no interaction
    # term is needed).
    root = _blank_root("31.02", "5069-L330ERMS2")
    entries, _ = build_report(root, MODEL)
    by_path = {e.path: e for e in entries}
    assert by_path["firmware_baseline_delta"].bytes == 11240
    assert by_path["safety_capable_baseline_delta"].bytes == 296


def test_catalog_baseline_delta_applies_to_confirmed_1769_processor_type():
    # OQ-BASELINE-PROCFW, 1769-series thread, wired 2026-08-29: real
    # capture shows 1769-L24ER-QBFC1B costs +80,832 over the flat baseline.
    root = _blank_root("35.05", "1769-L24ER-QBFC1B")
    entries, errors = build_report(root, MODEL)
    assert errors == []
    by_path = {e.path: e for e in entries}
    catalog_entry = by_path["catalog_baseline_delta"]
    assert catalog_entry.bytes == 80832
    assert catalog_entry.data_type == "CATALOG_BASELINE"


def test_catalog_baseline_delta_is_exact_string_match_not_prefix():
    # A single suffix character changes the real value by over 13,000
    # bytes (1769-L24ER-QB1B=67,160 vs -QBFC1B=80,832) -- an unconfirmed
    # 1769 catalog must NOT silently inherit a sibling's real value.
    root = _blank_root("35.05", "1769-L24ER-NOTREAL")
    entries, _ = build_report(root, MODEL)
    assert "catalog_baseline_delta" not in {e.path for e in entries}


def _root_with_module(catalog_number: str) -> ET.Element:
    xml = f"""
    <RSLogix5000Content SchemaRevision="1.0">
      <Controller Name="Test">
        <DataTypes/>
        <AddOnInstructionDefinitions/>
        <Tags/>
        <Programs/>
        <Modules>
          <Module Name="Local" CatalogNumber="1756-L81E">
            <Ports><Port Id="1" Address="0" Type="ICP" Upstream="false"/></Ports>
          </Module>
          <Module Name="TestMod" CatalogNumber="{catalog_number}">
            <Ports><Port Id="1" Address="1" Type="ICP" Upstream="true"/></Ports>
            <Communications>
              <Connections>
                <Connection Name="Standard" RPI="10000" Type="Input" InputSize="4" OutputSize="0">
                  <InputTag ExternalAccess="Read/Write">
                    <Data Format="Decorated">
                      <Structure DataType="AB:5000_DI16:I:0">
                        <DataValueMember Name="Fault" DataType="DINT" Value="0"/>
                      </Structure>
                    </Data>
                  </InputTag>
                </Connection>
              </Connections>
            </Communications>
          </Module>
        </Modules>
      </Controller>
    </RSLogix5000Content>
    """
    return ET.fromstring(xml)


def test_module_overhead_uses_real_per_catalog_value_when_known():
    # OQ-MODULEIO, wired 2026-08-29: 1756-DNB has a real n=1 capture point
    # (memory_model.yaml module_overhead_by_catalog) -- 6440, not the flat
    # cross-catalog FITTED default (1672).
    root = _root_with_module("1756-DNB")
    entries, errors = build_report(root, MODEL)
    assert errors == []
    module_entry = next(e for e in entries if e.category == "module_io")
    assert module_entry.basis == "ASSUMED"
    assert module_entry.bytes == 4 + 6440  # module_defined_bytes(4) + real 1756-DNB overhead


def test_module_overhead_falls_back_to_flat_default_for_unknown_catalog():
    root = _root_with_module("9999-NOT-A-REAL-CATALOG")
    entries, errors = build_report(root, MODEL)
    assert errors == []
    module_entry = next(e for e in entries if e.category == "module_io")
    assert module_entry.basis == MODEL.module_overhead_confidence
    assert module_entry.bytes == 4 + MODEL.module_overhead_bytes
