"""Full I/O module sweep -- one L5X per real catalog number in the corpus
(2026-08-27, James: "you need to generate a l5x for every io module. I want
your table to be complete and valid with 100% filled out information.").

Every module block below is a REAL module chain (the target module PLUS its
real parent chain up to the CPU's own port, e.g. a Point I/O module's real
1734-AENTR/C adapter, or a remote module's real 1756-EN2T bridge) extracted
directly from samples/local/ (gitignored real corpus, never committed) via
scripts/extract_module_data.py's sibling analysis pass -- genericized
(Module Name -> TestModN_<Catalog>, Ethernet Address -> a placeholder
192.168.1.x, Description/Comments/ExtendedProperties stripped) but
structurally VERBATIM otherwise. Nothing here is invented -- every
Port/Connection/ConfigTag/ConfigData/ConfigScript shape is copied straight
from a real file that successfully compiled in Studio 5000.

86 catalogs covered -- every real, non-processor, non-legacy-platform
catalog number in the corpus with a single consistent real shape. NOT
covered, deliberately, not guessed:
  - 14 catalogs where the SAME catalog number showed 2+ DIFFERENT real
    shapes across the corpus (e.g. 2198-S086-ERS3 appears both as a plain
    2-Connection drive and a 4-Connection safety-variant drive) -- picking
    one arbitrarily would misrepresent the other real shape, needs its own
    look rather than a coin flip.
  - Legacy chassis/remote-I/O platforms (SLCChassis, RIOChassis,
    ControlNet, DPI port types -- 1746/1747/1771/1785-series, DH+/RIO
    scanners, PLC-5 bridges): architecturally different addressing schemes
    from a modern Logix5000 module, not a mechanical shape reuse.
  - Placeholder/generic profile labels (ETHERNET-MODULE, CIP-MODULE,
    ETHERNET-BRIDGE, ETHERNET-PANELVIEW, Generic-1756-Device,
    Generic-Ethernet-Device) -- not real catalog numbers, Logix Designer's
    own label for an unrecognized/generic device profile.
  - Motion (2198-series) and VFD (PowerFlex) shapes: see
    gen_module_motion.py / gen_module_vfd.py instead, built separately.

Run: python -m sample_gen.gen_module_sweep
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


# Catalog -> (real module chain XML, source file it was extracted from,
# how many modules in the chain -- 1 = standalone, 2-3 = target + real
# parent adapter/bridge chain).
_MODULE_CHAINS: dict[str, tuple[str, str, int]] = {
    '1732E-IB16M12DR/A': ("""\
<Module Name="TestMod1_1732EIB16M12DRA" CatalogNumber="1732E-IB16M12DR/A" Vendor="1" ProductType="7" ProductCode="355" Major="1" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigTag ConfigSize="10" ExternalAccess="Read/Write">
<Data Format="L5K">
[14,107,1,1000,1000,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1732_D16Diag:C:0">
<DataValueMember Name="FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt00_01OpenWireEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02_03OpenWireEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04_05OpenWireEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt06_07OpenWireEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt08_09OpenWireEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt10_11OpenWireEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt12_13OpenWireEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt14_15OpenWireEn" DataType="BOOL" Value="0" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="OutputData" RPI="20000" Type="Input" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1732_DI16Diag:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="Data" DataType="INT" Radix="Binary" Value="2#0000_1111_1101_1100" />
<DataValueMember Name="Pt00_01OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02_03OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04_05OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt06_07OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt08_09OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt10_11OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt12_13OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt14_15OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt00_01ShortCircuit" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02_03ShortCircuit" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04_05ShortCircuit" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt06_07ShortCircuit" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt08_09ShortCircuit" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt10_11ShortCircuit" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt12_13ShortCircuit" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt14_15ShortCircuit" DataType="BOOL" Value="0" />
</Structure>
</Data>
</InputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'DnR_Personal/Bender134053_201104.L5X', 1),
    '1732E-IB16M12R/A': ("""\
<Module Name="TestMod1_1732EIB16M12RA" CatalogNumber="1732E-IB16M12R/A" Vendor="1" ProductType="7" ProductCode="369" Major="1" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigTag ConfigSize="8" ExternalAccess="Read/Write">
<Data Format="L5K">
[12,101,1,1000,1000]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1732_DI16:C:0">
<DataValueMember Name="FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="InputData" RPI="20000" Type="Input" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1732_DI16:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="Data" DataType="INT" Radix="Binary" Value="2#0011_1111_0000_0000" />
</Structure>
</Data>
</InputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'DnR_Personal/TOYOTA_135453_20221024.L5X', 1),
    '1732E-OB16M12R/A': ("""\
<Module Name="TestMod1_1732EOB16M12RA" CatalogNumber="1732E-OB16M12R/A" Vendor="1" ProductType="7" ProductCode="370" Major="1" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigTag ConfigSize="5" ExternalAccess="Read/Write">
<Data Format="L5K">
[9,100,1,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1732_DO16:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="OutputData" RPI="20000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1732_D2:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1732_DO16:O:0">
<DataValueMember Name="Data" DataType="INT" Radix="Binary" Value="2#0000_0000_0000_0000" />
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'DnR_Personal/Bender134053_201104.L5X', 1),
    '1734-232ASC/C': ("""\
<Module Name="TestMod1_1734232ASCC" CatalogNumber="1734-AENT/C" Vendor="1" ProductType="12" ProductCode="108" Major="7" Minor="11" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="0" Type="PointIO" Upstream="false">
<Bus Size="2" />
</Port>
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications CommMethod="805306369">
<Connections>
<Connection Name="Output" RPI="20000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_2SLOT:I:0">
<DataValueMember Name="SlotStatusBits0_31" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111" />
<DataValueMember Name="SlotStatusBits32_63" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111" />
<ArrayMember Name="Data" DataType="SINT" Dimensions="2" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000" />
<Element Index="[1]" Value="2#0000_0000" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[-1,-1,[0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_2SLOT:O:0">
<ArrayMember Name="Data" DataType="SINT" Dimensions="2" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000" />
<Element Index="[1]" Value="2#0000_0000" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module Name="TestMod2_1734232ASCC" CatalogNumber="1734-232ASC/C" Vendor="1" ProductType="115" ProductCode="110" Major="4" Minor="4" ParentModule="TestMod1_1734232ASCC" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="1" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="536870913">
<ConfigTag ConfigSize="22" ExternalAccess="Read/Write">
<Data Format="L5K">
[26,103,1,3,0,80,0,58,2,13,1,1,0,0,1,80,0,13,1,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_232ASC:C:0">
<DataValueMember Name="SerialCharacterFormat" DataType="SINT" Radix="Decimal" Value="3" />
<DataValueMember Name="SerialCommSpeed" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaxReceiveCharacters" DataType="SINT" Radix="Decimal" Value="80" />
<DataValueMember Name="ReceiveStartDelimiterMode" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="ReceiveStartDelimiterCharacter" DataType="SINT" Radix="Decimal" Value="58" />
<DataValueMember Name="ReceiveRecordEndMode" DataType="SINT" Radix="Decimal" Value="2" />
<DataValueMember Name="ReceiveEndDelimiter" DataType="SINT" Radix="Decimal" Value="13" />
<DataValueMember Name="ReceiveStringDataType" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="PadMode" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="PadCharacter" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="ReceiveSwapMode" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="DeviceNetHandshakeMode" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="MaxTransmitCharacters" DataType="SINT" Radix="Decimal" Value="80" />
<DataValueMember Name="TransmitEndDelimiterMode" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="TransmitEndDelimiterCharacter" DataType="SINT" Radix="Decimal" Value="13" />
<DataValueMember Name="ConsumeStringDataType" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="TransmitSwapMode" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="DeviceNetRecordHeaderMode" DataType="SINT" Radix="Decimal" Value="0" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="OutputData" RPI="80000" Type="Output" InputCxnPoint="101" OutputCxnPoint="102" OutputSize="84" InputSize="88" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_232ASC_80Bytes:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="ReceiveRecordNumber" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Status" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Length" DataType="SINT" Radix="Decimal" Value="0" />
<ArrayMember Name="Data" DataType="SINT" Dimensions="80" Radix="Decimal">
<Element Index="[0]" Value="0" />
<Element Index="[1]" Value="0" />
<Element Index="[2]" Value="0" />
<Element Index="[3]" Value="0" />
<Element Index="[4]" Value="0" />
<Element Index="[5]" Value="0" />
<Element Index="[6]" Value="0" />
<Element Index="[7]" Value="0" />
<Element Index="[8]" Value="0" />
<Element Index="[9]" Value="0" />
<Element Index="[10]" Value="0" />
<Element Index="[11]" Value="0" />
<Element Index="[12]" Value="0" />
<Element Index="[13]" Value="0" />
<Element Index="[14]" Value="0" />
<Element Index="[15]" Value="0" />
<Element Index="[16]" Value="0" />
<Element Index="[17]" Value="0" />
<Element Index="[18]" Value="0" />
<Element Index="[19]" Value="0" />
<Element Index="[20]" Value="0" />
<Element Index="[21]" Value="0" />
<Element Index="[22]" Value="0" />
<Element Index="[23]" Value="0" />
<Element Index="[24]" Value="0" />
<Element Index="[25]" Value="0" />
<Element Index="[26]" Value="0" />
<Element Index="[27]" Value="0" />
<Element Index="[28]" Value="0" />
<Element Index="[29]" Value="0" />
<Element Index="[30]" Value="0" />
<Element Index="[31]" Value="0" />
<Element Index="[32]" Value="0" />
<Element Index="[33]" Value="0" />
<Element Index="[34]" Value="0" />
<Element Index="[35]" Value="0" />
<Element Index="[36]" Value="0" />
<Element Index="[37]" Value="0" />
<Element Index="[38]" Value="0" />
<Element Index="[39]" Value="0" />
<Element Index="[40]" Value="0" />
<Element Index="[41]" Value="0" />
<Element Index="[42]" Value="0" />
<Element Index="[43]" Value="0" />
<Element Index="[44]" Value="0" />
<Element Index="[45]" Value="0" />
<Element Index="[46]" Value="0" />
<Element Index="[47]" Value="0" />
<Element Index="[48]" Value="0" />
<Element Index="[49]" Value="0" />
<Element Index="[50]" Value="0" />
<Element Index="[51]" Value="0" />
<Element Index="[52]" Value="0" />
<Element Index="[53]" Value="0" />
<Element Index="[54]" Value="0" />
<Element Index="[55]" Value="0" />
<Element Index="[56]" Value="0" />
<Element Index="[57]" Value="0" />
<Element Index="[58]" Value="0" />
<Element Index="[59]" Value="0" />
<Element Index="[60]" Value="0" />
<Element Index="[61]" Value="0" />
<Element Index="[62]" Value="0" />
<Element Index="[63]" Value="0" />
<Element Index="[64]" Value="0" />
<Element Index="[65]" Value="0" />
<Element Index="[66]" Value="0" />
<Element Index="[67]" Value="0" />
<Element Index="[68]" Value="0" />
<Element Index="[69]" Value="0" />
<Element Index="[70]" Value="0" />
<Element Index="[71]" Value="0" />
<Element Index="[72]" Value="0" />
<Element Index="[73]" Value="0" />
<Element Index="[74]" Value="0" />
<Element Index="[75]" Value="0" />
<Element Index="[76]" Value="0" />
<Element Index="[77]" Value="0" />
<Element Index="[78]" Value="0" />
<Element Index="[79]" Value="0" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[0,-19,0,41,[0,1,0,3,-62,-8,-49,-112,28,69,77,83,71,58,32,80,76,65,78,78,69,82,32,84,82,70,32,32,78,79,84,32,82,85,78,78,73
		,78,71,4,97,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_232ASC_80Bytes:O:0">
<DataValueMember Name="NextTransmitRecordNumber" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="TransmitRecordNumber" DataType="SINT" Radix="Decimal" Value="-19" />
<DataValueMember Name="Length" DataType="SINT" Radix="Decimal" Value="41" />
<ArrayMember Name="Data" DataType="SINT" Dimensions="80" Radix="Decimal">
<Element Index="[0]" Value="0" />
<Element Index="[1]" Value="1" />
<Element Index="[2]" Value="0" />
<Element Index="[3]" Value="3" />
<Element Index="[4]" Value="-62" />
<Element Index="[5]" Value="-8" />
<Element Index="[6]" Value="-49" />
<Element Index="[7]" Value="-112" />
<Element Index="[8]" Value="28" />
<Element Index="[9]" Value="69" />
<Element Index="[10]" Value="77" />
<Element Index="[11]" Value="83" />
<Element Index="[12]" Value="71" />
<Element Index="[13]" Value="58" />
<Element Index="[14]" Value="32" />
<Element Index="[15]" Value="80" />
<Element Index="[16]" Value="76" />
<Element Index="[17]" Value="65" />
<Element Index="[18]" Value="78" />
<Element Index="[19]" Value="78" />
<Element Index="[20]" Value="69" />
<Element Index="[21]" Value="82" />
<Element Index="[22]" Value="32" />
<Element Index="[23]" Value="84" />
<Element Index="[24]" Value="82" />
<Element Index="[25]" Value="70" />
<Element Index="[26]" Value="32" />
<Element Index="[27]" Value="32" />
<Element Index="[28]" Value="78" />
<Element Index="[29]" Value="79" />
<Element Index="[30]" Value="84" />
<Element Index="[31]" Value="32" />
<Element Index="[32]" Value="82" />
<Element Index="[33]" Value="85" />
<Element Index="[34]" Value="78" />
<Element Index="[35]" Value="78" />
<Element Index="[36]" Value="73" />
<Element Index="[37]" Value="78" />
<Element Index="[38]" Value="71" />
<Element Index="[39]" Value="4" />
<Element Index="[40]" Value="97" />
<Element Index="[41]" Value="0" />
<Element Index="[42]" Value="0" />
<Element Index="[43]" Value="0" />
<Element Index="[44]" Value="0" />
<Element Index="[45]" Value="0" />
<Element Index="[46]" Value="0" />
<Element Index="[47]" Value="0" />
<Element Index="[48]" Value="0" />
<Element Index="[49]" Value="0" />
<Element Index="[50]" Value="0" />
<Element Index="[51]" Value="0" />
<Element Index="[52]" Value="0" />
<Element Index="[53]" Value="0" />
<Element Index="[54]" Value="0" />
<Element Index="[55]" Value="0" />
<Element Index="[56]" Value="0" />
<Element Index="[57]" Value="0" />
<Element Index="[58]" Value="0" />
<Element Index="[59]" Value="0" />
<Element Index="[60]" Value="0" />
<Element Index="[61]" Value="0" />
<Element Index="[62]" Value="0" />
<Element Index="[63]" Value="0" />
<Element Index="[64]" Value="0" />
<Element Index="[65]" Value="0" />
<Element Index="[66]" Value="0" />
<Element Index="[67]" Value="0" />
<Element Index="[68]" Value="0" />
<Element Index="[69]" Value="0" />
<Element Index="[70]" Value="0" />
<Element Index="[71]" Value="0" />
<Element Index="[72]" Value="0" />
<Element Index="[73]" Value="0" />
<Element Index="[74]" Value="0" />
<Element Index="[75]" Value="0" />
<Element Index="[76]" Value="0" />
<Element Index="[77]" Value="0" />
<Element Index="[78]" Value="0" />
<Element Index="[79]" Value="0" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'BAI10048_TrimmerTally_20250704.L5X', 2),
    '1734-485ASC/C': ("""\
<Module Name="TestMod1_1734485ASCC" CatalogNumber="1734-AENT/B" Vendor="1" ProductType="12" ProductCode="108" Major="5" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="Disabled" />
<Ports>
<Port Id="1" Address="0" Type="PointIO" Upstream="false">
<Bus Size="7" />
</Port>
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications CommMethod="805306369">
<Connections>
<Connection Name="Output" RPI="2000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_7SLOT:I:0">
<DataValueMember Name="SlotStatusBits0_31" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1011_1001" />
<DataValueMember Name="SlotStatusBits32_63" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111" />
<ArrayMember Name="Data" DataType="SINT" Dimensions="7" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000" />
<Element Index="[1]" Value="2#1010_0001" />
<Element Index="[2]" Value="2#0010_0010" />
<Element Index="[3]" Value="2#0000_0000" />
<Element Index="[4]" Value="2#0000_0000" />
<Element Index="[5]" Value="2#0000_0000" />
<Element Index="[6]" Value="2#0000_0000" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[-71,-1,[0,0,0,0,0,0,16]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_7SLOT:O:0">
<ArrayMember Name="Data" DataType="SINT" Dimensions="7" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000" />
<Element Index="[1]" Value="2#0000_0000" />
<Element Index="[2]" Value="2#0000_0000" />
<Element Index="[3]" Value="2#0000_0000" />
<Element Index="[4]" Value="2#0000_0000" />
<Element Index="[5]" Value="2#0000_0000" />
<Element Index="[6]" Value="2#0001_0000" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module Name="TestMod2_1734485ASCC" CatalogNumber="1734-485ASC/C" Vendor="1" ProductType="115" ProductCode="133" Major="4" Minor="1" ParentModule="TestMod1_1734485ASCC" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="4" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="536870913">
<ConfigTag ConfigSize="22" ExternalAccess="Read/Write">
<Data Format="L5K">
[26,103,1,3,4,40,1,10,1,13,1,0,0,0,1,40,1,13,1,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_485ASC:C:0">
<DataValueMember Name="SerialCharacterFormat" DataType="SINT" Radix="Decimal" Value="3" />
<DataValueMember Name="SerialCommSpeed" DataType="SINT" Radix="Decimal" Value="4" />
<DataValueMember Name="MaxReceiveCharacters" DataType="SINT" Radix="Decimal" Value="40" />
<DataValueMember Name="ReceiveStartDelimiterMode" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="ReceiveStartDelimiterCharacter" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="ReceiveRecordEndMode" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="ReceiveEndDelimiter" DataType="SINT" Radix="Decimal" Value="13" />
<DataValueMember Name="ReceiveStringDataType" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="PadMode" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="PadCharacter" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="ReceiveSwapMode" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="DeviceNetHandshakeMode" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="MaxTransmitCharacters" DataType="SINT" Radix="Decimal" Value="40" />
<DataValueMember Name="TransmitEndDelimiterMode" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="TransmitEndDelimiterCharacter" DataType="SINT" Radix="Decimal" Value="13" />
<DataValueMember Name="ConsumeStringDataType" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="TransmitSwapMode" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="DeviceNetRecordHeaderMode" DataType="SINT" Radix="Decimal" Value="0" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="Output" RPI="2000" Type="Output" InputCxnPoint="101" OutputCxnPoint="102" OutputSize="44" InputSize="48" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_485ASC_40Bytes:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="ReceiveRecordNumber" DataType="SINT" Radix="Decimal" Value="83" />
<DataValueMember Name="Status" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Length" DataType="SINT" Radix="Decimal" Value="9" />
<ArrayMember Name="Data" DataType="SINT" Dimensions="40" Radix="Decimal">
<Element Index="[0]" Value="68" />
<Element Index="[1]" Value="48" />
<Element Index="[2]" Value="48" />
<Element Index="[3]" Value="48" />
<Element Index="[4]" Value="48" />
<Element Index="[5]" Value="48" />
<Element Index="[6]" Value="48" />
<Element Index="[7]" Value="48" />
<Element Index="[8]" Value="48" />
<Element Index="[9]" Value="0" />
<Element Index="[10]" Value="0" />
<Element Index="[11]" Value="0" />
<Element Index="[12]" Value="0" />
<Element Index="[13]" Value="0" />
<Element Index="[14]" Value="0" />
<Element Index="[15]" Value="0" />
<Element Index="[16]" Value="0" />
<Element Index="[17]" Value="0" />
<Element Index="[18]" Value="0" />
<Element Index="[19]" Value="0" />
<Element Index="[20]" Value="0" />
<Element Index="[21]" Value="0" />
<Element Index="[22]" Value="0" />
<Element Index="[23]" Value="0" />
<Element Index="[24]" Value="0" />
<Element Index="[25]" Value="0" />
<Element Index="[26]" Value="0" />
<Element Index="[27]" Value="0" />
<Element Index="[28]" Value="0" />
<Element Index="[29]" Value="0" />
<Element Index="[30]" Value="0" />
<Element Index="[31]" Value="0" />
<Element Index="[32]" Value="0" />
<Element Index="[33]" Value="0" />
<Element Index="[34]" Value="0" />
<Element Index="[35]" Value="0" />
<Element Index="[36]" Value="0" />
<Element Index="[37]" Value="0" />
<Element Index="[38]" Value="0" />
<Element Index="[39]" Value="0" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[0,45,0,3,[10,68,13,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_485ASC_40Bytes:O:0">
<DataValueMember Name="NextTransmitRecordNumber" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="TransmitRecordNumber" DataType="SINT" Radix="Decimal" Value="45" />
<DataValueMember Name="Length" DataType="SINT" Radix="Decimal" Value="3" />
<ArrayMember Name="Data" DataType="SINT" Dimensions="40" Radix="Decimal">
<Element Index="[0]" Value="10" />
<Element Index="[1]" Value="68" />
<Element Index="[2]" Value="13" />
<Element Index="[3]" Value="0" />
<Element Index="[4]" Value="0" />
<Element Index="[5]" Value="0" />
<Element Index="[6]" Value="0" />
<Element Index="[7]" Value="0" />
<Element Index="[8]" Value="0" />
<Element Index="[9]" Value="0" />
<Element Index="[10]" Value="0" />
<Element Index="[11]" Value="0" />
<Element Index="[12]" Value="0" />
<Element Index="[13]" Value="0" />
<Element Index="[14]" Value="0" />
<Element Index="[15]" Value="0" />
<Element Index="[16]" Value="0" />
<Element Index="[17]" Value="0" />
<Element Index="[18]" Value="0" />
<Element Index="[19]" Value="0" />
<Element Index="[20]" Value="0" />
<Element Index="[21]" Value="0" />
<Element Index="[22]" Value="0" />
<Element Index="[23]" Value="0" />
<Element Index="[24]" Value="0" />
<Element Index="[25]" Value="0" />
<Element Index="[26]" Value="0" />
<Element Index="[27]" Value="0" />
<Element Index="[28]" Value="0" />
<Element Index="[29]" Value="0" />
<Element Index="[30]" Value="0" />
<Element Index="[31]" Value="0" />
<Element Index="[32]" Value="0" />
<Element Index="[33]" Value="0" />
<Element Index="[34]" Value="0" />
<Element Index="[35]" Value="0" />
<Element Index="[36]" Value="0" />
<Element Index="[37]" Value="0" />
<Element Index="[38]" Value="0" />
<Element Index="[39]" Value="0" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'L5X_Samples/CMU_2025_10_14r00.L5X', 2),
    '1734-8CFG/C': ("""\
<Module Name="TestMod1_17348CFGC" CatalogNumber="1734-AENT/B" Vendor="1" ProductType="12" ProductCode="108" Major="4" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="0" Type="PointIO" Upstream="false">
<Bus Size="3" />
</Port>
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications CommMethod="805306369">
<Connections>
<Connection Name="Output" RPI="20000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_3SLOT:I:0">
<DataValueMember Name="SlotStatusBits0_31" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1011" />
<DataValueMember Name="SlotStatusBits32_63" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111" />
<ArrayMember Name="Data" DataType="SINT" Dimensions="3" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000" />
<Element Index="[1]" Value="2#0000_0000" />
<Element Index="[2]" Value="2#0000_1000" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[-5,-1,[0,0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_3SLOT:O:0">
<ArrayMember Name="Data" DataType="SINT" Dimensions="3" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000" />
<Element Index="[1]" Value="2#0000_0000" />
<Element Index="[2]" Value="2#0000_0000" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module CatalogNumber="1734-8CFG/C" Vendor="1" ProductType="7" ProductCode="371" Major="3" Minor="7" ParentModule="TestMod1_17348CFGC" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="2" Type="PointIO" Upstream="true" />
</Ports>
<Communications>
<ConfigTag ConfigSize="12" ExternalAccess="Read/Write">
<Data Format="L5K">
[16,103,1,1000,1000,0,0,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_8CFG:C:0">
<DataValueMember Name="FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="FaultMode" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="FaultValue" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="ProgMode" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="ProgValue" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<RackConnection>
<InAliasTag>
</InAliasTag>
<OutAliasTag>
</OutAliasTag>
</RackConnection>
</Connections>
</Communications>
</Module>
""", 'L5X_Samples/Sorter1_20260722r00.L5X', 2),
    '1734-AENT/B': ("""\
<Module Name="TestMod1_1734AENTB" CatalogNumber="1734-AENT/B" Vendor="1" ProductType="12" ProductCode="108" Major="4" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="0" Type="PointIO" Upstream="false">
<Bus Size="8" />
</Port>
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications CommMethod="805306369">
<Connections>
<Connection Name="Output" RPI="20000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_8SLOT:I:0">
<DataValueMember Name="SlotStatusBits0_31" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_0000_0001" />
<DataValueMember Name="SlotStatusBits32_63" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111" />
<ArrayMember Name="Data" DataType="SINT" Dimensions="8" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000" />
<Element Index="[1]" Value="2#1110_0001" />
<Element Index="[2]" Value="2#1111_1111" />
<Element Index="[3]" Value="2#1011_1111" />
<Element Index="[4]" Value="2#1111_1101" />
<Element Index="[5]" Value="2#0011_1111" />
<Element Index="[6]" Value="2#0000_0000" />
<Element Index="[7]" Value="2#0000_0000" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[-255,-1,[0,0,0,0,0,0,0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_8SLOT:O:0">
<ArrayMember Name="Data" DataType="SINT" Dimensions="8" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000" />
<Element Index="[1]" Value="2#0000_0000" />
<Element Index="[2]" Value="2#0000_0000" />
<Element Index="[3]" Value="2#0000_0000" />
<Element Index="[4]" Value="2#0000_0000" />
<Element Index="[5]" Value="2#0000_0000" />
<Element Index="[6]" Value="2#0000_0000" />
<Element Index="[7]" Value="2#0000_0000" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'BAI10048_TrimmerTally_20250704.L5X', 1),
    '1734-AENT/C': ("""\
<Module Name="TestMod1_1734AENTC" CatalogNumber="1734-AENT/C" Vendor="1" ProductType="12" ProductCode="108" Major="7" Minor="11" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="0" Type="PointIO" Upstream="false">
<Bus Size="2" />
</Port>
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications CommMethod="805306369">
<Connections>
<Connection Name="Output" RPI="20000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_2SLOT:I:0">
<DataValueMember Name="SlotStatusBits0_31" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111" />
<DataValueMember Name="SlotStatusBits32_63" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111" />
<ArrayMember Name="Data" DataType="SINT" Dimensions="2" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000" />
<Element Index="[1]" Value="2#0000_0000" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[-1,-1,[0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_2SLOT:O:0">
<ArrayMember Name="Data" DataType="SINT" Dimensions="2" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000" />
<Element Index="[1]" Value="2#0000_0000" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'BAI10048_TrimmerTally_20250704.L5X', 1),
    '1734-AENTR/B': ("""\
<Module Name="TestMod1_1734AENTRB" CatalogNumber="1734-AENTR/B" Vendor="1" ProductType="12" ProductCode="196" Major="4" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="0" Type="PointIO" Upstream="false">
<Bus Size="1" />
</Port>
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications CommMethod="805306369">
<Connections>
<Connection Name="Output" RPI="20000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_1SLOT:I:0">
<DataValueMember Name="SlotStatusBits0_31" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="SlotStatusBits32_63" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<ArrayMember Name="Data" DataType="SINT" Dimensions="1" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[0,0,[0]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_1SLOT:O:0">
<ArrayMember Name="Data" DataType="SINT" Dimensions="1" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'SJ_Gormley_20251112_r02.L5X', 1),
    '1734-AENTR/C': ("""\
<Module Name="TestMod1_1734AENTRC" CatalogNumber="1734-AENTR/C" Vendor="1" ProductType="12" ProductCode="196" Major="7" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="0" Type="PointIO" Upstream="false">
<Bus Size="1" />
</Port>
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications CommMethod="805306369">
<Connections>
<Connection Name="Output" RPI="20000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_1SLOT:I:0">
<DataValueMember Name="SlotStatusBits0_31" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="SlotStatusBits32_63" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<ArrayMember Name="Data" DataType="SINT" Dimensions="1" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[0,0,[0]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_1SLOT:O:0">
<ArrayMember Name="Data" DataType="SINT" Dimensions="1" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'SJ_Gormley_20251112_r02.L5X', 1),
    '1734-IB8/C': ("""\
<Module Name="TestMod1_1734IB8C" CatalogNumber="1734-AENTR/C" Vendor="1" ProductType="12" ProductCode="196" Major="7" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="0" Type="PointIO" Upstream="false">
<Bus Size="12" />
</Port>
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications CommMethod="805306369">
<Connections>
<Connection Name="Output" RPI="20000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_12SLOT:I:0">
<DataValueMember Name="SlotStatusBits0_31" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="SlotStatusBits32_63" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<ArrayMember Name="Data" DataType="SINT" Dimensions="12" Radix="Binary">
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
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[0,0,[0,0,0,0,0,0,0,0,0,0,0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_12SLOT:O:0">
<ArrayMember Name="Data" DataType="SINT" Dimensions="12" Radix="Binary">
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
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module CatalogNumber="1734-IB8/C" Vendor="1" ProductType="7" ProductCode="216" Major="3" Minor="1" ParentModule="TestMod1_1734IB8C" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="1" Type="PointIO" Upstream="true" />
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
""", 'SJ_Gormley_20251112_r02.L5X', 2),
    '1734-IE2C/C': ("""\
<Module Name="TestMod1_1734IE2CC" CatalogNumber="1734-AENTR/C" Vendor="1" ProductType="12" ProductCode="196" Major="6" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="0" Type="PointIO" Upstream="false">
<Bus Size="14" />
</Port>
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications CommMethod="805306369">
<Connections>
<Connection Name="Output" RPI="5000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_14SLOT:I:0">
<DataValueMember Name="SlotStatusBits0_31" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_0000_0001_1111" />
<DataValueMember Name="SlotStatusBits32_63" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111" />
<ArrayMember Name="Data" DataType="SINT" Dimensions="14" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000" />
<Element Index="[1]" Value="2#0000_0000" />
<Element Index="[2]" Value="2#0000_0000" />
<Element Index="[3]" Value="2#0000_0000" />
<Element Index="[4]" Value="2#0000_0000" />
<Element Index="[5]" Value="2#1010_1111" />
<Element Index="[6]" Value="2#0000_0001" />
<Element Index="[7]" Value="2#1100_0000" />
<Element Index="[8]" Value="2#0000_0000" />
<Element Index="[9]" Value="2#0000_0000" />
<Element Index="[10]" Value="2#0000_0000" />
<Element Index="[11]" Value="2#0000_0011" />
<Element Index="[12]" Value="2#0000_0000" />
<Element Index="[13]" Value="2#0000_0000" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[-4065,-1,[0,0,0,0,0,0,0,0,0,8,6,0,0,0]]
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
<Element Index="[9]" Value="2#0000_1000" />
<Element Index="[10]" Value="2#0000_0110" />
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

<Module Name="TestMod2_1734IE2CC" CatalogNumber="1734-IE2C/C" Vendor="1" ProductType="115" ProductCode="24" Major="3" Minor="1" ParentModule="TestMod1_1734IE2CC" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="4" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="536870913">
<ConfigTag ConfigSize="42" ExternalAccess="Read/Write">
<Data Format="L5K">
[46,123,1,0,32767,0,3113,16547,2867,16793,3,0,1,0,0,16383,0,3113,16547,2867,16793,3,0,1,2,10]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_IE2:C:0">
<DataValueMember Name="Ch0LowEngineering" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch0HighEngineering" DataType="INT" Radix="Decimal" Value="32767" />
<DataValueMember Name="Ch0DigitalFilter" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch0LAlarmLimit" DataType="INT" Radix="Decimal" Value="3113" />
<DataValueMember Name="Ch0HAlarmLimit" DataType="INT" Radix="Decimal" Value="16547" />
<DataValueMember Name="Ch0LLAlarmLimit" DataType="INT" Radix="Decimal" Value="2867" />
<DataValueMember Name="Ch0HHAlarmLimit" DataType="INT" Radix="Decimal" Value="16793" />
<DataValueMember Name="Ch0RangeType" DataType="SINT" Radix="Decimal" Value="3" />
<DataValueMember Name="Ch0LimitAlarmLatch" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch0AlarmDisable" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="Ch1LowEngineering" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1HighEngineering" DataType="INT" Radix="Decimal" Value="16383" />
<DataValueMember Name="Ch1DigitalFilter" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1LAlarmLimit" DataType="INT" Radix="Decimal" Value="3113" />
<DataValueMember Name="Ch1HAlarmLimit" DataType="INT" Radix="Decimal" Value="16547" />
<DataValueMember Name="Ch1LLAlarmLimit" DataType="INT" Radix="Decimal" Value="2867" />
<DataValueMember Name="Ch1HHAlarmLimit" DataType="INT" Radix="Decimal" Value="16793" />
<DataValueMember Name="Ch1RangeType" DataType="SINT" Radix="Decimal" Value="3" />
<DataValueMember Name="Ch1LimitAlarmLatch" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1AlarmDisable" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="NotchFilter" DataType="SINT" Radix="Decimal" Value="2" />
<DataValueMember Name="RealTimeSample" DataType="INT" Radix="Decimal" Value="10" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="InputData" RPI="5000" Type="Input" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_IE2:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="Ch0Data" DataType="INT" Radix="Decimal" Value="32767" />
<DataValueMember Name="Ch1Data" DataType="INT" Radix="Decimal" Value="-4072" />
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
""", 'DnR_Personal/Bender134053_201104.L5X', 2),
    '1734-IE2V/C': ("""\
<Module Name="TestMod1_1734IE2VC" CatalogNumber="1734-AENT/C" Vendor="1" ProductType="12" ProductCode="108" Major="6" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="0" Type="PointIO" Upstream="false">
<Bus Size="6" />
</Port>
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications CommMethod="805306369">
<Connections>
<Connection Name="Output" RPI="20000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_6SLOT:I:0">
<DataValueMember Name="SlotStatusBits0_31" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_0001" />
<DataValueMember Name="SlotStatusBits32_63" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111" />
<ArrayMember Name="Data" DataType="SINT" Dimensions="6" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000" />
<Element Index="[1]" Value="2#0000_0000" />
<Element Index="[2]" Value="2#0001_0000" />
<Element Index="[3]" Value="2#0000_0000" />
<Element Index="[4]" Value="2#0000_0000" />
<Element Index="[5]" Value="2#0000_0000" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[-15,-1,[0,0,0,0,0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_6SLOT:O:0">
<ArrayMember Name="Data" DataType="SINT" Dimensions="6" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000" />
<Element Index="[1]" Value="2#0000_0000" />
<Element Index="[2]" Value="2#0000_0000" />
<Element Index="[3]" Value="2#0000_0000" />
<Element Index="[4]" Value="2#0000_0000" />
<Element Index="[5]" Value="2#0000_0000" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module CatalogNumber="1734-IE2V/C" Vendor="1" ProductType="115" ProductCode="55" Major="3" Minor="1" ParentModule="TestMod1_1734IE2VC" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="5" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="536870913">
<ConfigTag ConfigSize="42" ExternalAccess="Read/Write">
<Data Format="L5K">
[46,123,1,0,10000,0,500,9500,200,9800,2,0,0,0,0,10000,0,500,9500,200,9800,2,0,0,2,100]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_IE2:C:0">
<DataValueMember Name="Ch0LowEngineering" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch0HighEngineering" DataType="INT" Radix="Decimal" Value="10000" />
<DataValueMember Name="Ch0DigitalFilter" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch0LAlarmLimit" DataType="INT" Radix="Decimal" Value="500" />
<DataValueMember Name="Ch0HAlarmLimit" DataType="INT" Radix="Decimal" Value="9500" />
<DataValueMember Name="Ch0LLAlarmLimit" DataType="INT" Radix="Decimal" Value="200" />
<DataValueMember Name="Ch0HHAlarmLimit" DataType="INT" Radix="Decimal" Value="9800" />
<DataValueMember Name="Ch0RangeType" DataType="SINT" Radix="Decimal" Value="2" />
<DataValueMember Name="Ch0LimitAlarmLatch" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch0AlarmDisable" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1LowEngineering" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1HighEngineering" DataType="INT" Radix="Decimal" Value="10000" />
<DataValueMember Name="Ch1DigitalFilter" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1LAlarmLimit" DataType="INT" Radix="Decimal" Value="500" />
<DataValueMember Name="Ch1HAlarmLimit" DataType="INT" Radix="Decimal" Value="9500" />
<DataValueMember Name="Ch1LLAlarmLimit" DataType="INT" Radix="Decimal" Value="200" />
<DataValueMember Name="Ch1HHAlarmLimit" DataType="INT" Radix="Decimal" Value="9800" />
<DataValueMember Name="Ch1RangeType" DataType="SINT" Radix="Decimal" Value="2" />
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
<DataValueMember Name="Ch0Data" DataType="INT" Radix="Decimal" Value="10004" />
<DataValueMember Name="Ch1Data" DataType="INT" Radix="Decimal" Value="10577" />
<DataValueMember Name="Ch0Status" DataType="SINT" Radix="Binary" Value="2#0010_1001" />
<DataValueMember Name="Ch0Fault" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch0Calibration" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0LAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0HAlarm" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch0LLAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0HHAlarm" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch0Underrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0Overrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1Status" DataType="SINT" Radix="Binary" Value="2#1010_1001" />
<DataValueMember Name="Ch1Fault" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch1Calibration" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1LAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1HAlarm" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch1LLAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1HHAlarm" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch1Underrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1Overrange" DataType="BOOL" Value="1" />
</Structure>
</Data>
</InputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'L5X_Samples/Sorter1_20260722r00.L5X', 2),
    '1734-IE4C/C': ("""\
<Module Name="TestMod1_1734IE4CC" CatalogNumber="1734-AENTR/B" Vendor="1" ProductType="12" ProductCode="196" Major="4" Minor="3" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="0" Type="PointIO" Upstream="false">
<Bus Size="12" />
</Port>
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications CommMethod="805306369">
<Connections>
<Connection Name="Output" RPI="20000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_12SLOT:I:0">
<DataValueMember Name="SlotStatusBits0_31" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1000_0100_0001" />
<DataValueMember Name="SlotStatusBits32_63" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111" />
<ArrayMember Name="Data" DataType="SINT" Dimensions="12" Radix="Binary">
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
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[-1983,-1,[0,0,0,0,0,0,0,0,49,0,0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_12SLOT:O:0">
<ArrayMember Name="Data" DataType="SINT" Dimensions="12" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000" />
<Element Index="[1]" Value="2#0000_0000" />
<Element Index="[2]" Value="2#0000_0000" />
<Element Index="[3]" Value="2#0000_0000" />
<Element Index="[4]" Value="2#0000_0000" />
<Element Index="[5]" Value="2#0000_0000" />
<Element Index="[6]" Value="2#0000_0000" />
<Element Index="[7]" Value="2#0000_0000" />
<Element Index="[8]" Value="2#0011_0001" />
<Element Index="[9]" Value="2#0000_0000" />
<Element Index="[10]" Value="2#0000_0000" />
<Element Index="[11]" Value="2#0000_0000" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module Name="TestMod2_1734IE4CC" CatalogNumber="1734-IE4C/C" Vendor="1" ProductType="115" ProductCode="209" Major="3" Minor="1" ParentModule="TestMod1_1734IE4CC" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="11" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="536870913">
<ConfigTag ConfigSize="78" ExternalAccess="Read/Write">
<Data Format="L5K">
[82,123,1,3277,16383,0,3113,16547,2867,16793,3,0,1,0,3277,16383,0,3113,16547,2867,16793,3,0,1,0,3277,16383,0,3113
		,16547,2867,16793,3,0,1,0,3277,16383,0,3113,16547,2867,16793,3,0,1,0,67]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_IE4:C:0">
<DataValueMember Name="Ch0LowEngineering" DataType="INT" Radix="Decimal" Value="3277" />
<DataValueMember Name="Ch0HighEngineering" DataType="INT" Radix="Decimal" Value="16383" />
<DataValueMember Name="Ch0DigitalFilter" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch0LAlarmLimit" DataType="INT" Radix="Decimal" Value="3113" />
<DataValueMember Name="Ch0HAlarmLimit" DataType="INT" Radix="Decimal" Value="16547" />
<DataValueMember Name="Ch0LLAlarmLimit" DataType="INT" Radix="Decimal" Value="2867" />
<DataValueMember Name="Ch0HHAlarmLimit" DataType="INT" Radix="Decimal" Value="16793" />
<DataValueMember Name="Ch0RangeType" DataType="SINT" Radix="Decimal" Value="3" />
<DataValueMember Name="Ch0LimitAlarmLatch" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch0AlarmDisable" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="Ch1LowEngineering" DataType="INT" Radix="Decimal" Value="3277" />
<DataValueMember Name="Ch1HighEngineering" DataType="INT" Radix="Decimal" Value="16383" />
<DataValueMember Name="Ch1DigitalFilter" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1LAlarmLimit" DataType="INT" Radix="Decimal" Value="3113" />
<DataValueMember Name="Ch1HAlarmLimit" DataType="INT" Radix="Decimal" Value="16547" />
<DataValueMember Name="Ch1LLAlarmLimit" DataType="INT" Radix="Decimal" Value="2867" />
<DataValueMember Name="Ch1HHAlarmLimit" DataType="INT" Radix="Decimal" Value="16793" />
<DataValueMember Name="Ch1RangeType" DataType="SINT" Radix="Decimal" Value="3" />
<DataValueMember Name="Ch1LimitAlarmLatch" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1AlarmDisable" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="Ch2LowEngineering" DataType="INT" Radix="Decimal" Value="3277" />
<DataValueMember Name="Ch2HighEngineering" DataType="INT" Radix="Decimal" Value="16383" />
<DataValueMember Name="Ch2DigitalFilter" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch2LAlarmLimit" DataType="INT" Radix="Decimal" Value="3113" />
<DataValueMember Name="Ch2HAlarmLimit" DataType="INT" Radix="Decimal" Value="16547" />
<DataValueMember Name="Ch2LLAlarmLimit" DataType="INT" Radix="Decimal" Value="2867" />
<DataValueMember Name="Ch2HHAlarmLimit" DataType="INT" Radix="Decimal" Value="16793" />
<DataValueMember Name="Ch2RangeType" DataType="SINT" Radix="Decimal" Value="3" />
<DataValueMember Name="Ch2LimitAlarmLatch" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch2AlarmDisable" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="Ch3LowEngineering" DataType="INT" Radix="Decimal" Value="3277" />
<DataValueMember Name="Ch3HighEngineering" DataType="INT" Radix="Decimal" Value="16383" />
<DataValueMember Name="Ch3DigitalFilter" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch3LAlarmLimit" DataType="INT" Radix="Decimal" Value="3113" />
<DataValueMember Name="Ch3HAlarmLimit" DataType="INT" Radix="Decimal" Value="16547" />
<DataValueMember Name="Ch3LLAlarmLimit" DataType="INT" Radix="Decimal" Value="2867" />
<DataValueMember Name="Ch3HHAlarmLimit" DataType="INT" Radix="Decimal" Value="16793" />
<DataValueMember Name="Ch3RangeType" DataType="SINT" Radix="Decimal" Value="3" />
<DataValueMember Name="Ch3LimitAlarmLatch" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch3AlarmDisable" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="NotchFilter" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="RealTimeSample" DataType="INT" Radix="Decimal" Value="67" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="InputData" RPI="4000" Type="Input" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_IE4:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="Ch0Data" DataType="INT" Radix="Decimal" Value="-5" />
<DataValueMember Name="Ch1Data" DataType="INT" Radix="Decimal" Value="-6" />
<DataValueMember Name="Ch2Data" DataType="INT" Radix="Decimal" Value="-6" />
<DataValueMember Name="Ch3Data" DataType="INT" Radix="Decimal" Value="-3" />
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
<DataValueMember Name="Ch2Status" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Ch2Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch2Calibration" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch2LAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch2HAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch2LLAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch2HHAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch2Underrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch2Overrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch3Status" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Ch3Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch3Calibration" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch3LAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch3HAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch3LLAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch3HHAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch3Underrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch3Overrange" DataType="BOOL" Value="0" />
</Structure>
</Data>
</InputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'L5X_Samples/Sorter1_20260722r00.L5X', 2),
    '1734-IJ/C': ("""\
<Module Name="TestMod1_1734IJC" CatalogNumber="1734-AENTR/C" Vendor="1" ProductType="12" ProductCode="196" Major="7" Minor="1" ParentModule="Local" ParentModPortId="4" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="0" Type="PointIO" Upstream="false">
<Bus Size="14" />
</Port>
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
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

<Module Name="TestMod2_1734IJC" CatalogNumber="1734-IJ/C" Vendor="1" ProductType="109" ProductCode="15" Major="3" Minor="1" ParentModule="TestMod1_1734IJC" ParentModPortId="1" Inhibited="false" MajorFault="false">
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
""", 'DnR_Personal/FlareFunction_311D_240731.L5X', 2),
    '1734-IK/C': ("""\
<Module Name="TestMod1_1734IKC" CatalogNumber="1734-AENTR/B" Vendor="1" ProductType="12" ProductCode="196" Major="4" Minor="3" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="0" Type="PointIO" Upstream="false">
<Bus Size="13" />
</Port>
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications CommMethod="805306369">
<Connections>
<Connection Name="Output" RPI="10000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_13SLOT:I:0">
<DataValueMember Name="SlotStatusBits0_31" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1110_0000_0111_1111" />
<DataValueMember Name="SlotStatusBits32_63" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111" />
<ArrayMember Name="Data" DataType="SINT" Dimensions="13" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000" />
<Element Index="[1]" Value="2#0000_0000" />
<Element Index="[2]" Value="2#0000_0000" />
<Element Index="[3]" Value="2#0000_0000" />
<Element Index="[4]" Value="2#0000_0000" />
<Element Index="[5]" Value="2#0000_0000" />
<Element Index="[6]" Value="2#0000_0000" />
<Element Index="[7]" Value="2#1111_1100" />
<Element Index="[8]" Value="2#0011_1111" />
<Element Index="[9]" Value="2#0000_0100" />
<Element Index="[10]" Value="2#0000_0000" />
<Element Index="[11]" Value="2#1000_0000" />
<Element Index="[12]" Value="2#1111_1111" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[-8065,-1,[0,0,0,0,0,0,0,0,0,0,0,0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_13SLOT:O:0">
<ArrayMember Name="Data" DataType="SINT" Dimensions="13" Radix="Binary">
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
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module CatalogNumber="1734-IK/C" Vendor="1" ProductType="109" ProductCode="16" Major="3" Minor="4" ParentModule="TestMod1_1734IKC" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="1" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="536870913">
<ConfigTag ConfigSize="22" ExternalAccess="Read/Write">
<Data Format="L5K">
[26,123,0,-60,1,1,0,0,0,0,16777215,0,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_IJK:C:0">
<DataValueMember Name="CounterConfig" DataType="SINT" Radix="Binary" Value="2#1100_0100" />
<DataValueMember Name="Config_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Config_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Config_2" DataType="BOOL" Value="1" />
<DataValueMember Name="Config_3" DataType="BOOL" Value="0" />
<DataValueMember Name="Mode_4" DataType="BOOL" Value="0" />
<DataValueMember Name="Mode_5" DataType="BOOL" Value="0" />
<DataValueMember Name="Mode_6" DataType="BOOL" Value="1" />
<DataValueMember Name="ZInput" DataType="BOOL" Value="1" />
<DataValueMember Name="Filter" DataType="SINT" Radix="Binary" Value="2#0000_0001" />
<DataValueMember Name="Filter_0" DataType="BOOL" Value="1" />
<DataValueMember Name="Filter_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Filter_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Filter_3" DataType="BOOL" Value="0" />
<DataValueMember Name="FilterA" DataType="BOOL" Value="0" />
<DataValueMember Name="FilterB" DataType="BOOL" Value="0" />
<DataValueMember Name="FilterZ" DataType="BOOL" Value="0" />
<DataValueMember Name="DecimalPosition" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="TimeBase" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="GateInterval" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Scalar" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="RollOver" DataType="DINT" Radix="Decimal" Value="16777215" />
<DataValueMember Name="Preset" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="SSCounterControl" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SSCounterReset" DataType="BOOL" Value="0" />
<DataValueMember Name="SSCounterPreset" DataType="BOOL" Value="0" />
<DataValueMember Name="SSValueReset" DataType="BOOL" Value="0" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="OutputData" RPI="10000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_IJK:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="PresentData" DataType="DINT" Radix="Decimal" Value="9417503" />
<DataValueMember Name="StoredData" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Status" DataType="INT" Radix="Binary" Value="2#0000_0000_0011_0000" />
<DataValueMember Name="ZeroFreqDetect" DataType="BOOL" Value="0" />
<DataValueMember Name="StoredDataCount_2" DataType="BOOL" Value="0" />
<DataValueMember Name="StoredDataCount_3" DataType="BOOL" Value="0" />
<DataValueMember Name="AInputStatus" DataType="BOOL" Value="1" />
<DataValueMember Name="BInputStatus" DataType="BOOL" Value="1" />
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
""", 'L5X_Samples/Gutchess_GreenLine_2026_06_04r00.L5X', 2),
    '1734-IR2/C': ("""\
<Module Name="TestMod1_1734IR2C" CatalogNumber="1734-AENT/C" Vendor="1" ProductType="12" ProductCode="108" Major="6" Minor="12" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="0" Type="PointIO" Upstream="false">
<Bus Size="2" />
</Port>
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications CommMethod="805306369">
<Connections>
<Connection Name="Output" RPI="4000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_2SLOT:I:0">
<DataValueMember Name="SlotStatusBits0_31" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111" />
<DataValueMember Name="SlotStatusBits32_63" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111" />
<ArrayMember Name="Data" DataType="SINT" Dimensions="2" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000" />
<Element Index="[1]" Value="2#0000_0000" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[-1,-1,[0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_2SLOT:O:0">
<ArrayMember Name="Data" DataType="SINT" Dimensions="2" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000" />
<Element Index="[1]" Value="2#0000_0000" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module Name="TestMod2_1734IR2C" CatalogNumber="1734-IR2/C" Vendor="1" ProductType="115" ProductCode="50" Major="3" Minor="1" ParentModule="TestMod1_1734IR2C" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="1" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="536870913">
<ConfigTag ConfigSize="42" ExternalAccess="Read/Write">
<Data Format="L5K">
[46,123,1,1000,5000,0,-32768,32767,-32768,32767,0,0,1,2,1000,5000,0,-32768,32767,-32768,32767,0,0,1,2,1,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_IR2:C:0">
<DataValueMember Name="Ch0LowEngineering" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Ch0HighEngineering" DataType="INT" Radix="Decimal" Value="5000" />
<DataValueMember Name="Ch0DigitalFilter" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch0LAlarmLimit" DataType="INT" Radix="Decimal" Value="-32768" />
<DataValueMember Name="Ch0HAlarmLimit" DataType="INT" Radix="Decimal" Value="32767" />
<DataValueMember Name="Ch0LLAlarmLimit" DataType="INT" Radix="Decimal" Value="-32768" />
<DataValueMember Name="Ch0HHAlarmLimit" DataType="INT" Radix="Decimal" Value="32767" />
<DataValueMember Name="Ch0LimitAlarmLatch" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch0AlarmDisable" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch0SensorType" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="Ch0TempMode" DataType="SINT" Radix="Decimal" Value="2" />
<DataValueMember Name="Ch1LowEngineering" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Ch1HighEngineering" DataType="INT" Radix="Decimal" Value="5000" />
<DataValueMember Name="Ch1DigitalFilter" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1LAlarmLimit" DataType="INT" Radix="Decimal" Value="-32768" />
<DataValueMember Name="Ch1HAlarmLimit" DataType="INT" Radix="Decimal" Value="32767" />
<DataValueMember Name="Ch1LLAlarmLimit" DataType="INT" Radix="Decimal" Value="-32768" />
<DataValueMember Name="Ch1HHAlarmLimit" DataType="INT" Radix="Decimal" Value="32767" />
<DataValueMember Name="Ch1LimitAlarmLatch" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1AlarmDisable" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1SensorType" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="Ch1TempMode" DataType="SINT" Radix="Decimal" Value="2" />
<DataValueMember Name="NotchFilter" DataType="SINT" Radix="Decimal" Value="1" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="InputData" RPI="80000" Type="Input" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_IR2:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="Ch0Data" DataType="INT" Radix="Decimal" Value="1017" />
<DataValueMember Name="Ch1Data" DataType="INT" Radix="Decimal" Value="1014" />
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
""", 'L5X_Samples/K3M16_Edgers_20220808r00.L5X', 2),
    '1734-OA4/C': ("""\
<Module Name="TestMod1_1734OA4C" CatalogNumber="1734-AENT/C" Vendor="1" ProductType="12" ProductCode="108" Major="6" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="0" Type="PointIO" Upstream="false">
<Bus Size="8" />
</Port>
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications CommMethod="805306369">
<Connections>
<Connection Name="Output" RPI="20000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_8SLOT:I:0">
<DataValueMember Name="SlotStatusBits0_31" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_0000_0001" />
<DataValueMember Name="SlotStatusBits32_63" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111" />
<ArrayMember Name="Data" DataType="SINT" Dimensions="8" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000" />
<Element Index="[1]" Value="2#0000_1000" />
<Element Index="[2]" Value="2#0000_1000" />
<Element Index="[3]" Value="2#0000_0000" />
<Element Index="[4]" Value="2#0000_0000" />
<Element Index="[5]" Value="2#0000_0000" />
<Element Index="[6]" Value="2#0000_0000" />
<Element Index="[7]" Value="2#0000_0000" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[-255,-1,[0,0,0,0,0,0,0,2]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_8SLOT:O:0">
<ArrayMember Name="Data" DataType="SINT" Dimensions="8" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000" />
<Element Index="[1]" Value="2#0000_0000" />
<Element Index="[2]" Value="2#0000_0000" />
<Element Index="[3]" Value="2#0000_0000" />
<Element Index="[4]" Value="2#0000_0000" />
<Element Index="[5]" Value="2#0000_0000" />
<Element Index="[6]" Value="2#0000_0000" />
<Element Index="[7]" Value="2#0000_0010" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module CatalogNumber="1734-OA4/C" Vendor="1" ProductType="7" ProductCode="290" Major="3" Minor="1" ParentModule="TestMod1_1734OA4C" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="6" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="1073741824">
<ConfigTag ConfigSize="8" ExternalAccess="Read/Write">
<Data Format="L5K">
[12,103,1,0,0,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_DO4:C:0">
<DataValueMember Name="FaultMode" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3ProgValue" DataType="BOOL" Value="0" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<RackConnection>
<OutAliasTag />
</RackConnection>
</Connections>
</Communications>
</Module>
""", 'L5X_Samples/Sorter1_20260722r00.L5X', 2),
    '1734-OB2EP/C': ("""\
<Module Name="TestMod1_1734OB2EPC" CatalogNumber="1734-AENTR/C" Vendor="1" ProductType="12" ProductCode="196" Major="6" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="0" Type="PointIO" Upstream="false">
<Bus Size="10" />
</Port>
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications CommMethod="805306369">
<Connections>
<Connection Name="Output" RPI="20000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_10SLOT:I:0">
<DataValueMember Name="SlotStatusBits0_31" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1100_0011_0001" />
<DataValueMember Name="SlotStatusBits32_63" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111" />
<ArrayMember Name="Data" DataType="SINT" Dimensions="10" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000" />
<Element Index="[1]" Value="2#0000_0000" />
<Element Index="[2]" Value="2#0000_0000" />
<Element Index="[3]" Value="2#0000_0011" />
<Element Index="[4]" Value="2#0000_0000" />
<Element Index="[5]" Value="2#0000_0000" />
<Element Index="[6]" Value="2#0000_0000" />
<Element Index="[7]" Value="2#0000_0000" />
<Element Index="[8]" Value="2#0000_0000" />
<Element Index="[9]" Value="2#0000_0000" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[-975,-1,[0,0,0,0,0,0,0,0,0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_10SLOT:O:0">
<ArrayMember Name="Data" DataType="SINT" Dimensions="10" Radix="Binary">
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
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module Name="TestMod2_1734OB2EPC" CatalogNumber="1734-OB2EP/C" Vendor="1" ProductType="7" ProductCode="163" Major="3" Minor="1" ParentModule="TestMod1_1734OB2EPC" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="6" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="1073741824">
<ConfigTag ConfigSize="12" ExternalAccess="Read/Write">
<Data Format="L5K">
[16,123,1,0,0,0,0,0,0,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_DOB2:C:0">
<DataValueMember Name="FaultMode" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="AutoRestartEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultLatchEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultLatchEn" DataType="BOOL" Value="0" />
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
""", 'DnR_Personal/Bender134053_201104.L5X', 2),
    '1734-OB8/C': ("""\
<Module Name="TestMod1_1734OB8C" CatalogNumber="1734-AENTR/C" Vendor="1" ProductType="12" ProductCode="196" Major="7" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="0" Type="PointIO" Upstream="false">
<Bus Size="12" />
</Port>
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications CommMethod="805306369">
<Connections>
<Connection Name="Output" RPI="20000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_12SLOT:I:0">
<DataValueMember Name="SlotStatusBits0_31" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="SlotStatusBits32_63" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<ArrayMember Name="Data" DataType="SINT" Dimensions="12" Radix="Binary">
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
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[0,0,[0,0,0,0,0,0,0,0,0,0,0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_12SLOT:O:0">
<ArrayMember Name="Data" DataType="SINT" Dimensions="12" Radix="Binary">
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
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module CatalogNumber="1734-OB8/C" Vendor="1" ProductType="7" ProductCode="232" Major="3" Minor="1" ParentModule="TestMod1_1734OB8C" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="5" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="1073741824">
<ConfigTag ConfigSize="12" ExternalAccess="Read/Write">
<Data Format="L5K">
[16,123,1,0,0,0,0,0,0,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_DO8_NoDiag:C:0">
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
""", 'SJ_Gormley_20251112_r02.L5X', 2),
    '1734-OB8E/C': ("""\
<Module Name="TestMod1_1734OB8EC" CatalogNumber="1734-AENTR/C" Vendor="1" ProductType="12" ProductCode="196" Major="6" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="0" Type="PointIO" Upstream="false">
<Bus Size="14" />
</Port>
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications CommMethod="805306369">
<Connections>
<Connection Name="Output" RPI="5000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_14SLOT:I:0">
<DataValueMember Name="SlotStatusBits0_31" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_0000_0001_1111" />
<DataValueMember Name="SlotStatusBits32_63" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111" />
<ArrayMember Name="Data" DataType="SINT" Dimensions="14" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000" />
<Element Index="[1]" Value="2#0000_0000" />
<Element Index="[2]" Value="2#0000_0000" />
<Element Index="[3]" Value="2#0000_0000" />
<Element Index="[4]" Value="2#0000_0000" />
<Element Index="[5]" Value="2#1010_1111" />
<Element Index="[6]" Value="2#0000_0001" />
<Element Index="[7]" Value="2#1100_0000" />
<Element Index="[8]" Value="2#0000_0000" />
<Element Index="[9]" Value="2#0000_0000" />
<Element Index="[10]" Value="2#0000_0000" />
<Element Index="[11]" Value="2#0000_0011" />
<Element Index="[12]" Value="2#0000_0000" />
<Element Index="[13]" Value="2#0000_0000" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[-4065,-1,[0,0,0,0,0,0,0,0,0,8,6,0,0,0]]
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
<Element Index="[9]" Value="2#0000_1000" />
<Element Index="[10]" Value="2#0000_0110" />
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

<Module Name="TestMod2_1734OB8EC" CatalogNumber="1734-OB8E/C" Vendor="1" ProductType="7" ProductCode="218" Major="3" Minor="1" ParentModule="TestMod1_1734OB8EC" ParentModPortId="1" Inhibited="false" MajorFault="false">
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
""", 'DnR_Personal/Bender134053_201104.L5X', 2),
    '1734-OB8S/A': ("""\
<Module Name="TestMod1_1734OB8SA" CatalogNumber="1734-AENT/C" Vendor="1" ProductType="12" ProductCode="108" Major="6" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="0" Type="PointIO" Upstream="false">
<Bus Size="17" />
</Port>
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications CommMethod="805306369">
<Connections>
<Connection Name="Output" RPI="20000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_17SLOT:I:0">
<DataValueMember Name="SlotStatusBits0_31" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1110_0000_0000_0001_1111" />
<DataValueMember Name="SlotStatusBits32_63" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111" />
<ArrayMember Name="Data" DataType="SINT" Dimensions="17" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000" />
<Element Index="[1]" Value="2#0000_0000" />
<Element Index="[2]" Value="2#0000_0000" />
<Element Index="[3]" Value="2#0000_0000" />
<Element Index="[4]" Value="2#0000_0000" />
<Element Index="[5]" Value="2#0000_1100" />
<Element Index="[6]" Value="2#0000_1000" />
<Element Index="[7]" Value="2#0001_0100" />
<Element Index="[8]" Value="2#0001_0101" />
<Element Index="[9]" Value="2#0000_0100" />
<Element Index="[10]" Value="2#0000_0000" />
<Element Index="[11]" Value="2#0000_0000" />
<Element Index="[12]" Value="2#0000_0000" />
<Element Index="[13]" Value="2#0000_0000" />
<Element Index="[14]" Value="2#0000_0000" />
<Element Index="[15]" Value="2#0000_0000" />
<Element Index="[16]" Value="2#0000_0000" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[-131041,-1,[0,0,0,0,0,0,0,0,0,0,0,0,35,2,0,11,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_17SLOT:O:0">
<ArrayMember Name="Data" DataType="SINT" Dimensions="17" Radix="Binary">
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
<Element Index="[12]" Value="2#0010_0011" />
<Element Index="[13]" Value="2#0000_0010" />
<Element Index="[14]" Value="2#0000_0000" />
<Element Index="[15]" Value="2#0000_1011" />
<Element Index="[16]" Value="2#0000_0000" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module Name="TestMod2_1734OB8SA" CatalogNumber="1734-OB8S/A" Vendor="1" ProductType="35" ProductCode="16" Major="1" Minor="1" ParentModule="TestMod1_1734OB8SA" ParentModPortId="1" Inhibited="false" MajorFault="false" SafetyNetwork="16#0000_41a6_051c_de92">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="3" Type="PointIO" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="26">
<Data Format="L5K">
[30,864,-1475071598,49403583,16900,33686504,16843009,16843009,257]
</Data>
</ConfigData>
<Connections>
<Connection Name="Input" RPI="10000" Type="SafetyInput" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="40.064" MaxObservedNetworkDelay="0" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_OB8S_Safety3:I:0">
<DataValueMember Name="RunMode" DataType="BOOL" Value="1" />
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt00Readback" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01Readback" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02Readback" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt03Readback" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04Readback" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt05Readback" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt06Readback" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt07Readback" DataType="BOOL" Value="0" />
<DataValueMember Name="OutputPowerStatus" DataType="BOOL" Value="0" />
<DataValueMember Name="CombinedOutputStatus" DataType="BOOL" Value="1" />
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
""", 'DnR_Personal/TOYOTA_135453_20221024.L5X', 2),
    '1734-OB8S/B': ("""\
<Module Name="TestMod1_1734OB8SB" CatalogNumber="1734-AENTR/C" Vendor="1" ProductType="12" ProductCode="196" Major="6" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="0" Type="PointIO" Upstream="false">
<Bus Size="14" />
</Port>
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications CommMethod="805306369">
<Connections>
<Connection Name="Output" RPI="5000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_14SLOT:I:0">
<DataValueMember Name="SlotStatusBits0_31" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_0000_0001_1111" />
<DataValueMember Name="SlotStatusBits32_63" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111" />
<ArrayMember Name="Data" DataType="SINT" Dimensions="14" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000" />
<Element Index="[1]" Value="2#0000_0000" />
<Element Index="[2]" Value="2#0000_0000" />
<Element Index="[3]" Value="2#0000_0000" />
<Element Index="[4]" Value="2#0000_0000" />
<Element Index="[5]" Value="2#1010_1111" />
<Element Index="[6]" Value="2#0000_0001" />
<Element Index="[7]" Value="2#1100_0000" />
<Element Index="[8]" Value="2#0000_0000" />
<Element Index="[9]" Value="2#0000_0000" />
<Element Index="[10]" Value="2#0000_0000" />
<Element Index="[11]" Value="2#0000_0011" />
<Element Index="[12]" Value="2#0000_0000" />
<Element Index="[13]" Value="2#0000_0000" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[-4065,-1,[0,0,0,0,0,0,0,0,0,8,6,0,0,0]]
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
<Element Index="[9]" Value="2#0000_1000" />
<Element Index="[10]" Value="2#0000_0110" />
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

<Module Name="TestMod2_1734OB8SB" CatalogNumber="1734-OB8S/B" Vendor="1" ProductType="35" ProductCode="16" Major="2" Minor="1" ParentModule="TestMod1_1734OB8SB" ParentModPortId="1" Inhibited="false" MajorFault="false" SafetyNetwork="16#0000_447d_042b_b261">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="3" Type="PointIO" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="26">
<Data Format="L5K">
[30,864,1181255011,46978231,17651,16843752,16843009,16843009,257]
</Data>
</ConfigData>
<Connections>
<Connection Name="Input" RPI="10000" Type="SafetyInput" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="40.064" MaxObservedNetworkDelay="0" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_OB8S_Safety1:I:0">
<DataValueMember Name="RunMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt00OutputStatus" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01OutputStatus" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02OutputStatus" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt03OutputStatus" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04OutputStatus" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt05OutputStatus" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt06OutputStatus" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt07OutputStatus" DataType="BOOL" Value="0" />
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
""", 'DnR_Personal/Bender134053_201104.L5X', 2),
    '1734-OE2C/C': ("""\
<Module Name="TestMod1_1734OE2CC" CatalogNumber="1734-AENTR/C" Vendor="1" ProductType="12" ProductCode="196" Major="6" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="0" Type="PointIO" Upstream="false">
<Bus Size="14" />
</Port>
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
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

<Module Name="TestMod2_1734OE2CC" CatalogNumber="1734-OE2C/C" Vendor="1" ProductType="115" ProductCode="25" Major="3" Minor="1" ParentModule="TestMod1_1734OE2CC" ParentModPortId="1" Inhibited="false" MajorFault="false">
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
""", 'DnR_Personal/Bender134053_201104.L5X', 2),
    '1756-CNB/D': ("""\
<Module Name="TestMod1_1756CNBD" CatalogNumber="1756-CNB/D" Vendor="1" ProductType="12" ProductCode="7" Major="5" Minor="50" ParentModule="Local" ParentModPortId="1" Inhibited="false" MajorFault="false" ControlNetSignature="16#bb2b_890b">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="3" Type="ICP" Upstream="true" />
<Port Id="2" Address="1" Type="ControlNet" Upstream="false">
<Bus />
</Port>
</Ports>
</Module>
""", 'L5X_Samples/RobbinsGrn_2026_05_13r00.L5X', 1),
    '1756-DHRIO/E': ("""\
<Module Name="TestMod1_1756DHRIOE" CatalogNumber="1756-DHRIO/E" Vendor="1" ProductType="12" ProductCode="18" Major="7" Minor="2" ParentModule="Local" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="2" Type="ICP" Upstream="true" />
<Port Id="2" Type="RIO" Upstream="false">
<Bus Baud="230.4" />
</Port>
<Port Id="3" Type="RIO" Upstream="false">
<Bus Baud="57.6" />
</Port>
</Ports>
<Communications CommMethod="536870913">
<Connections>
<Connection Name="Standard" RPI="25000" Type="Input" EventID="0" ProgrammaticallySendEventTrigger="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1756_DHRIO:I:0">
<DataValueMember Name="CHA_Status" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="CHB_Status" DataType="SINT" Radix="Decimal" Value="3" />
</Structure>
</Data>
</InputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'L5X_Samples/Gutchess_GreenLine_2026_06_04r00.L5X', 1),
    '1756-DNB': ("""\
<Module Name="TestMod1_1756DNB" CatalogNumber="1756-DNB" Vendor="1" ProductType="12" ProductCode="14" Major="6" Minor="2" ParentModule="Local" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="4" Type="ICP" Upstream="true" />
<Port Id="2" Address="0" Type="DeviceNet" Upstream="false">
<Bus />
</Port>
</Ports>
<Communications CommMethod="536870913" PrimCxnInputSize="500" PrimCxnOutputSize="496" SecCxnInputSize="128">
<Connections>
<Connection Name="Standard" RPI="10000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1756_DNB_500Bytes:I:0">
<StructureMember Name="StatusRegister" DataType="AB:1756_DNB_StatusRegister:I:0">
<DataValueMember Name="Run" DataType="BOOL" Value="1" />
<DataValueMember Name="Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="DisableNetwork" DataType="BOOL" Value="0" />
<DataValueMember Name="DeviceFailure" DataType="BOOL" Value="1" />
<DataValueMember Name="Autoverify" DataType="BOOL" Value="0" />
<DataValueMember Name="CommFailure" DataType="BOOL" Value="0" />
<DataValueMember Name="DupNodeFail" DataType="BOOL" Value="0" />
<DataValueMember Name="DnetPowerDetect" DataType="BOOL" Value="0" />
</StructureMember>
<ArrayMember Name="Data" DataType="DINT" Dimensions="124" Radix="Decimal">
<Element Index="[0]" Value="743181071" />
<Element Index="[1]" Value="0" />
<Element Index="[2]" Value="0" />
<Element Index="[3]" Value="0" />
<Element Index="[4]" Value="2572" />
<Element Index="[5]" Value="0" />
<Element Index="[6]" Value="24775439" />
<Element Index="[7]" Value="0" />
<Element Index="[8]" Value="4" />
<Element Index="[9]" Value="655294464" />
<Element Index="[10]" Value="2572" />
<Element Index="[11]" Value="0" />
<Element Index="[12]" Value="467143439" />
<Element Index="[13]" Value="0" />
<Element Index="[14]" Value="2572" />
<Element Index="[15]" Value="0" />
<Element Index="[16]" Value="2572" />
<Element Index="[17]" Value="0" />
<Element Index="[18]" Value="2572" />
<Element Index="[19]" Value="0" />
<Element Index="[20]" Value="2572" />
<Element Index="[21]" Value="0" />
<Element Index="[22]" Value="2572" />
<Element Index="[23]" Value="0" />
<Element Index="[24]" Value="192" />
<Element Index="[25]" Value="655294464" />
<Element Index="[26]" Value="128" />
<Element Index="[27]" Value="655294464" />
<Element Index="[28]" Value="637012751" />
<Element Index="[29]" Value="0" />
<Element Index="[30]" Value="690096911" />
<Element Index="[31]" Value="8" ForceValue="2#...._...._...._...._...._...._...._1..." />
<Element Index="[32]" Value="1" />
<Element Index="[33]" Value="655294464" />
<Element Index="[34]" Value="4" />
<Element Index="[35]" Value="655294464" />
<Element Index="[36]" Value="0" />
<Element Index="[37]" Value="0" />
<Element Index="[38]" Value="0" />
<Element Index="[39]" Value="655294464" />
<Element Index="[40]" Value="0" />
<Element Index="[41]" Value="655294464" />
<Element Index="[42]" Value="0" />
<Element Index="[43]" Value="0" />
<Element Index="[44]" Value="40108500" />
<Element Index="[45]" Value="655294494" />
<Element Index="[46]" Value="35783124" />
<Element Index="[47]" Value="655294520" />
<Element Index="[48]" Value="0" />
<Element Index="[49]" Value="0" />
<Element Index="[50]" Value="23069140" />
<Element Index="[51]" Value="655294489" />
<Element Index="[52]" Value="2572" />
<Element Index="[53]" Value="0" />
<Element Index="[54]" Value="0" />
<Element Index="[55]" Value="0" />
<Element Index="[56]" Value="0" />
<Element Index="[57]" Value="0" />
<Element Index="[58]" Value="0" />
<Element Index="[59]" Value="0" />
<Element Index="[60]" Value="0" />
<Element Index="[61]" Value="0" />
<Element Index="[62]" Value="0" />
<Element Index="[63]" Value="0" />
<Element Index="[64]" Value="0" />
<Element Index="[65]" Value="0" />
<Element Index="[66]" Value="0" />
<Element Index="[67]" Value="0" />
<Element Index="[68]" Value="0" />
<Element Index="[69]" Value="0" />
<Element Index="[70]" Value="0" />
<Element Index="[71]" Value="0" />
<Element Index="[72]" Value="0" />
<Element Index="[73]" Value="0" />
<Element Index="[74]" Value="0" />
<Element Index="[75]" Value="0" />
<Element Index="[76]" Value="0" />
<Element Index="[77]" Value="0" />
<Element Index="[78]" Value="0" />
<Element Index="[79]" Value="0" />
<Element Index="[80]" Value="0" />
<Element Index="[81]" Value="0" />
<Element Index="[82]" Value="0" />
<Element Index="[83]" Value="0" />
<Element Index="[84]" Value="0" />
<Element Index="[85]" Value="0" />
<Element Index="[86]" Value="0" />
<Element Index="[87]" Value="0" />
<Element Index="[88]" Value="0" />
<Element Index="[89]" Value="0" />
<Element Index="[90]" Value="0" />
<Element Index="[91]" Value="0" />
<Element Index="[92]" Value="0" />
<Element Index="[93]" Value="0" />
<Element Index="[94]" Value="0" />
<Element Index="[95]" Value="0" />
<Element Index="[96]" Value="0" />
<Element Index="[97]" Value="0" />
<Element Index="[98]" Value="0" />
<Element Index="[99]" Value="0" />
<Element Index="[100]" Value="0" />
<Element Index="[101]" Value="0" />
<Element Index="[102]" Value="0" />
<Element Index="[103]" Value="0" />
<Element Index="[104]" Value="0" />
<Element Index="[105]" Value="0" />
<Element Index="[106]" Value="0" />
<Element Index="[107]" Value="0" />
<Element Index="[108]" Value="0" />
<Element Index="[109]" Value="0" />
<Element Index="[110]" Value="0" />
<Element Index="[111]" Value="0" />
<Element Index="[112]" Value="0" />
<Element Index="[113]" Value="0" />
<Element Index="[114]" Value="0" />
<Element Index="[115]" Value="0" />
<Element Index="[116]" Value="0" />
<Element Index="[117]" Value="0" />
<Element Index="[118]" Value="0" />
<Element Index="[119]" Value="0" />
<Element Index="[120]" Value="0" />
<Element Index="[121]" Value="0" />
<Element Index="[122]" Value="0" />
<Element Index="[123]" Value="0" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[[1],[743182418,97,0,97,4161,97,98,0,97,97,4161,97,467144786,96,1376522305,97,1651834945,97,1651834945,97
		,1651834977,97,94769217,96,96,97,96,97,637014098,0,690098258,0,97,0,97,0,96,0,96,0,96,0,96,0,97,0,97,0,96,0,97,0,4161
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1756_DNB_496Bytes:O:0">
<StructureMember Name="CommandRegister" DataType="AB:1756_DNB_CommandRegister:O:0">
<DataValueMember Name="Run" DataType="BOOL" Value="1" />
<DataValueMember Name="Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="DisableNetwork" DataType="BOOL" Value="0" />
<DataValueMember Name="HaltScanner" DataType="BOOL" Value="0" />
<DataValueMember Name="Reset" DataType="BOOL" Value="0" />
</StructureMember>
<ArrayMember Name="Data" DataType="DINT" Dimensions="123" Radix="Decimal">
<Element Index="[0]" Value="743182418" />
<Element Index="[1]" Value="97" />
<Element Index="[2]" Value="0" />
<Element Index="[3]" Value="97" />
<Element Index="[4]" Value="4161" />
<Element Index="[5]" Value="97" />
<Element Index="[6]" Value="98" />
<Element Index="[7]" Value="0" />
<Element Index="[8]" Value="97" />
<Element Index="[9]" Value="97" />
<Element Index="[10]" Value="4161" />
<Element Index="[11]" Value="97" />
<Element Index="[12]" Value="467144786" />
<Element Index="[13]" Value="96" />
<Element Index="[14]" Value="1376522305" />
<Element Index="[15]" Value="97" />
<Element Index="[16]" Value="1651834945" />
<Element Index="[17]" Value="97" />
<Element Index="[18]" Value="1651834945" />
<Element Index="[19]" Value="97" />
<Element Index="[20]" Value="1651834977" />
<Element Index="[21]" Value="97" />
<Element Index="[22]" Value="94769217" />
<Element Index="[23]" Value="96" />
<Element Index="[24]" Value="96" />
<Element Index="[25]" Value="97" />
<Element Index="[26]" Value="96" />
<Element Index="[27]" Value="97" />
<Element Index="[28]" Value="637014098" />
<Element Index="[29]" Value="0" />
<Element Index="[30]" Value="690098258" />
<Element Index="[31]" Value="0" />
<Element Index="[32]" Value="97" />
<Element Index="[33]" Value="0" />
<Element Index="[34]" Value="97" />
<Element Index="[35]" Value="0" />
<Element Index="[36]" Value="96" />
<Element Index="[37]" Value="0" />
<Element Index="[38]" Value="96" />
<Element Index="[39]" Value="0" />
<Element Index="[40]" Value="96" />
<Element Index="[41]" Value="0" />
<Element Index="[42]" Value="96" />
<Element Index="[43]" Value="0" />
<Element Index="[44]" Value="97" />
<Element Index="[45]" Value="0" />
<Element Index="[46]" Value="97" />
<Element Index="[47]" Value="0" />
<Element Index="[48]" Value="96" />
<Element Index="[49]" Value="0" />
<Element Index="[50]" Value="97" />
<Element Index="[51]" Value="0" />
<Element Index="[52]" Value="4161" />
<Element Index="[53]" Value="0" />
<Element Index="[54]" Value="0" />
<Element Index="[55]" Value="0" />
<Element Index="[56]" Value="0" />
<Element Index="[57]" Value="0" />
<Element Index="[58]" Value="0" />
<Element Index="[59]" Value="0" />
<Element Index="[60]" Value="0" />
<Element Index="[61]" Value="0" />
<Element Index="[62]" Value="0" />
<Element Index="[63]" Value="0" />
<Element Index="[64]" Value="0" />
<Element Index="[65]" Value="0" />
<Element Index="[66]" Value="0" />
<Element Index="[67]" Value="0" />
<Element Index="[68]" Value="0" />
<Element Index="[69]" Value="0" />
<Element Index="[70]" Value="0" />
<Element Index="[71]" Value="0" />
<Element Index="[72]" Value="0" />
<Element Index="[73]" Value="0" />
<Element Index="[74]" Value="0" />
<Element Index="[75]" Value="0" />
<Element Index="[76]" Value="0" />
<Element Index="[77]" Value="0" />
<Element Index="[78]" Value="0" />
<Element Index="[79]" Value="0" />
<Element Index="[80]" Value="0" />
<Element Index="[81]" Value="0" />
<Element Index="[82]" Value="0" />
<Element Index="[83]" Value="0" />
<Element Index="[84]" Value="0" />
<Element Index="[85]" Value="0" />
<Element Index="[86]" Value="0" />
<Element Index="[87]" Value="0" />
<Element Index="[88]" Value="0" />
<Element Index="[89]" Value="0" />
<Element Index="[90]" Value="0" />
<Element Index="[91]" Value="0" />
<Element Index="[92]" Value="0" />
<Element Index="[93]" Value="0" />
<Element Index="[94]" Value="0" />
<Element Index="[95]" Value="0" />
<Element Index="[96]" Value="0" />
<Element Index="[97]" Value="0" />
<Element Index="[98]" Value="0" />
<Element Index="[99]" Value="0" />
<Element Index="[100]" Value="0" />
<Element Index="[101]" Value="0" />
<Element Index="[102]" Value="0" />
<Element Index="[103]" Value="0" />
<Element Index="[104]" Value="0" />
<Element Index="[105]" Value="0" />
<Element Index="[106]" Value="0" />
<Element Index="[107]" Value="0" />
<Element Index="[108]" Value="0" />
<Element Index="[109]" Value="0" />
<Element Index="[110]" Value="0" />
<Element Index="[111]" Value="0" />
<Element Index="[112]" Value="0" />
<Element Index="[113]" Value="0" />
<Element Index="[114]" Value="0" />
<Element Index="[115]" Value="0" />
<Element Index="[116]" Value="0" />
<Element Index="[117]" Value="0" />
<Element Index="[118]" Value="0" />
<Element Index="[119]" Value="0" />
<Element Index="[120]" Value="0" />
<Element Index="[121]" Value="0" />
<Element Index="[122]" Value="0" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
<Connection Name="Status" RPI="10000" Type="Input" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1756_DNB_Status_128Bytes:S:0">
<DataValueMember Name="ScanCounter" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_1111_0011_0011" />
<ArrayMember Name="DeviceFailureRegister" DataType="SINT" Dimensions="8" Radix="Binary">
<Element Index="[0]" Value="2#0000_0100" />
<Element Index="[1]" Value="2#0000_0000" />
<Element Index="[2]" Value="2#0100_1000" />
<Element Index="[3]" Value="2#0000_0010" />
<Element Index="[4]" Value="2#0000_0000" />
<Element Index="[5]" Value="2#0000_0000" />
<Element Index="[6]" Value="2#0000_0000" />
<Element Index="[7]" Value="2#0000_0000" />
</ArrayMember>
<ArrayMember Name="AutoverifyFailureRegister" DataType="SINT" Dimensions="8" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000" />
<Element Index="[1]" Value="2#0000_0000" />
<Element Index="[2]" Value="2#0000_0000" />
<Element Index="[3]" Value="2#0000_0000" />
<Element Index="[4]" Value="2#0000_0000" />
<Element Index="[5]" Value="2#0000_0000" />
<Element Index="[6]" Value="2#0000_0000" />
<Element Index="[7]" Value="2#0000_0000" />
</ArrayMember>
<ArrayMember Name="DeviceIdleRegister" DataType="SINT" Dimensions="8" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000" />
<Element Index="[1]" Value="2#0000_0000" />
<Element Index="[2]" Value="2#0000_0000" />
<Element Index="[3]" Value="2#0000_0000" />
<Element Index="[4]" Value="2#0000_0000" />
<Element Index="[5]" Value="2#0000_0000" />
<Element Index="[6]" Value="2#0000_0000" />
<Element Index="[7]" Value="2#0000_0000" />
</ArrayMember>
<ArrayMember Name="ActiveNodeRegister" DataType="SINT" Dimensions="8" Radix="Binary">
<Element Index="[0]" Value="2#1111_1110" />
<Element Index="[1]" Value="2#1111_1111" />
<Element Index="[2]" Value="2#1111_1111" />
<Element Index="[3]" Value="2#0000_1111" />
<Element Index="[4]" Value="2#0000_0000" />
<Element Index="[5]" Value="2#0000_0000" />
<Element Index="[6]" Value="2#0000_0000" />
<Element Index="[7]" Value="2#0000_0000" />
</ArrayMember>
<ArrayMember Name="StatusDisplay" DataType="SINT" Dimensions="4" Radix="Binary">
<Element Index="[0]" Value="2#0100_1110" />
<Element Index="[1]" Value="2#0010_0011" />
<Element Index="[2]" Value="2#0011_0010" />
<Element Index="[3]" Value="2#0011_0010" />
</ArrayMember>
<DataValueMember Name="ScannerAddress" DataType="SINT" Radix="Hex" Value="16#00" />
<DataValueMember Name="ScannerStatus" DataType="SINT" Radix="Hex" Value="16#00" />
<DataValueMember Name="ScrollingDeviceAddress" DataType="SINT" Radix="Hex" Value="16#13" />
<DataValueMember Name="ScrollingDeviceStatus" DataType="SINT" Radix="Hex" Value="16#4e" />
<ArrayMember Name="DeviceStatus" DataType="SINT" Dimensions="64" Radix="Hex">
<Element Index="[0]" Value="16#00" />
<Element Index="[1]" Value="16#00" />
<Element Index="[2]" Value="16#4e" />
<Element Index="[3]" Value="16#00" />
<Element Index="[4]" Value="16#00" />
<Element Index="[5]" Value="16#00" />
<Element Index="[6]" Value="16#00" />
<Element Index="[7]" Value="16#00" />
<Element Index="[8]" Value="16#00" />
<Element Index="[9]" Value="16#00" />
<Element Index="[10]" Value="16#00" />
<Element Index="[11]" Value="16#00" />
<Element Index="[12]" Value="16#00" />
<Element Index="[13]" Value="16#00" />
<Element Index="[14]" Value="16#00" />
<Element Index="[15]" Value="16#00" />
<Element Index="[16]" Value="16#00" />
<Element Index="[17]" Value="16#00" />
<Element Index="[18]" Value="16#00" />
<Element Index="[19]" Value="16#4e" />
<Element Index="[20]" Value="16#00" />
<Element Index="[21]" Value="16#00" />
<Element Index="[22]" Value="16#4e" />
<Element Index="[23]" Value="16#00" />
<Element Index="[24]" Value="16#00" />
<Element Index="[25]" Value="16#4e" />
<Element Index="[26]" Value="16#00" />
<Element Index="[27]" Value="16#00" />
<Element Index="[28]" Value="16#00" />
<Element Index="[29]" Value="16#00" />
<Element Index="[30]" Value="16#00" />
<Element Index="[31]" Value="16#00" />
<Element Index="[32]" Value="16#00" />
<Element Index="[33]" Value="16#00" />
<Element Index="[34]" Value="16#00" />
<Element Index="[35]" Value="16#00" />
<Element Index="[36]" Value="16#00" />
<Element Index="[37]" Value="16#00" />
<Element Index="[38]" Value="16#00" />
<Element Index="[39]" Value="16#00" />
<Element Index="[40]" Value="16#00" />
<Element Index="[41]" Value="16#00" />
<Element Index="[42]" Value="16#00" />
<Element Index="[43]" Value="16#00" />
<Element Index="[44]" Value="16#00" />
<Element Index="[45]" Value="16#00" />
<Element Index="[46]" Value="16#00" />
<Element Index="[47]" Value="16#00" />
<Element Index="[48]" Value="16#00" />
<Element Index="[49]" Value="16#00" />
<Element Index="[50]" Value="16#00" />
<Element Index="[51]" Value="16#00" />
<Element Index="[52]" Value="16#00" />
<Element Index="[53]" Value="16#00" />
<Element Index="[54]" Value="16#00" />
<Element Index="[55]" Value="16#00" />
<Element Index="[56]" Value="16#00" />
<Element Index="[57]" Value="16#00" />
<Element Index="[58]" Value="16#00" />
<Element Index="[59]" Value="16#00" />
<Element Index="[60]" Value="16#00" />
<Element Index="[61]" Value="16#00" />
<Element Index="[62]" Value="16#00" />
<Element Index="[63]" Value="16#00" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'L5X_Samples/RobbinsGrn_2026_05_13r00.L5X', 1),
    '1756-EN4TR': ("""\
<Module Name="TestMod1_1756EN4TR" CatalogNumber="1756-EN4TR" Vendor="1" ProductType="12" ProductCode="258" Major="4" Minor="1" ParentModule="Local" ParentModPortId="1" Inhibited="false" MajorFault="false" AutoDiagsEnabled="true">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="14" Type="ICP" Upstream="true" />
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="false">
<Bus />
</Port>
</Ports>
<Communications>
<ConfigData ConfigSize="16">
<Data Format="L5K">
[20,768,393217,33554433,256,0]
</Data>
</ConfigData>
<Connections>
<Connection Name="Input2" RPI="500000" Type="Input" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="false" />
</Connections>
</Communications>
</Module>
""", 'L5X_Samples/RobbinsGrn_2026_05_13r00.L5X', 1),
    '1756-HSC/A': ("""\
<Module Name="TestMod1_1756HSCA" CatalogNumber="1756-HSC/A" Vendor="1" ProductType="109" ProductCode="10" Major="1" Minor="6" ParentModule="Local" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="8" Type="ICP" Upstream="true" />
</Ports>
<Communications CommMethod="536870913">
<ConfigTag ConfigSize="116" ExternalAccess="Read/Write">
<Data Format="L5K">
[120,3,0,0,0,[65535,65535],[0,0],[0,0],[2,2],[4,4],0,0,0,0,[[[0,0],[0,0],0,0,0,0],[[0,0],[0,0],0,0,0,0],[[0,0],[0,0],0,0,0,0],[[0,0],[0,0],0,0,0,0]]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1756_HSC:C:0">
<DataValueMember Name="ProgToFaultEn" DataType="BOOL" Value="0" />
<ArrayMember Name="RollOver" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="65535" />
<Element Index="[1]" Value="65535" />
</ArrayMember>
<ArrayMember Name="Preset" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="0" />
<Element Index="[1]" Value="0" />
</ArrayMember>
<ArrayMember Name="Scaler" DataType="INT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="0" />
<Element Index="[1]" Value="0" />
</ArrayMember>
<ArrayMember Name="OperationalMode" DataType="SINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="2" />
<Element Index="[1]" Value="2" />
</ArrayMember>
<ArrayMember Name="StorageMode" DataType="SINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="4" />
<Element Index="[1]" Value="4" />
</ArrayMember>
<DataValueMember Name="ZInvert" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="FilterA" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="FilterB" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="FilterZ" DataType="SINT" Radix="Decimal" Value="0" />
<ArrayMember Name="Output" DataType="AB:1756_HSC_Output:C:0" Dimensions="4">
<Element Index="[0]">
<Structure DataType="AB:1756_HSC_Output:C:0">
<ArrayMember Name="ONValue" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="0" />
<Element Index="[1]" Value="0" />
</ArrayMember>
<ArrayMember Name="OFFValue" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="0" />
<Element Index="[1]" Value="0" />
</ArrayMember>
<DataValueMember Name="ToThisCounter" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="FaultMode" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="ProgMode" DataType="SINT" Radix="Decimal" Value="0" />
</Structure>
</Element>
<Element Index="[1]">
<Structure DataType="AB:1756_HSC_Output:C:0">
<ArrayMember Name="ONValue" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="0" />
<Element Index="[1]" Value="0" />
</ArrayMember>
<ArrayMember Name="OFFValue" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="0" />
<Element Index="[1]" Value="0" />
</ArrayMember>
<DataValueMember Name="ToThisCounter" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="FaultMode" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="ProgMode" DataType="SINT" Radix="Decimal" Value="0" />
</Structure>
</Element>
<Element Index="[2]">
<Structure DataType="AB:1756_HSC_Output:C:0">
<ArrayMember Name="ONValue" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="0" />
<Element Index="[1]" Value="0" />
</ArrayMember>
<ArrayMember Name="OFFValue" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="0" />
<Element Index="[1]" Value="0" />
</ArrayMember>
<DataValueMember Name="ToThisCounter" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="FaultMode" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="ProgMode" DataType="SINT" Radix="Decimal" Value="0" />
</Structure>
</Element>
<Element Index="[3]">
<Structure DataType="AB:1756_HSC_Output:C:0">
<ArrayMember Name="ONValue" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="0" />
<Element Index="[1]" Value="0" />
</ArrayMember>
<ArrayMember Name="OFFValue" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="0" />
<Element Index="[1]" Value="0" />
</ArrayMember>
<DataValueMember Name="ToThisCounter" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="FaultMode" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="ProgMode" DataType="SINT" Radix="Decimal" Value="0" />
</Structure>
</Element>
</ArrayMember>
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="Standard" RPI="2000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1756_HSC:I:0">
<DataValueMember Name="CommStatus" DataType="DINT" Radix="Decimal" Value="0" />
<ArrayMember Name="PresentValue" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="899" />
<Element Index="[1]" Value="278" />
</ArrayMember>
<ArrayMember Name="StoredValue" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="2000" />
<Element Index="[1]" Value="2000" />
</ArrayMember>
<DataValueMember Name="WasReset" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="WasPreset" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="NewDataFlag" DataType="SINT" Radix="Decimal" Value="3" />
<DataValueMember Name="ZState" DataType="SINT" Radix="Decimal" Value="2" />
<DataValueMember Name="OutputState" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="IsOverridden" DataType="SINT" Radix="Decimal" Value="3" />
<ArrayMember Name="CSTTimestamp" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="131156783" />
<Element Index="[1]" Value="220" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[0,0,0,0,[1,1,0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1756_HSC:O:0">
<DataValueMember Name="ResetCounter" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="LoadPreset" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="ResetNewDataFlag" DataType="SINT" Radix="Decimal" Value="0" />
<ArrayMember Name="OutputControl" DataType="SINT" Dimensions="4" Radix="Decimal">
<Element Index="[0]" Value="1" />
<Element Index="[1]" Value="1" />
<Element Index="[2]" Value="0" />
<Element Index="[3]" Value="0" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'L5X_Samples/RobbinsGrn_2026_05_13r00.L5X', 1),
    '1756-HSC/B': ("""\
<Module Name="TestMod1_1756HSCB" CatalogNumber="1756-HSC/B" Vendor="1" ProductType="109" ProductCode="10" Major="3" Minor="1" ParentModule="Local" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="4" Type="ICP" Upstream="true" />
</Ports>
<Communications CommMethod="536870913">
<ConfigTag ConfigSize="116" ExternalAccess="Read/Write">
<Data Format="L5K">
[120,3,0,0,0,[65535,65535],[0,0],[0,0],[2,2],[4,4],0,0,0,0,[[[0,0],[0,0],0,0,0,0],[[0,0],[0,0],0,0,0,0],[[0,0],[0,0],0,0,0,0],[[0,0],[0,0],0,0,0,0]]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1756_HSC:C:0">
<DataValueMember Name="ProgToFaultEn" DataType="BOOL" Value="0" />
<ArrayMember Name="RollOver" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="65535" />
<Element Index="[1]" Value="65535" />
</ArrayMember>
<ArrayMember Name="Preset" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="0" />
<Element Index="[1]" Value="0" />
</ArrayMember>
<ArrayMember Name="Scaler" DataType="INT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="0" />
<Element Index="[1]" Value="0" />
</ArrayMember>
<ArrayMember Name="OperationalMode" DataType="SINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="2" />
<Element Index="[1]" Value="2" />
</ArrayMember>
<ArrayMember Name="StorageMode" DataType="SINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="4" />
<Element Index="[1]" Value="4" />
</ArrayMember>
<DataValueMember Name="ZInvert" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="FilterA" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="FilterB" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="FilterZ" DataType="SINT" Radix="Decimal" Value="0" />
<ArrayMember Name="Output" DataType="AB:1756_HSC_Output:C:0" Dimensions="4">
<Element Index="[0]">
<Structure DataType="AB:1756_HSC_Output:C:0">
<ArrayMember Name="ONValue" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="0" />
<Element Index="[1]" Value="0" />
</ArrayMember>
<ArrayMember Name="OFFValue" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="0" />
<Element Index="[1]" Value="0" />
</ArrayMember>
<DataValueMember Name="ToThisCounter" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="FaultMode" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="ProgMode" DataType="SINT" Radix="Decimal" Value="0" />
</Structure>
</Element>
<Element Index="[1]">
<Structure DataType="AB:1756_HSC_Output:C:0">
<ArrayMember Name="ONValue" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="0" />
<Element Index="[1]" Value="0" />
</ArrayMember>
<ArrayMember Name="OFFValue" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="0" />
<Element Index="[1]" Value="0" />
</ArrayMember>
<DataValueMember Name="ToThisCounter" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="FaultMode" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="ProgMode" DataType="SINT" Radix="Decimal" Value="0" />
</Structure>
</Element>
<Element Index="[2]">
<Structure DataType="AB:1756_HSC_Output:C:0">
<ArrayMember Name="ONValue" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="0" />
<Element Index="[1]" Value="0" />
</ArrayMember>
<ArrayMember Name="OFFValue" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="0" />
<Element Index="[1]" Value="0" />
</ArrayMember>
<DataValueMember Name="ToThisCounter" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="FaultMode" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="ProgMode" DataType="SINT" Radix="Decimal" Value="0" />
</Structure>
</Element>
<Element Index="[3]">
<Structure DataType="AB:1756_HSC_Output:C:0">
<ArrayMember Name="ONValue" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="0" />
<Element Index="[1]" Value="0" />
</ArrayMember>
<ArrayMember Name="OFFValue" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="0" />
<Element Index="[1]" Value="0" />
</ArrayMember>
<DataValueMember Name="ToThisCounter" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="FaultMode" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="ProgMode" DataType="SINT" Radix="Decimal" Value="0" />
</Structure>
</Element>
</ArrayMember>
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="Standard" RPI="2000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1756_HSC:I:0">
<DataValueMember Name="CommStatus" DataType="DINT" Radix="Decimal" Value="0" />
<ArrayMember Name="PresentValue" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="336" />
<Element Index="[1]" Value="0" />
</ArrayMember>
<ArrayMember Name="StoredValue" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="2000" />
<Element Index="[1]" Value="0" />
</ArrayMember>
<DataValueMember Name="WasReset" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="WasPreset" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="NewDataFlag" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="ZState" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="OutputState" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="IsOverridden" DataType="SINT" Radix="Decimal" Value="0" />
<ArrayMember Name="CSTTimestamp" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="-1856297339" />
<Element Index="[1]" Value="3075" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[0,0,0,0,[0,0,0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1756_HSC:O:0">
<DataValueMember Name="ResetCounter" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="LoadPreset" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="ResetNewDataFlag" DataType="SINT" Radix="Decimal" Value="0" />
<ArrayMember Name="OutputControl" DataType="SINT" Dimensions="4" Radix="Decimal">
<Element Index="[0]" Value="0" />
<Element Index="[1]" Value="0" />
<Element Index="[2]" Value="0" />
<Element Index="[3]" Value="0" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'L5X_Samples/Gutchess_GreenLine_2026_06_04r00.L5X', 1),
    '1756-HYD02': ("""\
<Module Name="TestMod1_1756HYD02" CatalogNumber="1756-HYD02" Vendor="1" ProductType="16" ProductCode="17" Major="33" Minor="1" ParentModule="Local" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="Disabled" />
<Ports>
<Port Id="1" Address="7" Type="ICP" Upstream="true" />
</Ports>
<Communications CommMethod="536870913">
<ConfigData ConfigSize="12">
<Data Format="L5K">
[16,0,0,0,3,0,0,0,1,0,0,0,4,0,0,0,-36,5,0,0]
</Data>
</ConfigData>
<Connections>
<Connection Name="MotionAsync" RPI="25000" Type="MotionAsync" EventID="0" ProgrammaticallySendEventTrigger="false" />
<Connection Name="MotionEvent" RPI="1000000" Type="MotionEvent" EventID="0" ProgrammaticallySendEventTrigger="false" />
<Connection Name="MotionSync" RPI="6000" Type="MotionSync" EventID="0" ProgrammaticallySendEventTrigger="false" />
</Connections>
</Communications>
</Module>
""", 'L5X_Samples/RobbinsGrn_2026_05_13r00.L5X', 1),
    '1756-IA32/A': ("""\
<Module Name="TestMod1_1756IA32A" CatalogNumber="1756-IA32/A" Vendor="1" ProductType="7" ProductCode="10" Major="3" Minor="4" ParentModule="Local" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="9" Type="ICP" Upstream="true" />
</Ports>
<Communications CommMethod="536870913">
<ConfigTag ConfigSize="24" ExternalAccess="Read/Write">
<Data Format="L5K">
[28,16,0,0,0,0,1,9,1,9,1,9,1,9,-1,-1]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1756_DI:C:1">
<DataValueMember Name="FilterOffOn_0_7" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="FilterOnOff_0_7" DataType="SINT" Radix="Decimal" Value="9" />
<DataValueMember Name="FilterOffOn_8_15" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="FilterOnOff_8_15" DataType="SINT" Radix="Decimal" Value="9" />
<DataValueMember Name="FilterOffOn_16_23" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="FilterOnOff_16_23" DataType="SINT" Radix="Decimal" Value="9" />
<DataValueMember Name="FilterOffOn_24_31" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="FilterOnOff_24_31" DataType="SINT" Radix="Decimal" Value="9" />
<DataValueMember Name="COSOnOffEn" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111" />
<DataValueMember Name="COSOffOnEn" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="StandardInput" RPI="20000" Type="Input" EventID="0" ProgrammaticallySendEventTrigger="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1756_DI:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
</Structure>
</Data>
</InputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'BAI10048_TrimmerTally_20250704.L5X', 1),
    '1756-IB16': ("""\
<Module Name="TestMod1_1756IB16" CatalogNumber="1756-IB16" Vendor="1" ProductType="7" ProductCode="11" Major="2" Minor="5" ParentModule="Local" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="11" Type="ICP" Upstream="true" />
</Ports>
<Communications CommMethod="536870913">
<ConfigTag ConfigSize="24" ExternalAccess="Read/Write">
<Data Format="L5K">
[28,16,1,0,0,0,1,1,1,1,0,0,0,0,65535,65535]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1756_DI:C:0">
<DataValueMember Name="DiagCOSDisable" DataType="BOOL" Value="0" />
<DataValueMember Name="FilterOffOn_0_7" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="FilterOnOff_0_7" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="FilterOffOn_8_15" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="FilterOnOff_8_15" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="FilterOffOn_16_23" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="FilterOnOff_16_23" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="FilterOffOn_24_31" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="FilterOnOff_24_31" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="COSOnOffEn" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_1111_1111_1111_1111" />
<DataValueMember Name="COSOffOnEn" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_1111_1111_1111_1111" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="StandardInput" RPI="10000" Type="Input" EventID="0" ProgrammaticallySendEventTrigger="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1756_DI:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_1111_0000_0000_0001" />
</Structure>
</Data>
</InputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'L5X_Samples/RobbinsGrn_2026_05_13r00.L5X', 1),
    '1756-IB16IF/A': ("""\
<Module Name="TestMod1_1756IB16IFA" CatalogNumber="1756-IB16IF/A" Vendor="1" ProductType="7" ProductCode="386" Major="1" Minor="1" ParentModule="Local" ParentModPortId="1" Inhibited="false" MajorFault="false" AutoDiagsEnabled="true">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="1" Type="ICP" Upstream="true" />
</Ports>
<Communications>
<ConfigTag ConfigSize="72" ExternalAccess="Read/Write">
<Data Format="L5K">
[76,100,1,0,0,0,0,[[6],[6],[6],[6],[6],[6],[6],[6],[6],[6],[6],[6],[6],[6],[6],[6]]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1756_IB16IF:C:0">
<DataValueMember Name="LatchTimestamps" DataType="BOOL" Value="0" />
<DataValueMember Name="FilterOffOn" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="FilterOnOff" DataType="INT" Radix="Decimal" Value="0" />
<ArrayMember Name="Pt" DataType="AB:1756_IB16IF_PtStruct:C:0" Dimensions="16">
<Element Index="[0]">
<Structure DataType="AB:1756_IB16IF_PtStruct:C:0">
<DataValueMember Name="FilterEn" DataType="BOOL" Value="0" />
<DataValueMember Name="COSOffOnEn" DataType="BOOL" Value="1" />
<DataValueMember Name="COSOnOffEn" DataType="BOOL" Value="1" />
</Structure>
</Element>
<Element Index="[1]">
<Structure DataType="AB:1756_IB16IF_PtStruct:C:0">
<DataValueMember Name="FilterEn" DataType="BOOL" Value="0" />
<DataValueMember Name="COSOffOnEn" DataType="BOOL" Value="1" />
<DataValueMember Name="COSOnOffEn" DataType="BOOL" Value="1" />
</Structure>
</Element>
<Element Index="[2]">
<Structure DataType="AB:1756_IB16IF_PtStruct:C:0">
<DataValueMember Name="FilterEn" DataType="BOOL" Value="0" />
<DataValueMember Name="COSOffOnEn" DataType="BOOL" Value="1" />
<DataValueMember Name="COSOnOffEn" DataType="BOOL" Value="1" />
</Structure>
</Element>
<Element Index="[3]">
<Structure DataType="AB:1756_IB16IF_PtStruct:C:0">
<DataValueMember Name="FilterEn" DataType="BOOL" Value="0" />
<DataValueMember Name="COSOffOnEn" DataType="BOOL" Value="1" />
<DataValueMember Name="COSOnOffEn" DataType="BOOL" Value="1" />
</Structure>
</Element>
<Element Index="[4]">
<Structure DataType="AB:1756_IB16IF_PtStruct:C:0">
<DataValueMember Name="FilterEn" DataType="BOOL" Value="0" />
<DataValueMember Name="COSOffOnEn" DataType="BOOL" Value="1" />
<DataValueMember Name="COSOnOffEn" DataType="BOOL" Value="1" />
</Structure>
</Element>
<Element Index="[5]">
<Structure DataType="AB:1756_IB16IF_PtStruct:C:0">
<DataValueMember Name="FilterEn" DataType="BOOL" Value="0" />
<DataValueMember Name="COSOffOnEn" DataType="BOOL" Value="1" />
<DataValueMember Name="COSOnOffEn" DataType="BOOL" Value="1" />
</Structure>
</Element>
<Element Index="[6]">
<Structure DataType="AB:1756_IB16IF_PtStruct:C:0">
<DataValueMember Name="FilterEn" DataType="BOOL" Value="0" />
<DataValueMember Name="COSOffOnEn" DataType="BOOL" Value="1" />
<DataValueMember Name="COSOnOffEn" DataType="BOOL" Value="1" />
</Structure>
</Element>
<Element Index="[7]">
<Structure DataType="AB:1756_IB16IF_PtStruct:C:0">
<DataValueMember Name="FilterEn" DataType="BOOL" Value="0" />
<DataValueMember Name="COSOffOnEn" DataType="BOOL" Value="1" />
<DataValueMember Name="COSOnOffEn" DataType="BOOL" Value="1" />
</Structure>
</Element>
<Element Index="[8]">
<Structure DataType="AB:1756_IB16IF_PtStruct:C:0">
<DataValueMember Name="FilterEn" DataType="BOOL" Value="0" />
<DataValueMember Name="COSOffOnEn" DataType="BOOL" Value="1" />
<DataValueMember Name="COSOnOffEn" DataType="BOOL" Value="1" />
</Structure>
</Element>
<Element Index="[9]">
<Structure DataType="AB:1756_IB16IF_PtStruct:C:0">
<DataValueMember Name="FilterEn" DataType="BOOL" Value="0" />
<DataValueMember Name="COSOffOnEn" DataType="BOOL" Value="1" />
<DataValueMember Name="COSOnOffEn" DataType="BOOL" Value="1" />
</Structure>
</Element>
<Element Index="[10]">
<Structure DataType="AB:1756_IB16IF_PtStruct:C:0">
<DataValueMember Name="FilterEn" DataType="BOOL" Value="0" />
<DataValueMember Name="COSOffOnEn" DataType="BOOL" Value="1" />
<DataValueMember Name="COSOnOffEn" DataType="BOOL" Value="1" />
</Structure>
</Element>
<Element Index="[11]">
<Structure DataType="AB:1756_IB16IF_PtStruct:C:0">
<DataValueMember Name="FilterEn" DataType="BOOL" Value="0" />
<DataValueMember Name="COSOffOnEn" DataType="BOOL" Value="1" />
<DataValueMember Name="COSOnOffEn" DataType="BOOL" Value="1" />
</Structure>
</Element>
<Element Index="[12]">
<Structure DataType="AB:1756_IB16IF_PtStruct:C:0">
<DataValueMember Name="FilterEn" DataType="BOOL" Value="0" />
<DataValueMember Name="COSOffOnEn" DataType="BOOL" Value="1" />
<DataValueMember Name="COSOnOffEn" DataType="BOOL" Value="1" />
</Structure>
</Element>
<Element Index="[13]">
<Structure DataType="AB:1756_IB16IF_PtStruct:C:0">
<DataValueMember Name="FilterEn" DataType="BOOL" Value="0" />
<DataValueMember Name="COSOffOnEn" DataType="BOOL" Value="1" />
<DataValueMember Name="COSOnOffEn" DataType="BOOL" Value="1" />
</Structure>
</Element>
<Element Index="[14]">
<Structure DataType="AB:1756_IB16IF_PtStruct:C:0">
<DataValueMember Name="FilterEn" DataType="BOOL" Value="0" />
<DataValueMember Name="COSOffOnEn" DataType="BOOL" Value="1" />
<DataValueMember Name="COSOnOffEn" DataType="BOOL" Value="1" />
</Structure>
</Element>
<Element Index="[15]">
<Structure DataType="AB:1756_IB16IF_PtStruct:C:0">
<DataValueMember Name="FilterEn" DataType="BOOL" Value="0" />
<DataValueMember Name="COSOffOnEn" DataType="BOOL" Value="1" />
<DataValueMember Name="COSOnOffEn" DataType="BOOL" Value="1" />
</Structure>
</Element>
</ArrayMember>
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="InputData" RPI="2000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1756_IB16IF:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<ArrayMember Name="LocalClockOffset" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="99117716" />
<Element Index="[1]" Value="409482" />
</ArrayMember>
<ArrayMember Name="OffsetTimestamp" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="198434448" />
<Element Index="[1]" Value="409893" />
</ArrayMember>
<ArrayMember Name="GrandMasterClockID" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="-6546176" />
<Element Index="[1]" Value="320265470" />
</ArrayMember>
<ArrayMember Name="Pt" DataType="AB:1756_IB16IF_Struct:I:0" Dimensions="16">
<Element Index="[0]">
<Structure DataType="AB:1756_IB16IF_Struct:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="NewDataOffOn" DataType="BOOL" Value="1" />
<DataValueMember Name="NewDataOnOff" DataType="BOOL" Value="1" />
<DataValueMember Name="TimestampDropped" DataType="BOOL" Value="1" />
<DataValueMember Name="CIPSyncValid" DataType="BOOL" Value="1" />
<DataValueMember Name="CIPSyncTimeout" DataType="BOOL" Value="0" />
<DataValueMember Name="InputOverrideStatus" DataType="BOOL" Value="0" />
<StructureMember Name="Timestamp" DataType="AB:1756_IB16IF_TimeStruct:I:0">
<ArrayMember Name="OffOn" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="196448114" />
<Element Index="[1]" Value="409893" />
</ArrayMember>
<ArrayMember Name="OnOff" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="196718385" />
<Element Index="[1]" Value="409893" />
</ArrayMember>
</StructureMember>
</Structure>
</Element>
<Element Index="[1]">
<Structure DataType="AB:1756_IB16IF_Struct:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="NewDataOffOn" DataType="BOOL" Value="1" />
<DataValueMember Name="NewDataOnOff" DataType="BOOL" Value="1" />
<DataValueMember Name="TimestampDropped" DataType="BOOL" Value="1" />
<DataValueMember Name="CIPSyncValid" DataType="BOOL" Value="1" />
<DataValueMember Name="CIPSyncTimeout" DataType="BOOL" Value="0" />
<DataValueMember Name="InputOverrideStatus" DataType="BOOL" Value="0" />
<StructureMember Name="Timestamp" DataType="AB:1756_IB16IF_TimeStruct:I:0">
<ArrayMember Name="OffOn" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="196447703" />
<Element Index="[1]" Value="409893" />
</ArrayMember>
<ArrayMember Name="OnOff" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="196717233" />
<Element Index="[1]" Value="409893" />
</ArrayMember>
</StructureMember>
</Structure>
</Element>
<Element Index="[2]">
<Structure DataType="AB:1756_IB16IF_Struct:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="NewDataOffOn" DataType="BOOL" Value="1" />
<DataValueMember Name="NewDataOnOff" DataType="BOOL" Value="1" />
<DataValueMember Name="TimestampDropped" DataType="BOOL" Value="1" />
<DataValueMember Name="CIPSyncValid" DataType="BOOL" Value="1" />
<DataValueMember Name="CIPSyncTimeout" DataType="BOOL" Value="0" />
<DataValueMember Name="InputOverrideStatus" DataType="BOOL" Value="0" />
<StructureMember Name="Timestamp" DataType="AB:1756_IB16IF_TimeStruct:I:0">
<ArrayMember Name="OffOn" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="196443754" />
<Element Index="[1]" Value="409893" />
</ArrayMember>
<ArrayMember Name="OnOff" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="196713497" />
<Element Index="[1]" Value="409893" />
</ArrayMember>
</StructureMember>
</Structure>
</Element>
<Element Index="[3]">
<Structure DataType="AB:1756_IB16IF_Struct:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="NewDataOffOn" DataType="BOOL" Value="1" />
<DataValueMember Name="NewDataOnOff" DataType="BOOL" Value="1" />
<DataValueMember Name="TimestampDropped" DataType="BOOL" Value="1" />
<DataValueMember Name="CIPSyncValid" DataType="BOOL" Value="1" />
<DataValueMember Name="CIPSyncTimeout" DataType="BOOL" Value="0" />
<DataValueMember Name="InputOverrideStatus" DataType="BOOL" Value="0" />
<StructureMember Name="Timestamp" DataType="AB:1756_IB16IF_TimeStruct:I:0">
<ArrayMember Name="OffOn" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="196446103" />
<Element Index="[1]" Value="409893" />
</ArrayMember>
<ArrayMember Name="OnOff" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="196714400" />
<Element Index="[1]" Value="409893" />
</ArrayMember>
</StructureMember>
</Structure>
</Element>
<Element Index="[4]">
<Structure DataType="AB:1756_IB16IF_Struct:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="NewDataOffOn" DataType="BOOL" Value="1" />
<DataValueMember Name="NewDataOnOff" DataType="BOOL" Value="1" />
<DataValueMember Name="TimestampDropped" DataType="BOOL" Value="1" />
<DataValueMember Name="CIPSyncValid" DataType="BOOL" Value="1" />
<DataValueMember Name="CIPSyncTimeout" DataType="BOOL" Value="0" />
<DataValueMember Name="InputOverrideStatus" DataType="BOOL" Value="0" />
<StructureMember Name="Timestamp" DataType="AB:1756_IB16IF_TimeStruct:I:0">
<ArrayMember Name="OffOn" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="196445818" />
<Element Index="[1]" Value="409893" />
</ArrayMember>
<ArrayMember Name="OnOff" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="196715903" />
<Element Index="[1]" Value="409893" />
</ArrayMember>
</StructureMember>
</Structure>
</Element>
<Element Index="[5]">
<Structure DataType="AB:1756_IB16IF_Struct:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="NewDataOffOn" DataType="BOOL" Value="1" />
<DataValueMember Name="NewDataOnOff" DataType="BOOL" Value="1" />
<DataValueMember Name="TimestampDropped" DataType="BOOL" Value="1" />
<DataValueMember Name="CIPSyncValid" DataType="BOOL" Value="1" />
<DataValueMember Name="CIPSyncTimeout" DataType="BOOL" Value="0" />
<DataValueMember Name="InputOverrideStatus" DataType="BOOL" Value="0" />
<StructureMember Name="Timestamp" DataType="AB:1756_IB16IF_TimeStruct:I:0">
<ArrayMember Name="OffOn" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="196442215" />
<Element Index="[1]" Value="409893" />
</ArrayMember>
<ArrayMember Name="OnOff" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="196712486" />
<Element Index="[1]" Value="409893" />
</ArrayMember>
</StructureMember>
</Structure>
</Element>
<Element Index="[6]">
<Structure DataType="AB:1756_IB16IF_Struct:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="NewDataOffOn" DataType="BOOL" Value="1" />
<DataValueMember Name="NewDataOnOff" DataType="BOOL" Value="1" />
<DataValueMember Name="TimestampDropped" DataType="BOOL" Value="1" />
<DataValueMember Name="CIPSyncValid" DataType="BOOL" Value="1" />
<DataValueMember Name="CIPSyncTimeout" DataType="BOOL" Value="0" />
<DataValueMember Name="InputOverrideStatus" DataType="BOOL" Value="0" />
<StructureMember Name="Timestamp" DataType="AB:1756_IB16IF_TimeStruct:I:0">
<ArrayMember Name="OffOn" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="196441634" />
<Element Index="[1]" Value="409893" />
</ArrayMember>
<ArrayMember Name="OnOff" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="196712348" />
<Element Index="[1]" Value="409893" />
</ArrayMember>
</StructureMember>
</Structure>
</Element>
<Element Index="[7]">
<Structure DataType="AB:1756_IB16IF_Struct:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="NewDataOffOn" DataType="BOOL" Value="1" />
<DataValueMember Name="NewDataOnOff" DataType="BOOL" Value="1" />
<DataValueMember Name="TimestampDropped" DataType="BOOL" Value="1" />
<DataValueMember Name="CIPSyncValid" DataType="BOOL" Value="1" />
<DataValueMember Name="CIPSyncTimeout" DataType="BOOL" Value="0" />
<DataValueMember Name="InputOverrideStatus" DataType="BOOL" Value="0" />
<StructureMember Name="Timestamp" DataType="AB:1756_IB16IF_TimeStruct:I:0">
<ArrayMember Name="OffOn" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="196441801" />
<Element Index="[1]" Value="409893" />
</ArrayMember>
<ArrayMember Name="OnOff" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="196711342" />
<Element Index="[1]" Value="409893" />
</ArrayMember>
</StructureMember>
</Structure>
</Element>
<Element Index="[8]">
<Structure DataType="AB:1756_IB16IF_Struct:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="NewDataOffOn" DataType="BOOL" Value="1" />
<DataValueMember Name="NewDataOnOff" DataType="BOOL" Value="1" />
<DataValueMember Name="TimestampDropped" DataType="BOOL" Value="1" />
<DataValueMember Name="CIPSyncValid" DataType="BOOL" Value="1" />
<DataValueMember Name="CIPSyncTimeout" DataType="BOOL" Value="0" />
<DataValueMember Name="InputOverrideStatus" DataType="BOOL" Value="0" />
<StructureMember Name="Timestamp" DataType="AB:1756_IB16IF_TimeStruct:I:0">
<ArrayMember Name="OffOn" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="196438224" />
<Element Index="[1]" Value="409893" />
</ArrayMember>
<ArrayMember Name="OnOff" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="196709665" />
<Element Index="[1]" Value="409893" />
</ArrayMember>
</StructureMember>
</Structure>
</Element>
<Element Index="[9]">
<Structure DataType="AB:1756_IB16IF_Struct:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="NewDataOffOn" DataType="BOOL" Value="1" />
<DataValueMember Name="NewDataOnOff" DataType="BOOL" Value="1" />
<DataValueMember Name="TimestampDropped" DataType="BOOL" Value="1" />
<DataValueMember Name="CIPSyncValid" DataType="BOOL" Value="1" />
<DataValueMember Name="CIPSyncTimeout" DataType="BOOL" Value="0" />
<DataValueMember Name="InputOverrideStatus" DataType="BOOL" Value="0" />
<StructureMember Name="Timestamp" DataType="AB:1756_IB16IF_TimeStruct:I:0">
<ArrayMember Name="OffOn" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="196437838" />
<Element Index="[1]" Value="409893" />
</ArrayMember>
<ArrayMember Name="OnOff" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="196707573" />
<Element Index="[1]" Value="409893" />
</ArrayMember>
</StructureMember>
</Structure>
</Element>
<Element Index="[10]">
<Structure DataType="AB:1756_IB16IF_Struct:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="NewDataOffOn" DataType="BOOL" Value="1" />
<DataValueMember Name="NewDataOnOff" DataType="BOOL" Value="1" />
<DataValueMember Name="TimestampDropped" DataType="BOOL" Value="1" />
<DataValueMember Name="CIPSyncValid" DataType="BOOL" Value="1" />
<DataValueMember Name="CIPSyncTimeout" DataType="BOOL" Value="0" />
<DataValueMember Name="InputOverrideStatus" DataType="BOOL" Value="0" />
<StructureMember Name="Timestamp" DataType="AB:1756_IB16IF_TimeStruct:I:0">
<ArrayMember Name="OffOn" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="196434447" />
<Element Index="[1]" Value="409893" />
</ArrayMember>
<ArrayMember Name="OnOff" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="196706169" />
<Element Index="[1]" Value="409893" />
</ArrayMember>
</StructureMember>
</Structure>
</Element>
<Element Index="[11]">
<Structure DataType="AB:1756_IB16IF_Struct:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="NewDataOffOn" DataType="BOOL" Value="1" />
<DataValueMember Name="NewDataOnOff" DataType="BOOL" Value="1" />
<DataValueMember Name="TimestampDropped" DataType="BOOL" Value="1" />
<DataValueMember Name="CIPSyncValid" DataType="BOOL" Value="1" />
<DataValueMember Name="CIPSyncTimeout" DataType="BOOL" Value="0" />
<DataValueMember Name="InputOverrideStatus" DataType="BOOL" Value="0" />
<StructureMember Name="Timestamp" DataType="AB:1756_IB16IF_TimeStruct:I:0">
<ArrayMember Name="OffOn" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="196433429" />
<Element Index="[1]" Value="409893" />
</ArrayMember>
<ArrayMember Name="OnOff" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="196703771" />
<Element Index="[1]" Value="409893" />
</ArrayMember>
</StructureMember>
</Structure>
</Element>
<Element Index="[12]">
<Structure DataType="AB:1756_IB16IF_Struct:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="NewDataOffOn" DataType="BOOL" Value="1" />
<DataValueMember Name="NewDataOnOff" DataType="BOOL" Value="1" />
<DataValueMember Name="TimestampDropped" DataType="BOOL" Value="1" />
<DataValueMember Name="CIPSyncValid" DataType="BOOL" Value="1" />
<DataValueMember Name="CIPSyncTimeout" DataType="BOOL" Value="0" />
<DataValueMember Name="InputOverrideStatus" DataType="BOOL" Value="0" />
<StructureMember Name="Timestamp" DataType="AB:1756_IB16IF_TimeStruct:I:0">
<ArrayMember Name="OffOn" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="196430617" />
<Element Index="[1]" Value="409893" />
</ArrayMember>
<ArrayMember Name="OnOff" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="196701649" />
<Element Index="[1]" Value="409893" />
</ArrayMember>
</StructureMember>
</Structure>
</Element>
<Element Index="[13]">
<Structure DataType="AB:1756_IB16IF_Struct:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="NewDataOffOn" DataType="BOOL" Value="1" />
<DataValueMember Name="NewDataOnOff" DataType="BOOL" Value="1" />
<DataValueMember Name="TimestampDropped" DataType="BOOL" Value="1" />
<DataValueMember Name="CIPSyncValid" DataType="BOOL" Value="1" />
<DataValueMember Name="CIPSyncTimeout" DataType="BOOL" Value="0" />
<DataValueMember Name="InputOverrideStatus" DataType="BOOL" Value="0" />
<StructureMember Name="Timestamp" DataType="AB:1756_IB16IF_TimeStruct:I:0">
<ArrayMember Name="OffOn" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="196429582" />
<Element Index="[1]" Value="409893" />
</ArrayMember>
<ArrayMember Name="OnOff" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="196699090" />
<Element Index="[1]" Value="409893" />
</ArrayMember>
</StructureMember>
</Structure>
</Element>
<Element Index="[14]">
<Structure DataType="AB:1756_IB16IF_Struct:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="NewDataOffOn" DataType="BOOL" Value="1" />
<DataValueMember Name="NewDataOnOff" DataType="BOOL" Value="1" />
<DataValueMember Name="TimestampDropped" DataType="BOOL" Value="1" />
<DataValueMember Name="CIPSyncValid" DataType="BOOL" Value="1" />
<DataValueMember Name="CIPSyncTimeout" DataType="BOOL" Value="0" />
<DataValueMember Name="InputOverrideStatus" DataType="BOOL" Value="0" />
<StructureMember Name="Timestamp" DataType="AB:1756_IB16IF_TimeStruct:I:0">
<ArrayMember Name="OffOn" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="196427091" />
<Element Index="[1]" Value="409893" />
</ArrayMember>
<ArrayMember Name="OnOff" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="196696671" />
<Element Index="[1]" Value="409893" />
</ArrayMember>
</StructureMember>
</Structure>
</Element>
<Element Index="[15]">
<Structure DataType="AB:1756_IB16IF_Struct:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="NewDataOffOn" DataType="BOOL" Value="1" />
<DataValueMember Name="NewDataOnOff" DataType="BOOL" Value="1" />
<DataValueMember Name="TimestampDropped" DataType="BOOL" Value="1" />
<DataValueMember Name="CIPSyncValid" DataType="BOOL" Value="1" />
<DataValueMember Name="CIPSyncTimeout" DataType="BOOL" Value="0" />
<DataValueMember Name="InputOverrideStatus" DataType="BOOL" Value="0" />
<StructureMember Name="Timestamp" DataType="AB:1756_IB16IF_TimeStruct:I:0">
<ArrayMember Name="OffOn" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="196424803" />
<Element Index="[1]" Value="409893" />
</ArrayMember>
<ArrayMember Name="OnOff" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="196695006" />
<Element Index="[1]" Value="409893" />
</ArrayMember>
</StructureMember>
</Structure>
</Element>
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[0,[[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0]]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1756_IB16IF:O:0">
<DataValueMember Name="ResetTimestamps" DataType="BOOL" Value="0" />
<ArrayMember Name="Pt" DataType="AB:1756_IB16IF_OPtStruct:O:0" Dimensions="16">
<Element Index="[0]">
<Structure DataType="AB:1756_IB16IF_OPtStruct:O:0">
<DataValueMember Name="NewDataOffOnAck" DataType="BOOL" Value="0" />
<DataValueMember Name="NewDataOnOffAck" DataType="BOOL" Value="0" />
<DataValueMember Name="DataOverrideEn" DataType="BOOL" Value="0" />
<DataValueMember Name="DataOverrideValue" DataType="BOOL" Value="0" />
</Structure>
</Element>
<Element Index="[1]">
<Structure DataType="AB:1756_IB16IF_OPtStruct:O:0">
<DataValueMember Name="NewDataOffOnAck" DataType="BOOL" Value="0" />
<DataValueMember Name="NewDataOnOffAck" DataType="BOOL" Value="0" />
<DataValueMember Name="DataOverrideEn" DataType="BOOL" Value="0" />
<DataValueMember Name="DataOverrideValue" DataType="BOOL" Value="0" />
</Structure>
</Element>
<Element Index="[2]">
<Structure DataType="AB:1756_IB16IF_OPtStruct:O:0">
<DataValueMember Name="NewDataOffOnAck" DataType="BOOL" Value="0" />
<DataValueMember Name="NewDataOnOffAck" DataType="BOOL" Value="0" />
<DataValueMember Name="DataOverrideEn" DataType="BOOL" Value="0" />
<DataValueMember Name="DataOverrideValue" DataType="BOOL" Value="0" />
</Structure>
</Element>
<Element Index="[3]">
<Structure DataType="AB:1756_IB16IF_OPtStruct:O:0">
<DataValueMember Name="NewDataOffOnAck" DataType="BOOL" Value="0" />
<DataValueMember Name="NewDataOnOffAck" DataType="BOOL" Value="0" />
<DataValueMember Name="DataOverrideEn" DataType="BOOL" Value="0" />
<DataValueMember Name="DataOverrideValue" DataType="BOOL" Value="0" />
</Structure>
</Element>
<Element Index="[4]">
<Structure DataType="AB:1756_IB16IF_OPtStruct:O:0">
<DataValueMember Name="NewDataOffOnAck" DataType="BOOL" Value="0" />
<DataValueMember Name="NewDataOnOffAck" DataType="BOOL" Value="0" />
<DataValueMember Name="DataOverrideEn" DataType="BOOL" Value="0" />
<DataValueMember Name="DataOverrideValue" DataType="BOOL" Value="0" />
</Structure>
</Element>
<Element Index="[5]">
<Structure DataType="AB:1756_IB16IF_OPtStruct:O:0">
<DataValueMember Name="NewDataOffOnAck" DataType="BOOL" Value="0" />
<DataValueMember Name="NewDataOnOffAck" DataType="BOOL" Value="0" />
<DataValueMember Name="DataOverrideEn" DataType="BOOL" Value="0" />
<DataValueMember Name="DataOverrideValue" DataType="BOOL" Value="0" />
</Structure>
</Element>
<Element Index="[6]">
<Structure DataType="AB:1756_IB16IF_OPtStruct:O:0">
<DataValueMember Name="NewDataOffOnAck" DataType="BOOL" Value="0" />
<DataValueMember Name="NewDataOnOffAck" DataType="BOOL" Value="0" />
<DataValueMember Name="DataOverrideEn" DataType="BOOL" Value="0" />
<DataValueMember Name="DataOverrideValue" DataType="BOOL" Value="0" />
</Structure>
</Element>
<Element Index="[7]">
<Structure DataType="AB:1756_IB16IF_OPtStruct:O:0">
<DataValueMember Name="NewDataOffOnAck" DataType="BOOL" Value="0" />
<DataValueMember Name="NewDataOnOffAck" DataType="BOOL" Value="0" />
<DataValueMember Name="DataOverrideEn" DataType="BOOL" Value="0" />
<DataValueMember Name="DataOverrideValue" DataType="BOOL" Value="0" />
</Structure>
</Element>
<Element Index="[8]">
<Structure DataType="AB:1756_IB16IF_OPtStruct:O:0">
<DataValueMember Name="NewDataOffOnAck" DataType="BOOL" Value="0" />
<DataValueMember Name="NewDataOnOffAck" DataType="BOOL" Value="0" />
<DataValueMember Name="DataOverrideEn" DataType="BOOL" Value="0" />
<DataValueMember Name="DataOverrideValue" DataType="BOOL" Value="0" />
</Structure>
</Element>
<Element Index="[9]">
<Structure DataType="AB:1756_IB16IF_OPtStruct:O:0">
<DataValueMember Name="NewDataOffOnAck" DataType="BOOL" Value="0" />
<DataValueMember Name="NewDataOnOffAck" DataType="BOOL" Value="0" />
<DataValueMember Name="DataOverrideEn" DataType="BOOL" Value="0" />
<DataValueMember Name="DataOverrideValue" DataType="BOOL" Value="0" />
</Structure>
</Element>
<Element Index="[10]">
<Structure DataType="AB:1756_IB16IF_OPtStruct:O:0">
<DataValueMember Name="NewDataOffOnAck" DataType="BOOL" Value="0" />
<DataValueMember Name="NewDataOnOffAck" DataType="BOOL" Value="0" />
<DataValueMember Name="DataOverrideEn" DataType="BOOL" Value="0" />
<DataValueMember Name="DataOverrideValue" DataType="BOOL" Value="0" />
</Structure>
</Element>
<Element Index="[11]">
<Structure DataType="AB:1756_IB16IF_OPtStruct:O:0">
<DataValueMember Name="NewDataOffOnAck" DataType="BOOL" Value="0" />
<DataValueMember Name="NewDataOnOffAck" DataType="BOOL" Value="0" />
<DataValueMember Name="DataOverrideEn" DataType="BOOL" Value="0" />
<DataValueMember Name="DataOverrideValue" DataType="BOOL" Value="0" />
</Structure>
</Element>
<Element Index="[12]">
<Structure DataType="AB:1756_IB16IF_OPtStruct:O:0">
<DataValueMember Name="NewDataOffOnAck" DataType="BOOL" Value="0" />
<DataValueMember Name="NewDataOnOffAck" DataType="BOOL" Value="0" />
<DataValueMember Name="DataOverrideEn" DataType="BOOL" Value="0" />
<DataValueMember Name="DataOverrideValue" DataType="BOOL" Value="0" />
</Structure>
</Element>
<Element Index="[13]">
<Structure DataType="AB:1756_IB16IF_OPtStruct:O:0">
<DataValueMember Name="NewDataOffOnAck" DataType="BOOL" Value="0" />
<DataValueMember Name="NewDataOnOffAck" DataType="BOOL" Value="0" />
<DataValueMember Name="DataOverrideEn" DataType="BOOL" Value="0" />
<DataValueMember Name="DataOverrideValue" DataType="BOOL" Value="0" />
</Structure>
</Element>
<Element Index="[14]">
<Structure DataType="AB:1756_IB16IF_OPtStruct:O:0">
<DataValueMember Name="NewDataOffOnAck" DataType="BOOL" Value="0" />
<DataValueMember Name="NewDataOnOffAck" DataType="BOOL" Value="0" />
<DataValueMember Name="DataOverrideEn" DataType="BOOL" Value="0" />
<DataValueMember Name="DataOverrideValue" DataType="BOOL" Value="0" />
</Structure>
</Element>
<Element Index="[15]">
<Structure DataType="AB:1756_IB16IF_OPtStruct:O:0">
<DataValueMember Name="NewDataOffOnAck" DataType="BOOL" Value="0" />
<DataValueMember Name="NewDataOnOffAck" DataType="BOOL" Value="0" />
<DataValueMember Name="DataOverrideEn" DataType="BOOL" Value="0" />
<DataValueMember Name="DataOverrideValue" DataType="BOOL" Value="0" />
</Structure>
</Element>
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'L5X_Samples/CMU_2025_10_14r00.L5X', 1),
    '1756-IF8/A': ("""\
<Module Name="TestMod1_1756IF8A" CatalogNumber="1756-IF8/A" Vendor="1" ProductType="10" ProductCode="7" Major="1" Minor="5" ParentModule="Local" ParentModPortId="1" Inhibited="false" MajorFault="false" AutoDiagsEnabled="true">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="2" Type="ICP" Upstream="true" />
</Ports>
<Communications CommMethod="536870913">
<ConfigTag ConfigSize="196" ExternalAccess="Read/Write">
<Data Format="L5K">
[200,36,1,3,100,[64,3,0,0.00000000e+000,4.00000000e+000,2.00000000e+001,4.80000000e+001,0.00000000e+000
		,-1.00000000e+001,1.00000000e+001,-1.00000000e+001,1.00000000e+001,0.00000000e+000,0.00000000e+000
		],[0,3,0,0.00000000e+000,4.00000000e+000,2.00000000e+001,4.00000000e+000,2.00000000e+001,-1.00000000e+001
		,1.00000000e+001,-1.00000000e+001,1.00000000e+001,0.00000000e+000,0.00000000e+000],[0,3,0,0.00000000e+000
		,0.00000000e+000,2.00000000e+001,0.00000000e+000,1.00000000e+002,-1.00000000e+001,1.00000000e+001
		,-1.00000000e+001,1.00000000e+001,0.00000000e+000,0.00000000e+000],[0,3,0,0.00000000e+000,0.00000000e+000
		,2.00000000e+001,0.00000000e+000,1.00000000e+002,-1.00000000e+001,1.00000000e+001,-1.00000000e+001
		,1.00000000e+001,0.00000000e+000,0.00000000e+000]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1756_IF4_Float:C:0">
<DataValueMember Name="ModuleFilter" DataType="SINT" Radix="Decimal" Value="3" />
<DataValueMember Name="RealTimeSample" DataType="INT" Radix="Decimal" Value="100" />
<StructureMember Name="Ch0Config" DataType="AB:1756_NII_Struct:C:0">
<DataValueMember Name="AlarmDisable" DataType="BOOL" Value="1" />
<DataValueMember Name="ProcessAlarmLatch" DataType="BOOL" Value="0" />
<DataValueMember Name="RateAlarmLatch" DataType="BOOL" Value="0" />
<DataValueMember Name="RangeType" DataType="SINT" Radix="Decimal" Value="3" />
<DataValueMember Name="DigitalFilter" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="RateAlarmLimit" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="LowSignal" DataType="REAL" Radix="Float" Value="4.0" />
<DataValueMember Name="HighSignal" DataType="REAL" Radix="Float" Value="20.0" />
<DataValueMember Name="LowEngineering" DataType="REAL" Radix="Float" Value="48.0" />
<DataValueMember Name="HighEngineering" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="LAlarmLimit" DataType="REAL" Radix="Float" Value="-10.0" />
<DataValueMember Name="HAlarmLimit" DataType="REAL" Radix="Float" Value="10.0" />
<DataValueMember Name="LLAlarmLimit" DataType="REAL" Radix="Float" Value="-10.0" />
<DataValueMember Name="HHAlarmLimit" DataType="REAL" Radix="Float" Value="10.0" />
<DataValueMember Name="AlarmDeadband" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="CalBias" DataType="REAL" Radix="Float" Value="0.0" />
</StructureMember>
<StructureMember Name="Ch1Config" DataType="AB:1756_NII_Struct:C:0">
<DataValueMember Name="AlarmDisable" DataType="BOOL" Value="0" />
<DataValueMember Name="ProcessAlarmLatch" DataType="BOOL" Value="0" />
<DataValueMember Name="RateAlarmLatch" DataType="BOOL" Value="0" />
<DataValueMember Name="RangeType" DataType="SINT" Radix="Decimal" Value="3" />
<DataValueMember Name="DigitalFilter" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="RateAlarmLimit" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="LowSignal" DataType="REAL" Radix="Float" Value="4.0" />
<DataValueMember Name="HighSignal" DataType="REAL" Radix="Float" Value="20.0" />
<DataValueMember Name="LowEngineering" DataType="REAL" Radix="Float" Value="4.0" />
<DataValueMember Name="HighEngineering" DataType="REAL" Radix="Float" Value="20.0" />
<DataValueMember Name="LAlarmLimit" DataType="REAL" Radix="Float" Value="-10.0" />
<DataValueMember Name="HAlarmLimit" DataType="REAL" Radix="Float" Value="10.0" />
<DataValueMember Name="LLAlarmLimit" DataType="REAL" Radix="Float" Value="-10.0" />
<DataValueMember Name="HHAlarmLimit" DataType="REAL" Radix="Float" Value="10.0" />
<DataValueMember Name="AlarmDeadband" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="CalBias" DataType="REAL" Radix="Float" Value="0.0" />
</StructureMember>
<StructureMember Name="Ch2Config" DataType="AB:1756_NII_Struct:C:0">
<DataValueMember Name="AlarmDisable" DataType="BOOL" Value="0" />
<DataValueMember Name="ProcessAlarmLatch" DataType="BOOL" Value="0" />
<DataValueMember Name="RateAlarmLatch" DataType="BOOL" Value="0" />
<DataValueMember Name="RangeType" DataType="SINT" Radix="Decimal" Value="3" />
<DataValueMember Name="DigitalFilter" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="RateAlarmLimit" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="LowSignal" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="HighSignal" DataType="REAL" Radix="Float" Value="20.0" />
<DataValueMember Name="LowEngineering" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="HighEngineering" DataType="REAL" Radix="Float" Value="100.0" />
<DataValueMember Name="LAlarmLimit" DataType="REAL" Radix="Float" Value="-10.0" />
<DataValueMember Name="HAlarmLimit" DataType="REAL" Radix="Float" Value="10.0" />
<DataValueMember Name="LLAlarmLimit" DataType="REAL" Radix="Float" Value="-10.0" />
<DataValueMember Name="HHAlarmLimit" DataType="REAL" Radix="Float" Value="10.0" />
<DataValueMember Name="AlarmDeadband" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="CalBias" DataType="REAL" Radix="Float" Value="0.0" />
</StructureMember>
<StructureMember Name="Ch3Config" DataType="AB:1756_NII_Struct:C:0">
<DataValueMember Name="AlarmDisable" DataType="BOOL" Value="0" />
<DataValueMember Name="ProcessAlarmLatch" DataType="BOOL" Value="0" />
<DataValueMember Name="RateAlarmLatch" DataType="BOOL" Value="0" />
<DataValueMember Name="RangeType" DataType="SINT" Radix="Decimal" Value="3" />
<DataValueMember Name="DigitalFilter" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="RateAlarmLimit" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="LowSignal" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="HighSignal" DataType="REAL" Radix="Float" Value="20.0" />
<DataValueMember Name="LowEngineering" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="HighEngineering" DataType="REAL" Radix="Float" Value="100.0" />
<DataValueMember Name="LAlarmLimit" DataType="REAL" Radix="Float" Value="-10.0" />
<DataValueMember Name="HAlarmLimit" DataType="REAL" Radix="Float" Value="10.0" />
<DataValueMember Name="LLAlarmLimit" DataType="REAL" Radix="Float" Value="-10.0" />
<DataValueMember Name="HHAlarmLimit" DataType="REAL" Radix="Float" Value="10.0" />
<DataValueMember Name="AlarmDeadband" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="CalBias" DataType="REAL" Radix="Float" Value="0.0" />
</StructureMember>
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="Input" RPI="100000" Type="Input" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="false">
<InputTag ExternalAccess="Read/Write">
<EngineeringUnits>
<EngineeringUnit Operand=".CH0DATA">
po
</EngineeringUnit>
<EngineeringUnit Operand=".CH1DATA">
mPo
</EngineeringUnit>
<EngineeringUnit Operand=".CH2DATA">
mPo
</EngineeringUnit>
<EngineeringUnit Operand=".CH3DATA">
mPo
</EngineeringUnit>
</EngineeringUnits>
<Data Format="Decorated">
<Structure DataType="AB:1756_IF4_Float:I:0">
<DataValueMember Name="ChannelFaults" DataType="INT" Radix="Binary" Value="2#0000_0000_0000_1110" />
<DataValueMember Name="Ch0Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1Fault" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch2Fault" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch3Fault" DataType="BOOL" Value="1" />
<DataValueMember Name="ModuleFaults" DataType="INT" Radix="Binary" Value="2#1000_0010_0000_0000" />
<DataValueMember Name="AnalogGroupFault" DataType="BOOL" Value="1" />
<DataValueMember Name="Calibrating" DataType="BOOL" Value="0" />
<DataValueMember Name="CalFault" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch0Status" DataType="SINT" Radix="Binary" Value="2#1000_0000" />
<DataValueMember Name="Ch0CalFault" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch0Underrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0Overrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0RateAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0LAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0HAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0LLAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0HHAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1Status" DataType="SINT" Radix="Binary" Value="2#1100_0000" />
<DataValueMember Name="Ch1CalFault" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch1Underrange" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch1Overrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1RateAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1LAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1HAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1LLAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1HHAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch2Status" DataType="SINT" Radix="Binary" Value="2#1100_0000" />
<DataValueMember Name="Ch2CalFault" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch2Underrange" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch2Overrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch2RateAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch2LAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch2HAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch2LLAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch2HHAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch3Status" DataType="SINT" Radix="Binary" Value="2#1100_0000" />
<DataValueMember Name="Ch3CalFault" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch3Underrange" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch3Overrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch3RateAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch3LAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch3HAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch3LLAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch3HHAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0Data" DataType="REAL" Radix="Float" Value="47.9832" />
<DataValueMember Name="Ch1Data" DataType="REAL" Radix="Float" Value="0.003455162" />
<DataValueMember Name="Ch2Data" DataType="REAL" Radix="Float" Value="6.28280640e-003" />
<DataValueMember Name="Ch3Data" DataType="REAL" Radix="Float" Value="0.020412445" />
<DataValueMember Name="RollingTimestamp" DataType="INT" Radix="Decimal" Value="29018" />
</Structure>
</Data>
</InputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'BAI10048_TrimmerTally_20250704.L5X', 1),
    '1756-OA16': ("""\
<Module Name="TestMod1_1756OA16" CatalogNumber="1756-OA16" Vendor="1" ProductType="7" ProductCode="13" Major="2" Minor="3" ParentModule="Local" ParentModPortId="1" Inhibited="false" MajorFault="false" AutoDiagsEnabled="true">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="15" Type="ICP" Upstream="true" />
</Ports>
<Communications CommMethod="536870914">
<ConfigTag ConfigSize="24" ExternalAccess="Read/Write">
<Data Format="L5K">
[28,18,1,0,0,0,0,0,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1756_DO:C:0">
<DataValueMember Name="ProgToFaultEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultMode" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="FaultValue" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="ProgMode" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="ProgValue" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="Fused" RPI="10000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1756_DO_Fused:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<ArrayMember Name="CSTTimestamp" DataType="DINT" Dimensions="2" Radix="Decimal">
<Element Index="[0]" Value="0" />
<Element Index="[1]" Value="-2147483648" />
</ArrayMember>
<DataValueMember Name="FuseBlown" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1756_DO:O:0">
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'L5X_Samples/RobbinsGrn_2026_05_13r00.L5X', 1),
    '1756-OA16I': ("""\
<Module Name="TestMod1_1756OA16I" CatalogNumber="1756-OA16I" Vendor="1" ProductType="7" ProductCode="7" Major="3" Minor="2" ParentModule="Local" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="12" Type="ICP" Upstream="true" />
</Ports>
<Communications CommMethod="536870913">
<ConfigTag ConfigSize="24" ExternalAccess="Read/Write">
<Data Format="L5K">
[28,18,0,0,0,0,0,0,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1756_DO:C:0">
<DataValueMember Name="ProgToFaultEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultMode" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="FaultValue" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="ProgMode" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="ProgValue" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="Standard" RPI="20000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1756_DO:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0100" />
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[4]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1756_DO:O:0">
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0100" />
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'BAI10048_TrimmerTally_20250704.L5X', 1),
    '1756-OF4/A': ("""\
<Module Name="TestMod1_1756OF4A" CatalogNumber="1756-OF4/A" Vendor="1" ProductType="10" ProductCode="8" Major="1" Minor="5" ParentModule="Local" ParentModPortId="1" Inhibited="false" MajorFault="false" AutoDiagsEnabled="true">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="10" Type="ICP" Upstream="true" />
</Ports>
<Communications CommMethod="536870913">
<ConfigTag ConfigSize="180" ExternalAccess="Read/Write">
<Data Format="L5K">
[184,36,1,0,0,[0,0,0.00000000e+000,0.00000000e+000,0.00000000e+000,-1.00000000e+001,1.00000000e+001
		,-1.00000000e+001,1.00000000e+001,-1.00000000e+001,1.00000000e+001,0.00000000e+000],[0,0,0.00000000e+000
		,0.00000000e+000,0.00000000e+000,-1.00000000e+001,1.00000000e+001,-1.00000000e+001,1.00000000e+001
		,-1.00000000e+001,1.00000000e+001,0.00000000e+000],[0,0,0.00000000e+000,0.00000000e+000,0.00000000e+000
		,-1.00000000e+001,1.00000000e+001,-1.00000000e+001,1.00000000e+001,-1.00000000e+001,1.00000000e+001
		,0.00000000e+000],[0,0,0.00000000e+000,0.00000000e+000,0.00000000e+000,-1.00000000e+001,1.00000000e+001
		,-1.00000000e+001,1.00000000e+001,-1.00000000e+001,1.00000000e+001,0.00000000e+000]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1756_OF4_Float:C:0">
<DataValueMember Name="ProgToFaultEn" DataType="BOOL" Value="0" />
<StructureMember Name="Ch0Config" DataType="AB:1756_NIO_Struct:C:0">
<DataValueMember Name="HoldForInit" DataType="BOOL" Value="0" />
<DataValueMember Name="AlarmDisable" DataType="BOOL" Value="0" />
<DataValueMember Name="RampAlarmLatch" DataType="BOOL" Value="0" />
<DataValueMember Name="LimitAlarmLatch" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="RampToRun" DataType="BOOL" Value="0" />
<DataValueMember Name="RampToProg" DataType="BOOL" Value="0" />
<DataValueMember Name="RampToFault" DataType="BOOL" Value="0" />
<DataValueMember Name="RangeType" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaxRampRate" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="FaultValue" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="ProgValue" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="LowSignal" DataType="REAL" Radix="Float" Value="-10.0" />
<DataValueMember Name="HighSignal" DataType="REAL" Radix="Float" Value="10.0" />
<DataValueMember Name="LowEngineering" DataType="REAL" Radix="Float" Value="-10.0" />
<DataValueMember Name="HighEngineering" DataType="REAL" Radix="Float" Value="10.0" />
<DataValueMember Name="LowLimit" DataType="REAL" Radix="Float" Value="-10.0" />
<DataValueMember Name="HighLimit" DataType="REAL" Radix="Float" Value="10.0" />
<DataValueMember Name="CalBias" DataType="REAL" Radix="Float" Value="0.0" />
</StructureMember>
<StructureMember Name="Ch1Config" DataType="AB:1756_NIO_Struct:C:0">
<DataValueMember Name="HoldForInit" DataType="BOOL" Value="0" />
<DataValueMember Name="AlarmDisable" DataType="BOOL" Value="0" />
<DataValueMember Name="RampAlarmLatch" DataType="BOOL" Value="0" />
<DataValueMember Name="LimitAlarmLatch" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="RampToRun" DataType="BOOL" Value="0" />
<DataValueMember Name="RampToProg" DataType="BOOL" Value="0" />
<DataValueMember Name="RampToFault" DataType="BOOL" Value="0" />
<DataValueMember Name="RangeType" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaxRampRate" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="FaultValue" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="ProgValue" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="LowSignal" DataType="REAL" Radix="Float" Value="-10.0" />
<DataValueMember Name="HighSignal" DataType="REAL" Radix="Float" Value="10.0" />
<DataValueMember Name="LowEngineering" DataType="REAL" Radix="Float" Value="-10.0" />
<DataValueMember Name="HighEngineering" DataType="REAL" Radix="Float" Value="10.0" />
<DataValueMember Name="LowLimit" DataType="REAL" Radix="Float" Value="-10.0" />
<DataValueMember Name="HighLimit" DataType="REAL" Radix="Float" Value="10.0" />
<DataValueMember Name="CalBias" DataType="REAL" Radix="Float" Value="0.0" />
</StructureMember>
<StructureMember Name="Ch2Config" DataType="AB:1756_NIO_Struct:C:0">
<DataValueMember Name="HoldForInit" DataType="BOOL" Value="0" />
<DataValueMember Name="AlarmDisable" DataType="BOOL" Value="0" />
<DataValueMember Name="RampAlarmLatch" DataType="BOOL" Value="0" />
<DataValueMember Name="LimitAlarmLatch" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="RampToRun" DataType="BOOL" Value="0" />
<DataValueMember Name="RampToProg" DataType="BOOL" Value="0" />
<DataValueMember Name="RampToFault" DataType="BOOL" Value="0" />
<DataValueMember Name="RangeType" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaxRampRate" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="FaultValue" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="ProgValue" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="LowSignal" DataType="REAL" Radix="Float" Value="-10.0" />
<DataValueMember Name="HighSignal" DataType="REAL" Radix="Float" Value="10.0" />
<DataValueMember Name="LowEngineering" DataType="REAL" Radix="Float" Value="-10.0" />
<DataValueMember Name="HighEngineering" DataType="REAL" Radix="Float" Value="10.0" />
<DataValueMember Name="LowLimit" DataType="REAL" Radix="Float" Value="-10.0" />
<DataValueMember Name="HighLimit" DataType="REAL" Radix="Float" Value="10.0" />
<DataValueMember Name="CalBias" DataType="REAL" Radix="Float" Value="0.0" />
</StructureMember>
<StructureMember Name="Ch3Config" DataType="AB:1756_NIO_Struct:C:0">
<DataValueMember Name="HoldForInit" DataType="BOOL" Value="0" />
<DataValueMember Name="AlarmDisable" DataType="BOOL" Value="0" />
<DataValueMember Name="RampAlarmLatch" DataType="BOOL" Value="0" />
<DataValueMember Name="LimitAlarmLatch" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="RampToRun" DataType="BOOL" Value="0" />
<DataValueMember Name="RampToProg" DataType="BOOL" Value="0" />
<DataValueMember Name="RampToFault" DataType="BOOL" Value="0" />
<DataValueMember Name="RangeType" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaxRampRate" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="FaultValue" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="ProgValue" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="LowSignal" DataType="REAL" Radix="Float" Value="-10.0" />
<DataValueMember Name="HighSignal" DataType="REAL" Radix="Float" Value="10.0" />
<DataValueMember Name="LowEngineering" DataType="REAL" Radix="Float" Value="-10.0" />
<DataValueMember Name="HighEngineering" DataType="REAL" Radix="Float" Value="10.0" />
<DataValueMember Name="LowLimit" DataType="REAL" Radix="Float" Value="-10.0" />
<DataValueMember Name="HighLimit" DataType="REAL" Radix="Float" Value="10.0" />
<DataValueMember Name="CalBias" DataType="REAL" Radix="Float" Value="0.0" />
</StructureMember>
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="Float" RPI="12000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1756_OF4_Float:I:0">
<DataValueMember Name="ChannelFaults" DataType="INT" Radix="Binary" Value="2#0000_0000_0000_0000" />
<DataValueMember Name="Ch0Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch2Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch3Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="ModuleFaults" DataType="INT" Radix="Binary" Value="2#0000_0000_0000_0000" />
<DataValueMember Name="AnalogGroupFault" DataType="BOOL" Value="0" />
<DataValueMember Name="Calibrating" DataType="BOOL" Value="0" />
<DataValueMember Name="CalFault" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0Status" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Ch0OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0NotANumber" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0CalFault" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0InHold" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0RampAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0LLimitAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0HLimitAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1Status" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Ch1OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1NotANumber" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1CalFault" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1InHold" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1RampAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1LLimitAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1HLimitAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch2Status" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Ch2OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch2NotANumber" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch2CalFault" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch2InHold" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch2RampAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch2LLimitAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch2HLimitAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch3Status" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Ch3OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch3NotANumber" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch3CalFault" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch3InHold" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch3RampAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch3LLimitAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch3HLimitAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0Data" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="Ch1Data" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="Ch2Data" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="Ch3Data" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="RollingTimestamp" DataType="INT" Radix="Decimal" Value="19396" />
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[0.00000000e+000,0.00000000e+000,0.00000000e+000,0.00000000e+000]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1756_OF4_Float:O:0">
<DataValueMember Name="Ch0Data" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="Ch1Data" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="Ch2Data" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="Ch3Data" DataType="REAL" Radix="Float" Value="0.0" />
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'L5X_Samples/RobbinsGrn_2026_05_13r00.L5X', 1),
    '1756-OF8/B': ("""\
<Module CatalogNumber="1756-OF8/B" Vendor="1" ProductType="10" ProductCode="9" Major="2" Minor="11" ParentModule="Local" ParentModPortId="1" Inhibited="false" MajorFault="false" AutoDiagsEnabled="true">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="3" Type="ICP" Upstream="true" />
</Ports>
<Communications CommMethod="536870913">
<ConfigTag ConfigSize="356" ExternalAccess="Read/Write">
<Data Format="L5K">
[360,34,0,0,0,[0,0,0.00000000e+000,0.00000000e+000,0.00000000e+000,0.00000000e+000,1.00000000e+001
		,0.00000000e+000,1.00000000e+004,0.00000000e+000,1.00000000e+002,0.00000000e+000],[0,0,0.00000000e+000
		,0.00000000e+000,0.00000000e+000,0.00000000e+000,1.00000000e+001,0.00000000e+000,1.00000000e+004
		,0.00000000e+000,1.00000000e+002,0.00000000e+000],[0,0,0.00000000e+000,0.00000000e+000,0.00000000e+000
		,0.00000000e+000,1.00000000e+001,0.00000000e+000,1.00000000e+004,0.00000000e+000,1.00000000e+002
		,0.00000000e+000],[0,0,0.00000000e+000,0.00000000e+000,0.00000000e+000,0.00000000e+000,1.00000000e+001
		,0.00000000e+000,1.00000000e+004,0.00000000e+000,1.00000000e+002,0.00000000e+000],[0,0,0.00000000e+000
		,0.00000000e+000,0.00000000e+000,0.00000000e+000,1.00000000e+001,0.00000000e+000,1.00000000e+004
		,0.00000000e+000,1.00000000e+002,0.00000000e+000],[0,0,0.00000000e+000,0.00000000e+000,0.00000000e+000
		,0.00000000e+000,1.00000000e+001,0.00000000e+000,1.00000000e+004,0.00000000e+000,1.00000000e+002
		,0.00000000e+000],[0,0,0.00000000e+000,0.00000000e+000,0.00000000e+000,0.00000000e+000,1.00000000e+001
		,0.00000000e+000,1.00000000e+004,0.00000000e+000,1.00000000e+002,0.00000000e+000],[0,0,0.00000000e+000
		,0.00000000e+000,0.00000000e+000,0.00000000e+000,1.00000000e+001,0.00000000e+000,1.00000000e+004
		,0.00000000e+000,1.00000000e+002,0.00000000e+000]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1756_OF8_Float:C:0">
<DataValueMember Name="ProgToFaultEn" DataType="BOOL" Value="0" />
<StructureMember Name="Ch0Config" DataType="AB:1756_NIO_Struct:C:0">
<DataValueMember Name="HoldForInit" DataType="BOOL" Value="0" />
<DataValueMember Name="AlarmDisable" DataType="BOOL" Value="0" />
<DataValueMember Name="RampAlarmLatch" DataType="BOOL" Value="0" />
<DataValueMember Name="LimitAlarmLatch" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="RampToRun" DataType="BOOL" Value="0" />
<DataValueMember Name="RampToProg" DataType="BOOL" Value="0" />
<DataValueMember Name="RampToFault" DataType="BOOL" Value="0" />
<DataValueMember Name="RangeType" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaxRampRate" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="FaultValue" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="ProgValue" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="LowSignal" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="HighSignal" DataType="REAL" Radix="Float" Value="10.0" />
<DataValueMember Name="LowEngineering" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="HighEngineering" DataType="REAL" Radix="Float" Value="10000.0" />
<DataValueMember Name="LowLimit" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="HighLimit" DataType="REAL" Radix="Float" Value="100.0" />
<DataValueMember Name="CalBias" DataType="REAL" Radix="Float" Value="0.0" />
</StructureMember>
<StructureMember Name="Ch1Config" DataType="AB:1756_NIO_Struct:C:0">
<DataValueMember Name="HoldForInit" DataType="BOOL" Value="0" />
<DataValueMember Name="AlarmDisable" DataType="BOOL" Value="0" />
<DataValueMember Name="RampAlarmLatch" DataType="BOOL" Value="0" />
<DataValueMember Name="LimitAlarmLatch" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="RampToRun" DataType="BOOL" Value="0" />
<DataValueMember Name="RampToProg" DataType="BOOL" Value="0" />
<DataValueMember Name="RampToFault" DataType="BOOL" Value="0" />
<DataValueMember Name="RangeType" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaxRampRate" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="FaultValue" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="ProgValue" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="LowSignal" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="HighSignal" DataType="REAL" Radix="Float" Value="10.0" />
<DataValueMember Name="LowEngineering" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="HighEngineering" DataType="REAL" Radix="Float" Value="10000.0" />
<DataValueMember Name="LowLimit" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="HighLimit" DataType="REAL" Radix="Float" Value="100.0" />
<DataValueMember Name="CalBias" DataType="REAL" Radix="Float" Value="0.0" />
</StructureMember>
<StructureMember Name="Ch2Config" DataType="AB:1756_NIO_Struct:C:0">
<DataValueMember Name="HoldForInit" DataType="BOOL" Value="0" />
<DataValueMember Name="AlarmDisable" DataType="BOOL" Value="0" />
<DataValueMember Name="RampAlarmLatch" DataType="BOOL" Value="0" />
<DataValueMember Name="LimitAlarmLatch" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="RampToRun" DataType="BOOL" Value="0" />
<DataValueMember Name="RampToProg" DataType="BOOL" Value="0" />
<DataValueMember Name="RampToFault" DataType="BOOL" Value="0" />
<DataValueMember Name="RangeType" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaxRampRate" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="FaultValue" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="ProgValue" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="LowSignal" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="HighSignal" DataType="REAL" Radix="Float" Value="10.0" />
<DataValueMember Name="LowEngineering" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="HighEngineering" DataType="REAL" Radix="Float" Value="10000.0" />
<DataValueMember Name="LowLimit" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="HighLimit" DataType="REAL" Radix="Float" Value="100.0" />
<DataValueMember Name="CalBias" DataType="REAL" Radix="Float" Value="0.0" />
</StructureMember>
<StructureMember Name="Ch3Config" DataType="AB:1756_NIO_Struct:C:0">
<DataValueMember Name="HoldForInit" DataType="BOOL" Value="0" />
<DataValueMember Name="AlarmDisable" DataType="BOOL" Value="0" />
<DataValueMember Name="RampAlarmLatch" DataType="BOOL" Value="0" />
<DataValueMember Name="LimitAlarmLatch" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="RampToRun" DataType="BOOL" Value="0" />
<DataValueMember Name="RampToProg" DataType="BOOL" Value="0" />
<DataValueMember Name="RampToFault" DataType="BOOL" Value="0" />
<DataValueMember Name="RangeType" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaxRampRate" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="FaultValue" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="ProgValue" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="LowSignal" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="HighSignal" DataType="REAL" Radix="Float" Value="10.0" />
<DataValueMember Name="LowEngineering" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="HighEngineering" DataType="REAL" Radix="Float" Value="10000.0" />
<DataValueMember Name="LowLimit" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="HighLimit" DataType="REAL" Radix="Float" Value="100.0" />
<DataValueMember Name="CalBias" DataType="REAL" Radix="Float" Value="0.0" />
</StructureMember>
<StructureMember Name="Ch4Config" DataType="AB:1756_NIO_Struct:C:0">
<DataValueMember Name="HoldForInit" DataType="BOOL" Value="0" />
<DataValueMember Name="AlarmDisable" DataType="BOOL" Value="0" />
<DataValueMember Name="RampAlarmLatch" DataType="BOOL" Value="0" />
<DataValueMember Name="LimitAlarmLatch" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="RampToRun" DataType="BOOL" Value="0" />
<DataValueMember Name="RampToProg" DataType="BOOL" Value="0" />
<DataValueMember Name="RampToFault" DataType="BOOL" Value="0" />
<DataValueMember Name="RangeType" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaxRampRate" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="FaultValue" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="ProgValue" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="LowSignal" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="HighSignal" DataType="REAL" Radix="Float" Value="10.0" />
<DataValueMember Name="LowEngineering" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="HighEngineering" DataType="REAL" Radix="Float" Value="10000.0" />
<DataValueMember Name="LowLimit" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="HighLimit" DataType="REAL" Radix="Float" Value="100.0" />
<DataValueMember Name="CalBias" DataType="REAL" Radix="Float" Value="0.0" />
</StructureMember>
<StructureMember Name="Ch5Config" DataType="AB:1756_NIO_Struct:C:0">
<DataValueMember Name="HoldForInit" DataType="BOOL" Value="0" />
<DataValueMember Name="AlarmDisable" DataType="BOOL" Value="0" />
<DataValueMember Name="RampAlarmLatch" DataType="BOOL" Value="0" />
<DataValueMember Name="LimitAlarmLatch" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="RampToRun" DataType="BOOL" Value="0" />
<DataValueMember Name="RampToProg" DataType="BOOL" Value="0" />
<DataValueMember Name="RampToFault" DataType="BOOL" Value="0" />
<DataValueMember Name="RangeType" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaxRampRate" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="FaultValue" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="ProgValue" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="LowSignal" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="HighSignal" DataType="REAL" Radix="Float" Value="10.0" />
<DataValueMember Name="LowEngineering" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="HighEngineering" DataType="REAL" Radix="Float" Value="10000.0" />
<DataValueMember Name="LowLimit" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="HighLimit" DataType="REAL" Radix="Float" Value="100.0" />
<DataValueMember Name="CalBias" DataType="REAL" Radix="Float" Value="0.0" />
</StructureMember>
<StructureMember Name="Ch6Config" DataType="AB:1756_NIO_Struct:C:0">
<DataValueMember Name="HoldForInit" DataType="BOOL" Value="0" />
<DataValueMember Name="AlarmDisable" DataType="BOOL" Value="0" />
<DataValueMember Name="RampAlarmLatch" DataType="BOOL" Value="0" />
<DataValueMember Name="LimitAlarmLatch" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="RampToRun" DataType="BOOL" Value="0" />
<DataValueMember Name="RampToProg" DataType="BOOL" Value="0" />
<DataValueMember Name="RampToFault" DataType="BOOL" Value="0" />
<DataValueMember Name="RangeType" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaxRampRate" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="FaultValue" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="ProgValue" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="LowSignal" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="HighSignal" DataType="REAL" Radix="Float" Value="10.0" />
<DataValueMember Name="LowEngineering" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="HighEngineering" DataType="REAL" Radix="Float" Value="10000.0" />
<DataValueMember Name="LowLimit" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="HighLimit" DataType="REAL" Radix="Float" Value="100.0" />
<DataValueMember Name="CalBias" DataType="REAL" Radix="Float" Value="0.0" />
</StructureMember>
<StructureMember Name="Ch7Config" DataType="AB:1756_NIO_Struct:C:0">
<DataValueMember Name="HoldForInit" DataType="BOOL" Value="0" />
<DataValueMember Name="AlarmDisable" DataType="BOOL" Value="0" />
<DataValueMember Name="RampAlarmLatch" DataType="BOOL" Value="0" />
<DataValueMember Name="LimitAlarmLatch" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="RampToRun" DataType="BOOL" Value="0" />
<DataValueMember Name="RampToProg" DataType="BOOL" Value="0" />
<DataValueMember Name="RampToFault" DataType="BOOL" Value="0" />
<DataValueMember Name="RangeType" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaxRampRate" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="FaultValue" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="ProgValue" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="LowSignal" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="HighSignal" DataType="REAL" Radix="Float" Value="10.0" />
<DataValueMember Name="LowEngineering" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="HighEngineering" DataType="REAL" Radix="Float" Value="10000.0" />
<DataValueMember Name="LowLimit" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="HighLimit" DataType="REAL" Radix="Float" Value="100.0" />
<DataValueMember Name="CalBias" DataType="REAL" Radix="Float" Value="0.0" />
</StructureMember>
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="Float" RPI="12000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1756_OF8_Float:I:0">
<DataValueMember Name="ChannelFaults" DataType="INT" Radix="Binary" Value="2#0000_0000_0000_0000" />
<DataValueMember Name="Ch0Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch2Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch3Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch4Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch5Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch6Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch7Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="ModuleFaults" DataType="INT" Radix="Binary" Value="2#0000_0000_0000_0000" />
<DataValueMember Name="AnalogGroupFault" DataType="BOOL" Value="0" />
<DataValueMember Name="Calibrating" DataType="BOOL" Value="0" />
<DataValueMember Name="CalFault" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0Status" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Ch0OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0NotANumber" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0CalFault" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0InHold" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0RampAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0LLimitAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0HLimitAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1Status" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Ch1OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1NotANumber" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1CalFault" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1InHold" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1RampAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1LLimitAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1HLimitAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch2Status" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Ch2OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch2NotANumber" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch2CalFault" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch2InHold" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch2RampAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch2LLimitAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch2HLimitAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch3Status" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Ch3OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch3NotANumber" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch3CalFault" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch3InHold" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch3RampAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch3LLimitAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch3HLimitAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch4Status" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Ch4OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch4NotANumber" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch4CalFault" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch4InHold" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch4RampAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch4LLimitAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch4HLimitAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch5Status" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Ch5OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch5NotANumber" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch5CalFault" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch5InHold" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch5RampAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch5LLimitAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch5HLimitAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch6Status" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Ch6OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch6NotANumber" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch6CalFault" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch6InHold" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch6RampAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch6LLimitAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch6HLimitAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch7Status" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Ch7OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch7NotANumber" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch7CalFault" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch7InHold" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch7RampAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch7LLimitAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch7HLimitAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0Data" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="Ch1Data" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="Ch2Data" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="Ch3Data" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="Ch4Data" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="Ch5Data" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="Ch6Data" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="Ch7Data" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="RollingTimestamp" DataType="INT" Radix="Decimal" Value="0" />
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<EngineeringUnits>
<EngineeringUnit Operand=".CH0DATA">
%
</EngineeringUnit>
<EngineeringUnit Operand=".CH1DATA">
%
</EngineeringUnit>
<EngineeringUnit Operand=".CH2DATA">
%
</EngineeringUnit>
<EngineeringUnit Operand=".CH3DATA">
%
</EngineeringUnit>
<EngineeringUnit Operand=".CH4DATA">
%
</EngineeringUnit>
<EngineeringUnit Operand=".CH5DATA">
%
</EngineeringUnit>
<EngineeringUnit Operand=".CH6DATA">
%
</EngineeringUnit>
<EngineeringUnit Operand=".CH7DATA">
%
</EngineeringUnit>
</EngineeringUnits>
<Data Format="L5K">
[0.00000000e+000,0.00000000e+000,0.00000000e+000,0.00000000e+000,0.00000000e+000,0.00000000e+000
		,0.00000000e+000,0.00000000e+000]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1756_OF8_Float:O:0">
<DataValueMember Name="Ch0Data" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="Ch1Data" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="Ch2Data" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="Ch3Data" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="Ch4Data" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="Ch5Data" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="Ch6Data" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="Ch7Data" DataType="REAL" Radix="Float" Value="0.0" />
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'BAI10048_TrimmerTally_20250704.L5X', 1),
    '1756-OW16I': ("""\
<Module Name="TestMod1_1756OW16I" CatalogNumber="1756-EN2T" Vendor="1" ProductType="12" ProductCode="166" Major="11" Minor="2" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="0" Type="ICP" Upstream="false">
<Bus Size="13" />
</Port>
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications CommMethod="805306369">
<Connections>
<Connection Name="Output" RPI="10000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1756_ENET_13SLOT:I:0">
<DataValueMember Name="SlotStatusBits" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1110_0000_0000_0001" />
<ArrayMember Name="Slot" DataType="AB:1756_ENET_SLOT:I:0" Dimensions="13">
<Element Index="[0]">
<Structure DataType="AB:1756_ENET_SLOT:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111" />
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
</Structure>
</Element>
<Element Index="[1]">
<Structure DataType="AB:1756_ENET_SLOT:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0100_0000_0010_0000_1010" />
</Structure>
</Element>
<Element Index="[2]">
<Structure DataType="AB:1756_ENET_SLOT:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#1000_0011_0000_0000_0000_0000_0000_0000" />
</Structure>
</Element>
<Element Index="[3]">
<Structure DataType="AB:1756_ENET_SLOT:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0001_1011_1011_0000_0000_1000" />
</Structure>
</Element>
<Element Index="[4]">
<Structure DataType="AB:1756_ENET_SLOT:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0001_0000_0000" />
</Structure>
</Element>
<Element Index="[5]">
<Structure DataType="AB:1756_ENET_SLOT:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0010_0000_0000_1001" />
</Structure>
</Element>
<Element Index="[6]">
<Structure DataType="AB:1756_ENET_SLOT:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_1000_0010_0110_0000" />
</Structure>
</Element>
<Element Index="[7]">
<Structure DataType="AB:1756_ENET_SLOT:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_1100_0000_1010" />
</Structure>
</Element>
<Element Index="[8]">
<Structure DataType="AB:1756_ENET_SLOT:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_1110_0001_1110_1000" />
</Structure>
</Element>
<Element Index="[9]">
<Structure DataType="AB:1756_ENET_SLOT:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_1000_0000_0100" />
</Structure>
</Element>
<Element Index="[10]">
<Structure DataType="AB:1756_ENET_SLOT:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_1001_0000" />
</Structure>
</Element>
<Element Index="[11]">
<Structure DataType="AB:1756_ENET_SLOT:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0010_0110_0000" />
</Structure>
</Element>
<Element Index="[12]">
<Structure DataType="AB:1756_ENET_SLOT:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_1111_0100" />
</Structure>
</Element>
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[-8191,[[0],[0],[0],[1814536],[256],[0],[0],[0],[0],[2052],[144],[608],[244]]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1756_ENET_13SLOT:O:0">
<ArrayMember Name="Slot" DataType="AB:1756_ENET_SLOT:O:0" Dimensions="13">
<Element Index="[0]">
<Structure DataType="AB:1756_ENET_SLOT:O:0">
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
</Structure>
</Element>
<Element Index="[1]">
<Structure DataType="AB:1756_ENET_SLOT:O:0">
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
</Structure>
</Element>
<Element Index="[2]">
<Structure DataType="AB:1756_ENET_SLOT:O:0">
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
</Structure>
</Element>
<Element Index="[3]">
<Structure DataType="AB:1756_ENET_SLOT:O:0">
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0001_1011_1011_0000_0000_1000" />
</Structure>
</Element>
<Element Index="[4]">
<Structure DataType="AB:1756_ENET_SLOT:O:0">
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0001_0000_0000" />
</Structure>
</Element>
<Element Index="[5]">
<Structure DataType="AB:1756_ENET_SLOT:O:0">
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
</Structure>
</Element>
<Element Index="[6]">
<Structure DataType="AB:1756_ENET_SLOT:O:0">
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
</Structure>
</Element>
<Element Index="[7]">
<Structure DataType="AB:1756_ENET_SLOT:O:0">
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
</Structure>
</Element>
<Element Index="[8]">
<Structure DataType="AB:1756_ENET_SLOT:O:0">
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
</Structure>
</Element>
<Element Index="[9]">
<Structure DataType="AB:1756_ENET_SLOT:O:0">
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_1000_0000_0100" />
</Structure>
</Element>
<Element Index="[10]">
<Structure DataType="AB:1756_ENET_SLOT:O:0">
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_1001_0000" />
</Structure>
</Element>
<Element Index="[11]">
<Structure DataType="AB:1756_ENET_SLOT:O:0">
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0010_0110_0000" />
</Structure>
</Element>
<Element Index="[12]">
<Structure DataType="AB:1756_ENET_SLOT:O:0">
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_1111_0100" />
</Structure>
</Element>
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module Name="TestMod2_1756OW16I" CatalogNumber="1756-OW16I" Vendor="1" ProductType="7" ProductCode="30" Major="3" Minor="3" ParentModule="TestMod1_1756OW16I" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="9" Type="ICP" Upstream="true" />
</Ports>
<Communications CommMethod="1073741824">
<ConfigTag ConfigSize="24" ExternalAccess="Read/Write">
<Data Format="L5K">
[28,18,0,0,0,0,0,0,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1756_DO:C:0">
<DataValueMember Name="ProgToFaultEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultMode" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="FaultValue" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="ProgMode" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="ProgValue" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
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
""", 'BAI10048_TrimmerTally_20250704.L5X', 2),
    '1783-NATR': ("""\
<Module Name="TestMod1_1783NATR" CatalogNumber="1783-NATR" Vendor="1" ProductType="12" ProductCode="309" Major="1" Minor="1" ParentModule="Local" ParentModPortId="4" Inhibited="false" MajorFault="false" SafetyEnabled="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
</Module>
""", 'DnR_Personal/FlareFunction_311D_240731.L5X', 1),
    '1794-ACN15/C': ("""\
<Module Name="TestMod1_1794ACN15C" CatalogNumber="1756-CNB/D" Vendor="1" ProductType="12" ProductCode="7" Major="5" Minor="50" ParentModule="Local" ParentModPortId="1" Inhibited="false" MajorFault="false" ControlNetSignature="16#bb2b_890b">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="3" Type="ICP" Upstream="true" />
<Port Id="2" Address="1" Type="ControlNet" Upstream="false">
<Bus />
</Port>
</Ports>
</Module>

<Module Name="TestMod2_1794ACN15C" CatalogNumber="1794-ACN15/C" Vendor="1" ProductType="12" ProductCode="36" Major="4" Minor="1" ParentModule="TestMod1_1794ACN15C" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Type="Flex" Upstream="false">
<Bus Size="8" />
</Port>
<Port Id="2" Address="11" Type="ControlNet" Upstream="true" />
</Ports>
<Communications CommMethod="805306369">
<Connections>
<Connection Name="Output" RPI="20000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1794_ACN15_8SLOT:I:0">
<DataValueMember Name="SlotStatusBits" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<ArrayMember Name="Data" DataType="INT" Dimensions="8" Radix="Binary">
<Element Index="[0]" Value="2#0000_0100_0100_0100" />
<Element Index="[1]" Value="2#0001_0000_0011_1110" />
<Element Index="[2]" Value="2#0000_0000_0000_0000" />
<Element Index="[3]" Value="2#0000_0000_0000_0000" />
<Element Index="[4]" Value="2#0000_0000_0000_0000" />
<Element Index="[5]" Value="2#0000_0000_0000_0000" />
<Element Index="[6]" Value="2#0000_0000_0000_0000" />
<Element Index="[7]" Value="2#0000_0000_0000_0000" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[[0,0,1,0,0,0,0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1794_ACN15_8SLOT:O:0">
<ArrayMember Name="Data" DataType="INT" Dimensions="8" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000_0000_0000" />
<Element Index="[1]" Value="2#0000_0000_0000_0000" />
<Element Index="[2]" Value="2#0000_0000_0000_0001" />
<Element Index="[3]" Value="2#0000_0000_0000_0000" />
<Element Index="[4]" Value="2#0000_0000_0000_0000" />
<Element Index="[5]" Value="2#0000_0000_0000_0000" />
<Element Index="[6]" Value="2#0000_0000_0000_0000" />
<Element Index="[7]" Value="2#0000_0000_0000_0000" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'L5X_Samples/RobbinsGrn_2026_05_13r00.L5X', 2),
    '1794-AENT': ("""\
<Module Name="TestMod1_1794AENT" CatalogNumber="1794-AENT" Vendor="1" ProductType="12" ProductCode="90" Major="4" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Type="Flex" Upstream="false">
<Bus Size="8" />
</Port>
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications CommMethod="805306369">
<Connections>
<Connection Name="Output" RPI="20000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1794_AEN_8SLOT:I:0">
<DataValueMember Name="SlotStatusBits" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<ArrayMember Name="Data" DataType="INT" Dimensions="8" Radix="Binary">
<Element Index="[0]" Value="2#0000_0001_1111_0110" />
<Element Index="[1]" Value="2#0000_0000_0000_0000" />
<Element Index="[2]" Value="2#0000_0000_0000_0000" />
<Element Index="[3]" Value="2#0000_0000_0000_0000" />
<Element Index="[4]" Value="2#0000_0000_0000_0000" />
<Element Index="[5]" Value="2#0000_0000_0000_0000" />
<Element Index="[6]" Value="2#0000_0000_0000_0000" />
<Element Index="[7]" Value="2#0000_0000_0000_0000" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[[0,127,0,0,0,0,0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1794_AEN_8SLOT:O:0">
<ArrayMember Name="Data" DataType="INT" Dimensions="8" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000_0000_0000" />
<Element Index="[1]" Value="2#0000_0000_0111_1111" />
<Element Index="[2]" Value="2#0000_0000_0000_0000" />
<Element Index="[3]" Value="2#0000_0000_0000_0000" />
<Element Index="[4]" Value="2#0000_0000_0000_0000" />
<Element Index="[5]" Value="2#0000_0000_0000_0000" />
<Element Index="[6]" Value="2#0000_0000_0000_0000" />
<Element Index="[7]" Value="2#0000_0000_0000_0000" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'L5X_Samples/EmporiumEdger_20250905r1.L5X', 1),
    '1794-IA16/A': ("""\
<Module Name="TestMod1_1794IA16A" CatalogNumber="1794-AENT" Vendor="1" ProductType="12" ProductCode="90" Major="4" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Type="Flex" Upstream="false">
<Bus Size="8" />
</Port>
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications CommMethod="805306369">
<Connections>
<Connection Name="Output" RPI="20000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1794_AEN_8SLOT:I:0">
<DataValueMember Name="SlotStatusBits" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<ArrayMember Name="Data" DataType="INT" Dimensions="8" Radix="Binary">
<Element Index="[0]" Value="2#0000_0001_1111_0110" />
<Element Index="[1]" Value="2#0000_0000_0000_0000" />
<Element Index="[2]" Value="2#0000_0000_0000_0000" />
<Element Index="[3]" Value="2#0000_0000_0000_0000" />
<Element Index="[4]" Value="2#0000_0000_0000_0000" />
<Element Index="[5]" Value="2#0000_0000_0000_0000" />
<Element Index="[6]" Value="2#0000_0000_0000_0000" />
<Element Index="[7]" Value="2#0000_0000_0000_0000" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[[0,127,0,0,0,0,0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1794_AEN_8SLOT:O:0">
<ArrayMember Name="Data" DataType="INT" Dimensions="8" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000_0000_0000" />
<Element Index="[1]" Value="2#0000_0000_0111_1111" />
<Element Index="[2]" Value="2#0000_0000_0000_0000" />
<Element Index="[3]" Value="2#0000_0000_0000_0000" />
<Element Index="[4]" Value="2#0000_0000_0000_0000" />
<Element Index="[5]" Value="2#0000_0000_0000_0000" />
<Element Index="[6]" Value="2#0000_0000_0000_0000" />
<Element Index="[7]" Value="2#0000_0000_0000_0000" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module Name="TestMod2_1794IA16A" CatalogNumber="1794-IA16/A" Vendor="1" ProductType="7" ProductCode="51" Major="1" Minor="1" ParentModule="TestMod1_1794IA16A" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="0" Type="Flex" Upstream="true" />
</Ports>
<Communications CommMethod="1073741824">
<ConfigTag ConfigSize="34" ExternalAccess="Read/Write">
<Data Format="L5K">
[38,3,1,2,0,125,12,4,16,125,10,16,125,11,7,521,0,1,1,0,1,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1794_DI_Delay16:C:0">
<DataValueMember Name="Config" DataType="INT" Radix="Binary" Value="2#0000_0000_0000_0000" />
<DataValueMember Name="DelayTime_0" DataType="BOOL" Value="0" />
<DataValueMember Name="DelayTime_1" DataType="BOOL" Value="0" />
<DataValueMember Name="DelayTime_2" DataType="BOOL" Value="0" />
<DataValueMember Name="DelayTime_3" DataType="BOOL" Value="0" />
<DataValueMember Name="DelayTime_4" DataType="BOOL" Value="0" />
<DataValueMember Name="DelayTime_5" DataType="BOOL" Value="0" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<RackConnection>
<InAliasTag>
</InAliasTag>
</RackConnection>
</Connections>
</Communications>
</Module>
""", 'L5X_Samples/EmporiumEdger_20250905r1.L5X', 2),
    '1794-IB16/A': ("""\
<Module Name="TestMod1_1794IB16A" CatalogNumber="1756-CNB/D" Vendor="1" ProductType="12" ProductCode="7" Major="5" Minor="50" ParentModule="Local" ParentModPortId="1" Inhibited="false" MajorFault="false" ControlNetSignature="16#bb2b_890b">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="3" Type="ICP" Upstream="true" />
<Port Id="2" Address="1" Type="ControlNet" Upstream="false">
<Bus />
</Port>
</Ports>
</Module>

<Module Name="TestMod2_1794IB16A" CatalogNumber="1794-ACN15/C" Vendor="1" ProductType="12" ProductCode="36" Major="4" Minor="1" ParentModule="TestMod1_1794IB16A" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Type="Flex" Upstream="false">
<Bus Size="8" />
</Port>
<Port Id="2" Address="11" Type="ControlNet" Upstream="true" />
</Ports>
<Communications CommMethod="805306369">
<Connections>
<Connection Name="Output" RPI="20000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1794_ACN15_8SLOT:I:0">
<DataValueMember Name="SlotStatusBits" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<ArrayMember Name="Data" DataType="INT" Dimensions="8" Radix="Binary">
<Element Index="[0]" Value="2#0000_0100_0100_0100" />
<Element Index="[1]" Value="2#0001_0000_0011_1110" />
<Element Index="[2]" Value="2#0000_0000_0000_0000" />
<Element Index="[3]" Value="2#0000_0000_0000_0000" />
<Element Index="[4]" Value="2#0000_0000_0000_0000" />
<Element Index="[5]" Value="2#0000_0000_0000_0000" />
<Element Index="[6]" Value="2#0000_0000_0000_0000" />
<Element Index="[7]" Value="2#0000_0000_0000_0000" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[[0,0,1,0,0,0,0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1794_ACN15_8SLOT:O:0">
<ArrayMember Name="Data" DataType="INT" Dimensions="8" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000_0000_0000" />
<Element Index="[1]" Value="2#0000_0000_0000_0000" />
<Element Index="[2]" Value="2#0000_0000_0000_0001" />
<Element Index="[3]" Value="2#0000_0000_0000_0000" />
<Element Index="[4]" Value="2#0000_0000_0000_0000" />
<Element Index="[5]" Value="2#0000_0000_0000_0000" />
<Element Index="[6]" Value="2#0000_0000_0000_0000" />
<Element Index="[7]" Value="2#0000_0000_0000_0000" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module Name="TestMod3_1794IB16A" CatalogNumber="1794-IB16/A" Vendor="1" ProductType="7" ProductCode="34" Major="1" Minor="1" ParentModule="TestMod2_1794IB16A" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="1" Type="Flex" Upstream="true" />
</Ports>
<Communications CommMethod="1073741824">
<ConfigTag ConfigSize="34" ExternalAccess="Read/Write">
<Data Format="L5K">
[38,3,1,2,0,125,12,4,16,125,10,16,125,11,7,8191,0,1,1,0,1,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1794_IB16:C:0">
<DataValueMember Name="Config" DataType="INT" Radix="Binary" Value="2#0000_0000_0000_0000" />
<DataValueMember Name="Filter0_00_11" DataType="BOOL" Value="0" />
<DataValueMember Name="Filter1_00_11" DataType="BOOL" Value="0" />
<DataValueMember Name="Filter2_00_11" DataType="BOOL" Value="0" />
<DataValueMember Name="Filter3_12_15" DataType="BOOL" Value="0" />
<DataValueMember Name="Filter4_12_15" DataType="BOOL" Value="0" />
<DataValueMember Name="Filter5_12_15" DataType="BOOL" Value="0" />
<DataValueMember Name="ResetCounter" DataType="BOOL" Value="0" />
<DataValueMember Name="DisableFilter" DataType="BOOL" Value="0" />
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
""", 'L5X_Samples/RobbinsGrn_2026_05_13r00.L5X', 3),
    '1794-IB16XOB16P/A': ("""\
<Module Name="TestMod1_1794IB16XOB16PA" CatalogNumber="1756-CNB/D" Vendor="1" ProductType="12" ProductCode="7" Major="5" Minor="50" ParentModule="Local" ParentModPortId="1" Inhibited="false" MajorFault="false" ControlNetSignature="16#bb2b_890b">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="3" Type="ICP" Upstream="true" />
<Port Id="2" Address="1" Type="ControlNet" Upstream="false">
<Bus />
</Port>
</Ports>
</Module>

<Module Name="TestMod2_1794IB16XOB16PA" CatalogNumber="1794-ACN15/C" Vendor="1" ProductType="12" ProductCode="36" Major="4" Minor="1" ParentModule="TestMod1_1794IB16XOB16PA" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Type="Flex" Upstream="false">
<Bus Size="8" />
</Port>
<Port Id="2" Address="12" Type="ControlNet" Upstream="true" />
</Ports>
<Communications CommMethod="805306369">
<Connections>
<Connection Name="Output" RPI="20000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1794_ACN15_8SLOT:I:0">
<DataValueMember Name="SlotStatusBits" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<ArrayMember Name="Data" DataType="INT" Dimensions="8" Radix="Binary">
<Element Index="[0]" Value="2#0101_0010_1010_1010" />
<Element Index="[1]" Value="2#1010_1010_1010_1010" />
<Element Index="[2]" Value="2#1010_1010_1110_1010" />
<Element Index="[3]" Value="2#0000_0000_0000_0000" />
<Element Index="[4]" Value="2#0000_0000_0000_0001" />
<Element Index="[5]" Value="2#0000_0000_0000_0000" />
<Element Index="[6]" Value="2#0000_0000_0000_0000" />
<Element Index="[7]" Value="2#0000_0000_0000_0000" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[[22816,-32513,8191,0,0,0,0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1794_ACN15_8SLOT:O:0">
<ArrayMember Name="Data" DataType="INT" Dimensions="8" Radix="Binary">
<Element Index="[0]" Value="2#0101_1001_0010_0000" />
<Element Index="[1]" Value="2#1000_0000_1111_1111" />
<Element Index="[2]" Value="2#0001_1111_1111_1111" />
<Element Index="[3]" Value="2#0000_0000_0000_0000" />
<Element Index="[4]" Value="2#0000_0000_0000_0000" />
<Element Index="[5]" Value="2#0000_0000_0000_0000" />
<Element Index="[6]" Value="2#0000_0000_0000_0000" />
<Element Index="[7]" Value="2#0000_0000_0000_0000" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module Name="TestMod3_1794IB16XOB16PA" CatalogNumber="1794-IB16XOB16P/A" Vendor="1" ProductType="7" ProductCode="155" Major="1" Minor="1" ParentModule="TestMod2_1794IB16XOB16PA" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="0" Type="Flex" Upstream="true" />
</Ports>
<Communications CommMethod="1073741824">
<ConfigTag ConfigSize="36" ExternalAccess="Read/Write">
<Data Format="L5K">
[40,3,1,2,16,125,12,4,16,125,10,0,125,11,8,8191,0,1,0,1,1,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1794_IB16XOB16P:C:0">
<DataValueMember Name="Filter_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Filter_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Filter_2" DataType="BOOL" Value="0" />
<DataValueMember Name="SSData" DataType="INT" Radix="Binary" Value="2#0000_0000_0000_0000" />
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
""", 'L5X_Samples/RobbinsGrn_2026_05_13r00.L5X', 3),
    '1794-IB32/A': ("""\
<Module Name="TestMod1_1794IB32A" CatalogNumber="1756-CNB/D" Vendor="1" ProductType="12" ProductCode="7" Major="5" Minor="50" ParentModule="Local" ParentModPortId="1" Inhibited="false" MajorFault="false" ControlNetSignature="16#bb2b_890b">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="3" Type="ICP" Upstream="true" />
<Port Id="2" Address="1" Type="ControlNet" Upstream="false">
<Bus />
</Port>
</Ports>
</Module>

<Module Name="TestMod2_1794IB32A" CatalogNumber="1794-ACN15/C" Vendor="1" ProductType="12" ProductCode="36" Major="4" Minor="1" ParentModule="TestMod1_1794IB32A" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Type="Flex" Upstream="false">
<Bus Size="8" />
</Port>
<Port Id="2" Address="11" Type="ControlNet" Upstream="true" />
</Ports>
<Communications CommMethod="805306369">
<Connections>
<Connection Name="Output" RPI="20000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1794_ACN15_8SLOT:I:0">
<DataValueMember Name="SlotStatusBits" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<ArrayMember Name="Data" DataType="INT" Dimensions="8" Radix="Binary">
<Element Index="[0]" Value="2#0000_0100_0100_0100" />
<Element Index="[1]" Value="2#0001_0000_0011_1110" />
<Element Index="[2]" Value="2#0000_0000_0000_0000" />
<Element Index="[3]" Value="2#0000_0000_0000_0000" />
<Element Index="[4]" Value="2#0000_0000_0000_0000" />
<Element Index="[5]" Value="2#0000_0000_0000_0000" />
<Element Index="[6]" Value="2#0000_0000_0000_0000" />
<Element Index="[7]" Value="2#0000_0000_0000_0000" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[[0,0,1,0,0,0,0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1794_ACN15_8SLOT:O:0">
<ArrayMember Name="Data" DataType="INT" Dimensions="8" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000_0000_0000" />
<Element Index="[1]" Value="2#0000_0000_0000_0000" />
<Element Index="[2]" Value="2#0000_0000_0000_0001" />
<Element Index="[3]" Value="2#0000_0000_0000_0000" />
<Element Index="[4]" Value="2#0000_0000_0000_0000" />
<Element Index="[5]" Value="2#0000_0000_0000_0000" />
<Element Index="[6]" Value="2#0000_0000_0000_0000" />
<Element Index="[7]" Value="2#0000_0000_0000_0000" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module Name="TestMod3_1794IB32A" CatalogNumber="1794-IB32/A" Vendor="1" ProductType="7" ProductCode="156" Major="1" Minor="1" ParentModule="TestMod2_1794IB32A" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="0" Type="Flex" Upstream="true" />
</Ports>
<Communications CommMethod="536870913">
<ConfigTag ConfigSize="34" ExternalAccess="Read/Write">
<Data Format="L5K">
[38,3,1,2,0,125,12,4,32,125,10,0,125,11,7,8191,0,2,0,0,1,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1794_IB32:C:0">
<DataValueMember Name="Config" DataType="INT" Radix="Binary" Value="2#0000_0000_0000_0000" />
<DataValueMember Name="Filter_8" DataType="BOOL" Value="0" />
<DataValueMember Name="Filter_9" DataType="BOOL" Value="0" />
<DataValueMember Name="Filter_10" DataType="BOOL" Value="0" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="InputData" RPI="5000" Type="Input" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1794_IB32:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#1111_1100_0010_0000_0000_0100_0100_0100" ForceValue="2#1..._...._...._...._...._...._...._...." />
</Structure>
</Data>
</InputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'L5X_Samples/RobbinsGrn_2026_05_13r00.L5X', 3),
    '1794-IR8/A': ("""\
<Module Name="TestMod1_1794IR8A" CatalogNumber="1756-CNB/D" Vendor="1" ProductType="12" ProductCode="7" Major="5" Minor="50" ParentModule="Local" ParentModPortId="1" Inhibited="false" MajorFault="false" ControlNetSignature="16#bb2b_890b">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="3" Type="ICP" Upstream="true" />
<Port Id="2" Address="1" Type="ControlNet" Upstream="false">
<Bus />
</Port>
</Ports>
</Module>

<Module Name="TestMod2_1794IR8A" CatalogNumber="1794-ACN15/C" Vendor="1" ProductType="12" ProductCode="36" Major="4" Minor="1" ParentModule="TestMod1_1794IR8A" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Type="Flex" Upstream="false">
<Bus Size="8" />
</Port>
<Port Id="2" Address="13" Type="ControlNet" Upstream="true" />
</Ports>
<Communications CommMethod="805306369">
<Connections>
<Connection Name="Output" RPI="20000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1794_ACN15_8SLOT:I:0">
<DataValueMember Name="SlotStatusBits" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<ArrayMember Name="Data" DataType="INT" Dimensions="8" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000_0000_0000" />
<Element Index="[1]" Value="2#0000_0000_0000_0000" />
<Element Index="[2]" Value="2#0000_0000_0000_0000" />
<Element Index="[3]" Value="2#0000_0000_0000_0000" />
<Element Index="[4]" Value="2#0000_0000_0000_0000" />
<Element Index="[5]" Value="2#0000_0000_0000_0000" />
<Element Index="[6]" Value="2#0000_0000_0000_0000" />
<Element Index="[7]" Value="2#0000_0000_0000_0000" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[[0,0,0,0,0,65,0,2]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1794_ACN15_8SLOT:O:0">
<ArrayMember Name="Data" DataType="INT" Dimensions="8" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000_0000_0000" />
<Element Index="[1]" Value="2#0000_0000_0000_0000" />
<Element Index="[2]" Value="2#0000_0000_0000_0000" />
<Element Index="[3]" Value="2#0000_0000_0000_0000" />
<Element Index="[4]" Value="2#0000_0000_0000_0000" />
<Element Index="[5]" Value="2#0000_0000_0100_0001" />
<Element Index="[6]" Value="2#0000_0000_0000_0000" />
<Element Index="[7]" Value="2#0000_0000_0000_0010" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module Name="TestMod3_1794IR8A" CatalogNumber="1794-IR8/A" Vendor="1" ProductType="10" ProductCode="27" Major="1" Minor="1" ParentModule="TestMod2_1794IR8A" ParentModPortId="1" Inhibited="false" MajorFault="false" AutoDiagsEnabled="true">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="6" Type="Flex" Upstream="true" />
</Ports>
<Communications CommMethod="536870913">
<ConfigTag ConfigSize="40" ExternalAccess="Read/Write">
<Data Format="L5K">
[44,3,1,2,0,125,12,4,144,125,10,32,125,11,10,8191,0,9,2,0,4,5,0,13107,13107,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1794_IR8:C:0">
<DataValueMember Name="Config1" DataType="SINT" Radix="Binary" Value="2#0000_0101" />
<DataValueMember Name="ModuleDataType0" DataType="BOOL" Value="1" />
<DataValueMember Name="ModuleDataType1" DataType="BOOL" Value="0" />
<DataValueMember Name="EnhancedMode" DataType="BOOL" Value="1" />
<DataValueMember Name="NotchFrequency3" DataType="BOOL" Value="0" />
<DataValueMember Name="NotchFrequency4" DataType="BOOL" Value="0" />
<DataValueMember Name="NotchFrequency5" DataType="BOOL" Value="0" />
<DataValueMember Name="GainOffsetCalibration" DataType="BOOL" Value="0" />
<DataValueMember Name="CalibrationClock" DataType="BOOL" Value="0" />
<DataValueMember Name="CalibrationMaskCh0" DataType="BOOL" Value="0" />
<DataValueMember Name="CalibrationMaskCh1" DataType="BOOL" Value="0" />
<DataValueMember Name="CalibrationMaskCh2" DataType="BOOL" Value="0" />
<DataValueMember Name="CalibrationMaskCh3" DataType="BOOL" Value="0" />
<DataValueMember Name="CalibrationMaskCh4" DataType="BOOL" Value="0" />
<DataValueMember Name="CalibrationMaskCh5" DataType="BOOL" Value="0" />
<DataValueMember Name="CalibrationMaskCh6" DataType="BOOL" Value="0" />
<DataValueMember Name="CalibrationMaskCh7" DataType="BOOL" Value="0" />
<DataValueMember Name="Config2" DataType="INT" Radix="Binary" Value="2#0011_0011_0011_0011" />
<DataValueMember Name="Ch0RTDType0" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch0RTDType1" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch0RTDType2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0RTDType3" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1RTDType4" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch1RTDType5" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch1RTDType6" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1RTDType7" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch2RTDType8" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch2RTDType9" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch2RTDType10" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch2RTDType11" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch3RTDType12" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch3RTDType13" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch3RTDType14" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch3RTDType15" DataType="BOOL" Value="0" />
<DataValueMember Name="Config3" DataType="INT" Radix="Binary" Value="2#0011_0011_0011_0011" />
<DataValueMember Name="Ch4RTDType0" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch4RTDType1" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch4RTDType2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch4RTDType3" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch5RTDType4" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch5RTDType5" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch5RTDType6" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch5RTDType7" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch6RTDType8" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch6RTDType9" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch6RTDType10" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch6RTDType11" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch7RTDType12" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch7RTDType13" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch7RTDType14" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch7RTDType15" DataType="BOOL" Value="0" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="InputData" RPI="50000" Type="Input" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1794_IR8:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="Ch0Data" DataType="INT" Radix="Decimal" Value="683" />
<DataValueMember Name="Ch1Data" DataType="INT" Radix="Decimal" Value="618" />
<DataValueMember Name="Ch2Data" DataType="INT" Radix="Decimal" Value="11660" />
<DataValueMember Name="Ch3Data" DataType="INT" Radix="Decimal" Value="11660" />
<DataValueMember Name="Ch4Data" DataType="INT" Radix="Decimal" Value="11660" />
<DataValueMember Name="Ch5Data" DataType="INT" Radix="Decimal" Value="11660" />
<DataValueMember Name="Ch6Data" DataType="INT" Radix="Decimal" Value="11660" />
<DataValueMember Name="Ch7Data" DataType="INT" Radix="Decimal" Value="11660" />
<DataValueMember Name="Alarms" DataType="INT" Radix="Binary" Value="2#1111_1100_0000_0000" />
<DataValueMember Name="Ch0UnderrangeAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1UnderrangeAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch2UnderrangeAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch3UnderrangeAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch4UnderrangeAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch5UnderrangeAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch6UnderrangeAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch7UnderrangeAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0OverrangeAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1OverrangeAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch2OverrangeAlarm" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch3OverrangeAlarm" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch4OverrangeAlarm" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch5OverrangeAlarm" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch6OverrangeAlarm" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch7OverrangeAlarm" DataType="BOOL" Value="1" />
<DataValueMember Name="Status" DataType="INT" Radix="Binary" Value="2#0000_0000_1000_0000" />
<DataValueMember Name="PowerUp" DataType="BOOL" Value="0" />
<DataValueMember Name="CriticalError4" DataType="BOOL" Value="0" />
<DataValueMember Name="CriticalError5" DataType="BOOL" Value="0" />
<DataValueMember Name="CriticalError6" DataType="BOOL" Value="0" />
<DataValueMember Name="CalibrationOutOfRange" DataType="BOOL" Value="0" />
<DataValueMember Name="CalibrationDone" DataType="BOOL" Value="0" />
<DataValueMember Name="CalibrationBad" DataType="BOOL" Value="0" />
</Structure>
</Data>
</InputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'L5X_Samples/RobbinsGrn_2026_05_13r00.L5X', 3),
    '1794-OA8/A': ("""\
<Module Name="TestMod1_1794OA8A" CatalogNumber="1756-CNB/D" Vendor="1" ProductType="12" ProductCode="7" Major="5" Minor="50" ParentModule="Local" ParentModPortId="1" Inhibited="false" MajorFault="false" ControlNetSignature="16#bb2b_890b">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="3" Type="ICP" Upstream="true" />
<Port Id="2" Address="1" Type="ControlNet" Upstream="false">
<Bus />
</Port>
</Ports>
</Module>

<Module Name="TestMod2_1794OA8A" CatalogNumber="1794-ACN15/C" Vendor="1" ProductType="12" ProductCode="36" Major="4" Minor="1" ParentModule="TestMod1_1794OA8A" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Type="Flex" Upstream="false">
<Bus Size="8" />
</Port>
<Port Id="2" Address="11" Type="ControlNet" Upstream="true" />
</Ports>
<Communications CommMethod="805306369">
<Connections>
<Connection Name="Output" RPI="20000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1794_ACN15_8SLOT:I:0">
<DataValueMember Name="SlotStatusBits" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<ArrayMember Name="Data" DataType="INT" Dimensions="8" Radix="Binary">
<Element Index="[0]" Value="2#0000_0100_0100_0100" />
<Element Index="[1]" Value="2#0001_0000_0011_1110" />
<Element Index="[2]" Value="2#0000_0000_0000_0000" />
<Element Index="[3]" Value="2#0000_0000_0000_0000" />
<Element Index="[4]" Value="2#0000_0000_0000_0000" />
<Element Index="[5]" Value="2#0000_0000_0000_0000" />
<Element Index="[6]" Value="2#0000_0000_0000_0000" />
<Element Index="[7]" Value="2#0000_0000_0000_0000" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[[0,0,1,0,0,0,0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1794_ACN15_8SLOT:O:0">
<ArrayMember Name="Data" DataType="INT" Dimensions="8" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000_0000_0000" />
<Element Index="[1]" Value="2#0000_0000_0000_0000" />
<Element Index="[2]" Value="2#0000_0000_0000_0001" />
<Element Index="[3]" Value="2#0000_0000_0000_0000" />
<Element Index="[4]" Value="2#0000_0000_0000_0000" />
<Element Index="[5]" Value="2#0000_0000_0000_0000" />
<Element Index="[6]" Value="2#0000_0000_0000_0000" />
<Element Index="[7]" Value="2#0000_0000_0000_0000" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module Name="TestMod3_1794OA8A" CatalogNumber="1794-OA8/A" Vendor="1" ProductType="7" ProductCode="33" Major="1" Minor="1" ParentModule="TestMod2_1794OA8A" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="2" Type="Flex" Upstream="true" />
</Ports>
<Communications CommMethod="1073741824">
<ConfigTag ConfigSize="36" ExternalAccess="Read/Write">
<Data Format="L5K">
[40,3,1,2,16,125,12,4,0,125,10,16,125,11,8,8191,0,0,1,1,1,0,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1794_DO8:C:0">
<DataValueMember Name="SSData" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<RackConnection>
<OutAliasTag />
</RackConnection>
</Connections>
</Communications>
</Module>
""", 'L5X_Samples/RobbinsGrn_2026_05_13r00.L5X', 3),
    '1794-OE4/B': ("""\
<Module Name="TestMod1_1794OE4B" CatalogNumber="1756-CNB/D" Vendor="1" ProductType="12" ProductCode="7" Major="5" Minor="50" ParentModule="Local" ParentModPortId="1" Inhibited="false" MajorFault="false" ControlNetSignature="16#bb2b_890b">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="3" Type="ICP" Upstream="true" />
<Port Id="2" Address="1" Type="ControlNet" Upstream="false">
<Bus />
</Port>
</Ports>
</Module>

<Module Name="TestMod2_1794OE4B" CatalogNumber="1794-ACN15/C" Vendor="1" ProductType="12" ProductCode="36" Major="4" Minor="1" ParentModule="TestMod1_1794OE4B" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Type="Flex" Upstream="false">
<Bus Size="8" />
</Port>
<Port Id="2" Address="16" Type="ControlNet" Upstream="true" />
</Ports>
<Communications CommMethod="805306369">
<Connections>
<Connection Name="Output" RPI="20000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1794_ACN15_8SLOT:I:0">
<DataValueMember Name="SlotStatusBits" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<ArrayMember Name="Data" DataType="INT" Dimensions="8" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000_0000_0000" />
<Element Index="[1]" Value="2#0000_0000_0000_0000" />
<Element Index="[2]" Value="2#0000_0000_0000_0000" />
<Element Index="[3]" Value="2#0000_0000_0000_0000" />
<Element Index="[4]" Value="2#0000_0000_0000_0000" />
<Element Index="[5]" Value="2#0000_0000_0000_0000" />
<Element Index="[6]" Value="2#0000_0000_0000_0000" />
<Element Index="[7]" Value="2#0000_0000_0000_0000" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[[0,0,2,65,0,0,0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1794_ACN15_8SLOT:O:0">
<ArrayMember Name="Data" DataType="INT" Dimensions="8" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000_0000_0000" />
<Element Index="[1]" Value="2#0000_0000_0000_0000" />
<Element Index="[2]" Value="2#0000_0000_0000_0010" />
<Element Index="[3]" Value="2#0000_0000_0100_0001" />
<Element Index="[4]" Value="2#0000_0000_0000_0000" />
<Element Index="[5]" Value="2#0000_0000_0000_0000" />
<Element Index="[6]" Value="2#0000_0000_0000_0000" />
<Element Index="[7]" Value="2#0000_0000_0000_0000" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module Name="TestMod3_1794OE4B" CatalogNumber="1794-OE4/B" Vendor="1" ProductType="10" ProductCode="26" Major="2" Minor="1" ParentModule="TestMod2_1794OE4B" ParentModPortId="1" Inhibited="false" MajorFault="false" AutoDiagsEnabled="true">
<EKey State="Disabled" />
<Ports>
<Port Id="1" Address="0" Type="Flex" Upstream="true" />
</Ports>
<Communications CommMethod="536870913">
<ConfigTag ConfigSize="44" ExternalAccess="Read/Write">
<Data Format="L5K">
[48,3,1,2,64,125,12,4,0,125,10,16,125,11,12,8191,0,0,1,4,2,15,15,0,0,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1794_OE4:C:0">
<DataValueMember Name="Config1" DataType="INT" Radix="Binary" Value="2#0000_0000_0000_1111" />
<DataValueMember Name="Ch0SafeStateConfig" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch1SafeStateConfig" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch2SafeStateConfig" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch3SafeStateConfig" DataType="BOOL" Value="1" />
<DataValueMember Name="Config2" DataType="INT" Radix="Binary" Value="2#0000_0000_0000_1111" />
<DataValueMember Name="Ch0FullRange" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch1FullRange" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch2FullRange" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch3FullRange" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch0ConfigSelect" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1ConfigSelect" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch2ConfigSelect" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch3ConfigSelect" DataType="BOOL" Value="0" />
<DataValueMember Name="SSCh0OutputData" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="SSCh1OutputData" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="SSCh2OutputData" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="SSCh3OutputData" DataType="INT" Radix="Decimal" Value="0" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="OutputData" RPI="20000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1794_OE4:I:1">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="Status" DataType="INT" Radix="Binary" Value="2#0000_0000_0000_0000" />
<DataValueMember Name="Ch0OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch2OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch3OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="PowerUp" DataType="BOOL" Value="0" />
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[0,0,10,10]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1794_OE4:O:0">
<DataValueMember Name="Ch0Data" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1Data" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch2Data" DataType="INT" Radix="Decimal" Value="10" />
<DataValueMember Name="Ch3Data" DataType="INT" Radix="Decimal" Value="10" />
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'L5X_Samples/RobbinsGrn_2026_05_13r00.L5X', 3),
    '1794-OW8/A': ("""\
<Module Name="TestMod1_1794OW8A" CatalogNumber="1756-CNB/D" Vendor="1" ProductType="12" ProductCode="7" Major="5" Minor="50" ParentModule="Local" ParentModPortId="1" Inhibited="false" MajorFault="false" ControlNetSignature="16#bb2b_890b">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="3" Type="ICP" Upstream="true" />
<Port Id="2" Address="1" Type="ControlNet" Upstream="false">
<Bus />
</Port>
</Ports>
</Module>

<Module Name="TestMod2_1794OW8A" CatalogNumber="1794-ACN15/C" Vendor="1" ProductType="12" ProductCode="36" Major="4" Minor="1" ParentModule="TestMod1_1794OW8A" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Type="Flex" Upstream="false">
<Bus Size="8" />
</Port>
<Port Id="2" Address="13" Type="ControlNet" Upstream="true" />
</Ports>
<Communications CommMethod="805306369">
<Connections>
<Connection Name="Output" RPI="20000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1794_ACN15_8SLOT:I:0">
<DataValueMember Name="SlotStatusBits" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<ArrayMember Name="Data" DataType="INT" Dimensions="8" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000_0000_0000" />
<Element Index="[1]" Value="2#0000_0000_0000_0000" />
<Element Index="[2]" Value="2#0000_0000_0000_0000" />
<Element Index="[3]" Value="2#0000_0000_0000_0000" />
<Element Index="[4]" Value="2#0000_0000_0000_0000" />
<Element Index="[5]" Value="2#0000_0000_0000_0000" />
<Element Index="[6]" Value="2#0000_0000_0000_0000" />
<Element Index="[7]" Value="2#0000_0000_0000_0000" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[[0,0,0,0,0,65,0,2]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1794_ACN15_8SLOT:O:0">
<ArrayMember Name="Data" DataType="INT" Dimensions="8" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000_0000_0000" />
<Element Index="[1]" Value="2#0000_0000_0000_0000" />
<Element Index="[2]" Value="2#0000_0000_0000_0000" />
<Element Index="[3]" Value="2#0000_0000_0000_0000" />
<Element Index="[4]" Value="2#0000_0000_0000_0000" />
<Element Index="[5]" Value="2#0000_0000_0100_0001" />
<Element Index="[6]" Value="2#0000_0000_0000_0000" />
<Element Index="[7]" Value="2#0000_0000_0000_0010" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module Name="TestMod3_1794OW8A" CatalogNumber="1794-OW8/A" Vendor="1" ProductType="7" ProductCode="37" Major="1" Minor="1" ParentModule="TestMod2_1794OW8A" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="5" Type="Flex" Upstream="true" />
</Ports>
<Communications CommMethod="1073741824">
<ConfigTag ConfigSize="36" ExternalAccess="Read/Write">
<Data Format="L5K">
[40,3,1,2,16,125,12,4,0,125,10,16,125,11,8,8191,0,0,1,1,1,0,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1794_DO8:C:0">
<DataValueMember Name="SSData" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<RackConnection>
<OutAliasTag />
</RackConnection>
</Connections>
</Communications>
</Module>
""", 'L5X_Samples/RobbinsGrn_2026_05_13r00.L5X', 3),
    '1794-VHSC/A': ("""\
<Module Name="TestMod1_1794VHSCA" CatalogNumber="1756-CNB/D" Vendor="1" ProductType="12" ProductCode="7" Major="5" Minor="50" ParentModule="Local" ParentModPortId="1" Inhibited="false" MajorFault="false" ControlNetSignature="16#bb2b_890b">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="3" Type="ICP" Upstream="true" />
<Port Id="2" Address="1" Type="ControlNet" Upstream="false">
<Bus />
</Port>
</Ports>
</Module>

<Module Name="TestMod2_1794VHSCA" CatalogNumber="1794-ACN15/C" Vendor="1" ProductType="12" ProductCode="36" Major="4" Minor="1" ParentModule="TestMod1_1794VHSCA" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Type="Flex" Upstream="false">
<Bus Size="8" />
</Port>
<Port Id="2" Address="16" Type="ControlNet" Upstream="true" />
</Ports>
<Communications CommMethod="805306369">
<Connections>
<Connection Name="Output" RPI="20000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1794_ACN15_8SLOT:I:0">
<DataValueMember Name="SlotStatusBits" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<ArrayMember Name="Data" DataType="INT" Dimensions="8" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000_0000_0000" />
<Element Index="[1]" Value="2#0000_0000_0000_0000" />
<Element Index="[2]" Value="2#0000_0000_0000_0000" />
<Element Index="[3]" Value="2#0000_0000_0000_0000" />
<Element Index="[4]" Value="2#0000_0000_0000_0000" />
<Element Index="[5]" Value="2#0000_0000_0000_0000" />
<Element Index="[6]" Value="2#0000_0000_0000_0000" />
<Element Index="[7]" Value="2#0000_0000_0000_0000" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[[0,0,2,65,0,0,0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1794_ACN15_8SLOT:O:0">
<ArrayMember Name="Data" DataType="INT" Dimensions="8" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000_0000_0000" />
<Element Index="[1]" Value="2#0000_0000_0000_0000" />
<Element Index="[2]" Value="2#0000_0000_0000_0010" />
<Element Index="[3]" Value="2#0000_0000_0100_0001" />
<Element Index="[4]" Value="2#0000_0000_0000_0000" />
<Element Index="[5]" Value="2#0000_0000_0000_0000" />
<Element Index="[6]" Value="2#0000_0000_0000_0000" />
<Element Index="[7]" Value="2#0000_0000_0000_0000" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module Name="TestMod3_1794VHSCA" CatalogNumber="1794-VHSC/A" Vendor="1" ProductType="109" ProductCode="5" Major="1" Minor="1" ParentModule="TestMod2_1794VHSCA" ParentModPortId="1" Inhibited="false" MajorFault="false" AutoDiagsEnabled="true">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="4" Type="Flex" Upstream="true" />
</Ports>
<Communications CommMethod="536870913">
<ConfigTag ConfigSize="152" ExternalAccess="Read/Write">
<Data Format="L5K">
[156,3,1,2,64,125,12,4,144,125,10,0,125,11,66,8191,0,9,0,4,56,0,0,0,0,0,0,16777215,16777215,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1794_VHSC:C:0">
<DataValueMember Name="Config" DataType="INT" Radix="Binary" Value="2#0000_0000_0000_0000" />
<DataValueMember Name="Counter0Config0" DataType="BOOL" Value="0" />
<DataValueMember Name="Counter0Config1" DataType="BOOL" Value="0" />
<DataValueMember Name="Counter0Config2" DataType="BOOL" Value="0" />
<DataValueMember Name="Counter0Config3" DataType="BOOL" Value="0" />
<DataValueMember Name="Counter0Mode4" DataType="BOOL" Value="0" />
<DataValueMember Name="Counter0Mode5" DataType="BOOL" Value="0" />
<DataValueMember Name="Counter0Mode6" DataType="BOOL" Value="0" />
<DataValueMember Name="Counter0Zinvert" DataType="BOOL" Value="0" />
<DataValueMember Name="Counter1Config8" DataType="BOOL" Value="0" />
<DataValueMember Name="Counter1Config9" DataType="BOOL" Value="0" />
<DataValueMember Name="Counter1Config10" DataType="BOOL" Value="0" />
<DataValueMember Name="Counter1Config11" DataType="BOOL" Value="0" />
<DataValueMember Name="Counter1Mode12" DataType="BOOL" Value="0" />
<DataValueMember Name="Counter1Mode13" DataType="BOOL" Value="0" />
<DataValueMember Name="Counter1Mode14" DataType="BOOL" Value="0" />
<DataValueMember Name="Counter1Zinvert" DataType="BOOL" Value="0" />
<DataValueMember Name="FilterConfig" DataType="INT" Radix="Binary" Value="2#0000_0000_0000_0000" />
<DataValueMember Name="Counter0Filter0" DataType="BOOL" Value="0" />
<DataValueMember Name="Counter0Filter1" DataType="BOOL" Value="0" />
<DataValueMember Name="Counter0Filter2" DataType="BOOL" Value="0" />
<DataValueMember Name="Counter0Filter3" DataType="BOOL" Value="0" />
<DataValueMember Name="Counter0AFilter" DataType="BOOL" Value="0" />
<DataValueMember Name="Counter0BFilter" DataType="BOOL" Value="0" />
<DataValueMember Name="Counter0ZFilter" DataType="BOOL" Value="0" />
<DataValueMember Name="Counter1Filter8" DataType="BOOL" Value="0" />
<DataValueMember Name="Counter1Filter9" DataType="BOOL" Value="0" />
<DataValueMember Name="Counter1Filter10" DataType="BOOL" Value="0" />
<DataValueMember Name="Counter1Filter11" DataType="BOOL" Value="0" />
<DataValueMember Name="Counter1AFilter" DataType="BOOL" Value="0" />
<DataValueMember Name="Counter1BFilter" DataType="BOOL" Value="0" />
<DataValueMember Name="Counter1ZFilter" DataType="BOOL" Value="0" />
<DataValueMember Name="TimeBase" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch0GateInterval" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1GateInterval" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch0Rollover" DataType="DINT" Radix="Decimal" Value="16777215" />
<DataValueMember Name="Ch1Rollover" DataType="DINT" Radix="Decimal" Value="16777215" />
<DataValueMember Name="Ch0Preset" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1Preset" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch0Scalar" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1Scalar" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="OutputTies1" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="OP1Counter1Window1" DataType="BOOL" Value="0" />
<DataValueMember Name="OP1Counter1Window2" DataType="BOOL" Value="0" />
<DataValueMember Name="OP1Counter1Window3" DataType="BOOL" Value="0" />
<DataValueMember Name="OP1Counter1Window4" DataType="BOOL" Value="0" />
<DataValueMember Name="OP1Counter2Window1" DataType="BOOL" Value="0" />
<DataValueMember Name="OP1Counter2Window2" DataType="BOOL" Value="0" />
<DataValueMember Name="OP1Counter2Window3" DataType="BOOL" Value="0" />
<DataValueMember Name="OP1Counter2Window4" DataType="BOOL" Value="0" />
<DataValueMember Name="OutputTies2" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="OP2Counter1Window1" DataType="BOOL" Value="0" />
<DataValueMember Name="OP2Counter1Window2" DataType="BOOL" Value="0" />
<DataValueMember Name="OP2Counter1Window3" DataType="BOOL" Value="0" />
<DataValueMember Name="OP2Counter1Window4" DataType="BOOL" Value="0" />
<DataValueMember Name="OP2Counter2Window1" DataType="BOOL" Value="0" />
<DataValueMember Name="OP2Counter2Window2" DataType="BOOL" Value="0" />
<DataValueMember Name="OP2Counter2Window3" DataType="BOOL" Value="0" />
<DataValueMember Name="OP2Counter2Window4" DataType="BOOL" Value="0" />
<DataValueMember Name="OutputTies3" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="OP3Counter1Window1" DataType="BOOL" Value="0" />
<DataValueMember Name="OP3Counter1Window2" DataType="BOOL" Value="0" />
<DataValueMember Name="OP3Counter1Window3" DataType="BOOL" Value="0" />
<DataValueMember Name="OP3Counter1Window4" DataType="BOOL" Value="0" />
<DataValueMember Name="OP3Counter2Window1" DataType="BOOL" Value="0" />
<DataValueMember Name="OP3Counter2Window2" DataType="BOOL" Value="0" />
<DataValueMember Name="OP3Counter2Window3" DataType="BOOL" Value="0" />
<DataValueMember Name="OP3Counter2Window4" DataType="BOOL" Value="0" />
<DataValueMember Name="OutputTies4" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="OP4Counter1Window1" DataType="BOOL" Value="0" />
<DataValueMember Name="OP4Counter1Window2" DataType="BOOL" Value="0" />
<DataValueMember Name="OP4Counter1Window3" DataType="BOOL" Value="0" />
<DataValueMember Name="OP4Counter1Window4" DataType="BOOL" Value="0" />
<DataValueMember Name="OP4Counter2Window1" DataType="BOOL" Value="0" />
<DataValueMember Name="OP4Counter2Window2" DataType="BOOL" Value="0" />
<DataValueMember Name="OP4Counter2Window3" DataType="BOOL" Value="0" />
<DataValueMember Name="OP4Counter2Window4" DataType="BOOL" Value="0" />
<DataValueMember Name="Counter1ON1" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Counter1OFF1" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Counter1ON2" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Counter1OFF2" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Counter1ON3" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Counter1OFF3" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Counter1ON4" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Counter1OFF4" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Counter2ON1" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Counter2OFF1" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Counter2ON2" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Counter2OFF2" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Counter2ON3" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Counter2OFF3" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Counter2ON4" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Counter2OFF4" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="SSCounterControl" DataType="INT" Radix="Binary" Value="2#0000_0000_0000_0000" />
<DataValueMember Name="SSCh0CounterReset" DataType="BOOL" Value="0" />
<DataValueMember Name="SSCh0CounterPreset" DataType="BOOL" Value="0" />
<DataValueMember Name="SSCh0ValueReset" DataType="BOOL" Value="0" />
<DataValueMember Name="SSCh1CounterReset" DataType="BOOL" Value="0" />
<DataValueMember Name="SSCh1CounterPreset" DataType="BOOL" Value="0" />
<DataValueMember Name="SSCh1ValueReset" DataType="BOOL" Value="0" />
<DataValueMember Name="SSOutputControl" DataType="INT" Radix="Binary" Value="2#0000_0000_0000_0000" />
<DataValueMember Name="SSOut0Force" DataType="BOOL" Value="0" />
<DataValueMember Name="SSOut0Enable" DataType="BOOL" Value="0" />
<DataValueMember Name="SSOut0Local" DataType="BOOL" Value="0" />
<DataValueMember Name="SSOut1Force" DataType="BOOL" Value="0" />
<DataValueMember Name="SSOut1Enable" DataType="BOOL" Value="0" />
<DataValueMember Name="SSOut1Local" DataType="BOOL" Value="0" />
<DataValueMember Name="SSOut2Force" DataType="BOOL" Value="0" />
<DataValueMember Name="SSOut2Enable" DataType="BOOL" Value="0" />
<DataValueMember Name="SSOut2Local" DataType="BOOL" Value="0" />
<DataValueMember Name="SSOut3Force" DataType="BOOL" Value="0" />
<DataValueMember Name="SSOut3Enable" DataType="BOOL" Value="0" />
<DataValueMember Name="SSOut3Local" DataType="BOOL" Value="0" />
<DataValueMember Name="SSCh0PWM" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="SSCh1PWM" DataType="INT" Radix="Decimal" Value="0" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="OutputData" RPI="50000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1794_VHSC:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="Ch0CurrentCount" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1CurrentCount" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch0StoredCount" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1StoredCount" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Status" DataType="INT" Radix="Binary" Value="2#0100_0000_0000_0000" />
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[0,0,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1794_VHSC:O:0">
<DataValueMember Name="CounterControl" DataType="INT" Radix="Binary" Value="2#0000_0000_0000_0000" />
<DataValueMember Name="Ch0CounterReset" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0CounterPreset" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0ValueReset" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1CounterReset" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1CounterPreset" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1ValueReset" DataType="BOOL" Value="0" />
<DataValueMember Name="OutputControl" DataType="INT" Radix="Binary" Value="2#0000_0000_0000_0000" />
<DataValueMember Name="Out0Force" DataType="BOOL" Value="0" />
<DataValueMember Name="Out0Enable" DataType="BOOL" Value="0" />
<DataValueMember Name="Out0Local" DataType="BOOL" Value="0" />
<DataValueMember Name="Out1Force" DataType="BOOL" Value="0" />
<DataValueMember Name="Out1Enable" DataType="BOOL" Value="0" />
<DataValueMember Name="Out1Local" DataType="BOOL" Value="0" />
<DataValueMember Name="Out2Force" DataType="BOOL" Value="0" />
<DataValueMember Name="Out2Enable" DataType="BOOL" Value="0" />
<DataValueMember Name="Out2Local" DataType="BOOL" Value="0" />
<DataValueMember Name="Out3Force" DataType="BOOL" Value="0" />
<DataValueMember Name="Out3Enable" DataType="BOOL" Value="0" />
<DataValueMember Name="Out3Local" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0PWMOutput" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1PWMOutput" DataType="INT" Radix="Decimal" Value="0" />
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'L5X_Samples/RobbinsGrn_2026_05_13r00.L5X', 3),
    '193-ECM-ETR/A': ("""\
<Module Name="TestMod1_193ECMETRA" CatalogNumber="1756-EN4TR" Vendor="1" ProductType="12" ProductCode="258" Major="4" Minor="1" ParentModule="Local" ParentModPortId="1" Inhibited="false" MajorFault="false" AutoDiagsEnabled="true">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="14" Type="ICP" Upstream="true" />
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="false">
<Bus />
</Port>
</Ports>
<Communications>
<ConfigData ConfigSize="16">
<Data Format="L5K">
[20,768,393217,33554433,256,0]
</Data>
</ConfigData>
<Connections>
<Connection Name="Input2" RPI="500000" Type="Input" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="false" />
</Connections>
</Communications>
</Module>

<Module Name="TestMod2_193ECMETRA" CatalogNumber="193-ECM-ETR/A" Vendor="1" ProductType="3" ProductCode="651" Major="6" Minor="1" ParentModule="TestMod1_193ECMETRA" ParentModPortId="2" Inhibited="false" MajorFault="false" SafetyEnabled="false" AutoDiagsEnabled="true">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="2" Address="192.168.1.64" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigTag ConfigSize="408" ExternalAccess="Read/Write">
<Data Format="L5K">
[412,120,0,2,4,3000,3000,10,18,75,85,[3,0,0,0,0,0,9161,256,0,0],[-1,-1,63,63,4095,4095,26623,8191,4095,4095],4095,2,5,0,32
		,4096,0,2,0,600,0,0,500,10000,100,1,10,5,0,250,200,0,10,10,0,600,10,50,250,150,10,50,50,70,10,50,35,20,5,5,10,10,35,40,10
		,35,40,10,35,40,10,10,100,90,10,100,90,10,100,90,10,10,10,10,[2,3,28,29,30,31,38,39],0,3072,-1,480,480,0,10,10,10,1000,4000
		,10,10,5000,4900,10,10,15,10,10,10,57,58,10,10,63,62,15,1,10,10,10,10,0,0,0,0,10,10,10,10,0,0,0,0,10,10,10,10,0,0,0,0,10,10,10
		,10,0,0,0,0,10,10,-90,-95,10,10,-95,-90,10,10,90,95,10,10,95,90,1,50,2,3,51,52,38,39,300,0,[10,10,10,0,0,0,0,0,0,0,0,0,0,0,0,0],[10,10
		,10,0,0,0,0,0,0,0,0,0,0,0,0,0],[10,10,10,0,0,0,0,0,0,0,0,0,0,0,0,0],[10,10,10,0,0,0,0,0,0,0,0,0,0,0,0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:E300:C:3">
<DataValueMember Name="FLA1" DataType="DINT" Radix="Decimal" Value="3000" />
<DataValueMember Name="FLA2" DataType="DINT" Radix="Decimal" Value="3000" />
<DataValueMember Name="TripClass" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="OverloadResetMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ThreePhase" DataType="BOOL" Value="1" />
<DataValueMember Name="GroundFaultFilterEn" DataType="BOOL" Value="0" />
<DataValueMember Name="GroundFaultMaxInhibitEn" DataType="BOOL" Value="0" />
<DataValueMember Name="PhaseRotationTripType_0" DataType="BOOL" Value="1" />
<DataValueMember Name="PhaseRotationTripType_1" DataType="BOOL" Value="0" />
<DataValueMember Name="PowerScale" DataType="BOOL" Value="0" />
<DataValueMember Name="VoltageScale" DataType="BOOL" Value="0" />
<DataValueMember Name="OverloadResetLevel" DataType="SINT" Radix="Decimal" Value="75" />
<DataValueMember Name="OverloadWarningLimit" DataType="SINT" Radix="Decimal" Value="85" />
<StructureMember Name="Protection" DataType="AB:E300_Protection_Struct:C:3">
<DataValueMember Name="OverloadTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="PhaseLossTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="GroundFaultTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="StallTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="JamTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderloadTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="CurrentImbalanceTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="L1UnderCurrentTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="L2UnderCurrentTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="L3UnderCurrentTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="L1OverCurrentTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="L2OverCurrentTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="L3OverCurrentTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="L1LineLossTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="L2LineLossTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="L3LineLossTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="OverloadWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="GroundFaultWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="JamWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderloadWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="CurrentImbalanceWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="L1UnderCurrentWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="L2UnderCurrentWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="L3UnderCurrentWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="L1OverCurrentWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="L2OverCurrentWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="L3OverCurrentWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="L1LineLossWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="L2LineLossWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="L3LineLossWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderVoltageTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="OverVoltageTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="VoltageImbalanceTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="PhaseRotationTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderFrequencyTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="OverFrequencyTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderVoltageWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="OverVoltageWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="VoltageImbalanceWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="PhaseRotationWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderFrequencyWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="OverFrequencyWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderRealPowerTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="OverRealPowerTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderReactivePowerConsumedTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="OverReactivePowerConsumedTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderReactivePowerGeneratedTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="OverReactivePowerGeneratedTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderApparentPowerTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="OverApparentPowerTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderPowerFactorLaggingTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="OverPowerFactorLaggingTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderPowerFactorLeadingTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="OverPowerFactorLeadingTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderRealPowerWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="OverRealPowerWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderReactivePowerConsumedWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="OverReactivePowerConsumedWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderReactivePowerGeneratedWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="OverReactivePowerGeneratedWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderApparentPowerWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="OverApparentPowerWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderPowerFactorLaggingWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="OverPowerFactorLaggingWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderPowerFactorLeadingWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="OverPowerFactorLeadingWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="TestTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="PTCTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="DeviceLogixTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="OperatorStationTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="RemoteTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="BlockedStartTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FeedbackTimeoutTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="ExpansionBusTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="MCCTestPositionTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="PTCWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="DeviceLogixWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FeedbackTimeoutWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="ExpansionBusWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="NumberOfStartsWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="OperatingHoursWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog1Ch00TripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog1Ch01TripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog1Ch02TripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog2Ch00TripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog2Ch01TripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog2Ch02TripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog3Ch00TripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog3Ch01TripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog3Ch02TripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog4Ch00TripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog4Ch01TripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog4Ch02TripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog1Ch00WarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog1Ch01WarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog1Ch02WarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog2Ch00WarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog2Ch01WarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog2Ch02WarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog3Ch00WarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog3Ch01WarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog3Ch02WarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog4Ch00WarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog4Ch01WarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog4Ch02WarningEn" DataType="BOOL" Value="0" />
</StructureMember>
<StructureMember Name="History" DataType="AB:E300_History_Struct:C:3">
<DataValueMember Name="OverloadTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="PhaseLossTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="GroundFaultTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="StallTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="JamTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="UnderloadTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="CurrentImbalanceTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="L1UnderCurrentTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="L2UnderCurrentTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="L3UnderCurrentTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="L1OverCurrentTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="L2OverCurrentTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="L3OverCurrentTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="L1LineLossTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="L2LineLossTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="L3LineLossTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="OverloadWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="GroundFaultWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="JamWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="UnderloadWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="CurrentImbalanceWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="L1UnderCurrentWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="L2UnderCurrentWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="L3UnderCurrentWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="L1OverCurrentWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="L2OverCurrentWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="L3OverCurrentWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="L1LineLossWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="L2LineLossWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="L3LineLossWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="UnderVoltageTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="OverVoltageTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="VoltageImbalanceTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="PhaseRotationTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="UnderFrequencyTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="OverFrequencyTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="UnderVoltageWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="OverVoltageWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="VoltageImbalanceWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="PhaseRotationWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="UnderFrequencyWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="OverFrequencyWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="UnderRealPowerTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="OverRealPowerTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="UnderReactivePowerConsumedTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="OverReactivePowerConsumedTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="UnderReactivePowerGeneratedTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="OverReactivePowerGeneratedTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="UnderApparentPowerTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="OverApparentPowerTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="UnderPowerFactorLaggingTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="OverPowerFactorLaggingTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="UnderPowerFactorLeadingTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="OverPowerFactorLeadingTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="UnderRealPowerWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="OverRealPowerWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="UnderReactivePowerConsumedWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="OverReactivePowerConsumedWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="UnderReactivePowerGeneratedWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="OverReactivePowerGeneratedWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="UnderApparentPowerWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="OverApparentPowerWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="UnderPowerFactorLaggingWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="OverPowerFactorLaggingWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="UnderPowerFactorLeadingWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="OverPowerFactorLeadingWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="TestTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="PTCTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="DeviceLogixTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="OperatorStationTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="RemoteTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="BlockedStartTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="HardwareFaultTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="ConfigurationTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="FeedbackTimeoutTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="ExpansionBusTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="NVMErrorTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="MCCTestPositionTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="PTCWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="DeviceLogixWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="FeedbackTimeoutWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="ExpansionBusWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="NumberOfStartsWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="OperatingHoursWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Analog1Ch00TripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Analog1Ch01TripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Analog1Ch02TripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Analog2Ch00TripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Analog2Ch01TripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Analog2Ch02TripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Analog3Ch00TripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Analog3Ch01TripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Analog3Ch02TripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Analog4Ch00TripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Analog4Ch01TripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Analog4Ch02TripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Analog1Ch00WarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Analog1Ch01WarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Analog1Ch02WarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Analog2Ch00WarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Analog2Ch01WarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Analog2Ch02WarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Analog3Ch00WarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Analog3Ch01WarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Analog3Ch02WarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Analog4Ch00WarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Analog4Ch01WarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Analog4Ch02WarningEn" DataType="BOOL" Value="1" />
</StructureMember>
<DataValueMember Name="Pt00InputFunction_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt00InputFunction_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt00InputFunction_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt00InputFunction_3" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01InputFunction_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01InputFunction_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01InputFunction_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01InputFunction_3" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02InputFunction_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02InputFunction_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02InputFunction_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02InputFunction_3" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt03InputFunction_0" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt03InputFunction_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt03InputFunction_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt03InputFunction_3" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04InputFunction_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04InputFunction_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04InputFunction_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04InputFunction_3" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt05InputFunction_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt05InputFunction_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt05InputFunction_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt05InputFunction_3" DataType="BOOL" Value="0" />
<DataValueMember Name="FLA2Select_0" DataType="BOOL" Value="0" />
<DataValueMember Name="FLA2Select_1" DataType="BOOL" Value="0" />
<DataValueMember Name="FLA2Select_2" DataType="BOOL" Value="0" />
<DataValueMember Name="FLA2Select_3" DataType="BOOL" Value="0" />
<DataValueMember Name="EmergencyStartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="StartsPerHourLimit" DataType="SINT" Radix="Decimal" Value="2" />
<DataValueMember Name="Pt00OutputFaultFinalState" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01OutputFaultFinalState" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02OutputFaultFinalState" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital1FaultFinalState" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital2FaultFinalState" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital3FaultFinalState" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital4FaultFinalState" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicDefinedDataFaultFinalState" DataType="BOOL" Value="0" />
<DataValueMember Name="StartsIntervalLimit" DataType="INT" Radix="Decimal" Value="600" />
<DataValueMember Name="TotalStartsLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="OperatingHoursLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="FeedbackTimeout" DataType="INT" Radix="Decimal" Value="500" />
<DataValueMember Name="StarterTransitionDelay" DataType="INT" Radix="Decimal" Value="10000" />
<DataValueMember Name="StarterInterlockDelay" DataType="INT" Radix="Decimal" Value="100" />
<DataValueMember Name="GroundFaultType" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="GroundFaultInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="GroundFaultTripDelay" DataType="SINT" Radix="Decimal" Value="5" />
<DataValueMember Name="GroundFaultWarnDelay" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="GroundFaultTripLimit" DataType="INT" Radix="Decimal" Value="250" />
<DataValueMember Name="GroundFaultWarnLimit" DataType="INT" Radix="Decimal" Value="200" />
<DataValueMember Name="PhaseLossInhibitTime" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="PhaseLossTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="StallEnabledTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="StallTripLimit" DataType="INT" Radix="Decimal" Value="600" />
<DataValueMember Name="JamInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="JamTripDelay" DataType="SINT" Radix="Decimal" Value="50" />
<DataValueMember Name="JamTripLimit" DataType="INT" Radix="Decimal" Value="250" />
<DataValueMember Name="JamWarnLimit" DataType="INT" Radix="Decimal" Value="150" />
<DataValueMember Name="UnderloadInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="UnderloadTripDelay" DataType="SINT" Radix="Decimal" Value="50" />
<DataValueMember Name="UnderloadTripLimit" DataType="SINT" Radix="Decimal" Value="50" />
<DataValueMember Name="UnderloadWarnLimit" DataType="SINT" Radix="Decimal" Value="70" />
<DataValueMember Name="CurrentImbalanceInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="CurrentImbalanceTripDelay" DataType="SINT" Radix="Decimal" Value="50" />
<DataValueMember Name="CurrentImbalanceTripLimit" DataType="SINT" Radix="Decimal" Value="35" />
<DataValueMember Name="CurrentImbalanceWarnLimit" DataType="SINT" Radix="Decimal" Value="20" />
<DataValueMember Name="CTPrimary" DataType="INT" Radix="Decimal" Value="5" />
<DataValueMember Name="CTSecondary" DataType="INT" Radix="Decimal" Value="5" />
<DataValueMember Name="UnderCurrentInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="L1UnderCurrentTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="L1UnderCurrentTripLimit" DataType="SINT" Radix="Decimal" Value="35" />
<DataValueMember Name="L1UnderCurrentWarnLimit" DataType="SINT" Radix="Decimal" Value="40" />
<DataValueMember Name="L2UnderCurrentTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="L2UnderCurrentTripLimit" DataType="SINT" Radix="Decimal" Value="35" />
<DataValueMember Name="L2UnderCurrentWarnLimit" DataType="SINT" Radix="Decimal" Value="40" />
<DataValueMember Name="L3UnderCurrentTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="L3UnderCurrentTripLimit" DataType="SINT" Radix="Decimal" Value="35" />
<DataValueMember Name="L3UnderCurrentWarnLimit" DataType="SINT" Radix="Decimal" Value="40" />
<DataValueMember Name="OverCurrentInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="L1OverCurrentTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="L1OverCurrentTripLimit" DataType="SINT" Radix="Decimal" Value="100" />
<DataValueMember Name="L1OverCurrentWarnLimit" DataType="SINT" Radix="Decimal" Value="90" />
<DataValueMember Name="L2OverCurrentTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="L2OverCurrentTripLimit" DataType="SINT" Radix="Decimal" Value="100" />
<DataValueMember Name="L2OverCurrentWarnLimit" DataType="SINT" Radix="Decimal" Value="90" />
<DataValueMember Name="L3OverCurrentTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="L3OverCurrentTripLimit" DataType="SINT" Radix="Decimal" Value="100" />
<DataValueMember Name="L3OverCurrentWarnLimit" DataType="SINT" Radix="Decimal" Value="90" />
<DataValueMember Name="LineLossInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="L1LineLossTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="L2LineLossTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="L3LineLossTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="Pt00OutputProtectionFaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt00OutputProtectionFaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt00OutputFaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt00OutputFaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt00OutputProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt00OutputProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01OutputProtectionFaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01OutputProtectionFaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01OutputFaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01OutputFaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01OutputProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01OutputProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02OutputProtectionFaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02OutputProtectionFaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02OutputFaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02OutputFaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02OutputProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02OutputProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital1ProtectionFaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital1ProtectionFaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital1FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital1FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital1ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital1ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital2ProtectionFaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital2ProtectionFaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital2FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital2FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital2ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital2ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital3ProtectionFaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital3ProtectionFaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital3FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital3FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital3ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital3ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital4ProtectionFaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital4ProtectionFaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital4FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital4FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital4ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital4ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="LocalControlOnCommFaultEn" DataType="BOOL" Value="1" />
<DataValueMember Name="LocalControlOnNetworkFaultEn" DataType="BOOL" Value="1" />
<DataValueMember Name="LogicDefinedDataFaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicDefinedDataFaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicDefinedDataProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicDefinedDataProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="PTPrimary" DataType="INT" Radix="Decimal" Value="480" />
<DataValueMember Name="PTSecondary" DataType="INT" Radix="Decimal" Value="480" />
<DataValueMember Name="VoltageMode" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="PhaseRotationInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="UnderVoltageInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="UnderVoltageTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="UnderVoltageTripLimit" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="UnderVoltageWarnLimit" DataType="INT" Radix="Decimal" Value="4000" />
<DataValueMember Name="OverVoltageInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="OverVoltageTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="OverVoltageTripLimit" DataType="INT" Radix="Decimal" Value="5000" />
<DataValueMember Name="OverVoltageWarnLimit" DataType="INT" Radix="Decimal" Value="4900" />
<DataValueMember Name="VoltageImbalanceInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="VoltageImbalanceTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="VoltageImbalanceTripLimit" DataType="SINT" Radix="Decimal" Value="15" />
<DataValueMember Name="VoltageImbalanceWarnLimit" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="UnderFrequencyInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="UnderFrequencyTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="UnderFrequencyTripLimit" DataType="SINT" Radix="Decimal" Value="57" />
<DataValueMember Name="UnderFrequencyWarnLimit" DataType="SINT" Radix="Decimal" Value="58" />
<DataValueMember Name="OverFrequencyInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="OverFrequencyTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="OverFrequencyTripLimit" DataType="SINT" Radix="Decimal" Value="63" />
<DataValueMember Name="OverFrequencyWarnLimit" DataType="SINT" Radix="Decimal" Value="62" />
<DataValueMember Name="DemandPeriod" DataType="SINT" Radix="Decimal" Value="15" />
<DataValueMember Name="NumberOfDemandPeriods" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="UnderRealPowerInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="UnderRealPowerTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="OverRealPowerInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="OverRealPowerTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="UnderRealPowerTripLimit" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="UnderRealPowerWarnLimit" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="OverRealPowerTripLimit" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="OverRealPowerWarnLimit" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="UnderReactivePowerConsumedInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="UnderReactivePowerConsumedTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="OverReactivePowerConsumedInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="OverReactivePowerConsumedTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="UnderReactivePowerConsumedTripLimit" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="UnderReactivePowerConsumedWarnLimit" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="OverReactivePowerConsumedTripLimit" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="OverReactivePowerConsumedWarnLimit" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="UnderReactivePowerGeneratedInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="UnderReactivePowerGeneratedTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="OverReactivePowerGeneratedInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="OverReactivePowerGeneratedTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="UnderReactivePowerGeneratedTripLimit" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="UnderReactivePowerGeneratedWarnLimit" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="OverReactivePowerGeneratedTripLimit" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="OverReactivePowerGeneratedWarnLimit" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="UnderApparentPowerInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="UnderApparentPowerTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="OverApparentPowerInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="OverApparentPowerTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="UnderApparentPowerTripLimit" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="UnderApparentPowerWarnLimit" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="OverApparentPowerTripLimit" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="OverApparentPowerWarnLimit" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="UnderPowerFactorLaggingInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="UnderPowerFactorLaggingTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="UnderPowerFactorLaggingTripLimit" DataType="SINT" Radix="Decimal" Value="-90" />
<DataValueMember Name="UnderPowerFactorLaggingWarnLimit" DataType="SINT" Radix="Decimal" Value="-95" />
<DataValueMember Name="OverPowerFactorLaggingInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="OverPowerFactorLaggingTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="OverPowerFactorLaggingTripLimit" DataType="SINT" Radix="Decimal" Value="-95" />
<DataValueMember Name="OverPowerFactorLaggingWarnLimit" DataType="SINT" Radix="Decimal" Value="-90" />
<DataValueMember Name="UnderPowerFactorLeadingInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="UnderPowerFactorLeadingTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="UnderPowerFactorLeadingTripLimit" DataType="SINT" Radix="Decimal" Value="90" />
<DataValueMember Name="UnderPowerFactorLeadingWarnLimit" DataType="SINT" Radix="Decimal" Value="95" />
<DataValueMember Name="OverPowerFactorLeadingInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="OverPowerFactorLeadingTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="OverPowerFactorLeadingTripLimit" DataType="SINT" Radix="Decimal" Value="95" />
<DataValueMember Name="OverPowerFactorLeadingWarnLimit" DataType="SINT" Radix="Decimal" Value="90" />
<DataValueMember Name="Screen1ParameterSelect1" DataType="INT" Radix="Decimal" Value="1" />
<DataValueMember Name="Screen1ParameterSelect2" DataType="INT" Radix="Decimal" Value="50" />
<DataValueMember Name="Screen2ParameterSelect1" DataType="INT" Radix="Decimal" Value="2" />
<DataValueMember Name="Screen2ParameterSelect2" DataType="INT" Radix="Decimal" Value="3" />
<DataValueMember Name="Screen3ParameterSelect1" DataType="INT" Radix="Decimal" Value="51" />
<DataValueMember Name="Screen3ParameterSelect2" DataType="INT" Radix="Decimal" Value="52" />
<DataValueMember Name="Screen4ParameterSelect1" DataType="INT" Radix="Decimal" Value="38" />
<DataValueMember Name="Screen4ParameterSelect2" DataType="INT" Radix="Decimal" Value="39" />
<DataValueMember Name="OperatorStationDisplayTimeout" DataType="INT" Radix="Decimal" Value="300" />
<StructureMember Name="Analog1" DataType="AB:E300_Analog_Struct:C:1">
<DataValueMember Name="Ch00InputTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="Ch01InputTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="Ch02InputTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="Ch00InputTripLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch00InputWarnLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch01InputTripLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch01InputWarnLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch02InputTripLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch02InputWarnLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch00InputRangeType_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputRangeType_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputRangeType_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputRangeType_3" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputRangeType_4" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputRangeType_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputRangeType_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputRangeType_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputRangeType_3" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputRangeType_4" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputRangeType_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputRangeType_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputRangeType_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputRangeType_3" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputRangeType_4" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputMode" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch00InputFormat_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputFormat_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputFormat_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputFilter_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputFilter_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputFilter_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputOpenWire_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputOpenWire_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputFormat_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputFormat_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputFormat_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputFilter_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputFilter_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputFilter_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputOpenWire_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputOpenWire_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputFormat_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputFormat_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputFormat_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputFilter_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputFilter_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputFilter_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputOpenWire_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputOpenWire_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputTempMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputTwoWireRTD" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputTempMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputTwoWireRTD" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputTempMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputTwoWireRTD" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputFaultMode_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputFaultMode_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputProtectionFaultMode_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputProtectionFaultMode_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputRangeType_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputRangeType_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputRangeType_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputRangeType_3" DataType="BOOL" Value="0" />
</StructureMember>
<StructureMember Name="Analog2" DataType="AB:E300_Analog_Struct:C:1">
<DataValueMember Name="Ch00InputTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="Ch01InputTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="Ch02InputTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="Ch00InputTripLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch00InputWarnLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch01InputTripLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch01InputWarnLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch02InputTripLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch02InputWarnLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch00InputRangeType_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputRangeType_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputRangeType_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputRangeType_3" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputRangeType_4" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputRangeType_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputRangeType_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputRangeType_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputRangeType_3" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputRangeType_4" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputRangeType_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputRangeType_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputRangeType_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputRangeType_3" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputRangeType_4" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputMode" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch00InputFormat_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputFormat_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputFormat_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputFilter_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputFilter_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputFilter_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputOpenWire_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputOpenWire_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputFormat_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputFormat_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputFormat_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputFilter_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputFilter_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputFilter_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputOpenWire_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputOpenWire_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputFormat_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputFormat_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputFormat_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputFilter_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputFilter_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputFilter_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputOpenWire_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputOpenWire_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputTempMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputTwoWireRTD" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputTempMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputTwoWireRTD" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputTempMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputTwoWireRTD" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputFaultMode_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputFaultMode_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputProtectionFaultMode_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputProtectionFaultMode_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputRangeType_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputRangeType_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputRangeType_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputRangeType_3" DataType="BOOL" Value="0" />
</StructureMember>
<StructureMember Name="Analog3" DataType="AB:E300_Analog_Struct:C:1">
<DataValueMember Name="Ch00InputTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="Ch01InputTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="Ch02InputTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="Ch00InputTripLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch00InputWarnLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch01InputTripLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch01InputWarnLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch02InputTripLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch02InputWarnLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch00InputRangeType_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputRangeType_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputRangeType_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputRangeType_3" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputRangeType_4" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputRangeType_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputRangeType_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputRangeType_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputRangeType_3" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputRangeType_4" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputRangeType_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputRangeType_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputRangeType_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputRangeType_3" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputRangeType_4" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputMode" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch00InputFormat_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputFormat_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputFormat_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputFilter_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputFilter_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputFilter_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputOpenWire_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputOpenWire_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputFormat_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputFormat_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputFormat_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputFilter_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputFilter_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputFilter_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputOpenWire_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputOpenWire_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputFormat_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputFormat_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputFormat_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputFilter_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputFilter_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputFilter_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputOpenWire_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputOpenWire_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputTempMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputTwoWireRTD" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputTempMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputTwoWireRTD" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputTempMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputTwoWireRTD" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputFaultMode_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputFaultMode_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputProtectionFaultMode_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputProtectionFaultMode_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputRangeType_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputRangeType_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputRangeType_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputRangeType_3" DataType="BOOL" Value="0" />
</StructureMember>
<StructureMember Name="Analog4" DataType="AB:E300_Analog_Struct:C:1">
<DataValueMember Name="Ch00InputTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="Ch01InputTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="Ch02InputTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="Ch00InputTripLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch00InputWarnLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch01InputTripLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch01InputWarnLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch02InputTripLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch02InputWarnLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch00InputRangeType_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputRangeType_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputRangeType_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputRangeType_3" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputRangeType_4" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputRangeType_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputRangeType_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputRangeType_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputRangeType_3" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputRangeType_4" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputRangeType_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputRangeType_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputRangeType_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputRangeType_3" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputRangeType_4" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputMode" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch00InputFormat_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputFormat_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputFormat_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputFilter_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputFilter_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputFilter_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputOpenWire_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputOpenWire_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputFormat_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputFormat_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputFormat_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputFilter_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputFilter_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputFilter_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputOpenWire_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputOpenWire_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputFormat_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputFormat_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputFormat_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputFilter_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputFilter_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputFilter_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputOpenWire_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputOpenWire_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputTempMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputTwoWireRTD" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputTempMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputTwoWireRTD" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputTempMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputTwoWireRTD" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputFaultMode_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputFaultMode_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputProtectionFaultMode_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputProtectionFaultMode_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputRangeType_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputRangeType_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputRangeType_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputRangeType_3" DataType="BOOL" Value="0" />
</StructureMember>
</Structure>
</Data>
</ConfigTag>
<ConfigScript Size="468">
<Data Format="L5K">
[-48,1,0,0,4,0,0,0,0,0,0,0,0,0,0,0,-66,1,0,0,11,1,0,0,0,1,0,0,0,2,0,0,0,-96,1,0,0,16,3,32,4,36,120,48,3,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,-72,12,0,0,8,0,0,0,72,0,0,0,0,0]
</Data>
</ConfigScript>
<Connections>
<Connection Name="Standard" RPI="50000" Type="StandardDataDriven" OutputSize="8" InputSize="156" EventID="0" ProgrammaticallySendEventTrigger="false" Priority="Scheduled" InputConnectionType="Unicast" InputProductionTrigger="Cyclic" ConnectionPath="20 04 24 78 2c 90 2c c7" InputTagSuffix="I" OutputTagSuffix="O">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:E300:I:3">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="TripPresent" DataType="BOOL" Value="0" />
<DataValueMember Name="WarningPresent" DataType="BOOL" Value="0" />
<DataValueMember Name="InvalidConfiguration" DataType="BOOL" Value="0" />
<DataValueMember Name="MotorCurrentPresent" DataType="BOOL" Value="1" />
<DataValueMember Name="GroundFaultCurrentPresent" DataType="BOOL" Value="0" />
<DataValueMember Name="MotorVoltagePresent" DataType="BOOL" Value="0" />
<DataValueMember Name="EmergencyStartEnabled" DataType="BOOL" Value="0" />
<DataValueMember Name="DeviceLogixEnabled" DataType="BOOL" Value="1" />
<DataValueMember Name="FeedbackTimeoutEnabled" DataType="BOOL" Value="0" />
<DataValueMember Name="OperatorStationPresent" DataType="BOOL" Value="0" />
<DataValueMember Name="VoltageSensingPresent" DataType="BOOL" Value="0" />
<DataValueMember Name="InternalGroundFaultSensingPresent" DataType="BOOL" Value="1" />
<DataValueMember Name="ExternalGroundFaultSensingPresent" DataType="BOOL" Value="0" />
<DataValueMember Name="PTCSensingPresent" DataType="BOOL" Value="0" />
<DataValueMember Name="Ready" DataType="BOOL" Value="1" />
<DataValueMember Name="ContolModule24VDCPresent" DataType="BOOL" Value="0" />
<DataValueMember Name="ControlModule120VACPresent" DataType="BOOL" Value="1" />
<DataValueMember Name="ControlModule240VACPresent" DataType="BOOL" Value="0" />
<DataValueMember Name="SensingModule30APresent" DataType="BOOL" Value="1" />
<DataValueMember Name="SensingModule60APresent" DataType="BOOL" Value="0" />
<DataValueMember Name="SensingModule100APresent" DataType="BOOL" Value="0" />
<DataValueMember Name="SensingModule200APresent" DataType="BOOL" Value="0" />
<DataValueMember Name="DigitalModule1Present" DataType="BOOL" Value="0" />
<DataValueMember Name="DigitalModule2Present" DataType="BOOL" Value="0" />
<DataValueMember Name="DigitalModule3Present" DataType="BOOL" Value="0" />
<DataValueMember Name="DigitalModule4Present" DataType="BOOL" Value="0" />
<DataValueMember Name="AnalogModule1Present" DataType="BOOL" Value="0" />
<DataValueMember Name="AnalogModule2Present" DataType="BOOL" Value="0" />
<DataValueMember Name="AnalogModule3Present" DataType="BOOL" Value="0" />
<DataValueMember Name="AnalogModule4Present" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt00Data" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt01Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02Data" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt03Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt05Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital1Pt00Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital1Pt01Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital1Pt02Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital1Pt03Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital2Pt00Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital2Pt01Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital2Pt02Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital2Pt03Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital3Pt00Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital3Pt01Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital3Pt02Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital3Pt03Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital4Pt00Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital4Pt01Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital4Pt02Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital4Pt03Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt00Readback" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt01Readback" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02Readback" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital1Pt00Readback" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital1Pt01Readback" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital2Pt00Readback" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital2Pt01Readback" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital3Pt00Readback" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital3Pt01Readback" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital4Pt00Readback" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital4Pt01Readback" DataType="BOOL" Value="0" />
<DataValueMember Name="OperatorStation" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="OperatorStationI" DataType="BOOL" Value="0" />
<DataValueMember Name="OperatorStationII" DataType="BOOL" Value="0" />
<DataValueMember Name="OperatorStationLocalRemote" DataType="BOOL" Value="0" />
<DataValueMember Name="OperatorStationO" DataType="BOOL" Value="0" />
<DataValueMember Name="OperatorStationReset" DataType="BOOL" Value="0" />
<DataValueMember Name="OperatorStationILEDReadback" DataType="BOOL" Value="0" />
<DataValueMember Name="OperatorStationIILEDReadback" DataType="BOOL" Value="0" />
<DataValueMember Name="OperatorStationLocalLEDReadback" DataType="BOOL" Value="0" />
<DataValueMember Name="OperatorStationRemoteLEDReadback" DataType="BOOL" Value="0" />
<DataValueMember Name="OperatorStationOLEDReadback" DataType="BOOL" Value="0" />
<StructureMember Name="Protection" DataType="AB:E300_Protection_Struct:I:3">
<DataValueMember Name="CurrentTripStatus" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="OverloadTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="PhaseLossTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="GroundFaultCurrentTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="StallTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="JamTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderloadTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="CurrentImbalanceTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="L1UnderCurrentTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="L2UnderCurrentTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="L3UnderCurrentTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="L1OverCurrentTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="L2OverCurrentTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="L3OverCurrentTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="L1LineLossTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="L2LineLossTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="L3LineLossTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="CurrentWarningStatus" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="OverloadWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="PhaseLossWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="GroundFaultCurrentWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="StallWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="JamWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderloadWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="CurrentImbalanceWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="L1UnderCurrentWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="L2UnderCurrentWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="L3UnderCurrentWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="L1OverCurrentWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="L2OverCurrentWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="L3OverCurrentWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="L1LineLossWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="L2LineLossWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="L3LineLossWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="VoltageTripStatus" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="UnderVoltageTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="OverVoltageTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="VoltageImbalanceTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="PhaseRotationMismatchTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderFrequencyTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="OverFrequencyTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="VoltageWarningStatus" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="UnderVoltageWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="OverVoltageWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="VoltageImbalanceWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="PhaseRotationMismatchWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderFrequencyWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="OverFrequencyWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="PowerTripStatus" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="UnderRealPowerTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="OverRealPowerTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderReactivePowerConsumedTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="OverReactivePowerConsumedTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderReactivePowerGeneratedTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="OverReactivePowerGeneratedTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderApparentPowerTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="OverApparentPowerTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderPowerFactorLaggingTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="OverPowerFactorLaggingTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderPowerFactorLeadingTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="OverPowerFactorLeadingTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="PowerWarningStatus" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="UnderRealPowerWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="OverRealPowerWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderReactivePowerConsumedWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="OverReactivePowerConsumedWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderReactivePowerGeneratedWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="OverReactivePowerGeneratedWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderApparentPowerWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="OverApparentPowerWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderPowerFactorLaggingWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="OverPowerFactorLaggingWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderPowerFactorLeadingWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="OverPowerFactorLeadingWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="ControlTripStatus" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="TestTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="PTCTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="DeviceLogixTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="OperatorStationTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="RemoteTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="BlockedStartTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="HardwareFaultTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="ConfigurationTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="ModuleMismatchTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="FeedbackTimeoutTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="ExpansionBusTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="NVMErrorTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="MCCTestPositionTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="ControlWarningStatus" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="PTCWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="DeviceLogixWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="ModuleMismatchWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="FeedbackTimeoutWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="ExpansionBusWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="NumberOfStartsWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="OperatingHoursWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog1Ch00Trip" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog1Ch01Trip" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog1Ch02Trip" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog2Ch00Trip" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog2Ch01Trip" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog2Ch02Trip" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog3Ch00Trip" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog3Ch01Trip" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog3Ch02Trip" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog4Ch00Trip" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog4Ch01Trip" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog4Ch02Trip" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog1Ch00Warning" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog1Ch01Warning" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog1Ch02Warning" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog2Ch00Warning" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog2Ch01Warning" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog2Ch02Warning" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog3Ch00Warning" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog3Ch01Warning" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog3Ch02Warning" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog4Ch00Warning" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog4Ch01Warning" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog4Ch02Warning" DataType="BOOL" Value="0" />
<DataValueMember Name="ControlModuleMismatch" DataType="BOOL" Value="0" />
<DataValueMember Name="SensingModuleMismatch" DataType="BOOL" Value="0" />
<DataValueMember Name="OperatorStationMismatch" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital1Mismatch" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital2Mismatch" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital3Mismatch" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital4Mismatch" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog1Mismatch" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog2Mismatch" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog3Mismatch" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog4Mismatch" DataType="BOOL" Value="0" />
</StructureMember>
<DataValueMember Name="PercentTCU" DataType="SINT" Radix="Decimal" Value="5" />
<DataValueMember Name="CurrentImbalance" DataType="SINT" Radix="Decimal" Value="8" />
<DataValueMember Name="AvgPercentFLA" DataType="INT" Radix="Decimal" Value="113" />
<DataValueMember Name="AvgCurrent" DataType="DINT" Radix="Decimal" Value="341" />
<DataValueMember Name="L1Current" DataType="DINT" Radix="Decimal" Value="312" />
<DataValueMember Name="L2Current" DataType="DINT" Radix="Decimal" Value="357" />
<DataValueMember Name="L3Current" DataType="DINT" Radix="Decimal" Value="353" />
<DataValueMember Name="GroundFaultCurrent" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="AvgLLVoltage" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="L1L2Voltage" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="L2L3Voltage" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="L3L1Voltage" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="TotalRealPower" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="TotalReactivePower" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="TotalApparentPower" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="PowerFactor" DataType="INT" Radix="Decimal" Value="0" />
<ArrayMember Name="UserDefinedData" DataType="DINT" Dimensions="8" Radix="Decimal">
<Element Index="[0]" Value="9999" />
<Element Index="[1]" Value="0" />
<Element Index="[2]" Value="3350" />
<Element Index="[3]" Value="801" />
<Element Index="[4]" Value="2" />
<Element Index="[5]" Value="0" />
<Element Index="[6]" Value="0" />
<Element Index="[7]" Value="0" />
</ArrayMember>
<DataValueMember Name="Pt00DeviceOut" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01DeviceOut" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02DeviceOut" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt03DeviceOut" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04DeviceOut" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt05DeviceOut" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt06DeviceOut" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt07DeviceOut" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt08DeviceOut" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt09DeviceOut" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt10DeviceOut" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt11DeviceOut" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt12DeviceOut" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt13DeviceOut" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt14DeviceOut" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt15DeviceOut" DataType="BOOL" Value="0" />
<DataValueMember Name="Int00DeviceOut" DataType="INT" Radix="Decimal" Value="0" />
<StructureMember Name="Analog1" DataType="AB:E300_Analog_Struct:I:1">
<DataValueMember Name="Ch00Data" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch01Data" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch02Data" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch00InputOpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputOverrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputUnderrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputOpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputOverrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputUnderrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputOpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputOverrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputUnderrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputOpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputInHold" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputOverrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputUnderrange" DataType="BOOL" Value="0" />
<DataValueMember Name="AddressChanged" DataType="BOOL" Value="0" />
<DataValueMember Name="SelftestFailed" DataType="BOOL" Value="0" />
</StructureMember>
<StructureMember Name="Analog2" DataType="AB:E300_Analog_Struct:I:1">
<DataValueMember Name="Ch00Data" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch01Data" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch02Data" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch00InputOpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputOverrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputUnderrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputOpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputOverrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputUnderrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputOpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputOverrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputUnderrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputOpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputInHold" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputOverrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputUnderrange" DataType="BOOL" Value="0" />
<DataValueMember Name="AddressChanged" DataType="BOOL" Value="0" />
<DataValueMember Name="SelftestFailed" DataType="BOOL" Value="0" />
</StructureMember>
<StructureMember Name="Analog3" DataType="AB:E300_Analog_Struct:I:1">
<DataValueMember Name="Ch00Data" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch01Data" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch02Data" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch00InputOpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputOverrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputUnderrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputOpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputOverrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputUnderrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputOpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputOverrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputUnderrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputOpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputInHold" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputOverrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputUnderrange" DataType="BOOL" Value="0" />
<DataValueMember Name="AddressChanged" DataType="BOOL" Value="0" />
<DataValueMember Name="SelftestFailed" DataType="BOOL" Value="0" />
</StructureMember>
<StructureMember Name="Analog4" DataType="AB:E300_Analog_Struct:I:1">
<DataValueMember Name="Ch00Data" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch01Data" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch02Data" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch00InputOpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputOverrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputUnderrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputOpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputOverrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputUnderrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputOpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputOverrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputUnderrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputOpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputInHold" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputOverrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputUnderrange" DataType="BOOL" Value="0" />
<DataValueMember Name="AddressChanged" DataType="BOOL" Value="0" />
<DataValueMember Name="SelftestFailed" DataType="BOOL" Value="0" />
</StructureMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[8,1,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:E300:O:1">
<DataValueMember Name="Pt00Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital1Pt00Data" DataType="BOOL" Value="1" />
<DataValueMember Name="Digital1Pt01Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital2Pt00Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital2Pt01Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital3Pt00Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital3Pt01Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital4Pt00Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital4Pt01Data" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicDefinedPt00Data" DataType="BOOL" Value="1" />
<DataValueMember Name="LogicDefinedPt01Data" DataType="BOOL" Value="0" />
<DataValueMember Name="TripReset" DataType="BOOL" Value="0" />
<DataValueMember Name="EmergencyStartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="RemoteTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="OperatorStationILED" DataType="BOOL" Value="0" />
<DataValueMember Name="OperatorStationIILED" DataType="BOOL" Value="0" />
<DataValueMember Name="OperatorStationLocalLED" DataType="BOOL" Value="0" />
<DataValueMember Name="OperatorStationRemoteLED" DataType="BOOL" Value="0" />
<DataValueMember Name="OperatorStationOLED" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt00DeviceIn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01DeviceIn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02DeviceIn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt03DeviceIn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04DeviceIn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt05DeviceIn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt06DeviceIn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt07DeviceIn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt08DeviceIn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt09DeviceIn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt10DeviceIn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt11DeviceIn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt12DeviceIn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt13DeviceIn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt14DeviceIn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt15DeviceIn" DataType="BOOL" Value="0" />
<DataValueMember Name="Int00DeviceIn" DataType="INT" Radix="Decimal" Value="0" />
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'L5X_Samples/RobbinsGrn_2026_05_13r00.L5X', 2),
    '193-ECM-ETR/B': ("""\
<Module Name="TestMod1_193ECMETRB" CatalogNumber="1756-EN4TR" Vendor="1" ProductType="12" ProductCode="258" Major="4" Minor="1" ParentModule="Local" ParentModPortId="1" Inhibited="false" MajorFault="false" AutoDiagsEnabled="true">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="14" Type="ICP" Upstream="true" />
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="false">
<Bus />
</Port>
</Ports>
<Communications>
<ConfigData ConfigSize="16">
<Data Format="L5K">
[20,768,393217,33554433,256,0]
</Data>
</ConfigData>
<Connections>
<Connection Name="Input2" RPI="500000" Type="Input" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="false" />
</Connections>
</Communications>
</Module>

<Module Name="TestMod2_193ECMETRB" CatalogNumber="193-ECM-ETR/B" Vendor="1" ProductType="3" ProductCode="651" Major="7" Minor="198" ParentModule="TestMod1_193ECMETRB" ParentModPortId="2" Inhibited="false" MajorFault="false" SafetyEnabled="false" AutoDiagsEnabled="true">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="2" Address="192.168.1.64" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigTag ConfigSize="408" ExternalAccess="Read/Write">
<Data Format="L5K">
[412,120,0,2,4,648,648,10,18,75,85,[3,0,0,0,0,0,9161,256,0,0],[-1,-1,63,63,4095,4095,26623,8191,4095,4095],4095,2,9,0,32,0
		,0,2,0,600,0,0,500,10000,100,1,10,5,0,250,200,0,10,10,0,600,10,50,250,150,10,50,50,70,10,50,35,20,5,5,10,10,35,40,10,35,40
		,10,35,40,10,10,100,90,10,100,90,10,100,90,10,10,10,10,[2,3,28,29,30,31,38,39],0,3072,-1,480,480,0,10,10,10,1000,4000,10
		,10,5000,4900,10,10,15,10,10,10,57,58,10,10,63,62,15,1,10,10,10,10,0,0,0,0,10,10,10,10,0,0,0,0,10,10,10,10,0,0,0,0,10,10,10,10
		,0,0,0,0,10,10,-90,-95,10,10,-95,-90,10,10,90,95,10,10,95,90,1,50,2,3,51,52,38,39,300,0,[10,10,10,0,0,0,0,0,0,0,0,0,0,0,0,0],[10,10,10
		,0,0,0,0,0,0,0,0,0,0,0,0,0],[10,10,10,0,0,0,0,0,0,0,0,0,0,0,0,0],[10,10,10,0,0,0,0,0,0,0,0,0,0,0,0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:E300:C:3">
<DataValueMember Name="FLA1" DataType="DINT" Radix="Decimal" Value="648" />
<DataValueMember Name="FLA2" DataType="DINT" Radix="Decimal" Value="648" />
<DataValueMember Name="TripClass" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="OverloadResetMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ThreePhase" DataType="BOOL" Value="1" />
<DataValueMember Name="GroundFaultFilterEn" DataType="BOOL" Value="0" />
<DataValueMember Name="GroundFaultMaxInhibitEn" DataType="BOOL" Value="0" />
<DataValueMember Name="PhaseRotationTripType_0" DataType="BOOL" Value="1" />
<DataValueMember Name="PhaseRotationTripType_1" DataType="BOOL" Value="0" />
<DataValueMember Name="PowerScale" DataType="BOOL" Value="0" />
<DataValueMember Name="VoltageScale" DataType="BOOL" Value="0" />
<DataValueMember Name="OverloadResetLevel" DataType="SINT" Radix="Decimal" Value="75" />
<DataValueMember Name="OverloadWarningLimit" DataType="SINT" Radix="Decimal" Value="85" />
<StructureMember Name="Protection" DataType="AB:E300_Protection_Struct:C:3">
<DataValueMember Name="OverloadTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="PhaseLossTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="GroundFaultTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="StallTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="JamTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderloadTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="CurrentImbalanceTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="L1UnderCurrentTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="L2UnderCurrentTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="L3UnderCurrentTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="L1OverCurrentTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="L2OverCurrentTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="L3OverCurrentTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="L1LineLossTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="L2LineLossTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="L3LineLossTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="OverloadWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="GroundFaultWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="JamWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderloadWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="CurrentImbalanceWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="L1UnderCurrentWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="L2UnderCurrentWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="L3UnderCurrentWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="L1OverCurrentWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="L2OverCurrentWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="L3OverCurrentWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="L1LineLossWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="L2LineLossWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="L3LineLossWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderVoltageTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="OverVoltageTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="VoltageImbalanceTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="PhaseRotationTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderFrequencyTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="OverFrequencyTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderVoltageWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="OverVoltageWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="VoltageImbalanceWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="PhaseRotationWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderFrequencyWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="OverFrequencyWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderRealPowerTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="OverRealPowerTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderReactivePowerConsumedTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="OverReactivePowerConsumedTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderReactivePowerGeneratedTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="OverReactivePowerGeneratedTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderApparentPowerTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="OverApparentPowerTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderPowerFactorLaggingTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="OverPowerFactorLaggingTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderPowerFactorLeadingTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="OverPowerFactorLeadingTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderRealPowerWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="OverRealPowerWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderReactivePowerConsumedWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="OverReactivePowerConsumedWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderReactivePowerGeneratedWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="OverReactivePowerGeneratedWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderApparentPowerWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="OverApparentPowerWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderPowerFactorLaggingWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="OverPowerFactorLaggingWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderPowerFactorLeadingWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="OverPowerFactorLeadingWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="TestTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="PTCTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="DeviceLogixTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="OperatorStationTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="RemoteTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="BlockedStartTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FeedbackTimeoutTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="ExpansionBusTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="MCCTestPositionTripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="PTCWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="DeviceLogixWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FeedbackTimeoutWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="ExpansionBusWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="NumberOfStartsWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="OperatingHoursWarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog1Ch00TripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog1Ch01TripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog1Ch02TripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog2Ch00TripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog2Ch01TripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog2Ch02TripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog3Ch00TripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog3Ch01TripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog3Ch02TripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog4Ch00TripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog4Ch01TripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog4Ch02TripEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog1Ch00WarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog1Ch01WarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog1Ch02WarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog2Ch00WarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog2Ch01WarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog2Ch02WarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog3Ch00WarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog3Ch01WarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog3Ch02WarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog4Ch00WarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog4Ch01WarningEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog4Ch02WarningEn" DataType="BOOL" Value="0" />
</StructureMember>
<StructureMember Name="History" DataType="AB:E300_History_Struct:C:3">
<DataValueMember Name="OverloadTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="PhaseLossTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="GroundFaultTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="StallTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="JamTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="UnderloadTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="CurrentImbalanceTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="L1UnderCurrentTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="L2UnderCurrentTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="L3UnderCurrentTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="L1OverCurrentTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="L2OverCurrentTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="L3OverCurrentTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="L1LineLossTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="L2LineLossTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="L3LineLossTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="OverloadWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="GroundFaultWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="JamWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="UnderloadWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="CurrentImbalanceWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="L1UnderCurrentWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="L2UnderCurrentWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="L3UnderCurrentWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="L1OverCurrentWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="L2OverCurrentWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="L3OverCurrentWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="L1LineLossWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="L2LineLossWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="L3LineLossWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="UnderVoltageTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="OverVoltageTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="VoltageImbalanceTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="PhaseRotationTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="UnderFrequencyTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="OverFrequencyTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="UnderVoltageWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="OverVoltageWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="VoltageImbalanceWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="PhaseRotationWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="UnderFrequencyWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="OverFrequencyWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="UnderRealPowerTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="OverRealPowerTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="UnderReactivePowerConsumedTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="OverReactivePowerConsumedTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="UnderReactivePowerGeneratedTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="OverReactivePowerGeneratedTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="UnderApparentPowerTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="OverApparentPowerTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="UnderPowerFactorLaggingTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="OverPowerFactorLaggingTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="UnderPowerFactorLeadingTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="OverPowerFactorLeadingTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="UnderRealPowerWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="OverRealPowerWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="UnderReactivePowerConsumedWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="OverReactivePowerConsumedWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="UnderReactivePowerGeneratedWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="OverReactivePowerGeneratedWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="UnderApparentPowerWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="OverApparentPowerWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="UnderPowerFactorLaggingWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="OverPowerFactorLaggingWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="UnderPowerFactorLeadingWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="OverPowerFactorLeadingWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="TestTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="PTCTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="DeviceLogixTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="OperatorStationTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="RemoteTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="BlockedStartTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="HardwareFaultTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="ConfigurationTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="FeedbackTimeoutTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="ExpansionBusTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="NVMErrorTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="MCCTestPositionTripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="PTCWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="DeviceLogixWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="FeedbackTimeoutWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="ExpansionBusWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="NumberOfStartsWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="OperatingHoursWarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Analog1Ch00TripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Analog1Ch01TripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Analog1Ch02TripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Analog2Ch00TripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Analog2Ch01TripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Analog2Ch02TripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Analog3Ch00TripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Analog3Ch01TripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Analog3Ch02TripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Analog4Ch00TripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Analog4Ch01TripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Analog4Ch02TripEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Analog1Ch00WarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Analog1Ch01WarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Analog1Ch02WarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Analog2Ch00WarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Analog2Ch01WarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Analog2Ch02WarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Analog3Ch00WarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Analog3Ch01WarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Analog3Ch02WarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Analog4Ch00WarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Analog4Ch01WarningEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Analog4Ch02WarningEn" DataType="BOOL" Value="1" />
</StructureMember>
<DataValueMember Name="Pt00InputFunction_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt00InputFunction_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt00InputFunction_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt00InputFunction_3" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01InputFunction_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01InputFunction_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01InputFunction_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01InputFunction_3" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02InputFunction_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02InputFunction_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02InputFunction_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02InputFunction_3" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt03InputFunction_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt03InputFunction_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt03InputFunction_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt03InputFunction_3" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04InputFunction_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04InputFunction_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04InputFunction_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04InputFunction_3" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt05InputFunction_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt05InputFunction_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt05InputFunction_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt05InputFunction_3" DataType="BOOL" Value="0" />
<DataValueMember Name="FLA2Select_0" DataType="BOOL" Value="0" />
<DataValueMember Name="FLA2Select_1" DataType="BOOL" Value="0" />
<DataValueMember Name="FLA2Select_2" DataType="BOOL" Value="0" />
<DataValueMember Name="FLA2Select_3" DataType="BOOL" Value="0" />
<DataValueMember Name="EmergencyStartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="StartsPerHourLimit" DataType="SINT" Radix="Decimal" Value="2" />
<DataValueMember Name="Pt00OutputFaultFinalState" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01OutputFaultFinalState" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02OutputFaultFinalState" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital1FaultFinalState" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital2FaultFinalState" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital3FaultFinalState" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital4FaultFinalState" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicDefinedDataFaultFinalState" DataType="BOOL" Value="0" />
<DataValueMember Name="StartsIntervalLimit" DataType="INT" Radix="Decimal" Value="600" />
<DataValueMember Name="TotalStartsLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="OperatingHoursLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="FeedbackTimeout" DataType="INT" Radix="Decimal" Value="500" />
<DataValueMember Name="StarterTransitionDelay" DataType="INT" Radix="Decimal" Value="10000" />
<DataValueMember Name="StarterInterlockDelay" DataType="INT" Radix="Decimal" Value="100" />
<DataValueMember Name="GroundFaultType" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="GroundFaultInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="GroundFaultTripDelay" DataType="SINT" Radix="Decimal" Value="5" />
<DataValueMember Name="GroundFaultWarnDelay" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="GroundFaultTripLimit" DataType="INT" Radix="Decimal" Value="250" />
<DataValueMember Name="GroundFaultWarnLimit" DataType="INT" Radix="Decimal" Value="200" />
<DataValueMember Name="PhaseLossInhibitTime" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="PhaseLossTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="StallEnabledTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="StallTripLimit" DataType="INT" Radix="Decimal" Value="600" />
<DataValueMember Name="JamInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="JamTripDelay" DataType="SINT" Radix="Decimal" Value="50" />
<DataValueMember Name="JamTripLimit" DataType="INT" Radix="Decimal" Value="250" />
<DataValueMember Name="JamWarnLimit" DataType="INT" Radix="Decimal" Value="150" />
<DataValueMember Name="UnderloadInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="UnderloadTripDelay" DataType="SINT" Radix="Decimal" Value="50" />
<DataValueMember Name="UnderloadTripLimit" DataType="SINT" Radix="Decimal" Value="50" />
<DataValueMember Name="UnderloadWarnLimit" DataType="SINT" Radix="Decimal" Value="70" />
<DataValueMember Name="CurrentImbalanceInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="CurrentImbalanceTripDelay" DataType="SINT" Radix="Decimal" Value="50" />
<DataValueMember Name="CurrentImbalanceTripLimit" DataType="SINT" Radix="Decimal" Value="35" />
<DataValueMember Name="CurrentImbalanceWarnLimit" DataType="SINT" Radix="Decimal" Value="20" />
<DataValueMember Name="CTPrimary" DataType="INT" Radix="Decimal" Value="5" />
<DataValueMember Name="CTSecondary" DataType="INT" Radix="Decimal" Value="5" />
<DataValueMember Name="UnderCurrentInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="L1UnderCurrentTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="L1UnderCurrentTripLimit" DataType="SINT" Radix="Decimal" Value="35" />
<DataValueMember Name="L1UnderCurrentWarnLimit" DataType="SINT" Radix="Decimal" Value="40" />
<DataValueMember Name="L2UnderCurrentTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="L2UnderCurrentTripLimit" DataType="SINT" Radix="Decimal" Value="35" />
<DataValueMember Name="L2UnderCurrentWarnLimit" DataType="SINT" Radix="Decimal" Value="40" />
<DataValueMember Name="L3UnderCurrentTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="L3UnderCurrentTripLimit" DataType="SINT" Radix="Decimal" Value="35" />
<DataValueMember Name="L3UnderCurrentWarnLimit" DataType="SINT" Radix="Decimal" Value="40" />
<DataValueMember Name="OverCurrentInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="L1OverCurrentTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="L1OverCurrentTripLimit" DataType="SINT" Radix="Decimal" Value="100" />
<DataValueMember Name="L1OverCurrentWarnLimit" DataType="SINT" Radix="Decimal" Value="90" />
<DataValueMember Name="L2OverCurrentTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="L2OverCurrentTripLimit" DataType="SINT" Radix="Decimal" Value="100" />
<DataValueMember Name="L2OverCurrentWarnLimit" DataType="SINT" Radix="Decimal" Value="90" />
<DataValueMember Name="L3OverCurrentTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="L3OverCurrentTripLimit" DataType="SINT" Radix="Decimal" Value="100" />
<DataValueMember Name="L3OverCurrentWarnLimit" DataType="SINT" Radix="Decimal" Value="90" />
<DataValueMember Name="LineLossInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="L1LineLossTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="L2LineLossTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="L3LineLossTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="Pt00OutputProtectionFaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt00OutputProtectionFaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt00OutputFaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt00OutputFaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt00OutputProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt00OutputProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01OutputProtectionFaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01OutputProtectionFaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01OutputFaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01OutputFaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01OutputProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01OutputProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02OutputProtectionFaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02OutputProtectionFaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02OutputFaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02OutputFaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02OutputProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02OutputProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital1ProtectionFaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital1ProtectionFaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital1FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital1FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital1ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital1ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital2ProtectionFaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital2ProtectionFaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital2FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital2FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital2ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital2ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital3ProtectionFaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital3ProtectionFaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital3FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital3FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital3ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital3ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital4ProtectionFaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital4ProtectionFaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital4FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital4FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital4ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital4ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="LocalControlOnCommFaultEn" DataType="BOOL" Value="1" />
<DataValueMember Name="LocalControlOnNetworkFaultEn" DataType="BOOL" Value="1" />
<DataValueMember Name="LogicDefinedDataFaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicDefinedDataFaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicDefinedDataProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicDefinedDataProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="PTPrimary" DataType="INT" Radix="Decimal" Value="480" />
<DataValueMember Name="PTSecondary" DataType="INT" Radix="Decimal" Value="480" />
<DataValueMember Name="VoltageMode" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="PhaseRotationInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="UnderVoltageInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="UnderVoltageTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="UnderVoltageTripLimit" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="UnderVoltageWarnLimit" DataType="INT" Radix="Decimal" Value="4000" />
<DataValueMember Name="OverVoltageInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="OverVoltageTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="OverVoltageTripLimit" DataType="INT" Radix="Decimal" Value="5000" />
<DataValueMember Name="OverVoltageWarnLimit" DataType="INT" Radix="Decimal" Value="4900" />
<DataValueMember Name="VoltageImbalanceInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="VoltageImbalanceTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="VoltageImbalanceTripLimit" DataType="SINT" Radix="Decimal" Value="15" />
<DataValueMember Name="VoltageImbalanceWarnLimit" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="UnderFrequencyInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="UnderFrequencyTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="UnderFrequencyTripLimit" DataType="SINT" Radix="Decimal" Value="57" />
<DataValueMember Name="UnderFrequencyWarnLimit" DataType="SINT" Radix="Decimal" Value="58" />
<DataValueMember Name="OverFrequencyInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="OverFrequencyTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="OverFrequencyTripLimit" DataType="SINT" Radix="Decimal" Value="63" />
<DataValueMember Name="OverFrequencyWarnLimit" DataType="SINT" Radix="Decimal" Value="62" />
<DataValueMember Name="DemandPeriod" DataType="SINT" Radix="Decimal" Value="15" />
<DataValueMember Name="NumberOfDemandPeriods" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="UnderRealPowerInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="UnderRealPowerTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="OverRealPowerInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="OverRealPowerTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="UnderRealPowerTripLimit" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="UnderRealPowerWarnLimit" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="OverRealPowerTripLimit" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="OverRealPowerWarnLimit" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="UnderReactivePowerConsumedInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="UnderReactivePowerConsumedTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="OverReactivePowerConsumedInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="OverReactivePowerConsumedTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="UnderReactivePowerConsumedTripLimit" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="UnderReactivePowerConsumedWarnLimit" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="OverReactivePowerConsumedTripLimit" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="OverReactivePowerConsumedWarnLimit" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="UnderReactivePowerGeneratedInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="UnderReactivePowerGeneratedTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="OverReactivePowerGeneratedInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="OverReactivePowerGeneratedTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="UnderReactivePowerGeneratedTripLimit" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="UnderReactivePowerGeneratedWarnLimit" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="OverReactivePowerGeneratedTripLimit" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="OverReactivePowerGeneratedWarnLimit" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="UnderApparentPowerInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="UnderApparentPowerTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="OverApparentPowerInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="OverApparentPowerTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="UnderApparentPowerTripLimit" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="UnderApparentPowerWarnLimit" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="OverApparentPowerTripLimit" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="OverApparentPowerWarnLimit" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="UnderPowerFactorLaggingInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="UnderPowerFactorLaggingTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="UnderPowerFactorLaggingTripLimit" DataType="SINT" Radix="Decimal" Value="-90" />
<DataValueMember Name="UnderPowerFactorLaggingWarnLimit" DataType="SINT" Radix="Decimal" Value="-95" />
<DataValueMember Name="OverPowerFactorLaggingInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="OverPowerFactorLaggingTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="OverPowerFactorLaggingTripLimit" DataType="SINT" Radix="Decimal" Value="-95" />
<DataValueMember Name="OverPowerFactorLaggingWarnLimit" DataType="SINT" Radix="Decimal" Value="-90" />
<DataValueMember Name="UnderPowerFactorLeadingInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="UnderPowerFactorLeadingTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="UnderPowerFactorLeadingTripLimit" DataType="SINT" Radix="Decimal" Value="90" />
<DataValueMember Name="UnderPowerFactorLeadingWarnLimit" DataType="SINT" Radix="Decimal" Value="95" />
<DataValueMember Name="OverPowerFactorLeadingInhibitTime" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="OverPowerFactorLeadingTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="OverPowerFactorLeadingTripLimit" DataType="SINT" Radix="Decimal" Value="95" />
<DataValueMember Name="OverPowerFactorLeadingWarnLimit" DataType="SINT" Radix="Decimal" Value="90" />
<DataValueMember Name="Screen1ParameterSelect1" DataType="INT" Radix="Decimal" Value="1" />
<DataValueMember Name="Screen1ParameterSelect2" DataType="INT" Radix="Decimal" Value="50" />
<DataValueMember Name="Screen2ParameterSelect1" DataType="INT" Radix="Decimal" Value="2" />
<DataValueMember Name="Screen2ParameterSelect2" DataType="INT" Radix="Decimal" Value="3" />
<DataValueMember Name="Screen3ParameterSelect1" DataType="INT" Radix="Decimal" Value="51" />
<DataValueMember Name="Screen3ParameterSelect2" DataType="INT" Radix="Decimal" Value="52" />
<DataValueMember Name="Screen4ParameterSelect1" DataType="INT" Radix="Decimal" Value="38" />
<DataValueMember Name="Screen4ParameterSelect2" DataType="INT" Radix="Decimal" Value="39" />
<DataValueMember Name="OperatorStationDisplayTimeout" DataType="INT" Radix="Decimal" Value="300" />
<StructureMember Name="Analog1" DataType="AB:E300_Analog_Struct:C:1">
<DataValueMember Name="Ch00InputTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="Ch01InputTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="Ch02InputTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="Ch00InputTripLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch00InputWarnLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch01InputTripLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch01InputWarnLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch02InputTripLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch02InputWarnLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch00InputRangeType_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputRangeType_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputRangeType_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputRangeType_3" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputRangeType_4" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputRangeType_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputRangeType_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputRangeType_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputRangeType_3" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputRangeType_4" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputRangeType_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputRangeType_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputRangeType_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputRangeType_3" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputRangeType_4" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputMode" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch00InputFormat_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputFormat_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputFormat_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputFilter_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputFilter_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputFilter_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputOpenWire_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputOpenWire_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputFormat_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputFormat_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputFormat_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputFilter_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputFilter_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputFilter_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputOpenWire_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputOpenWire_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputFormat_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputFormat_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputFormat_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputFilter_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputFilter_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputFilter_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputOpenWire_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputOpenWire_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputTempMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputTwoWireRTD" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputTempMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputTwoWireRTD" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputTempMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputTwoWireRTD" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputFaultMode_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputFaultMode_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputProtectionFaultMode_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputProtectionFaultMode_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputRangeType_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputRangeType_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputRangeType_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputRangeType_3" DataType="BOOL" Value="0" />
</StructureMember>
<StructureMember Name="Analog2" DataType="AB:E300_Analog_Struct:C:1">
<DataValueMember Name="Ch00InputTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="Ch01InputTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="Ch02InputTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="Ch00InputTripLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch00InputWarnLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch01InputTripLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch01InputWarnLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch02InputTripLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch02InputWarnLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch00InputRangeType_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputRangeType_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputRangeType_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputRangeType_3" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputRangeType_4" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputRangeType_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputRangeType_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputRangeType_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputRangeType_3" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputRangeType_4" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputRangeType_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputRangeType_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputRangeType_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputRangeType_3" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputRangeType_4" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputMode" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch00InputFormat_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputFormat_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputFormat_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputFilter_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputFilter_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputFilter_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputOpenWire_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputOpenWire_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputFormat_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputFormat_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputFormat_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputFilter_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputFilter_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputFilter_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputOpenWire_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputOpenWire_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputFormat_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputFormat_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputFormat_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputFilter_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputFilter_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputFilter_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputOpenWire_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputOpenWire_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputTempMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputTwoWireRTD" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputTempMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputTwoWireRTD" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputTempMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputTwoWireRTD" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputFaultMode_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputFaultMode_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputProtectionFaultMode_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputProtectionFaultMode_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputRangeType_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputRangeType_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputRangeType_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputRangeType_3" DataType="BOOL" Value="0" />
</StructureMember>
<StructureMember Name="Analog3" DataType="AB:E300_Analog_Struct:C:1">
<DataValueMember Name="Ch00InputTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="Ch01InputTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="Ch02InputTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="Ch00InputTripLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch00InputWarnLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch01InputTripLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch01InputWarnLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch02InputTripLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch02InputWarnLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch00InputRangeType_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputRangeType_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputRangeType_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputRangeType_3" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputRangeType_4" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputRangeType_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputRangeType_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputRangeType_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputRangeType_3" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputRangeType_4" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputRangeType_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputRangeType_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputRangeType_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputRangeType_3" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputRangeType_4" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputMode" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch00InputFormat_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputFormat_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputFormat_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputFilter_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputFilter_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputFilter_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputOpenWire_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputOpenWire_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputFormat_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputFormat_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputFormat_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputFilter_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputFilter_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputFilter_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputOpenWire_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputOpenWire_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputFormat_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputFormat_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputFormat_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputFilter_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputFilter_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputFilter_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputOpenWire_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputOpenWire_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputTempMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputTwoWireRTD" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputTempMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputTwoWireRTD" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputTempMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputTwoWireRTD" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputFaultMode_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputFaultMode_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputProtectionFaultMode_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputProtectionFaultMode_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputRangeType_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputRangeType_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputRangeType_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputRangeType_3" DataType="BOOL" Value="0" />
</StructureMember>
<StructureMember Name="Analog4" DataType="AB:E300_Analog_Struct:C:1">
<DataValueMember Name="Ch00InputTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="Ch01InputTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="Ch02InputTripDelay" DataType="SINT" Radix="Decimal" Value="10" />
<DataValueMember Name="Ch00InputTripLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch00InputWarnLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch01InputTripLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch01InputWarnLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch02InputTripLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch02InputWarnLimit" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch00InputRangeType_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputRangeType_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputRangeType_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputRangeType_3" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputRangeType_4" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputRangeType_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputRangeType_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputRangeType_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputRangeType_3" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputRangeType_4" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputRangeType_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputRangeType_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputRangeType_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputRangeType_3" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputRangeType_4" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputMode" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch00InputFormat_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputFormat_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputFormat_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputFilter_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputFilter_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputFilter_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputOpenWire_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputOpenWire_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputFormat_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputFormat_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputFormat_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputFilter_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputFilter_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputFilter_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputOpenWire_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputOpenWire_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputFormat_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputFormat_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputFormat_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputFilter_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputFilter_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputFilter_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputOpenWire_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputOpenWire_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputTempMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputTwoWireRTD" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputTempMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputTwoWireRTD" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputTempMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputTwoWireRTD" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputFaultMode_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputFaultMode_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputProtectionFaultMode_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputProtectionFaultMode_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputRangeType_0" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputRangeType_1" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputRangeType_2" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputRangeType_3" DataType="BOOL" Value="0" />
</StructureMember>
</Structure>
</Data>
</ConfigTag>
<ConfigScript Size="468">
<Data Format="L5K">
[-48,1,0,0,4,0,0,0,0,0,0,0,0,0,0,0,-66,1,0,0,11,1,0,0,0,1,0,0,0,2,0,0,0,-96,1,0,0,16,3,32,4,36,120,48,3,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,-72,12,0,0,8,0,0,0,72,0,0,0,0,0]
</Data>
</ConfigScript>
<Connections>
<Connection Name="Standard" RPI="100000" Type="StandardDataDriven" OutputSize="8" InputSize="156" EventID="0" ProgrammaticallySendEventTrigger="false" Priority="Scheduled" InputConnectionType="Unicast" InputProductionTrigger="Cyclic" ConnectionPath="20 04 24 78 2c 90 2c c7" InputTagSuffix="I" OutputTagSuffix="O">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:E300:I:3">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="TripPresent" DataType="BOOL" Value="0" />
<DataValueMember Name="WarningPresent" DataType="BOOL" Value="0" />
<DataValueMember Name="InvalidConfiguration" DataType="BOOL" Value="0" />
<DataValueMember Name="MotorCurrentPresent" DataType="BOOL" Value="1" />
<DataValueMember Name="GroundFaultCurrentPresent" DataType="BOOL" Value="0" />
<DataValueMember Name="MotorVoltagePresent" DataType="BOOL" Value="0" />
<DataValueMember Name="EmergencyStartEnabled" DataType="BOOL" Value="0" />
<DataValueMember Name="DeviceLogixEnabled" DataType="BOOL" Value="1" />
<DataValueMember Name="FeedbackTimeoutEnabled" DataType="BOOL" Value="0" />
<DataValueMember Name="OperatorStationPresent" DataType="BOOL" Value="0" />
<DataValueMember Name="VoltageSensingPresent" DataType="BOOL" Value="0" />
<DataValueMember Name="InternalGroundFaultSensingPresent" DataType="BOOL" Value="0" />
<DataValueMember Name="ExternalGroundFaultSensingPresent" DataType="BOOL" Value="0" />
<DataValueMember Name="PTCSensingPresent" DataType="BOOL" Value="0" />
<DataValueMember Name="Ready" DataType="BOOL" Value="1" />
<DataValueMember Name="ContolModule24VDCPresent" DataType="BOOL" Value="0" />
<DataValueMember Name="ControlModule120VACPresent" DataType="BOOL" Value="1" />
<DataValueMember Name="ControlModule240VACPresent" DataType="BOOL" Value="0" />
<DataValueMember Name="SensingModule30APresent" DataType="BOOL" Value="1" />
<DataValueMember Name="SensingModule60APresent" DataType="BOOL" Value="0" />
<DataValueMember Name="SensingModule100APresent" DataType="BOOL" Value="0" />
<DataValueMember Name="SensingModule200APresent" DataType="BOOL" Value="0" />
<DataValueMember Name="DigitalModule1Present" DataType="BOOL" Value="0" />
<DataValueMember Name="DigitalModule2Present" DataType="BOOL" Value="0" />
<DataValueMember Name="DigitalModule3Present" DataType="BOOL" Value="0" />
<DataValueMember Name="DigitalModule4Present" DataType="BOOL" Value="0" />
<DataValueMember Name="AnalogModule1Present" DataType="BOOL" Value="0" />
<DataValueMember Name="AnalogModule2Present" DataType="BOOL" Value="0" />
<DataValueMember Name="AnalogModule3Present" DataType="BOOL" Value="0" />
<DataValueMember Name="AnalogModule4Present" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt00Data" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt01Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02Data" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt03Data" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt04Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt05Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital1Pt00Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital1Pt01Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital1Pt02Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital1Pt03Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital2Pt00Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital2Pt01Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital2Pt02Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital2Pt03Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital3Pt00Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital3Pt01Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital3Pt02Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital3Pt03Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital4Pt00Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital4Pt01Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital4Pt02Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital4Pt03Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt00Readback" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt01Readback" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02Readback" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital1Pt00Readback" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital1Pt01Readback" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital2Pt00Readback" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital2Pt01Readback" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital3Pt00Readback" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital3Pt01Readback" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital4Pt00Readback" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital4Pt01Readback" DataType="BOOL" Value="0" />
<DataValueMember Name="OperatorStation" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="OperatorStationI" DataType="BOOL" Value="0" />
<DataValueMember Name="OperatorStationII" DataType="BOOL" Value="0" />
<DataValueMember Name="OperatorStationLocalRemote" DataType="BOOL" Value="0" />
<DataValueMember Name="OperatorStationO" DataType="BOOL" Value="0" />
<DataValueMember Name="OperatorStationReset" DataType="BOOL" Value="0" />
<DataValueMember Name="OperatorStationILEDReadback" DataType="BOOL" Value="0" />
<DataValueMember Name="OperatorStationIILEDReadback" DataType="BOOL" Value="0" />
<DataValueMember Name="OperatorStationLocalLEDReadback" DataType="BOOL" Value="0" />
<DataValueMember Name="OperatorStationRemoteLEDReadback" DataType="BOOL" Value="0" />
<DataValueMember Name="OperatorStationOLEDReadback" DataType="BOOL" Value="0" />
<StructureMember Name="Protection" DataType="AB:E300_Protection_Struct:I:3">
<DataValueMember Name="CurrentTripStatus" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="OverloadTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="PhaseLossTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="GroundFaultCurrentTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="StallTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="JamTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderloadTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="CurrentImbalanceTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="L1UnderCurrentTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="L2UnderCurrentTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="L3UnderCurrentTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="L1OverCurrentTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="L2OverCurrentTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="L3OverCurrentTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="L1LineLossTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="L2LineLossTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="L3LineLossTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="CurrentWarningStatus" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="OverloadWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="PhaseLossWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="GroundFaultCurrentWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="StallWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="JamWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderloadWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="CurrentImbalanceWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="L1UnderCurrentWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="L2UnderCurrentWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="L3UnderCurrentWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="L1OverCurrentWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="L2OverCurrentWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="L3OverCurrentWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="L1LineLossWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="L2LineLossWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="L3LineLossWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="VoltageTripStatus" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="UnderVoltageTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="OverVoltageTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="VoltageImbalanceTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="PhaseRotationMismatchTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderFrequencyTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="OverFrequencyTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="VoltageWarningStatus" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="UnderVoltageWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="OverVoltageWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="VoltageImbalanceWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="PhaseRotationMismatchWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderFrequencyWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="OverFrequencyWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="PowerTripStatus" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="UnderRealPowerTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="OverRealPowerTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderReactivePowerConsumedTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="OverReactivePowerConsumedTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderReactivePowerGeneratedTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="OverReactivePowerGeneratedTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderApparentPowerTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="OverApparentPowerTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderPowerFactorLaggingTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="OverPowerFactorLaggingTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderPowerFactorLeadingTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="OverPowerFactorLeadingTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="PowerWarningStatus" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="UnderRealPowerWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="OverRealPowerWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderReactivePowerConsumedWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="OverReactivePowerConsumedWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderReactivePowerGeneratedWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="OverReactivePowerGeneratedWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderApparentPowerWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="OverApparentPowerWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderPowerFactorLaggingWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="OverPowerFactorLaggingWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="UnderPowerFactorLeadingWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="OverPowerFactorLeadingWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="ControlTripStatus" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="TestTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="PTCTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="DeviceLogixTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="OperatorStationTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="RemoteTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="BlockedStartTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="HardwareFaultTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="ConfigurationTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="ModuleMismatchTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="FeedbackTimeoutTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="ExpansionBusTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="NVMErrorTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="MCCTestPositionTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="ControlWarningStatus" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="PTCWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="DeviceLogixWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="ModuleMismatchWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="FeedbackTimeoutWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="ExpansionBusWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="NumberOfStartsWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="OperatingHoursWarning" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog1Ch00Trip" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog1Ch01Trip" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog1Ch02Trip" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog2Ch00Trip" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog2Ch01Trip" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog2Ch02Trip" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog3Ch00Trip" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog3Ch01Trip" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog3Ch02Trip" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog4Ch00Trip" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog4Ch01Trip" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog4Ch02Trip" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog1Ch00Warning" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog1Ch01Warning" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog1Ch02Warning" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog2Ch00Warning" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog2Ch01Warning" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog2Ch02Warning" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog3Ch00Warning" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog3Ch01Warning" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog3Ch02Warning" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog4Ch00Warning" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog4Ch01Warning" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog4Ch02Warning" DataType="BOOL" Value="0" />
<DataValueMember Name="ControlModuleMismatch" DataType="BOOL" Value="0" />
<DataValueMember Name="SensingModuleMismatch" DataType="BOOL" Value="0" />
<DataValueMember Name="OperatorStationMismatch" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital1Mismatch" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital2Mismatch" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital3Mismatch" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital4Mismatch" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog1Mismatch" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog2Mismatch" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog3Mismatch" DataType="BOOL" Value="0" />
<DataValueMember Name="Analog4Mismatch" DataType="BOOL" Value="0" />
</StructureMember>
<DataValueMember Name="PercentTCU" DataType="SINT" Radix="Decimal" Value="25" />
<DataValueMember Name="CurrentImbalance" DataType="SINT" Radix="Decimal" Value="4" />
<DataValueMember Name="AvgPercentFLA" DataType="INT" Radix="Decimal" Value="544" />
<DataValueMember Name="AvgCurrent" DataType="DINT" Radix="Decimal" Value="352" />
<DataValueMember Name="L1Current" DataType="DINT" Radix="Decimal" Value="340" />
<DataValueMember Name="L2Current" DataType="DINT" Radix="Decimal" Value="362" />
<DataValueMember Name="L3Current" DataType="DINT" Radix="Decimal" Value="355" />
<DataValueMember Name="GroundFaultCurrent" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="AvgLLVoltage" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="L1L2Voltage" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="L2L3Voltage" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="L3L1Voltage" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="TotalRealPower" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="TotalReactivePower" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="TotalApparentPower" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="PowerFactor" DataType="INT" Radix="Decimal" Value="0" />
<ArrayMember Name="UserDefinedData" DataType="DINT" Dimensions="8" Radix="Decimal">
<Element Index="[0]" Value="9999" />
<Element Index="[1]" Value="0" />
<Element Index="[2]" Value="3242" />
<Element Index="[3]" Value="753" />
<Element Index="[4]" Value="2" />
<Element Index="[5]" Value="0" />
<Element Index="[6]" Value="0" />
<Element Index="[7]" Value="0" />
</ArrayMember>
<DataValueMember Name="Pt00DeviceOut" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01DeviceOut" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02DeviceOut" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt03DeviceOut" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04DeviceOut" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt05DeviceOut" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt06DeviceOut" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt07DeviceOut" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt08DeviceOut" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt09DeviceOut" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt10DeviceOut" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt11DeviceOut" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt12DeviceOut" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt13DeviceOut" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt14DeviceOut" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt15DeviceOut" DataType="BOOL" Value="0" />
<DataValueMember Name="Int00DeviceOut" DataType="INT" Radix="Decimal" Value="0" />
<StructureMember Name="Analog1" DataType="AB:E300_Analog_Struct:I:1">
<DataValueMember Name="Ch00Data" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch01Data" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch02Data" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch00InputOpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputOverrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputUnderrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputOpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputOverrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputUnderrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputOpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputOverrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputUnderrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputOpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputInHold" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputOverrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputUnderrange" DataType="BOOL" Value="0" />
<DataValueMember Name="AddressChanged" DataType="BOOL" Value="0" />
<DataValueMember Name="SelftestFailed" DataType="BOOL" Value="0" />
</StructureMember>
<StructureMember Name="Analog2" DataType="AB:E300_Analog_Struct:I:1">
<DataValueMember Name="Ch00Data" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch01Data" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch02Data" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch00InputOpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputOverrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputUnderrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputOpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputOverrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputUnderrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputOpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputOverrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputUnderrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputOpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputInHold" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputOverrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputUnderrange" DataType="BOOL" Value="0" />
<DataValueMember Name="AddressChanged" DataType="BOOL" Value="0" />
<DataValueMember Name="SelftestFailed" DataType="BOOL" Value="0" />
</StructureMember>
<StructureMember Name="Analog3" DataType="AB:E300_Analog_Struct:I:1">
<DataValueMember Name="Ch00Data" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch01Data" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch02Data" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch00InputOpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputOverrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputUnderrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputOpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputOverrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputUnderrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputOpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputOverrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputUnderrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputOpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputInHold" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputOverrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputUnderrange" DataType="BOOL" Value="0" />
<DataValueMember Name="AddressChanged" DataType="BOOL" Value="0" />
<DataValueMember Name="SelftestFailed" DataType="BOOL" Value="0" />
</StructureMember>
<StructureMember Name="Analog4" DataType="AB:E300_Analog_Struct:I:1">
<DataValueMember Name="Ch00Data" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch01Data" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch02Data" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch00InputOpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputOverrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00InputUnderrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputOpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputOverrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch01InputUnderrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputOpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputOverrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch02InputUnderrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputOpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputInHold" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputOverrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch00OutputUnderrange" DataType="BOOL" Value="0" />
<DataValueMember Name="AddressChanged" DataType="BOOL" Value="0" />
<DataValueMember Name="SelftestFailed" DataType="BOOL" Value="0" />
</StructureMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[0,1,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:E300:O:1">
<DataValueMember Name="Pt00Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital1Pt00Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital1Pt01Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital2Pt00Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital2Pt01Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital3Pt00Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital3Pt01Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital4Pt00Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Digital4Pt01Data" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicDefinedPt00Data" DataType="BOOL" Value="1" />
<DataValueMember Name="LogicDefinedPt01Data" DataType="BOOL" Value="0" />
<DataValueMember Name="TripReset" DataType="BOOL" Value="0" />
<DataValueMember Name="EmergencyStartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="RemoteTrip" DataType="BOOL" Value="0" />
<DataValueMember Name="OperatorStationILED" DataType="BOOL" Value="0" />
<DataValueMember Name="OperatorStationIILED" DataType="BOOL" Value="0" />
<DataValueMember Name="OperatorStationLocalLED" DataType="BOOL" Value="0" />
<DataValueMember Name="OperatorStationRemoteLED" DataType="BOOL" Value="0" />
<DataValueMember Name="OperatorStationOLED" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt00DeviceIn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01DeviceIn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02DeviceIn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt03DeviceIn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04DeviceIn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt05DeviceIn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt06DeviceIn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt07DeviceIn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt08DeviceIn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt09DeviceIn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt10DeviceIn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt11DeviceIn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt12DeviceIn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt13DeviceIn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt14DeviceIn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt15DeviceIn" DataType="BOOL" Value="0" />
<DataValueMember Name="Int00DeviceIn" DataType="INT" Radix="Decimal" Value="0" />
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'L5X_Samples/RobbinsGrn_2026_05_13r00.L5X', 2),
    '2097-V34PR5-LM': ("""\
<Module Name="TestMod1_2097V34PR5LM" CatalogNumber="2097-V34PR5-LM" Vendor="1" ProductType="37" ProductCode="37" Major="2" Minor="4" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="220">
<Data Format="L5K">
[224,1,257,37,37,0,10000,16908292,0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,8192005,8192125,67305985
		,5,0,0,0,0,0,0]
</Data>
</ConfigData>
<Connections>
<Connection Name="MotionDiagnostics" RPI="1000" Type="DiagnosticInput" EventID="0" ProgrammaticallySendEventTrigger="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:Motion_Diagnostics:S:1">
<DataValueMember Name="LostControllerToDriveTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LateControllerToDriveTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LostDriveToControllerTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LateDriveToControllerTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="TimingStatisticsEnabled" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="ControllerToDriveConnectionSize" DataType="INT" Radix="Decimal" Value="44" />
<DataValueMember Name="DriveToControllerConnectionSize" DataType="INT" Radix="Decimal" Value="36" />
<DataValueMember Name="NominalControllerToDriveTime" DataType="INT" Radix="Decimal" Value="2000" />
<DataValueMember Name="NominalDriveToControllerTime" DataType="INT" Radix="Decimal" Value="2000" />
<DataValueMember Name="CoarseUpdatePeriod" DataType="INT" Radix="Decimal" Value="4000" />
</Structure>
</Data>
</InputTag>
</Connection>
<Connection Name="MotionSync" RPI="4000" Type="MotionSync" EventID="0" ProgrammaticallySendEventTrigger="false" />
</Connections>
</Communications>
</Module>
""", 'BAI10048_TrimmerTally_20250704.L5X', 1),
    '2198-C4004-ERS': ("""\
<Module Name="TestMod1_2198C4004ERS" CatalogNumber="2198-C4004-ERS" Vendor="1" ProductType="37" ProductCode="78" Major="13" Minor="1" ParentModule="Local" ParentModPortId="4" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="468">
<Data Format="L5K">
[472,7,257,78,32113775,16,10000,33686020,1,0,0,0,0,0,0,0,0,-1027080192,0,0,0,0,0,0,0,0,0,0,0,0,0,16843009,16843009
		,0,0,33554432,230,-65536,1045220557,0,0,0,0,1120403456,1120403456,0,1120403456,1124859904,0,0,1120403456
		,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,0,257,0,0,0,8192000,8192125,67305984,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,778,0,10,0]
</Data>
</ConfigData>
<Connections>
<Connection Name="A_MotionDiagnostics" RPI="1000" Type="DiagnosticInput" EventID="0" ProgrammaticallySendEventTrigger="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:Motion_Diagnostics:S:1">
<DataValueMember Name="LostControllerToDriveTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LateControllerToDriveTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LostDriveToControllerTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LateDriveToControllerTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="TimingStatisticsEnabled" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="ControllerToDriveConnectionSize" DataType="INT" Radix="Decimal" Value="44" />
<DataValueMember Name="DriveToControllerConnectionSize" DataType="INT" Radix="Decimal" Value="40" />
<DataValueMember Name="NominalControllerToDriveTime" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="NominalDriveToControllerTime" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="CoarseUpdatePeriod" DataType="INT" Radix="Decimal" Value="2000" />
</Structure>
</Data>
</InputTag>
</Connection>
<Connection Name="B_MotionSync" RPI="2000" Type="MotionSync" EventID="0" ProgrammaticallySendEventTrigger="false" />
</Connections>
</Communications>
</Module>
""", 'DnR_Personal/Fisher_Synergy_Bead_20240725.L5X', 1),
    '2198-H008-ERS': ("""\
<Module Name="TestMod1_2198H008ERS" CatalogNumber="2198-H008-ERS" Vendor="1" ProductType="37" ProductCode="47" Major="7" Minor="1" ParentModule="Local" ParentModPortId="4" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="376">
<Data Format="L5K">
[380,3,257,47,430572775,0,2565904,131588,1,0,0,0,0,0,0,0,0,-1027080192,0,0,0,0,0,0,0,524296000,524296000,524296000
		,524296000,0,0,1,0,0,460,-65536,1045220557,0,0,0,0,1120403456,1120403456,0,1120403456,1124859904,0,0,1120403456
		,1,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,1,0,8192000,8192125,1034,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
</Data>
</ConfigData>
<Connections>
<Connection Name="MotionDiagnostics" RPI="1000" Type="DiagnosticInput" EventID="0" ProgrammaticallySendEventTrigger="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:Motion_Diagnostics:S:1">
<DataValueMember Name="LostControllerToDriveTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LateControllerToDriveTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LostDriveToControllerTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LateDriveToControllerTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="TimingStatisticsEnabled" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="ControllerToDriveConnectionSize" DataType="INT" Radix="Decimal" Value="44" />
<DataValueMember Name="DriveToControllerConnectionSize" DataType="INT" Radix="Decimal" Value="36" />
<DataValueMember Name="NominalControllerToDriveTime" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="NominalDriveToControllerTime" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="CoarseUpdatePeriod" DataType="INT" Radix="Decimal" Value="2000" />
</Structure>
</Data>
</InputTag>
</Connection>
<Connection Name="MotionSync" RPI="2000" Type="MotionSync" EventID="0" ProgrammaticallySendEventTrigger="false" />
</Connections>
</Communications>
</Module>
""", 'DnR_Personal/FlareFunction_311D_240731.L5X', 1),
    '2198-P031': ("""\
<Module Name="TestMod1_2198P031" CatalogNumber="2198-P031" Vendor="1" ProductType="48" ProductCode="1" Major="11" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="376">
<Data Format="L5K">
[380,3,257,1,25822311,2,2565904,131588,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,-65280,0,0,0,0,0,1120403456,0,0,1120403456
		,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
</Data>
</ConfigData>
<Connections>
<Connection Name="A_MotionDiagnostics" RPI="1000" Type="DiagnosticInput" EventID="0" ProgrammaticallySendEventTrigger="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:MotionDevice_Diagnostics:S:0">
<DataValueMember Name="LostControllerToDeviceTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LateControllerToDeviceTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LostDeviceToControllerTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LateDeviceToControllerTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastControllerToDeviceTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageControllerToDeviceTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumControllerToDeviceTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastDeviceToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageDeviceToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumDeviceToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="TimingStatisticsEnabled" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="ControllerToDeviceConnectionSize" DataType="INT" Radix="Decimal" Value="36" />
<DataValueMember Name="DeviceToControllerConnectionSize" DataType="INT" Radix="Decimal" Value="36" />
<DataValueMember Name="NominalControllerToDeviceTime" DataType="INT" Radix="Decimal" Value="2000" />
<DataValueMember Name="NominalDeviceToControllerTime" DataType="INT" Radix="Decimal" Value="2000" />
<DataValueMember Name="CoarseUpdatePeriod" DataType="INT" Radix="Decimal" Value="4000" />
</Structure>
</Data>
</InputTag>
</Connection>
<Connection Name="B_MotionSync" RPI="4000" Type="MotionSync" EventID="0" ProgrammaticallySendEventTrigger="false" />
</Connections>
</Communications>
</Module>
""", 'DnR_Personal/Bender134053_201104.L5X', 1),
    '2198-P070': ("""\
<Module Name="TestMod1_2198P070" CatalogNumber="2198-P070" Vendor="1" ProductType="48" ProductCode="2" Major="11" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="376">
<Data Format="L5K">
[380,3,257,2,25822311,2,2565904,131588,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,-65024,0,0,0,0,0,1120403456,0,0,1120403456
		,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
</Data>
</ConfigData>
<Connections>
<Connection Name="A_MotionDiagnostics" RPI="1000" Type="DiagnosticInput" EventID="0" ProgrammaticallySendEventTrigger="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:MotionDevice_Diagnostics:S:0">
<DataValueMember Name="LostControllerToDeviceTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LateControllerToDeviceTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LostDeviceToControllerTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LateDeviceToControllerTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastControllerToDeviceTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageControllerToDeviceTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumControllerToDeviceTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastDeviceToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageDeviceToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumDeviceToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="TimingStatisticsEnabled" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="ControllerToDeviceConnectionSize" DataType="INT" Radix="Decimal" Value="36" />
<DataValueMember Name="DeviceToControllerConnectionSize" DataType="INT" Radix="Decimal" Value="44" />
<DataValueMember Name="NominalControllerToDeviceTime" DataType="INT" Radix="Decimal" Value="2000" />
<DataValueMember Name="NominalDeviceToControllerTime" DataType="INT" Radix="Decimal" Value="2000" />
<DataValueMember Name="CoarseUpdatePeriod" DataType="INT" Radix="Decimal" Value="4000" />
</Structure>
</Data>
</InputTag>
</Connection>
<Connection Name="B_MotionSync" RPI="4000" Type="MotionSync" EventID="0" ProgrammaticallySendEventTrigger="false" />
</Connections>
</Communications>
</Module>
""", 'DnR_Personal/Bender134053_201104.L5X', 1),
    '2198-P141': ("""\
<Module Name="TestMod1_2198P141" CatalogNumber="2198-P141" Vendor="1" ProductType="48" ProductCode="3" Major="14" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="376">
<Data Format="L5K">
[380,3,257,3,294257767,2,2565904,131588,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,460,-64768,0,0,0,0,0,1120403456
		,0,0,1120403456,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
</Data>
</ConfigData>
<Connections>
<Connection Name="A_MotionDiagnostics" RPI="1000" Type="DiagnosticInput" EventID="0" ProgrammaticallySendEventTrigger="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:MotionDevice_Diagnostics:S:0">
<DataValueMember Name="LostControllerToDeviceTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LateControllerToDeviceTransmissions" DataType="INT" Radix="Decimal" Value="4" />
<DataValueMember Name="LostDeviceToControllerTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LateDeviceToControllerTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastControllerToDeviceTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageControllerToDeviceTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumControllerToDeviceTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastDeviceToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageDeviceToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumDeviceToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="TimingStatisticsEnabled" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="ControllerToDeviceConnectionSize" DataType="INT" Radix="Decimal" Value="40" />
<DataValueMember Name="DeviceToControllerConnectionSize" DataType="INT" Radix="Decimal" Value="44" />
<DataValueMember Name="NominalControllerToDeviceTime" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="NominalDeviceToControllerTime" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="CoarseUpdatePeriod" DataType="INT" Radix="Decimal" Value="2000" />
</Structure>
</Data>
</InputTag>
</Connection>
<Connection Name="B_MotionSync" RPI="4000" Type="MotionSync" EventID="0" ProgrammaticallySendEventTrigger="false" />
</Connections>
</Communications>
</Module>
""", 'L5X_Samples/CMU_2025_10_14r00.L5X', 1),
    '2198-P208': ("""\
<Module Name="TestMod1_2198P208" CatalogNumber="2198-P208" Vendor="1" ProductType="48" ProductCode="4" Major="14" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="376">
<Data Format="L5K">
[380,3,257,4,294257767,2,2565904,131588,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,460,-65280,0,0,0,0,0,1120403456
		,0,0,1120403456,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
</Data>
</ConfigData>
<Connections>
<Connection Name="A_MotionDiagnostics" RPI="1000" Type="DiagnosticInput" EventID="0" ProgrammaticallySendEventTrigger="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:MotionDevice_Diagnostics:S:0">
<DataValueMember Name="LostControllerToDeviceTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LateControllerToDeviceTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LostDeviceToControllerTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LateDeviceToControllerTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastControllerToDeviceTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageControllerToDeviceTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumControllerToDeviceTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastDeviceToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageDeviceToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumDeviceToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="TimingStatisticsEnabled" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="ControllerToDeviceConnectionSize" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="DeviceToControllerConnectionSize" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="NominalControllerToDeviceTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="NominalDeviceToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="CoarseUpdatePeriod" DataType="INT" Radix="Decimal" Value="0" />
</Structure>
</Data>
</InputTag>
</Connection>
<Connection Name="B_MotionSync" RPI="2000" Type="MotionSync" EventID="0" ProgrammaticallySendEventTrigger="false" />
</Connections>
</Communications>
</Module>
""", 'SJ_Gormley_20251112_r02.L5X', 1),
    '2198-RP200': ("""\
<Module Name="TestMod1_2198RP200" CatalogNumber="2198-RP200" Vendor="1" ProductType="48" ProductCode="9" Major="11" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="452">
<Data Format="L5K">
[456,6,257,9,25165831,2,10000,131588,0,0,0,0,0,0,0,0,0,-1027080192,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,16843009,16843009,16777216
		,0,512,1045220557,0,0,0,0,1120403456,1120403456,0,1120403456,1124859904,0,0,1120403456,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
</Data>
</ConfigData>
<Connections>
<Connection Name="A_MotionDiagnostics" RPI="1000" Type="DiagnosticInput" EventID="0" ProgrammaticallySendEventTrigger="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:MotionDevice_Diagnostics:S:0">
<DataValueMember Name="LostControllerToDeviceTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LateControllerToDeviceTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LostDeviceToControllerTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LateDeviceToControllerTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastControllerToDeviceTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageControllerToDeviceTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumControllerToDeviceTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastDeviceToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageDeviceToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumDeviceToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="TimingStatisticsEnabled" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="ControllerToDeviceConnectionSize" DataType="INT" Radix="Decimal" Value="40" />
<DataValueMember Name="DeviceToControllerConnectionSize" DataType="INT" Radix="Decimal" Value="68" />
<DataValueMember Name="NominalControllerToDeviceTime" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="NominalDeviceToControllerTime" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="CoarseUpdatePeriod" DataType="INT" Radix="Decimal" Value="2000" />
</Structure>
</Data>
</InputTag>
</Connection>
<Connection Name="B_MotionSync" RPI="10000" Type="MotionSync" EventID="0" ProgrammaticallySendEventTrigger="false" />
</Connections>
</Communications>
</Module>
""", 'L5X_Samples/Emporium_2025_05_28r01.L5X', 1),
    '2198-S130-ERS3': ("""\
<Module Name="TestMod1_2198S130ERS3" CatalogNumber="2198-S130-ERS3" Vendor="1" ProductType="45" ProductCode="8" Major="11" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false" SafetyEnabled="false">
<EKey State="Disabled" />
<Ports>
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="448">
<Data Format="L5K">
[452,5,1793,8,165675015,0,10000,131588,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,131,0,2,0,256,0,0,0,0,0,0,0,0,0,1176256512
		,0,0,0,2,2,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,0,257,0,0,0,8192000,8192125,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0]
</Data>
</ConfigData>
<Connections>
<Connection Name="A_MotionDiagnostics" RPI="1000" Type="DiagnosticInput" EventID="0" ProgrammaticallySendEventTrigger="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:Motion_Diagnostics:S:1">
<DataValueMember Name="LostControllerToDriveTransmissions" DataType="INT" Radix="Decimal" Value="1" />
<DataValueMember Name="LateControllerToDriveTransmissions" DataType="INT" Radix="Decimal" Value="1" />
<DataValueMember Name="LostDriveToControllerTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LateDriveToControllerTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="TimingStatisticsEnabled" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="ControllerToDriveConnectionSize" DataType="INT" Radix="Decimal" Value="48" />
<DataValueMember Name="DriveToControllerConnectionSize" DataType="INT" Radix="Decimal" Value="100" />
<DataValueMember Name="NominalControllerToDriveTime" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="NominalDriveToControllerTime" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="CoarseUpdatePeriod" DataType="INT" Radix="Decimal" Value="2000" />
</Structure>
</Data>
</InputTag>
</Connection>
<Connection Name="B_MotionSync2" RPI="2000" Type="MotionSync" EventID="0" ProgrammaticallySendEventTrigger="false" />
</Connections>
</Communications>
</Module>
""", 'L5X_Samples/Emporium_2025_05_28r01.L5X', 1),
    '2702782': ("""\
<Module Name="TestMod1_2702782" CatalogNumber="2702782" Vendor="562" ProductType="12" ProductCode="8169" Major="1" Minor="2" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false" SafetyEnabled="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<Connections>
<Connection Name="_200424012C642C6E" RPI="20000" Type="StandardDataDriven" OutputSize="6" InputSize="10" EventID="0" ProgrammaticallySendEventTrigger="false" Priority="Scheduled" InputConnectionType="Unicast" InputProductionTrigger="Cyclic" ConnectionPath="20 04 24 01 2c 64 2c 6e" InputTagSuffix="I" OutputTagSuffix="O">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="_0232:2702782_BD7BDD2D:I:0">
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="1" />
<ArrayMember Name="Data" DataType="INT" Dimensions="3" Radix="Decimal">
<Element Index="[0]" Value="0" />
<Element Index="[1]" Value="0" />
<Element Index="[2]" Value="0" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[[0,0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="_0232:2702782_B82B6E11:O:0">
<ArrayMember Name="Data" DataType="INT" Dimensions="3" Radix="Decimal">
<Element Index="[0]" Value="0" />
<Element Index="[1]" Value="0" />
<Element Index="[2]" Value="0" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'BaillieLeitchField_Edger_20260812_r00.L5X', 1),
    '440C-CR30-22BBB/A': ("""\
<Module Name="TestMod1_440CCR3022BBBA" CatalogNumber="440C-CR30-22BBB/A" Vendor="1" ProductType="154" ProductCode="1" Major="10" Minor="11" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="20">
<Data Format="L5K">
[24,101,2053501260,1234361284,1289223558,1775907960,103]
</Data>
</ConfigData>
<Connections>
<Connection Name="Data" RPI="2000000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:440C_CR30:I:0">
<DataValueMember Name="RunMode" DataType="BOOL" Value="1" />
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="0" />
<DataValueMember Name="MajorFault" DataType="BOOL" Value="0" />
<DataValueMember Name="MinorFault" DataType="BOOL" Value="0" />
<DataValueMember Name="VerificationID" DataType="INT" Radix="Decimal" Value="6508" />
<DataValueMember Name="MajorFaultCode" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="MajorFaultType" DataType="SINT" Radix="Hex" Value="16#00" />
<DataValueMember Name="MinorFaultInstance" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="MinorFaultType" DataType="SINT" Radix="Hex" Value="16#00" />
<DataValueMember Name="MinorFaultCode" DataType="INT" Radix="Hex" Value="16#0000" />
<DataValueMember Name="Pt00Data" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt01Data" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt02Data" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt03Data" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt04Data" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt05Data" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt06Data" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt07Data" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt08Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt09Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt10Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt11Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt12Data" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt13Data" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt14Data" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt15Data" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt16Data" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt17Data" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt18Data" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt19Data" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt20Data" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt21Data" DataType="BOOL" Value="1" />
<DataValueMember Name="SMF01" DataType="BOOL" Value="1" />
<DataValueMember Name="SMF02" DataType="BOOL" Value="0" />
<DataValueMember Name="SMF03" DataType="BOOL" Value="1" />
<DataValueMember Name="SMF04" DataType="BOOL" Value="0" />
<DataValueMember Name="SMF05" DataType="BOOL" Value="0" />
<DataValueMember Name="SMF06" DataType="BOOL" Value="1" />
<DataValueMember Name="SMF07" DataType="BOOL" Value="0" />
<DataValueMember Name="SMF08" DataType="BOOL" Value="1" />
<DataValueMember Name="SMF09" DataType="BOOL" Value="0" />
<DataValueMember Name="SMF10" DataType="BOOL" Value="0" />
<DataValueMember Name="SMF11" DataType="BOOL" Value="0" />
<DataValueMember Name="SMF12" DataType="BOOL" Value="0" />
<DataValueMember Name="SMF13" DataType="BOOL" Value="0" />
<DataValueMember Name="SMF14" DataType="BOOL" Value="0" />
<DataValueMember Name="SMF15" DataType="BOOL" Value="0" />
<DataValueMember Name="SMF16" DataType="BOOL" Value="0" />
<DataValueMember Name="SMF17" DataType="BOOL" Value="0" />
<DataValueMember Name="SMF18" DataType="BOOL" Value="0" />
<DataValueMember Name="SMF19" DataType="BOOL" Value="0" />
<DataValueMember Name="SMF20" DataType="BOOL" Value="0" />
<DataValueMember Name="SMF21" DataType="BOOL" Value="0" />
<DataValueMember Name="SMF22" DataType="BOOL" Value="0" />
<DataValueMember Name="SMF23" DataType="BOOL" Value="0" />
<DataValueMember Name="SMF24" DataType="BOOL" Value="0" />
<DataValueMember Name="LLA01" DataType="BOOL" Value="1" />
<DataValueMember Name="LLA02" DataType="BOOL" Value="0" />
<DataValueMember Name="LLA03" DataType="BOOL" Value="0" />
<DataValueMember Name="LLA04" DataType="BOOL" Value="0" />
<DataValueMember Name="LLA05" DataType="BOOL" Value="0" />
<DataValueMember Name="LLA06" DataType="BOOL" Value="0" />
<DataValueMember Name="LLA07" DataType="BOOL" Value="1" />
<DataValueMember Name="LLA08" DataType="BOOL" Value="0" />
<DataValueMember Name="LLA09" DataType="BOOL" Value="0" />
<DataValueMember Name="LLA10" DataType="BOOL" Value="0" />
<DataValueMember Name="LLA11" DataType="BOOL" Value="0" />
<DataValueMember Name="LLA12" DataType="BOOL" Value="0" />
<DataValueMember Name="LLA13" DataType="BOOL" Value="0" />
<DataValueMember Name="LLA14" DataType="BOOL" Value="0" />
<DataValueMember Name="LLA15" DataType="BOOL" Value="0" />
<DataValueMember Name="LLA16" DataType="BOOL" Value="0" />
<DataValueMember Name="LLB01" DataType="BOOL" Value="1" />
<DataValueMember Name="LLB02" DataType="BOOL" Value="1" />
<DataValueMember Name="LLB03" DataType="BOOL" Value="0" />
<DataValueMember Name="LLB04" DataType="BOOL" Value="1" />
<DataValueMember Name="LLB05" DataType="BOOL" Value="1" />
<DataValueMember Name="LLB06" DataType="BOOL" Value="1" />
<DataValueMember Name="LLB07" DataType="BOOL" Value="0" />
<DataValueMember Name="LLB08" DataType="BOOL" Value="0" />
<DataValueMember Name="LLB09" DataType="BOOL" Value="0" />
<DataValueMember Name="LLB10" DataType="BOOL" Value="0" />
<DataValueMember Name="LLB11" DataType="BOOL" Value="0" />
<DataValueMember Name="LLB12" DataType="BOOL" Value="0" />
<DataValueMember Name="LLB13" DataType="BOOL" Value="0" />
<DataValueMember Name="LLB14" DataType="BOOL" Value="0" />
<DataValueMember Name="LLB15" DataType="BOOL" Value="0" />
<DataValueMember Name="LLB16" DataType="BOOL" Value="0" />
<DataValueMember Name="SOF01" DataType="BOOL" Value="1" />
<DataValueMember Name="SOF02" DataType="BOOL" Value="1" />
<DataValueMember Name="SOF03" DataType="BOOL" Value="0" />
<DataValueMember Name="SOF04" DataType="BOOL" Value="1" />
<DataValueMember Name="SOF05" DataType="BOOL" Value="0" />
<DataValueMember Name="SOF06" DataType="BOOL" Value="1" />
<DataValueMember Name="SOF07" DataType="BOOL" Value="1" />
<DataValueMember Name="SOF08" DataType="BOOL" Value="0" />
<DataValueMember Name="SOF09" DataType="BOOL" Value="0" />
<DataValueMember Name="SOF10" DataType="BOOL" Value="0" />
<DataValueMember Name="SOF11" DataType="BOOL" Value="0" />
<DataValueMember Name="SOF12" DataType="BOOL" Value="0" />
<DataValueMember Name="SOF13" DataType="BOOL" Value="0" />
<DataValueMember Name="SOF14" DataType="BOOL" Value="0" />
<DataValueMember Name="SOF15" DataType="BOOL" Value="0" />
<DataValueMember Name="SOF16" DataType="BOOL" Value="0" />
<DataValueMember Name="SOF01ResetRequired" DataType="BOOL" Value="0" />
<DataValueMember Name="SOF02ResetRequired" DataType="BOOL" Value="0" />
<DataValueMember Name="SOF03ResetRequired" DataType="BOOL" Value="0" />
<DataValueMember Name="SOF04ResetRequired" DataType="BOOL" Value="0" />
<DataValueMember Name="SOF05ResetRequired" DataType="BOOL" Value="0" />
<DataValueMember Name="SOF06ResetRequired" DataType="BOOL" Value="0" />
<DataValueMember Name="SOF07ResetRequired" DataType="BOOL" Value="0" />
<DataValueMember Name="SOF08ResetRequired" DataType="BOOL" Value="0" />
<DataValueMember Name="SOF09ResetRequired" DataType="BOOL" Value="0" />
<DataValueMember Name="SOF10ResetRequired" DataType="BOOL" Value="0" />
<DataValueMember Name="SOF11ResetRequired" DataType="BOOL" Value="0" />
<DataValueMember Name="SOF12ResetRequired" DataType="BOOL" Value="0" />
<DataValueMember Name="SOF13ResetRequired" DataType="BOOL" Value="0" />
<DataValueMember Name="SOF14ResetRequired" DataType="BOOL" Value="0" />
<DataValueMember Name="SOF15ResetRequired" DataType="BOOL" Value="0" />
<DataValueMember Name="SOF16ResetRequired" DataType="BOOL" Value="0" />
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:440C_CR30:O:0">
<DataValueMember Name="LogicDefinedData00" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicDefinedData01" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicDefinedData02" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicDefinedData03" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicDefinedData04" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicDefinedData05" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicDefinedData06" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicDefinedData07" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicDefinedData08" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicDefinedData09" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicDefinedData10" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicDefinedData11" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicDefinedData12" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicDefinedData13" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicDefinedData14" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicDefinedData15" DataType="BOOL" Value="0" />
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'L5X_Samples/K3M16_Edgers_20220808r00.L5X', 1),
    '442G-MABLB-UR-E0JP4679/A': ("""\
<Module Name="TestMod1_442GMABLBURE0JP4679A" CatalogNumber="442G-MABLB-UR-E0JP4679/A" Vendor="1" ProductType="157" ProductCode="10" Major="1" Minor="6" ParentModule="Local" ParentModPortId="4" Inhibited="false" MajorFault="false" SafetyNetwork="16#0000_4abf_0367_fe7c">
<EKey State="ExactMatch" />
<Ports>
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="12">
<Data Format="L5K">
[16,1088,0,0,0]
</Data>
</ConfigData>
<Connections>
<Connection Name="SafetyInput" RPI="10000" Type="SafetyInput" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="40.064" MaxObservedNetworkDelay="0">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:442G_MABB_E0JP4679:I:0">
<DataValueMember Name="RunMode" DataType="BOOL" Value="1" />
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="0" />
<DataValueMember Name="DiagnosticActive" DataType="BOOL" Value="0" />
<DataValueMember Name="EStop" DataType="BOOL" Value="1" />
<DataValueMember Name="EnablingSwitch" DataType="BOOL" Value="0" />
<DataValueMember Name="GuardClosed" DataType="BOOL" Value="1" />
<DataValueMember Name="GuardInterlocked" DataType="BOOL" Value="1" />
<DataValueMember Name="GuardLocked" DataType="BOOL" Value="1" />
<DataValueMember Name="Switch4" DataType="BOOL" Value="0" />
<DataValueMember Name="Switch6" DataType="BOOL" Value="0" />
<DataValueMember Name="Switch7" DataType="BOOL" Value="0" />
<DataValueMember Name="Switch9" DataType="BOOL" Value="0" />
<DataValueMember Name="LockSequenceFault" DataType="BOOL" Value="0" />
<DataValueMember Name="EStopFault" DataType="BOOL" Value="0" />
<DataValueMember Name="EnablingSwitchFault" DataType="BOOL" Value="0" />
<DataValueMember Name="UnlockCommandFault" DataType="BOOL" Value="0" />
<DataValueMember Name="CycleThresholdExceeded" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultCode" DataType="INT" Radix="Binary" Value="2#0000_0000_0000_0000" />
</Structure>
</Data>
</InputTag>
</Connection>
<Connection Name="SafetyOutput" RPI="20000" Type="SafetyOutput" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="60" MaxObservedNetworkDelay="0" Unicast="true">
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[0,1,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:442G_MABB_E0JP4679:O:0">
<DataValueMember Name="Unlock" DataType="BOOL" Value="0" />
<DataValueMember Name="Light4" DataType="BOOL" Value="1" />
<DataValueMember Name="Light6" DataType="BOOL" Value="0" />
<DataValueMember Name="Light7" DataType="BOOL" Value="0" />
<DataValueMember Name="Light9" DataType="BOOL" Value="0" />
<DataValueMember Name="EStopLight" DataType="BOOL" Value="0" />
<DataValueMember Name="GeneralFaultUnlatch" DataType="BOOL" Value="0" />
<DataValueMember Name="LockSequenceFaultUnlatch" DataType="BOOL" Value="0" />
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'DnR_Personal/FlareFunction_311D_240731.L5X', 1),
    '5069-IB16/A': ("""\
<Module Name="TestMod1_5069IB16A" CatalogNumber="5069-IB16/A" Vendor="1" ProductType="7" ProductCode="390" Major="2" Minor="1" ParentModule="Local" ParentModPortId="1" Inhibited="false" MajorFault="false" SafetyEnabled="false" AutoDiagsEnabled="true">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="1" Type="5069" Upstream="true" />
</Ports>
<Communications>
<ConfigTag ConfigSize="64" ExternalAccess="Read/Write">
<Data Format="L5K">
[68,160,[13,13,0],[13,13,0],[13,13,0],[13,13,0],[13,13,0],[13,13,0],[13,13,0],[13,13,0],[13,13,0],[13,13,0],[13,13,0],[13,13,0],[13,13,0],[13,13,0],[13,13,0],[13
		,13,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:5000_DI16:C:0">
<StructureMember Name="Pt00" DataType="AB:5000_DI_Channel:C:0">
<DataValueMember Name="InputOffOnFilter" DataType="SINT" Radix="Decimal" Value="13" />
<DataValueMember Name="InputOnOffFilter" DataType="SINT" Radix="Decimal" Value="13" />
</StructureMember>
<StructureMember Name="Pt01" DataType="AB:5000_DI_Channel:C:0">
<DataValueMember Name="InputOffOnFilter" DataType="SINT" Radix="Decimal" Value="13" />
<DataValueMember Name="InputOnOffFilter" DataType="SINT" Radix="Decimal" Value="13" />
</StructureMember>
<StructureMember Name="Pt02" DataType="AB:5000_DI_Channel:C:0">
<DataValueMember Name="InputOffOnFilter" DataType="SINT" Radix="Decimal" Value="13" />
<DataValueMember Name="InputOnOffFilter" DataType="SINT" Radix="Decimal" Value="13" />
</StructureMember>
<StructureMember Name="Pt03" DataType="AB:5000_DI_Channel:C:0">
<DataValueMember Name="InputOffOnFilter" DataType="SINT" Radix="Decimal" Value="13" />
<DataValueMember Name="InputOnOffFilter" DataType="SINT" Radix="Decimal" Value="13" />
</StructureMember>
<StructureMember Name="Pt04" DataType="AB:5000_DI_Channel:C:0">
<DataValueMember Name="InputOffOnFilter" DataType="SINT" Radix="Decimal" Value="13" />
<DataValueMember Name="InputOnOffFilter" DataType="SINT" Radix="Decimal" Value="13" />
</StructureMember>
<StructureMember Name="Pt05" DataType="AB:5000_DI_Channel:C:0">
<DataValueMember Name="InputOffOnFilter" DataType="SINT" Radix="Decimal" Value="13" />
<DataValueMember Name="InputOnOffFilter" DataType="SINT" Radix="Decimal" Value="13" />
</StructureMember>
<StructureMember Name="Pt06" DataType="AB:5000_DI_Channel:C:0">
<DataValueMember Name="InputOffOnFilter" DataType="SINT" Radix="Decimal" Value="13" />
<DataValueMember Name="InputOnOffFilter" DataType="SINT" Radix="Decimal" Value="13" />
</StructureMember>
<StructureMember Name="Pt07" DataType="AB:5000_DI_Channel:C:0">
<DataValueMember Name="InputOffOnFilter" DataType="SINT" Radix="Decimal" Value="13" />
<DataValueMember Name="InputOnOffFilter" DataType="SINT" Radix="Decimal" Value="13" />
</StructureMember>
<StructureMember Name="Pt08" DataType="AB:5000_DI_Channel:C:0">
<DataValueMember Name="InputOffOnFilter" DataType="SINT" Radix="Decimal" Value="13" />
<DataValueMember Name="InputOnOffFilter" DataType="SINT" Radix="Decimal" Value="13" />
</StructureMember>
<StructureMember Name="Pt09" DataType="AB:5000_DI_Channel:C:0">
<DataValueMember Name="InputOffOnFilter" DataType="SINT" Radix="Decimal" Value="13" />
<DataValueMember Name="InputOnOffFilter" DataType="SINT" Radix="Decimal" Value="13" />
</StructureMember>
<StructureMember Name="Pt10" DataType="AB:5000_DI_Channel:C:0">
<DataValueMember Name="InputOffOnFilter" DataType="SINT" Radix="Decimal" Value="13" />
<DataValueMember Name="InputOnOffFilter" DataType="SINT" Radix="Decimal" Value="13" />
</StructureMember>
<StructureMember Name="Pt11" DataType="AB:5000_DI_Channel:C:0">
<DataValueMember Name="InputOffOnFilter" DataType="SINT" Radix="Decimal" Value="13" />
<DataValueMember Name="InputOnOffFilter" DataType="SINT" Radix="Decimal" Value="13" />
</StructureMember>
<StructureMember Name="Pt12" DataType="AB:5000_DI_Channel:C:0">
<DataValueMember Name="InputOffOnFilter" DataType="SINT" Radix="Decimal" Value="13" />
<DataValueMember Name="InputOnOffFilter" DataType="SINT" Radix="Decimal" Value="13" />
</StructureMember>
<StructureMember Name="Pt13" DataType="AB:5000_DI_Channel:C:0">
<DataValueMember Name="InputOffOnFilter" DataType="SINT" Radix="Decimal" Value="13" />
<DataValueMember Name="InputOnOffFilter" DataType="SINT" Radix="Decimal" Value="13" />
</StructureMember>
<StructureMember Name="Pt14" DataType="AB:5000_DI_Channel:C:0">
<DataValueMember Name="InputOffOnFilter" DataType="SINT" Radix="Decimal" Value="13" />
<DataValueMember Name="InputOnOffFilter" DataType="SINT" Radix="Decimal" Value="13" />
</StructureMember>
<StructureMember Name="Pt15" DataType="AB:5000_DI_Channel:C:0">
<DataValueMember Name="InputOffOnFilter" DataType="SINT" Radix="Decimal" Value="13" />
<DataValueMember Name="InputOnOffFilter" DataType="SINT" Radix="Decimal" Value="13" />
</StructureMember>
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="InputData" RPI="5000" Type="StandardDataDriven" OutputSize="0" InputSize="12" EventID="0" ProgrammaticallySendEventTrigger="false" Priority="Scheduled" InputConnectionType="Multicast" InputProductionTrigger="Cyclic" ConnectionPath="20 04 24 a0 2c c7 2c 9c" InputTagSuffix="I">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:5000_DI16_Packed:I:0">
<DataValueMember Name="RunMode" DataType="BOOL" Value="1" />
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="0" />
<DataValueMember Name="DiagnosticActive" DataType="BOOL" Value="0" />
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0" />
<DataValueMember Name="DiagnosticSequenceCount" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Pt00Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt03Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt05Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt06Data" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt07Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt08Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt09Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt10Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt11Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt12Data" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt13Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt14Data" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt15Data" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt00Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt03Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt05Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt06Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt07Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt08Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt09Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt10Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt11Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt12Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt13Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt14Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt15Fault" DataType="BOOL" Value="0" />
</Structure>
</Data>
</InputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'DnR_Personal/Fisher_Synergy_Bead_20240725.L5X', 1),
    '5069-IB8S/A': ("""\
<Module CatalogNumber="5069-IB8S/A" Vendor="1" ProductType="35" ProductCode="23" Major="2" Minor="1" ParentModule="Local" ParentModPortId="1" Inhibited="false" MajorFault="false" SafetyNetwork="16#0000_49d6_03bc_cbd4" SafetyEnabled="true">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="1" Type="5069" Upstream="true" />
</Ports>
<Communications>
<SafetyScript Size="137">
<Data Format="L5K">
[-123,0,0,0,5,0,0,0,0,0,0,0,0,0,0,0,117,0,0,0,0,0,0,0,0,3,0,0,0,103,0,0,0,0,0,0,96,0,0,0,-89,0,0,0,105,-37,68,5,-9,108,-66,2,122,75,0,0,2,0
		,0,0,2,0,0,0,2,0,0,0,2,0,0,0,0,0,0,0,-24,3,113,0,0,0,0,0,-24,3,113,1,0,0,0,0,-24,3,1,0,0,0,0,0,-24,3,1,2,0,0,0,0,-24,3,1,2,0,0,0,0,-24,3,2,0,0,0,0
		,0,-24,3,114,0,0,0,0,0,-24,3,114,0,0]
</Data>
</SafetyScript>
<Connections>
<Connection Name="SafetyInput" RPI="10000" Type="SafetyInputDataDriven" InputSize="52" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="40.064" MaxObservedNetworkDelay="1.792" Priority="High" InputConnectionType="Multicast" InputProductionTrigger="Application" ConnectionPath="20 04 24 a7 20 04 24 c7 20 04 25 00 42 03" InputTagSuffix="I">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:5000_SDI8:I:0">
<DataValueMember Name="RunMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="1" />
<DataValueMember Name="DiagnosticActive" DataType="BOOL" Value="0" />
<DataValueMember Name="DiagnosticSequenceCount" DataType="SINT" Radix="Decimal" Value="0" />
<StructureMember Name="Pt00" DataType="CHANNEL_SDI:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Fault" DataType="BOOL" Value="1" />
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0" />
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0" />
<DataValueMember Name="Status" DataType="BOOL" Value="0" />
</StructureMember>
<StructureMember Name="Pt01" DataType="CHANNEL_SDI:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Fault" DataType="BOOL" Value="1" />
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0" />
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0" />
<DataValueMember Name="Status" DataType="BOOL" Value="0" />
</StructureMember>
<StructureMember Name="Pt02" DataType="CHANNEL_SDI:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Fault" DataType="BOOL" Value="1" />
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0" />
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0" />
<DataValueMember Name="Status" DataType="BOOL" Value="0" />
</StructureMember>
<StructureMember Name="Pt03" DataType="CHANNEL_SDI:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Fault" DataType="BOOL" Value="1" />
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0" />
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0" />
<DataValueMember Name="Status" DataType="BOOL" Value="0" />
</StructureMember>
<StructureMember Name="Pt04" DataType="CHANNEL_SDI:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Fault" DataType="BOOL" Value="1" />
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0" />
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0" />
<DataValueMember Name="Status" DataType="BOOL" Value="0" />
</StructureMember>
<StructureMember Name="Pt05" DataType="CHANNEL_SDI:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Fault" DataType="BOOL" Value="1" />
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0" />
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0" />
<DataValueMember Name="Status" DataType="BOOL" Value="0" />
</StructureMember>
<StructureMember Name="Pt06" DataType="CHANNEL_SDI:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Fault" DataType="BOOL" Value="1" />
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0" />
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0" />
<DataValueMember Name="Status" DataType="BOOL" Value="0" />
</StructureMember>
<StructureMember Name="Pt07" DataType="CHANNEL_SDI:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Fault" DataType="BOOL" Value="1" />
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0" />
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0" />
<DataValueMember Name="Status" DataType="BOOL" Value="0" />
</StructureMember>
<StructureMember Name="Test00" DataType="AB:5000_SafetyReadback_Channel:I:0">
<DataValueMember Name="Readback" DataType="BOOL" Value="0" />
<DataValueMember Name="Fault" DataType="BOOL" Value="1" />
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0" />
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0" />
<DataValueMember Name="FieldPowerOff" DataType="BOOL" Value="0" />
<DataValueMember Name="Status" DataType="BOOL" Value="0" />
</StructureMember>
<StructureMember Name="Test01" DataType="AB:5000_SafetyReadback_Channel:I:0">
<DataValueMember Name="Readback" DataType="BOOL" Value="0" />
<DataValueMember Name="Fault" DataType="BOOL" Value="1" />
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0" />
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0" />
<DataValueMember Name="FieldPowerOff" DataType="BOOL" Value="0" />
<DataValueMember Name="Status" DataType="BOOL" Value="0" />
</StructureMember>
<StructureMember Name="Test02" DataType="AB:5000_SafetyReadback_Channel:I:0">
<DataValueMember Name="Readback" DataType="BOOL" Value="0" />
<DataValueMember Name="Fault" DataType="BOOL" Value="1" />
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0" />
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0" />
<DataValueMember Name="FieldPowerOff" DataType="BOOL" Value="0" />
<DataValueMember Name="Status" DataType="BOOL" Value="0" />
</StructureMember>
<StructureMember Name="Test03" DataType="AB:5000_SafetyReadback_Channel:I:0">
<DataValueMember Name="Readback" DataType="BOOL" Value="0" />
<DataValueMember Name="Fault" DataType="BOOL" Value="1" />
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0" />
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0" />
<DataValueMember Name="FieldPowerOff" DataType="BOOL" Value="0" />
<DataValueMember Name="Status" DataType="BOOL" Value="0" />
</StructureMember>
</Structure>
</Data>
</InputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'DnR_Personal/BT1XX_FFC_20240325.L5X', 1),
    '5069-IY4/A': ("""\
<Module CatalogNumber="5069-IY4/A" Vendor="1" ProductType="115" ProductCode="314" Major="2" Minor="1" ParentModule="Local" ParentModPortId="1" Inhibited="false" MajorFault="false" SafetyEnabled="false" AutoDiagsEnabled="true">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="5" Type="5069" Upstream="true" />
</Ports>
<Communications>
<ConfigTag ConfigSize="208" ExternalAccess="Read/Write">
<Data Format="L5K">
[212,122,[1,0,0,0.00000000e+000],[1,0,0,0.00000000e+000],[5,0,2,1,0,0,4.00000000e+000,2.00000000e+001,0.00000000e+000
		,1.00000000e+002,0.00000000e+000,0.00000000e+000,1.00000000e+002,1.00000000e+002,0.00000000e+000
		,0.00000000e+000],[4,0,2,17,0,0,0.00000000e+000,2.00000000e+001,0.00000000e+000,1.00000000e+002
		,0.00000000e+000,0.00000000e+000,1.00000000e+002,1.00000000e+002,0.00000000e+000,0.00000000e+000
		],[4,0,2,17,0,0,0.00000000e+000,2.00000000e+001,0.00000000e+000,1.00000000e+002,0.00000000e+000
		,0.00000000e+000,1.00000000e+002,1.00000000e+002,0.00000000e+000,0.00000000e+000],[4,0,2,17,0
		,0,0.00000000e+000,2.00000000e+001,0.00000000e+000,1.00000000e+002,0.00000000e+000,0.00000000e+000
		,1.00000000e+002,1.00000000e+002,0.00000000e+000,0.00000000e+000]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:5000_AI4CJ:C:0">
<StructureMember Name="CJCh00" DataType="AB:5000_AI_CJ_Channel:C:0">
<DataValueMember Name="Disable" DataType="BOOL" Value="1" />
<DataValueMember Name="Remote" DataType="BOOL" Value="0" />
<DataValueMember Name="SensorOffset" DataType="REAL" Radix="Float" Value="0.0" />
</StructureMember>
<StructureMember Name="CJCh01" DataType="AB:5000_AI_CJ_Channel:C:0">
<DataValueMember Name="Disable" DataType="BOOL" Value="1" />
<DataValueMember Name="Remote" DataType="BOOL" Value="0" />
<DataValueMember Name="SensorOffset" DataType="REAL" Radix="Float" Value="0.0" />
</StructureMember>
<StructureMember Name="Ch00" DataType="AB:5000_AI_Channel:C:0">
<DataValueMember Name="Range" DataType="SINT" Radix="Decimal" Value="5" />
<DataValueMember Name="SensorType" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="NotchFilter" DataType="SINT" Radix="Decimal" Value="2" />
<DataValueMember Name="AlarmDisable" DataType="BOOL" Value="1" />
<DataValueMember Name="ProcessAlarmLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="RateAlarmLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="OpenWireEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Disable" DataType="BOOL" Value="0" />
<DataValueMember Name="TenOhmOffset" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="DigitalFilter" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LowSignal" DataType="REAL" Radix="Float" Value="4.0" />
<DataValueMember Name="HighSignal" DataType="REAL" Radix="Float" Value="20.0" />
<DataValueMember Name="LowEngineering" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="HighEngineering" DataType="REAL" Radix="Float" Value="100.0" />
<DataValueMember Name="LLAlarmLimit" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="LAlarmLimit" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="HAlarmLimit" DataType="REAL" Radix="Float" Value="100.0" />
<DataValueMember Name="HHAlarmLimit" DataType="REAL" Radix="Float" Value="100.0" />
<DataValueMember Name="RateAlarmLimit" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="AlarmDeadband" DataType="REAL" Radix="Float" Value="0.0" />
</StructureMember>
<StructureMember Name="Ch01" DataType="AB:5000_AI_Channel:C:0">
<DataValueMember Name="Range" DataType="SINT" Radix="Decimal" Value="4" />
<DataValueMember Name="SensorType" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="NotchFilter" DataType="SINT" Radix="Decimal" Value="2" />
<DataValueMember Name="AlarmDisable" DataType="BOOL" Value="1" />
<DataValueMember Name="ProcessAlarmLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="RateAlarmLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="OpenWireEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Disable" DataType="BOOL" Value="1" />
<DataValueMember Name="TenOhmOffset" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="DigitalFilter" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LowSignal" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="HighSignal" DataType="REAL" Radix="Float" Value="20.0" />
<DataValueMember Name="LowEngineering" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="HighEngineering" DataType="REAL" Radix="Float" Value="100.0" />
<DataValueMember Name="LLAlarmLimit" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="LAlarmLimit" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="HAlarmLimit" DataType="REAL" Radix="Float" Value="100.0" />
<DataValueMember Name="HHAlarmLimit" DataType="REAL" Radix="Float" Value="100.0" />
<DataValueMember Name="RateAlarmLimit" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="AlarmDeadband" DataType="REAL" Radix="Float" Value="0.0" />
</StructureMember>
<StructureMember Name="Ch02" DataType="AB:5000_AI_Channel:C:0">
<DataValueMember Name="Range" DataType="SINT" Radix="Decimal" Value="4" />
<DataValueMember Name="SensorType" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="NotchFilter" DataType="SINT" Radix="Decimal" Value="2" />
<DataValueMember Name="AlarmDisable" DataType="BOOL" Value="1" />
<DataValueMember Name="ProcessAlarmLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="RateAlarmLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="OpenWireEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Disable" DataType="BOOL" Value="1" />
<DataValueMember Name="TenOhmOffset" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="DigitalFilter" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LowSignal" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="HighSignal" DataType="REAL" Radix="Float" Value="20.0" />
<DataValueMember Name="LowEngineering" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="HighEngineering" DataType="REAL" Radix="Float" Value="100.0" />
<DataValueMember Name="LLAlarmLimit" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="LAlarmLimit" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="HAlarmLimit" DataType="REAL" Radix="Float" Value="100.0" />
<DataValueMember Name="HHAlarmLimit" DataType="REAL" Radix="Float" Value="100.0" />
<DataValueMember Name="RateAlarmLimit" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="AlarmDeadband" DataType="REAL" Radix="Float" Value="0.0" />
</StructureMember>
<StructureMember Name="Ch03" DataType="AB:5000_AI_Channel:C:0">
<DataValueMember Name="Range" DataType="SINT" Radix="Decimal" Value="4" />
<DataValueMember Name="SensorType" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="NotchFilter" DataType="SINT" Radix="Decimal" Value="2" />
<DataValueMember Name="AlarmDisable" DataType="BOOL" Value="1" />
<DataValueMember Name="ProcessAlarmLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="RateAlarmLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="OpenWireEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Disable" DataType="BOOL" Value="1" />
<DataValueMember Name="TenOhmOffset" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="DigitalFilter" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LowSignal" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="HighSignal" DataType="REAL" Radix="Float" Value="20.0" />
<DataValueMember Name="LowEngineering" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="HighEngineering" DataType="REAL" Radix="Float" Value="100.0" />
<DataValueMember Name="LLAlarmLimit" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="LAlarmLimit" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="HAlarmLimit" DataType="REAL" Radix="Float" Value="100.0" />
<DataValueMember Name="HHAlarmLimit" DataType="REAL" Radix="Float" Value="100.0" />
<DataValueMember Name="RateAlarmLimit" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="AlarmDeadband" DataType="REAL" Radix="Float" Value="0.0" />
</StructureMember>
</Structure>
</Data>
</ConfigTag>
<ConfigScript Size="340">
<Data Format="L5K">
[80,1,0,0,4,0,0,0,0,0,0,0,0,0,0,0,62,1,0,0,7,1,0,0,0,3,0,0,0,-48,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,8,-97,0,0,0,0,0,0,0,0,0,0,0,96,1,0,0,-96,0,0,0,-96,0,0,0,31,0,0,0,0,2,0,0,0,2,0,0,96,1,0,0,32,2,0,0,32,2,0,0,31,0,0,0,-128,3,0,0,-128,3,0,0
		,96,1,0,0,-96,3,0,0,-96,3,0,0,31,0,0,0,0,5,0,0,0,5,0,0,96,1,0,0,32,5,0,0,32,5,0,0,0,0]
</Data>
</ConfigScript>
<Connections>
<Connection Name="InputData" RPI="10000" Type="StandardDataDriven" OutputSize="32" InputSize="68" EventID="0" ProgrammaticallySendEventTrigger="false" Priority="Scheduled" InputConnectionType="Multicast" InputProductionTrigger="Cyclic" ConnectionPath="20 04 24 7a 2c 66 2c 98" InputTagSuffix="I" OutputTagSuffix="O">
<InputTag ExternalAccess="Read/Write">
<EngineeringUnits>
<EngineeringUnit Operand=".CH00.DATA">
%
</EngineeringUnit>
<EngineeringUnit Operand=".CH01.DATA">
%
</EngineeringUnit>
<EngineeringUnit Operand=".CH02.DATA">
%
</EngineeringUnit>
<EngineeringUnit Operand=".CH03.DATA">
%
</EngineeringUnit>
</EngineeringUnits>
<Data Format="Decorated">
<Structure DataType="AB:5000_AI4CJ:I:0">
<DataValueMember Name="RunMode" DataType="BOOL" Value="1" />
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="0" />
<DataValueMember Name="DiagnosticActive" DataType="BOOL" Value="0" />
<DataValueMember Name="DiagnosticSequenceCount" DataType="SINT" Radix="Decimal" Value="0" />
<StructureMember Name="CJCh00" DataType="CHANNEL_AI_CJ_DIAG:I:0">
<DataValueMember Name="Fault" DataType="BOOL" Value="1" />
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0" />
<DataValueMember Name="OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="FieldPowerOff" DataType="BOOL" Value="0" />
<DataValueMember Name="Underrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Overrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Temperature" DataType="REAL" Radix="Float" Value="1.#QNAN" />
</StructureMember>
<StructureMember Name="CJCh01" DataType="CHANNEL_AI_CJ_DIAG:I:0">
<DataValueMember Name="Fault" DataType="BOOL" Value="1" />
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0" />
<DataValueMember Name="OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="FieldPowerOff" DataType="BOOL" Value="0" />
<DataValueMember Name="Underrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Overrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Temperature" DataType="REAL" Radix="Float" Value="1.#QNAN" />
</StructureMember>
<StructureMember Name="Ch00" DataType="CHANNEL_AI_DIAG:I:0">
<DataValueMember Name="Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0" />
<DataValueMember Name="OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="OverTemperature" DataType="BOOL" Value="0" />
<DataValueMember Name="FieldPowerOff" DataType="BOOL" Value="0" />
<DataValueMember Name="NotANumber" DataType="BOOL" Value="0" />
<DataValueMember Name="Underrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Overrange" DataType="BOOL" Value="0" />
<DataValueMember Name="LLAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="LAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="HAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="HHAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="RateAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="CalFault" DataType="BOOL" Value="0" />
<DataValueMember Name="Calibrating" DataType="BOOL" Value="0" />
<DataValueMember Name="Data" DataType="REAL" Radix="Float" Value="49.91237" />
<DataValueMember Name="RollingTimestamp" DataType="INT" Radix="Decimal" Value="1427" />
</StructureMember>
<StructureMember Name="Ch01" DataType="CHANNEL_AI_DIAG:I:0">
<DataValueMember Name="Fault" DataType="BOOL" Value="1" />
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0" />
<DataValueMember Name="OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="OverTemperature" DataType="BOOL" Value="0" />
<DataValueMember Name="FieldPowerOff" DataType="BOOL" Value="0" />
<DataValueMember Name="NotANumber" DataType="BOOL" Value="0" />
<DataValueMember Name="Underrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Overrange" DataType="BOOL" Value="0" />
<DataValueMember Name="LLAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="LAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="HAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="HHAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="RateAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="CalFault" DataType="BOOL" Value="0" />
<DataValueMember Name="Calibrating" DataType="BOOL" Value="0" />
<DataValueMember Name="Data" DataType="REAL" Radix="Float" Value="1.#QNAN" />
<DataValueMember Name="RollingTimestamp" DataType="INT" Radix="Decimal" Value="0" />
</StructureMember>
<StructureMember Name="Ch02" DataType="CHANNEL_AI_DIAG:I:0">
<DataValueMember Name="Fault" DataType="BOOL" Value="1" />
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0" />
<DataValueMember Name="OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="OverTemperature" DataType="BOOL" Value="0" />
<DataValueMember Name="FieldPowerOff" DataType="BOOL" Value="0" />
<DataValueMember Name="NotANumber" DataType="BOOL" Value="0" />
<DataValueMember Name="Underrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Overrange" DataType="BOOL" Value="0" />
<DataValueMember Name="LLAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="LAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="HAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="HHAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="RateAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="CalFault" DataType="BOOL" Value="0" />
<DataValueMember Name="Calibrating" DataType="BOOL" Value="0" />
<DataValueMember Name="Data" DataType="REAL" Radix="Float" Value="1.#QNAN" />
<DataValueMember Name="RollingTimestamp" DataType="INT" Radix="Decimal" Value="0" />
</StructureMember>
<StructureMember Name="Ch03" DataType="CHANNEL_AI_DIAG:I:0">
<DataValueMember Name="Fault" DataType="BOOL" Value="1" />
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0" />
<DataValueMember Name="OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="OverTemperature" DataType="BOOL" Value="0" />
<DataValueMember Name="FieldPowerOff" DataType="BOOL" Value="0" />
<DataValueMember Name="NotANumber" DataType="BOOL" Value="0" />
<DataValueMember Name="Underrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Overrange" DataType="BOOL" Value="0" />
<DataValueMember Name="LLAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="LAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="HAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="HHAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="RateAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="CalFault" DataType="BOOL" Value="0" />
<DataValueMember Name="Calibrating" DataType="BOOL" Value="0" />
<DataValueMember Name="Data" DataType="REAL" Radix="Float" Value="1.#QNAN" />
<DataValueMember Name="RollingTimestamp" DataType="INT" Radix="Decimal" Value="0" />
</StructureMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[[0,0,0,0.00000000e+000],[0,0,0,0.00000000e+000],[0,0,0,0.00000000e+000],[0,0,0,0.00000000e+000]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:5000_AI4:O:0">
<StructureMember Name="Ch00" DataType="CHANNEL_AI:O:0">
<DataValueMember Name="LLAlarmEn" DataType="BOOL" Value="0" />
<DataValueMember Name="LAlarmEn" DataType="BOOL" Value="0" />
<DataValueMember Name="HAlarmEn" DataType="BOOL" Value="0" />
<DataValueMember Name="HHAlarmEn" DataType="BOOL" Value="0" />
<DataValueMember Name="RateAlarmEn" DataType="BOOL" Value="0" />
<DataValueMember Name="LLAlarmUnlatch" DataType="BOOL" Value="0" />
<DataValueMember Name="LAlarmUnlatch" DataType="BOOL" Value="0" />
<DataValueMember Name="HAlarmUnlatch" DataType="BOOL" Value="0" />
<DataValueMember Name="HHAlarmUnlatch" DataType="BOOL" Value="0" />
<DataValueMember Name="RateAlarmUnlatch" DataType="BOOL" Value="0" />
<DataValueMember Name="SensorOffset" DataType="REAL" Radix="Float" Value="0.0" />
</StructureMember>
<StructureMember Name="Ch01" DataType="CHANNEL_AI:O:0">
<DataValueMember Name="LLAlarmEn" DataType="BOOL" Value="0" />
<DataValueMember Name="LAlarmEn" DataType="BOOL" Value="0" />
<DataValueMember Name="HAlarmEn" DataType="BOOL" Value="0" />
<DataValueMember Name="HHAlarmEn" DataType="BOOL" Value="0" />
<DataValueMember Name="RateAlarmEn" DataType="BOOL" Value="0" />
<DataValueMember Name="LLAlarmUnlatch" DataType="BOOL" Value="0" />
<DataValueMember Name="LAlarmUnlatch" DataType="BOOL" Value="0" />
<DataValueMember Name="HAlarmUnlatch" DataType="BOOL" Value="0" />
<DataValueMember Name="HHAlarmUnlatch" DataType="BOOL" Value="0" />
<DataValueMember Name="RateAlarmUnlatch" DataType="BOOL" Value="0" />
<DataValueMember Name="SensorOffset" DataType="REAL" Radix="Float" Value="0.0" />
</StructureMember>
<StructureMember Name="Ch02" DataType="CHANNEL_AI:O:0">
<DataValueMember Name="LLAlarmEn" DataType="BOOL" Value="0" />
<DataValueMember Name="LAlarmEn" DataType="BOOL" Value="0" />
<DataValueMember Name="HAlarmEn" DataType="BOOL" Value="0" />
<DataValueMember Name="HHAlarmEn" DataType="BOOL" Value="0" />
<DataValueMember Name="RateAlarmEn" DataType="BOOL" Value="0" />
<DataValueMember Name="LLAlarmUnlatch" DataType="BOOL" Value="0" />
<DataValueMember Name="LAlarmUnlatch" DataType="BOOL" Value="0" />
<DataValueMember Name="HAlarmUnlatch" DataType="BOOL" Value="0" />
<DataValueMember Name="HHAlarmUnlatch" DataType="BOOL" Value="0" />
<DataValueMember Name="RateAlarmUnlatch" DataType="BOOL" Value="0" />
<DataValueMember Name="SensorOffset" DataType="REAL" Radix="Float" Value="0.0" />
</StructureMember>
<StructureMember Name="Ch03" DataType="CHANNEL_AI:O:0">
<DataValueMember Name="LLAlarmEn" DataType="BOOL" Value="0" />
<DataValueMember Name="LAlarmEn" DataType="BOOL" Value="0" />
<DataValueMember Name="HAlarmEn" DataType="BOOL" Value="0" />
<DataValueMember Name="HHAlarmEn" DataType="BOOL" Value="0" />
<DataValueMember Name="RateAlarmEn" DataType="BOOL" Value="0" />
<DataValueMember Name="LLAlarmUnlatch" DataType="BOOL" Value="0" />
<DataValueMember Name="LAlarmUnlatch" DataType="BOOL" Value="0" />
<DataValueMember Name="HAlarmUnlatch" DataType="BOOL" Value="0" />
<DataValueMember Name="HHAlarmUnlatch" DataType="BOOL" Value="0" />
<DataValueMember Name="RateAlarmUnlatch" DataType="BOOL" Value="0" />
<DataValueMember Name="SensorOffset" DataType="REAL" Radix="Float" Value="0.0" />
</StructureMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'DnR_Personal/BT1XX_FFC_20240325.L5X', 1),
    '5069-OB16/A': ("""\
<Module Name="TestMod1_5069OB16A" CatalogNumber="5069-OB16/A" Vendor="1" ProductType="7" ProductCode="392" Major="2" Minor="1" ParentModule="Local" ParentModPortId="1" Inhibited="false" MajorFault="false" SafetyEnabled="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="5" Type="5069" Upstream="true" />
</Ports>
<Communications>
<ConfigTag ConfigSize="64" ExternalAccess="Read/Write">
<Data Format="L5K">
[68,163,[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:5000_DO16_Diag:C:0">
<StructureMember Name="Pt00" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0" />
</StructureMember>
<StructureMember Name="Pt01" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0" />
</StructureMember>
<StructureMember Name="Pt02" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0" />
</StructureMember>
<StructureMember Name="Pt03" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0" />
</StructureMember>
<StructureMember Name="Pt04" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0" />
</StructureMember>
<StructureMember Name="Pt05" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0" />
</StructureMember>
<StructureMember Name="Pt06" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0" />
</StructureMember>
<StructureMember Name="Pt07" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0" />
</StructureMember>
<StructureMember Name="Pt08" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0" />
</StructureMember>
<StructureMember Name="Pt09" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0" />
</StructureMember>
<StructureMember Name="Pt10" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0" />
</StructureMember>
<StructureMember Name="Pt11" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0" />
</StructureMember>
<StructureMember Name="Pt12" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0" />
</StructureMember>
<StructureMember Name="Pt13" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0" />
</StructureMember>
<StructureMember Name="Pt14" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0" />
</StructureMember>
<StructureMember Name="Pt15" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0" />
</StructureMember>
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="OutputData" RPI="5000" Type="StandardDataDriven" OutputSize="4" InputSize="12" EventID="0" ProgrammaticallySendEventTrigger="false" Priority="Scheduled" InputConnectionType="Multicast" InputProductionTrigger="Cyclic" ConnectionPath="20 04 24 a3 2c 65 2c 9c" InputTagSuffix="I" OutputTagSuffix="O">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:5000_DI16_Packed:I:0">
<DataValueMember Name="RunMode" DataType="BOOL" Value="1" />
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="0" />
<DataValueMember Name="DiagnosticActive" DataType="BOOL" Value="0" />
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0" />
<DataValueMember Name="DiagnosticSequenceCount" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Pt00Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt03Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04Data" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt05Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt06Data" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt07Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt08Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt09Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt10Data" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt11Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt12Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt13Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt14Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt15Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt00Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt03Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt05Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt06Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt07Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt08Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt09Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt10Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt11Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt12Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt13Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt14Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt15Fault" DataType="BOOL" Value="0" />
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[1104,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:5000_DO16_Packed:O:0">
<DataValueMember Name="Pt00Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt03Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04Data" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt05Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt06Data" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt07Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt08Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt09Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt10Data" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt11Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt12Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt13Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt14Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt15Data" DataType="BOOL" Value="0" />
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'DnR_Personal/PWO_134190.L5X', 1),
    '5069-OB16/B': ("""\
<Module Name="TestMod1_5069OB16B" CatalogNumber="5069-OB16/B" Vendor="1" ProductType="7" ProductCode="392" Major="3" Minor="1" ParentModule="Local" ParentModPortId="1" Inhibited="false" MajorFault="false" SafetyEnabled="false" AutoDiagsEnabled="true">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="3" Type="5069" Upstream="true" />
</Ports>
<Communications>
<ConfigTag ConfigSize="64" ExternalAccess="Read/Write">
<Data Format="L5K">
[68,163,[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:5000_DO16_Diag:C:0">
<StructureMember Name="Pt00" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0" />
</StructureMember>
<StructureMember Name="Pt01" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0" />
</StructureMember>
<StructureMember Name="Pt02" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0" />
</StructureMember>
<StructureMember Name="Pt03" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0" />
</StructureMember>
<StructureMember Name="Pt04" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0" />
</StructureMember>
<StructureMember Name="Pt05" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0" />
</StructureMember>
<StructureMember Name="Pt06" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0" />
</StructureMember>
<StructureMember Name="Pt07" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0" />
</StructureMember>
<StructureMember Name="Pt08" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0" />
</StructureMember>
<StructureMember Name="Pt09" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0" />
</StructureMember>
<StructureMember Name="Pt10" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0" />
</StructureMember>
<StructureMember Name="Pt11" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0" />
</StructureMember>
<StructureMember Name="Pt12" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0" />
</StructureMember>
<StructureMember Name="Pt13" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0" />
</StructureMember>
<StructureMember Name="Pt14" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0" />
</StructureMember>
<StructureMember Name="Pt15" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0" />
</StructureMember>
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="OutputData" RPI="5000" Type="StandardDataDriven" OutputSize="4" InputSize="12" EventID="0" ProgrammaticallySendEventTrigger="false" Priority="Scheduled" InputConnectionType="Multicast" InputProductionTrigger="Cyclic" ConnectionPath="20 04 24 a3 2c 65 2c 9c" InputTagSuffix="I" OutputTagSuffix="O">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:5000_DI16_Packed:I:0">
<DataValueMember Name="RunMode" DataType="BOOL" Value="1" />
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="0" />
<DataValueMember Name="DiagnosticActive" DataType="BOOL" Value="0" />
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0" />
<DataValueMember Name="DiagnosticSequenceCount" DataType="SINT" Radix="Decimal" Value="16" />
<DataValueMember Name="Pt00Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt03Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt05Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt06Data" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt07Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt08Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt09Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt10Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt11Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt12Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt13Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt14Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt15Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt00Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt03Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt05Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt06Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt07Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt08Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt09Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt10Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt11Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt12Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt13Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt14Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt15Fault" DataType="BOOL" Value="0" />
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[64,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:5000_DO16_Packed:O:0">
<DataValueMember Name="Pt00Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt03Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt05Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt06Data" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt07Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt08Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt09Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt10Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt11Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt12Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt13Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt14Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt15Data" DataType="BOOL" Value="0" />
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'DnR_Personal/Fisher_Synergy_Bead_20240725.L5X', 1),
    '5069-OBV8S/A': ("""\
<Module CatalogNumber="5069-OBV8S/A" Vendor="1" ProductType="35" ProductCode="24" Major="3" Minor="1" ParentModule="Local" ParentModPortId="1" Inhibited="false" MajorFault="false" SafetyNetwork="16#0000_49d6_03bc_cbd4" SafetyEnabled="true">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="4" Type="5069" Upstream="true" />
</Ports>
<Communications>
<SafetyScript Size="105">
<Data Format="L5K">
[101,0,0,0,5,0,0,0,0,0,0,0,0,0,0,0,85,0,0,0,0,0,0,0,0,3,0,0,0,71,0,0,0,0,0,0,64,0,0,0,-88,0,0,0,68,-126,123,-28,-16,14,-65,2,122,75,0,0,-24
		,3,2,0,-24,3,2,0,-24,3,2,0,-24,3,2,0,-24,3,1,2,-24,3,1,2,-24,3,1,2,-24,3,1,2,1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,0]
</Data>
</SafetyScript>
<Connections>
<Connection Name="SafetyInput" RPI="10000" Type="SafetyInputDataDriven" InputSize="36" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="40.064" MaxObservedNetworkDelay="1.792" Priority="High" InputConnectionType="Multicast" InputProductionTrigger="Application" ConnectionPath="20 04 24 a8 20 04 24 c7 20 04 25 00 25 04" InputTagSuffix="I">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:5000_SDO8:I:1">
<DataValueMember Name="RunMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="1" />
<DataValueMember Name="DiagnosticActive" DataType="BOOL" Value="0" />
<DataValueMember Name="DiagnosticSequenceCount" DataType="SINT" Radix="Decimal" Value="0" />
<StructureMember Name="Pt00" DataType="AB:5000_SafetyReadback_Channel:I:1">
<DataValueMember Name="Readback" DataType="BOOL" Value="0" />
<DataValueMember Name="Fault" DataType="BOOL" Value="1" />
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoad" DataType="BOOL" Value="0" />
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0" />
<DataValueMember Name="FieldPowerOff" DataType="BOOL" Value="0" />
<DataValueMember Name="Status" DataType="BOOL" Value="0" />
</StructureMember>
<StructureMember Name="Pt01" DataType="AB:5000_SafetyReadback_Channel:I:1">
<DataValueMember Name="Readback" DataType="BOOL" Value="0" />
<DataValueMember Name="Fault" DataType="BOOL" Value="1" />
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoad" DataType="BOOL" Value="0" />
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0" />
<DataValueMember Name="FieldPowerOff" DataType="BOOL" Value="0" />
<DataValueMember Name="Status" DataType="BOOL" Value="0" />
</StructureMember>
<StructureMember Name="Pt02" DataType="AB:5000_SafetyReadback_Channel:I:1">
<DataValueMember Name="Readback" DataType="BOOL" Value="0" />
<DataValueMember Name="Fault" DataType="BOOL" Value="1" />
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoad" DataType="BOOL" Value="0" />
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0" />
<DataValueMember Name="FieldPowerOff" DataType="BOOL" Value="0" />
<DataValueMember Name="Status" DataType="BOOL" Value="0" />
</StructureMember>
<StructureMember Name="Pt03" DataType="AB:5000_SafetyReadback_Channel:I:1">
<DataValueMember Name="Readback" DataType="BOOL" Value="0" />
<DataValueMember Name="Fault" DataType="BOOL" Value="1" />
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoad" DataType="BOOL" Value="0" />
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0" />
<DataValueMember Name="FieldPowerOff" DataType="BOOL" Value="0" />
<DataValueMember Name="Status" DataType="BOOL" Value="0" />
</StructureMember>
<StructureMember Name="Pt04" DataType="AB:5000_SafetyReadback_Channel:I:1">
<DataValueMember Name="Readback" DataType="BOOL" Value="0" />
<DataValueMember Name="Fault" DataType="BOOL" Value="1" />
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoad" DataType="BOOL" Value="0" />
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0" />
<DataValueMember Name="FieldPowerOff" DataType="BOOL" Value="0" />
<DataValueMember Name="Status" DataType="BOOL" Value="0" />
</StructureMember>
<StructureMember Name="Pt05" DataType="AB:5000_SafetyReadback_Channel:I:1">
<DataValueMember Name="Readback" DataType="BOOL" Value="0" />
<DataValueMember Name="Fault" DataType="BOOL" Value="1" />
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoad" DataType="BOOL" Value="0" />
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0" />
<DataValueMember Name="FieldPowerOff" DataType="BOOL" Value="0" />
<DataValueMember Name="Status" DataType="BOOL" Value="0" />
</StructureMember>
<StructureMember Name="Pt06" DataType="AB:5000_SafetyReadback_Channel:I:1">
<DataValueMember Name="Readback" DataType="BOOL" Value="0" />
<DataValueMember Name="Fault" DataType="BOOL" Value="1" />
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoad" DataType="BOOL" Value="0" />
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0" />
<DataValueMember Name="FieldPowerOff" DataType="BOOL" Value="0" />
<DataValueMember Name="Status" DataType="BOOL" Value="0" />
</StructureMember>
<StructureMember Name="Pt07" DataType="AB:5000_SafetyReadback_Channel:I:1">
<DataValueMember Name="Readback" DataType="BOOL" Value="0" />
<DataValueMember Name="Fault" DataType="BOOL" Value="1" />
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoad" DataType="BOOL" Value="0" />
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0" />
<DataValueMember Name="FieldPowerOff" DataType="BOOL" Value="0" />
<DataValueMember Name="Status" DataType="BOOL" Value="0" />
</StructureMember>
</Structure>
</Data>
</InputTag>
</Connection>
<Connection Name="SafetyOutput" RPI="20000" Type="SafetyOutputDataDriven" OutputSize="32" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="60" MaxObservedNetworkDelay="0" Priority="High" InputConnectionType="Unicast" InputProductionTrigger="Application" ConnectionPath="20 04 24 a8 20 04 24 74 20 04 24 c7" OutputTagSuffix="O">
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[[1,0,0,0],[1,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:5000_DO8:O:0">
<StructureMember Name="Pt00" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="1" />
</StructureMember>
<StructureMember Name="Pt01" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="1" />
</StructureMember>
<StructureMember Name="Pt02" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0" />
</StructureMember>
<StructureMember Name="Pt03" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0" />
</StructureMember>
<StructureMember Name="Pt04" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0" />
</StructureMember>
<StructureMember Name="Pt05" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0" />
</StructureMember>
<StructureMember Name="Pt06" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0" />
</StructureMember>
<StructureMember Name="Pt07" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0" />
</StructureMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'DnR_Personal/BT1XX_FFC_20240325.L5X', 1),
    '842E-CM-M': ("""\
<Module Name="TestMod1_842ECMM" CatalogNumber="842E-CM-M" Vendor="1" ProductType="37" ProductCode="53" Major="1" Minor="2" ParentModule="Local" ParentModPortId="2" Inhibited="true" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="220">
<Data Format="L5K">
[224,1,1,53,39,0,10000,131588,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,8192000,8192125,67305985
		,5,0,0,0,0,0,0]
</Data>
</ConfigData>
<Connections>
<Connection Name="MotionDiagnostics" RPI="1000" Type="DiagnosticInput" EventID="0" ProgrammaticallySendEventTrigger="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:MotionDevice_Diagnostics:S:0">
<DataValueMember Name="LostControllerToDeviceTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LateControllerToDeviceTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LostDeviceToControllerTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LateDeviceToControllerTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastControllerToDeviceTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageControllerToDeviceTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumControllerToDeviceTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastDeviceToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageDeviceToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumDeviceToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="TimingStatisticsEnabled" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="ControllerToDeviceConnectionSize" DataType="INT" Radix="Decimal" Value="36" />
<DataValueMember Name="DeviceToControllerConnectionSize" DataType="INT" Radix="Decimal" Value="52" />
<DataValueMember Name="NominalControllerToDeviceTime" DataType="INT" Radix="Decimal" Value="2500" />
<DataValueMember Name="NominalDeviceToControllerTime" DataType="INT" Radix="Decimal" Value="2500" />
<DataValueMember Name="CoarseUpdatePeriod" DataType="INT" Radix="Decimal" Value="5000" />
</Structure>
</Data>
</InputTag>
</Connection>
<Connection Name="MotionSync" RPI="20000" Type="MotionSync" EventID="0" ProgrammaticallySendEventTrigger="false" />
</Connections>
</Communications>
</Module>
""", 'L5X_Samples/Sorter1_20260722r00.L5X', 1),
    '843E-MIPxxBAx/A': ("""\
<Module Name="TestMod1_843EMIPxxBAxA" CatalogNumber="843E-MIPxxBAx/A" Vendor="1" ProductType="34" ProductCode="4" Major="1" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false" SafetyEnabled="false" AutoDiagsEnabled="true">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="84">
<Data Format="L5K">
[88,884,11,2000,2000,0,4096,1,1,100,1,100,135405327,0,0,0,0,0,1999,655421536,0,0,4608]
</Data>
</ConfigData>
<Connections>
<Connection Name="Data" RPI="1000" Type="StandardDataDriven" OutputSize="4" InputSize="24" EventID="0" ProgrammaticallySendEventTrigger="false" Priority="Scheduled" InputConnectionType="Unicast" InputProductionTrigger="Cyclic" ConnectionPath="20 04 25 00 74 03 2d 00 e8 03 2d 00 28 04" InputTagSuffix="I" OutputTagSuffix="O">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:ENC1_DIAG:I:0">
<DataValueMember Name="RunMode" DataType="BOOL" Value="1" />
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="0" />
<DataValueMember Name="DiagnosticActive" DataType="BOOL" Value="1" />
<DataValueMember Name="DiagnosticSequenceCount" DataType="SINT" Radix="Decimal" Value="-70" />
<StructureMember Name="Encoder" DataType="CHANNEL_ENC_DIAG:I:0">
<DataValueMember Name="Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0" />
<DataValueMember Name="LVelocityAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="HVelocityAlarm" DataType="BOOL" Value="1" />
<DataValueMember Name="LAccelAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="HAccelAlarm" DataType="BOOL" Value="1" />
<DataValueMember Name="LPositionAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="HPositionAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="LTemperatureAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="HTemperatureAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Position" DataType="DINT" Radix="Decimal" Value="1522" />
<DataValueMember Name="Velocity" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Acceleration" DataType="DINT" Radix="Decimal" Value="4" />
<DataValueMember Name="TemperatureOutOfRange" DataType="BOOL" Value="0" />
<DataValueMember Name="OverCurrentLED" DataType="BOOL" Value="0" />
<DataValueMember Name="SystemPowerOutOfRange" DataType="BOOL" Value="0" />
<DataValueMember Name="OverVelocity" DataType="BOOL" Value="0" />
</StructureMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[[0,0,0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:ENC1:O:0">
<StructureMember Name="Encoder" DataType="CHANNEL_ENC:O:0">
<DataValueMember Name="SetZeroPosition" DataType="BOOL" Value="0" />
</StructureMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'BAI10048_TrimmerTally_20250704.L5X', 1),
    'AL1122': ("""\
<Module Name="TestMod1_AL1122" CatalogNumber="AL1122" Vendor="322" ProductType="12" ProductCode="1122" Major="1" Minor="5" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false" SafetyEnabled="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigTag ConfigSize="98" ExternalAccess="Read/Write">
<Data Format="L5K">
[102,4,3,4,3,0,1,0,0,0,0,1,3,0,1,0,0,0,0,1,3,0,1,0,0,0,0,1,3,0,1,0,0,0,0,1,3,0,1,0,0,0,0,1,3,0,1,0,0,0,0,1,3,0,1,0,0,0,0,1,3,0,1,0,0,0,0,1]
</Data>
<Data Format="Decorated">
<Structure DataType="_0142:AL1122_C3657FB3:C:0">
<DataValueMember Name="Communication_Profile" DataType="USINT" Radix="Decimal" Value="3" />
<DataValueMember Name="Port_Process_Data_Size" DataType="SINT" Radix="Decimal" Value="4" />
<DataValueMember Name="Port_Mode_Port_1" DataType="SINT" Radix="Decimal" Value="3" />
<DataValueMember Name="Port_Cycle_Time_Port_1" DataType="USINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Swap_Port_1" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="Validation_Data_Storage_Port_1" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Vendor_ID_Port_1" DataType="UINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Device_ID_Port_1" DataType="UDINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Fail_Safe_Mode_Port_1" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Fail_Safe_Value_DO_Port_1" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="Port_Mode_Port_2" DataType="SINT" Radix="Decimal" Value="3" />
<DataValueMember Name="Port_Cycle_Time_Port_2" DataType="USINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Swap_Port_2" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="Validation_Data_Storage_Port_2" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Vendor_ID_Port_2" DataType="UINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Device_ID_Port_2" DataType="UDINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Fail_Safe_Mode_Port_2" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Fail_Safe_Value_DO_Port_2" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="Port_Mode_Port_3" DataType="SINT" Radix="Decimal" Value="3" />
<DataValueMember Name="Port_Cycle_Time_Port_3" DataType="USINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Swap_Port_3" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="Validation_Data_Storage_Port_3" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Vendor_ID_Port_3" DataType="UINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Device_ID_Port_3" DataType="UDINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Fail_Safe_Mode_Port_3" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Fail_Safe_Value_DO_Port_3" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="Port_Mode_Port_4" DataType="SINT" Radix="Decimal" Value="3" />
<DataValueMember Name="Port_Cycle_Time_Port_4" DataType="USINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Swap_Port_4" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="Validation_Data_Storage_Port_4" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Vendor_ID_Port_4" DataType="UINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Device_ID_Port_4" DataType="UDINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Fail_Safe_Mode_Port_4" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Fail_Safe_Value_DO_Port_4" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="Port_Mode_Port_5" DataType="SINT" Radix="Decimal" Value="3" />
<DataValueMember Name="Port_Cycle_Time_Port_5" DataType="USINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Swap_Port_5" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="Validation_Data_Storage_Port_5" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Vendor_ID_Port_5" DataType="UINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Device_ID_Port_5" DataType="UDINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Fail_Safe_Mode_Port_5" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Fail_Safe_Value_DO_Port_5" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="Port_Mode_Port_6" DataType="SINT" Radix="Decimal" Value="3" />
<DataValueMember Name="Port_Cycle_Time_Port_6" DataType="USINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Swap_Port_6" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="Validation_Data_Storage_Port_6" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Vendor_ID_Port_6" DataType="UINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Device_ID_Port_6" DataType="UDINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Fail_Safe_Mode_Port_6" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Fail_Safe_Value_DO_Port_6" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="Port_Mode_Port_7" DataType="SINT" Radix="Decimal" Value="3" />
<DataValueMember Name="Port_Cycle_Time_Port_7" DataType="USINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Swap_Port_7" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="Validation_Data_Storage_Port_7" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Vendor_ID_Port_7" DataType="UINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Device_ID_Port_7" DataType="UDINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Fail_Safe_Mode_Port_7" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Fail_Safe_Value_DO_Port_7" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="Port_Mode_Port_8" DataType="SINT" Radix="Decimal" Value="3" />
<DataValueMember Name="Port_Cycle_Time_Port_8" DataType="USINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Swap_Port_8" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="Validation_Data_Storage_Port_8" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Vendor_ID_Port_8" DataType="UINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Device_ID_Port_8" DataType="UDINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Fail_Safe_Mode_Port_8" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Fail_Safe_Value_DO_Port_8" DataType="SINT" Radix="Decimal" Value="1" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="_200424C72C962C64" RPI="10000" Type="StandardDataDriven" OutputSize="302" InputSize="450" EventID="0" ProgrammaticallySendEventTrigger="false" Priority="Scheduled" InputConnectionType="Unicast" InputProductionTrigger="Cyclic" ConnectionPath="20 04 24 c7 2c 96 2c 64" InputTagSuffix="I1" OutputTagSuffix="O1">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="_0142:AL1122_04852EE3:I:0">
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="0" />
<ArrayMember Name="Data" DataType="INT" Dimensions="223" Radix="Decimal">
<Element Index="[0]" Value="0" />
<Element Index="[1]" Value="0" />
<Element Index="[2]" Value="0" />
<Element Index="[3]" Value="0" />
<Element Index="[4]" Value="0" />
<Element Index="[5]" Value="0" />
<Element Index="[6]" Value="0" />
<Element Index="[7]" Value="0" />
<Element Index="[8]" Value="0" />
<Element Index="[9]" Value="0" />
<Element Index="[10]" Value="0" />
<Element Index="[11]" Value="0" />
<Element Index="[12]" Value="0" />
<Element Index="[13]" Value="0" />
<Element Index="[14]" Value="0" />
<Element Index="[15]" Value="0" />
<Element Index="[16]" Value="0" />
<Element Index="[17]" Value="0" />
<Element Index="[18]" Value="0" />
<Element Index="[19]" Value="0" />
<Element Index="[20]" Value="0" />
<Element Index="[21]" Value="0" />
<Element Index="[22]" Value="0" />
<Element Index="[23]" Value="0" />
<Element Index="[24]" Value="0" />
<Element Index="[25]" Value="0" />
<Element Index="[26]" Value="0" />
<Element Index="[27]" Value="0" />
<Element Index="[28]" Value="0" />
<Element Index="[29]" Value="0" />
<Element Index="[30]" Value="0" />
<Element Index="[31]" Value="0" />
<Element Index="[32]" Value="0" />
<Element Index="[33]" Value="0" />
<Element Index="[34]" Value="0" />
<Element Index="[35]" Value="0" />
<Element Index="[36]" Value="0" />
<Element Index="[37]" Value="0" />
<Element Index="[38]" Value="0" />
<Element Index="[39]" Value="0" />
<Element Index="[40]" Value="0" />
<Element Index="[41]" Value="0" />
<Element Index="[42]" Value="0" />
<Element Index="[43]" Value="0" />
<Element Index="[44]" Value="0" />
<Element Index="[45]" Value="0" />
<Element Index="[46]" Value="0" />
<Element Index="[47]" Value="0" />
<Element Index="[48]" Value="0" />
<Element Index="[49]" Value="0" />
<Element Index="[50]" Value="0" />
<Element Index="[51]" Value="0" />
<Element Index="[52]" Value="0" />
<Element Index="[53]" Value="0" />
<Element Index="[54]" Value="0" />
<Element Index="[55]" Value="0" />
<Element Index="[56]" Value="0" />
<Element Index="[57]" Value="0" />
<Element Index="[58]" Value="0" />
<Element Index="[59]" Value="0" />
<Element Index="[60]" Value="0" />
<Element Index="[61]" Value="0" />
<Element Index="[62]" Value="0" />
<Element Index="[63]" Value="0" />
<Element Index="[64]" Value="0" />
<Element Index="[65]" Value="0" />
<Element Index="[66]" Value="0" />
<Element Index="[67]" Value="0" />
<Element Index="[68]" Value="0" />
<Element Index="[69]" Value="0" />
<Element Index="[70]" Value="0" />
<Element Index="[71]" Value="0" />
<Element Index="[72]" Value="0" />
<Element Index="[73]" Value="0" />
<Element Index="[74]" Value="0" />
<Element Index="[75]" Value="0" />
<Element Index="[76]" Value="0" />
<Element Index="[77]" Value="0" />
<Element Index="[78]" Value="0" />
<Element Index="[79]" Value="0" />
<Element Index="[80]" Value="0" />
<Element Index="[81]" Value="0" />
<Element Index="[82]" Value="0" />
<Element Index="[83]" Value="0" />
<Element Index="[84]" Value="0" />
<Element Index="[85]" Value="0" />
<Element Index="[86]" Value="0" />
<Element Index="[87]" Value="0" />
<Element Index="[88]" Value="0" />
<Element Index="[89]" Value="0" />
<Element Index="[90]" Value="0" />
<Element Index="[91]" Value="0" />
<Element Index="[92]" Value="0" />
<Element Index="[93]" Value="0" />
<Element Index="[94]" Value="0" />
<Element Index="[95]" Value="0" />
<Element Index="[96]" Value="0" />
<Element Index="[97]" Value="0" />
<Element Index="[98]" Value="0" />
<Element Index="[99]" Value="0" />
<Element Index="[100]" Value="0" />
<Element Index="[101]" Value="0" />
<Element Index="[102]" Value="0" />
<Element Index="[103]" Value="0" />
<Element Index="[104]" Value="0" />
<Element Index="[105]" Value="0" />
<Element Index="[106]" Value="0" />
<Element Index="[107]" Value="0" />
<Element Index="[108]" Value="0" />
<Element Index="[109]" Value="0" />
<Element Index="[110]" Value="0" />
<Element Index="[111]" Value="0" />
<Element Index="[112]" Value="0" />
<Element Index="[113]" Value="0" />
<Element Index="[114]" Value="0" />
<Element Index="[115]" Value="0" />
<Element Index="[116]" Value="0" />
<Element Index="[117]" Value="0" />
<Element Index="[118]" Value="0" />
<Element Index="[119]" Value="0" />
<Element Index="[120]" Value="0" />
<Element Index="[121]" Value="0" />
<Element Index="[122]" Value="0" />
<Element Index="[123]" Value="0" />
<Element Index="[124]" Value="0" />
<Element Index="[125]" Value="0" />
<Element Index="[126]" Value="0" />
<Element Index="[127]" Value="0" />
<Element Index="[128]" Value="0" />
<Element Index="[129]" Value="0" />
<Element Index="[130]" Value="0" />
<Element Index="[131]" Value="0" />
<Element Index="[132]" Value="0" />
<Element Index="[133]" Value="0" />
<Element Index="[134]" Value="0" />
<Element Index="[135]" Value="0" />
<Element Index="[136]" Value="0" />
<Element Index="[137]" Value="0" />
<Element Index="[138]" Value="0" />
<Element Index="[139]" Value="0" />
<Element Index="[140]" Value="0" />
<Element Index="[141]" Value="0" />
<Element Index="[142]" Value="0" />
<Element Index="[143]" Value="0" />
<Element Index="[144]" Value="0" />
<Element Index="[145]" Value="0" />
<Element Index="[146]" Value="0" />
<Element Index="[147]" Value="0" />
<Element Index="[148]" Value="0" />
<Element Index="[149]" Value="0" />
<Element Index="[150]" Value="0" />
<Element Index="[151]" Value="0" />
<Element Index="[152]" Value="0" />
<Element Index="[153]" Value="0" />
<Element Index="[154]" Value="0" />
<Element Index="[155]" Value="0" />
<Element Index="[156]" Value="0" />
<Element Index="[157]" Value="0" />
<Element Index="[158]" Value="0" />
<Element Index="[159]" Value="0" />
<Element Index="[160]" Value="0" />
<Element Index="[161]" Value="0" />
<Element Index="[162]" Value="0" />
<Element Index="[163]" Value="0" />
<Element Index="[164]" Value="0" />
<Element Index="[165]" Value="0" />
<Element Index="[166]" Value="0" />
<Element Index="[167]" Value="0" />
<Element Index="[168]" Value="0" />
<Element Index="[169]" Value="0" />
<Element Index="[170]" Value="0" />
<Element Index="[171]" Value="0" />
<Element Index="[172]" Value="0" />
<Element Index="[173]" Value="0" />
<Element Index="[174]" Value="0" />
<Element Index="[175]" Value="0" />
<Element Index="[176]" Value="0" />
<Element Index="[177]" Value="0" />
<Element Index="[178]" Value="0" />
<Element Index="[179]" Value="0" />
<Element Index="[180]" Value="0" />
<Element Index="[181]" Value="0" />
<Element Index="[182]" Value="0" />
<Element Index="[183]" Value="0" />
<Element Index="[184]" Value="0" />
<Element Index="[185]" Value="0" />
<Element Index="[186]" Value="0" />
<Element Index="[187]" Value="0" />
<Element Index="[188]" Value="0" />
<Element Index="[189]" Value="0" />
<Element Index="[190]" Value="0" />
<Element Index="[191]" Value="0" />
<Element Index="[192]" Value="0" />
<Element Index="[193]" Value="0" />
<Element Index="[194]" Value="0" />
<Element Index="[195]" Value="0" />
<Element Index="[196]" Value="0" />
<Element Index="[197]" Value="0" />
<Element Index="[198]" Value="0" />
<Element Index="[199]" Value="0" />
<Element Index="[200]" Value="0" />
<Element Index="[201]" Value="0" />
<Element Index="[202]" Value="0" />
<Element Index="[203]" Value="0" />
<Element Index="[204]" Value="0" />
<Element Index="[205]" Value="0" />
<Element Index="[206]" Value="0" />
<Element Index="[207]" Value="0" />
<Element Index="[208]" Value="0" />
<Element Index="[209]" Value="0" />
<Element Index="[210]" Value="0" />
<Element Index="[211]" Value="0" />
<Element Index="[212]" Value="0" />
<Element Index="[213]" Value="0" />
<Element Index="[214]" Value="0" />
<Element Index="[215]" Value="0" />
<Element Index="[216]" Value="0" />
<Element Index="[217]" Value="0" />
<Element Index="[218]" Value="0" />
<Element Index="[219]" Value="0" />
<Element Index="[220]" Value="0" />
<Element Index="[221]" Value="0" />
<Element Index="[222]" Value="0" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="_0142:AL1122_23FE281C:O:0">
<ArrayMember Name="Data" DataType="INT" Dimensions="151" Radix="Decimal">
<Element Index="[0]" Value="0" />
<Element Index="[1]" Value="0" />
<Element Index="[2]" Value="0" />
<Element Index="[3]" Value="0" />
<Element Index="[4]" Value="0" />
<Element Index="[5]" Value="0" />
<Element Index="[6]" Value="0" />
<Element Index="[7]" Value="0" />
<Element Index="[8]" Value="0" />
<Element Index="[9]" Value="0" />
<Element Index="[10]" Value="0" />
<Element Index="[11]" Value="0" />
<Element Index="[12]" Value="0" />
<Element Index="[13]" Value="0" />
<Element Index="[14]" Value="0" />
<Element Index="[15]" Value="0" />
<Element Index="[16]" Value="0" />
<Element Index="[17]" Value="0" />
<Element Index="[18]" Value="0" />
<Element Index="[19]" Value="0" />
<Element Index="[20]" Value="0" />
<Element Index="[21]" Value="0" />
<Element Index="[22]" Value="0" />
<Element Index="[23]" Value="0" />
<Element Index="[24]" Value="0" />
<Element Index="[25]" Value="0" />
<Element Index="[26]" Value="0" />
<Element Index="[27]" Value="0" />
<Element Index="[28]" Value="0" />
<Element Index="[29]" Value="0" />
<Element Index="[30]" Value="0" />
<Element Index="[31]" Value="0" />
<Element Index="[32]" Value="0" />
<Element Index="[33]" Value="0" />
<Element Index="[34]" Value="0" />
<Element Index="[35]" Value="0" />
<Element Index="[36]" Value="0" />
<Element Index="[37]" Value="0" />
<Element Index="[38]" Value="0" />
<Element Index="[39]" Value="0" />
<Element Index="[40]" Value="0" />
<Element Index="[41]" Value="0" />
<Element Index="[42]" Value="0" />
<Element Index="[43]" Value="0" />
<Element Index="[44]" Value="0" />
<Element Index="[45]" Value="0" />
<Element Index="[46]" Value="0" />
<Element Index="[47]" Value="0" />
<Element Index="[48]" Value="0" />
<Element Index="[49]" Value="0" />
<Element Index="[50]" Value="0" />
<Element Index="[51]" Value="0" />
<Element Index="[52]" Value="0" />
<Element Index="[53]" Value="0" />
<Element Index="[54]" Value="0" />
<Element Index="[55]" Value="0" />
<Element Index="[56]" Value="0" />
<Element Index="[57]" Value="0" />
<Element Index="[58]" Value="0" />
<Element Index="[59]" Value="0" />
<Element Index="[60]" Value="0" />
<Element Index="[61]" Value="0" />
<Element Index="[62]" Value="0" />
<Element Index="[63]" Value="0" />
<Element Index="[64]" Value="0" />
<Element Index="[65]" Value="0" />
<Element Index="[66]" Value="0" />
<Element Index="[67]" Value="0" />
<Element Index="[68]" Value="0" />
<Element Index="[69]" Value="0" />
<Element Index="[70]" Value="0" />
<Element Index="[71]" Value="0" />
<Element Index="[72]" Value="0" />
<Element Index="[73]" Value="0" />
<Element Index="[74]" Value="0" />
<Element Index="[75]" Value="0" />
<Element Index="[76]" Value="0" />
<Element Index="[77]" Value="0" />
<Element Index="[78]" Value="0" />
<Element Index="[79]" Value="0" />
<Element Index="[80]" Value="0" />
<Element Index="[81]" Value="0" />
<Element Index="[82]" Value="0" />
<Element Index="[83]" Value="0" />
<Element Index="[84]" Value="0" />
<Element Index="[85]" Value="0" />
<Element Index="[86]" Value="0" />
<Element Index="[87]" Value="0" />
<Element Index="[88]" Value="0" />
<Element Index="[89]" Value="0" />
<Element Index="[90]" Value="0" />
<Element Index="[91]" Value="0" />
<Element Index="[92]" Value="0" />
<Element Index="[93]" Value="0" />
<Element Index="[94]" Value="0" />
<Element Index="[95]" Value="0" />
<Element Index="[96]" Value="0" />
<Element Index="[97]" Value="0" />
<Element Index="[98]" Value="0" />
<Element Index="[99]" Value="0" />
<Element Index="[100]" Value="0" />
<Element Index="[101]" Value="0" />
<Element Index="[102]" Value="0" />
<Element Index="[103]" Value="0" />
<Element Index="[104]" Value="0" />
<Element Index="[105]" Value="0" />
<Element Index="[106]" Value="0" />
<Element Index="[107]" Value="0" />
<Element Index="[108]" Value="0" />
<Element Index="[109]" Value="0" />
<Element Index="[110]" Value="0" />
<Element Index="[111]" Value="0" />
<Element Index="[112]" Value="0" />
<Element Index="[113]" Value="0" />
<Element Index="[114]" Value="0" />
<Element Index="[115]" Value="0" />
<Element Index="[116]" Value="0" />
<Element Index="[117]" Value="0" />
<Element Index="[118]" Value="0" />
<Element Index="[119]" Value="0" />
<Element Index="[120]" Value="0" />
<Element Index="[121]" Value="0" />
<Element Index="[122]" Value="0" />
<Element Index="[123]" Value="0" />
<Element Index="[124]" Value="0" />
<Element Index="[125]" Value="0" />
<Element Index="[126]" Value="0" />
<Element Index="[127]" Value="0" />
<Element Index="[128]" Value="0" />
<Element Index="[129]" Value="0" />
<Element Index="[130]" Value="0" />
<Element Index="[131]" Value="0" />
<Element Index="[132]" Value="0" />
<Element Index="[133]" Value="0" />
<Element Index="[134]" Value="0" />
<Element Index="[135]" Value="0" />
<Element Index="[136]" Value="0" />
<Element Index="[137]" Value="0" />
<Element Index="[138]" Value="0" />
<Element Index="[139]" Value="0" />
<Element Index="[140]" Value="0" />
<Element Index="[141]" Value="0" />
<Element Index="[142]" Value="0" />
<Element Index="[143]" Value="0" />
<Element Index="[144]" Value="0" />
<Element Index="[145]" Value="0" />
<Element Index="[146]" Value="0" />
<Element Index="[147]" Value="0" />
<Element Index="[148]" Value="0" />
<Element Index="[149]" Value="0" />
<Element Index="[150]" Value="0" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'SJ_Gormley_20251112_r02.L5X', 1),
    'AL1222': ("""\
<Module Name="TestMod1_AL1222" CatalogNumber="AL1222" Vendor="322" ProductType="12" ProductCode="1222" Major="1" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false" SafetyEnabled="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigTag ConfigSize="98" ExternalAccess="Read/Write">
<Data Format="L5K">
[102,4,3,4,3,0,1,0,0,0,0,1,3,0,1,0,0,0,0,1,3,0,1,0,0,0,0,1,3,0,1,0,0,0,0,1,3,0,1,0,0,0,0,1,3,0,1,0,0,0,0,1,3,0,1,0,0,0,0,1,3,0,1,0,0,0,0,1]
</Data>
<Data Format="Decorated">
<Structure DataType="_0142:AL1222_C3657FB3:C:0">
<DataValueMember Name="Communication_Profile" DataType="USINT" Radix="Decimal" Value="3" />
<DataValueMember Name="Port_Process_Data_Size" DataType="SINT" Radix="Decimal" Value="4" />
<DataValueMember Name="Port_Mode_Port_1" DataType="SINT" Radix="Decimal" Value="3" />
<DataValueMember Name="Port_Cycle_Time_Port_1" DataType="USINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Swap_Port_1" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="Validation_Data_Storage_Port_1" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Vendor_ID_Port_1" DataType="UINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Device_ID_Port_1" DataType="UDINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Fail_Safe_Mode_Port_1" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Fail_Safe_Value_DO_Port_1" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="Port_Mode_Port_2" DataType="SINT" Radix="Decimal" Value="3" />
<DataValueMember Name="Port_Cycle_Time_Port_2" DataType="USINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Swap_Port_2" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="Validation_Data_Storage_Port_2" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Vendor_ID_Port_2" DataType="UINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Device_ID_Port_2" DataType="UDINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Fail_Safe_Mode_Port_2" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Fail_Safe_Value_DO_Port_2" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="Port_Mode_Port_3" DataType="SINT" Radix="Decimal" Value="3" />
<DataValueMember Name="Port_Cycle_Time_Port_3" DataType="USINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Swap_Port_3" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="Validation_Data_Storage_Port_3" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Vendor_ID_Port_3" DataType="UINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Device_ID_Port_3" DataType="UDINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Fail_Safe_Mode_Port_3" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Fail_Safe_Value_DO_Port_3" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="Port_Mode_Port_4" DataType="SINT" Radix="Decimal" Value="3" />
<DataValueMember Name="Port_Cycle_Time_Port_4" DataType="USINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Swap_Port_4" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="Validation_Data_Storage_Port_4" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Vendor_ID_Port_4" DataType="UINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Device_ID_Port_4" DataType="UDINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Fail_Safe_Mode_Port_4" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Fail_Safe_Value_DO_Port_4" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="Port_Mode_Port_5" DataType="SINT" Radix="Decimal" Value="3" />
<DataValueMember Name="Port_Cycle_Time_Port_5" DataType="USINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Swap_Port_5" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="Validation_Data_Storage_Port_5" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Vendor_ID_Port_5" DataType="UINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Device_ID_Port_5" DataType="UDINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Fail_Safe_Mode_Port_5" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Fail_Safe_Value_DO_Port_5" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="Port_Mode_Port_6" DataType="SINT" Radix="Decimal" Value="3" />
<DataValueMember Name="Port_Cycle_Time_Port_6" DataType="USINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Swap_Port_6" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="Validation_Data_Storage_Port_6" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Vendor_ID_Port_6" DataType="UINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Device_ID_Port_6" DataType="UDINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Fail_Safe_Mode_Port_6" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Fail_Safe_Value_DO_Port_6" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="Port_Mode_Port_7" DataType="SINT" Radix="Decimal" Value="3" />
<DataValueMember Name="Port_Cycle_Time_Port_7" DataType="USINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Swap_Port_7" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="Validation_Data_Storage_Port_7" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Vendor_ID_Port_7" DataType="UINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Device_ID_Port_7" DataType="UDINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Fail_Safe_Mode_Port_7" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Fail_Safe_Value_DO_Port_7" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="Port_Mode_Port_8" DataType="SINT" Radix="Decimal" Value="3" />
<DataValueMember Name="Port_Cycle_Time_Port_8" DataType="USINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Swap_Port_8" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="Validation_Data_Storage_Port_8" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Vendor_ID_Port_8" DataType="UINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Device_ID_Port_8" DataType="UDINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Fail_Safe_Mode_Port_8" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Fail_Safe_Value_DO_Port_8" DataType="SINT" Radix="Decimal" Value="1" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="_200424C72C962C64" RPI="10000" Type="StandardDataDriven" OutputSize="302" InputSize="450" EventID="0" ProgrammaticallySendEventTrigger="false" Priority="Scheduled" InputConnectionType="Unicast" InputProductionTrigger="Cyclic" ConnectionPath="20 04 24 c7 2c 96 2c 64" InputTagSuffix="I1" OutputTagSuffix="O1">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="_0142:AL1222_90D03083:I:0">
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="0" />
<ArrayMember Name="Data" DataType="SINT" Dimensions="446" Radix="Decimal">
<Element Index="[0]" Value="0" />
<Element Index="[1]" Value="0" />
<Element Index="[2]" Value="0" />
<Element Index="[3]" Value="0" />
<Element Index="[4]" Value="0" />
<Element Index="[5]" Value="0" />
<Element Index="[6]" Value="0" />
<Element Index="[7]" Value="0" />
<Element Index="[8]" Value="0" />
<Element Index="[9]" Value="0" />
<Element Index="[10]" Value="0" />
<Element Index="[11]" Value="0" />
<Element Index="[12]" Value="0" />
<Element Index="[13]" Value="0" />
<Element Index="[14]" Value="0" />
<Element Index="[15]" Value="0" />
<Element Index="[16]" Value="0" />
<Element Index="[17]" Value="0" />
<Element Index="[18]" Value="0" />
<Element Index="[19]" Value="0" />
<Element Index="[20]" Value="0" />
<Element Index="[21]" Value="0" />
<Element Index="[22]" Value="0" />
<Element Index="[23]" Value="0" />
<Element Index="[24]" Value="0" />
<Element Index="[25]" Value="0" />
<Element Index="[26]" Value="0" />
<Element Index="[27]" Value="0" />
<Element Index="[28]" Value="0" />
<Element Index="[29]" Value="0" />
<Element Index="[30]" Value="0" />
<Element Index="[31]" Value="0" />
<Element Index="[32]" Value="0" />
<Element Index="[33]" Value="0" />
<Element Index="[34]" Value="0" />
<Element Index="[35]" Value="0" />
<Element Index="[36]" Value="0" />
<Element Index="[37]" Value="0" />
<Element Index="[38]" Value="0" />
<Element Index="[39]" Value="0" />
<Element Index="[40]" Value="0" />
<Element Index="[41]" Value="0" />
<Element Index="[42]" Value="0" />
<Element Index="[43]" Value="0" />
<Element Index="[44]" Value="0" />
<Element Index="[45]" Value="0" />
<Element Index="[46]" Value="7" />
<Element Index="[47]" Value="0" />
<Element Index="[48]" Value="0" />
<Element Index="[49]" Value="0" />
<Element Index="[50]" Value="0" />
<Element Index="[51]" Value="0" />
<Element Index="[52]" Value="0" />
<Element Index="[53]" Value="0" />
<Element Index="[54]" Value="0" />
<Element Index="[55]" Value="0" />
<Element Index="[56]" Value="0" />
<Element Index="[57]" Value="0" />
<Element Index="[58]" Value="0" />
<Element Index="[59]" Value="0" />
<Element Index="[60]" Value="0" />
<Element Index="[61]" Value="0" />
<Element Index="[62]" Value="0" />
<Element Index="[63]" Value="0" />
<Element Index="[64]" Value="7" />
<Element Index="[65]" Value="0" />
<Element Index="[66]" Value="0" />
<Element Index="[67]" Value="0" />
<Element Index="[68]" Value="0" />
<Element Index="[69]" Value="0" />
<Element Index="[70]" Value="0" />
<Element Index="[71]" Value="0" />
<Element Index="[72]" Value="0" />
<Element Index="[73]" Value="0" />
<Element Index="[74]" Value="0" />
<Element Index="[75]" Value="0" />
<Element Index="[76]" Value="0" />
<Element Index="[77]" Value="0" />
<Element Index="[78]" Value="0" />
<Element Index="[79]" Value="0" />
<Element Index="[80]" Value="0" />
<Element Index="[81]" Value="0" />
<Element Index="[82]" Value="7" />
<Element Index="[83]" Value="0" />
<Element Index="[84]" Value="0" />
<Element Index="[85]" Value="0" />
<Element Index="[86]" Value="0" />
<Element Index="[87]" Value="0" />
<Element Index="[88]" Value="0" />
<Element Index="[89]" Value="0" />
<Element Index="[90]" Value="0" />
<Element Index="[91]" Value="0" />
<Element Index="[92]" Value="0" />
<Element Index="[93]" Value="0" />
<Element Index="[94]" Value="0" />
<Element Index="[95]" Value="0" />
<Element Index="[96]" Value="0" />
<Element Index="[97]" Value="0" />
<Element Index="[98]" Value="0" />
<Element Index="[99]" Value="0" />
<Element Index="[100]" Value="7" />
<Element Index="[101]" Value="0" />
<Element Index="[102]" Value="0" />
<Element Index="[103]" Value="0" />
<Element Index="[104]" Value="0" />
<Element Index="[105]" Value="0" />
<Element Index="[106]" Value="0" />
<Element Index="[107]" Value="0" />
<Element Index="[108]" Value="0" />
<Element Index="[109]" Value="0" />
<Element Index="[110]" Value="0" />
<Element Index="[111]" Value="0" />
<Element Index="[112]" Value="0" />
<Element Index="[113]" Value="0" />
<Element Index="[114]" Value="0" />
<Element Index="[115]" Value="0" />
<Element Index="[116]" Value="0" />
<Element Index="[117]" Value="0" />
<Element Index="[118]" Value="1" />
<Element Index="[119]" Value="0" />
<Element Index="[120]" Value="47" />
<Element Index="[121]" Value="1" />
<Element Index="[122]" Value="19" />
<Element Index="[123]" Value="0" />
<Element Index="[124]" Value="12" />
<Element Index="[125]" Value="0" />
<Element Index="[126]" Value="0" />
<Element Index="[127]" Value="0" />
<Element Index="[128]" Value="0" />
<Element Index="[129]" Value="0" />
<Element Index="[130]" Value="0" />
<Element Index="[131]" Value="0" />
<Element Index="[132]" Value="0" />
<Element Index="[133]" Value="0" />
<Element Index="[134]" Value="0" />
<Element Index="[135]" Value="0" />
<Element Index="[136]" Value="7" />
<Element Index="[137]" Value="0" />
<Element Index="[138]" Value="0" />
<Element Index="[139]" Value="0" />
<Element Index="[140]" Value="0" />
<Element Index="[141]" Value="0" />
<Element Index="[142]" Value="0" />
<Element Index="[143]" Value="0" />
<Element Index="[144]" Value="0" />
<Element Index="[145]" Value="0" />
<Element Index="[146]" Value="0" />
<Element Index="[147]" Value="0" />
<Element Index="[148]" Value="0" />
<Element Index="[149]" Value="0" />
<Element Index="[150]" Value="0" />
<Element Index="[151]" Value="0" />
<Element Index="[152]" Value="0" />
<Element Index="[153]" Value="0" />
<Element Index="[154]" Value="7" />
<Element Index="[155]" Value="0" />
<Element Index="[156]" Value="0" />
<Element Index="[157]" Value="0" />
<Element Index="[158]" Value="0" />
<Element Index="[159]" Value="0" />
<Element Index="[160]" Value="0" />
<Element Index="[161]" Value="0" />
<Element Index="[162]" Value="0" />
<Element Index="[163]" Value="0" />
<Element Index="[164]" Value="0" />
<Element Index="[165]" Value="0" />
<Element Index="[166]" Value="0" />
<Element Index="[167]" Value="0" />
<Element Index="[168]" Value="0" />
<Element Index="[169]" Value="0" />
<Element Index="[170]" Value="0" />
<Element Index="[171]" Value="0" />
<Element Index="[172]" Value="7" />
<Element Index="[173]" Value="0" />
<Element Index="[174]" Value="0" />
<Element Index="[175]" Value="0" />
<Element Index="[176]" Value="0" />
<Element Index="[177]" Value="0" />
<Element Index="[178]" Value="0" />
<Element Index="[179]" Value="0" />
<Element Index="[180]" Value="0" />
<Element Index="[181]" Value="0" />
<Element Index="[182]" Value="0" />
<Element Index="[183]" Value="0" />
<Element Index="[184]" Value="0" />
<Element Index="[185]" Value="0" />
<Element Index="[186]" Value="0" />
<Element Index="[187]" Value="0" />
<Element Index="[188]" Value="0" />
<Element Index="[189]" Value="0" />
<Element Index="[190]" Value="0" />
<Element Index="[191]" Value="0" />
<Element Index="[192]" Value="0" />
<Element Index="[193]" Value="0" />
<Element Index="[194]" Value="0" />
<Element Index="[195]" Value="0" />
<Element Index="[196]" Value="0" />
<Element Index="[197]" Value="0" />
<Element Index="[198]" Value="0" />
<Element Index="[199]" Value="0" />
<Element Index="[200]" Value="0" />
<Element Index="[201]" Value="0" />
<Element Index="[202]" Value="0" />
<Element Index="[203]" Value="0" />
<Element Index="[204]" Value="0" />
<Element Index="[205]" Value="0" />
<Element Index="[206]" Value="0" />
<Element Index="[207]" Value="0" />
<Element Index="[208]" Value="0" />
<Element Index="[209]" Value="0" />
<Element Index="[210]" Value="0" />
<Element Index="[211]" Value="0" />
<Element Index="[212]" Value="0" />
<Element Index="[213]" Value="0" />
<Element Index="[214]" Value="0" />
<Element Index="[215]" Value="0" />
<Element Index="[216]" Value="0" />
<Element Index="[217]" Value="0" />
<Element Index="[218]" Value="0" />
<Element Index="[219]" Value="0" />
<Element Index="[220]" Value="0" />
<Element Index="[221]" Value="0" />
<Element Index="[222]" Value="0" />
<Element Index="[223]" Value="0" />
<Element Index="[224]" Value="0" />
<Element Index="[225]" Value="0" />
<Element Index="[226]" Value="0" />
<Element Index="[227]" Value="0" />
<Element Index="[228]" Value="0" />
<Element Index="[229]" Value="0" />
<Element Index="[230]" Value="0" />
<Element Index="[231]" Value="0" />
<Element Index="[232]" Value="0" />
<Element Index="[233]" Value="0" />
<Element Index="[234]" Value="0" />
<Element Index="[235]" Value="0" />
<Element Index="[236]" Value="0" />
<Element Index="[237]" Value="0" />
<Element Index="[238]" Value="0" />
<Element Index="[239]" Value="0" />
<Element Index="[240]" Value="0" />
<Element Index="[241]" Value="0" />
<Element Index="[242]" Value="0" />
<Element Index="[243]" Value="0" />
<Element Index="[244]" Value="0" />
<Element Index="[245]" Value="0" />
<Element Index="[246]" Value="0" />
<Element Index="[247]" Value="0" />
<Element Index="[248]" Value="0" />
<Element Index="[249]" Value="0" />
<Element Index="[250]" Value="0" />
<Element Index="[251]" Value="0" />
<Element Index="[252]" Value="0" />
<Element Index="[253]" Value="0" />
<Element Index="[254]" Value="0" />
<Element Index="[255]" Value="0" />
<Element Index="[256]" Value="0" />
<Element Index="[257]" Value="0" />
<Element Index="[258]" Value="0" />
<Element Index="[259]" Value="0" />
<Element Index="[260]" Value="0" />
<Element Index="[261]" Value="0" />
<Element Index="[262]" Value="0" />
<Element Index="[263]" Value="0" />
<Element Index="[264]" Value="0" />
<Element Index="[265]" Value="0" />
<Element Index="[266]" Value="0" />
<Element Index="[267]" Value="0" />
<Element Index="[268]" Value="0" />
<Element Index="[269]" Value="0" />
<Element Index="[270]" Value="0" />
<Element Index="[271]" Value="0" />
<Element Index="[272]" Value="0" />
<Element Index="[273]" Value="0" />
<Element Index="[274]" Value="0" />
<Element Index="[275]" Value="0" />
<Element Index="[276]" Value="0" />
<Element Index="[277]" Value="0" />
<Element Index="[278]" Value="0" />
<Element Index="[279]" Value="0" />
<Element Index="[280]" Value="0" />
<Element Index="[281]" Value="0" />
<Element Index="[282]" Value="0" />
<Element Index="[283]" Value="0" />
<Element Index="[284]" Value="0" />
<Element Index="[285]" Value="0" />
<Element Index="[286]" Value="0" />
<Element Index="[287]" Value="0" />
<Element Index="[288]" Value="0" />
<Element Index="[289]" Value="0" />
<Element Index="[290]" Value="0" />
<Element Index="[291]" Value="0" />
<Element Index="[292]" Value="0" />
<Element Index="[293]" Value="0" />
<Element Index="[294]" Value="0" />
<Element Index="[295]" Value="0" />
<Element Index="[296]" Value="0" />
<Element Index="[297]" Value="0" />
<Element Index="[298]" Value="0" />
<Element Index="[299]" Value="0" />
<Element Index="[300]" Value="0" />
<Element Index="[301]" Value="0" />
<Element Index="[302]" Value="0" />
<Element Index="[303]" Value="0" />
<Element Index="[304]" Value="0" />
<Element Index="[305]" Value="0" />
<Element Index="[306]" Value="0" />
<Element Index="[307]" Value="0" />
<Element Index="[308]" Value="0" />
<Element Index="[309]" Value="0" />
<Element Index="[310]" Value="0" />
<Element Index="[311]" Value="0" />
<Element Index="[312]" Value="0" />
<Element Index="[313]" Value="0" />
<Element Index="[314]" Value="0" />
<Element Index="[315]" Value="0" />
<Element Index="[316]" Value="0" />
<Element Index="[317]" Value="0" />
<Element Index="[318]" Value="10" />
<Element Index="[319]" Value="-93" />
<Element Index="[320]" Value="0" />
<Element Index="[321]" Value="0" />
<Element Index="[322]" Value="0" />
<Element Index="[323]" Value="0" />
<Element Index="[324]" Value="0" />
<Element Index="[325]" Value="0" />
<Element Index="[326]" Value="0" />
<Element Index="[327]" Value="0" />
<Element Index="[328]" Value="0" />
<Element Index="[329]" Value="0" />
<Element Index="[330]" Value="0" />
<Element Index="[331]" Value="0" />
<Element Index="[332]" Value="0" />
<Element Index="[333]" Value="0" />
<Element Index="[334]" Value="0" />
<Element Index="[335]" Value="0" />
<Element Index="[336]" Value="0" />
<Element Index="[337]" Value="0" />
<Element Index="[338]" Value="0" />
<Element Index="[339]" Value="0" />
<Element Index="[340]" Value="0" />
<Element Index="[341]" Value="0" />
<Element Index="[342]" Value="0" />
<Element Index="[343]" Value="0" />
<Element Index="[344]" Value="0" />
<Element Index="[345]" Value="0" />
<Element Index="[346]" Value="0" />
<Element Index="[347]" Value="0" />
<Element Index="[348]" Value="0" />
<Element Index="[349]" Value="0" />
<Element Index="[350]" Value="0" />
<Element Index="[351]" Value="0" />
<Element Index="[352]" Value="0" />
<Element Index="[353]" Value="0" />
<Element Index="[354]" Value="0" />
<Element Index="[355]" Value="0" />
<Element Index="[356]" Value="0" />
<Element Index="[357]" Value="0" />
<Element Index="[358]" Value="0" />
<Element Index="[359]" Value="0" />
<Element Index="[360]" Value="0" />
<Element Index="[361]" Value="0" />
<Element Index="[362]" Value="0" />
<Element Index="[363]" Value="0" />
<Element Index="[364]" Value="0" />
<Element Index="[365]" Value="0" />
<Element Index="[366]" Value="0" />
<Element Index="[367]" Value="0" />
<Element Index="[368]" Value="0" />
<Element Index="[369]" Value="0" />
<Element Index="[370]" Value="0" />
<Element Index="[371]" Value="0" />
<Element Index="[372]" Value="0" />
<Element Index="[373]" Value="0" />
<Element Index="[374]" Value="0" />
<Element Index="[375]" Value="0" />
<Element Index="[376]" Value="0" />
<Element Index="[377]" Value="0" />
<Element Index="[378]" Value="0" />
<Element Index="[379]" Value="0" />
<Element Index="[380]" Value="0" />
<Element Index="[381]" Value="0" />
<Element Index="[382]" Value="0" />
<Element Index="[383]" Value="0" />
<Element Index="[384]" Value="0" />
<Element Index="[385]" Value="0" />
<Element Index="[386]" Value="0" />
<Element Index="[387]" Value="0" />
<Element Index="[388]" Value="0" />
<Element Index="[389]" Value="0" />
<Element Index="[390]" Value="0" />
<Element Index="[391]" Value="0" />
<Element Index="[392]" Value="0" />
<Element Index="[393]" Value="0" />
<Element Index="[394]" Value="0" />
<Element Index="[395]" Value="0" />
<Element Index="[396]" Value="0" />
<Element Index="[397]" Value="0" />
<Element Index="[398]" Value="0" />
<Element Index="[399]" Value="0" />
<Element Index="[400]" Value="0" />
<Element Index="[401]" Value="0" />
<Element Index="[402]" Value="0" />
<Element Index="[403]" Value="0" />
<Element Index="[404]" Value="0" />
<Element Index="[405]" Value="0" />
<Element Index="[406]" Value="0" />
<Element Index="[407]" Value="0" />
<Element Index="[408]" Value="0" />
<Element Index="[409]" Value="0" />
<Element Index="[410]" Value="0" />
<Element Index="[411]" Value="0" />
<Element Index="[412]" Value="0" />
<Element Index="[413]" Value="0" />
<Element Index="[414]" Value="0" />
<Element Index="[415]" Value="0" />
<Element Index="[416]" Value="0" />
<Element Index="[417]" Value="0" />
<Element Index="[418]" Value="0" />
<Element Index="[419]" Value="0" />
<Element Index="[420]" Value="0" />
<Element Index="[421]" Value="0" />
<Element Index="[422]" Value="0" />
<Element Index="[423]" Value="0" />
<Element Index="[424]" Value="0" />
<Element Index="[425]" Value="0" />
<Element Index="[426]" Value="0" />
<Element Index="[427]" Value="0" />
<Element Index="[428]" Value="0" />
<Element Index="[429]" Value="0" />
<Element Index="[430]" Value="0" />
<Element Index="[431]" Value="0" />
<Element Index="[432]" Value="0" />
<Element Index="[433]" Value="0" />
<Element Index="[434]" Value="0" />
<Element Index="[435]" Value="0" />
<Element Index="[436]" Value="0" />
<Element Index="[437]" Value="0" />
<Element Index="[438]" Value="0" />
<Element Index="[439]" Value="0" />
<Element Index="[440]" Value="0" />
<Element Index="[441]" Value="0" />
<Element Index="[442]" Value="0" />
<Element Index="[443]" Value="0" />
<Element Index="[444]" Value="0" />
<Element Index="[445]" Value="0" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,10,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1
		,1,1,1,1,1,1,1,1,1,1,1,1,1,10,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="_0142:AL1222_7C39EFE1:O:0">
<ArrayMember Name="Data" DataType="SINT" Dimensions="302" Radix="Decimal">
<Element Index="[0]" Value="0" />
<Element Index="[1]" Value="0" />
<Element Index="[2]" Value="0" />
<Element Index="[3]" Value="0" />
<Element Index="[4]" Value="0" />
<Element Index="[5]" Value="0" />
<Element Index="[6]" Value="0" />
<Element Index="[7]" Value="0" />
<Element Index="[8]" Value="0" />
<Element Index="[9]" Value="0" />
<Element Index="[10]" Value="0" />
<Element Index="[11]" Value="0" />
<Element Index="[12]" Value="0" />
<Element Index="[13]" Value="0" />
<Element Index="[14]" Value="0" />
<Element Index="[15]" Value="0" />
<Element Index="[16]" Value="0" />
<Element Index="[17]" Value="0" />
<Element Index="[18]" Value="0" />
<Element Index="[19]" Value="0" />
<Element Index="[20]" Value="0" />
<Element Index="[21]" Value="0" />
<Element Index="[22]" Value="0" />
<Element Index="[23]" Value="0" />
<Element Index="[24]" Value="0" />
<Element Index="[25]" Value="0" />
<Element Index="[26]" Value="0" />
<Element Index="[27]" Value="0" />
<Element Index="[28]" Value="0" />
<Element Index="[29]" Value="0" />
<Element Index="[30]" Value="0" />
<Element Index="[31]" Value="0" />
<Element Index="[32]" Value="0" />
<Element Index="[33]" Value="0" />
<Element Index="[34]" Value="0" />
<Element Index="[35]" Value="0" />
<Element Index="[36]" Value="0" />
<Element Index="[37]" Value="0" />
<Element Index="[38]" Value="0" />
<Element Index="[39]" Value="0" />
<Element Index="[40]" Value="0" />
<Element Index="[41]" Value="0" />
<Element Index="[42]" Value="0" />
<Element Index="[43]" Value="0" />
<Element Index="[44]" Value="0" />
<Element Index="[45]" Value="0" />
<Element Index="[46]" Value="0" />
<Element Index="[47]" Value="0" />
<Element Index="[48]" Value="0" />
<Element Index="[49]" Value="0" />
<Element Index="[50]" Value="0" />
<Element Index="[51]" Value="0" />
<Element Index="[52]" Value="0" />
<Element Index="[53]" Value="0" />
<Element Index="[54]" Value="0" />
<Element Index="[55]" Value="0" />
<Element Index="[56]" Value="0" />
<Element Index="[57]" Value="0" />
<Element Index="[58]" Value="0" />
<Element Index="[59]" Value="0" />
<Element Index="[60]" Value="0" />
<Element Index="[61]" Value="0" />
<Element Index="[62]" Value="0" />
<Element Index="[63]" Value="0" />
<Element Index="[64]" Value="0" />
<Element Index="[65]" Value="0" />
<Element Index="[66]" Value="0" />
<Element Index="[67]" Value="0" />
<Element Index="[68]" Value="0" />
<Element Index="[69]" Value="0" />
<Element Index="[70]" Value="0" />
<Element Index="[71]" Value="0" />
<Element Index="[72]" Value="0" />
<Element Index="[73]" Value="0" />
<Element Index="[74]" Value="0" />
<Element Index="[75]" Value="0" />
<Element Index="[76]" Value="0" />
<Element Index="[77]" Value="0" />
<Element Index="[78]" Value="0" />
<Element Index="[79]" Value="0" />
<Element Index="[80]" Value="0" />
<Element Index="[81]" Value="0" />
<Element Index="[82]" Value="0" />
<Element Index="[83]" Value="0" />
<Element Index="[84]" Value="0" />
<Element Index="[85]" Value="0" />
<Element Index="[86]" Value="0" />
<Element Index="[87]" Value="10" />
<Element Index="[88]" Value="0" />
<Element Index="[89]" Value="0" />
<Element Index="[90]" Value="0" />
<Element Index="[91]" Value="0" />
<Element Index="[92]" Value="0" />
<Element Index="[93]" Value="0" />
<Element Index="[94]" Value="0" />
<Element Index="[95]" Value="0" />
<Element Index="[96]" Value="0" />
<Element Index="[97]" Value="0" />
<Element Index="[98]" Value="0" />
<Element Index="[99]" Value="0" />
<Element Index="[100]" Value="0" />
<Element Index="[101]" Value="0" />
<Element Index="[102]" Value="0" />
<Element Index="[103]" Value="0" />
<Element Index="[104]" Value="0" />
<Element Index="[105]" Value="0" />
<Element Index="[106]" Value="0" />
<Element Index="[107]" Value="0" />
<Element Index="[108]" Value="0" />
<Element Index="[109]" Value="0" />
<Element Index="[110]" Value="0" />
<Element Index="[111]" Value="0" />
<Element Index="[112]" Value="0" />
<Element Index="[113]" Value="0" />
<Element Index="[114]" Value="0" />
<Element Index="[115]" Value="0" />
<Element Index="[116]" Value="0" />
<Element Index="[117]" Value="0" />
<Element Index="[118]" Value="0" />
<Element Index="[119]" Value="1" />
<Element Index="[120]" Value="1" />
<Element Index="[121]" Value="1" />
<Element Index="[122]" Value="1" />
<Element Index="[123]" Value="1" />
<Element Index="[124]" Value="1" />
<Element Index="[125]" Value="1" />
<Element Index="[126]" Value="1" />
<Element Index="[127]" Value="1" />
<Element Index="[128]" Value="1" />
<Element Index="[129]" Value="1" />
<Element Index="[130]" Value="1" />
<Element Index="[131]" Value="1" />
<Element Index="[132]" Value="1" />
<Element Index="[133]" Value="1" />
<Element Index="[134]" Value="1" />
<Element Index="[135]" Value="1" />
<Element Index="[136]" Value="1" />
<Element Index="[137]" Value="1" />
<Element Index="[138]" Value="1" />
<Element Index="[139]" Value="1" />
<Element Index="[140]" Value="1" />
<Element Index="[141]" Value="1" />
<Element Index="[142]" Value="1" />
<Element Index="[143]" Value="1" />
<Element Index="[144]" Value="1" />
<Element Index="[145]" Value="1" />
<Element Index="[146]" Value="1" />
<Element Index="[147]" Value="1" />
<Element Index="[148]" Value="1" />
<Element Index="[149]" Value="1" />
<Element Index="[150]" Value="1" />
<Element Index="[151]" Value="1" />
<Element Index="[152]" Value="1" />
<Element Index="[153]" Value="1" />
<Element Index="[154]" Value="1" />
<Element Index="[155]" Value="1" />
<Element Index="[156]" Value="1" />
<Element Index="[157]" Value="1" />
<Element Index="[158]" Value="1" />
<Element Index="[159]" Value="1" />
<Element Index="[160]" Value="1" />
<Element Index="[161]" Value="1" />
<Element Index="[162]" Value="1" />
<Element Index="[163]" Value="1" />
<Element Index="[164]" Value="1" />
<Element Index="[165]" Value="1" />
<Element Index="[166]" Value="1" />
<Element Index="[167]" Value="1" />
<Element Index="[168]" Value="1" />
<Element Index="[169]" Value="1" />
<Element Index="[170]" Value="1" />
<Element Index="[171]" Value="1" />
<Element Index="[172]" Value="1" />
<Element Index="[173]" Value="1" />
<Element Index="[174]" Value="10" />
<Element Index="[175]" Value="0" />
<Element Index="[176]" Value="0" />
<Element Index="[177]" Value="0" />
<Element Index="[178]" Value="0" />
<Element Index="[179]" Value="0" />
<Element Index="[180]" Value="0" />
<Element Index="[181]" Value="0" />
<Element Index="[182]" Value="0" />
<Element Index="[183]" Value="0" />
<Element Index="[184]" Value="0" />
<Element Index="[185]" Value="0" />
<Element Index="[186]" Value="0" />
<Element Index="[187]" Value="0" />
<Element Index="[188]" Value="0" />
<Element Index="[189]" Value="0" />
<Element Index="[190]" Value="0" />
<Element Index="[191]" Value="0" />
<Element Index="[192]" Value="0" />
<Element Index="[193]" Value="0" />
<Element Index="[194]" Value="0" />
<Element Index="[195]" Value="0" />
<Element Index="[196]" Value="0" />
<Element Index="[197]" Value="0" />
<Element Index="[198]" Value="0" />
<Element Index="[199]" Value="0" />
<Element Index="[200]" Value="0" />
<Element Index="[201]" Value="0" />
<Element Index="[202]" Value="0" />
<Element Index="[203]" Value="0" />
<Element Index="[204]" Value="0" />
<Element Index="[205]" Value="0" />
<Element Index="[206]" Value="0" />
<Element Index="[207]" Value="0" />
<Element Index="[208]" Value="0" />
<Element Index="[209]" Value="0" />
<Element Index="[210]" Value="0" />
<Element Index="[211]" Value="0" />
<Element Index="[212]" Value="0" />
<Element Index="[213]" Value="0" />
<Element Index="[214]" Value="0" />
<Element Index="[215]" Value="0" />
<Element Index="[216]" Value="0" />
<Element Index="[217]" Value="0" />
<Element Index="[218]" Value="0" />
<Element Index="[219]" Value="0" />
<Element Index="[220]" Value="0" />
<Element Index="[221]" Value="0" />
<Element Index="[222]" Value="0" />
<Element Index="[223]" Value="0" />
<Element Index="[224]" Value="0" />
<Element Index="[225]" Value="0" />
<Element Index="[226]" Value="0" />
<Element Index="[227]" Value="0" />
<Element Index="[228]" Value="0" />
<Element Index="[229]" Value="0" />
<Element Index="[230]" Value="0" />
<Element Index="[231]" Value="0" />
<Element Index="[232]" Value="0" />
<Element Index="[233]" Value="0" />
<Element Index="[234]" Value="0" />
<Element Index="[235]" Value="0" />
<Element Index="[236]" Value="0" />
<Element Index="[237]" Value="0" />
<Element Index="[238]" Value="0" />
<Element Index="[239]" Value="0" />
<Element Index="[240]" Value="0" />
<Element Index="[241]" Value="0" />
<Element Index="[242]" Value="0" />
<Element Index="[243]" Value="0" />
<Element Index="[244]" Value="0" />
<Element Index="[245]" Value="0" />
<Element Index="[246]" Value="0" />
<Element Index="[247]" Value="0" />
<Element Index="[248]" Value="0" />
<Element Index="[249]" Value="0" />
<Element Index="[250]" Value="0" />
<Element Index="[251]" Value="0" />
<Element Index="[252]" Value="0" />
<Element Index="[253]" Value="0" />
<Element Index="[254]" Value="0" />
<Element Index="[255]" Value="0" />
<Element Index="[256]" Value="0" />
<Element Index="[257]" Value="0" />
<Element Index="[258]" Value="0" />
<Element Index="[259]" Value="0" />
<Element Index="[260]" Value="0" />
<Element Index="[261]" Value="0" />
<Element Index="[262]" Value="0" />
<Element Index="[263]" Value="0" />
<Element Index="[264]" Value="0" />
<Element Index="[265]" Value="0" />
<Element Index="[266]" Value="0" />
<Element Index="[267]" Value="0" />
<Element Index="[268]" Value="0" />
<Element Index="[269]" Value="0" />
<Element Index="[270]" Value="0" />
<Element Index="[271]" Value="0" />
<Element Index="[272]" Value="0" />
<Element Index="[273]" Value="0" />
<Element Index="[274]" Value="0" />
<Element Index="[275]" Value="0" />
<Element Index="[276]" Value="0" />
<Element Index="[277]" Value="0" />
<Element Index="[278]" Value="0" />
<Element Index="[279]" Value="0" />
<Element Index="[280]" Value="0" />
<Element Index="[281]" Value="0" />
<Element Index="[282]" Value="0" />
<Element Index="[283]" Value="0" />
<Element Index="[284]" Value="0" />
<Element Index="[285]" Value="0" />
<Element Index="[286]" Value="0" />
<Element Index="[287]" Value="0" />
<Element Index="[288]" Value="0" />
<Element Index="[289]" Value="0" />
<Element Index="[290]" Value="0" />
<Element Index="[291]" Value="0" />
<Element Index="[292]" Value="0" />
<Element Index="[293]" Value="0" />
<Element Index="[294]" Value="0" />
<Element Index="[295]" Value="0" />
<Element Index="[296]" Value="0" />
<Element Index="[297]" Value="0" />
<Element Index="[298]" Value="0" />
<Element Index="[299]" Value="0" />
<Element Index="[300]" Value="0" />
<Element Index="[301]" Value="0" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'L5X_Samples/IPC_EdgerLine_20251217r1.L5X', 1),
    'DSI-DRIVE-PERIPHERAL-MODULE': ("""\
<Module Name="TestMod1_DSIDRIVEPERIPHERALMO" CatalogNumber="PowerFlex 525-EENET" Vendor="1" ProductType="150" ProductCode="9" Major="3" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false" DrivesADCMode="true" DrivesADCEnabled="false" SafetyEnabled="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="0" Type="DSI" Upstream="false">
<Bus />
</Port>
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications CommMethod="536870913">
<ConfigData ConfigSize="58">
<Data Format="L5K">
[62,0,6,0,1,0,200,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
</Data>
</ConfigData>
<ConfigScript Size="8056">
<Data Format="L5K">
[116,31,0,0,4,0,0,0,0,0,0,0,0,0,0,0,25,0,0,0,8,-106,0,0,0,1,0,0,0,1,0,0,0,8,0,0,0,75,2,32,-110,36,0,-1,-1,0,0,0,-63,30,0,0,8,30,0,0,0,1,0,0,0,1
		,0,0,0,9,0,0,0,16,3,32,-109,36,0,48,2,3,1,0,0,0,10,0,0,0,16,3,32,-109,36,30,48,9,1,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,31,48,9,-52,1,1,0
		,0,0,10,0,0,0,16,3,32,-109,36,32,48,9,60,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,33,48,9,65,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,34,48,9,65
		,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,35,48,9,4,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,36,48,9,-37,6,1,0,0,0,10,0,0,0,16,3,32,-109,36,37,48
		,9,118,1,1,0,0,0,10,0,0,0,16,3,32,-109,36,39,48,9,1,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,41,48,9,50,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,42
		,48,9,50,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,43,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,44,48,9,76,29,1,0,0,0,10,0,0,0,16,3,32,-109,36
		,45,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,46,48,9,5,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,47,48,9,15,0,1,0,0,0,10,0,0,0,16,3,32,-109,36
		,48,48,9,2,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,49,48,9,5,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,50,48,9,1,0,1,0,0,0,10,0,0,0,16,3,32,-109,36
		,51,48,9,2,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,52,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,62,48,9,48,0,1,0,0,0,10,0,0,0,16,3,32,-109,36
		,63,48,9,50,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,64,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,65,48,9,7,0,1,0,0,0,10,0,0,0,16,3,32,-109,36
		,66,48,9,7,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,67,48,9,5,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,68,48,9,9,0,1,0,0,0,10,0,0,0,16,3,32,-109,36
		,69,48,9,2,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,70,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,71,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36
		,72,48,9,1,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,73,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,74,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36
		,75,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,76,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,77,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36
		,78,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,79,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,80,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36
		,81,48,9,2,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,82,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,83,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36
		,84,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,85,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,86,48,9,-56,0,1,0,0,0,10,0,0,0,16,3,32,-109
		,36,87,48,9,-56,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,88,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,89,48,9,100,0,1,0,0,0,10,0,0,0,16,3,32
		,-109,36,91,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,92,48,9,-24,3,1,0,0,0,10,0,0,0,16,3,32,-109,36,93,48,9,0,0,1,0,0,0,10,0,0,0,16,3
		,32,-109,36,94,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,95,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,96,48,9,-24,3,1,0,0,0,10,0,0,0,16
		,3,32,-109,36,97,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,98,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,99,48,9,0,0,1,0,0,0,10,0,0,0,16
		,3,32,-109,36,100,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,101,48,9,100,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,102,48,9,0,0,1,0,0,0,10
		,0,0,0,16,3,32,-109,36,103,48,9,-106,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,104,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,105,48,9,0,0
		,1,0,0,0,10,0,0,0,16,3,32,-109,36,121,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,122,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,123,48
		,9,3,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,124,48,9,100,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,125,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36
		,126,48,9,50,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,127,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-128,48,9,1,0,1,0,0,0,10,0,0,0,16,3,32,-109
		,36,-127,48,9,-64,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-126,48,9,-88,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-125,48,9,60,0,1,0,0,0,10,0
		,0,0,16,3,32,-109,36,-124,48,9,73,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-123,48,9,-1,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-122,48,9,-1
		,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-121,48,9,-1,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-120,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-119
		,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-118,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-117,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109
		,36,-116,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-115,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-113,48,9,0,0,1,0,0,0,10,0,0,0,16,3
		,32,-109,36,-112,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-111,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-110,48,9,0,0,1,0,0,0,10
		,0,0,0,16,3,32,-109,36,-109,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-108,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-107,48,9,0,0
		,1,0,0,0,10,0,0,0,16,3,32,-109,36,-106,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-103,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-102
		,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-101,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-100,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109
		,36,-99,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-98,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-97,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109
		,36,-96,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-95,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-94,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109
		,36,-93,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-92,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-91,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109
		,36,-90,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-89,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-88,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109
		,36,-87,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-85,48,9,2,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-84,48,9,3,0,1,0,0,0,10,0,0,0,16,3,32,-109
		,36,-83,48,9,4,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-82,48,9,5,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-81,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109
		,36,-76,48,9,-15,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-75,48,9,-15,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-74,48,9,-15,0,1,0,0,0,10,0,0,0
		,16,3,32,-109,36,-73,48,9,-15,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-72,48,9,-15,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-71,48,9,-15,0
		,1,0,0,0,10,0,0,0,16,3,32,-109,36,-70,48,9,-15,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-69,48,9,-15,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-66
		,48,9,44,1,1,0,0,0,10,0,0,0,16,3,32,-109,36,-65,48,9,44,1,1,0,0,0,10,0,0,0,16,3,32,-109,36,-64,48,9,44,1,1,0,0,0,10,0,0,0,16,3,32,-109
		,36,-63,48,9,44,1,1,0,0,0,10,0,0,0,16,3,32,-109,36,-62,48,9,44,1,1,0,0,0,10,0,0,0,16,3,32,-109,36,-61,48,9,44,1,1,0,0,0,10,0,0,0,16,3
		,32,-109,36,-60,48,9,44,1,1,0,0,0,10,0,0,0,16,3,32,-109,36,-59,48,9,44,1,1,0,0,0,10,0,0,0,16,3,32,-109,36,-56,48,9,0,0,1,0,0,0,10,0
		,0,0,16,3,32,-109,36,-55,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-54,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-53,48,9,0,0,1,0,0,0
		,10,0,0,0,16,3,32,-109,36,-52,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-51,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-50,48,9,0,0,1
		,0,0,0,10,0,0,0,16,3,32,-109,36,-49,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-48,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-47,48,9
		,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-46,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-45,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-44
		,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-43,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-42,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36
		,-41,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-102,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-101,1,48,9,-12,1,1,0,0,0,12,0,0,0
		,16,4,32,-109,37,0,-100,1,48,9,-24,3,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-99,1,48,9,-48,7,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-98,1
		,48,9,-72,11,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-97,1,48,9,-96,15,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-96,1,48,9,-120,19,1,0,0,0,12
		,0,0,0,16,4,32,-109,37,0,-95,1,48,9,112,23,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-94,1,48,9,112,23,1,0,0,0,12,0,0,0,16,4,32,-109,37,0
		,-93,1,48,9,112,23,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-92,1,48,9,112,23,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-91,1,48,9,112,23,1,0,0
		,0,12,0,0,0,16,4,32,-109,37,0,-90,1,48,9,112,23,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-89,1,48,9,112,23,1,0,0,0,12,0,0,0,16,4,32,-109
		,37,0,-88,1,48,9,112,23,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-87,1,48,9,112,23,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-86,1,48,9,112,23
		,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-85,1,48,9,112,23,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-84,1,48,9,1,0,1,0,0,0,12,0,0,0,16,4,32,-109
		,37,0,-83,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-82,1,48,9,100,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-81,1,48,9,-24,3,1,0,0,0,12
		,0,0,0,16,4,32,-109,37,0,-80,1,48,9,-24,3,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-79,1,48,9,-24,3,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-78
		,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-77,1,48,9,5,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-76,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109
		,37,0,-75,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-74,1,48,9,-24,3,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-73,1,48,9,0,0,1,0,0,0,12,0
		,0,0,16,4,32,-109,37,0,-72,1,48,9,30,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-71,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-70,1,48
		,9,-24,3,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-69,1,48,9,-24,3,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-68,1,48,9,-24,3,1,0,0,0,12,0,0,0,16,4
		,32,-109,37,0,-67,1,48,9,-24,3,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-66,1,48,9,-24,3,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-65,1,48,9,-24
		,3,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-64,1,48,9,50,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-63,1,48,9,30,0,1,0,0,0,12,0,0,0,16,4,32,-109
		,37,0,-62,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-61,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-60,1,48,9,0,0,1,0,0,0,12,0,0,0
		,16,4,32,-109,37,0,-59,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-58,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-57,1,48,9,0,0
		,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-56,1,48,9,88,2,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-55,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37
		,0,-54,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-53,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-52,1,48,9,0,0,1,0,0,0,12,0,0,0,16
		,4,32,-109,37,0,-51,1,48,9,1,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-50,1,48,9,20,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-49,1,48,9,0,0,1
		,0,0,0,12,0,0,0,16,4,32,-109,37,0,-48,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-47,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-46
		,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-45,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-44,1,48,9,88,2,1,0,0,0,12,0,0,0,16,4,32
		,-109,37,0,-43,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-42,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-41,1,48,9,0,0,1,0,0,0,12
		,0,0,0,16,4,32,-109,37,0,-40,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-39,1,48,9,1,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-38,1,48
		,9,20,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-37,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-36,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109
		,37,0,-35,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-34,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-33,1,48,9,0,0,1,0,0,0,12,0,0,0
		,16,4,32,-109,37,0,-31,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-30,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-29,1,48,9,0,4
		,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-28,1,48,9,-98,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-27,1,48,9,116,0,1,0,0,0,12,0,0,0,16,4,32,-109
		,37,0,-26,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-25,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-24,1,48,9,0,0,1,0,0,0,12,0,0,0
		,16,4,32,-109,37,0,-23,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-22,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-21,1,48,9,0,0
		,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-20,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-19,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0
		,-18,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-17,1,48,9,3,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-16,1,48,9,51,0,1,0,0,0,12,0,0,0,16
		,4,32,-109,37,0,-15,1,48,9,0,1,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-14,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-13,1,48,9,0,0,1,0
		,0,0,12,0,0,0,16,4,32,-109,37,0,-12,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-3,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-2,1
		,48,9,65,3,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-1,1,48,9,10,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,0,2,48,9,-36,5,1,0,0,0,12,0,0,0,16,4,32,-109
		,37,0,1,2,48,9,10,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,2,2,48,9,-48,7,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,3,2,48,9,10,0,1,0,0,0,12,0,0,0,16
		,4,32,-109,37,0,9,2,48,9,-24,3,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,10,2,48,9,100,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,11,2,48,9,-24,3
		,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,12,2,48,9,100,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,13,2,48,9,-24,3,1,0,0,0,12,0,0,0,16,4,32,-109,37
		,0,14,2,48,9,100,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,18,2,48,9,7,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,19,2,48,9,25,0,1,0,0,0,12,0,0,0,16
		,4,32,-109,37,0,20,2,48,9,-6,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,21,2,48,9,-106,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,22,2,48,9,-52
		,1,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,23,2,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,24,2,48,9,0,4,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,25
		,2,48,9,64,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,26,2,48,9,20,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,27,2,48,9,5,0,1,0,0,0,12,0,0,0,16,4,32,-109
		,37,0,28,2,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,29,2,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,30,2,48,9,10,0,1,0,0,0,12,0,0,0,16
		,4,32,-109,37,0,31,2,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,32,2,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,33,2,48,9,0,0,1,0,0,0,12
		,0,0,0,16,4,32,-109,37,0,34,2,48,9,65,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,35,2,48,9,1,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,36,2,48,9,0
		,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,37,2,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,38,2,48,9,1,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,40
		,2,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,41,2,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,42,2,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109
		,37,0,44,2,48,9,2,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,45,2,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,46,2,48,9,0,0,1,0,0,0,12,0,0,0,16,4
		,32,-109,37,0,47,2,48,9,0,16,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,48,2,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,49,2,48,9,0,0,1,0,0,0,12
		,0,0,0,16,4,32,-109,37,0,50,2,48,9,100,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,51,2,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,52,2,48,9
		,100,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,53,2,48,9,8,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,54,2,48,9,30,0,1,0,0,0,12,0,0,0,16,4,32,-109
		,37,0,55,2,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,56,2,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,57,2,48,9,0,0,1,0,0,0,12,0,0,0,16,4
		,32,-109,37,0,58,2,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,59,2,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,60,2,48,9,100,0,1,0,0,0
		,12,0,0,0,16,4,32,-109,37,0,61,2,48,9,3,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,62,2,48,9,0,0,1,0,0,0,37,0,0,0,16,3,32,-99,36,1,48,1,-127
		,0,99,42,0,17,1,1,0,1,0,16,0,67,117,115,116,111,109,32,71,114,111,117,112,32,32,32,32,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1
		,48,7,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,8,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,9,0,0,0,0,1,0,0,0,14,0,0,0,16,4
		,32,-108,37,0,17,1,48,10,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,11,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,12,0
		,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,13,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,14,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32
		,-108,37,0,17,1,48,15,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,16,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,17,0,0,0
		,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,18,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,19,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108
		,37,0,17,1,48,20,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,21,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,22,0,0,0,0,1,0,0
		,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,23,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,24,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37
		,0,17,1,48,25,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,26,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,27,0,0,0,0,1,0,0,0,14
		,0,0,0,16,4,32,-108,37,0,17,1,48,28,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,29,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17
		,1,48,30,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,31,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,32,0,0,0,0,1,0,0,0,14,0,0
		,0,16,4,32,-108,37,0,17,1,48,33,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,34,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48
		,35,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,36,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,37,0,0,0,0,1,0,0,0,14,0,0,0,16
		,4,32,-108,37,0,17,1,48,38,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,39,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,40
		,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,41,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,42,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32
		,-108,37,0,17,1,48,43,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,44,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,45,0,0,0
		,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,46,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,47,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108
		,37,0,17,1,48,48,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,49,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,50,0,0,0,0,1,0,0
		,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,51,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,52,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37
		,0,17,1,48,53,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,54,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,55,0,0,0,0,1,0,0,0,14
		,0,0,0,16,4,32,-108,37,0,17,1,48,56,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,57,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17
		,1,48,58,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,59,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,60,0,0,0,0,1,0,0,0,14,0,0
		,0,16,4,32,-108,37,0,17,1,48,61,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,62,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48
		,63,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,64,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,65,0,0,0,0,1,0,0,0,14,0,0,0,16
		,4,32,-108,37,0,17,1,48,66,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,67,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,68
		,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,69,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,70,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32
		,-108,37,0,17,1,48,71,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,72,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,73,0,0,0
		,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,74,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,75,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108
		,37,0,17,1,48,76,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,77,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,78,0,0,0,0,1,0,0
		,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,79,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,80,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37
		,0,17,1,48,81,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,82,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,83,0,0,0,0,1,0,0,0,14
		,0,0,0,16,4,32,-108,37,0,17,1,48,84,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,85,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17
		,1,48,86,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,87,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,88,0,0,0,0,1,0,0,0,14,0,0
		,0,16,4,32,-108,37,0,17,1,48,89,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,90,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48
		,91,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,92,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,93,0,0,0,0,1,0,0,0,14,0,0,0,16
		,4,32,-108,37,0,17,1,48,94,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,95,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,96
		,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,97,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,98,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32
		,-108,37,0,17,1,48,99,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,100,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,101,0
		,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,102,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,103,0,0,0,0,1,0,0,0,14,0,0,0,16,4
		,32,-108,37,0,17,1,48,104,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,105,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,17,1,48,106
		,0,0,0,0,1,0,0,0,28,0,0,0,16,3,32,-110,36,0,48,31,1,0,16,0,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,0,0,0,45,0,0,0,8,100,0,0,0
		,1,0,0,0,6,0,0,0,24,0,0,0,16,3,32,-110,36,0,48,38,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,64,0,0,0,0,0,0,34,0,0,0,8,61,0,0,0,1,0,0,0,1,0,0,0,9,0,0,0,16,3,32
		,-105,36,0,48,3,3,3,0,0,0,-120,19,0,0,0,0,29,0,0,0,0,100,0,0,0,2,0,0,0,-128,0,0,0,-19,95,-107,106,86,4,-21,17,-65,-27,-44,59,4,-36
		,-68,-105,0,0,0]
</Data>
</ConfigScript>
<Connections>
<Connection Name="Standard" RPI="70000" Type="Output" InputCxnPoint="1" OutputCxnPoint="2" OutputSize="4" InputSize="8" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:PowerFlex525V_EENET_Drive:I:0">
<DataValueMember Name="DriveStatus" DataType="INT" Radix="Binary" Value="2#0000_0110_0010_1111" />
<DataValueMember Name="Ready" DataType="BOOL" Value="1" />
<DataValueMember Name="Active" DataType="BOOL" Value="1" />
<DataValueMember Name="CommandDir" DataType="BOOL" Value="1" />
<DataValueMember Name="ActualDir" DataType="BOOL" Value="1" />
<DataValueMember Name="Accelerating" DataType="BOOL" Value="0" />
<DataValueMember Name="Decelerating" DataType="BOOL" Value="1" />
<DataValueMember Name="Faulted" DataType="BOOL" Value="0" />
<DataValueMember Name="AtReference" DataType="BOOL" Value="0" />
<DataValueMember Name="CommFreqCnt" DataType="BOOL" Value="1" />
<DataValueMember Name="CommLogicCnt" DataType="BOOL" Value="1" />
<DataValueMember Name="ParmsLocked" DataType="BOOL" Value="0" />
<DataValueMember Name="DigIn1Active" DataType="BOOL" Value="0" />
<DataValueMember Name="DigIn2Active" DataType="BOOL" Value="0" />
<DataValueMember Name="DigIn3Active" DataType="BOOL" Value="0" />
<DataValueMember Name="DigIn4Active" DataType="BOOL" Value="0" />
<DataValueMember Name="OutputFreq" DataType="INT" Radix="Decimal" Value="6577" />
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[18,5441]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:PowerFlex525V_EENET_Drive:O:0">
<DataValueMember Name="LogicCommand" DataType="INT" Radix="Binary" Value="2#0000_0000_0001_0010" />
<DataValueMember Name="Stop" DataType="BOOL" Value="0" />
<DataValueMember Name="Start" DataType="BOOL" Value="1" />
<DataValueMember Name="Jog" DataType="BOOL" Value="0" />
<DataValueMember Name="ClearFaults" DataType="BOOL" Value="0" />
<DataValueMember Name="Forward" DataType="BOOL" Value="1" />
<DataValueMember Name="Reverse" DataType="BOOL" Value="0" />
<DataValueMember Name="ForceKeypadCtrl" DataType="BOOL" Value="0" />
<DataValueMember Name="MOPIncrement" DataType="BOOL" Value="0" />
<DataValueMember Name="AccelRate1" DataType="BOOL" Value="0" />
<DataValueMember Name="AccelRate2" DataType="BOOL" Value="0" />
<DataValueMember Name="DecelRate1" DataType="BOOL" Value="0" />
<DataValueMember Name="DecelRate2" DataType="BOOL" Value="0" />
<DataValueMember Name="FreqSel01" DataType="BOOL" Value="0" />
<DataValueMember Name="FreqSel02" DataType="BOOL" Value="0" />
<DataValueMember Name="FreqSel03" DataType="BOOL" Value="0" />
<DataValueMember Name="MOPDecrement" DataType="BOOL" Value="0" />
<DataValueMember Name="FreqCommand" DataType="INT" Radix="Decimal" Value="5441" />
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module CatalogNumber="DSI-DRIVE-PERIPHERAL-MODULE" Vendor="1" ProductType="0" ProductCode="29" Major="1" Minor="1" UserDefinedVendor="1" UserDefinedProductType="150" UserDefinedProductCode="33279" UserDefinedMajor="3" UserDefinedMinor="1" ParentModule="TestMod1_DSIDRIVEPERIPHERALMO" ParentModPortId="1" Inhibited="false" MajorFault="false" ShutdownParentOnFault="false" DrivesADCMode="true" DrivesADCEnabled="false" UserDefinedCatalogNumber="22-HIM-A3 SER C">
<EKey State="Disabled" />
<Ports>
<Port Id="2" Address="1" Type="DSI" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="4">
<Data Format="L5K">
[8,6,1]
</Data>
</ConfigData>
<ConfigScript Size="568">
<Data Format="L5K">
[52,2,0,0,4,0,0,0,0,0,0,0,0,0,0,0,25,0,0,0,8,-106,0,0,0,1,0,0,0,1,0,0,0,8,0,0,0,75,2,32,-110,36,0,-1,-1,0,0,0,-126,1,0,0,8,30,0,0,0,1,0,0,0,1,0,0
		,0,9,0,0,0,16,3,32,-109,36,0,48,2,3,1,0,0,0,10,0,0,0,16,3,32,-109,36,1,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,2,48,9,1,0,1,0,0,0,10,0,0
		,0,16,3,32,-109,36,4,48,9,3,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,5,48,9,5,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,6,48,9,1,0,1,0,0,0,10,0,0,0,16
		,3,32,-109,36,7,48,9,50,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,8,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,9,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32
		,-109,36,11,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,12,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,13,48,9,88,2,1,0,0,0,10,0,0,0,16,3,32
		,-109,36,14,48,9,1,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,15,48,9,72,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,16,48,9,72,0,1,0,0,0,10,0,0,0,16,3
		,32,-109,36,17,48,9,122,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,18,48,9,32,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,19,48,9,32,0,1,0,0,0,10,0,0
		,0,16,3,32,-109,36,20,48,9,32,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,21,48,9,32,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,22,48,9,32,0,0,0,45,0
		,0,0,8,100,0,0,0,1,0,0,0,6,0,0,0,24,0,0,0,16,3,32,-110,36,0,48,38,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,64,0,0,0,0,0,0,34,0,0,0,8,61,0,0,0,1,0,0,0,1,0,0,0
		,9,0,0,0,16,3,32,-105,36,0,48,3,3,3,0,0,0,-120,19,0,0,0,0,29,0,0,0,0,100,0,0,0,2,0,0,0,-128,0,0,0,-18,95,-107,106,86,4,-21,17,-65,-27
		,-44,59,4,-36,-68,-105,0,0,0]
</Data>
</ConfigScript>
<Connections />
</Communications>
</Module>
""", 'L5X_Samples/Sorter1_20260722r00.L5X', 2),
    'EX260-SEN1/A': ("""\
<Module Name="TestMod1_EX260SEN1A" CatalogNumber="EX260-SEN1/A" Vendor="7" ProductType="27" ProductCode="156" Major="2" Minor="3" ParentModule="Local" ParentModPortId="4" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="0">
<Data Format="L5K">
[4,105]
</Data>
</ConfigData>
<Connections>
<Connection Name="Output" RPI="20000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="SM:EX260_SEN1:I:0">
<DataValueMember Name="InputArea" DataType="INT" Radix="Binary" Value="2#0000_1000_0000_0000" />
<DataValueMember Name="SOLV_Status" DataType="BOOL" Value="1" />
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[[0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="SM:EX260_SEN1:O:0">
<ArrayMember Name="OutputArea" DataType="INT" Dimensions="2" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000_0000_0000" />
<Element Index="[1]" Value="2#0000_0000_0000_0000" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'DnR_Personal/Fisher_Synergy_Bead_20240725.L5X', 1),
    'EX260-SEN3/A': ("""\
<Module Name="TestMod1_EX260SEN3A" CatalogNumber="EX260-SEN3/A" Vendor="7" ProductType="27" ProductCode="158" Major="2" Minor="3" ParentModule="Local" ParentModPortId="4" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="0">
<Data Format="L5K">
[4,105]
</Data>
</ConfigData>
<Connections>
<Connection Name="Output" RPI="10000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="SM:EX260_SEN3:I:0">
<DataValueMember Name="InputArea" DataType="INT" Radix="Binary" Value="2#1111_1111_1111_1111" />
<DataValueMember Name="SOLV_Status" DataType="BOOL" Value="1" />
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[153]
</Data>
<Data Format="Decorated">
<Structure DataType="SM:EX260_SEN3:O:0">
<DataValueMember Name="OutputArea" DataType="INT" Radix="Binary" Value="2#0000_0000_1001_1001" />
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'DnR_Personal/Fisher_P800Sub_20240531.L5X', 1),
    'FANUC Robot R30iB Plus/A': ("""\
<Module Name="TestMod1_FANUCRobotR30iBPlusA" CatalogNumber="FANUC Robot R30iB Plus/A" Vendor="356" ProductType="12" ProductCode="4" Major="3" Minor="1" UserDefinedVendor="356" UserDefinedProductType="140" UserDefinedProductCode="40" UserDefinedMajor="3" UserDefinedMinor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false" SafetyNetwork="16#0000_44c9_02ec_6f66" SafetyEnabled="true">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="0">
<Data Format="L5K">
[4,100]
</Data>
</ConfigData>
<SafetyScript Size="57">
<Data Format="L5K">
[53,0,0,0,5,0,0,0,0,0,0,0,0,0,0,0,37,0,0,0,0,0,0,0,0,3,0,0,0,23,0,0,0,0,0,0,16,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
</Data>
</SafetyScript>
<Connections>
<Connection Name="A_Safety_Output" RPI="20000" Type="SafetyOutputDataDriven" OutputSize="8" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="60" MaxObservedNetworkDelay="0" Priority="High" InputConnectionType="Unicast" InputProductionTrigger="Application" ConnectionPath="20 04 25 00 00 04 20 04 25 00 88 03 20 04 25 00 00 04" OutputTagSuffix="SO">
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[[12,0,0,0,65,0,0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="FR:Safety_RobotPlus_8Bytes:SO:0">
<ArrayMember Name="Output" DataType="SINT" Dimensions="8" Radix="Hex">
<Element Index="[0]" Value="16#0c" />
<Element Index="[1]" Value="16#00" />
<Element Index="[2]" Value="16#00" />
<Element Index="[3]" Value="16#00" />
<Element Index="[4]" Value="16#41" />
<Element Index="[5]" Value="16#00" />
<Element Index="[6]" Value="16#00" />
<Element Index="[7]" Value="16#00" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
<Connection Name="B_Safety_Input" RPI="10000" Type="SafetyInputDataDriven" InputSize="12" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="40.064" MaxObservedNetworkDelay="0" Priority="High" InputConnectionType="Unicast" InputProductionTrigger="Application" ConnectionPath="20 04 25 00 00 04 20 04 25 00 00 04 20 04 25 00 08 03" InputTagSuffix="SI">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="FR:Safety_RobotPlus_8Bytes:SI:0">
<DataValueMember Name="RunMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="1" />
<ArrayMember Name="Input" DataType="SINT" Dimensions="8" Radix="Hex">
<Element Index="[0]" Value="16#00" />
<Element Index="[1]" Value="16#00" />
<Element Index="[2]" Value="16#00" />
<Element Index="[3]" Value="16#00" />
<Element Index="[4]" Value="16#00" />
<Element Index="[5]" Value="16#00" />
<Element Index="[6]" Value="16#00" />
<Element Index="[7]" Value="16#00" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
</Connection>
<Connection Name="Standard_Slot_01" RPI="32000" Type="StandardDataDriven" OutputSize="16" InputSize="16" EventID="0" ProgrammaticallySendEventTrigger="false" Priority="Scheduled" InputConnectionType="Unicast" InputProductionTrigger="Cyclic" ConnectionPath="20 04 24 64 2c 97 2c 65" InputTagSuffix="I1" OutputTagSuffix="O1">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="FR:Standard_RobotPlus_16Bytes:I1:0">
<ArrayMember Name="Input" DataType="SINT" Dimensions="16" Radix="Hex">
<Element Index="[0]" Value="16#70" />
<Element Index="[1]" Value="16#04" />
<Element Index="[2]" Value="16#00" />
<Element Index="[3]" Value="16#04" />
<Element Index="[4]" Value="16#ff" />
<Element Index="[5]" Value="16#00" />
<Element Index="[6]" Value="16#00" />
<Element Index="[7]" Value="16#00" />
<Element Index="[8]" Value="16#00" />
<Element Index="[9]" Value="16#02" />
<Element Index="[10]" Value="16#00" />
<Element Index="[11]" Value="16#e0" />
<Element Index="[12]" Value="16#1f" />
<Element Index="[13]" Value="16#00" />
<Element Index="[14]" Value="16#00" />
<Element Index="[15]" Value="16#80" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[[0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,-64]]
</Data>
<Data Format="Decorated">
<Structure DataType="FR:Standard_RobotPlus_16Bytes:O1:0">
<ArrayMember Name="Output" DataType="SINT" Dimensions="16" Radix="Hex">
<Element Index="[0]" Value="16#00" />
<Element Index="[1]" Value="16#00" />
<Element Index="[2]" Value="16#00" />
<Element Index="[3]" Value="16#00" />
<Element Index="[4]" Value="16#00" />
<Element Index="[5]" Value="16#00" />
<Element Index="[6]" Value="16#00" />
<Element Index="[7]" Value="16#00" />
<Element Index="[8]" Value="16#00" />
<Element Index="[9]" Value="16#02" />
<Element Index="[10]" Value="16#00" />
<Element Index="[11]" Value="16#00" />
<Element Index="[12]" Value="16#00" />
<Element Index="[13]" Value="16#00" />
<Element Index="[14]" Value="16#00" />
<Element Index="[15]" Value="16#c0" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'DnR_Personal/Bender134053_201104.L5X', 1),
    'PowerFlex 525-EENET': ("""\
<Module Name="TestMod1_PowerFlex525EENET" CatalogNumber="PowerFlex 525-EENET" Vendor="1" ProductType="150" ProductCode="9" Major="7" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false" DrivesADCMode="true" DrivesADCEnabled="true" SafetyEnabled="false" AutoDiagsEnabled="true">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="0" Type="DSI" Upstream="false">
<Bus />
</Port>
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications CommMethod="536870913">
<ConfigData ConfigSize="58">
<Data Format="L5K">
[62,0,6,0,1,0,220,0,41,42,431,432,3,4,2,44,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
</Data>
</ConfigData>
<ConfigScript Size="8728">
<Data Format="L5K">
[20,34,0,0,4,0,0,0,0,0,0,0,0,0,0,0,25,0,0,0,8,-106,0,0,0,1,0,0,0,1,0,0,0,8,0,0,0,75,2,32,-110,36,0,-1,-1,0,0,0,99,33,0,0,8,30,0,0,0,1,0,0,0,1,0,0
		,0,9,0,0,0,16,3,32,-109,36,0,48,2,3,1,0,0,0,10,0,0,0,16,3,32,-109,36,30,48,9,1,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,31,48,9,63,2,1,0,0,0,10
		,0,0,0,16,3,32,-109,36,32,48,9,60,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,33,48,9,-36,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,34,48,9,-83,0,1
		,0,0,0,10,0,0,0,16,3,32,-109,36,35,48,9,4,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,36,48,9,-42,6,1,0,0,0,10,0,0,0,16,3,32,-109,36,37,48,9,-36
		,5,1,0,0,0,10,0,0,0,16,3,32,-109,36,38,48,9,3,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,39,48,9,1,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,41,48,9,0
		,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,42,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,43,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,44,48,9,-32
		,46,1,0,0,0,10,0,0,0,16,3,32,-109,36,45,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,46,48,9,5,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,47,48,9
		,15,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,48,48,9,2,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,49,48,9,5,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,50,48
		,9,5,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,51,48,9,15,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,52,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,54,48
		,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,62,48,9,48,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,63,48,9,50,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,64
		,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,65,48,9,7,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,66,48,9,7,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,67
		,48,9,5,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,68,48,9,9,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,69,48,9,2,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,70
		,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,71,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,72,48,9,1,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,73
		,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,74,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,75,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,76
		,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,77,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,78,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,79
		,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,80,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,81,48,9,2,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,82
		,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,83,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,84,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,85
		,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,86,48,9,-56,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,87,48,9,-56,0,1,0,0,0,10,0,0,0,16,3,32,-109
		,36,88,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,89,48,9,100,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,91,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109
		,36,92,48,9,-24,3,1,0,0,0,10,0,0,0,16,3,32,-109,36,93,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,94,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109
		,36,95,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,96,48,9,-24,3,1,0,0,0,10,0,0,0,16,3,32,-109,36,97,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109
		,36,98,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,99,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,100,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109
		,36,101,48,9,100,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,102,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,103,48,9,-106,0,1,0,0,0,10,0,0,0,16
		,3,32,-109,36,104,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,105,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,106,48,9,0,0,1,0,0,0,10,0,0
		,0,16,3,32,-109,36,121,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,122,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,123,48,9,3,0,1,0,0,0,10
		,0,0,0,16,3,32,-109,36,124,48,9,100,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,125,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,126,48,9,50,0
		,1,0,0,0,10,0,0,0,16,3,32,-109,36,127,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-128,48,9,1,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-127
		,48,9,-64,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-126,48,9,-88,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-125,48,9,118,0,1,0,0,0,10,0,0,0,16,3
		,32,-109,36,-124,48,9,-125,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-123,48,9,-1,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-122,48,9,-1,0,1
		,0,0,0,10,0,0,0,16,3,32,-109,36,-121,48,9,-1,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-120,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-119
		,48,9,-64,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-118,48,9,-88,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-117,48,9,1,0,1,0,0,0,10,0,0,0,16,3,32
		,-109,36,-116,48,9,-2,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-115,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-113,48,9,0,0,1,0,0,0,10,0
		,0,0,16,3,32,-109,36,-112,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-111,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-110,48,9,0,0,1
		,0,0,0,10,0,0,0,16,3,32,-109,36,-109,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-108,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-107
		,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-106,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-103,48,9,41,0,1,0,0,0,10,0,0,0,16,3,32,-109
		,36,-102,48,9,42,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-101,48,9,-81,1,1,0,0,0,10,0,0,0,16,3,32,-109,36,-100,48,9,-80,1,1,0,0,0,10,0
		,0,0,16,3,32,-109,36,-99,48,9,3,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-98,48,9,4,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-97,48,9,2,0,1,0,0,0
		,10,0,0,0,16,3,32,-109,36,-96,48,9,44,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-95,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-94,48,9,0,0
		,1,0,0,0,10,0,0,0,16,3,32,-109,36,-93,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-92,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-91,48
		,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-90,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-89,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-88
		,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-87,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-85,48,9,2,0,1,0,0,0,10,0,0,0,16,3,32,-109,36
		,-84,48,9,3,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-83,48,9,4,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-82,48,9,5,0,1,0,0,0,10,0,0,0,16,3,32,-109
		,36,-81,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-76,48,9,-15,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-75,48,9,-15,0,1,0,0,0,10,0,0,0,16
		,3,32,-109,36,-74,48,9,-15,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-73,48,9,-15,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-72,48,9,-15,0,1,0
		,0,0,10,0,0,0,16,3,32,-109,36,-71,48,9,-15,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-70,48,9,-15,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-69
		,48,9,-15,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-66,48,9,44,1,1,0,0,0,10,0,0,0,16,3,32,-109,36,-65,48,9,44,1,1,0,0,0,10,0,0,0,16,3,32,-109
		,36,-64,48,9,44,1,1,0,0,0,10,0,0,0,16,3,32,-109,36,-63,48,9,44,1,1,0,0,0,10,0,0,0,16,3,32,-109,36,-62,48,9,44,1,1,0,0,0,10,0,0,0,16,3
		,32,-109,36,-61,48,9,44,1,1,0,0,0,10,0,0,0,16,3,32,-109,36,-60,48,9,44,1,1,0,0,0,10,0,0,0,16,3,32,-109,36,-59,48,9,44,1,1,0,0,0,10
		,0,0,0,16,3,32,-109,36,-56,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-55,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-54,48,9,0,0,1,0,0
		,0,10,0,0,0,16,3,32,-109,36,-53,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-52,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-51,48,9,0,0
		,1,0,0,0,10,0,0,0,16,3,32,-109,36,-50,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-49,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-48,48
		,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-47,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-46,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-45
		,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-44,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-43,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36
		,-42,48,9,0,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,-41,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-102,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32
		,-109,37,0,-101,1,48,9,-12,1,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-100,1,48,9,-24,3,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-99,1,48,9,-48
		,7,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-98,1,48,9,-72,11,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-97,1,48,9,-96,15,1,0,0,0,12,0,0,0,16,4,32
		,-109,37,0,-96,1,48,9,-120,19,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-95,1,48,9,112,23,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-94,1,48,9
		,112,23,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-93,1,48,9,112,23,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-92,1,48,9,112,23,1,0,0,0,12,0,0,0,16
		,4,32,-109,37,0,-91,1,48,9,112,23,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-90,1,48,9,112,23,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-89,1,48
		,9,112,23,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-88,1,48,9,112,23,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-87,1,48,9,112,23,1,0,0,0,12,0,0,0
		,16,4,32,-109,37,0,-86,1,48,9,112,23,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-85,1,48,9,112,23,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-84
		,1,48,9,1,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-83,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-82,1,48,9,100,0,1,0,0,0,12,0,0,0,16,4,32
		,-109,37,0,-81,1,48,9,7,23,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-80,1,48,9,46,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-79,1,48,9,-12,1,1
		,0,0,0,12,0,0,0,16,4,32,-109,37,0,-78,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-77,1,48,9,11,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0
		,-76,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-75,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-74,1,48,9,-24,3,1,0,0,0,12,0,0,0,16
		,4,32,-109,37,0,-73,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-72,1,48,9,40,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-71,1,48,9,0,0,1
		,0,0,0,12,0,0,0,16,4,32,-109,37,0,-70,1,48,9,-24,3,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-69,1,48,9,-24,3,1,0,0,0,12,0,0,0,16,4,32,-109
		,37,0,-68,1,48,9,-24,3,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-67,1,48,9,-24,3,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-66,1,48,9,-24,3,1,0,0
		,0,12,0,0,0,16,4,32,-109,37,0,-65,1,48,9,-24,3,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-64,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-63
		,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-62,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-61,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109
		,37,0,-60,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-59,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-58,1,48,9,0,0,1,0,0,0,12,0,0,0
		,16,4,32,-109,37,0,-57,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-56,1,48,9,88,2,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-55,1,48,9,0
		,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-54,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-53,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37
		,0,-52,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-51,1,48,9,1,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-50,1,48,9,20,0,1,0,0,0,12,0,0,0,16
		,4,32,-109,37,0,-49,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-48,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-47,1,48,9,0,0,1,0
		,0,0,12,0,0,0,16,4,32,-109,37,0,-46,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-45,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-44
		,1,48,9,88,2,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-43,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-42,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32
		,-109,37,0,-41,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-40,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-39,1,48,9,1,0,1,0,0,0,12
		,0,0,0,16,4,32,-109,37,0,-38,1,48,9,20,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-37,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-36,1,48
		,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-35,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-34,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109
		,37,0,-33,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-31,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-30,1,48,9,0,0,1,0,0,0,12,0,0,0
		,16,4,32,-109,37,0,-29,1,48,9,0,4,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-28,1,48,9,-14,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-27,1,48,9
		,-14,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-26,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-25,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109
		,37,0,-24,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-23,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-22,1,48,9,0,0,1,0,0,0,12,0,0,0
		,16,4,32,-109,37,0,-21,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-20,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-19,1,48,9,0,0
		,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-18,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-17,1,48,9,3,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0
		,-16,1,48,9,28,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-15,1,48,9,5,2,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-14,1,48,9,0,0,1,0,0,0,12,0,0,0,16
		,4,32,-109,37,0,-13,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-12,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-11,1,48,9,126,4
		,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-10,1,48,9,-1,6,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-9,1,48,9,-55,20,1,0,0,0,12,0,0,0,16,4,32,-109
		,37,0,-8,1,48,9,4,16,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-3,1,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,-2,1,48,9,65,3,1,0,0,0,12,0,0,0,16
		,4,32,-109,37,0,-1,1,48,9,10,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,0,2,48,9,-36,5,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,1,2,48,9,10,0,1,0,0
		,0,12,0,0,0,16,4,32,-109,37,0,2,2,48,9,-48,7,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,3,2,48,9,10,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,4,2,48
		,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,5,2,48,9,30,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,6,2,48,9,7,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0
		,7,2,48,9,100,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,8,2,48,9,2,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,9,2,48,9,-24,3,1,0,0,0,12,0,0,0,16,4,32
		,-109,37,0,10,2,48,9,100,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,11,2,48,9,-24,3,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,12,2,48,9,100,0,1,0
		,0,0,12,0,0,0,16,4,32,-109,37,0,13,2,48,9,-24,3,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,14,2,48,9,100,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0
		,15,2,48,9,94,1,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,16,2,48,9,44,1,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,17,2,48,9,7,0,1,0,0,0,12,0,0,0,16,4,32
		,-109,37,0,18,2,48,9,6,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,19,2,48,9,25,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,20,2,48,9,-6,0,1,0,0,0,12
		,0,0,0,16,4,32,-109,37,0,21,2,48,9,-106,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,22,2,48,9,63,2,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,23,2,48
		,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,24,2,48,9,0,4,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,25,2,48,9,64,0,1,0,0,0,12,0,0,0,16,4,32,-109,37
		,0,26,2,48,9,20,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,27,2,48,9,5,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,28,2,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32
		,-109,37,0,29,2,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,30,2,48,9,10,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,31,2,48,9,0,0,1,0,0,0,12,0
		,0,0,16,4,32,-109,37,0,32,2,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,33,2,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,34,2,48,9,65,0
		,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,35,2,48,9,1,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,36,2,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,37
		,2,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,38,2,48,9,1,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,40,2,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109
		,37,0,41,2,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,42,2,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,44,2,48,9,2,0,1,0,0,0,12,0,0,0,16,4
		,32,-109,37,0,45,2,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,46,2,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,47,2,48,9,0,16,1,0,0,0,12
		,0,0,0,16,4,32,-109,37,0,48,2,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,49,2,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,50,2,48,9,100
		,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,51,2,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,52,2,48,9,100,0,1,0,0,0,12,0,0,0,16,4,32,-109,37
		,0,53,2,48,9,8,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,54,2,48,9,30,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,55,2,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32
		,-109,37,0,56,2,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,57,2,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,58,2,48,9,0,0,1,0,0,0,12,0,0
		,0,16,4,32,-109,37,0,59,2,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,60,2,48,9,100,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,61,2,48,9,3,0
		,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,62,2,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,63,2,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,64
		,2,48,9,-6,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,68,2,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,69,2,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109
		,37,0,70,2,48,9,45,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,71,2,48,9,40,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,72,2,48,9,-6,0,1,0,0,0,12,0,0,0
		,16,4,32,-109,37,0,73,2,48,9,40,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,74,2,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,75,2,48,9,120,0
		,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,76,2,48,9,-12,1,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,77,2,48,9,0,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0
		,78,2,48,9,-24,3,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,79,2,48,9,35,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,80,2,48,9,30,0,1,0,0,0,12,0,0,0,16
		,4,32,-109,37,0,81,2,48,9,100,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,82,2,48,9,100,0,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,83,2,48,9,10,0
		,1,0,0,0,12,0,0,0,16,4,32,-109,37,0,84,2,48,9,10,0,1,0,0,0,37,0,0,0,16,3,32,-99,36,1,48,1,-127,0,99,42,0,18,1,1,0,1,0,16,0,67,117,115
		,116,111,109,32,71,114,111,117,112,32,32,32,32,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,7,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108
		,37,0,18,1,48,8,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,9,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,10,0,0,0,0,1,0,0,0,14
		,0,0,0,16,4,32,-108,37,0,18,1,48,11,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,12,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18
		,1,48,13,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,14,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,15,0,0,0,0,1,0,0,0,14,0,0
		,0,16,4,32,-108,37,0,18,1,48,16,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,17,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48
		,18,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,19,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,20,0,0,0,0,1,0,0,0,14,0,0,0,16
		,4,32,-108,37,0,18,1,48,21,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,22,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,23
		,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,24,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,25,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32
		,-108,37,0,18,1,48,26,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,27,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,28,0,0,0
		,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,29,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,30,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108
		,37,0,18,1,48,31,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,32,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,33,0,0,0,0,1,0,0
		,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,34,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,35,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37
		,0,18,1,48,36,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,37,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,38,0,0,0,0,1,0,0,0,14
		,0,0,0,16,4,32,-108,37,0,18,1,48,39,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,40,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18
		,1,48,41,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,42,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,43,0,0,0,0,1,0,0,0,14,0,0
		,0,16,4,32,-108,37,0,18,1,48,44,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,45,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48
		,46,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,47,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,48,0,0,0,0,1,0,0,0,14,0,0,0,16
		,4,32,-108,37,0,18,1,48,49,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,50,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,51
		,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,52,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,53,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32
		,-108,37,0,18,1,48,54,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,55,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,56,0,0,0
		,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,57,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,58,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108
		,37,0,18,1,48,59,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,60,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,61,0,0,0,0,1,0,0
		,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,62,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,63,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37
		,0,18,1,48,64,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,65,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,66,0,0,0,0,1,0,0,0,14
		,0,0,0,16,4,32,-108,37,0,18,1,48,67,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,68,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18
		,1,48,69,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,70,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,71,0,0,0,0,1,0,0,0,14,0,0
		,0,16,4,32,-108,37,0,18,1,48,72,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,73,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48
		,74,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,75,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,76,0,0,0,0,1,0,0,0,14,0,0,0,16
		,4,32,-108,37,0,18,1,48,77,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,78,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,79
		,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,80,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,81,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32
		,-108,37,0,18,1,48,82,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,83,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,84,0,0,0
		,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,85,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,86,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108
		,37,0,18,1,48,87,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,88,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,89,0,0,0,0,1,0,0
		,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,90,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,91,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37
		,0,18,1,48,92,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,93,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,94,0,0,0,0,1,0,0,0,14
		,0,0,0,16,4,32,-108,37,0,18,1,48,95,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,96,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18
		,1,48,97,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,98,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,99,0,0,0,0,1,0,0,0,14,0,0
		,0,16,4,32,-108,37,0,18,1,48,100,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,101,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18
		,1,48,102,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,103,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,104,0,0,0,0,1,0,0,0,14
		,0,0,0,16,4,32,-108,37,0,18,1,48,105,0,0,0,0,1,0,0,0,14,0,0,0,16,4,32,-108,37,0,18,1,48,106,0,0,0,0,1,0,0,0,28,0,0,0,16,3,32,-110,36,0
		,48,31,1,0,16,0,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,0,45,0,0,0,8,100,0,0,0,1,0,0,0,6,0,0,0,24,0,0,0,16,3,32,-110,36,0,48
		,38,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,64,0,0,0,0,0,0,34,0,0,0,8,61,0,0,0,1,0,0,0,1,0,0,0,9,0,0,0,16,3,32,-105,36,0,48,3,3,3,0,0,0,-120,19,0,0,0,0,29
		,0,0,0,0,100,0,0,0,2,0,0,0,-128,0,0,0,-102,94,105,-57,13,-69,-16,17,-106,32,60,-100,15,0,-34,32,0,0,0]
</Data>
</ConfigScript>
<Connections>
<Connection Name="Standard" RPI="20000" Type="Output" InputCxnPoint="1" OutputCxnPoint="2" OutputSize="12" InputSize="16" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:PowerFlex525V_E_F6518AFA:I:0">
<DataValueMember Name="DriveStatus" DataType="INT" Radix="Binary" Value="2#0000_0110_0000_1101" />
<DataValueMember Name="Ready" DataType="BOOL" Value="1" />
<DataValueMember Name="Active" DataType="BOOL" Value="0" />
<DataValueMember Name="CommandDir" DataType="BOOL" Value="1" />
<DataValueMember Name="ActualDir" DataType="BOOL" Value="1" />
<DataValueMember Name="Accelerating" DataType="BOOL" Value="0" />
<DataValueMember Name="Decelerating" DataType="BOOL" Value="0" />
<DataValueMember Name="Faulted" DataType="BOOL" Value="0" />
<DataValueMember Name="AtReference" DataType="BOOL" Value="0" />
<DataValueMember Name="CommFreqCnt" DataType="BOOL" Value="1" />
<DataValueMember Name="CommLogicCnt" DataType="BOOL" Value="1" />
<DataValueMember Name="ParmsLocked" DataType="BOOL" Value="0" />
<DataValueMember Name="DigIn1Active" DataType="BOOL" Value="0" />
<DataValueMember Name="DigIn2Active" DataType="BOOL" Value="0" />
<DataValueMember Name="DigIn3Active" DataType="BOOL" Value="0" />
<DataValueMember Name="DigIn4Active" DataType="BOOL" Value="0" />
<DataValueMember Name="OutputFreq" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="OutputCurrent" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="OutputVoltage" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="CommandedFreq" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumFreq" DataType="INT" Radix="Decimal" Value="12000" />
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[0,0,0,0,5895,46]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:PowerFlex525V_E_34F78343:O:0">
<DataValueMember Name="LogicCommand" DataType="INT" Radix="Binary" Value="2#0000_0000_0000_0000" />
<DataValueMember Name="Stop" DataType="BOOL" Value="0" />
<DataValueMember Name="Start" DataType="BOOL" Value="0" />
<DataValueMember Name="Jog" DataType="BOOL" Value="0" />
<DataValueMember Name="ClearFaults" DataType="BOOL" Value="0" />
<DataValueMember Name="Forward" DataType="BOOL" Value="0" />
<DataValueMember Name="Reverse" DataType="BOOL" Value="0" />
<DataValueMember Name="ForceKeypadCtrl" DataType="BOOL" Value="0" />
<DataValueMember Name="MOPIncrement" DataType="BOOL" Value="0" />
<DataValueMember Name="AccelRate1" DataType="BOOL" Value="0" />
<DataValueMember Name="AccelRate2" DataType="BOOL" Value="0" />
<DataValueMember Name="DecelRate1" DataType="BOOL" Value="0" />
<DataValueMember Name="DecelRate2" DataType="BOOL" Value="0" />
<DataValueMember Name="FreqSel01" DataType="BOOL" Value="0" />
<DataValueMember Name="FreqSel02" DataType="BOOL" Value="0" />
<DataValueMember Name="FreqSel03" DataType="BOOL" Value="0" />
<DataValueMember Name="MOPDecrement" DataType="BOOL" Value="0" />
<DataValueMember Name="FreqCommand" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="AccelTime1" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="DecelTime1" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="JogFrequency" DataType="INT" Radix="Decimal" Value="5895" />
<DataValueMember Name="JogAccelDecel" DataType="INT" Radix="Decimal" Value="46" />
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'SJ_Gormley_20251112_r02.L5X', 1),
    'PowerFlex 527-STO CIP Safety': ("""\
<Module Name="TestMod1_PowerFlex527STOCIPSa" CatalogNumber="PowerFlex 527-STO CIP Safety" Vendor="1" ProductType="45" ProductCode="15" Major="2" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false" SafetyNetwork="16#0000_44c9_02ec_6f66" SafetyEnabled="true">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="292">
<Data Format="L5K">
[296,2,257,18,94420071,0,2565904,16908804,1,0,0,0,0,0,0,0,0,262148000,262148000,262148000,262148000,0,0,32768
		,230,-65536,1120403456,1045220557,1073741824,0,1114636288,0,1120403456,1120403456,0,1120403456
		,1124859904,1115815936,0,1120403456,1,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,32768004,16384500,0,0,0,0,0,0,0,0]
</Data>
</ConfigData>
<SafetyScript Size="59">
<Data Format="L5K">
[55,0,0,0,5,0,0,0,0,0,0,0,0,0,0,0,39,0,0,0,0,0,0,0,0,3,0,0,0,25,0,0,0,0,0,0,18,0,0,0,0,0,0,0,-41,-20,58,-48,-19,44,105,3,-56,68,0,0,1,1,0]
</Data>
</SafetyScript>
<Connections>
<Connection Name="AMotionDiagnostics" RPI="1000" Type="DiagnosticInput" EventID="0" ProgrammaticallySendEventTrigger="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:Motion_Diagnostics:S:1">
<DataValueMember Name="LostControllerToDriveTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LateControllerToDriveTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LostDriveToControllerTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LateDriveToControllerTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="TimingStatisticsEnabled" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="ControllerToDriveConnectionSize" DataType="INT" Radix="Decimal" Value="48" />
<DataValueMember Name="DriveToControllerConnectionSize" DataType="INT" Radix="Decimal" Value="56" />
<DataValueMember Name="NominalControllerToDriveTime" DataType="INT" Radix="Decimal" Value="2000" />
<DataValueMember Name="NominalDriveToControllerTime" DataType="INT" Radix="Decimal" Value="2000" />
<DataValueMember Name="CoarseUpdatePeriod" DataType="INT" Radix="Decimal" Value="4000" />
</Structure>
</Data>
</InputTag>
</Connection>
<Connection Name="BMotionSync" RPI="4000" Type="MotionSync" EventID="0" ProgrammaticallySendEventTrigger="false" />
<Connection Name="CSafety_Output" RPI="20000" Type="SafetyOutputDataDriven" OutputSize="1" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="60" MaxObservedNetworkDelay="0" Priority="High" InputConnectionType="Unicast" InputProductionTrigger="Application" ConnectionPath="20 04 25 00 60 03 20 04 25 00 80 01 20 04 24 c7" OutputTagSuffix="SO">
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:CIP_Drive_Safety1:SO:0">
<DataValueMember Name="Command" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SafeTorqueOff" DataType="BOOL" Value="0" />
<DataValueMember Name="Reset" DataType="BOOL" Value="0" />
</Structure>
</Data>
</OutputTag>
</Connection>
<Connection Name="DSafety_Input" RPI="10000" Type="SafetyInputDataDriven" InputSize="5" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="40.064" MaxObservedNetworkDelay="0" Priority="High" InputConnectionType="Unicast" InputProductionTrigger="Application" ConnectionPath="20 04 25 00 60 03 20 04 24 c7 20 04 25 00 a0 01" InputTagSuffix="SI">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:CIP_Drive_Safety1:SI:0">
<DataValueMember Name="ConnectionStatus" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0010" />
<DataValueMember Name="RunMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="1" />
<DataValueMember Name="Status" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="TorqueDisabled" DataType="BOOL" Value="0" />
<DataValueMember Name="SafetyFault" DataType="BOOL" Value="0" />
<DataValueMember Name="ResetRequired" DataType="BOOL" Value="0" />
</Structure>
</Data>
</InputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'DnR_Personal/Bender134053_201104.L5X', 1),
    'PowerFlex 755-EENET': ("""\
<Module Name="TestMod1_PowerFlex755EENET" CatalogNumber="PowerFlex 755-EENET" Vendor="1" ProductType="143" ProductCode="2192" Major="14" Minor="5" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false" DrivesADCMode="true" DrivesADCEnabled="false" SafetyEnabled="false">
<EKey State="Disabled" />
<Ports>
<Port Id="1" Address="0" Type="RhinoBP" Upstream="false">
<Bus />
</Port>
<Port Id="13" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications CommMethod="536870913">
<ConfigData ConfigSize="356">
<Data Format="L5K">
[360,0,6,0,1,0,340,17152,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
</Data>
</ConfigData>
<ConfigScript Size="2204">
<Data Format="L5K">
[-104,8,0,0,4,0,0,0,0,0,0,0,0,0,0,0,25,0,0,0,8,-106,0,0,0,1,0,0,0,1,0,0,0,8,0,0,0,75,2,32,-110,36,0,-1,-1,0,0,0,-53,7,0,0,8,30,0,0,0,1,0,0,0,1,0
		,0,0,74,0,0,0,16,3,32,-98,36,1,48,5,2,0,3,0,0,2,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,1,0,0,0,74,0,0,0,16,3,32,-98,36,1,48,5,3,0,3,44,1,9,4,0,0,0,0,4,0,0,0,0,4,1,0,0,0,0,3,49,1,9,4,1,0,0,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,74,0,0,0,16,3,32,-98,36,1,48,5,4,0,47,0,0,5,1,1,0,3,0,0,1,2,0,0,0,1,0,0,2,1,0,0,2,1,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,74,0,0,0,16,3,32,-98,36,1,48,5,5,0,3,0,0,2,1,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,74,0,0,0,16,3,32,-98,36,1,48,5,6,0,1,0,0,31,36,2,0,16,0,80,0,111,0,119,0
		,101,0,114,0,70,0,108,0,101,0,120,0,32,0,55,0,53,0,53,0,32,0,32,0,32,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,74,0,0,0,16,3,32
		,-98,36,1,48,5,7,0,6,1,0,6,24,7,0,100,0,2,0,8,0,65,0,109,0,112,0,115,0,32,0,32,0,32,0,32,0,0,6,2,0,6,24,11,0,100,0,2,0,8,0,66,0,117,0,115
		,0,32,0,86,0,68,0,67,0,32,0,0,0,0,0,0,1,0,0,0,74,0,0,0,16,3,32,-98,36,1,48,5,8,0,6,3,0,6,24,8,0,100,0,2,0,8,0,79,0,117,0,116,0,32,0,86,0,108
		,0,116,0,115,0,0,6,4,0,6,24,9,0,100,0,2,0,8,0,79,0,117,0,116,0,32,0,80,0,119,0,114,0,32,0,0,0,0,0,0,1,0,0,0,74,0,0,0,16,3,32,-98,36,1,48
		,5,9,0,6,5,0,6,24,14,0,100,0,2,0,8,0,69,0,108,0,112,0,32,0,107,0,87,0,72,0,114,0,0,6,6,0,6,24,5,0,100,0,2,0,8,0,84,0,114,0,113,0,32,0,67
		,0,117,0,114,0,32,0,0,0,0,0,0,1,0,0,0,74,0,0,0,16,3,32,-98,36,1,48,5,10,0,3,70,0,9,4,1,0,0,0,0,3,25,0,9,4,0,0,-26,67,4,0,0,-128,64,4,0,0,112
		,66,4,0,0,-36,68,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,74,0,0,0,16,3,32,-98,36,1,48,5,11,0,3,30,0,9,4,0,0,64,64,0,3,71
		,0,9,4,0,0,72,66,0,3,73,0,9,4,0,0,-32,64,4,0,0,0,0,4,-92,112,17,65,4,0,0,0,64,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,74,0,0,0,16,3,32,-98
		,36,1,48,5,12,0,3,77,0,9,4,0,0,0,0,4,0,0,0,0,4,0,0,-32,64,0,3,81,0,9,4,0,0,0,0,4,0,0,0,0,0,3,86,0,9,4,102,102,-8,65,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,1,0,0,0,74,0,0,0,16,3,32,-98,36,1,48,5,13,0,3,87,0,9,4,0,0,-32,64,4,123,20,-96,65,4,123,20,-96,65,0,3,93,0,9,4,-123,-21,65
		,64,0,3,110,0,9,4,0,0,0,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,74,0,0,0,16,3,32,-98,36,1,48,5,14,0,3,120,0,9,4,123,20,-96,65
		,0,3,109,2,9,4,0,0,-16,65,0,3,36,0,9,4,0,0,-26,67,4,0,0,2,67,4,0,0,-128,64,0,3,43,0,9,4,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,74,0,0,0,16
		,3,32,-98,36,1,48,5,15,0,3,44,0,9,4,-57,41,58,62,0,3,60,0,9,4,0,0,-32,64,4,0,0,-32,64,4,0,0,-26,66,4,0,0,112,65,0,3,8,2,9,4,0,0,112,66
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,74,0,0,0,16,3,32,-98,36,1,48,5,16,0,3,9,2,9,4,0,0,112,-62,0,3,73,1,9,4,0,0,112,66,0,3,119,1,9,4
		,-35,-124,59,68,0,3,127,1,9,4,0,0,-8,65,0,3,-118,1,9,4,0,0,8,66,0,3,-90,1,9,4,0,0,76,66,0,0,0,0,0,1,0,0,0,74,0,0,0,16,3,32,-98,36,1,48,5
		,17,0,3,-89,1,9,4,0,0,76,66,0,3,-76,1,9,4,0,0,8,66,0,3,-73,1,9,4,0,0,8,66,0,3,-61,1,9,4,0,0,52,67,0,3,-58,1,9,4,0,0,52,67,0,3,-51,1,9,4,0,0,-106
		,67,0,0,0,0,0,1,0,0,0,74,0,0,0,16,3,32,-98,36,1,48,5,18,0,3,-45,1,9,4,0,0,-128,64,0,3,12,2,9,4,0,0,32,65,4,-113,-62,117,61,0,3,35,2,9,4
		,0,0,112,66,0,3,40,2,9,4,0,0,112,66,0,3,44,2,9,4,0,0,32,65,0,0,0,0,0,0,0,0,0,0,1,0,0,0,74,0,0,0,16,3,32,-98,36,1,48,5,19,0,3,45,2,9,4,0,0,32,65
		,0,3,52,2,9,4,0,0,112,66,0,3,59,2,9,4,0,0,-96,64,4,0,0,32,65,4,0,0,-96,65,4,0,0,-16,65,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,74,0,0,0,16
		,3,32,-98,36,1,48,5,20,0,3,63,2,9,4,0,0,32,66,4,0,0,72,66,4,0,0,112,66,0,3,90,2,9,4,0,0,112,66,0,3,94,2,9,4,0,0,112,66,0,3,125,0,9,4,-119
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,74,0,0,0,16,3,32,-98,36,1,48,5,21,0,3,126,0,9,4,3,0,0,0,0,3,124,2,9,4,0,0,32,65,0,3,-122,2,9,4,0,-128
		,59,69,0,3,-128,0,9,4,-119,0,0,0,4,3,0,0,0,0,3,-120,2,9,4,0,0,32,65,0,0,0,0,0,0,0,0,0,0,1,0,0,0,74,0,0,0,16,3,32,-98,36,1,48,5,22,0,3,-33,2
		,9,4,0,0,-64,64,0,3,17,3,9,4,0,0,-16,65,4,0,0,-16,-63,0,3,56,3,9,4,-102,-103,-103,62,0,3,81,4,9,4,-119,65,0,64,0,3,87,4,9,4,-119,65
		,0,64,0,0,0,0,0,0,0,0,0,0,1,0,0,0,74,0,0,0,16,3,32,-98,36,1,48,5,23,0,3,3,6,9,4,0,0,0,64,4,0,0,32,65,0,3,7,6,9,4,-51,-52,76,63,4,0,0,0,63,4,0,0
		,-120,65,0,3,25,6,9,4,-102,-103,25,62,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,74,0,0,0,16,3,32,-98,36,1,48,5,24,0,3,26,6,9,4,-113
		,-62,117,61,0,3,57,6,9,4,0,0,-16,65,4,0,0,-16,-63,0,3,93,6,9,4,0,0,112,66,0,3,105,6,9,4,0,0,112,66,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1
		,0,0,0,74,0,0,0,16,3,32,-98,36,1,48,5,25,0,3,23,2,9,4,0,0,-64,63,0,3,25,2,9,4,0,0,-64,63,0,3,33,2,9,4,109,3,0,0,0,3,-110,6,9,4,0,0,-64,64
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,10,0,0,0,16,3,32,-101,36,0,48,7,71,0,0,45,0,0,0,8,100,0,0,0,1,0,0,0,6,0,0,0,24,0,0,0,16,3
		,32,-110,36,0,48,38,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,64,0,0,0,0,0,0,34,0,0,0,8,61,0,0,0,1,0,0,0,1,0,0,0,9,0,0,0,16,3,32,-105,36,0,48,3,3,3,0,0,0,-120
		,19,0,0,0,0,23,0,0,0,8,62,0,0,0,1,0,0,0,1,0,0,0,6,0,0,0,75,2,32,-105,36,0,0,29,0,0,0,0,100,0,0,0,2,0,0,0,-128,0,0,0,122,-34,8,-21,-76,-46
		,-17,17,-70,-98,-84,116,-79,12,-70,106,0,0,0]
</Data>
</ConfigScript>
<Connections>
<Connection Name="Output" RPI="20000" Type="Output" InputCxnPoint="1" OutputCxnPoint="2" OutputSize="8" InputSize="12" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:PowerFlex755_EENET_Drive:I:0">
<DataValueMember Name="DriveStatus" DataType="DINT" Radix="Binary" Value="2#0010_0001_0000_0000_0000_0100_0000_1100" />
<DataValueMember Name="DriveStatus_Ready" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_Active" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_CommandDir" DataType="BOOL" Value="1" />
<DataValueMember Name="DriveStatus_ActualDir" DataType="BOOL" Value="1" />
<DataValueMember Name="DriveStatus_Accelerating" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_Decelerating" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_Alarm" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_Faulted" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_AtSpeed" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_Manual" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_SpdRefBit0" DataType="BOOL" Value="1" />
<DataValueMember Name="DriveStatus_SpdRefBit1" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_SpdRefBit2" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_SpdRefBit3" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_SpdRefBit4" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_Running" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_Jogging" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_Stopping" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_DCBraking" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_DBActive" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_SpeedMode" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_PositionMode" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_TorqueMode" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_AtZeroSpeed" DataType="BOOL" Value="1" />
<DataValueMember Name="DriveStatus_AtHome" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_AtLimit" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_CurrLimit" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_BusFrqReg" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_EnableOn" DataType="BOOL" Value="1" />
<DataValueMember Name="DriveStatus_MotorOL" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_Regen" DataType="BOOL" Value="0" />
<DataValueMember Name="Feedback" DataType="REAL" Radix="Float" Value="0.0" />
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[1,7.50000000e+001]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:PowerFlex755_EENET_Drive:O:0">
<DataValueMember Name="LogicCommand" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0001" />
<DataValueMember Name="LogicCommand_Stop" DataType="BOOL" Value="1" />
<DataValueMember Name="LogicCommand_Start" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicCommand_Jog1" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicCommand_ClearFaults" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicCommand_Forward" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicCommand_Reverse" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicCommand_Manual" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicCommand_AccelTime1" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicCommand_AccelTime2" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicCommand_DecelTime1" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicCommand_DecelTime2" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicCommand_SpdRefSel0" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicCommand_SpdRefSel1" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicCommand_SpdRefSel2" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicCommand_CoastStop" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicCommand_CLimitStop" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicCommand_Run" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicCommand_Jog2" DataType="BOOL" Value="0" />
<DataValueMember Name="Reference" DataType="REAL" Radix="Float" Value="75.0" />
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'L5X_Samples/Sorter1_20260722r00.L5X', 1),
    'PowerFlex 755-EENET-CM': ("""\
<Module Name="TestMod1_PowerFlex755EENETCM" CatalogNumber="PowerFlex 755-EENET-CM" Vendor="1" ProductType="37" ProductCode="21" Major="12" Minor="2" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="Disabled" />
<Ports>
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="448">
<Data Format="L5K">
[452,4,1,1124073812,31506279,4,10000,131588,1,0,0,0,0,0,0,0,0,-1035468800,0,0,0,0,0,0,0,524296000,524296000,524296000
		,524296000,0,0,1,0,65536,230,256,1065353216,1099694080,0,1109393408,0,1120403456,1120403456,0,1120403456
		,1124859904,1115815936,0,1120403456,1,1,0,0,0,0,0,0,0,8608,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,67108864,16778240
		,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
</Data>
</ConfigData>
<Connections>
<Connection Name="MotionDiagnostics" RPI="1000" Type="DiagnosticInput" EventID="0" ProgrammaticallySendEventTrigger="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:Motion_Diagnostics:S:1">
<DataValueMember Name="LostControllerToDriveTransmissions" DataType="INT" Radix="Decimal" Value="34" />
<DataValueMember Name="LateControllerToDriveTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LostDriveToControllerTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LateDriveToControllerTransmissions" DataType="INT" Radix="Decimal" Value="5" />
<DataValueMember Name="LastControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="TimingStatisticsEnabled" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="ControllerToDriveConnectionSize" DataType="INT" Radix="Decimal" Value="48" />
<DataValueMember Name="DriveToControllerConnectionSize" DataType="INT" Radix="Decimal" Value="72" />
<DataValueMember Name="NominalControllerToDriveTime" DataType="INT" Radix="Decimal" Value="2500" />
<DataValueMember Name="NominalDriveToControllerTime" DataType="INT" Radix="Decimal" Value="2500" />
<DataValueMember Name="CoarseUpdatePeriod" DataType="INT" Radix="Decimal" Value="5000" />
</Structure>
</Data>
</InputTag>
</Connection>
<Connection Name="MotionSync" RPI="5000" Type="MotionSync" EventID="0" ProgrammaticallySendEventTrigger="false" />
</Connections>
</Communications>
</Module>
""", 'L5X_Samples/Sorter1_20260722r00.L5X', 1),
    'PowerFlex 755-EENET-CM-S': ("""\
<Module Name="TestMod1_PowerFlex755EENETCMS" CatalogNumber="PowerFlex 755-EENET-CM-S" Vendor="1" ProductType="37" ProductCode="22" Major="20" Minor="3" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="2" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="448">
<Data Format="L5K">
[452,4,257,49,31506279,4,10000,131588,1,0,0,0,0,0,0,0,0,-1010302976,0,0,0,0,0,0,0,524296000,524296000,524296000
		,524296000,0,0,129,0,65536,0,256,1085213245,1146060800,0,1107820544,0,1120403456,1120403456,0,1120403456
		,1124859904,1115815936,0,1120403456,1,3,0,0,0,0,0,0,0,8608,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,67108864,16778240
		,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
</Data>
</ConfigData>
<Connections>
<Connection Name="MotionDiagnostics" RPI="1000" Type="DiagnosticInput" EventID="0" ProgrammaticallySendEventTrigger="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:Motion_Diagnostics:S:1">
<DataValueMember Name="LostControllerToDriveTransmissions" DataType="INT" Radix="Decimal" Value="24" />
<DataValueMember Name="LateControllerToDriveTransmissions" DataType="INT" Radix="Decimal" Value="20535" />
<DataValueMember Name="LostDriveToControllerTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LateDriveToControllerTransmissions" DataType="INT" Radix="Decimal" Value="11786" />
<DataValueMember Name="LastControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="TimingStatisticsEnabled" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="ControllerToDriveConnectionSize" DataType="INT" Radix="Decimal" Value="48" />
<DataValueMember Name="DriveToControllerConnectionSize" DataType="INT" Radix="Decimal" Value="76" />
<DataValueMember Name="NominalControllerToDriveTime" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="NominalDriveToControllerTime" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="CoarseUpdatePeriod" DataType="INT" Radix="Decimal" Value="2000" />
</Structure>
</Data>
</InputTag>
</Connection>
<Connection Name="MotionSync" RPI="2000" Type="MotionSync" EventID="0" ProgrammaticallySendEventTrigger="false" />
</Connections>
</Communications>
</Module>
""", 'L5X_Samples/MurrayBros_20260122r1.L5X', 1),
    'RHINOBP-DRIVE-PERIPHERAL-MODULE': ("""\
<Module Name="TestMod1_RHINOBPDRIVEPERIPHER" CatalogNumber="PowerFlex 755-EENET" Vendor="1" ProductType="143" ProductCode="2192" Major="14" Minor="5" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false" DrivesADCMode="true" DrivesADCEnabled="false" SafetyEnabled="false">
<EKey State="Disabled" />
<Ports>
<Port Id="1" Address="0" Type="RhinoBP" Upstream="false">
<Bus />
</Port>
<Port Id="13" Address="192.168.1.63" Type="Ethernet" Upstream="true" />
</Ports>
<Communications CommMethod="536870913">
<ConfigData ConfigSize="356">
<Data Format="L5K">
[360,0,6,0,1,0,340,17152,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
</Data>
</ConfigData>
<ConfigScript Size="2204">
<Data Format="L5K">
[-104,8,0,0,4,0,0,0,0,0,0,0,0,0,0,0,25,0,0,0,8,-106,0,0,0,1,0,0,0,1,0,0,0,8,0,0,0,75,2,32,-110,36,0,-1,-1,0,0,0,-53,7,0,0,8,30,0,0,0,1,0,0,0,1,0
		,0,0,74,0,0,0,16,3,32,-98,36,1,48,5,2,0,3,0,0,2,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,1,0,0,0,74,0,0,0,16,3,32,-98,36,1,48,5,3,0,3,44,1,9,4,0,0,0,0,4,0,0,0,0,4,1,0,0,0,0,3,49,1,9,4,1,0,0,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,74,0,0,0,16,3,32,-98,36,1,48,5,4,0,47,0,0,5,1,1,0,3,0,0,1,2,0,0,0,1,0,0,2,1,0,0,2,1,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,74,0,0,0,16,3,32,-98,36,1,48,5,5,0,3,0,0,2,1,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,74,0,0,0,16,3,32,-98,36,1,48,5,6,0,1,0,0,31,36,2,0,16,0,80,0,111,0,119,0
		,101,0,114,0,70,0,108,0,101,0,120,0,32,0,55,0,53,0,53,0,32,0,32,0,32,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,74,0,0,0,16,3,32
		,-98,36,1,48,5,7,0,6,1,0,6,24,7,0,100,0,2,0,8,0,65,0,109,0,112,0,115,0,32,0,32,0,32,0,32,0,0,6,2,0,6,24,11,0,100,0,2,0,8,0,66,0,117,0,115
		,0,32,0,86,0,68,0,67,0,32,0,0,0,0,0,0,1,0,0,0,74,0,0,0,16,3,32,-98,36,1,48,5,8,0,6,3,0,6,24,8,0,100,0,2,0,8,0,79,0,117,0,116,0,32,0,86,0,108
		,0,116,0,115,0,0,6,4,0,6,24,9,0,100,0,2,0,8,0,79,0,117,0,116,0,32,0,80,0,119,0,114,0,32,0,0,0,0,0,0,1,0,0,0,74,0,0,0,16,3,32,-98,36,1,48
		,5,9,0,6,5,0,6,24,14,0,100,0,2,0,8,0,69,0,108,0,112,0,32,0,107,0,87,0,72,0,114,0,0,6,6,0,6,24,5,0,100,0,2,0,8,0,84,0,114,0,113,0,32,0,67
		,0,117,0,114,0,32,0,0,0,0,0,0,1,0,0,0,74,0,0,0,16,3,32,-98,36,1,48,5,10,0,3,70,0,9,4,1,0,0,0,0,3,25,0,9,4,0,0,-26,67,4,0,0,-128,64,4,0,0,112
		,66,4,0,0,-36,68,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,74,0,0,0,16,3,32,-98,36,1,48,5,11,0,3,30,0,9,4,0,0,64,64,0,3,71
		,0,9,4,0,0,72,66,0,3,73,0,9,4,0,0,-32,64,4,0,0,0,0,4,-92,112,17,65,4,0,0,0,64,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,74,0,0,0,16,3,32,-98
		,36,1,48,5,12,0,3,77,0,9,4,0,0,0,0,4,0,0,0,0,4,0,0,-32,64,0,3,81,0,9,4,0,0,0,0,4,0,0,0,0,0,3,86,0,9,4,102,102,-8,65,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,1,0,0,0,74,0,0,0,16,3,32,-98,36,1,48,5,13,0,3,87,0,9,4,0,0,-32,64,4,123,20,-96,65,4,123,20,-96,65,0,3,93,0,9,4,-123,-21,65
		,64,0,3,110,0,9,4,0,0,0,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,74,0,0,0,16,3,32,-98,36,1,48,5,14,0,3,120,0,9,4,123,20,-96,65
		,0,3,109,2,9,4,0,0,-16,65,0,3,36,0,9,4,0,0,-26,67,4,0,0,2,67,4,0,0,-128,64,0,3,43,0,9,4,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,74,0,0,0,16
		,3,32,-98,36,1,48,5,15,0,3,44,0,9,4,-57,41,58,62,0,3,60,0,9,4,0,0,-32,64,4,0,0,-32,64,4,0,0,-26,66,4,0,0,112,65,0,3,8,2,9,4,0,0,112,66
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,74,0,0,0,16,3,32,-98,36,1,48,5,16,0,3,9,2,9,4,0,0,112,-62,0,3,73,1,9,4,0,0,112,66,0,3,119,1,9,4
		,-35,-124,59,68,0,3,127,1,9,4,0,0,-8,65,0,3,-118,1,9,4,0,0,8,66,0,3,-90,1,9,4,0,0,76,66,0,0,0,0,0,1,0,0,0,74,0,0,0,16,3,32,-98,36,1,48,5
		,17,0,3,-89,1,9,4,0,0,76,66,0,3,-76,1,9,4,0,0,8,66,0,3,-73,1,9,4,0,0,8,66,0,3,-61,1,9,4,0,0,52,67,0,3,-58,1,9,4,0,0,52,67,0,3,-51,1,9,4,0,0,-106
		,67,0,0,0,0,0,1,0,0,0,74,0,0,0,16,3,32,-98,36,1,48,5,18,0,3,-45,1,9,4,0,0,-128,64,0,3,12,2,9,4,0,0,32,65,4,-113,-62,117,61,0,3,35,2,9,4
		,0,0,112,66,0,3,40,2,9,4,0,0,112,66,0,3,44,2,9,4,0,0,32,65,0,0,0,0,0,0,0,0,0,0,1,0,0,0,74,0,0,0,16,3,32,-98,36,1,48,5,19,0,3,45,2,9,4,0,0,32,65
		,0,3,52,2,9,4,0,0,112,66,0,3,59,2,9,4,0,0,-96,64,4,0,0,32,65,4,0,0,-96,65,4,0,0,-16,65,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,74,0,0,0,16
		,3,32,-98,36,1,48,5,20,0,3,63,2,9,4,0,0,32,66,4,0,0,72,66,4,0,0,112,66,0,3,90,2,9,4,0,0,112,66,0,3,94,2,9,4,0,0,112,66,0,3,125,0,9,4,-119
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,74,0,0,0,16,3,32,-98,36,1,48,5,21,0,3,126,0,9,4,3,0,0,0,0,3,124,2,9,4,0,0,32,65,0,3,-122,2,9,4,0,-128
		,59,69,0,3,-128,0,9,4,-119,0,0,0,4,3,0,0,0,0,3,-120,2,9,4,0,0,32,65,0,0,0,0,0,0,0,0,0,0,1,0,0,0,74,0,0,0,16,3,32,-98,36,1,48,5,22,0,3,-33,2
		,9,4,0,0,-64,64,0,3,17,3,9,4,0,0,-16,65,4,0,0,-16,-63,0,3,56,3,9,4,-102,-103,-103,62,0,3,81,4,9,4,-119,65,0,64,0,3,87,4,9,4,-119,65
		,0,64,0,0,0,0,0,0,0,0,0,0,1,0,0,0,74,0,0,0,16,3,32,-98,36,1,48,5,23,0,3,3,6,9,4,0,0,0,64,4,0,0,32,65,0,3,7,6,9,4,-51,-52,76,63,4,0,0,0,63,4,0,0
		,-120,65,0,3,25,6,9,4,-102,-103,25,62,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,74,0,0,0,16,3,32,-98,36,1,48,5,24,0,3,26,6,9,4,-113
		,-62,117,61,0,3,57,6,9,4,0,0,-16,65,4,0,0,-16,-63,0,3,93,6,9,4,0,0,112,66,0,3,105,6,9,4,0,0,112,66,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1
		,0,0,0,74,0,0,0,16,3,32,-98,36,1,48,5,25,0,3,23,2,9,4,0,0,-64,63,0,3,25,2,9,4,0,0,-64,63,0,3,33,2,9,4,109,3,0,0,0,3,-110,6,9,4,0,0,-64,64
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,10,0,0,0,16,3,32,-101,36,0,48,7,71,0,0,45,0,0,0,8,100,0,0,0,1,0,0,0,6,0,0,0,24,0,0,0,16,3
		,32,-110,36,0,48,38,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,64,0,0,0,0,0,0,34,0,0,0,8,61,0,0,0,1,0,0,0,1,0,0,0,9,0,0,0,16,3,32,-105,36,0,48,3,3,3,0,0,0,-120
		,19,0,0,0,0,23,0,0,0,8,62,0,0,0,1,0,0,0,1,0,0,0,6,0,0,0,75,2,32,-105,36,0,0,29,0,0,0,0,100,0,0,0,2,0,0,0,-128,0,0,0,122,-34,8,-21,-76,-46
		,-17,17,-70,-98,-84,116,-79,12,-70,106,0,0,0]
</Data>
</ConfigScript>
<Connections>
<Connection Name="Output" RPI="20000" Type="Output" InputCxnPoint="1" OutputCxnPoint="2" OutputSize="8" InputSize="12" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:PowerFlex755_EENET_Drive:I:0">
<DataValueMember Name="DriveStatus" DataType="DINT" Radix="Binary" Value="2#0010_0001_0000_0000_0000_0100_0000_1100" />
<DataValueMember Name="DriveStatus_Ready" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_Active" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_CommandDir" DataType="BOOL" Value="1" />
<DataValueMember Name="DriveStatus_ActualDir" DataType="BOOL" Value="1" />
<DataValueMember Name="DriveStatus_Accelerating" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_Decelerating" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_Alarm" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_Faulted" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_AtSpeed" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_Manual" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_SpdRefBit0" DataType="BOOL" Value="1" />
<DataValueMember Name="DriveStatus_SpdRefBit1" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_SpdRefBit2" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_SpdRefBit3" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_SpdRefBit4" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_Running" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_Jogging" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_Stopping" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_DCBraking" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_DBActive" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_SpeedMode" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_PositionMode" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_TorqueMode" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_AtZeroSpeed" DataType="BOOL" Value="1" />
<DataValueMember Name="DriveStatus_AtHome" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_AtLimit" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_CurrLimit" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_BusFrqReg" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_EnableOn" DataType="BOOL" Value="1" />
<DataValueMember Name="DriveStatus_MotorOL" DataType="BOOL" Value="0" />
<DataValueMember Name="DriveStatus_Regen" DataType="BOOL" Value="0" />
<DataValueMember Name="Feedback" DataType="REAL" Radix="Float" Value="0.0" />
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[1,7.50000000e+001]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:PowerFlex755_EENET_Drive:O:0">
<DataValueMember Name="LogicCommand" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0001" />
<DataValueMember Name="LogicCommand_Stop" DataType="BOOL" Value="1" />
<DataValueMember Name="LogicCommand_Start" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicCommand_Jog1" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicCommand_ClearFaults" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicCommand_Forward" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicCommand_Reverse" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicCommand_Manual" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicCommand_AccelTime1" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicCommand_AccelTime2" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicCommand_DecelTime1" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicCommand_DecelTime2" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicCommand_SpdRefSel0" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicCommand_SpdRefSel1" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicCommand_SpdRefSel2" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicCommand_CoastStop" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicCommand_CLimitStop" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicCommand_Run" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicCommand_Jog2" DataType="BOOL" Value="0" />
<DataValueMember Name="Reference" DataType="REAL" Radix="Float" Value="75.0" />
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module CatalogNumber="RHINOBP-DRIVE-PERIPHERAL-MODULE" Vendor="1" ProductType="0" ProductCode="28" Major="1" Minor="1" UserDefinedVendor="1" UserDefinedProductType="143" UserDefinedProductCode="32928" UserDefinedMajor="1" UserDefinedMinor="1" ParentModule="TestMod1_RHINOBPDRIVEPERIPHER" ParentModPortId="1" Inhibited="false" MajorFault="false" ShutdownParentOnFault="false" DrivesADCMode="true" DrivesADCEnabled="false" UserDefinedCatalogNumber="EtherNet/IP">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="2" Address="13" Type="RhinoBP" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="4">
<Data Format="L5K">
[8,6,1]
</Data>
</ConfigData>
<ConfigScript Size="628">
<Data Format="L5K">
[112,2,0,0,4,0,0,0,0,0,0,0,0,0,0,0,25,0,0,0,8,-106,0,0,0,1,0,0,0,1,0,0,0,8,0,0,0,75,2,32,-110,36,0,-1,-1,0,0,0,-93,1,0,0,8,31,0,0,0,1,0,0,0,1,0,0
		,0,74,0,0,0,16,3,32,-96,36,1,48,5,2,0,3,0,0,2,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,1,0,0,0,74,0,0,0,16,3,32,-96,36,1,48,5,3,0,1,0,0,31,36,2,0,16,0,32,0,32,0,32,0,32,0,32,0,32,0,32,0,32,0,32,0,32,0,32,0,32,0,32,0
		,32,0,32,0,32,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,74,0,0,0,16,3,32,-96,36,1,48,5,4,0,3,36,0,9,4,0,0,0,0,0,3,38,0,9,4,-64,0,0,0,4
		,-88,0,0,0,4,60,0,0,0,4,114,0,0,0,4,-1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,74,0,0,0,16,3,32,-96,36,1,48,5,5,0,3,43,0,9,4
		,-1,0,0,0,4,-1,0,0,0,4,0,0,0,0,4,0,0,0,0,4,0,0,0,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,74,0,0,0,16,3,32,-96,36,1
		,48,5,6,0,3,49,0,9,4,0,0,0,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,45,0,0,0,8,100,0
		,0,0,1,0,0,0,6,0,0,0,24,0,0,0,16,3,32,-110,36,0,48,38,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,64,0,0,0,0,0,0,34,0,0,0,8,61,0,0,0,1,0,0,0,1,0,0,0,9,0,0,0,16,3
		,32,-105,36,0,48,3,3,3,0,0,0,-120,19,0,0,0,0,23,0,0,0,8,62,0,0,0,1,0,0,0,1,0,0,0,6,0,0,0,75,2,32,-105,36,0,0,29,0,0,0,0,100,0,0,0,2,0,0,0,-128
		,0,0,0,-49,125,-79,92,-113,-46,-17,17,-124,-18,24,38,73,109,58,37,0,0,0]
</Data>
</ConfigScript>
<Connections />
</Communications>
</Module>
""", 'L5X_Samples/Sorter1_20260722r00.L5X', 2),
}


def main() -> None:
    written = 0
    for catalog, (xml, source, chain_len) in _MODULE_CHAINS.items():
        out_name = "modulesweep_" + "".join(c if c.isalnum() else "_" for c in catalog).strip("_").lower()
        chain_note = "standalone module" if chain_len == 1 else f"module + its real {chain_len - 1}-deep parent chain"
        l5x = build_l5x(target_name="ModSweep_" + "".join(c if c.isalnum() else "" for c in catalog)[:20],
                         tags_xml="", extra_modules_xml=xml)
        _write_unmodeled(
            l5x, out_name,
            f"{catalog} -- real corpus module ({chain_note}), genericized from {source}, "
            f"structurally verbatim. Part of the full I/O module sweep, see OQ-MODULEIO.",
        )
        written += 1
    print(f"Done. {written} module sweep files written.")


if __name__ == "__main__":
    main()
