"""Guards for the 2198 Kinetix faults found.

Three coupled defects shipped in 654 drive module instances across ~550 files:
ProductCode hardcoded to D012's for every catalog, D012's ConfigData payload for
every catalog, and 118 L5K values under ConfigSize="468" when 118 is not a real
value count for ANY 2198 module. A fourth fault was independent: a drive with no
2198 bus power supply converts and then fails Build.

These tests exist because the faults were diagnosed wrong twice from inference,
and because an earlier commit recorded the value-count error BACKWARDS ("119
against the real 118") and deleted a value to match. The checks here are against
data read out of real exports, never against anything composed.
"""

from __future__ import annotations

import re

import pytest

from sample_gen.data.kinetix import CONFIG_DATA, MODULE_IDENTITY, REAL_CONFIG_PAIRS, payload_for
from sample_gen.gen_module_motion import _drive_module_xml
from sample_gen.lint import lint_l5x

ERS3_CATALOGS = (
    "2198-D012-ERS3", "2198-D020-ERS3", "2198-D032-ERS3",
    "2198-D057-ERS3", "2198-S086-ERS3", "2198-S130-ERS3",
)


def _wrap(modules: str, processor: str = "1756-L81E") -> str:
    return f"""
    <RSLogix5000Content SchemaRevision="1.0">
      <Controller Name="T" ProcessorType="{processor}" MajorRev="35">
        <DataTypes/><AddOnInstructionDefinitions/><Tags/>
        <Modules>
          <Module Name="Local" CatalogNumber="{processor}">
            <Ports><Port Id="1" Address="0" Type="ICP" Upstream="false"/></Ports>
          </Module>
          {modules}
        </Modules>
        <Programs/><Tasks/>
      </Controller>
    </RSLogix5000Content>
    """


def test_118_values_is_not_a_real_pair():
    """The exact wrong shape that shipped. 468/118 must never be acceptable."""
    assert (468, 118) not in REAL_CONFIG_PAIRS
    assert not any(count == 118 for _size, count in REAL_CONFIG_PAIRS)
    assert {count for size, count in REAL_CONFIG_PAIRS if size == 468} == {119}


@pytest.mark.parametrize("catalog", ERS3_CATALOGS)
def test_each_catalog_gets_its_own_identity_and_payload(catalog):
    """Every catalog must differ. They were all emitting D012's values."""
    xml = _drive_module_xml("Drv1", catalog, "false")
    product_code = re.search(r'ProductCode="(\d+)"', xml).group(1)
    size = int(re.search(r'ConfigSize="(\d+)"', xml).group(1))
    body = re.search(r"CDATA\[\[(.*?)\]\]\]", xml, re.S).group(1)
    values = [v for v in body.split(",") if v]

    assert product_code == MODULE_IDENTITY[catalog][2]
    assert (size, len(values)) in REAL_CONFIG_PAIRS
    # Index 3 of the L5K blob is the same catalog discriminator as ProductCode.
    # They were wrong together, so they are checked together.
    assert values[3] == product_code


def test_the_six_catalogs_do_not_share_one_payload():
    """The false docstring claim, pinned. If these ever collapse to one value
    again, one catalog's data has spread to the others."""
    payloads = {payload_for(c)[1] for c in ERS3_CATALOGS}
    assert len(payloads) == len(ERS3_CATALOGS)


def test_unknown_catalog_raises_rather_than_substituting():
    """Silent fallback is how D012's identity reached five other catalogs."""
    with pytest.raises(ValueError, match="No verified real"):
        _drive_module_xml("Drv1", "2198-DOES-NOT-EXIST", "false")


def test_payload_accessor_rejects_a_hand_edited_count(monkeypatch):
    """A payload whose length stops matching its declared size must fail at
    generation time, not ship. This is the check the original transcription
    needed and did not have."""
    broken = dict(CONFIG_DATA["2198-D012-ERS3"])
    size, values = max(broken.items(), key=lambda kv: kv[0])
    broken[size] = values.rsplit(",", 1)[0]          # drop one value
    monkeypatch.setitem(CONFIG_DATA, "2198-D012-ERS3", broken)
    with pytest.raises(ValueError, match="holds .* but its key"):
        payload_for("2198-D012-ERS3")


def test_drive_without_bus_supply_is_a_finding():
    xml = _wrap(_drive_module_xml("Drv1", "2198-D012-ERS3", "false"))
    kinds = {f.kind for f in lint_l5x(xml)}
    assert "kinetix_drive_without_bus_supply" in kinds


