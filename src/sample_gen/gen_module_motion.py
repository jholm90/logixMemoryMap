"""Motion node/drive module batch (2026-08-27, James uploaded real corpus
files: "heres samples for power supply, single axis and dual axis drives.
I gave you single instance and three copies of same axis. the dual drive
i gave one sample doubled up for reference.").

Real files (samples/local/motion_p208/, gitignored): p208_Node.L5X (2198-
P208 power supply alone, no axis -- baseline), p208_Node_axis.L5X (+ the
P208's own on-board axis + MOTION_GROUP), p208_D012_NodeAndAxis.L5X (+ a
2198-D012-ERS3 single-axis Kinetix 5700 drive module + its own axis),
p208_D012_NodeAndAxisDual.L5X (SAME single D012 module, but with a SECOND
axis tag riding on it -- a real dual-axis-capable drive hosting 2 axes off
one module, not two separate modules), p208_S086_NodeAndAxis.L5X (a
2198-S086-ERS3 SAFETY-rated servo drive + its own axis). Every "NodeAndAxis"
file keeps the P208's own on-board axis tag too (confirmed real, not
assumed) -- James's own test design isolates each addition on top of a
consistent baseline, same convention this project uses everywhere else.

Module XML genericized (customer names/IDs stripped) but structurally
verbatim from these real files. The AXIS_CIP_DRIVE/MOTION_GROUP TAG shape
reuses gen_axis_composite.py's own already-validated `_AXIS_TAG_XML`
template (confirmed against James's real corpus previously) rather than
building a new one from these files' own axis tags -- same predefined
structure, no reason to introduce an unvalidated variant.

Real module-level structural facts confirmed this pass:
  - P208 (power supply), D012 (single/dual-axis drive), and S086 (safety
    drive) all share the SAME module shape: `ConfigData` (not ConfigTag,
    L5K blob only, no Decorated structure -- same shape as the CIP Safety
    I/O module found earlier) + two Connections (A_MotionDiagnostics, a
    real 19-member Decorated Structure; B_MotionSync/B_MotionSync2, bare,
    no InputTag/OutputTag at all).
  - S086 (safety-rated) has NO separate safety Connection or SafetyNetwork
    attribute at the module level, unlike the 1734-IB8S/B CIP Safety I/O
    module -- Kinetix safety data rides the same channel as standard
    motion data. Its own AXIS_CIP_DRIVE tag is the SAME plain shape as a
    non-safety drive's, not a separate safety structure.
  - A "dual axis" drive module doesn't add a second Module element -- it's
    the SAME module with a second AXIS_CIP_DRIVE tag pointing at it (real,
    confirmed: p208_D012_NodeAndAxisDual.L5X has exactly one <Module
    CatalogNumber="2198-D012-ERS3"> but two Axis tags).

Run: python -m sample_gen.gen_module_motion
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from sample_gen.gen_axis_composite import _AXIS_TAG_XML
from sample_gen.manifest import append_manifest_row, write_sample_unmodeled
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "modules"


def _write_unmodeled(l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    write_sample_unmodeled(l5x, out_path)
    append_manifest_row(out_name, description, "modules", out_path, 0)
    print(f"Wrote {out_path} (predicted N/A -- module cost unmodeled, see OQ-MODULEIO)")


# ---------------------------------------------------------------------------
# Shared module XML -- P208 power supply, genericized from p208_Node.L5X.
# ---------------------------------------------------------------------------

_P208_MODULE_XML = """\
<Module Name="P208" CatalogNumber="2198-P208" Vendor="1" ProductType="48" ProductCode="4" Major="14" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule"/>
<Ports>
<Port Id="2" Address="192.168.1.1" Type="Ethernet" Upstream="true"/>
</Ports>
<Communications>
<ConfigData ConfigSize="376">
<Data Format="L5K"><![CDATA[[380,3,257,4,294257767,2,2565904,131588,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,460,-65280,0,0,0,0,0,1120403456,0,0,1120403456,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]]></Data>
</ConfigData>
<Connections>
<Connection Name="A_MotionDiagnostics" RPI="1000" Type="DiagnosticInput" EventID="0" ProgrammaticallySendEventTrigger="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:MotionDevice_Diagnostics:S:0">
<DataValueMember Name="LostControllerToDeviceTransmissions" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="LateControllerToDeviceTransmissions" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="LostDeviceToControllerTransmissions" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="LateDeviceToControllerTransmissions" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="LastControllerToDeviceTime" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="AverageControllerToDeviceTime" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="MaximumControllerToDeviceTime" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="LastDeviceToControllerTime" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="AverageDeviceToControllerTime" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="MaximumDeviceToControllerTime" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="LastSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="AverageSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="MaximumSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="TimingStatisticsEnabled" DataType="SINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="ControllerToDeviceConnectionSize" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="DeviceToControllerConnectionSize" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="NominalControllerToDeviceTime" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="NominalDeviceToControllerTime" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="CoarseUpdatePeriod" DataType="INT" Radix="Decimal" Value="0"/>
</Structure>
</Data>
</InputTag>
</Connection>
<Connection Name="B_MotionSync" RPI="0" Type="MotionSync" EventID="0" ProgrammaticallySendEventTrigger="false"/>
</Connections>
</Communications>
</Module>"""


def _drive_module_xml(name: str, catalog: str, safety_enabled: str, address: str = "192.168.1.2") -> str:
    """D012 (single/dual-axis, non-safety) and S086 (safety-rated) share
    this exact shape -- only Name/CatalogNumber/SafetyEnabled differ,
    confirmed by direct comparison of both real files.

    `address` defaults to a DIFFERENT IP than _P208_MODULE_XML's hardcoded
    192.168.1.1 (2026-08-27, real Studio 5000 import bug found by James:
    every drive module built from this function used to hard-code the
    SAME 192.168.1.1 as the P208 power supply it's always paired with in
    this file, a real "Duplicate IP Address" error the moment both are
    imported together -- which every single_axis/dual_axis/safety_axis
    file here does. That duplicate-IP failure was also silently sinking
    the axis tags: when a module fails Ethernet import, nothing else in
    the file can resolve a MotionModule reference against it, so the
    'axis tags never got made' symptom James reported was a downstream
    consequence of this one root cause, not a second bug)."""
    return f"""\
<Module Name="{name}" CatalogNumber="{catalog}" Vendor="1" ProductType="45" ProductCode="11" Major="14" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false" SafetyEnabled="{safety_enabled}">
<EKey State="CompatibleModule"/>
<Ports>
<Port Id="2" Address="{address}" Type="Ethernet" Upstream="true"/>
</Ports>
<Communications>
<ConfigData ConfigSize="468">
<Data Format="L5K"><![CDATA[[472,7,1793,11,434110479,18,10000,33686020,5,0,0,0,0,0,0,0,0,-1027080192,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,33686018,33686018,67108864,460,1,1045220557,0,0,0,0,1120403456,1120403456,0,1120403456,1124859904,0,0,1120403456,1,0,3,0,0,0,0,0,1,0,0,0,3,0,0,0,0,0,0,0,0,0,0,0,262148,0,50528513,0,0,0,8192000,8192125,67305985,0,0,0,67305985,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,50987786,0,655370,0]]]></Data>
</ConfigData>
<Connections>
<Connection Name="A_MotionDiagnostics" RPI="1000" Type="DiagnosticInput" EventID="0" ProgrammaticallySendEventTrigger="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:Motion_Diagnostics:S:1">
<DataValueMember Name="LostControllerToDriveTransmissions" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="LateControllerToDriveTransmissions" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="LostDriveToControllerTransmissions" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="LateDriveToControllerTransmissions" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="LastControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="AverageControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="MaximumControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="LastDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="AverageDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="MaximumDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="LastSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="AverageSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="MaximumSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="TimingStatisticsEnabled" DataType="SINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="ControllerToDriveConnectionSize" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="DriveToControllerConnectionSize" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="NominalControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="NominalDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="CoarseUpdatePeriod" DataType="INT" Radix="Decimal" Value="0"/>
</Structure>
</Data>
</InputTag>
</Connection>
<Connection Name="B_MotionSync2" RPI="2000" Type="MotionSync" EventID="0" ProgrammaticallySendEventTrigger="false"/>
</Connections>
</Communications>
</Module>"""


def _axis_tag(name: str, motion_module: str) -> str:
    """One AXIS_CIP_DRIVE tag using the already-validated shape from
    gen_axis_composite.py, retargeted at a specific drive module/channel
    (MotionModule) and given its own tag name -- MOTION_GROUP is shared
    (built separately, once per file) since only one Motion Group exists
    per real file here, matching every real corpus example found.

    AxisID is also given a unique value here (2026-08-27, real Studio 5000
    import bug found by James: every axis tag from this helper carried the
    SAME literal AxisID="510977205" from _AXIS_TAG_XML's single real
    reference value -- harmless with exactly one axis in a file, but a
    real "Duplicate Axis ID" import error the moment 2+ axis tags coexist,
    which every dual-axis/safety/Kinetix-bus file here does. AxisID is an
    opaque per-axis discriminator (no documented semantic meaning beyond
    uniqueness), so a stable hash of the tag name is a safe way to make
    every axis tag's ID distinct without touching any other real value."""
    body = _AXIS_TAG_XML.split('<Tag Name="MotionGroup"')[0]
    body = body.replace('Name="Axis_Cip_Drive"', f'Name="{name}"')
    body = body.replace('MotionModule="&lt;NA>"', f'MotionModule="{motion_module}"')
    body = body.replace('MotionGroup="MotionGroup"', 'MotionGroup="Motion"')
    digest = int(hashlib.sha256(name.encode()).hexdigest(), 16)
    unique_axis_id = str(digest % 900_000_000 + 100_000_000)
    body = body.replace('AxisID="510977205"', f'AxisID="{unique_axis_id}"')
    return body


_MOTION_GROUP_TAG_XML = """\
      <Tag Name="Motion" TagType="Base" DataType="MOTION_GROUP" ExternalAccess="Read/Write">
        <Data Format="MotionGroup">
<MotionGroupParameters CoarseUpdatePeriod="2000" PhaseShift="0" GeneralFaultType="Non Major Fault" AutoTagUpdate="Enabled" Alternate1UpdateMultiplier="1" Alternate2UpdateMultiplier="1"/>
        </Data>
      </Tag>"""


def group_motion_power_supply() -> None:
    """P208 power supply module alone, no axis -- pure baseline, isolates
    what a bare motion power-supply module costs with zero axes on it."""
    l5x = build_l5x(target_name="ModuleMotion1P208", tags_xml="", extra_modules_xml=_P208_MODULE_XML)
    _write_unmodeled(
        l5x, "modulemotion_p208_baseline",
        "2198-P208 motion power supply module alone, no axis -- genericized from real corpus "
        "(samples/local/motion_p208/p208_Node.L5X), isolates the module's own baseline cost with "
        "zero axes. See OQ-MODULEIO.",
    )


def group_motion_power_supply_axis() -> None:
    """P208 + its own on-board axis + MOTION_GROUP -- isolates what the
    power supply's own axis costs, on top of the bare-module baseline."""
    tags_xml = f"{_MOTION_GROUP_TAG_XML}\n{_axis_tag('P208_Axis', 'P208:Ch1')}"
    l5x = build_l5x(target_name="ModuleMotion2P208Axis", tags_xml=tags_xml, extra_modules_xml=_P208_MODULE_XML)
    _write_unmodeled(
        l5x, "modulemotion_p208_with_axis",
        "2198-P208 motion power supply + its own on-board AXIS_CIP_DRIVE axis + MOTION_GROUP -- "
        "genericized from real corpus (p208_Node_axis.L5X), isolates the power supply's own axis "
        "cost on top of the bare-module baseline. See OQ-MODULEIO.",
    )


def group_motion_single_axis_drive() -> None:
    """P208 (with its own axis, same as group 2) + a separate single-axis
    2198-D012-ERS3 Kinetix 5700 drive module + ITS OWN axis -- isolates
    the cost of adding a whole separate single-axis drive module."""
    module_xml = _P208_MODULE_XML + "\n" + _drive_module_xml("D012_1", "2198-D012-ERS3", "false")
    tags_xml = (
        f"{_MOTION_GROUP_TAG_XML}\n"
        f"{_axis_tag('P208', 'P208:Ch1')}\n"
        f"{_axis_tag('D012_Axis', 'D012_1:Ch1')}"
    )
    l5x = build_l5x(target_name="ModuleMotion3D012", tags_xml=tags_xml, extra_modules_xml=module_xml)
    _write_unmodeled(
        l5x, "modulemotion_d012_single_axis",
        "2198-P208 (+ its own axis) + a separate single-axis 2198-D012-ERS3 Kinetix 5700 drive "
        "module + its own axis -- genericized from real corpus (p208_D012_NodeAndAxis.L5X), "
        "isolates the cost of a whole separate single-axis drive module + axis on top of the "
        "P208-with-axis baseline. See OQ-MODULEIO.",
    )


def group_motion_dual_axis_drive() -> None:
    """SAME single D012 module as group 3, but with a SECOND axis tag
    riding on it (real, confirmed: a dual-axis-capable drive hosting 2
    axes off ONE module, not two modules) -- isolates the cost of a 2nd
    axis on an already-present drive module, vs a fresh module entirely."""
    module_xml = _P208_MODULE_XML + "\n" + _drive_module_xml("D012_1", "2198-D012-ERS3", "false")
    tags_xml = (
        f"{_MOTION_GROUP_TAG_XML}\n"
        f"{_axis_tag('P208', 'P208:Ch1')}\n"
        f"{_axis_tag('D012_Axis', 'D012_1:Ch1')}\n"
        f"{_axis_tag('D012_Axis1', 'D012_1:Ch3')}"
    )
    l5x = build_l5x(target_name="ModuleMotion4D012Dual", tags_xml=tags_xml, extra_modules_xml=module_xml)
    _write_unmodeled(
        l5x, "modulemotion_d012_dual_axis",
        "SAME single 2198-D012-ERS3 module as modulemotion_d012_single_axis, but with a SECOND "
        "AXIS_CIP_DRIVE tag riding on it (real dual-axis-capable drive, confirmed: one Module "
        "element, two Axis tags, not two modules) -- genericized from real corpus "
        "(p208_D012_NodeAndAxisDual.L5X, real channels Ch1/Ch3 -- fixed 2026-09-03, a real bug "
        "had this as Ch1/Ch2, see OPEN_QUESTIONS.md OQ-193ECMETR), isolates the cost of a 2nd "
        "axis on an already-present "
        "drive module vs a whole fresh module. See OQ-MODULEIO.",
    )


def group_motion_safety_axis_drive() -> None:
    """P208 (with its own axis) + a SAFETY-rated 2198-S086-ERS3 servo
    drive + its own axis -- same module shape as D012 (no separate safety
    Connection/SafetyNetwork at the module level, confirmed by direct
    comparison), isolates whether SafetyEnabled costs anything extra."""
    module_xml = _P208_MODULE_XML + "\n" + _drive_module_xml("S086", "2198-S086-ERS3", "false")
    tags_xml = (
        f"{_MOTION_GROUP_TAG_XML}\n"
        f"{_axis_tag('P208', 'P208:Ch1')}\n"
        f"{_axis_tag('S086_Axis', 'S086:Ch1')}"
    )
    l5x = build_l5x(target_name="ModuleMotion5S086", tags_xml=tags_xml, extra_modules_xml=module_xml)
    _write_unmodeled(
        l5x, "modulemotion_s086_safety_axis",
        "2198-P208 (+ its own axis) + a SAFETY-rated 2198-S086-ERS3 Kinetix 5700 servo drive + its "
        "own axis -- genericized from real corpus (p208_S086_NodeAndAxis.L5X). S086's own Module "
        "shape is IDENTICAL to D012's (no separate safety Connection/SafetyNetwork attribute at "
        "the module level, confirmed by direct comparison -- Kinetix safety data rides the "
        "standard motion channel) and its AXIS_CIP_DRIVE tag is the same plain shape as a "
        "non-safety drive's -- isolates whether a safety-rated drive costs anything beyond a "
        "plain one. See OQ-MODULEIO.",
    )


def main() -> None:
    group_motion_power_supply()
    group_motion_power_supply_axis()
    group_motion_single_axis_drive()
    group_motion_dual_axis_drive()
    group_motion_safety_axis_drive()
    print("\nDone. 5 files -- power-supply baseline, power-supply+axis, single-axis drive, "
          "dual-axis drive (same module), safety-rated drive.")


if __name__ == "__main__":
    main()
