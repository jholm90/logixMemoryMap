"""Point I/O RACK tests -- multiple real modules mounted together on ONE
adapter, not the one-module-at-a-time shape gen_module_sweep.py already
covers (2026-08-27, James: "a point io rack, one for each type of module
and on other test with multiple varied modules in one rack").

Two real racks, each extracted directly from samples/local/ (gitignored)
as the adapter + its full set of real children under ONE real 1734-AENTR/C,
deduplicated to one representative module per distinct real catalog (the
real files repeat several catalogs many times over -- a rack test needs
each TYPE once, not every physical instance, same anti-padding discipline
as everywhere else in this project). Genericized the same way as
gen_module_sweep.py: Name -> RackId_<Catalog>, Ethernet Address ->
placeholder, ExtendedProperties/Description/Comments stripped. Every
module's own real slot Address (its position on the point-bus) is kept
AS-IS from the real file -- already collision-free within each adapter's
own real rack, confirmed before writing this.

  - PtIORackA: DnR_Personal/Bender134053_201104.L5X, adapter "JB"
    (1734-AENTR/C) -- 5 distinct real child catalogs (IB8S/B safety input,
    IE2C/C analog input, IB8/C digital input via RackConnection, OE2C/C
    analog output, OB8E/C digital output via RackConnection).
  - PtIORackB: DnR_Personal/FlareFunction_311D_240731.L5X, adapter
    "Point_IO" (1734-AENTR/C) -- 6 distinct real child catalogs (adds
    IJ/C high-speed counter and OB8S/B safety output vs Rack A, drops
    OE2C/C) -- a genuinely different real module mix, not a relabeled
    copy of Rack A.

Both racks are real rack-optimized adapters (own combined Slot
InputTag/OutputTag ArrayMember, RackConnection/InAliasTag children where
that's the real shape) -- same real mechanism already confirmed
elsewhere in the sweep, just multiple real children on one adapter this
time instead of one.

Run: python -m sample_gen.gen_module_rack_pointio
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.manifest import append_manifest_row, write_sample_unmodeled
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "modules"


def _write_unmodeled(l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    write_sample_unmodeled(l5x, out_path)
    append_manifest_row(out_name, description, "modules", out_path, 0)


_RACK_A_XML = """\
<Module Name="PtIORackA_Adapter" CatalogNumber="1734-AENTR/C" Vendor="1" ProductType="12" ProductCode="196" Major="6" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="0" Type="PointIO" Upstream="false">
<Bus Size="14" />
</Port>
<Port Id="2" Address="192.168.1.50" Type="Ethernet" Upstream="true" />
</Ports>
<Communications CommMethod="805306369">
<Connections>
<Connection Name="Output" RPI="20000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_14SLOT:I:0">
<DataValueMember Name="SlotStatusBits0_31" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1100_0000_1000_1111" />
<DataValueMember Name="SlotStatusBits32_63" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111" />
<ArrayMember Name="Data" DataType="SINT" Dimensions="14" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000" />
<Element Index="[1]" Value="2#0000_0000" />
<Element Index="[2]" Value="2#0000_0000" />
<Element Index="[3]" Value="2#0000_0000" />
<Element Index="[4]" Value="2#0000_0100" />
<Element Index="[5]" Value="2#0001_1010" />
<Element Index="[6]" Value="2#0000_0011" />
<Element Index="[7]" Value="2#0000_0000" />
<Element Index="[8]" Value="2#0000_0000" />
<Element Index="[9]" Value="2#0000_0000" />
<Element Index="[10]" Value="2#0000_0000" />
<Element Index="[11]" Value="2#0000_0000" />
<Element Index="[12]" Value="2#0110_0011" />
<Element Index="[13]" Value="2#0000_0000" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[-16241,-1,[0,0,0,0,0,0,0,0,0,16,6,6,0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_14SLOT:O:0">
<ArrayMember Name="Data" DataType="SINT" Dimensions="14" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000" />
<Element Index="[1]" Value="2#0000_0000" />
<Element Index="[2]" Value="2#0000_0000" />
<Element Index="[3]" Value="2#0000_0000" />
<Element Index="[4]" Value="2#0000_0000" />
<Element Index="[5]" Value="2#0000_0000" />
<Element Index="[6]" Value="2#0000_0000" />
<Element Index="[7]" Value="2#0000_0000" />
<Element Index="[8]" Value="2#0000_0000" />
<Element Index="[9]" Value="2#0001_0000" />
<Element Index="[10]" Value="2#0000_0110" />
<Element Index="[11]" Value="2#0000_0110" />
<Element Index="[12]" Value="2#0000_0000" />
<Element Index="[13]" Value="2#0000_0000" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>
<Module Name="PtIORackA_1734IB8SB" CatalogNumber="1734-IB8S/B" Vendor="1" ProductType="35" ProductCode="15" Major="2" Minor="1" ParentModule="PtIORackA_Adapter" ParentModPortId="1" Inhibited="false" MajorFault="false" SafetyNetwork="16#0000_447e_0429_d394">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="1" Type="PointIO" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="82">
<Data Format="L5K">
[86,864,-1812573082,51911118,17608,33686018,1000,16842752,0,513,50397184,0,1025,16842752,0,513,131072
		,0,65538,65566,65566,65566,30]
</Data>
</ConfigData>
<Connections>
<Connection Name="Input" RPI="10000" Type="SafetyInput" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="40.064" MaxObservedNetworkDelay="0" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_IB8S_Safety2:I:0">
<DataValueMember Name="RunMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt00Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt03Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt05Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt06Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt07Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt00Status" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01Status" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02Status" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt03Status" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04Status" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt05Status" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt06Status" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt07Status" DataType="BOOL" Value="0" />
</Structure>
</Data>
</InputTag>
</Connection>
<Connection Name="Output" RPI="20000" Type="SafetyOutput" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="60" MaxObservedNetworkDelay="0" Unicast="true">
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_IB8S:O:0">
<DataValueMember Name="Test00Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Test01Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Test02Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Test03Data" DataType="BOOL" Value="0" />
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>
<Module Name="PtIORackA_1734IE2CC" CatalogNumber="1734-IE2C/C" Vendor="1" ProductType="115" ProductCode="24" Major="3" Minor="1" ParentModule="PtIORackA_Adapter" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="3" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="536870913">
<ConfigTag ConfigSize="42" ExternalAccess="Read/Write">
<Data Format="L5K">
[46,123,1,3277,16383,0,3113,16547,2867,16793,3,0,0,0,3277,16383,0,3113,16547,2867,16793,3,0,0,2,100]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_IE2:C:0">
<DataValueMember Name="Ch0LowEngineering" DataType="INT" Radix="Decimal" Value="3277" />
<DataValueMember Name="Ch0HighEngineering" DataType="INT" Radix="Decimal" Value="16383" />
<DataValueMember Name="Ch0DigitalFilter" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch0LAlarmLimit" DataType="INT" Radix="Decimal" Value="3113" />
<DataValueMember Name="Ch0HAlarmLimit" DataType="INT" Radix="Decimal" Value="16547" />
<DataValueMember Name="Ch0LLAlarmLimit" DataType="INT" Radix="Decimal" Value="2867" />
<DataValueMember Name="Ch0HHAlarmLimit" DataType="INT" Radix="Decimal" Value="16793" />
<DataValueMember Name="Ch0RangeType" DataType="SINT" Radix="Decimal" Value="3" />
<DataValueMember Name="Ch0LimitAlarmLatch" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch0AlarmDisable" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1LowEngineering" DataType="INT" Radix="Decimal" Value="3277" />
<DataValueMember Name="Ch1HighEngineering" DataType="INT" Radix="Decimal" Value="16383" />
<DataValueMember Name="Ch1DigitalFilter" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1LAlarmLimit" DataType="INT" Radix="Decimal" Value="3113" />
<DataValueMember Name="Ch1HAlarmLimit" DataType="INT" Radix="Decimal" Value="16547" />
<DataValueMember Name="Ch1LLAlarmLimit" DataType="INT" Radix="Decimal" Value="2867" />
<DataValueMember Name="Ch1HHAlarmLimit" DataType="INT" Radix="Decimal" Value="16793" />
<DataValueMember Name="Ch1RangeType" DataType="SINT" Radix="Decimal" Value="3" />
<DataValueMember Name="Ch1LimitAlarmLatch" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1AlarmDisable" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="NotchFilter" DataType="SINT" Radix="Decimal" Value="2" />
<DataValueMember Name="RealTimeSample" DataType="INT" Radix="Decimal" Value="100" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="InputData" RPI="80000" Type="Input" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_IE2:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="Ch0Data" DataType="INT" Radix="Decimal" Value="3306" />
<DataValueMember Name="Ch1Data" DataType="INT" Radix="Decimal" Value="19" />
<DataValueMember Name="Ch0Status" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Ch0Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0Calibration" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0LAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0HAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0LLAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0HHAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0Underrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0Overrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1Status" DataType="SINT" Radix="Binary" Value="2#0101_0101" />
<DataValueMember Name="Ch1Fault" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch1Calibration" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1LAlarm" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch1HAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1LLAlarm" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch1HHAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1Underrange" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch1Overrange" DataType="BOOL" Value="0" />
</Structure>
</Data>
</InputTag>
</Connection>
</Connections>
</Communications>
</Module>
<Module Name="PtIORackA_1734IB8C" CatalogNumber="1734-IB8/C" Vendor="1" ProductType="7" ProductCode="216" Major="3" Minor="1" ParentModule="PtIORackA_Adapter" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="4" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="1073741824">
<ConfigTag ConfigSize="36" ExternalAccess="Read/Write">
<Data Format="L5K">
[40,103,1,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_DI8:C:0">
<DataValueMember Name="Pt0FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt0FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt1FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt1FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt2FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt2FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt3FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt3FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt4FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt4FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt5FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt5FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt6FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt6FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt7FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt7FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<RackConnection>
<InAliasTag />
</RackConnection>
</Connections>
</Communications>
</Module>
<Module Name="PtIORackA_1734OE2CC" CatalogNumber="1734-OE2C/C" Vendor="1" ProductType="115" ProductCode="25" Major="3" Minor="1" ParentModule="PtIORackA_Adapter" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="7" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="536870913">
<ConfigTag ConfigSize="40" ExternalAccess="Read/Write">
<Data Format="L5K">
[44,123,1,0,0,3277,16383,-32768,32767,0,1,1,0,0,0,0,0,1638,8191,-32768,32767,0,1,1,0,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_OE2:C:0">
<DataValueMember Name="Ch0FaultValue" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch0ProgValue" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch0LowEngineering" DataType="INT" Radix="Decimal" Value="3277" />
<DataValueMember Name="Ch0HighEngineering" DataType="INT" Radix="Decimal" Value="16383" />
<DataValueMember Name="Ch0LowLimit" DataType="INT" Radix="Decimal" Value="-32768" />
<DataValueMember Name="Ch0HighLimit" DataType="INT" Radix="Decimal" Value="32767" />
<DataValueMember Name="Ch0RangeType" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch0FaultMode" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="Ch0ProgMode" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="Ch0LimitAlarmLatch" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch0AlarmDisable" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1FaultValue" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1ProgValue" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1LowEngineering" DataType="INT" Radix="Decimal" Value="1638" />
<DataValueMember Name="Ch1HighEngineering" DataType="INT" Radix="Decimal" Value="8191" />
<DataValueMember Name="Ch1LowLimit" DataType="INT" Radix="Decimal" Value="-32768" />
<DataValueMember Name="Ch1HighLimit" DataType="INT" Radix="Decimal" Value="32767" />
<DataValueMember Name="Ch1RangeType" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1FaultMode" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="Ch1ProgMode" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="Ch1LimitAlarmLatch" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1AlarmDisable" DataType="SINT" Radix="Decimal" Value="0" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="OutputData" RPI="20000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_OE2:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="Ch0Status" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Ch0Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0Calibration" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0LAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0HAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1Status" DataType="SINT" Radix="Binary" Value="2#0000_1001" />
<DataValueMember Name="Ch1Fault" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch1Calibration" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1LAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1HAlarm" DataType="BOOL" Value="1" />
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[5000,32767]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_OE2:O:0">
<DataValueMember Name="Ch0Data" DataType="INT" Radix="Decimal" Value="5000" />
<DataValueMember Name="Ch1Data" DataType="INT" Radix="Decimal" Value="32767" />
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>
<Module Name="PtIORackA_1734OB8EC" CatalogNumber="1734-OB8E/C" Vendor="1" ProductType="7" ProductCode="218" Major="3" Minor="1" ParentModule="PtIORackA_Adapter" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="8" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="1073741824">
<ConfigTag ConfigSize="12" ExternalAccess="Read/Write">
<Data Format="L5K">
[16,123,1,0,0,0,0,0,0,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_DOB8:C:0">
<DataValueMember Name="FaultMode" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="AutoRestartEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultLatchEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7FaultLatchEn" DataType="BOOL" Value="0" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<RackConnection>
<InAliasTag />
<OutAliasTag />
</RackConnection>
</Connections>
</Communications>
</Module>
"""

_RACK_B_XML = """\
<Module Name="PtIORackB_Adapter" CatalogNumber="1734-AENTR/C" Vendor="1" ProductType="12" ProductCode="196" Major="7" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="0" Type="PointIO" Upstream="false">
<Bus Size="14" />
</Port>
<Port Id="2" Address="192.168.1.50" Type="Ethernet" Upstream="true" />
</Ports>
<Communications CommMethod="805306369">
<Connections>
<Connection Name="Output" RPI="5000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_14SLOT:I:0">
<DataValueMember Name="SlotStatusBits0_31" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1100_0000_0011_1111" />
<DataValueMember Name="SlotStatusBits32_63" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111" />
<ArrayMember Name="Data" DataType="SINT" Dimensions="14" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000" />
<Element Index="[1]" Value="2#0000_0000" />
<Element Index="[2]" Value="2#0000_0000" />
<Element Index="[3]" Value="2#0000_0000" />
<Element Index="[4]" Value="2#0000_0000" />
<Element Index="[5]" Value="2#0000_0000" />
<Element Index="[6]" Value="2#0001_0000" />
<Element Index="[7]" Value="2#1010_1010" />
<Element Index="[8]" Value="2#0000_1010" />
<Element Index="[9]" Value="2#0000_0101" />
<Element Index="[10]" Value="2#0000_0000" />
<Element Index="[11]" Value="2#0000_0000" />
<Element Index="[12]" Value="2#1111_1111" />
<Element Index="[13]" Value="2#1111_1111" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[-16321,-1,[0,0,0,0,0,0,0,0,0,0,0,0,0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_14SLOT:O:0">
<ArrayMember Name="Data" DataType="SINT" Dimensions="14" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000" />
<Element Index="[1]" Value="2#0000_0000" />
<Element Index="[2]" Value="2#0000_0000" />
<Element Index="[3]" Value="2#0000_0000" />
<Element Index="[4]" Value="2#0000_0000" />
<Element Index="[5]" Value="2#0000_0000" />
<Element Index="[6]" Value="2#0000_0000" />
<Element Index="[7]" Value="2#0000_0000" />
<Element Index="[8]" Value="2#0000_0000" />
<Element Index="[9]" Value="2#0000_0000" />
<Element Index="[10]" Value="2#0000_0000" />
<Element Index="[11]" Value="2#0000_0000" />
<Element Index="[12]" Value="2#0000_0000" />
<Element Index="[13]" Value="2#0000_0000" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>
<Module Name="PtIORackB_1734IB8SB" CatalogNumber="1734-IB8S/B" Vendor="1" ProductType="35" ProductCode="15" Major="2" Minor="1" ParentModule="PtIORackB_Adapter" ParentModPortId="1" Inhibited="false" MajorFault="false" SafetyNetwork="16#0000_4aa6_0006_cca2">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="1" Type="PointIO" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="82">
<Data Format="L5K">
[86,864,537552089,49793404,19177,33686018,1000,16842752,0,513,0,0,0,50397184,0,769,67174400,0,66305,10
		,0,0,0]
</Data>
</ConfigData>
<Connections>
<Connection Name="Input" RPI="10000" Type="SafetyInput" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="40.064" MaxObservedNetworkDelay="0" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_IB8S_Safety2:I:0">
<DataValueMember Name="RunMode" DataType="BOOL" Value="1" />
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt00Data" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt01Data" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt02Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt03Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04Data" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt05Data" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt06Data" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt07Data" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt00Status" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt01Status" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt02Status" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt03Status" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt04Status" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt05Status" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt06Status" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt07Status" DataType="BOOL" Value="1" />
</Structure>
</Data>
</InputTag>
</Connection>
<Connection Name="Output" RPI="20000" Type="SafetyOutput" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="60" MaxObservedNetworkDelay="0" Unicast="true">
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_OB8S:O:0">
<DataValueMember Name="Test00Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Test01Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Test02Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Test03Data" DataType="BOOL" Value="0" />
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>
<Module Name="PtIORackB_1734OB8SB" CatalogNumber="1734-OB8S/B" Vendor="1" ProductType="35" ProductCode="16" Major="2" Minor="1" ParentModule="PtIORackB_Adapter" ParentModPortId="1" Inhibited="false" MajorFault="false" SafetyNetwork="16#0000_4aa6_0006_cca2">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="2" Type="PointIO" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="26">
<Data Format="L5K">
[30,864,1181255011,49864333,19177,16843752,16843009,16843009,257]
</Data>
</ConfigData>
<Connections>
<Connection Name="Input" RPI="10000" Type="SafetyInput" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="40.064" MaxObservedNetworkDelay="0" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_OB8S_Safety1:I:0">
<DataValueMember Name="RunMode" DataType="BOOL" Value="1" />
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt00OutputStatus" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt01OutputStatus" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt02OutputStatus" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt03OutputStatus" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt04OutputStatus" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt05OutputStatus" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt06OutputStatus" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt07OutputStatus" DataType="BOOL" Value="1" />
</Structure>
</Data>
</InputTag>
</Connection>
<Connection Name="Output" RPI="20000" Type="SafetyOutput" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="60" MaxObservedNetworkDelay="0" Unicast="true">
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_OB8S:O:0">
<DataValueMember Name="Pt00Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt03Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt05Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt06Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt07Data" DataType="BOOL" Value="0" />
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>
<Module Name="PtIORackB_1734IJC" CatalogNumber="1734-IJ/C" Vendor="1" ProductType="109" ProductCode="15" Major="3" Minor="1" ParentModule="PtIORackB_Adapter" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="3" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="536870913">
<ConfigTag ConfigSize="22" ExternalAccess="Read/Write">
<Data Format="L5K">
[26,123,0,1,113,1,0,0,0,1,360,180,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_IJK:C:0">
<DataValueMember Name="CounterConfig" DataType="SINT" Radix="Binary" Value="2#0000_0001" />
<DataValueMember Name="Config_0" DataType="BOOL" Value="1" />
<DataValueMember Name="Config_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Config_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Config_3" DataType="BOOL" Value="0" />
<DataValueMember Name="Mode_4" DataType="BOOL" Value="0" />
<DataValueMember Name="Mode_5" DataType="BOOL" Value="0" />
<DataValueMember Name="Mode_6" DataType="BOOL" Value="0" />
<DataValueMember Name="ZInput" DataType="BOOL" Value="0" />
<DataValueMember Name="Filter" DataType="SINT" Radix="Binary" Value="2#0111_0001" />
<DataValueMember Name="Filter_0" DataType="BOOL" Value="1" />
<DataValueMember Name="Filter_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Filter_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Filter_3" DataType="BOOL" Value="0" />
<DataValueMember Name="FilterA" DataType="BOOL" Value="1" />
<DataValueMember Name="FilterB" DataType="BOOL" Value="1" />
<DataValueMember Name="FilterZ" DataType="BOOL" Value="1" />
<DataValueMember Name="DecimalPosition" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="TimeBase" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="GateInterval" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Scalar" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="RollOver" DataType="DINT" Radix="Decimal" Value="360" />
<DataValueMember Name="Preset" DataType="DINT" Radix="Decimal" Value="180" />
<DataValueMember Name="SSCounterControl" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SSCounterReset" DataType="BOOL" Value="0" />
<DataValueMember Name="SSCounterPreset" DataType="BOOL" Value="0" />
<DataValueMember Name="SSValueReset" DataType="BOOL" Value="0" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="OutputData" RPI="2000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_IJK:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="PresentData" DataType="DINT" Radix="Decimal" Value="180" />
<DataValueMember Name="StoredData" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Status" DataType="INT" Radix="Binary" Value="2#0000_0000_0001_0000" />
<DataValueMember Name="ZeroFreqDetect" DataType="BOOL" Value="0" />
<DataValueMember Name="StoredDataCount_2" DataType="BOOL" Value="0" />
<DataValueMember Name="StoredDataCount_3" DataType="BOOL" Value="0" />
<DataValueMember Name="AInputStatus" DataType="BOOL" Value="1" />
<DataValueMember Name="BInputStatus" DataType="BOOL" Value="0" />
<DataValueMember Name="ZInputStatus" DataType="BOOL" Value="0" />
<DataValueMember Name="NotReady" DataType="BOOL" Value="0" />
<DataValueMember Name="EEPROMFault" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgramFault" DataType="BOOL" Value="0" />
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_IJK:O:0">
<DataValueMember Name="CounterControl" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="CounterReset" DataType="BOOL" Value="0" />
<DataValueMember Name="CounterPreset" DataType="BOOL" Value="0" />
<DataValueMember Name="ValueReset" DataType="BOOL" Value="0" />
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>
<Module Name="PtIORackB_1734IE2CC" CatalogNumber="1734-IE2C/C" Vendor="1" ProductType="115" ProductCode="24" Major="3" Minor="1" ParentModule="PtIORackB_Adapter" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="5" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="536870913">
<ConfigTag ConfigSize="42" ExternalAccess="Read/Write">
<Data Format="L5K">
[46,123,1,3277,16383,0,3113,16547,2867,16793,3,0,0,0,3277,16383,0,3113,16547,2867,16793,3,0,0,2,10]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_IE2:C:0">
<DataValueMember Name="Ch0LowEngineering" DataType="INT" Radix="Decimal" Value="3277" />
<DataValueMember Name="Ch0HighEngineering" DataType="INT" Radix="Decimal" Value="16383" />
<DataValueMember Name="Ch0DigitalFilter" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch0LAlarmLimit" DataType="INT" Radix="Decimal" Value="3113" />
<DataValueMember Name="Ch0HAlarmLimit" DataType="INT" Radix="Decimal" Value="16547" />
<DataValueMember Name="Ch0LLAlarmLimit" DataType="INT" Radix="Decimal" Value="2867" />
<DataValueMember Name="Ch0HHAlarmLimit" DataType="INT" Radix="Decimal" Value="16793" />
<DataValueMember Name="Ch0RangeType" DataType="SINT" Radix="Decimal" Value="3" />
<DataValueMember Name="Ch0LimitAlarmLatch" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch0AlarmDisable" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1LowEngineering" DataType="INT" Radix="Decimal" Value="3277" />
<DataValueMember Name="Ch1HighEngineering" DataType="INT" Radix="Decimal" Value="16383" />
<DataValueMember Name="Ch1DigitalFilter" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1LAlarmLimit" DataType="INT" Radix="Decimal" Value="3113" />
<DataValueMember Name="Ch1HAlarmLimit" DataType="INT" Radix="Decimal" Value="16547" />
<DataValueMember Name="Ch1LLAlarmLimit" DataType="INT" Radix="Decimal" Value="2867" />
<DataValueMember Name="Ch1HHAlarmLimit" DataType="INT" Radix="Decimal" Value="16793" />
<DataValueMember Name="Ch1RangeType" DataType="SINT" Radix="Decimal" Value="3" />
<DataValueMember Name="Ch1LimitAlarmLatch" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1AlarmDisable" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="NotchFilter" DataType="SINT" Radix="Decimal" Value="2" />
<DataValueMember Name="RealTimeSample" DataType="INT" Radix="Decimal" Value="10" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="InputData" RPI="10000" Type="Input" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_IE2:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="Ch0Data" DataType="INT" Radix="Decimal" Value="3314" />
<DataValueMember Name="Ch1Data" DataType="INT" Radix="Decimal" Value="3384" />
<DataValueMember Name="Ch0Status" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Ch0Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0Calibration" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0LAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0HAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0LLAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0HHAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0Underrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0Overrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1Status" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Ch1Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1Calibration" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1LAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1HAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1LLAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1HHAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1Underrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1Overrange" DataType="BOOL" Value="0" />
</Structure>
</Data>
</InputTag>
</Connection>
</Connections>
</Communications>
</Module>
<Module Name="PtIORackB_1734IB8C" CatalogNumber="1734-IB8/C" Vendor="1" ProductType="7" ProductCode="216" Major="3" Minor="1" ParentModule="PtIORackB_Adapter" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="6" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="1073741824">
<ConfigTag ConfigSize="36" ExternalAccess="Read/Write">
<Data Format="L5K">
[40,103,1,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_DI8:C:0">
<DataValueMember Name="Pt0FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt0FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt1FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt1FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt2FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt2FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt3FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt3FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt4FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt4FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt5FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt5FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt6FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt6FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt7FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt7FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<RackConnection>
<InAliasTag />
</RackConnection>
</Connections>
</Communications>
</Module>
<Module Name="PtIORackB_1734OB8EC" CatalogNumber="1734-OB8E/C" Vendor="1" ProductType="7" ProductCode="218" Major="3" Minor="1" ParentModule="PtIORackB_Adapter" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="11" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="1073741824">
<ConfigTag ConfigSize="12" ExternalAccess="Read/Write">
<Data Format="L5K">
[16,123,1,0,0,0,0,-1,0,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_DOB8:C:0">
<DataValueMember Name="FaultMode" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="SINT" Radix="Binary" Value="2#1111_1111" />
<DataValueMember Name="Pt0NoLoadEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt1NoLoadEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt2NoLoadEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt3NoLoadEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt4NoLoadEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt5NoLoadEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt6NoLoadEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt7NoLoadEn" DataType="BOOL" Value="1" />
<DataValueMember Name="AutoRestartEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultLatchEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7FaultLatchEn" DataType="BOOL" Value="0" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<RackConnection>
<InAliasTag />
<OutAliasTag />
</RackConnection>
</Connections>
</Communications>
</Module>
"""


def main() -> None:
    l5x_a = build_l5x(target_name="PtIORackA", tags_xml="", extra_modules_xml=_RACK_A_XML)
    _write_unmodeled(
        l5x_a, "modulerack_pointio_a",
        "Point I/O rack test A: real 1734-AENTR/C adapter + 5 distinct real child module "
        "catalogs (IB8S/B safety input, IE2C/C analog input, IB8/C digital input via "
        "RackConnection, OE2C/C analog output, OB8E/C digital output via RackConnection), "
        "genericized from DnR_Personal/Bender134053_201104.L5X adapter 'JB', deduplicated "
        "to one representative module per real catalog. See OQ-MODULEIO.",
    )
    l5x_b = build_l5x(target_name="PtIORackB", tags_xml="", extra_modules_xml=_RACK_B_XML)
    _write_unmodeled(
        l5x_b, "modulerack_pointio_b",
        "Point I/O rack test B: a SECOND, different real 1734-AENTR/C adapter + 6 distinct "
        "real child module catalogs (adds IJ/C high-speed counter and OB8S/B safety output "
        "vs rack A, no OE2C/C), genericized from DnR_Personal/FlareFunction_311D_240731.L5X "
        "adapter 'Point_IO', deduplicated to one representative module per real catalog. "
        "See OQ-MODULEIO.",
    )
    print("Done. 2 Point I/O rack files written.")


if __name__ == "__main__":
    main()