def test_drive_with_bus_supply_is_clean():
    from sample_gen.gen_module_motion import _P208_MODULE_XML

    xml = _wrap(_P208_MODULE_XML + "\n"
                + _drive_module_xml("Drv1", "2198-D012-ERS3", "false", address="192.168.1.20"))
    kinds = {f.kind for f in lint_l5x(xml)}
    assert "kinetix_drive_without_bus_supply" not in kinds


def test_wrong_product_code_is_a_finding():
    """An S086 wearing D012's ProductCode -- the exact shipped state."""
    xml = _wrap('<Module Name="Drv1" CatalogNumber="2198-S086-ERS3" Vendor="1" '
                'ProductType="45" ProductCode="11" Major="13" Minor="1"/>'
                '<Module Name="PS" CatalogNumber="2198-P208"/>')
    kinds = {f.kind for f in lint_l5x(xml)}
    assert "module_identity_mismatch" in kinds


def test_configsize_payload_mismatch_is_a_finding():
    xml = _wrap('<Module Name="PS" CatalogNumber="2198-P208"/>'
                '<Module Name="Drv1" CatalogNumber="2198-D012-ERS3" Vendor="1" '
                'ProductType="45" ProductCode="11" Major="14" Minor="1">'
                '<Communications><ConfigData ConfigSize="468">'
                '<Data Format="L5K"><![CDATA[[1,2,3]]]></Data>'
                '</ConfigData></Communications></Module>')
    kinds = {f.kind for f in lint_l5x(xml)}
    assert "module_configdata_size_mismatch" in kinds


# --- Channels are per catalog ------------------------------------
# The rule these replace was catalog-blind: it checked the channel against one
# global {Ch1, Ch3} set, so it PASSED the S086-on-Ch3 shape that Studio actually
# rejects, and would have FLAGGED the one real Ch2 in the corpus. Both
# directions are asserted here so neither can come back.

def _axis_file(catalog: str, channels: tuple[str, ...]) -> str:
    modules = (
        f'<Module Name="Drv01" CatalogNumber="{catalog}" Vendor="1" ProductType="45" '
        f'ProductCode="7" Major="13" Minor="1" ParentModule="Local" ParentModPortId="2" '
        f'Inhibited="false" MajorFault="false"><Ports/></Module>'
    )
    tags = "".join(
        f'<Tag Name="Ax{i}" TagType="Base" DataType="AXIS_CIP_DRIVE"><Data Format="Axis">'
        f'<AxisParameters MotionModule="Drv01:{ch}"/></Data></Tag>'
        for i, ch in enumerate(channels)
    )
    return (
        '<RSLogix5000Content SchemaRevision="1.0" SoftwareRevision="35.05">'
        '<Controller Name="T" ProcessorType="1756-L81E" MajorRev="35" MinorRev="11">'
        f"<Modules>{modules}</Modules><Tags>{tags}</Tags>"
        "</Controller></RSLogix5000Content>"
    )


def _kinds(text):
    return {f.kind for f in lint_l5x(text)}


def test_s086_second_axis_on_ch3_is_rejected():
    """The exact shape that sank six axmarg_* files in Studio."""
    assert "drive_axis_unreal_channel" in _kinds(
        _axis_file("2198-S086-ERS3", ("Ch1", "Ch3"))
    )


def test_s086_second_axis_on_ch2_is_accepted():
    """Ch2 is real on S086 -- EmporiumEdger DRV01_BedRolls. The old global
    {Ch1, Ch3} rule would have flagged this correct file."""
    assert "drive_axis_unreal_channel" not in _kinds(
        _axis_file("2198-S086-ERS3", ("Ch1", "Ch2"))
    )


def test_d_series_second_axis_on_ch2_is_rejected():
    assert "drive_axis_unreal_channel" in _kinds(
        _axis_file("2198-D020-ERS3", ("Ch1", "Ch2"))
    )


def test_d_series_second_axis_on_ch3_is_accepted():
    assert "drive_axis_unreal_channel" not in _kinds(
        _axis_file("2198-D020-ERS3", ("Ch1", "Ch3"))
    )


def test_single_axis_drive_cannot_carry_two_axes():
    """2198-S130-ERS3 is Ch1 only in every real export."""
    assert _kinds(_axis_file("2198-S130-ERS3", ("Ch1", "Ch3"))) & {
        "drive_axis_unreal_channel",
        "drive_axis_too_many",
    }


def test_too_many_axes_on_a_dual_drive_is_flagged():
    assert "drive_axis_too_many" in _kinds(
        _axis_file("2198-D020-ERS3", ("Ch1", "Ch3", "Ch1"))
    )
