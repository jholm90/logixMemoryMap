"""I/O module sweep, part 2 -- real catalogs that show 2+ DIFFERENT real
shapes across the corpus (2026-08-27, follow-up to gen_module_sweep.py's
86-catalog single-shape sweep, same "James: every module, 100% filled
out" ask). gen_module_sweep.py deliberately skipped these 14 catalogs
since picking one shape arbitrarily would misrepresent the other real
configuration -- this file covers ALL real variants found for each,
labeled by what actually differs (connection count, rack-aliased vs
direct, etc), not guessed at.

Genuinely useful real finding here: the SAME Kinetix drive catalog number
(2198-D012/D020/D032/D057-ERS3, 2198-S086-ERS3) shows up with either 2
Connections (plain motion) or 4 Connections (motion + separate
SafetyInputDataDriven/SafetyOutputDataDriven) depending on whether
Integrated Safety is actually wired/enabled for that instance -- a real,
config-dependent memory footprint difference on the exact same catalog
number, not two different products.

Run: python -m sample_gen.gen_module_sweep_variants
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


# Catalog -> list of (label, xml, source, chain_len) -- each entry a
# DIFFERENT real shape actually found for that same catalog number.
_MODULE_VARIANTS: dict[str, list[tuple[str, str, str, int]]] = {
    '1734-IB8S/B': [
        ('2conn', """\
<Module Name="TestMod1_1734IB8SB" CatalogNumber="1734-AENTR/C" Vendor="1" ProductType="12" ProductCode="196" Major="7" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="0" Type="PointIO" Upstream="false">
<Bus Size="12" />
</Port>
<Port Id="2" Address="192.168.1.73" Type="Ethernet" Upstream="true" />
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

<Module CatalogNumber="1734-IB8S/B" Vendor="1" ProductType="35" ProductCode="15" Major="2" Minor="1" ParentModule="TestMod1_1734IB8SB" ParentModPortId="1" Inhibited="false" MajorFault="false" SafetyNetwork="16#0000_4cd9_030d_7a8a">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="7" Type="PointIO" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="82">
<Data Format="L5K">
[86,864,-1305618411,51214899,19673,514,1000,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
</Data>
</ConfigData>
<Connections>
<Connection Name="Input" RPI="10000" Type="SafetyInput" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="40.064" MaxObservedNetworkDelay="0" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_IB8S_Safety2:I:0">
<DataValueMember Name="RunMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="0" />
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
""", 'SJ_Gormley_20251112_r02.L5X', 2),
        ('1conn', """\
<Module Name="TestMod1_1734IB8SB" CatalogNumber="1734-AENT/C" Vendor="1" ProductType="12" ProductCode="108" Major="6" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="0" Type="PointIO" Upstream="false">
<Bus Size="17" />
</Port>
<Port Id="2" Address="192.168.1.73" Type="Ethernet" Upstream="true" />
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

<Module Name="TestMod2_1734IB8SB" CatalogNumber="1734-IB8S/B" Vendor="1" ProductType="35" ProductCode="15" Major="2" Minor="1" ParentModule="TestMod1_1734IB8SB" ParentModPortId="1" Inhibited="false" MajorFault="false" SafetyNetwork="16#0000_41a6_051c_de92">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="1" Type="PointIO" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="82">
<Data Format="L5K">
[86,864,1986065483,67167386,17121,514,1000,16842752,0,513,16842752,0,513,16842752,0,513,16842752,0,66049
		,50,0,0,0]
</Data>
</ConfigData>
<Connections>
<Connection Name="Input" RPI="10000" Type="SafetyInput" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="40.064" MaxObservedNetworkDelay="0" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_IB8S_Safety6:I:0">
<DataValueMember Name="RunMode" DataType="BOOL" Value="1" />
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt00Data" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt01Data" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt02Data" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt03Data" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt04Data" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt05Data" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt06Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt07Data" DataType="BOOL" Value="0" />
<DataValueMember Name="InputPowerStatus" DataType="BOOL" Value="0" />
<DataValueMember Name="CombinedInputStatus" DataType="BOOL" Value="1" />
</Structure>
</Data>
</InputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'DnR_Personal/TOYOTA_135453_20221024.L5X', 2),
    ],
    '1756-EN2T': [
        ('1conn', """\
<Module Name="TestMod1_1756EN2T" CatalogNumber="1756-EN2T" Vendor="1" ProductType="12" ProductCode="166" Major="11" Minor="2" ParentModule="Local" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="1" Type="ICP" Upstream="true" />
<Port Id="2" Address="192.168.1.73" Type="Ethernet" Upstream="false">
<Bus />
</Port>
</Ports>
<Communications CommMethod="536870914">
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
""", 'BAI10048_TrimmerTally_20250704.L5X', 1),
        ('1conn2', """\
<Module Name="TestMod1_1756EN2T" CatalogNumber="1756-EN2T" Vendor="1" ProductType="12" ProductCode="166" Major="11" Minor="2" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="0" Type="ICP" Upstream="false">
<Bus Size="13" />
</Port>
<Port Id="2" Address="192.168.1.73" Type="Ethernet" Upstream="true" />
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
""", 'BAI10048_TrimmerTally_20250704.L5X', 1),
        ('noconn', """\
<Module Name="TestMod1_1756EN2T" CatalogNumber="1756-EN2T" Vendor="1" ProductType="12" ProductCode="166" Major="10" Minor="3" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="1" Type="ICP" Upstream="false">
<Bus Size="10" />
</Port>
<Port Id="2" Address="192.168.1.73" Type="Ethernet" Upstream="true" />
</Ports>
<Communications CommMethod="536870914">
<Connections />
</Communications>
</Module>
""", 'L5X_Samples/Sorter1_20260722r00.L5X', 1),
    ],
    '1756-ENBT/A': [
        ('noconn', """\
<Module Name="TestMod1_1756ENBTA" CatalogNumber="1756-ENBT/A" Vendor="1" ProductType="12" ProductCode="58" Major="3" Minor="6" ParentModule="Local" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="2" Type="ICP" Upstream="true" />
<Port Id="2" Address="192.168.1.73" Type="Ethernet" Upstream="false">
<Bus />
</Port>
</Ports>
<Communications CommMethod="536870914">
<Connections />
</Communications>
</Module>
""", 'L5X_Samples/RobbinsGrn_2026_05_13r00.L5X', 1),
        ('1conn', """\
<Module Name="TestMod1_1756ENBTA" CatalogNumber="1756-ENBT/A" Vendor="1" ProductType="12" ProductCode="58" Major="6" Minor="6" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="7" Type="ICP" Upstream="false">
<Bus Size="13" />
</Port>
<Port Id="2" Address="192.168.1.73" Type="Ethernet" Upstream="true" />
</Ports>
<Communications CommMethod="805306369">
<Connections>
<Connection Name="Output" RPI="10000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1756_ENET_13SLOT:I:0">
<DataValueMember Name="SlotStatusBits" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111" />
<ArrayMember Name="Slot" DataType="AB:1756_ENET_SLOT:I:0" Dimensions="13">
<Element Index="[0]">
<Structure DataType="AB:1756_ENET_SLOT:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111" />
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
</Structure>
</Element>
<Element Index="[1]">
<Structure DataType="AB:1756_ENET_SLOT:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111" />
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
</Structure>
</Element>
<Element Index="[2]">
<Structure DataType="AB:1756_ENET_SLOT:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111" />
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
</Structure>
</Element>
<Element Index="[3]">
<Structure DataType="AB:1756_ENET_SLOT:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111" />
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
</Structure>
</Element>
<Element Index="[4]">
<Structure DataType="AB:1756_ENET_SLOT:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111" />
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
</Structure>
</Element>
<Element Index="[5]">
<Structure DataType="AB:1756_ENET_SLOT:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111" />
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
</Structure>
</Element>
<Element Index="[6]">
<Structure DataType="AB:1756_ENET_SLOT:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111" />
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
</Structure>
</Element>
<Element Index="[7]">
<Structure DataType="AB:1756_ENET_SLOT:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111" />
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
</Structure>
</Element>
<Element Index="[8]">
<Structure DataType="AB:1756_ENET_SLOT:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111" />
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
</Structure>
</Element>
<Element Index="[9]">
<Structure DataType="AB:1756_ENET_SLOT:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111" />
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
</Structure>
</Element>
<Element Index="[10]">
<Structure DataType="AB:1756_ENET_SLOT:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111" />
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
</Structure>
</Element>
<Element Index="[11]">
<Structure DataType="AB:1756_ENET_SLOT:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111" />
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
</Structure>
</Element>
<Element Index="[12]">
<Structure DataType="AB:1756_ENET_SLOT:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111" />
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
</Structure>
</Element>
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[-1,[[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0]]]
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
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
</Structure>
</Element>
<Element Index="[4]">
<Structure DataType="AB:1756_ENET_SLOT:O:0">
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
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
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
</Structure>
</Element>
<Element Index="[10]">
<Structure DataType="AB:1756_ENET_SLOT:O:0">
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
</Structure>
</Element>
<Element Index="[11]">
<Structure DataType="AB:1756_ENET_SLOT:O:0">
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
</Structure>
</Element>
<Element Index="[12]">
<Structure DataType="AB:1756_ENET_SLOT:O:0">
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
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
""", 'L5X_Samples/Sorter1_20260722r00.L5X', 1),
    ],
    '1756-IA16': [
        ('rackaliased', """\
<Module Name="TestMod1_1756IA16" CatalogNumber="1756-EN2T" Vendor="1" ProductType="12" ProductCode="166" Major="11" Minor="2" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="0" Type="ICP" Upstream="false">
<Bus Size="13" />
</Port>
<Port Id="2" Address="192.168.1.73" Type="Ethernet" Upstream="true" />
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

<Module Name="TestMod2_1756IA16" CatalogNumber="1756-IA16" Vendor="1" ProductType="7" ProductCode="9" Major="3" Minor="4" ParentModule="TestMod1_1756IA16" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="5" Type="ICP" Upstream="true" />
</Ports>
<Communications CommMethod="1073741824">
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
<RackConnection>
<InAliasTag />
</RackConnection>
</Connections>
</Communications>
</Module>
""", 'BAI10048_TrimmerTally_20250704.L5X', 2),
        ('1conn', """\
<Module Name="TestMod1_1756IA16" CatalogNumber="1756-IA16" Vendor="1" ProductType="7" ProductCode="9" Major="2" Minor="5" ParentModule="Local" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="13" Type="ICP" Upstream="true" />
</Ports>
<Communications CommMethod="536870913">
<ConfigTag ConfigSize="24" ExternalAccess="Read/Write">
<Data Format="L5K">
[28,16,1,0,0,0,1,9,1,9,0,0,0,0,65535,65535]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1756_DI:C:0">
<DataValueMember Name="DiagCOSDisable" DataType="BOOL" Value="0" />
<DataValueMember Name="FilterOffOn_0_7" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="FilterOnOff_0_7" DataType="SINT" Radix="Decimal" Value="9" />
<DataValueMember Name="FilterOffOn_8_15" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="FilterOnOff_8_15" DataType="SINT" Radix="Decimal" Value="9" />
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
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_1001_0000_0011_1000" />
</Structure>
</Data>
</InputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'L5X_Samples/RobbinsGrn_2026_05_13r00.L5X', 1),
    ],
    '1756-IB32/B': [
        ('1conn', """\
<Module Name="TestMod1_1756IB32B" CatalogNumber="1756-IB32/B" Vendor="1" ProductType="7" ProductCode="12" Major="3" Minor="6" ParentModule="Local" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="4" Type="ICP" Upstream="true" />
</Ports>
<Communications CommMethod="536870913">
<ConfigTag ConfigSize="24" ExternalAccess="Read/Write">
<Data Format="L5K">
[28,16,0,0,0,0,1,1,1,1,1,1,1,1,-1,-1]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1756_DI:C:1">
<DataValueMember Name="FilterOffOn_0_7" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="FilterOnOff_0_7" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="FilterOffOn_8_15" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="FilterOnOff_8_15" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="FilterOffOn_16_23" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="FilterOnOff_16_23" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="FilterOffOn_24_31" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="FilterOnOff_24_31" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="COSOnOffEn" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111" />
<DataValueMember Name="COSOffOnEn" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="StandardInput" RPI="500" Type="Input" EventID="0" ProgrammaticallySendEventTrigger="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1756_DI:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#1100_0011_0000_0000_1000_0000_0000_0001" />
</Structure>
</Data>
</InputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'BAI10048_TrimmerTally_20250704.L5X', 1),
        ('rackaliased', """\
<Module Name="TestMod1_1756IB32B" CatalogNumber="1756-EN2T" Vendor="1" ProductType="12" ProductCode="166" Major="11" Minor="2" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="0" Type="ICP" Upstream="false">
<Bus Size="13" />
</Port>
<Port Id="2" Address="192.168.1.73" Type="Ethernet" Upstream="true" />
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

<Module Name="TestMod2_1756IB32B" CatalogNumber="1756-IB32/B" Vendor="1" ProductType="7" ProductCode="12" Major="3" Minor="6" ParentModule="TestMod1_1756IB32B" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="1" Type="ICP" Upstream="true" />
</Ports>
<Communications CommMethod="1073741824">
<ConfigTag ConfigSize="24" ExternalAccess="Read/Write">
<Data Format="L5K">
[28,16,0,0,0,0,1,1,1,1,1,1,1,1,-1,-1]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1756_DI:C:1">
<DataValueMember Name="FilterOffOn_0_7" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="FilterOnOff_0_7" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="FilterOffOn_8_15" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="FilterOnOff_8_15" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="FilterOffOn_16_23" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="FilterOnOff_16_23" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="FilterOffOn_24_31" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="FilterOnOff_24_31" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="COSOnOffEn" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111" />
<DataValueMember Name="COSOffOnEn" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111" />
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
""", 'BAI10048_TrimmerTally_20250704.L5X', 2),
    ],
    '1756-OB16E': [
        ('1conn', """\
<Module Name="TestMod1_1756OB16E" CatalogNumber="1756-OB16E" Vendor="1" ProductType="7" ProductCode="16" Major="2" Minor="4" ParentModule="Local" ParentModPortId="1" Inhibited="false" MajorFault="false" AutoDiagsEnabled="true">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="6" Type="ICP" Upstream="true" />
</Ports>
<Communications CommMethod="536870914">
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
<Connection Name="Fused" RPI="20000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1756_DO_Fused:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_1100_1000" />
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
[200]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1756_DO:O:0">
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_1100_1000" />
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'BAI10048_TrimmerTally_20250704.L5X', 1),
        ('rackaliased', """\
<Module Name="TestMod1_1756OB16E" CatalogNumber="1756-EN2T" Vendor="1" ProductType="12" ProductCode="166" Major="11" Minor="2" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="0" Type="ICP" Upstream="false">
<Bus Size="13" />
</Port>
<Port Id="2" Address="192.168.1.73" Type="Ethernet" Upstream="true" />
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

<Module Name="TestMod2_1756OB16E" CatalogNumber="1756-OB16E" Vendor="1" ProductType="7" ProductCode="16" Major="3" Minor="4" ParentModule="TestMod1_1756OB16E" ParentModPortId="1" Inhibited="false" MajorFault="false" AutoDiagsEnabled="true">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="4" Type="ICP" Upstream="true" />
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
    ],
    '1756-OB32': [
        ('rackaliased', """\
<Module Name="TestMod1_1756OB32" CatalogNumber="1756-EN2T" Vendor="1" ProductType="12" ProductCode="166" Major="11" Minor="2" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="0" Type="ICP" Upstream="false">
<Bus Size="13" />
</Port>
<Port Id="2" Address="192.168.1.73" Type="Ethernet" Upstream="true" />
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

<Module Name="TestMod2_1756OB32" CatalogNumber="1756-OB32" Vendor="1" ProductType="7" ProductCode="17" Major="3" Minor="3" ParentModule="TestMod1_1756OB32" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="3" Type="ICP" Upstream="true" />
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
        ('1conn', """\
<Module Name="TestMod1_1756OB32" CatalogNumber="1756-OB32" Vendor="1" ProductType="7" ProductCode="17" Major="3" Minor="1" ParentModule="Local" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="4" Type="ICP" Upstream="true" />
</Ports>
<Communications CommMethod="536870913">
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
<Connection Name="Standard" RPI="20000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1756_DO:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0010_0001" />
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[33]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1756_DO:O:0">
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0010_0001" />
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'L5X_Samples/Sorter1_20260722r00.L5X', 1),
    ],
    '2198-D012-ERS3': [
        ('4conn', """\
<Module Name="TestMod1_2198D012ERS3" CatalogNumber="2198-D012-ERS3" Vendor="1" ProductType="45" ProductCode="11" Major="14" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false" SafetyNetwork="16#0000_4cd3_03df_cbbd" SafetyEnabled="true">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="2" Address="192.168.1.73" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="468">
<Data Format="L5K">
[472,7,1793,11,434110479,18,10000,33686020,5,0,0,0,0,0,0,0,0,-1027080192,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,33686018,33686018
		,67108864,460,1,1045220557,0,0,0,0,1120403456,1120403456,0,1120403456,1124859904,0,0,1120403456,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,262148,0,50528513,0,0,0,8192000,8192125,67305985,0,0,0,67305985,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,50987786,0,655370,0]
</Data>
</ConfigData>
<SafetyScript Size="353">
<Data Format="L5K">
[93,1,0,0,5,0,0,0,0,0,0,0,0,0,0,0,77,1,0,0,0,0,0,0,0,3,0,0,0,63,1,0,0,0,0,0,56,1,0,0,102,0,0,0,92,-1,104,-115,-103,-46,98,4,-45,76,0,0,0,0,0
		,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-128,63,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-128,63
		,1,1,1,1,0,0,1,0,0,0,-128,63,1,0,0,0,-1,-1,121,-60,0,0,0,0,1,0,0,0,1,0,0,0,0,0,1,0,0,0,-128,63,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,1,0,0,0,0,0,-128,63
		,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-128,63,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,-128,63,1,1,1,1,0,0,1,0,0,0,-128,63,1,0,0,0,-1,-1,121,-60,0,0,0,0,1,0,0,0,1,0,0,0,0,0,1,0,0,0,-128,63,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0
		,1,0,0,0,0,0,-128,63,0,0,0,0,0,0,1,0,0]
</Data>
</SafetyScript>
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
<DataValueMember Name="ControllerToDriveConnectionSize" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="DriveToControllerConnectionSize" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="NominalControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="NominalDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="CoarseUpdatePeriod" DataType="INT" Radix="Decimal" Value="0" />
</Structure>
</Data>
</InputTag>
</Connection>
<Connection Name="B_MotionSync2" RPI="2000" Type="MotionSync" EventID="0" ProgrammaticallySendEventTrigger="false" />
<Connection Name="C_Safety_Output2" RPI="20000" Type="SafetyOutputDataDriven" OutputSize="28" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="60" MaxObservedNetworkDelay="0" Priority="High" InputConnectionType="Unicast" InputProductionTrigger="Application" ConnectionPath="20 04 24 66 20 04 25 00 02 03 20 04 24 c7" OutputTagSuffix="SO">
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:CIP_Motion_Device_Safety2:SO:0">
<DataValueMember Name="PassThruDataA1" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="PassThruDataB1" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="PassThruDataA2" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="PassThruDataB2" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="PassThruStopStatus1" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SBCIntegrity1" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCActive1" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCBrakeEngaged1" DataType="BOOL" Value="0" />
<DataValueMember Name="SS1Active1" DataType="BOOL" Value="0" />
<DataValueMember Name="SS2Active1" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSActive1" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSStandstill1" DataType="BOOL" Value="0" />
<DataValueMember Name="PassThruSpeedLimitStatus1" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SSMActive1" DataType="BOOL" Value="0" />
<DataValueMember Name="SSMStatus1" DataType="BOOL" Value="0" />
<DataValueMember Name="SLSActive1" DataType="BOOL" Value="0" />
<DataValueMember Name="SLSLimit1" DataType="BOOL" Value="0" />
<DataValueMember Name="SDIActive1" DataType="BOOL" Value="0" />
<DataValueMember Name="SDILimit1" DataType="BOOL" Value="0" />
<DataValueMember Name="PassThruPositionLimitStatus1" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SCAActive1" DataType="BOOL" Value="0" />
<DataValueMember Name="SCAStatus1" DataType="BOOL" Value="0" />
<DataValueMember Name="SLPActive1" DataType="BOOL" Value="0" />
<DataValueMember Name="SLPLimit1" DataType="BOOL" Value="0" />
<DataValueMember Name="SFHomed1" DataType="BOOL" Value="0" />
<DataValueMember Name="PassThruStopFaults1" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SFXFault1" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCFault1" DataType="BOOL" Value="0" />
<DataValueMember Name="SS1Fault1" DataType="BOOL" Value="0" />
<DataValueMember Name="SS2Fault1" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSFault1" DataType="BOOL" Value="0" />
<DataValueMember Name="PassThruLimitFaults1" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SSMFault1" DataType="BOOL" Value="0" />
<DataValueMember Name="SLSFault1" DataType="BOOL" Value="0" />
<DataValueMember Name="SDIFault1" DataType="BOOL" Value="0" />
<DataValueMember Name="SCAFault1" DataType="BOOL" Value="0" />
<DataValueMember Name="SLPFault1" DataType="BOOL" Value="0" />
<DataValueMember Name="SafetyStopFunctions1" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="STOOutput1" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCOutput1" DataType="BOOL" Value="0" />
<DataValueMember Name="SS1Request1" DataType="BOOL" Value="0" />
<DataValueMember Name="SS2Request1" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSRequest1" DataType="BOOL" Value="0" />
<DataValueMember Name="SMTRequest1" DataType="BOOL" Value="0" />
<DataValueMember Name="ResetRequest1" DataType="BOOL" Value="0" />
<DataValueMember Name="PassThruStopStatus2" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SBCIntegrity2" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCActive2" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCBrakeEngaged2" DataType="BOOL" Value="0" />
<DataValueMember Name="SS1Active2" DataType="BOOL" Value="0" />
<DataValueMember Name="SS2Active2" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSActive2" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSStandstill2" DataType="BOOL" Value="0" />
<DataValueMember Name="PassThruSpeedLimitStatus2" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SSMActive2" DataType="BOOL" Value="0" />
<DataValueMember Name="SSMStatus2" DataType="BOOL" Value="0" />
<DataValueMember Name="SLSActive2" DataType="BOOL" Value="0" />
<DataValueMember Name="SLSLimit2" DataType="BOOL" Value="0" />
<DataValueMember Name="SDIActive2" DataType="BOOL" Value="0" />
<DataValueMember Name="SDILimit2" DataType="BOOL" Value="0" />
<DataValueMember Name="PassThruPositionLimitStatus2" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SCAActive2" DataType="BOOL" Value="0" />
<DataValueMember Name="SCAStatus2" DataType="BOOL" Value="0" />
<DataValueMember Name="SLPActive2" DataType="BOOL" Value="0" />
<DataValueMember Name="SLPLimit2" DataType="BOOL" Value="0" />
<DataValueMember Name="SFHomed2" DataType="BOOL" Value="0" />
<DataValueMember Name="PassThruStopFaults2" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SFXFault2" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCFault2" DataType="BOOL" Value="0" />
<DataValueMember Name="SS1Fault2" DataType="BOOL" Value="0" />
<DataValueMember Name="SS2Fault2" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSFault2" DataType="BOOL" Value="0" />
<DataValueMember Name="PassThruLimitFaults2" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SSMFault2" DataType="BOOL" Value="0" />
<DataValueMember Name="SLSFault2" DataType="BOOL" Value="0" />
<DataValueMember Name="SDIFault2" DataType="BOOL" Value="0" />
<DataValueMember Name="SCAFault2" DataType="BOOL" Value="0" />
<DataValueMember Name="SLPFault2" DataType="BOOL" Value="0" />
<DataValueMember Name="SafetyStopFunctions2" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="STOOutput2" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCOutput2" DataType="BOOL" Value="0" />
<DataValueMember Name="SS1Request2" DataType="BOOL" Value="0" />
<DataValueMember Name="SS2Request2" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSRequest2" DataType="BOOL" Value="0" />
<DataValueMember Name="SMTRequest2" DataType="BOOL" Value="0" />
<DataValueMember Name="ResetRequest2" DataType="BOOL" Value="0" />
</Structure>
</Data>
</OutputTag>
</Connection>
<Connection Name="D_Safety_Input2" RPI="10000" Type="SafetyInputDataDriven" InputSize="44" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="40.064" MaxObservedNetworkDelay="0" Priority="High" InputConnectionType="Unicast" InputProductionTrigger="Application" ConnectionPath="20 04 24 66 20 04 24 c7 20 04 25 00 02 04" InputTagSuffix="SI">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:CIP_Motion_Device_Safety2:SI:0">
<DataValueMember Name="ConnectionStatus" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="RunMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="0" />
<DataValueMember Name="FeedbackPosition1" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="FeedbackVelocity1" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="SecondaryFeedbackPosition1" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="SecondaryFeedbackVelocity1" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="FeedbackPosition2" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="FeedbackVelocity2" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="SecondaryFeedbackPosition2" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="SecondaryFeedbackVelocity2" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="StopStatus1" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="STOActive1" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCActive1" DataType="BOOL" Value="0" />
<DataValueMember Name="SS1Active1" DataType="BOOL" Value="0" />
<DataValueMember Name="SS2Active1" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSStandstill1" DataType="BOOL" Value="0" />
<DataValueMember Name="SMTOvertemp1" DataType="BOOL" Value="0" />
<DataValueMember Name="SafetyFault1" DataType="BOOL" Value="0" />
<DataValueMember Name="RestartRequired1" DataType="BOOL" Value="0" />
<DataValueMember Name="SafeStatus1" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="TorqueDisabled1" DataType="BOOL" Value="0" />
<DataValueMember Name="BrakeEngaged1" DataType="BOOL" Value="0" />
<DataValueMember Name="MotionStatus1" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="MotionPositive1" DataType="BOOL" Value="0" />
<DataValueMember Name="MotionNegative1" DataType="BOOL" Value="0" />
<DataValueMember Name="FunctionSupport1" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="PrimaryFeedbackValid1" DataType="BOOL" Value="0" />
<DataValueMember Name="SecondaryFeedbackValid1" DataType="BOOL" Value="0" />
<DataValueMember Name="DiscrepancyCheckingActive1" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCReady1" DataType="BOOL" Value="0" />
<DataValueMember Name="SS1Ready1" DataType="BOOL" Value="0" />
<DataValueMember Name="SS2Ready1" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSReady1" DataType="BOOL" Value="0" />
<DataValueMember Name="SMTReady1" DataType="BOOL" Value="0" />
<DataValueMember Name="StopStatus2" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="STOActive2" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCActive2" DataType="BOOL" Value="0" />
<DataValueMember Name="SS1Active2" DataType="BOOL" Value="0" />
<DataValueMember Name="SS2Active2" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSStandstill2" DataType="BOOL" Value="0" />
<DataValueMember Name="SMTOvertemp2" DataType="BOOL" Value="0" />
<DataValueMember Name="SafetyFault2" DataType="BOOL" Value="0" />
<DataValueMember Name="RestartRequired2" DataType="BOOL" Value="0" />
<DataValueMember Name="SafeStatus2" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="TorqueDisabled2" DataType="BOOL" Value="0" />
<DataValueMember Name="BrakeEngaged2" DataType="BOOL" Value="0" />
<DataValueMember Name="MotionStatus2" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="MotionPositive2" DataType="BOOL" Value="0" />
<DataValueMember Name="MotionNegative2" DataType="BOOL" Value="0" />
<DataValueMember Name="FunctionSupport2" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="PrimaryFeedbackValid2" DataType="BOOL" Value="0" />
<DataValueMember Name="SecondaryFeedbackValid2" DataType="BOOL" Value="0" />
<DataValueMember Name="DiscrepancyCheckingActive2" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCReady2" DataType="BOOL" Value="0" />
<DataValueMember Name="SS1Ready2" DataType="BOOL" Value="0" />
<DataValueMember Name="SS2Ready2" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSReady2" DataType="BOOL" Value="0" />
<DataValueMember Name="SMTReady2" DataType="BOOL" Value="0" />
</Structure>
</Data>
</InputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'SJ_Gormley_20251112_r02.L5X', 1),
        ('2conn', """\
<Module Name="TestMod1_2198D012ERS3" CatalogNumber="2198-D012-ERS3" Vendor="1" ProductType="45" ProductCode="11" Major="14" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false" SafetyEnabled="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="2" Address="192.168.1.73" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="468">
<Data Format="L5K">
[472,7,1793,11,434110479,18,10000,33686020,5,0,0,0,0,0,0,0,0,-1027080192,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,33686018,33686018
		,67108864,460,1,1045220557,0,0,0,0,1120403456,1120403456,0,1120403456,1124859904,0,0,1120403456,1,0
		,3,0,0,0,0,0,1,0,0,0,3,0,0,0,0,0,0,0,0,0,0,0,262148,0,50528513,0,0,0,8192000,8192125,67305985,0,0,0,67305985,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,50987786,0,655370,0]
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
<DataValueMember Name="ControllerToDriveConnectionSize" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="DriveToControllerConnectionSize" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="NominalControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="NominalDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="CoarseUpdatePeriod" DataType="INT" Radix="Decimal" Value="0" />
</Structure>
</Data>
</InputTag>
</Connection>
<Connection Name="B_MotionSync2" RPI="2000" Type="MotionSync" EventID="0" ProgrammaticallySendEventTrigger="false" />
</Connections>
</Communications>
</Module>
""", 'motion_p208/p208_D012_NodeAndAxisDual3.L5X', 1),
    ],
    '2198-D020-ERS3': [
        ('4conn', """\
<Module Name="TestMod1_2198D020ERS3" CatalogNumber="2198-D020-ERS3" Vendor="1" ProductType="45" ProductCode="12" Major="14" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false" SafetyNetwork="16#0000_4cd3_03df_cbbd" SafetyEnabled="true">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="2" Address="192.168.1.73" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="468">
<Data Format="L5K">
[472,7,1793,12,434110479,18,10000,33686020,5,0,0,0,0,0,0,0,0,-1027080192,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,33686018,33686018
		,67108864,460,1,1045220557,0,0,0,0,1120403456,1120403456,0,1120403456,1124859904,0,0,1120403456,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,262148,0,50528513,0,0,0,8192000,8192125,67305985,0,0,0,67305985,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,50987786,0,655370,0]
</Data>
</ConfigData>
<SafetyScript Size="353">
<Data Format="L5K">
[93,1,0,0,5,0,0,0,0,0,0,0,0,0,0,0,77,1,0,0,0,0,0,0,0,3,0,0,0,63,1,0,0,0,0,0,56,1,0,0,102,0,0,0,92,-1,104,-115,-119,112,98,4,-45,76,0,0,0,0,0
		,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-128,63,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-128,63
		,1,1,1,1,0,0,1,0,0,0,-128,63,1,0,0,0,-1,-1,121,-60,0,0,0,0,1,0,0,0,1,0,0,0,0,0,1,0,0,0,-128,63,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,1,0,0,0,0,0,-128,63
		,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-128,63,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,-128,63,1,1,1,1,0,0,1,0,0,0,-128,63,1,0,0,0,-1,-1,121,-60,0,0,0,0,1,0,0,0,1,0,0,0,0,0,1,0,0,0,-128,63,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0
		,1,0,0,0,0,0,-128,63,0,0,0,0,0,0,1,0,0]
</Data>
</SafetyScript>
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
<DataValueMember Name="ControllerToDriveConnectionSize" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="DriveToControllerConnectionSize" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="NominalControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="NominalDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="CoarseUpdatePeriod" DataType="INT" Radix="Decimal" Value="0" />
</Structure>
</Data>
</InputTag>
</Connection>
<Connection Name="B_MotionSync2" RPI="2000" Type="MotionSync" EventID="0" ProgrammaticallySendEventTrigger="false" />
<Connection Name="C_Safety_Output2" RPI="20000" Type="SafetyOutputDataDriven" OutputSize="28" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="60" MaxObservedNetworkDelay="0" Priority="High" InputConnectionType="Unicast" InputProductionTrigger="Application" ConnectionPath="20 04 24 66 20 04 25 00 02 03 20 04 24 c7" OutputTagSuffix="SO">
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:CIP_Motion_Device_Safety2:SO:0">
<DataValueMember Name="PassThruDataA1" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="PassThruDataB1" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="PassThruDataA2" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="PassThruDataB2" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="PassThruStopStatus1" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SBCIntegrity1" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCActive1" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCBrakeEngaged1" DataType="BOOL" Value="0" />
<DataValueMember Name="SS1Active1" DataType="BOOL" Value="0" />
<DataValueMember Name="SS2Active1" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSActive1" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSStandstill1" DataType="BOOL" Value="0" />
<DataValueMember Name="PassThruSpeedLimitStatus1" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SSMActive1" DataType="BOOL" Value="0" />
<DataValueMember Name="SSMStatus1" DataType="BOOL" Value="0" />
<DataValueMember Name="SLSActive1" DataType="BOOL" Value="0" />
<DataValueMember Name="SLSLimit1" DataType="BOOL" Value="0" />
<DataValueMember Name="SDIActive1" DataType="BOOL" Value="0" />
<DataValueMember Name="SDILimit1" DataType="BOOL" Value="0" />
<DataValueMember Name="PassThruPositionLimitStatus1" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SCAActive1" DataType="BOOL" Value="0" />
<DataValueMember Name="SCAStatus1" DataType="BOOL" Value="0" />
<DataValueMember Name="SLPActive1" DataType="BOOL" Value="0" />
<DataValueMember Name="SLPLimit1" DataType="BOOL" Value="0" />
<DataValueMember Name="SFHomed1" DataType="BOOL" Value="0" />
<DataValueMember Name="PassThruStopFaults1" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SFXFault1" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCFault1" DataType="BOOL" Value="0" />
<DataValueMember Name="SS1Fault1" DataType="BOOL" Value="0" />
<DataValueMember Name="SS2Fault1" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSFault1" DataType="BOOL" Value="0" />
<DataValueMember Name="PassThruLimitFaults1" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SSMFault1" DataType="BOOL" Value="0" />
<DataValueMember Name="SLSFault1" DataType="BOOL" Value="0" />
<DataValueMember Name="SDIFault1" DataType="BOOL" Value="0" />
<DataValueMember Name="SCAFault1" DataType="BOOL" Value="0" />
<DataValueMember Name="SLPFault1" DataType="BOOL" Value="0" />
<DataValueMember Name="SafetyStopFunctions1" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="STOOutput1" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCOutput1" DataType="BOOL" Value="0" />
<DataValueMember Name="SS1Request1" DataType="BOOL" Value="0" />
<DataValueMember Name="SS2Request1" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSRequest1" DataType="BOOL" Value="0" />
<DataValueMember Name="SMTRequest1" DataType="BOOL" Value="0" />
<DataValueMember Name="ResetRequest1" DataType="BOOL" Value="0" />
<DataValueMember Name="PassThruStopStatus2" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SBCIntegrity2" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCActive2" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCBrakeEngaged2" DataType="BOOL" Value="0" />
<DataValueMember Name="SS1Active2" DataType="BOOL" Value="0" />
<DataValueMember Name="SS2Active2" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSActive2" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSStandstill2" DataType="BOOL" Value="0" />
<DataValueMember Name="PassThruSpeedLimitStatus2" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SSMActive2" DataType="BOOL" Value="0" />
<DataValueMember Name="SSMStatus2" DataType="BOOL" Value="0" />
<DataValueMember Name="SLSActive2" DataType="BOOL" Value="0" />
<DataValueMember Name="SLSLimit2" DataType="BOOL" Value="0" />
<DataValueMember Name="SDIActive2" DataType="BOOL" Value="0" />
<DataValueMember Name="SDILimit2" DataType="BOOL" Value="0" />
<DataValueMember Name="PassThruPositionLimitStatus2" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SCAActive2" DataType="BOOL" Value="0" />
<DataValueMember Name="SCAStatus2" DataType="BOOL" Value="0" />
<DataValueMember Name="SLPActive2" DataType="BOOL" Value="0" />
<DataValueMember Name="SLPLimit2" DataType="BOOL" Value="0" />
<DataValueMember Name="SFHomed2" DataType="BOOL" Value="0" />
<DataValueMember Name="PassThruStopFaults2" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SFXFault2" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCFault2" DataType="BOOL" Value="0" />
<DataValueMember Name="SS1Fault2" DataType="BOOL" Value="0" />
<DataValueMember Name="SS2Fault2" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSFault2" DataType="BOOL" Value="0" />
<DataValueMember Name="PassThruLimitFaults2" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SSMFault2" DataType="BOOL" Value="0" />
<DataValueMember Name="SLSFault2" DataType="BOOL" Value="0" />
<DataValueMember Name="SDIFault2" DataType="BOOL" Value="0" />
<DataValueMember Name="SCAFault2" DataType="BOOL" Value="0" />
<DataValueMember Name="SLPFault2" DataType="BOOL" Value="0" />
<DataValueMember Name="SafetyStopFunctions2" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="STOOutput2" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCOutput2" DataType="BOOL" Value="0" />
<DataValueMember Name="SS1Request2" DataType="BOOL" Value="0" />
<DataValueMember Name="SS2Request2" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSRequest2" DataType="BOOL" Value="0" />
<DataValueMember Name="SMTRequest2" DataType="BOOL" Value="0" />
<DataValueMember Name="ResetRequest2" DataType="BOOL" Value="0" />
</Structure>
</Data>
</OutputTag>
</Connection>
<Connection Name="D_Safety_Input2" RPI="10000" Type="SafetyInputDataDriven" InputSize="44" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="40.064" MaxObservedNetworkDelay="0" Priority="High" InputConnectionType="Unicast" InputProductionTrigger="Application" ConnectionPath="20 04 24 66 20 04 24 c7 20 04 25 00 02 04" InputTagSuffix="SI">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:CIP_Motion_Device_Safety2:SI:0">
<DataValueMember Name="ConnectionStatus" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="RunMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="0" />
<DataValueMember Name="FeedbackPosition1" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="FeedbackVelocity1" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="SecondaryFeedbackPosition1" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="SecondaryFeedbackVelocity1" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="FeedbackPosition2" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="FeedbackVelocity2" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="SecondaryFeedbackPosition2" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="SecondaryFeedbackVelocity2" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="StopStatus1" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="STOActive1" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCActive1" DataType="BOOL" Value="0" />
<DataValueMember Name="SS1Active1" DataType="BOOL" Value="0" />
<DataValueMember Name="SS2Active1" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSStandstill1" DataType="BOOL" Value="0" />
<DataValueMember Name="SMTOvertemp1" DataType="BOOL" Value="0" />
<DataValueMember Name="SafetyFault1" DataType="BOOL" Value="0" />
<DataValueMember Name="RestartRequired1" DataType="BOOL" Value="0" />
<DataValueMember Name="SafeStatus1" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="TorqueDisabled1" DataType="BOOL" Value="0" />
<DataValueMember Name="BrakeEngaged1" DataType="BOOL" Value="0" />
<DataValueMember Name="MotionStatus1" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="MotionPositive1" DataType="BOOL" Value="0" />
<DataValueMember Name="MotionNegative1" DataType="BOOL" Value="0" />
<DataValueMember Name="FunctionSupport1" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="PrimaryFeedbackValid1" DataType="BOOL" Value="0" />
<DataValueMember Name="SecondaryFeedbackValid1" DataType="BOOL" Value="0" />
<DataValueMember Name="DiscrepancyCheckingActive1" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCReady1" DataType="BOOL" Value="0" />
<DataValueMember Name="SS1Ready1" DataType="BOOL" Value="0" />
<DataValueMember Name="SS2Ready1" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSReady1" DataType="BOOL" Value="0" />
<DataValueMember Name="SMTReady1" DataType="BOOL" Value="0" />
<DataValueMember Name="StopStatus2" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="STOActive2" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCActive2" DataType="BOOL" Value="0" />
<DataValueMember Name="SS1Active2" DataType="BOOL" Value="0" />
<DataValueMember Name="SS2Active2" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSStandstill2" DataType="BOOL" Value="0" />
<DataValueMember Name="SMTOvertemp2" DataType="BOOL" Value="0" />
<DataValueMember Name="SafetyFault2" DataType="BOOL" Value="0" />
<DataValueMember Name="RestartRequired2" DataType="BOOL" Value="0" />
<DataValueMember Name="SafeStatus2" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="TorqueDisabled2" DataType="BOOL" Value="0" />
<DataValueMember Name="BrakeEngaged2" DataType="BOOL" Value="0" />
<DataValueMember Name="MotionStatus2" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="MotionPositive2" DataType="BOOL" Value="0" />
<DataValueMember Name="MotionNegative2" DataType="BOOL" Value="0" />
<DataValueMember Name="FunctionSupport2" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="PrimaryFeedbackValid2" DataType="BOOL" Value="0" />
<DataValueMember Name="SecondaryFeedbackValid2" DataType="BOOL" Value="0" />
<DataValueMember Name="DiscrepancyCheckingActive2" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCReady2" DataType="BOOL" Value="0" />
<DataValueMember Name="SS1Ready2" DataType="BOOL" Value="0" />
<DataValueMember Name="SS2Ready2" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSReady2" DataType="BOOL" Value="0" />
<DataValueMember Name="SMTReady2" DataType="BOOL" Value="0" />
</Structure>
</Data>
</InputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'SJ_Gormley_20251112_r02.L5X', 1),
        ('2conn', """\
<Module Name="TestMod1_2198D020ERS3" CatalogNumber="2198-D020-ERS3" Vendor="1" ProductType="45" ProductCode="12" Major="14" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false" SafetyEnabled="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="2" Address="192.168.1.73" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="468">
<Data Format="L5K">
[472,7,1793,12,434110479,18,10000,33686020,5,0,0,0,0,0,0,0,0,-1027080192,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,33686018,33686018
		,67108864,460,1,1045220557,0,0,0,0,1120403456,1120403456,0,1120403456,1124859904,0,0,1120403456,2,0
		,4,0,0,0,0,0,2,0,0,0,4,0,0,0,0,0,0,0,0,0,0,0,262148,0,50528513,0,0,0,8192000,8192125,67305985,0,0,0,67305985,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,50987786,0,655370,0]
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
<DataValueMember Name="ControllerToDriveConnectionSize" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="DriveToControllerConnectionSize" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="NominalControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="NominalDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="CoarseUpdatePeriod" DataType="INT" Radix="Decimal" Value="0" />
</Structure>
</Data>
</InputTag>
</Connection>
<Connection Name="B_MotionSync2" RPI="8000" Type="MotionSync" EventID="0" ProgrammaticallySendEventTrigger="false" />
</Connections>
</Communications>
</Module>
""", 'BaillieLeitchField_Edger_20260812_r00.L5X', 1),
    ],
    '2198-D032-ERS3': [
        ('4conn', """\
<Module Name="TestMod1_2198D032ERS3" CatalogNumber="2198-D032-ERS3" Vendor="1" ProductType="45" ProductCode="13" Major="14" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false" SafetyNetwork="16#0000_4cd3_03df_cbbd" SafetyEnabled="true">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="2" Address="192.168.1.73" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="468">
<Data Format="L5K">
[472,7,1793,13,434110479,18,10000,33686020,5,0,0,0,0,0,0,0,0,-1027080192,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,33686018,33686018
		,67108864,460,1,1045220557,0,0,0,0,1120403456,1120403456,0,1120403456,1124859904,0,0,1120403456,0,0
		,3,0,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,0,0,262148,0,50528513,0,0,0,8192000,8192125,67305985,0,0,0,67305985,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,50987786,0,655370,0]
</Data>
</ConfigData>
<SafetyScript Size="353">
<Data Format="L5K">
[93,1,0,0,5,0,0,0,0,0,0,0,0,0,0,0,77,1,0,0,0,0,0,0,0,3,0,0,0,63,1,0,0,0,0,0,56,1,0,0,102,0,0,0,92,-1,104,-115,-106,15,97,4,-45,76,0,0,0,0,0,0
		,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-128,63,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-128,63,1
		,1,1,1,0,0,1,0,0,0,-128,63,1,0,0,0,-1,-1,121,-60,0,0,0,0,1,0,0,0,1,0,0,0,0,0,1,0,0,0,-128,63,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,1,0,0,0,0,0,-128,63
		,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-128,63,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,-128,63,1,1,1,1,0,0,1,0,0,0,-128,63,1,0,0,0,-1,-1,121,-60,0,0,0,0,1,0,0,0,1,0,0,0,0,0,1,0,0,0,-128,63,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0
		,1,0,0,0,0,0,-128,63,0,0,0,0,0,0,1,0,0]
</Data>
</SafetyScript>
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
<DataValueMember Name="ControllerToDriveConnectionSize" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="DriveToControllerConnectionSize" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="NominalControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="NominalDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="CoarseUpdatePeriod" DataType="INT" Radix="Decimal" Value="0" />
</Structure>
</Data>
</InputTag>
</Connection>
<Connection Name="B_MotionSync2" RPI="2000" Type="MotionSync" EventID="0" ProgrammaticallySendEventTrigger="false" />
<Connection Name="C_Safety_Output2" RPI="20000" Type="SafetyOutputDataDriven" OutputSize="28" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="60" MaxObservedNetworkDelay="0" Priority="High" InputConnectionType="Unicast" InputProductionTrigger="Application" ConnectionPath="20 04 24 66 20 04 25 00 02 03 20 04 24 c7" OutputTagSuffix="SO">
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:CIP_Motion_Device_Safety2:SO:0">
<DataValueMember Name="PassThruDataA1" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="PassThruDataB1" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="PassThruDataA2" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="PassThruDataB2" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="PassThruStopStatus1" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SBCIntegrity1" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCActive1" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCBrakeEngaged1" DataType="BOOL" Value="0" />
<DataValueMember Name="SS1Active1" DataType="BOOL" Value="0" />
<DataValueMember Name="SS2Active1" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSActive1" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSStandstill1" DataType="BOOL" Value="0" />
<DataValueMember Name="PassThruSpeedLimitStatus1" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SSMActive1" DataType="BOOL" Value="0" />
<DataValueMember Name="SSMStatus1" DataType="BOOL" Value="0" />
<DataValueMember Name="SLSActive1" DataType="BOOL" Value="0" />
<DataValueMember Name="SLSLimit1" DataType="BOOL" Value="0" />
<DataValueMember Name="SDIActive1" DataType="BOOL" Value="0" />
<DataValueMember Name="SDILimit1" DataType="BOOL" Value="0" />
<DataValueMember Name="PassThruPositionLimitStatus1" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SCAActive1" DataType="BOOL" Value="0" />
<DataValueMember Name="SCAStatus1" DataType="BOOL" Value="0" />
<DataValueMember Name="SLPActive1" DataType="BOOL" Value="0" />
<DataValueMember Name="SLPLimit1" DataType="BOOL" Value="0" />
<DataValueMember Name="SFHomed1" DataType="BOOL" Value="0" />
<DataValueMember Name="PassThruStopFaults1" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SFXFault1" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCFault1" DataType="BOOL" Value="0" />
<DataValueMember Name="SS1Fault1" DataType="BOOL" Value="0" />
<DataValueMember Name="SS2Fault1" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSFault1" DataType="BOOL" Value="0" />
<DataValueMember Name="PassThruLimitFaults1" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SSMFault1" DataType="BOOL" Value="0" />
<DataValueMember Name="SLSFault1" DataType="BOOL" Value="0" />
<DataValueMember Name="SDIFault1" DataType="BOOL" Value="0" />
<DataValueMember Name="SCAFault1" DataType="BOOL" Value="0" />
<DataValueMember Name="SLPFault1" DataType="BOOL" Value="0" />
<DataValueMember Name="SafetyStopFunctions1" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="STOOutput1" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCOutput1" DataType="BOOL" Value="0" />
<DataValueMember Name="SS1Request1" DataType="BOOL" Value="0" />
<DataValueMember Name="SS2Request1" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSRequest1" DataType="BOOL" Value="0" />
<DataValueMember Name="SMTRequest1" DataType="BOOL" Value="0" />
<DataValueMember Name="ResetRequest1" DataType="BOOL" Value="0" />
<DataValueMember Name="PassThruStopStatus2" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SBCIntegrity2" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCActive2" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCBrakeEngaged2" DataType="BOOL" Value="0" />
<DataValueMember Name="SS1Active2" DataType="BOOL" Value="0" />
<DataValueMember Name="SS2Active2" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSActive2" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSStandstill2" DataType="BOOL" Value="0" />
<DataValueMember Name="PassThruSpeedLimitStatus2" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SSMActive2" DataType="BOOL" Value="0" />
<DataValueMember Name="SSMStatus2" DataType="BOOL" Value="0" />
<DataValueMember Name="SLSActive2" DataType="BOOL" Value="0" />
<DataValueMember Name="SLSLimit2" DataType="BOOL" Value="0" />
<DataValueMember Name="SDIActive2" DataType="BOOL" Value="0" />
<DataValueMember Name="SDILimit2" DataType="BOOL" Value="0" />
<DataValueMember Name="PassThruPositionLimitStatus2" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SCAActive2" DataType="BOOL" Value="0" />
<DataValueMember Name="SCAStatus2" DataType="BOOL" Value="0" />
<DataValueMember Name="SLPActive2" DataType="BOOL" Value="0" />
<DataValueMember Name="SLPLimit2" DataType="BOOL" Value="0" />
<DataValueMember Name="SFHomed2" DataType="BOOL" Value="0" />
<DataValueMember Name="PassThruStopFaults2" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SFXFault2" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCFault2" DataType="BOOL" Value="0" />
<DataValueMember Name="SS1Fault2" DataType="BOOL" Value="0" />
<DataValueMember Name="SS2Fault2" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSFault2" DataType="BOOL" Value="0" />
<DataValueMember Name="PassThruLimitFaults2" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SSMFault2" DataType="BOOL" Value="0" />
<DataValueMember Name="SLSFault2" DataType="BOOL" Value="0" />
<DataValueMember Name="SDIFault2" DataType="BOOL" Value="0" />
<DataValueMember Name="SCAFault2" DataType="BOOL" Value="0" />
<DataValueMember Name="SLPFault2" DataType="BOOL" Value="0" />
<DataValueMember Name="SafetyStopFunctions2" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="STOOutput2" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCOutput2" DataType="BOOL" Value="0" />
<DataValueMember Name="SS1Request2" DataType="BOOL" Value="0" />
<DataValueMember Name="SS2Request2" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSRequest2" DataType="BOOL" Value="0" />
<DataValueMember Name="SMTRequest2" DataType="BOOL" Value="0" />
<DataValueMember Name="ResetRequest2" DataType="BOOL" Value="0" />
</Structure>
</Data>
</OutputTag>
</Connection>
<Connection Name="D_Safety_Input2" RPI="10000" Type="SafetyInputDataDriven" InputSize="44" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="40.064" MaxObservedNetworkDelay="0" Priority="High" InputConnectionType="Unicast" InputProductionTrigger="Application" ConnectionPath="20 04 24 66 20 04 24 c7 20 04 25 00 02 04" InputTagSuffix="SI">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:CIP_Motion_Device_Safety2:SI:0">
<DataValueMember Name="ConnectionStatus" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="RunMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="0" />
<DataValueMember Name="FeedbackPosition1" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="FeedbackVelocity1" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="SecondaryFeedbackPosition1" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="SecondaryFeedbackVelocity1" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="FeedbackPosition2" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="FeedbackVelocity2" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="SecondaryFeedbackPosition2" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="SecondaryFeedbackVelocity2" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="StopStatus1" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="STOActive1" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCActive1" DataType="BOOL" Value="0" />
<DataValueMember Name="SS1Active1" DataType="BOOL" Value="0" />
<DataValueMember Name="SS2Active1" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSStandstill1" DataType="BOOL" Value="0" />
<DataValueMember Name="SMTOvertemp1" DataType="BOOL" Value="0" />
<DataValueMember Name="SafetyFault1" DataType="BOOL" Value="0" />
<DataValueMember Name="RestartRequired1" DataType="BOOL" Value="0" />
<DataValueMember Name="SafeStatus1" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="TorqueDisabled1" DataType="BOOL" Value="0" />
<DataValueMember Name="BrakeEngaged1" DataType="BOOL" Value="0" />
<DataValueMember Name="MotionStatus1" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="MotionPositive1" DataType="BOOL" Value="0" />
<DataValueMember Name="MotionNegative1" DataType="BOOL" Value="0" />
<DataValueMember Name="FunctionSupport1" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="PrimaryFeedbackValid1" DataType="BOOL" Value="0" />
<DataValueMember Name="SecondaryFeedbackValid1" DataType="BOOL" Value="0" />
<DataValueMember Name="DiscrepancyCheckingActive1" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCReady1" DataType="BOOL" Value="0" />
<DataValueMember Name="SS1Ready1" DataType="BOOL" Value="0" />
<DataValueMember Name="SS2Ready1" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSReady1" DataType="BOOL" Value="0" />
<DataValueMember Name="SMTReady1" DataType="BOOL" Value="0" />
<DataValueMember Name="StopStatus2" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="STOActive2" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCActive2" DataType="BOOL" Value="0" />
<DataValueMember Name="SS1Active2" DataType="BOOL" Value="0" />
<DataValueMember Name="SS2Active2" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSStandstill2" DataType="BOOL" Value="0" />
<DataValueMember Name="SMTOvertemp2" DataType="BOOL" Value="0" />
<DataValueMember Name="SafetyFault2" DataType="BOOL" Value="0" />
<DataValueMember Name="RestartRequired2" DataType="BOOL" Value="0" />
<DataValueMember Name="SafeStatus2" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="TorqueDisabled2" DataType="BOOL" Value="0" />
<DataValueMember Name="BrakeEngaged2" DataType="BOOL" Value="0" />
<DataValueMember Name="MotionStatus2" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="MotionPositive2" DataType="BOOL" Value="0" />
<DataValueMember Name="MotionNegative2" DataType="BOOL" Value="0" />
<DataValueMember Name="FunctionSupport2" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="PrimaryFeedbackValid2" DataType="BOOL" Value="0" />
<DataValueMember Name="SecondaryFeedbackValid2" DataType="BOOL" Value="0" />
<DataValueMember Name="DiscrepancyCheckingActive2" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCReady2" DataType="BOOL" Value="0" />
<DataValueMember Name="SS1Ready2" DataType="BOOL" Value="0" />
<DataValueMember Name="SS2Ready2" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSReady2" DataType="BOOL" Value="0" />
<DataValueMember Name="SMTReady2" DataType="BOOL" Value="0" />
</Structure>
</Data>
</InputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'SJ_Gormley_20251112_r02.L5X', 1),
        ('2conn', """\
<Module Name="TestMod1_2198D032ERS3" CatalogNumber="2198-D032-ERS3" Vendor="1" ProductType="45" ProductCode="13" Major="14" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false" SafetyEnabled="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="2" Address="192.168.1.73" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="468">
<Data Format="L5K">
[472,7,1793,13,434110479,18,10000,33686020,5,0,0,0,0,0,0,0,0,-1027080192,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,33686018,33686018
		,67108864,460,1,1045220557,0,0,0,0,1120403456,1120403456,0,1120403456,1124859904,0,0,1120403456,2,0
		,4,0,0,0,0,0,2,0,0,0,4,0,0,0,0,0,0,0,0,0,0,0,262148,0,50528513,0,0,0,8192000,8192125,67305985,0,0,0,67305985,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,50987786,0,655370,0]
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
<DataValueMember Name="ControllerToDriveConnectionSize" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="DriveToControllerConnectionSize" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="NominalControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="NominalDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="CoarseUpdatePeriod" DataType="INT" Radix="Decimal" Value="0" />
</Structure>
</Data>
</InputTag>
</Connection>
<Connection Name="B_MotionSync2" RPI="4000" Type="MotionSync" EventID="0" ProgrammaticallySendEventTrigger="false" />
</Connections>
</Communications>
</Module>
""", 'BaillieLeitchField_Edger_20260812_r00.L5X', 1),
    ],
    '2198-D057-ERS3': [
        ('4conn', """\
<Module Name="TestMod1_2198D057ERS3" CatalogNumber="2198-D057-ERS3" Vendor="1" ProductType="45" ProductCode="14" Major="14" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false" SafetyNetwork="16#0000_4cd3_03df_cbbd" SafetyEnabled="true">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="2" Address="192.168.1.73" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="468">
<Data Format="L5K">
[472,7,1793,14,434110479,18,10000,33686020,5,0,0,0,0,0,0,0,0,-1027080192,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,33686018,33686018
		,67108864,460,1,1045220557,0,0,0,0,1120403456,1120403456,0,1120403456,1124859904,0,0,1120403456,2,0
		,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,262148,0,50528513,0,0,0,8192000,8192125,67305985,0,0,0,67305985,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,50987786,0,655370,0]
</Data>
</ConfigData>
<SafetyScript Size="353">
<Data Format="L5K">
[93,1,0,0,5,0,0,0,0,0,0,0,0,0,0,0,77,1,0,0,0,0,0,0,0,3,0,0,0,63,1,0,0,0,0,0,56,1,0,0,102,0,0,0,-64,114,-103,34,-79,-119,-128,4,-44,76,0,0
		,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-128,63,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-128
		,63,1,1,0,0,0,0,1,0,0,0,-128,63,1,0,0,0,-1,-1,121,-60,0,0,0,0,1,0,0,0,1,0,0,0,0,0,1,0,0,0,-128,63,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,1,0,0,0,0,0,-128
		,63,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-128,63,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,-128,63,1,1,0,0,0,0,1,0,0,0,-128,63,1,0,0,0,-1,-1,121,-60,0,0,0,0,1,0,0,0,1,0,0,0,0,0,1,0,0,0,-128,63,0,0,0,0,0,0,0,0,1,0,0,0,0,0
		,1,0,1,0,0,0,0,0,-128,63,0,0,0,0,0,0,1,0,0]
</Data>
</SafetyScript>
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
<DataValueMember Name="ControllerToDriveConnectionSize" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="DriveToControllerConnectionSize" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="NominalControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="NominalDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="CoarseUpdatePeriod" DataType="INT" Radix="Decimal" Value="0" />
</Structure>
</Data>
</InputTag>
</Connection>
<Connection Name="B_MotionSync2" RPI="2000" Type="MotionSync" EventID="0" ProgrammaticallySendEventTrigger="false" />
<Connection Name="C_Safety_Output2" RPI="20000" Type="SafetyOutputDataDriven" OutputSize="28" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="60" MaxObservedNetworkDelay="0" Priority="High" InputConnectionType="Unicast" InputProductionTrigger="Application" ConnectionPath="20 04 24 66 20 04 25 00 02 03 20 04 24 c7" OutputTagSuffix="SO">
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:CIP_Motion_Device_Safety2:SO:0">
<DataValueMember Name="PassThruDataA1" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="PassThruDataB1" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="PassThruDataA2" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="PassThruDataB2" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="PassThruStopStatus1" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SBCIntegrity1" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCActive1" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCBrakeEngaged1" DataType="BOOL" Value="0" />
<DataValueMember Name="SS1Active1" DataType="BOOL" Value="0" />
<DataValueMember Name="SS2Active1" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSActive1" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSStandstill1" DataType="BOOL" Value="0" />
<DataValueMember Name="PassThruSpeedLimitStatus1" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SSMActive1" DataType="BOOL" Value="0" />
<DataValueMember Name="SSMStatus1" DataType="BOOL" Value="0" />
<DataValueMember Name="SLSActive1" DataType="BOOL" Value="0" />
<DataValueMember Name="SLSLimit1" DataType="BOOL" Value="0" />
<DataValueMember Name="SDIActive1" DataType="BOOL" Value="0" />
<DataValueMember Name="SDILimit1" DataType="BOOL" Value="0" />
<DataValueMember Name="PassThruPositionLimitStatus1" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SCAActive1" DataType="BOOL" Value="0" />
<DataValueMember Name="SCAStatus1" DataType="BOOL" Value="0" />
<DataValueMember Name="SLPActive1" DataType="BOOL" Value="0" />
<DataValueMember Name="SLPLimit1" DataType="BOOL" Value="0" />
<DataValueMember Name="SFHomed1" DataType="BOOL" Value="0" />
<DataValueMember Name="PassThruStopFaults1" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SFXFault1" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCFault1" DataType="BOOL" Value="0" />
<DataValueMember Name="SS1Fault1" DataType="BOOL" Value="0" />
<DataValueMember Name="SS2Fault1" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSFault1" DataType="BOOL" Value="0" />
<DataValueMember Name="PassThruLimitFaults1" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SSMFault1" DataType="BOOL" Value="0" />
<DataValueMember Name="SLSFault1" DataType="BOOL" Value="0" />
<DataValueMember Name="SDIFault1" DataType="BOOL" Value="0" />
<DataValueMember Name="SCAFault1" DataType="BOOL" Value="0" />
<DataValueMember Name="SLPFault1" DataType="BOOL" Value="0" />
<DataValueMember Name="SafetyStopFunctions1" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="STOOutput1" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCOutput1" DataType="BOOL" Value="0" />
<DataValueMember Name="SS1Request1" DataType="BOOL" Value="0" />
<DataValueMember Name="SS2Request1" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSRequest1" DataType="BOOL" Value="0" />
<DataValueMember Name="SMTRequest1" DataType="BOOL" Value="0" />
<DataValueMember Name="ResetRequest1" DataType="BOOL" Value="0" />
<DataValueMember Name="PassThruStopStatus2" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SBCIntegrity2" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCActive2" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCBrakeEngaged2" DataType="BOOL" Value="0" />
<DataValueMember Name="SS1Active2" DataType="BOOL" Value="0" />
<DataValueMember Name="SS2Active2" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSActive2" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSStandstill2" DataType="BOOL" Value="0" />
<DataValueMember Name="PassThruSpeedLimitStatus2" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SSMActive2" DataType="BOOL" Value="0" />
<DataValueMember Name="SSMStatus2" DataType="BOOL" Value="0" />
<DataValueMember Name="SLSActive2" DataType="BOOL" Value="0" />
<DataValueMember Name="SLSLimit2" DataType="BOOL" Value="0" />
<DataValueMember Name="SDIActive2" DataType="BOOL" Value="0" />
<DataValueMember Name="SDILimit2" DataType="BOOL" Value="0" />
<DataValueMember Name="PassThruPositionLimitStatus2" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SCAActive2" DataType="BOOL" Value="0" />
<DataValueMember Name="SCAStatus2" DataType="BOOL" Value="0" />
<DataValueMember Name="SLPActive2" DataType="BOOL" Value="0" />
<DataValueMember Name="SLPLimit2" DataType="BOOL" Value="0" />
<DataValueMember Name="SFHomed2" DataType="BOOL" Value="0" />
<DataValueMember Name="PassThruStopFaults2" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SFXFault2" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCFault2" DataType="BOOL" Value="0" />
<DataValueMember Name="SS1Fault2" DataType="BOOL" Value="0" />
<DataValueMember Name="SS2Fault2" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSFault2" DataType="BOOL" Value="0" />
<DataValueMember Name="PassThruLimitFaults2" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SSMFault2" DataType="BOOL" Value="0" />
<DataValueMember Name="SLSFault2" DataType="BOOL" Value="0" />
<DataValueMember Name="SDIFault2" DataType="BOOL" Value="0" />
<DataValueMember Name="SCAFault2" DataType="BOOL" Value="0" />
<DataValueMember Name="SLPFault2" DataType="BOOL" Value="0" />
<DataValueMember Name="SafetyStopFunctions2" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="STOOutput2" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCOutput2" DataType="BOOL" Value="0" />
<DataValueMember Name="SS1Request2" DataType="BOOL" Value="0" />
<DataValueMember Name="SS2Request2" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSRequest2" DataType="BOOL" Value="0" />
<DataValueMember Name="SMTRequest2" DataType="BOOL" Value="0" />
<DataValueMember Name="ResetRequest2" DataType="BOOL" Value="0" />
</Structure>
</Data>
</OutputTag>
</Connection>
<Connection Name="D_Safety_Input2" RPI="10000" Type="SafetyInputDataDriven" InputSize="44" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="40.064" MaxObservedNetworkDelay="0" Priority="High" InputConnectionType="Unicast" InputProductionTrigger="Application" ConnectionPath="20 04 24 66 20 04 24 c7 20 04 25 00 02 04" InputTagSuffix="SI">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:CIP_Motion_Device_Safety2:SI:0">
<DataValueMember Name="ConnectionStatus" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="RunMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="0" />
<DataValueMember Name="FeedbackPosition1" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="FeedbackVelocity1" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="SecondaryFeedbackPosition1" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="SecondaryFeedbackVelocity1" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="FeedbackPosition2" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="FeedbackVelocity2" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="SecondaryFeedbackPosition2" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="SecondaryFeedbackVelocity2" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="StopStatus1" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="STOActive1" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCActive1" DataType="BOOL" Value="0" />
<DataValueMember Name="SS1Active1" DataType="BOOL" Value="0" />
<DataValueMember Name="SS2Active1" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSStandstill1" DataType="BOOL" Value="0" />
<DataValueMember Name="SMTOvertemp1" DataType="BOOL" Value="0" />
<DataValueMember Name="SafetyFault1" DataType="BOOL" Value="0" />
<DataValueMember Name="RestartRequired1" DataType="BOOL" Value="0" />
<DataValueMember Name="SafeStatus1" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="TorqueDisabled1" DataType="BOOL" Value="0" />
<DataValueMember Name="BrakeEngaged1" DataType="BOOL" Value="0" />
<DataValueMember Name="MotionStatus1" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="MotionPositive1" DataType="BOOL" Value="0" />
<DataValueMember Name="MotionNegative1" DataType="BOOL" Value="0" />
<DataValueMember Name="FunctionSupport1" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="PrimaryFeedbackValid1" DataType="BOOL" Value="0" />
<DataValueMember Name="SecondaryFeedbackValid1" DataType="BOOL" Value="0" />
<DataValueMember Name="DiscrepancyCheckingActive1" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCReady1" DataType="BOOL" Value="0" />
<DataValueMember Name="SS1Ready1" DataType="BOOL" Value="0" />
<DataValueMember Name="SS2Ready1" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSReady1" DataType="BOOL" Value="0" />
<DataValueMember Name="SMTReady1" DataType="BOOL" Value="0" />
<DataValueMember Name="StopStatus2" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="STOActive2" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCActive2" DataType="BOOL" Value="0" />
<DataValueMember Name="SS1Active2" DataType="BOOL" Value="0" />
<DataValueMember Name="SS2Active2" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSStandstill2" DataType="BOOL" Value="0" />
<DataValueMember Name="SMTOvertemp2" DataType="BOOL" Value="0" />
<DataValueMember Name="SafetyFault2" DataType="BOOL" Value="0" />
<DataValueMember Name="RestartRequired2" DataType="BOOL" Value="0" />
<DataValueMember Name="SafeStatus2" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="TorqueDisabled2" DataType="BOOL" Value="0" />
<DataValueMember Name="BrakeEngaged2" DataType="BOOL" Value="0" />
<DataValueMember Name="MotionStatus2" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="MotionPositive2" DataType="BOOL" Value="0" />
<DataValueMember Name="MotionNegative2" DataType="BOOL" Value="0" />
<DataValueMember Name="FunctionSupport2" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="PrimaryFeedbackValid2" DataType="BOOL" Value="0" />
<DataValueMember Name="SecondaryFeedbackValid2" DataType="BOOL" Value="0" />
<DataValueMember Name="DiscrepancyCheckingActive2" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCReady2" DataType="BOOL" Value="0" />
<DataValueMember Name="SS1Ready2" DataType="BOOL" Value="0" />
<DataValueMember Name="SS2Ready2" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSReady2" DataType="BOOL" Value="0" />
<DataValueMember Name="SMTReady2" DataType="BOOL" Value="0" />
</Structure>
</Data>
</InputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'SJ_Gormley_20251112_r02.L5X', 1),
        ('2conn', """\
<Module Name="TestMod1_2198D057ERS3" CatalogNumber="2198-D057-ERS3" Vendor="1" ProductType="45" ProductCode="14" Major="14" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false" SafetyEnabled="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="2" Address="192.168.1.73" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="468">
<Data Format="L5K">
[472,7,1793,14,434110479,18,10000,33686020,5,0,0,0,0,0,0,0,0,-1027080192,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,33686018,33686018
		,67108864,460,1,1045220557,0,0,0,0,1120403456,1120403456,0,1120403456,1124859904,0,0,1120403456,2,0
		,4,0,0,0,0,0,2,0,0,0,4,0,0,0,0,0,0,0,0,0,0,0,262148,0,50528513,0,0,0,8192000,8192125,67305985,0,0,0,67305985,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,50987786,0,655370,0]
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
<DataValueMember Name="ControllerToDriveConnectionSize" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="DriveToControllerConnectionSize" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="NominalControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="NominalDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="CoarseUpdatePeriod" DataType="INT" Radix="Decimal" Value="0" />
</Structure>
</Data>
</InputTag>
</Connection>
<Connection Name="B_MotionSync2" RPI="8000" Type="MotionSync" EventID="0" ProgrammaticallySendEventTrigger="false" />
</Connections>
</Communications>
</Module>
""", 'BaillieLeitchField_Edger_20260812_r00.L5X', 1),
    ],
    '2198-S086-ERS3': [
        ('4conn', """\
<Module Name="TestMod1_2198S086ERS3" CatalogNumber="2198-S086-ERS3" Vendor="1" ProductType="45" ProductCode="7" Major="13" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false" SafetyNetwork="16#0000_4cd3_03df_cbbd" SafetyEnabled="true">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="2" Address="192.168.1.73" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="468">
<Data Format="L5K">
[472,7,1793,7,434110479,18,10000,33686020,1,0,0,0,0,0,0,0,0,-1027080192,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,33686018,33686018
		,33554432,460,1,1045220557,0,0,0,0,1120403456,1120403456,0,1120403456,1124859904,0,0,1120403456,1,0
		,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,0,1,0,0,0,8192000,8192125,67305985,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,778,0,10,0]
</Data>
</ConfigData>
<SafetyScript Size="205">
<Data Format="L5K">
[-55,0,0,0,5,0,0,0,0,0,0,0,0,0,0,0,-71,0,0,0,0,0,0,0,0,3,0,0,0,-85,0,0,0,0,0,0,-92,0,0,0,101,0,0,0,36,97,-46,-16,-25,117,86,4,-45,76,0,0,0
		,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-128,63,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-128
		,63,1,1,1,1,0,0,1,0,0,0,-128,63,1,0,0,0,-1,-1,121,-60,0,0,0,0,1,0,0,0,1,0,0,0,0,0,1,0,0,0,-128,63,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,1,0,0,0,0,0,-128
		,63,0,0,0,0,0,0,1,0,0]
</Data>
</SafetyScript>
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
<DataValueMember Name="ControllerToDriveConnectionSize" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="DriveToControllerConnectionSize" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="NominalControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="NominalDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="CoarseUpdatePeriod" DataType="INT" Radix="Decimal" Value="0" />
</Structure>
</Data>
</InputTag>
</Connection>
<Connection Name="B_MotionSync2" RPI="2000" Type="MotionSync" EventID="0" ProgrammaticallySendEventTrigger="false" />
<Connection Name="C_Safety_Output2" RPI="20000" Type="SafetyOutputDataDriven" OutputSize="14" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="60" MaxObservedNetworkDelay="0" Priority="High" InputConnectionType="Unicast" InputProductionTrigger="Application" ConnectionPath="20 04 24 65 20 04 25 00 01 03 20 04 24 c7" OutputTagSuffix="SO">
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[0,0,0,0,0,0,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:CIP_Motion_Device_Safety1:SO:0">
<DataValueMember Name="PassThruDataA" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="PassThruDataB" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="PassThruStopStatus" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SBCIntegrity" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCActive" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCBrakeEngaged" DataType="BOOL" Value="0" />
<DataValueMember Name="SS1Active" DataType="BOOL" Value="0" />
<DataValueMember Name="SS2Active" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSActive" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSStandstill" DataType="BOOL" Value="0" />
<DataValueMember Name="PassThruSpeedLimitStatus" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SSMActive" DataType="BOOL" Value="0" />
<DataValueMember Name="SSMStatus" DataType="BOOL" Value="0" />
<DataValueMember Name="SLSActive" DataType="BOOL" Value="0" />
<DataValueMember Name="SLSLimit" DataType="BOOL" Value="0" />
<DataValueMember Name="SDIActive" DataType="BOOL" Value="0" />
<DataValueMember Name="SDILimit" DataType="BOOL" Value="0" />
<DataValueMember Name="PassThruPositionLimitStatus" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SCAActive" DataType="BOOL" Value="0" />
<DataValueMember Name="SCAStatus" DataType="BOOL" Value="0" />
<DataValueMember Name="SLPActive" DataType="BOOL" Value="0" />
<DataValueMember Name="SLPLimit" DataType="BOOL" Value="0" />
<DataValueMember Name="SFHomed" DataType="BOOL" Value="0" />
<DataValueMember Name="PassThruStopFaults" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SFXFault" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCFault" DataType="BOOL" Value="0" />
<DataValueMember Name="SS1Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="SS2Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSFault" DataType="BOOL" Value="0" />
<DataValueMember Name="PassThruLimitFaults" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SSMFault" DataType="BOOL" Value="0" />
<DataValueMember Name="SLSFault" DataType="BOOL" Value="0" />
<DataValueMember Name="SDIFault" DataType="BOOL" Value="0" />
<DataValueMember Name="SCAFault" DataType="BOOL" Value="0" />
<DataValueMember Name="SLPFault" DataType="BOOL" Value="0" />
<DataValueMember Name="SafetyStopFunctions" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="STOOutput" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCOutput" DataType="BOOL" Value="0" />
<DataValueMember Name="SS1Request" DataType="BOOL" Value="0" />
<DataValueMember Name="SS2Request" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSRequest" DataType="BOOL" Value="0" />
<DataValueMember Name="SMTRequest" DataType="BOOL" Value="0" />
<DataValueMember Name="ResetRequest" DataType="BOOL" Value="0" />
</Structure>
</Data>
</OutputTag>
</Connection>
<Connection Name="D_Safety_Input2" RPI="10000" Type="SafetyInputDataDriven" InputSize="24" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="40.064" MaxObservedNetworkDelay="0" Priority="High" InputConnectionType="Unicast" InputProductionTrigger="Application" ConnectionPath="20 04 24 65 20 04 24 c7 20 04 25 00 01 04" InputTagSuffix="SI">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:CIP_Motion_Device_Safety1:SI:0">
<DataValueMember Name="ConnectionStatus" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="RunMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="0" />
<DataValueMember Name="FeedbackPosition" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="FeedbackVelocity" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="SecondaryFeedbackPosition" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="SecondaryFeedbackVelocity" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="StopStatus" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="STOActive" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCActive" DataType="BOOL" Value="0" />
<DataValueMember Name="SS1Active" DataType="BOOL" Value="0" />
<DataValueMember Name="SS2Active" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSStandstill" DataType="BOOL" Value="0" />
<DataValueMember Name="SMTOvertemp" DataType="BOOL" Value="0" />
<DataValueMember Name="SafetyFault" DataType="BOOL" Value="0" />
<DataValueMember Name="RestartRequired" DataType="BOOL" Value="0" />
<DataValueMember Name="SafeStatus" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="TorqueDisabled" DataType="BOOL" Value="0" />
<DataValueMember Name="BrakeEngaged" DataType="BOOL" Value="0" />
<DataValueMember Name="MotionStatus" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="MotionPositive" DataType="BOOL" Value="0" />
<DataValueMember Name="MotionNegative" DataType="BOOL" Value="0" />
<DataValueMember Name="FunctionSupport" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="PrimaryFeedbackValid" DataType="BOOL" Value="0" />
<DataValueMember Name="SecondaryFeedbackValid" DataType="BOOL" Value="0" />
<DataValueMember Name="DiscrepancyCheckingActive" DataType="BOOL" Value="0" />
<DataValueMember Name="SBCReady" DataType="BOOL" Value="0" />
<DataValueMember Name="SS1Ready" DataType="BOOL" Value="0" />
<DataValueMember Name="SS2Ready" DataType="BOOL" Value="0" />
<DataValueMember Name="SOSReady" DataType="BOOL" Value="0" />
<DataValueMember Name="SMTReady" DataType="BOOL" Value="0" />
</Structure>
</Data>
</InputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'SJ_Gormley_20251112_r02.L5X', 1),
        ('2conn', """\
<Module Name="TestMod1_2198S086ERS3" CatalogNumber="2198-S086-ERS3" Vendor="1" ProductType="45" ProductCode="7" Major="13" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false" SafetyEnabled="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="2" Address="192.168.1.73" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="468">
<Data Format="L5K">
[472,7,1793,7,434110479,18,10000,33686020,1,0,0,0,0,0,0,0,0,-1027080192,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,33686018,33686018
		,33554432,460,1,1045220557,0,0,0,0,1120403456,1120403456,0,1120403456,1124859904,0,0,1120403456,2,0
		,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,0,1,0,0,0,8192000,8192125,67305985,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,778,0,10,0]
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
<DataValueMember Name="ControllerToDriveConnectionSize" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="DriveToControllerConnectionSize" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="NominalControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="NominalDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="CoarseUpdatePeriod" DataType="INT" Radix="Decimal" Value="0" />
</Structure>
</Data>
</InputTag>
</Connection>
<Connection Name="B_MotionSync2" RPI="8000" Type="MotionSync" EventID="0" ProgrammaticallySendEventTrigger="false" />
</Connections>
</Communications>
</Module>
""", 'BaillieLeitchField_Edger_20260812_r00.L5X', 1),
    ],
    'ETHERNET-MODULE': [
        ('1conn', """\
<Module Name="TestMod1_ETHERNETMODULE" CatalogNumber="ETHERNET-MODULE" Vendor="1" ProductType="0" ProductCode="18" Major="1" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="Disabled" />
<Ports>
<Port Id="2" Address="192.168.1.73" Type="Ethernet" Upstream="true" />
</Ports>
<Communications CommMethod="536870916" PrimCxnInputSize="450" PrimCxnOutputSize="8">
<ConfigTag ConfigSize="0" ExternalAccess="Read/Write">
<Data Format="L5K">
[4,1,[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:ETHERNET_MODULE:C:0">
<ArrayMember Name="Data" DataType="SINT" Dimensions="400" Radix="Hex">
<Element Index="[0]" Value="16#00" />
<Element Index="[1]" Value="16#00" />
<Element Index="[2]" Value="16#00" />
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
<Element Index="[19]" Value="16#00" />
<Element Index="[20]" Value="16#00" />
<Element Index="[21]" Value="16#00" />
<Element Index="[22]" Value="16#00" />
<Element Index="[23]" Value="16#00" />
<Element Index="[24]" Value="16#00" />
<Element Index="[25]" Value="16#00" />
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
<Element Index="[64]" Value="16#00" />
<Element Index="[65]" Value="16#00" />
<Element Index="[66]" Value="16#00" />
<Element Index="[67]" Value="16#00" />
<Element Index="[68]" Value="16#00" />
<Element Index="[69]" Value="16#00" />
<Element Index="[70]" Value="16#00" />
<Element Index="[71]" Value="16#00" />
<Element Index="[72]" Value="16#00" />
<Element Index="[73]" Value="16#00" />
<Element Index="[74]" Value="16#00" />
<Element Index="[75]" Value="16#00" />
<Element Index="[76]" Value="16#00" />
<Element Index="[77]" Value="16#00" />
<Element Index="[78]" Value="16#00" />
<Element Index="[79]" Value="16#00" />
<Element Index="[80]" Value="16#00" />
<Element Index="[81]" Value="16#00" />
<Element Index="[82]" Value="16#00" />
<Element Index="[83]" Value="16#00" />
<Element Index="[84]" Value="16#00" />
<Element Index="[85]" Value="16#00" />
<Element Index="[86]" Value="16#00" />
<Element Index="[87]" Value="16#00" />
<Element Index="[88]" Value="16#00" />
<Element Index="[89]" Value="16#00" />
<Element Index="[90]" Value="16#00" />
<Element Index="[91]" Value="16#00" />
<Element Index="[92]" Value="16#00" />
<Element Index="[93]" Value="16#00" />
<Element Index="[94]" Value="16#00" />
<Element Index="[95]" Value="16#00" />
<Element Index="[96]" Value="16#00" />
<Element Index="[97]" Value="16#00" />
<Element Index="[98]" Value="16#00" />
<Element Index="[99]" Value="16#00" />
<Element Index="[100]" Value="16#00" />
<Element Index="[101]" Value="16#00" />
<Element Index="[102]" Value="16#00" />
<Element Index="[103]" Value="16#00" />
<Element Index="[104]" Value="16#00" />
<Element Index="[105]" Value="16#00" />
<Element Index="[106]" Value="16#00" />
<Element Index="[107]" Value="16#00" />
<Element Index="[108]" Value="16#00" />
<Element Index="[109]" Value="16#00" />
<Element Index="[110]" Value="16#00" />
<Element Index="[111]" Value="16#00" />
<Element Index="[112]" Value="16#00" />
<Element Index="[113]" Value="16#00" />
<Element Index="[114]" Value="16#00" />
<Element Index="[115]" Value="16#00" />
<Element Index="[116]" Value="16#00" />
<Element Index="[117]" Value="16#00" />
<Element Index="[118]" Value="16#00" />
<Element Index="[119]" Value="16#00" />
<Element Index="[120]" Value="16#00" />
<Element Index="[121]" Value="16#00" />
<Element Index="[122]" Value="16#00" />
<Element Index="[123]" Value="16#00" />
<Element Index="[124]" Value="16#00" />
<Element Index="[125]" Value="16#00" />
<Element Index="[126]" Value="16#00" />
<Element Index="[127]" Value="16#00" />
<Element Index="[128]" Value="16#00" />
<Element Index="[129]" Value="16#00" />
<Element Index="[130]" Value="16#00" />
<Element Index="[131]" Value="16#00" />
<Element Index="[132]" Value="16#00" />
<Element Index="[133]" Value="16#00" />
<Element Index="[134]" Value="16#00" />
<Element Index="[135]" Value="16#00" />
<Element Index="[136]" Value="16#00" />
<Element Index="[137]" Value="16#00" />
<Element Index="[138]" Value="16#00" />
<Element Index="[139]" Value="16#00" />
<Element Index="[140]" Value="16#00" />
<Element Index="[141]" Value="16#00" />
<Element Index="[142]" Value="16#00" />
<Element Index="[143]" Value="16#00" />
<Element Index="[144]" Value="16#00" />
<Element Index="[145]" Value="16#00" />
<Element Index="[146]" Value="16#00" />
<Element Index="[147]" Value="16#00" />
<Element Index="[148]" Value="16#00" />
<Element Index="[149]" Value="16#00" />
<Element Index="[150]" Value="16#00" />
<Element Index="[151]" Value="16#00" />
<Element Index="[152]" Value="16#00" />
<Element Index="[153]" Value="16#00" />
<Element Index="[154]" Value="16#00" />
<Element Index="[155]" Value="16#00" />
<Element Index="[156]" Value="16#00" />
<Element Index="[157]" Value="16#00" />
<Element Index="[158]" Value="16#00" />
<Element Index="[159]" Value="16#00" />
<Element Index="[160]" Value="16#00" />
<Element Index="[161]" Value="16#00" />
<Element Index="[162]" Value="16#00" />
<Element Index="[163]" Value="16#00" />
<Element Index="[164]" Value="16#00" />
<Element Index="[165]" Value="16#00" />
<Element Index="[166]" Value="16#00" />
<Element Index="[167]" Value="16#00" />
<Element Index="[168]" Value="16#00" />
<Element Index="[169]" Value="16#00" />
<Element Index="[170]" Value="16#00" />
<Element Index="[171]" Value="16#00" />
<Element Index="[172]" Value="16#00" />
<Element Index="[173]" Value="16#00" />
<Element Index="[174]" Value="16#00" />
<Element Index="[175]" Value="16#00" />
<Element Index="[176]" Value="16#00" />
<Element Index="[177]" Value="16#00" />
<Element Index="[178]" Value="16#00" />
<Element Index="[179]" Value="16#00" />
<Element Index="[180]" Value="16#00" />
<Element Index="[181]" Value="16#00" />
<Element Index="[182]" Value="16#00" />
<Element Index="[183]" Value="16#00" />
<Element Index="[184]" Value="16#00" />
<Element Index="[185]" Value="16#00" />
<Element Index="[186]" Value="16#00" />
<Element Index="[187]" Value="16#00" />
<Element Index="[188]" Value="16#00" />
<Element Index="[189]" Value="16#00" />
<Element Index="[190]" Value="16#00" />
<Element Index="[191]" Value="16#00" />
<Element Index="[192]" Value="16#00" />
<Element Index="[193]" Value="16#00" />
<Element Index="[194]" Value="16#00" />
<Element Index="[195]" Value="16#00" />
<Element Index="[196]" Value="16#00" />
<Element Index="[197]" Value="16#00" />
<Element Index="[198]" Value="16#00" />
<Element Index="[199]" Value="16#00" />
<Element Index="[200]" Value="16#00" />
<Element Index="[201]" Value="16#00" />
<Element Index="[202]" Value="16#00" />
<Element Index="[203]" Value="16#00" />
<Element Index="[204]" Value="16#00" />
<Element Index="[205]" Value="16#00" />
<Element Index="[206]" Value="16#00" />
<Element Index="[207]" Value="16#00" />
<Element Index="[208]" Value="16#00" />
<Element Index="[209]" Value="16#00" />
<Element Index="[210]" Value="16#00" />
<Element Index="[211]" Value="16#00" />
<Element Index="[212]" Value="16#00" />
<Element Index="[213]" Value="16#00" />
<Element Index="[214]" Value="16#00" />
<Element Index="[215]" Value="16#00" />
<Element Index="[216]" Value="16#00" />
<Element Index="[217]" Value="16#00" />
<Element Index="[218]" Value="16#00" />
<Element Index="[219]" Value="16#00" />
<Element Index="[220]" Value="16#00" />
<Element Index="[221]" Value="16#00" />
<Element Index="[222]" Value="16#00" />
<Element Index="[223]" Value="16#00" />
<Element Index="[224]" Value="16#00" />
<Element Index="[225]" Value="16#00" />
<Element Index="[226]" Value="16#00" />
<Element Index="[227]" Value="16#00" />
<Element Index="[228]" Value="16#00" />
<Element Index="[229]" Value="16#00" />
<Element Index="[230]" Value="16#00" />
<Element Index="[231]" Value="16#00" />
<Element Index="[232]" Value="16#00" />
<Element Index="[233]" Value="16#00" />
<Element Index="[234]" Value="16#00" />
<Element Index="[235]" Value="16#00" />
<Element Index="[236]" Value="16#00" />
<Element Index="[237]" Value="16#00" />
<Element Index="[238]" Value="16#00" />
<Element Index="[239]" Value="16#00" />
<Element Index="[240]" Value="16#00" />
<Element Index="[241]" Value="16#00" />
<Element Index="[242]" Value="16#00" />
<Element Index="[243]" Value="16#00" />
<Element Index="[244]" Value="16#00" />
<Element Index="[245]" Value="16#00" />
<Element Index="[246]" Value="16#00" />
<Element Index="[247]" Value="16#00" />
<Element Index="[248]" Value="16#00" />
<Element Index="[249]" Value="16#00" />
<Element Index="[250]" Value="16#00" />
<Element Index="[251]" Value="16#00" />
<Element Index="[252]" Value="16#00" />
<Element Index="[253]" Value="16#00" />
<Element Index="[254]" Value="16#00" />
<Element Index="[255]" Value="16#00" />
<Element Index="[256]" Value="16#00" />
<Element Index="[257]" Value="16#00" />
<Element Index="[258]" Value="16#00" />
<Element Index="[259]" Value="16#00" />
<Element Index="[260]" Value="16#00" />
<Element Index="[261]" Value="16#00" />
<Element Index="[262]" Value="16#00" />
<Element Index="[263]" Value="16#00" />
<Element Index="[264]" Value="16#00" />
<Element Index="[265]" Value="16#00" />
<Element Index="[266]" Value="16#00" />
<Element Index="[267]" Value="16#00" />
<Element Index="[268]" Value="16#00" />
<Element Index="[269]" Value="16#00" />
<Element Index="[270]" Value="16#00" />
<Element Index="[271]" Value="16#00" />
<Element Index="[272]" Value="16#00" />
<Element Index="[273]" Value="16#00" />
<Element Index="[274]" Value="16#00" />
<Element Index="[275]" Value="16#00" />
<Element Index="[276]" Value="16#00" />
<Element Index="[277]" Value="16#00" />
<Element Index="[278]" Value="16#00" />
<Element Index="[279]" Value="16#00" />
<Element Index="[280]" Value="16#00" />
<Element Index="[281]" Value="16#00" />
<Element Index="[282]" Value="16#00" />
<Element Index="[283]" Value="16#00" />
<Element Index="[284]" Value="16#00" />
<Element Index="[285]" Value="16#00" />
<Element Index="[286]" Value="16#00" />
<Element Index="[287]" Value="16#00" />
<Element Index="[288]" Value="16#00" />
<Element Index="[289]" Value="16#00" />
<Element Index="[290]" Value="16#00" />
<Element Index="[291]" Value="16#00" />
<Element Index="[292]" Value="16#00" />
<Element Index="[293]" Value="16#00" />
<Element Index="[294]" Value="16#00" />
<Element Index="[295]" Value="16#00" />
<Element Index="[296]" Value="16#00" />
<Element Index="[297]" Value="16#00" />
<Element Index="[298]" Value="16#00" />
<Element Index="[299]" Value="16#00" />
<Element Index="[300]" Value="16#00" />
<Element Index="[301]" Value="16#00" />
<Element Index="[302]" Value="16#00" />
<Element Index="[303]" Value="16#00" />
<Element Index="[304]" Value="16#00" />
<Element Index="[305]" Value="16#00" />
<Element Index="[306]" Value="16#00" />
<Element Index="[307]" Value="16#00" />
<Element Index="[308]" Value="16#00" />
<Element Index="[309]" Value="16#00" />
<Element Index="[310]" Value="16#00" />
<Element Index="[311]" Value="16#00" />
<Element Index="[312]" Value="16#00" />
<Element Index="[313]" Value="16#00" />
<Element Index="[314]" Value="16#00" />
<Element Index="[315]" Value="16#00" />
<Element Index="[316]" Value="16#00" />
<Element Index="[317]" Value="16#00" />
<Element Index="[318]" Value="16#00" />
<Element Index="[319]" Value="16#00" />
<Element Index="[320]" Value="16#00" />
<Element Index="[321]" Value="16#00" />
<Element Index="[322]" Value="16#00" />
<Element Index="[323]" Value="16#00" />
<Element Index="[324]" Value="16#00" />
<Element Index="[325]" Value="16#00" />
<Element Index="[326]" Value="16#00" />
<Element Index="[327]" Value="16#00" />
<Element Index="[328]" Value="16#00" />
<Element Index="[329]" Value="16#00" />
<Element Index="[330]" Value="16#00" />
<Element Index="[331]" Value="16#00" />
<Element Index="[332]" Value="16#00" />
<Element Index="[333]" Value="16#00" />
<Element Index="[334]" Value="16#00" />
<Element Index="[335]" Value="16#00" />
<Element Index="[336]" Value="16#00" />
<Element Index="[337]" Value="16#00" />
<Element Index="[338]" Value="16#00" />
<Element Index="[339]" Value="16#00" />
<Element Index="[340]" Value="16#00" />
<Element Index="[341]" Value="16#00" />
<Element Index="[342]" Value="16#00" />
<Element Index="[343]" Value="16#00" />
<Element Index="[344]" Value="16#00" />
<Element Index="[345]" Value="16#00" />
<Element Index="[346]" Value="16#00" />
<Element Index="[347]" Value="16#00" />
<Element Index="[348]" Value="16#00" />
<Element Index="[349]" Value="16#00" />
<Element Index="[350]" Value="16#00" />
<Element Index="[351]" Value="16#00" />
<Element Index="[352]" Value="16#00" />
<Element Index="[353]" Value="16#00" />
<Element Index="[354]" Value="16#00" />
<Element Index="[355]" Value="16#00" />
<Element Index="[356]" Value="16#00" />
<Element Index="[357]" Value="16#00" />
<Element Index="[358]" Value="16#00" />
<Element Index="[359]" Value="16#00" />
<Element Index="[360]" Value="16#00" />
<Element Index="[361]" Value="16#00" />
<Element Index="[362]" Value="16#00" />
<Element Index="[363]" Value="16#00" />
<Element Index="[364]" Value="16#00" />
<Element Index="[365]" Value="16#00" />
<Element Index="[366]" Value="16#00" />
<Element Index="[367]" Value="16#00" />
<Element Index="[368]" Value="16#00" />
<Element Index="[369]" Value="16#00" />
<Element Index="[370]" Value="16#00" />
<Element Index="[371]" Value="16#00" />
<Element Index="[372]" Value="16#00" />
<Element Index="[373]" Value="16#00" />
<Element Index="[374]" Value="16#00" />
<Element Index="[375]" Value="16#00" />
<Element Index="[376]" Value="16#00" />
<Element Index="[377]" Value="16#00" />
<Element Index="[378]" Value="16#00" />
<Element Index="[379]" Value="16#00" />
<Element Index="[380]" Value="16#00" />
<Element Index="[381]" Value="16#00" />
<Element Index="[382]" Value="16#00" />
<Element Index="[383]" Value="16#00" />
<Element Index="[384]" Value="16#00" />
<Element Index="[385]" Value="16#00" />
<Element Index="[386]" Value="16#00" />
<Element Index="[387]" Value="16#00" />
<Element Index="[388]" Value="16#00" />
<Element Index="[389]" Value="16#00" />
<Element Index="[390]" Value="16#00" />
<Element Index="[391]" Value="16#00" />
<Element Index="[392]" Value="16#00" />
<Element Index="[393]" Value="16#00" />
<Element Index="[394]" Value="16#00" />
<Element Index="[395]" Value="16#00" />
<Element Index="[396]" Value="16#00" />
<Element Index="[397]" Value="16#00" />
<Element Index="[398]" Value="16#00" />
<Element Index="[399]" Value="16#00" />
</ArrayMember>
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="Standard" RPI="10000" Type="Output" InputCxnPoint="101" OutputCxnPoint="100" OutputSize="8" InputSize="450" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:ETHERNET_MODULE_SINT_450Bytes:I:0">
<ArrayMember Name="Data" DataType="SINT" Dimensions="450" Radix="Decimal">
<Element Index="[0]" Value="0" />
<Element Index="[1]" Value="0" />
<Element Index="[2]" Value="0" />
<Element Index="[3]" Value="0" />
<Element Index="[4]" Value="-25" />
<Element Index="[5]" Value="24" />
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
<Element Index="[318]" Value="0" />
<Element Index="[319]" Value="0" />
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
<Element Index="[446]" Value="0" />
<Element Index="[447]" Value="0" />
<Element Index="[448]" Value="0" />
<Element Index="[449]" Value="0" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[[0,0,0,0,0,0,0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:ETHERNET_MODULE_SINT_8Bytes:O:0">
<ArrayMember Name="Data" DataType="SINT" Dimensions="8" Radix="Decimal">
<Element Index="[0]" Value="0" />
<Element Index="[1]" Value="0" />
<Element Index="[2]" Value="0" />
<Element Index="[3]" Value="0" />
<Element Index="[4]" Value="0" />
<Element Index="[5]" Value="0" />
<Element Index="[6]" Value="0" />
<Element Index="[7]" Value="0" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'BaillieLeitchField_Edger_20260812_r00.L5X', 1),
        ('noconn', """\
<Module Name="TestMod1_ETHERNETMODULE" CatalogNumber="ETHERNET-MODULE" Vendor="1" ProductType="0" ProductCode="18" Major="1" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="true" MajorFault="false">
<EKey State="Disabled" />
<Ports>
<Port Id="2" Address="192.168.1.73" Type="Ethernet" Upstream="true" />
</Ports>
<Communications CommMethod="536870932">
<Connections />
</Communications>
</Module>
""", 'DnR_Personal/Fisher_Synergy_Bead_20240725.L5X', 1),
    ],
    'ETHERNET-PANELVIEW': [
        ('1conn', """\
<Module Name="TestMod1_ETHERNETPANELVIEW" CatalogNumber="ETHERNET-PANELVIEW" Vendor="1" ProductType="24" ProductCode="11" Major="1" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="true" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="2" Address="192.168.1.73" Type="Ethernet" Upstream="true" />
</Ports>
<Communications CommMethod="536870913" PrimCxnInputSize="4" PrimCxnOutputSize="4">
<Connections>
<Connection Name="Standard" RPI="750000" Type="Output" InputCxnPoint="7" OutputCxnPoint="6" OutputSize="4" InputSize="4" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:ETHERNET_PANELVIEW_DINT_4Bytes:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111" />
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[[0]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:ETHERNET_PANELVIEW_DINT_4Bytes:O:0">
<ArrayMember Name="Data" DataType="DINT" Dimensions="1" Radix="Decimal">
<Element Index="[0]" Value="0" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>
""", 'DnR_Personal/BT1XX_FFC_20240325.L5X', 1),
        ('1conn2', """\
<Module Name="TestMod1_ETHERNETPANELVIEW" CatalogNumber="ETHERNET-PANELVIEW" Vendor="1" ProductType="24" ProductCode="11" Major="1" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="true" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="2" Address="192.168.1.73" Type="Ethernet" Upstream="true" />
</Ports>
<Communications CommMethod="536870923" PrimCxnInputSize="450">
<Connections>
<Connection Name="Standard" RPI="100000" Type="Input" InputCxnPoint="7" OutputCxnPoint="6" OutputSize="0" InputSize="450" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:ETHERNET_PANELVIEW_INT_450Bytes:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111" />
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
</Connection>
</Connections>
</Communications>
</Module>
""", 'L5X_Samples/MurrayBros_20260122r1.L5X', 1),
    ],
}


def main() -> None:
    written = 0
    for catalog, variants in _MODULE_VARIANTS.items():
        cat_slug = "".join(c if c.isalnum() else "_" for c in catalog).strip("_").lower()
        for label, xml, source, chain_len in variants:
            out_name = f"modulesweep_{cat_slug}_variant_{label}"
            chain_note = "standalone module" if chain_len == 1 else f"module + its real {chain_len - 1}-deep parent chain"
            target = ("ModSweepV_" + "".join(c if c.isalnum() else "" for c in catalog) + label)[:24]
            l5x = build_l5x(target_name=target, tags_xml="", extra_modules_xml=xml)
            _write_unmodeled(
                l5x, out_name,
                f"{catalog} -- real corpus module, VARIANT '{label}' ({chain_note}), genericized "
                f"from {source}, structurally verbatim. One of {len(variants)} real DIFFERENT "
                f"shapes found for this same catalog number in the corpus -- see OQ-MODULEIO and "
                f"gen_module_sweep_variants.py's module docstring for why both are kept.",
            )
            written += 1
    print(f"Done. {written} module variant files written across {len(_MODULE_VARIANTS)} catalogs.")


if __name__ == "__main__":
    main()
