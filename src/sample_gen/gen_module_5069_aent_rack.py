"""Real 5069-AENTR remote-rack module blocks, genericized from James's
uploaded reference (Remote5069.L5X, 2026-09-02: "see attached for 5069 AENT
bus module to put 5069 cards remotely") -- structurally verbatim, only the
Controller/processor wrapper stripped. One 5069-AENTR EtherNet/IP adapter
(Bus Size=32, real) hosting 12 real 5069-family child I/O modules already
on real, unique, sequential slot addresses 1-12 (no remapping needed to
combine any subset of them in one file). Not independently used elsewhere
in this project -- gen_module_sweep.py's own 4 pre-existing 5069-family
catalogs (5069-IB16/A, 5069-IY4/A, 5069-OB16/A, 5069-OB16/B) are modeled
DIRECTLY on Local (Type="5069" Bus, no adapter), a different real shape;
this file's IB16/IY4/OB16-B blocks are the SAME real catalogs but in the
REMOTE-rack-via-adapter shape, both real, kept separate deliberately.
"""

from __future__ import annotations

_5069_AENT_CHAIN_BLOCKS = {
    '5069-AENTR': """\
<Module Name="AENT" CatalogNumber="5069-AENTR" Vendor="1" ProductType="12" ProductCode="317" Major="4" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false"
 SafetyEnabled="false">
<EKey State="CompatibleModule"/>
<Ports>
<Port Id="1" Address="0" Type="5069" Upstream="false">
<Bus Size="32"/>
</Port>
<Port Id="2" Address="192.168.1.1" Type="Ethernet" Upstream="true"/>
</Ports>
<ExtendedProperties>
<public><Vendor>Rockwell Automation/Allen-Bradley</Vendor><CatNum>5069-AENTR</CatNum><TimeSyncEnabled/><ConfigID>4325481</ConfigID></public>
</ExtendedProperties>
</Module>
""",
    '5069-IA16/A': """\
<Module CatalogNumber="5069-IA16/A" Vendor="1" ProductType="7" ProductCode="1212" Major="3" Minor="1" ParentModule="AENT" ParentModPortId="1" Inhibited="false" MajorFault="false" SafetyEnabled="false"
>
<EKey State="CompatibleModule"/>
<Ports>
<Port Id="1" Address="1" Type="5069" Upstream="true"/>
</Ports>
<Communications>
<ConfigTag ConfigSize="64" ExternalAccess="Read/Write">
<Data Format="L5K">
<![CDATA[[68,160,[13,16,0],[13,16,0],[13,16,0],[13,16,0],[13,16,0],[13,16,0],[13,16,0],[13,16,0],[13,16,0],[13,16,0],[13,16,0],[13,16,0],[13,16,0],[13,16,0],[13,16,0],[13
		,16,0]]]]>
</Data>
<Data Format="Decorated">
<Structure DataType="AB:5000_DI16:C:0">
<StructureMember Name="Pt00" DataType="AB:5000_DI_Channel:C:0">
<DataValueMember Name="InputOffOnFilter" DataType="SINT" Radix="Decimal" Value="13"/>
<DataValueMember Name="InputOnOffFilter" DataType="SINT" Radix="Decimal" Value="16"/>
</StructureMember>
<StructureMember Name="Pt01" DataType="AB:5000_DI_Channel:C:0">
<DataValueMember Name="InputOffOnFilter" DataType="SINT" Radix="Decimal" Value="13"/>
<DataValueMember Name="InputOnOffFilter" DataType="SINT" Radix="Decimal" Value="16"/>
</StructureMember>
<StructureMember Name="Pt02" DataType="AB:5000_DI_Channel:C:0">
<DataValueMember Name="InputOffOnFilter" DataType="SINT" Radix="Decimal" Value="13"/>
<DataValueMember Name="InputOnOffFilter" DataType="SINT" Radix="Decimal" Value="16"/>
</StructureMember>
<StructureMember Name="Pt03" DataType="AB:5000_DI_Channel:C:0">
<DataValueMember Name="InputOffOnFilter" DataType="SINT" Radix="Decimal" Value="13"/>
<DataValueMember Name="InputOnOffFilter" DataType="SINT" Radix="Decimal" Value="16"/>
</StructureMember>
<StructureMember Name="Pt04" DataType="AB:5000_DI_Channel:C:0">
<DataValueMember Name="InputOffOnFilter" DataType="SINT" Radix="Decimal" Value="13"/>
<DataValueMember Name="InputOnOffFilter" DataType="SINT" Radix="Decimal" Value="16"/>
</StructureMember>
<StructureMember Name="Pt05" DataType="AB:5000_DI_Channel:C:0">
<DataValueMember Name="InputOffOnFilter" DataType="SINT" Radix="Decimal" Value="13"/>
<DataValueMember Name="InputOnOffFilter" DataType="SINT" Radix="Decimal" Value="16"/>
</StructureMember>
<StructureMember Name="Pt06" DataType="AB:5000_DI_Channel:C:0">
<DataValueMember Name="InputOffOnFilter" DataType="SINT" Radix="Decimal" Value="13"/>
<DataValueMember Name="InputOnOffFilter" DataType="SINT" Radix="Decimal" Value="16"/>
</StructureMember>
<StructureMember Name="Pt07" DataType="AB:5000_DI_Channel:C:0">
<DataValueMember Name="InputOffOnFilter" DataType="SINT" Radix="Decimal" Value="13"/>
<DataValueMember Name="InputOnOffFilter" DataType="SINT" Radix="Decimal" Value="16"/>
</StructureMember>
<StructureMember Name="Pt08" DataType="AB:5000_DI_Channel:C:0">
<DataValueMember Name="InputOffOnFilter" DataType="SINT" Radix="Decimal" Value="13"/>
<DataValueMember Name="InputOnOffFilter" DataType="SINT" Radix="Decimal" Value="16"/>
</StructureMember>
<StructureMember Name="Pt09" DataType="AB:5000_DI_Channel:C:0">
<DataValueMember Name="InputOffOnFilter" DataType="SINT" Radix="Decimal" Value="13"/>
<DataValueMember Name="InputOnOffFilter" DataType="SINT" Radix="Decimal" Value="16"/>
</StructureMember>
<StructureMember Name="Pt10" DataType="AB:5000_DI_Channel:C:0">
<DataValueMember Name="InputOffOnFilter" DataType="SINT" Radix="Decimal" Value="13"/>
<DataValueMember Name="InputOnOffFilter" DataType="SINT" Radix="Decimal" Value="16"/>
</StructureMember>
<StructureMember Name="Pt11" DataType="AB:5000_DI_Channel:C:0">
<DataValueMember Name="InputOffOnFilter" DataType="SINT" Radix="Decimal" Value="13"/>
<DataValueMember Name="InputOnOffFilter" DataType="SINT" Radix="Decimal" Value="16"/>
</StructureMember>
<StructureMember Name="Pt12" DataType="AB:5000_DI_Channel:C:0">
<DataValueMember Name="InputOffOnFilter" DataType="SINT" Radix="Decimal" Value="13"/>
<DataValueMember Name="InputOnOffFilter" DataType="SINT" Radix="Decimal" Value="16"/>
</StructureMember>
<StructureMember Name="Pt13" DataType="AB:5000_DI_Channel:C:0">
<DataValueMember Name="InputOffOnFilter" DataType="SINT" Radix="Decimal" Value="13"/>
<DataValueMember Name="InputOnOffFilter" DataType="SINT" Radix="Decimal" Value="16"/>
</StructureMember>
<StructureMember Name="Pt14" DataType="AB:5000_DI_Channel:C:0">
<DataValueMember Name="InputOffOnFilter" DataType="SINT" Radix="Decimal" Value="13"/>
<DataValueMember Name="InputOnOffFilter" DataType="SINT" Radix="Decimal" Value="16"/>
</StructureMember>
<StructureMember Name="Pt15" DataType="AB:5000_DI_Channel:C:0">
<DataValueMember Name="InputOffOnFilter" DataType="SINT" Radix="Decimal" Value="13"/>
<DataValueMember Name="InputOnOffFilter" DataType="SINT" Radix="Decimal" Value="16"/>
</StructureMember>
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="InputData" RPI="5000" Type="StandardDataDriven" OutputSize="0" InputSize="68" EventID="0" ProgrammaticallySendEventTrigger="false" Priority="Scheduled" InputConnectionType="Unicast" InputProductionTrigger="Cyclic" ConnectionPath="20 04 24 a0 2c c7 2c 9a"
 InputTagSuffix="I">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:5000_DI16:I:0">
<DataValueMember Name="RunMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="0"/>
<DataValueMember Name="DiagnosticActive" DataType="BOOL" Value="0"/>
<DataValueMember Name="DiagnosticSequenceCount" DataType="SINT" Radix="Decimal" Value="0"/>
<StructureMember Name="Pt00" DataType="CHANNEL_DI:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt01" DataType="CHANNEL_DI:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt02" DataType="CHANNEL_DI:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt03" DataType="CHANNEL_DI:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt04" DataType="CHANNEL_DI:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt05" DataType="CHANNEL_DI:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt06" DataType="CHANNEL_DI:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt07" DataType="CHANNEL_DI:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt08" DataType="CHANNEL_DI:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt09" DataType="CHANNEL_DI:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt10" DataType="CHANNEL_DI:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt11" DataType="CHANNEL_DI:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt12" DataType="CHANNEL_DI:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt13" DataType="CHANNEL_DI:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt14" DataType="CHANNEL_DI:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt15" DataType="CHANNEL_DI:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
</Structure>
</Data>
</InputTag>
</Connection>
</Connections>
</Communications>
<ExtendedProperties>
<public><ConfigID>500</ConfigID><CatNum>5069-IA16</CatNum></public>
</ExtendedProperties>
</Module>
""",
    '5069-IB16/A': """\
<Module CatalogNumber="5069-IB16/A" Vendor="1" ProductType="7" ProductCode="390" Major="2" Minor="1" ParentModule="AENT" ParentModPortId="1" Inhibited="false" MajorFault="false" SafetyEnabled="false"
 AutoDiagsEnabled="true">
<EKey State="CompatibleModule"/>
<Ports>
<Port Id="1" Address="2" Type="5069" Upstream="true"/>
</Ports>
<Communications>
<ConfigTag ConfigSize="64" ExternalAccess="Read/Write">
<Data Format="L5K">
<![CDATA[[68,160,[13,13,0],[13,13,0],[13,13,0],[13,13,0],[13,13,0],[13,13,0],[13,13,0],[13,13,0],[13,13,0],[13,13,0],[13,13,0],[13,13,0],[13,13,0],[13,13,0],[13,13,0],[13
		,13,0]]]]>
</Data>
<Data Format="Decorated">
<Structure DataType="AB:5000_DI16:C:0">
<StructureMember Name="Pt00" DataType="AB:5000_DI_Channel:C:0">
<DataValueMember Name="InputOffOnFilter" DataType="SINT" Radix="Decimal" Value="13"/>
<DataValueMember Name="InputOnOffFilter" DataType="SINT" Radix="Decimal" Value="13"/>
</StructureMember>
<StructureMember Name="Pt01" DataType="AB:5000_DI_Channel:C:0">
<DataValueMember Name="InputOffOnFilter" DataType="SINT" Radix="Decimal" Value="13"/>
<DataValueMember Name="InputOnOffFilter" DataType="SINT" Radix="Decimal" Value="13"/>
</StructureMember>
<StructureMember Name="Pt02" DataType="AB:5000_DI_Channel:C:0">
<DataValueMember Name="InputOffOnFilter" DataType="SINT" Radix="Decimal" Value="13"/>
<DataValueMember Name="InputOnOffFilter" DataType="SINT" Radix="Decimal" Value="13"/>
</StructureMember>
<StructureMember Name="Pt03" DataType="AB:5000_DI_Channel:C:0">
<DataValueMember Name="InputOffOnFilter" DataType="SINT" Radix="Decimal" Value="13"/>
<DataValueMember Name="InputOnOffFilter" DataType="SINT" Radix="Decimal" Value="13"/>
</StructureMember>
<StructureMember Name="Pt04" DataType="AB:5000_DI_Channel:C:0">
<DataValueMember Name="InputOffOnFilter" DataType="SINT" Radix="Decimal" Value="13"/>
<DataValueMember Name="InputOnOffFilter" DataType="SINT" Radix="Decimal" Value="13"/>
</StructureMember>
<StructureMember Name="Pt05" DataType="AB:5000_DI_Channel:C:0">
<DataValueMember Name="InputOffOnFilter" DataType="SINT" Radix="Decimal" Value="13"/>
<DataValueMember Name="InputOnOffFilter" DataType="SINT" Radix="Decimal" Value="13"/>
</StructureMember>
<StructureMember Name="Pt06" DataType="AB:5000_DI_Channel:C:0">
<DataValueMember Name="InputOffOnFilter" DataType="SINT" Radix="Decimal" Value="13"/>
<DataValueMember Name="InputOnOffFilter" DataType="SINT" Radix="Decimal" Value="13"/>
</StructureMember>
<StructureMember Name="Pt07" DataType="AB:5000_DI_Channel:C:0">
<DataValueMember Name="InputOffOnFilter" DataType="SINT" Radix="Decimal" Value="13"/>
<DataValueMember Name="InputOnOffFilter" DataType="SINT" Radix="Decimal" Value="13"/>
</StructureMember>
<StructureMember Name="Pt08" DataType="AB:5000_DI_Channel:C:0">
<DataValueMember Name="InputOffOnFilter" DataType="SINT" Radix="Decimal" Value="13"/>
<DataValueMember Name="InputOnOffFilter" DataType="SINT" Radix="Decimal" Value="13"/>
</StructureMember>
<StructureMember Name="Pt09" DataType="AB:5000_DI_Channel:C:0">
<DataValueMember Name="InputOffOnFilter" DataType="SINT" Radix="Decimal" Value="13"/>
<DataValueMember Name="InputOnOffFilter" DataType="SINT" Radix="Decimal" Value="13"/>
</StructureMember>
<StructureMember Name="Pt10" DataType="AB:5000_DI_Channel:C:0">
<DataValueMember Name="InputOffOnFilter" DataType="SINT" Radix="Decimal" Value="13"/>
<DataValueMember Name="InputOnOffFilter" DataType="SINT" Radix="Decimal" Value="13"/>
</StructureMember>
<StructureMember Name="Pt11" DataType="AB:5000_DI_Channel:C:0">
<DataValueMember Name="InputOffOnFilter" DataType="SINT" Radix="Decimal" Value="13"/>
<DataValueMember Name="InputOnOffFilter" DataType="SINT" Radix="Decimal" Value="13"/>
</StructureMember>
<StructureMember Name="Pt12" DataType="AB:5000_DI_Channel:C:0">
<DataValueMember Name="InputOffOnFilter" DataType="SINT" Radix="Decimal" Value="13"/>
<DataValueMember Name="InputOnOffFilter" DataType="SINT" Radix="Decimal" Value="13"/>
</StructureMember>
<StructureMember Name="Pt13" DataType="AB:5000_DI_Channel:C:0">
<DataValueMember Name="InputOffOnFilter" DataType="SINT" Radix="Decimal" Value="13"/>
<DataValueMember Name="InputOnOffFilter" DataType="SINT" Radix="Decimal" Value="13"/>
</StructureMember>
<StructureMember Name="Pt14" DataType="AB:5000_DI_Channel:C:0">
<DataValueMember Name="InputOffOnFilter" DataType="SINT" Radix="Decimal" Value="13"/>
<DataValueMember Name="InputOnOffFilter" DataType="SINT" Radix="Decimal" Value="13"/>
</StructureMember>
<StructureMember Name="Pt15" DataType="AB:5000_DI_Channel:C:0">
<DataValueMember Name="InputOffOnFilter" DataType="SINT" Radix="Decimal" Value="13"/>
<DataValueMember Name="InputOnOffFilter" DataType="SINT" Radix="Decimal" Value="13"/>
</StructureMember>
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="InputData" RPI="5000" Type="StandardDataDriven" OutputSize="0" InputSize="68" EventID="0" ProgrammaticallySendEventTrigger="false" Priority="Scheduled" InputConnectionType="Unicast" InputProductionTrigger="Cyclic" ConnectionPath="20 04 24 a0 2c c7 2c 9a"
 InputTagSuffix="I">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:5000_DI16:I:0">
<DataValueMember Name="RunMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="0"/>
<DataValueMember Name="DiagnosticActive" DataType="BOOL" Value="0"/>
<DataValueMember Name="DiagnosticSequenceCount" DataType="SINT" Radix="Decimal" Value="0"/>
<StructureMember Name="Pt00" DataType="CHANNEL_DI:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt01" DataType="CHANNEL_DI:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt02" DataType="CHANNEL_DI:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt03" DataType="CHANNEL_DI:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt04" DataType="CHANNEL_DI:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt05" DataType="CHANNEL_DI:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt06" DataType="CHANNEL_DI:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt07" DataType="CHANNEL_DI:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt08" DataType="CHANNEL_DI:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt09" DataType="CHANNEL_DI:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt10" DataType="CHANNEL_DI:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt11" DataType="CHANNEL_DI:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt12" DataType="CHANNEL_DI:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt13" DataType="CHANNEL_DI:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt14" DataType="CHANNEL_DI:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt15" DataType="CHANNEL_DI:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
</Structure>
</Data>
</InputTag>
</Connection>
</Connections>
</Communications>
<ExtendedProperties>
<public><Vendor>Rockwell Automation/Allen-Bradley</Vendor><CatNum>5069-IB16</CatNum><ConfigID>500</ConfigID><ADDAVersion>1</ADDAVersion></public>
</ExtendedProperties>
</Module>
""",
    '5069-IF8/B': """\
<Module CatalogNumber="5069-IF8/B" Vendor="1" ProductType="115" ProductCode="312" Major="3" Minor="1" ParentModule="AENT" ParentModPortId="1" Inhibited="false" MajorFault="false" SafetyEnabled="false"
 AutoDiagsEnabled="true">
<EKey State="CompatibleModule"/>
<Ports>
<Port Id="1" Address="3" Type="5069" Upstream="true"/>
</Ports>
<Communications>
<ConfigTag ConfigSize="384" ExternalAccess="Read/Write">
<Data Format="L5K">
<![CDATA[[388,165,[4,0,2,1,0,0,0.00000000e+000,2.00000000e+001,0.00000000e+000,1.00000000e+002,0.00000000e+000
		,0.00000000e+000,1.00000000e+002,1.00000000e+002,0.00000000e+000,0.00000000e+000],[4,0,2,1,0,0
		,0.00000000e+000,2.00000000e+001,0.00000000e+000,1.00000000e+002,0.00000000e+000,0.00000000e+000
		,1.00000000e+002,1.00000000e+002,0.00000000e+000,0.00000000e+000],[4,0,2,1,0,0,0.00000000e+000
		,2.00000000e+001,0.00000000e+000,1.00000000e+002,0.00000000e+000,0.00000000e+000,1.00000000e+002
		,1.00000000e+002,0.00000000e+000,0.00000000e+000],[4,0,2,1,0,0,0.00000000e+000,2.00000000e+001
		,0.00000000e+000,1.00000000e+002,0.00000000e+000,0.00000000e+000,1.00000000e+002,1.00000000e+002
		,0.00000000e+000,0.00000000e+000],[4,0,2,1,0,0,0.00000000e+000,2.00000000e+001,0.00000000e+000
		,1.00000000e+002,0.00000000e+000,0.00000000e+000,1.00000000e+002,1.00000000e+002,0.00000000e+000
		,0.00000000e+000],[4,0,2,1,0,0,0.00000000e+000,2.00000000e+001,0.00000000e+000,1.00000000e+002
		,0.00000000e+000,0.00000000e+000,1.00000000e+002,1.00000000e+002,0.00000000e+000,0.00000000e+000
		],[4,0,2,1,0,0,0.00000000e+000,2.00000000e+001,0.00000000e+000,1.00000000e+002,0.00000000e+000
		,0.00000000e+000,1.00000000e+002,1.00000000e+002,0.00000000e+000,0.00000000e+000],[4,0,2,1,0,0
		,0.00000000e+000,2.00000000e+001,0.00000000e+000,1.00000000e+002,0.00000000e+000,0.00000000e+000
		,1.00000000e+002,1.00000000e+002,0.00000000e+000,0.00000000e+000]]]]>
</Data>
<Data Format="Decorated">
<Structure DataType="AB:5000_AI8:C:0">
<StructureMember Name="Ch00" DataType="AB:5000_AI_Channel:C:0">
<DataValueMember Name="Range" DataType="SINT" Radix="Decimal" Value="4"/>
<DataValueMember Name="SensorType" DataType="SINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="NotchFilter" DataType="SINT" Radix="Decimal" Value="2"/>
<DataValueMember Name="AlarmDisable" DataType="BOOL" Value="1"/>
<DataValueMember Name="ProcessAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="RateAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="OpenWireEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="Disable" DataType="BOOL" Value="0"/>
<DataValueMember Name="TenOhmOffset" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="DigitalFilter" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="LowSignal" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighSignal" DataType="REAL" Radix="Float" Value="20.0"/>
<DataValueMember Name="LowEngineering" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighEngineering" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="LLAlarmLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="LAlarmLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HAlarmLimit" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="HHAlarmLimit" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="RateAlarmLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="AlarmDeadband" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
<StructureMember Name="Ch01" DataType="AB:5000_AI_Channel:C:0">
<DataValueMember Name="Range" DataType="SINT" Radix="Decimal" Value="4"/>
<DataValueMember Name="SensorType" DataType="SINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="NotchFilter" DataType="SINT" Radix="Decimal" Value="2"/>
<DataValueMember Name="AlarmDisable" DataType="BOOL" Value="1"/>
<DataValueMember Name="ProcessAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="RateAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="OpenWireEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="Disable" DataType="BOOL" Value="0"/>
<DataValueMember Name="TenOhmOffset" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="DigitalFilter" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="LowSignal" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighSignal" DataType="REAL" Radix="Float" Value="20.0"/>
<DataValueMember Name="LowEngineering" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighEngineering" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="LLAlarmLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="LAlarmLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HAlarmLimit" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="HHAlarmLimit" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="RateAlarmLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="AlarmDeadband" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
<StructureMember Name="Ch02" DataType="AB:5000_AI_Channel:C:0">
<DataValueMember Name="Range" DataType="SINT" Radix="Decimal" Value="4"/>
<DataValueMember Name="SensorType" DataType="SINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="NotchFilter" DataType="SINT" Radix="Decimal" Value="2"/>
<DataValueMember Name="AlarmDisable" DataType="BOOL" Value="1"/>
<DataValueMember Name="ProcessAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="RateAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="OpenWireEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="Disable" DataType="BOOL" Value="0"/>
<DataValueMember Name="TenOhmOffset" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="DigitalFilter" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="LowSignal" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighSignal" DataType="REAL" Radix="Float" Value="20.0"/>
<DataValueMember Name="LowEngineering" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighEngineering" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="LLAlarmLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="LAlarmLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HAlarmLimit" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="HHAlarmLimit" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="RateAlarmLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="AlarmDeadband" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
<StructureMember Name="Ch03" DataType="AB:5000_AI_Channel:C:0">
<DataValueMember Name="Range" DataType="SINT" Radix="Decimal" Value="4"/>
<DataValueMember Name="SensorType" DataType="SINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="NotchFilter" DataType="SINT" Radix="Decimal" Value="2"/>
<DataValueMember Name="AlarmDisable" DataType="BOOL" Value="1"/>
<DataValueMember Name="ProcessAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="RateAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="OpenWireEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="Disable" DataType="BOOL" Value="0"/>
<DataValueMember Name="TenOhmOffset" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="DigitalFilter" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="LowSignal" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighSignal" DataType="REAL" Radix="Float" Value="20.0"/>
<DataValueMember Name="LowEngineering" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighEngineering" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="LLAlarmLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="LAlarmLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HAlarmLimit" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="HHAlarmLimit" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="RateAlarmLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="AlarmDeadband" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
<StructureMember Name="Ch04" DataType="AB:5000_AI_Channel:C:0">
<DataValueMember Name="Range" DataType="SINT" Radix="Decimal" Value="4"/>
<DataValueMember Name="SensorType" DataType="SINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="NotchFilter" DataType="SINT" Radix="Decimal" Value="2"/>
<DataValueMember Name="AlarmDisable" DataType="BOOL" Value="1"/>
<DataValueMember Name="ProcessAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="RateAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="OpenWireEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="Disable" DataType="BOOL" Value="0"/>
<DataValueMember Name="TenOhmOffset" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="DigitalFilter" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="LowSignal" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighSignal" DataType="REAL" Radix="Float" Value="20.0"/>
<DataValueMember Name="LowEngineering" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighEngineering" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="LLAlarmLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="LAlarmLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HAlarmLimit" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="HHAlarmLimit" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="RateAlarmLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="AlarmDeadband" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
<StructureMember Name="Ch05" DataType="AB:5000_AI_Channel:C:0">
<DataValueMember Name="Range" DataType="SINT" Radix="Decimal" Value="4"/>
<DataValueMember Name="SensorType" DataType="SINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="NotchFilter" DataType="SINT" Radix="Decimal" Value="2"/>
<DataValueMember Name="AlarmDisable" DataType="BOOL" Value="1"/>
<DataValueMember Name="ProcessAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="RateAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="OpenWireEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="Disable" DataType="BOOL" Value="0"/>
<DataValueMember Name="TenOhmOffset" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="DigitalFilter" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="LowSignal" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighSignal" DataType="REAL" Radix="Float" Value="20.0"/>
<DataValueMember Name="LowEngineering" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighEngineering" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="LLAlarmLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="LAlarmLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HAlarmLimit" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="HHAlarmLimit" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="RateAlarmLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="AlarmDeadband" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
<StructureMember Name="Ch06" DataType="AB:5000_AI_Channel:C:0">
<DataValueMember Name="Range" DataType="SINT" Radix="Decimal" Value="4"/>
<DataValueMember Name="SensorType" DataType="SINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="NotchFilter" DataType="SINT" Radix="Decimal" Value="2"/>
<DataValueMember Name="AlarmDisable" DataType="BOOL" Value="1"/>
<DataValueMember Name="ProcessAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="RateAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="OpenWireEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="Disable" DataType="BOOL" Value="0"/>
<DataValueMember Name="TenOhmOffset" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="DigitalFilter" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="LowSignal" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighSignal" DataType="REAL" Radix="Float" Value="20.0"/>
<DataValueMember Name="LowEngineering" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighEngineering" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="LLAlarmLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="LAlarmLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HAlarmLimit" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="HHAlarmLimit" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="RateAlarmLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="AlarmDeadband" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
<StructureMember Name="Ch07" DataType="AB:5000_AI_Channel:C:0">
<DataValueMember Name="Range" DataType="SINT" Radix="Decimal" Value="4"/>
<DataValueMember Name="SensorType" DataType="SINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="NotchFilter" DataType="SINT" Radix="Decimal" Value="2"/>
<DataValueMember Name="AlarmDisable" DataType="BOOL" Value="1"/>
<DataValueMember Name="ProcessAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="RateAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="OpenWireEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="Disable" DataType="BOOL" Value="0"/>
<DataValueMember Name="TenOhmOffset" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="DigitalFilter" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="LowSignal" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighSignal" DataType="REAL" Radix="Float" Value="20.0"/>
<DataValueMember Name="LowEngineering" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighEngineering" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="LLAlarmLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="LAlarmLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HAlarmLimit" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="HHAlarmLimit" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="RateAlarmLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="AlarmDeadband" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
</Structure>
</Data>
</ConfigTag>
<ConfigScript Size="612">
<Data Format="L5K">
<![CDATA[[96,2,0,0,4,0,0,0,0,0,0,0,0,0,0,0,78,2,0,0,7,1,0,0,0,3,0,0,0,-128,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,16,31,0,0,0,0,0,0,0,0,0,0,0,96,1,0,0,32,0,0,0,32,0,0,0,31,0,0,0,-128,1,0,0,-128,1,0,0,96,1,0,0,-96,1,0,0,-96,1
		,0,0,31,0,0,0,0,3,0,0,0,3,0,0,96,1,0,0,32,3,0,0,32,3,0,0,31,0,0,0,-128,4,0,0,-128,4,0,0,96,1,0,0,-96,4,0,0,-96,4,0,0,31,0,0,0,0,6,0,0,0,6,0,0,96
		,1,0,0,32,6,0,0,32,6,0,0,31,0,0,0,-128,7,0,0,-128,7,0,0,96,1,0,0,-96,7,0,0,-96,7,0,0,31,0,0,0,0,9,0,0,0,9,0,0,96,1,0,0,32,9,0,0,32,9,0,0,31,0,0
		,0,-128,10,0,0,-128,10,0,0,96,1,0,0,-96,10,0,0,-96,10,0,0,0,0]]]>
</Data>
</ConfigScript>
<Connections>
<Connection Name="InputData" RPI="100000" Type="StandardDataDriven" OutputSize="64" InputSize="100" EventID="0" ProgrammaticallySendEventTrigger="false" Priority="Scheduled" InputConnectionType="Unicast" InputProductionTrigger="Cyclic" ConnectionPath="20 04 24 a5 2c 6a 2c 8b"
 InputTagSuffix="I" OutputTagSuffix="O">
<InputTag ExternalAccess="Read/Write">
<EngineeringUnits>
<EngineeringUnit Operand=".CH00.DATA">
<![CDATA[%]]>
</EngineeringUnit>
<EngineeringUnit Operand=".CH01.DATA">
<![CDATA[%]]>
</EngineeringUnit>
<EngineeringUnit Operand=".CH02.DATA">
<![CDATA[%]]>
</EngineeringUnit>
<EngineeringUnit Operand=".CH03.DATA">
<![CDATA[%]]>
</EngineeringUnit>
<EngineeringUnit Operand=".CH04.DATA">
<![CDATA[%]]>
</EngineeringUnit>
<EngineeringUnit Operand=".CH05.DATA">
<![CDATA[%]]>
</EngineeringUnit>
<EngineeringUnit Operand=".CH06.DATA">
<![CDATA[%]]>
</EngineeringUnit>
<EngineeringUnit Operand=".CH07.DATA">
<![CDATA[%]]>
</EngineeringUnit>
</EngineeringUnits>
<Data Format="Decorated">
<Structure DataType="AB:5000_AI8:I:0">
<DataValueMember Name="RunMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="0"/>
<DataValueMember Name="DiagnosticActive" DataType="BOOL" Value="0"/>
<DataValueMember Name="DiagnosticSequenceCount" DataType="SINT" Radix="Decimal" Value="0"/>
<StructureMember Name="Ch00" DataType="CHANNEL_AI_DIAG:I:0">
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="OpenWire" DataType="BOOL" Value="0"/>
<DataValueMember Name="OverTemperature" DataType="BOOL" Value="0"/>
<DataValueMember Name="FieldPowerOff" DataType="BOOL" Value="0"/>
<DataValueMember Name="NotANumber" DataType="BOOL" Value="0"/>
<DataValueMember Name="Underrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="Overrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="LLAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="LAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="HAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="HHAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="RateAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="CalFault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Calibrating" DataType="BOOL" Value="0"/>
<DataValueMember Name="Data" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="RollingTimestamp" DataType="INT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Ch01" DataType="CHANNEL_AI_DIAG:I:0">
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="OpenWire" DataType="BOOL" Value="0"/>
<DataValueMember Name="OverTemperature" DataType="BOOL" Value="0"/>
<DataValueMember Name="FieldPowerOff" DataType="BOOL" Value="0"/>
<DataValueMember Name="NotANumber" DataType="BOOL" Value="0"/>
<DataValueMember Name="Underrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="Overrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="LLAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="LAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="HAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="HHAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="RateAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="CalFault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Calibrating" DataType="BOOL" Value="0"/>
<DataValueMember Name="Data" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="RollingTimestamp" DataType="INT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Ch02" DataType="CHANNEL_AI_DIAG:I:0">
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="OpenWire" DataType="BOOL" Value="0"/>
<DataValueMember Name="OverTemperature" DataType="BOOL" Value="0"/>
<DataValueMember Name="FieldPowerOff" DataType="BOOL" Value="0"/>
<DataValueMember Name="NotANumber" DataType="BOOL" Value="0"/>
<DataValueMember Name="Underrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="Overrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="LLAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="LAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="HAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="HHAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="RateAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="CalFault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Calibrating" DataType="BOOL" Value="0"/>
<DataValueMember Name="Data" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="RollingTimestamp" DataType="INT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Ch03" DataType="CHANNEL_AI_DIAG:I:0">
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="OpenWire" DataType="BOOL" Value="0"/>
<DataValueMember Name="OverTemperature" DataType="BOOL" Value="0"/>
<DataValueMember Name="FieldPowerOff" DataType="BOOL" Value="0"/>
<DataValueMember Name="NotANumber" DataType="BOOL" Value="0"/>
<DataValueMember Name="Underrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="Overrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="LLAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="LAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="HAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="HHAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="RateAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="CalFault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Calibrating" DataType="BOOL" Value="0"/>
<DataValueMember Name="Data" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="RollingTimestamp" DataType="INT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Ch04" DataType="CHANNEL_AI_DIAG:I:0">
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="OpenWire" DataType="BOOL" Value="0"/>
<DataValueMember Name="OverTemperature" DataType="BOOL" Value="0"/>
<DataValueMember Name="FieldPowerOff" DataType="BOOL" Value="0"/>
<DataValueMember Name="NotANumber" DataType="BOOL" Value="0"/>
<DataValueMember Name="Underrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="Overrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="LLAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="LAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="HAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="HHAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="RateAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="CalFault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Calibrating" DataType="BOOL" Value="0"/>
<DataValueMember Name="Data" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="RollingTimestamp" DataType="INT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Ch05" DataType="CHANNEL_AI_DIAG:I:0">
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="OpenWire" DataType="BOOL" Value="0"/>
<DataValueMember Name="OverTemperature" DataType="BOOL" Value="0"/>
<DataValueMember Name="FieldPowerOff" DataType="BOOL" Value="0"/>
<DataValueMember Name="NotANumber" DataType="BOOL" Value="0"/>
<DataValueMember Name="Underrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="Overrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="LLAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="LAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="HAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="HHAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="RateAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="CalFault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Calibrating" DataType="BOOL" Value="0"/>
<DataValueMember Name="Data" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="RollingTimestamp" DataType="INT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Ch06" DataType="CHANNEL_AI_DIAG:I:0">
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="OpenWire" DataType="BOOL" Value="0"/>
<DataValueMember Name="OverTemperature" DataType="BOOL" Value="0"/>
<DataValueMember Name="FieldPowerOff" DataType="BOOL" Value="0"/>
<DataValueMember Name="NotANumber" DataType="BOOL" Value="0"/>
<DataValueMember Name="Underrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="Overrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="LLAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="LAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="HAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="HHAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="RateAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="CalFault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Calibrating" DataType="BOOL" Value="0"/>
<DataValueMember Name="Data" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="RollingTimestamp" DataType="INT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Ch07" DataType="CHANNEL_AI_DIAG:I:0">
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="OpenWire" DataType="BOOL" Value="0"/>
<DataValueMember Name="OverTemperature" DataType="BOOL" Value="0"/>
<DataValueMember Name="FieldPowerOff" DataType="BOOL" Value="0"/>
<DataValueMember Name="NotANumber" DataType="BOOL" Value="0"/>
<DataValueMember Name="Underrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="Overrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="LLAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="LAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="HAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="HHAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="RateAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="CalFault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Calibrating" DataType="BOOL" Value="0"/>
<DataValueMember Name="Data" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="RollingTimestamp" DataType="INT" Radix="Decimal" Value="0"/>
</StructureMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
<![CDATA[[[0,0,0,0.00000000e+000],[0,0,0,0.00000000e+000],[0,0,0,0.00000000e+000],[0,0,0,0.00000000e+000],[0,0,0,0.00000000e+000
		],[0,0,0,0.00000000e+000],[0,0,0,0.00000000e+000],[0,0,0,0.00000000e+000]]]]>
</Data>
<Data Format="Decorated">
<Structure DataType="AB:5000_AI8:O:0">
<StructureMember Name="Ch00" DataType="CHANNEL_AI:O:0">
<DataValueMember Name="LLAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="LAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="HAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="HHAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="RateAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="LLAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="LAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="HAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="HHAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="RateAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="SensorOffset" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
<StructureMember Name="Ch01" DataType="CHANNEL_AI:O:0">
<DataValueMember Name="LLAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="LAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="HAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="HHAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="RateAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="LLAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="LAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="HAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="HHAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="RateAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="SensorOffset" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
<StructureMember Name="Ch02" DataType="CHANNEL_AI:O:0">
<DataValueMember Name="LLAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="LAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="HAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="HHAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="RateAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="LLAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="LAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="HAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="HHAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="RateAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="SensorOffset" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
<StructureMember Name="Ch03" DataType="CHANNEL_AI:O:0">
<DataValueMember Name="LLAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="LAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="HAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="HHAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="RateAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="LLAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="LAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="HAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="HHAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="RateAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="SensorOffset" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
<StructureMember Name="Ch04" DataType="CHANNEL_AI:O:0">
<DataValueMember Name="LLAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="LAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="HAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="HHAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="RateAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="LLAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="LAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="HAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="HHAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="RateAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="SensorOffset" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
<StructureMember Name="Ch05" DataType="CHANNEL_AI:O:0">
<DataValueMember Name="LLAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="LAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="HAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="HHAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="RateAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="LLAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="LAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="HAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="HHAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="RateAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="SensorOffset" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
<StructureMember Name="Ch06" DataType="CHANNEL_AI:O:0">
<DataValueMember Name="LLAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="LAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="HAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="HHAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="RateAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="LLAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="LAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="HAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="HHAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="RateAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="SensorOffset" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
<StructureMember Name="Ch07" DataType="CHANNEL_AI:O:0">
<DataValueMember Name="LLAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="LAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="HAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="HHAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="RateAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="LLAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="LAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="HAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="HHAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="RateAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="SensorOffset" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
<ExtendedProperties>
<public><Vendor>Rockwell Automation/Allen-Bradley</Vendor><CatNum>5069-IF8</CatNum><ConfigID>101</ConfigID><ADDAVersion>1</ADDAVersion></public>
</ExtendedProperties>
</Module>
""",
    '5069-IY4/A': """\
<Module CatalogNumber="5069-IY4/A" Vendor="1" ProductType="115" ProductCode="314" Major="2" Minor="1" ParentModule="AENT" ParentModPortId="1" Inhibited="false" MajorFault="false" SafetyEnabled="false"
 AutoDiagsEnabled="true">
<EKey State="CompatibleModule"/>
<Ports>
<Port Id="1" Address="4" Type="5069" Upstream="true"/>
</Ports>
<Communications>
<ConfigTag ConfigSize="208" ExternalAccess="Read/Write">
<Data Format="L5K">
<![CDATA[[212,122,[0,0,0,0.00000000e+000],[0,0,0,0.00000000e+000],[4,0,2,1,0,0,0.00000000e+000,2.00000000e+001,0.00000000e+000
		,1.00000000e+002,0.00000000e+000,0.00000000e+000,1.00000000e+002,1.00000000e+002,0.00000000e+000
		,0.00000000e+000],[4,0,2,1,0,0,0.00000000e+000,2.00000000e+001,0.00000000e+000,1.00000000e+002
		,0.00000000e+000,0.00000000e+000,1.00000000e+002,1.00000000e+002,0.00000000e+000,0.00000000e+000
		],[4,0,2,1,0,0,0.00000000e+000,2.00000000e+001,0.00000000e+000,1.00000000e+002,0.00000000e+000
		,0.00000000e+000,1.00000000e+002,1.00000000e+002,0.00000000e+000,0.00000000e+000],[4,0,2,1,0,0
		,0.00000000e+000,2.00000000e+001,0.00000000e+000,1.00000000e+002,0.00000000e+000,0.00000000e+000
		,1.00000000e+002,1.00000000e+002,0.00000000e+000,0.00000000e+000]]]]>
</Data>
<Data Format="Decorated">
<Structure DataType="AB:5000_AI4CJ:C:0">
<StructureMember Name="CJCh00" DataType="AB:5000_AI_CJ_Channel:C:0">
<DataValueMember Name="Disable" DataType="BOOL" Value="0"/>
<DataValueMember Name="Remote" DataType="BOOL" Value="0"/>
<DataValueMember Name="SensorOffset" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
<StructureMember Name="CJCh01" DataType="AB:5000_AI_CJ_Channel:C:0">
<DataValueMember Name="Disable" DataType="BOOL" Value="0"/>
<DataValueMember Name="Remote" DataType="BOOL" Value="0"/>
<DataValueMember Name="SensorOffset" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
<StructureMember Name="Ch00" DataType="AB:5000_AI_Channel:C:0">
<DataValueMember Name="Range" DataType="SINT" Radix="Decimal" Value="4"/>
<DataValueMember Name="SensorType" DataType="SINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="NotchFilter" DataType="SINT" Radix="Decimal" Value="2"/>
<DataValueMember Name="AlarmDisable" DataType="BOOL" Value="1"/>
<DataValueMember Name="ProcessAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="RateAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="OpenWireEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="Disable" DataType="BOOL" Value="0"/>
<DataValueMember Name="TenOhmOffset" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="DigitalFilter" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="LowSignal" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighSignal" DataType="REAL" Radix="Float" Value="20.0"/>
<DataValueMember Name="LowEngineering" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighEngineering" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="LLAlarmLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="LAlarmLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HAlarmLimit" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="HHAlarmLimit" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="RateAlarmLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="AlarmDeadband" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
<StructureMember Name="Ch01" DataType="AB:5000_AI_Channel:C:0">
<DataValueMember Name="Range" DataType="SINT" Radix="Decimal" Value="4"/>
<DataValueMember Name="SensorType" DataType="SINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="NotchFilter" DataType="SINT" Radix="Decimal" Value="2"/>
<DataValueMember Name="AlarmDisable" DataType="BOOL" Value="1"/>
<DataValueMember Name="ProcessAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="RateAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="OpenWireEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="Disable" DataType="BOOL" Value="0"/>
<DataValueMember Name="TenOhmOffset" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="DigitalFilter" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="LowSignal" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighSignal" DataType="REAL" Radix="Float" Value="20.0"/>
<DataValueMember Name="LowEngineering" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighEngineering" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="LLAlarmLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="LAlarmLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HAlarmLimit" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="HHAlarmLimit" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="RateAlarmLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="AlarmDeadband" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
<StructureMember Name="Ch02" DataType="AB:5000_AI_Channel:C:0">
<DataValueMember Name="Range" DataType="SINT" Radix="Decimal" Value="4"/>
<DataValueMember Name="SensorType" DataType="SINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="NotchFilter" DataType="SINT" Radix="Decimal" Value="2"/>
<DataValueMember Name="AlarmDisable" DataType="BOOL" Value="1"/>
<DataValueMember Name="ProcessAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="RateAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="OpenWireEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="Disable" DataType="BOOL" Value="0"/>
<DataValueMember Name="TenOhmOffset" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="DigitalFilter" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="LowSignal" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighSignal" DataType="REAL" Radix="Float" Value="20.0"/>
<DataValueMember Name="LowEngineering" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighEngineering" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="LLAlarmLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="LAlarmLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HAlarmLimit" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="HHAlarmLimit" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="RateAlarmLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="AlarmDeadband" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
<StructureMember Name="Ch03" DataType="AB:5000_AI_Channel:C:0">
<DataValueMember Name="Range" DataType="SINT" Radix="Decimal" Value="4"/>
<DataValueMember Name="SensorType" DataType="SINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="NotchFilter" DataType="SINT" Radix="Decimal" Value="2"/>
<DataValueMember Name="AlarmDisable" DataType="BOOL" Value="1"/>
<DataValueMember Name="ProcessAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="RateAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="OpenWireEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="Disable" DataType="BOOL" Value="0"/>
<DataValueMember Name="TenOhmOffset" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="DigitalFilter" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="LowSignal" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighSignal" DataType="REAL" Radix="Float" Value="20.0"/>
<DataValueMember Name="LowEngineering" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighEngineering" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="LLAlarmLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="LAlarmLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HAlarmLimit" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="HHAlarmLimit" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="RateAlarmLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="AlarmDeadband" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
</Structure>
</Data>
</ConfigTag>
<ConfigScript Size="340">
<Data Format="L5K">
<![CDATA[[80,1,0,0,4,0,0,0,0,0,0,0,0,0,0,0,62,1,0,0,7,1,0,0,0,3,0,0,0,-48,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,8,-97,0,0,0,0,0,0,0,0,0,0,0,96,1,0,0,-96,0,0,0,-96,0,0,0,31,0,0,0,0,2,0,0,0,2,0,0,96,1,0,0,32,2,0,0,32,2,0,0,31,0,0,0,-128,3,0,0,-128,3,0,0
		,96,1,0,0,-96,3,0,0,-96,3,0,0,31,0,0,0,0,5,0,0,0,5,0,0,96,1,0,0,32,5,0,0,32,5,0,0,0,0]]]>
</Data>
</ConfigScript>
<Connections>
<Connection Name="InputData" RPI="100000" Type="StandardDataDriven" OutputSize="32" InputSize="68" EventID="0" ProgrammaticallySendEventTrigger="false" Priority="Scheduled" InputConnectionType="Unicast" InputProductionTrigger="Cyclic" ConnectionPath="20 04 24 7a 2c 66 2c 98"
 InputTagSuffix="I" OutputTagSuffix="O">
<InputTag ExternalAccess="Read/Write">
<EngineeringUnits>
<EngineeringUnit Operand=".CH00.DATA">
<![CDATA[%]]>
</EngineeringUnit>
<EngineeringUnit Operand=".CH01.DATA">
<![CDATA[%]]>
</EngineeringUnit>
<EngineeringUnit Operand=".CH02.DATA">
<![CDATA[%]]>
</EngineeringUnit>
<EngineeringUnit Operand=".CH03.DATA">
<![CDATA[%]]>
</EngineeringUnit>
</EngineeringUnits>
<Data Format="Decorated">
<Structure DataType="AB:5000_AI4CJ:I:0">
<DataValueMember Name="RunMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="0"/>
<DataValueMember Name="DiagnosticActive" DataType="BOOL" Value="0"/>
<DataValueMember Name="DiagnosticSequenceCount" DataType="SINT" Radix="Decimal" Value="0"/>
<StructureMember Name="CJCh00" DataType="CHANNEL_AI_CJ_DIAG:I:0">
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="OpenWire" DataType="BOOL" Value="0"/>
<DataValueMember Name="FieldPowerOff" DataType="BOOL" Value="0"/>
<DataValueMember Name="Underrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="Overrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="Temperature" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
<StructureMember Name="CJCh01" DataType="CHANNEL_AI_CJ_DIAG:I:0">
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="OpenWire" DataType="BOOL" Value="0"/>
<DataValueMember Name="FieldPowerOff" DataType="BOOL" Value="0"/>
<DataValueMember Name="Underrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="Overrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="Temperature" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
<StructureMember Name="Ch00" DataType="CHANNEL_AI_DIAG:I:0">
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="OpenWire" DataType="BOOL" Value="0"/>
<DataValueMember Name="OverTemperature" DataType="BOOL" Value="0"/>
<DataValueMember Name="FieldPowerOff" DataType="BOOL" Value="0"/>
<DataValueMember Name="NotANumber" DataType="BOOL" Value="0"/>
<DataValueMember Name="Underrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="Overrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="LLAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="LAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="HAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="HHAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="RateAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="CalFault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Calibrating" DataType="BOOL" Value="0"/>
<DataValueMember Name="Data" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="RollingTimestamp" DataType="INT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Ch01" DataType="CHANNEL_AI_DIAG:I:0">
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="OpenWire" DataType="BOOL" Value="0"/>
<DataValueMember Name="OverTemperature" DataType="BOOL" Value="0"/>
<DataValueMember Name="FieldPowerOff" DataType="BOOL" Value="0"/>
<DataValueMember Name="NotANumber" DataType="BOOL" Value="0"/>
<DataValueMember Name="Underrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="Overrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="LLAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="LAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="HAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="HHAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="RateAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="CalFault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Calibrating" DataType="BOOL" Value="0"/>
<DataValueMember Name="Data" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="RollingTimestamp" DataType="INT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Ch02" DataType="CHANNEL_AI_DIAG:I:0">
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="OpenWire" DataType="BOOL" Value="0"/>
<DataValueMember Name="OverTemperature" DataType="BOOL" Value="0"/>
<DataValueMember Name="FieldPowerOff" DataType="BOOL" Value="0"/>
<DataValueMember Name="NotANumber" DataType="BOOL" Value="0"/>
<DataValueMember Name="Underrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="Overrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="LLAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="LAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="HAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="HHAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="RateAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="CalFault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Calibrating" DataType="BOOL" Value="0"/>
<DataValueMember Name="Data" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="RollingTimestamp" DataType="INT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Ch03" DataType="CHANNEL_AI_DIAG:I:0">
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="OpenWire" DataType="BOOL" Value="0"/>
<DataValueMember Name="OverTemperature" DataType="BOOL" Value="0"/>
<DataValueMember Name="FieldPowerOff" DataType="BOOL" Value="0"/>
<DataValueMember Name="NotANumber" DataType="BOOL" Value="0"/>
<DataValueMember Name="Underrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="Overrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="LLAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="LAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="HAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="HHAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="RateAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="CalFault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Calibrating" DataType="BOOL" Value="0"/>
<DataValueMember Name="Data" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="RollingTimestamp" DataType="INT" Radix="Decimal" Value="0"/>
</StructureMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
<![CDATA[[[0,0,0,0.00000000e+000],[0,0,0,0.00000000e+000],[0,0,0,0.00000000e+000],[0,0,0,0.00000000e+000]]]]>
</Data>
<Data Format="Decorated">
<Structure DataType="AB:5000_AI4:O:0">
<StructureMember Name="Ch00" DataType="CHANNEL_AI:O:0">
<DataValueMember Name="LLAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="LAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="HAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="HHAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="RateAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="LLAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="LAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="HAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="HHAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="RateAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="SensorOffset" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
<StructureMember Name="Ch01" DataType="CHANNEL_AI:O:0">
<DataValueMember Name="LLAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="LAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="HAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="HHAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="RateAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="LLAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="LAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="HAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="HHAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="RateAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="SensorOffset" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
<StructureMember Name="Ch02" DataType="CHANNEL_AI:O:0">
<DataValueMember Name="LLAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="LAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="HAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="HHAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="RateAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="LLAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="LAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="HAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="HHAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="RateAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="SensorOffset" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
<StructureMember Name="Ch03" DataType="CHANNEL_AI:O:0">
<DataValueMember Name="LLAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="LAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="HAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="HHAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="RateAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="LLAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="LAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="HAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="HHAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="RateAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="SensorOffset" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
<ExtendedProperties>
<public><Vendor>Rockwell Automation/Allen-Bradley</Vendor><CatNum>5069-IY4</CatNum><ConfigID>201</ConfigID><ADDAVersion>1</ADDAVersion></public>
</ExtendedProperties>
</Module>
""",
    '5069-OA16/A': """\
<Module CatalogNumber="5069-OA16/A" Vendor="1" ProductType="7" ProductCode="1215" Major="3" Minor="1" ParentModule="AENT" ParentModPortId="1" Inhibited="false" MajorFault="false" SafetyEnabled="false"
>
<EKey State="CompatibleModule"/>
<Ports>
<Port Id="1" Address="5" Type="5069" Upstream="true"/>
</Ports>
<Communications>
<ConfigTag ConfigSize="64" ExternalAccess="Read/Write">
<Data Format="L5K">
<![CDATA[[68,171,[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]]]]>
</Data>
<Data Format="Decorated">
<Structure DataType="AB:5000_DO16:C:0">
<StructureMember Name="Pt00" DataType="AB:5000_DO_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt01" DataType="AB:5000_DO_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt02" DataType="AB:5000_DO_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt03" DataType="AB:5000_DO_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt04" DataType="AB:5000_DO_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt05" DataType="AB:5000_DO_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt06" DataType="AB:5000_DO_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt07" DataType="AB:5000_DO_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt08" DataType="AB:5000_DO_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt09" DataType="AB:5000_DO_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt10" DataType="AB:5000_DO_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt11" DataType="AB:5000_DO_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt12" DataType="AB:5000_DO_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt13" DataType="AB:5000_DO_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt14" DataType="AB:5000_DO_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt15" DataType="AB:5000_DO_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="OutputData" RPI="5000" Type="StandardDataDriven" OutputSize="64" InputSize="68" EventID="0" ProgrammaticallySendEventTrigger="false" Priority="Scheduled" InputConnectionType="Unicast" InputProductionTrigger="Cyclic" ConnectionPath="20 04 24 ab 2c 64 2d 00 45 03"
 InputTagSuffix="I" OutputTagSuffix="O">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:5000_DO16:I:0">
<DataValueMember Name="RunMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="0"/>
<DataValueMember Name="DiagnosticActive" DataType="BOOL" Value="0"/>
<DataValueMember Name="DiagnosticSequenceCount" DataType="SINT" Radix="Decimal" Value="0"/>
<StructureMember Name="Pt00" DataType="CHANNEL_DO:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt01" DataType="CHANNEL_DO:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt02" DataType="CHANNEL_DO:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt03" DataType="CHANNEL_DO:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt04" DataType="CHANNEL_DO:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt05" DataType="CHANNEL_DO:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt06" DataType="CHANNEL_DO:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt07" DataType="CHANNEL_DO:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt08" DataType="CHANNEL_DO:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt09" DataType="CHANNEL_DO:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt10" DataType="CHANNEL_DO:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt11" DataType="CHANNEL_DO:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt12" DataType="CHANNEL_DO:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt13" DataType="CHANNEL_DO:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt14" DataType="CHANNEL_DO:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt15" DataType="CHANNEL_DO:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
<![CDATA[[[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]]]>
</Data>
<Data Format="Decorated">
<Structure DataType="AB:5000_DO16:O:0">
<StructureMember Name="Pt00" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt01" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt02" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt03" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt04" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt05" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt06" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt07" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt08" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt09" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt10" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt11" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt12" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt13" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt14" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt15" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
<ExtendedProperties>
<public><ConfigID>110</ConfigID><CatNum>5069-OA16</CatNum></public>
</ExtendedProperties>
</Module>
""",
    '5069-OB16/B': """\
<Module CatalogNumber="5069-OB16/B" Vendor="1" ProductType="7" ProductCode="392" Major="3" Minor="1" ParentModule="AENT" ParentModPortId="1" Inhibited="false" MajorFault="false" SafetyEnabled="false"
 AutoDiagsEnabled="true">
<EKey State="CompatibleModule"/>
<Ports>
<Port Id="1" Address="6" Type="5069" Upstream="true"/>
</Ports>
<Communications>
<ConfigTag ConfigSize="64" ExternalAccess="Read/Write">
<Data Format="L5K">
<![CDATA[[68,163,[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]]]]>
</Data>
<Data Format="Decorated">
<Structure DataType="AB:5000_DO16_Diag:C:0">
<StructureMember Name="Pt00" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt01" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt02" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt03" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt04" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt05" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt06" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt07" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt08" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt09" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt10" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt11" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt12" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt13" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt14" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt15" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="OutputData" RPI="5000" Type="StandardDataDriven" OutputSize="64" InputSize="68" EventID="0" ProgrammaticallySendEventTrigger="false" Priority="Scheduled" InputConnectionType="Unicast" InputProductionTrigger="Cyclic" ConnectionPath="20 04 24 a3 2c 64 2c 85"
 InputTagSuffix="I" OutputTagSuffix="O">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:5000_DO16_Diag:I:0">
<DataValueMember Name="RunMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="0"/>
<DataValueMember Name="DiagnosticActive" DataType="BOOL" Value="0"/>
<DataValueMember Name="DiagnosticSequenceCount" DataType="SINT" Radix="Decimal" Value="0"/>
<StructureMember Name="Pt00" DataType="CHANNEL_DO_DIAG:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoad" DataType="BOOL" Value="0"/>
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt01" DataType="CHANNEL_DO_DIAG:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoad" DataType="BOOL" Value="0"/>
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt02" DataType="CHANNEL_DO_DIAG:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoad" DataType="BOOL" Value="0"/>
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt03" DataType="CHANNEL_DO_DIAG:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoad" DataType="BOOL" Value="0"/>
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt04" DataType="CHANNEL_DO_DIAG:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoad" DataType="BOOL" Value="0"/>
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt05" DataType="CHANNEL_DO_DIAG:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoad" DataType="BOOL" Value="0"/>
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt06" DataType="CHANNEL_DO_DIAG:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoad" DataType="BOOL" Value="0"/>
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt07" DataType="CHANNEL_DO_DIAG:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoad" DataType="BOOL" Value="0"/>
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt08" DataType="CHANNEL_DO_DIAG:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoad" DataType="BOOL" Value="0"/>
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt09" DataType="CHANNEL_DO_DIAG:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoad" DataType="BOOL" Value="0"/>
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt10" DataType="CHANNEL_DO_DIAG:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoad" DataType="BOOL" Value="0"/>
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt11" DataType="CHANNEL_DO_DIAG:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoad" DataType="BOOL" Value="0"/>
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt12" DataType="CHANNEL_DO_DIAG:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoad" DataType="BOOL" Value="0"/>
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt13" DataType="CHANNEL_DO_DIAG:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoad" DataType="BOOL" Value="0"/>
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt14" DataType="CHANNEL_DO_DIAG:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoad" DataType="BOOL" Value="0"/>
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt15" DataType="CHANNEL_DO_DIAG:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoad" DataType="BOOL" Value="0"/>
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0"/>
</StructureMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
<![CDATA[[[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]]]>
</Data>
<Data Format="Decorated">
<Structure DataType="AB:5000_DO16:O:0">
<StructureMember Name="Pt00" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt01" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt02" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt03" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt04" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt05" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt06" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt07" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt08" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt09" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt10" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt11" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt12" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt13" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt14" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt15" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
<ExtendedProperties>
<public><Vendor>Rockwell Automation/Allen-Bradley</Vendor><CatNum>5069-OB16</CatNum><ConfigID>110</ConfigID><ADDAVersion>1</ADDAVersion></public>
</ExtendedProperties>
</Module>
""",
    '5069-OB8/A': """\
<Module CatalogNumber="5069-OB8/A" Vendor="1" ProductType="7" ProductCode="1213" Major="3" Minor="1" ParentModule="AENT" ParentModPortId="1" Inhibited="false" MajorFault="false" SafetyEnabled="false"
>
<EKey State="CompatibleModule"/>
<Ports>
<Port Id="1" Address="7" Type="5069" Upstream="true"/>
</Ports>
<Communications>
<ConfigTag ConfigSize="32" ExternalAccess="Read/Write">
<Data Format="L5K">
<![CDATA[[36,179,[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]]]]>
</Data>
<Data Format="Decorated">
<Structure DataType="AB:5000_DO8_Diag:C:0">
<StructureMember Name="Pt00" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt01" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt02" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt03" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt04" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt05" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt06" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt07" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="OutputData" RPI="5000" Type="StandardDataDriven" OutputSize="32" InputSize="36" EventID="0" ProgrammaticallySendEventTrigger="false" Priority="Scheduled" InputConnectionType="Unicast" InputProductionTrigger="Cyclic" ConnectionPath="20 04 24 b3 2c 74 2d 00 46 03"
 InputTagSuffix="I" OutputTagSuffix="O">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:5000_DO8_Diag:I:0">
<DataValueMember Name="RunMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="0"/>
<DataValueMember Name="DiagnosticActive" DataType="BOOL" Value="0"/>
<DataValueMember Name="DiagnosticSequenceCount" DataType="SINT" Radix="Decimal" Value="0"/>
<StructureMember Name="Pt00" DataType="CHANNEL_DO_DIAG:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoad" DataType="BOOL" Value="0"/>
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt01" DataType="CHANNEL_DO_DIAG:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoad" DataType="BOOL" Value="0"/>
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt02" DataType="CHANNEL_DO_DIAG:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoad" DataType="BOOL" Value="0"/>
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt03" DataType="CHANNEL_DO_DIAG:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoad" DataType="BOOL" Value="0"/>
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt04" DataType="CHANNEL_DO_DIAG:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoad" DataType="BOOL" Value="0"/>
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt05" DataType="CHANNEL_DO_DIAG:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoad" DataType="BOOL" Value="0"/>
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt06" DataType="CHANNEL_DO_DIAG:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoad" DataType="BOOL" Value="0"/>
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt07" DataType="CHANNEL_DO_DIAG:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoad" DataType="BOOL" Value="0"/>
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0"/>
</StructureMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
<![CDATA[[[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]]]>
</Data>
<Data Format="Decorated">
<Structure DataType="AB:5000_DO8:O:0">
<StructureMember Name="Pt00" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt01" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt02" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt03" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt04" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt05" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt06" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt07" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
<ExtendedProperties>
<public><ConfigID>210</ConfigID><CatNum>5069-OB8</CatNum></public>
</ExtendedProperties>
</Module>
""",
    '5069-OF4/A': """\
<Module CatalogNumber="5069-OF4/A" Vendor="1" ProductType="115" ProductCode="320" Major="2" Minor="1" ParentModule="AENT" ParentModPortId="1" Inhibited="false" MajorFault="false" SafetyEnabled="false"
 AutoDiagsEnabled="true">
<EKey State="CompatibleModule"/>
<Ports>
<Port Id="1" Address="8" Type="5069" Upstream="true"/>
</Ports>
<Communications>
<ConfigTag ConfigSize="192" ExternalAccess="Read/Write">
<Data Format="L5K">
<![CDATA[[196,172,[4,0,3,0,0.00000000e+000,0.00000000e+000,2.00000000e+001,0.00000000e+000,1.00000000e+002
		,0.00000000e+000,1.00000000e+002,0.00000000e+000,0.00000000e+000,0.00000000e+000,0.00000000e+000
		],[4,0,3,0,0.00000000e+000,0.00000000e+000,2.00000000e+001,0.00000000e+000,1.00000000e+002,0.00000000e+000
		,1.00000000e+002,0.00000000e+000,0.00000000e+000,0.00000000e+000,0.00000000e+000],[4,0,3,0,0.00000000e+000
		,0.00000000e+000,2.00000000e+001,0.00000000e+000,1.00000000e+002,0.00000000e+000,1.00000000e+002
		,0.00000000e+000,0.00000000e+000,0.00000000e+000,0.00000000e+000],[4,0,3,0,0.00000000e+000,0.00000000e+000
		,2.00000000e+001,0.00000000e+000,1.00000000e+002,0.00000000e+000,1.00000000e+002,0.00000000e+000
		,0.00000000e+000,0.00000000e+000,0.00000000e+000]]]]>
</Data>
<Data Format="Decorated">
<Structure DataType="AB:5000_AO4:C:0">
<StructureMember Name="Ch00" DataType="AB:5000_AO_Channel:C:0">
<DataValueMember Name="Range" DataType="SINT" Radix="Decimal" Value="4"/>
<DataValueMember Name="AlarmDisable" DataType="BOOL" Value="0"/>
<DataValueMember Name="LimitAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="Disable" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultMode" DataType="BOOL" Value="1"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="1"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampInRun" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampToProg" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampToFault" DataType="BOOL" Value="0"/>
<DataValueMember Name="HoldForInit" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="MaxRampRate" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="LowSignal" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighSignal" DataType="REAL" Radix="Float" Value="20.0"/>
<DataValueMember Name="LowEngineering" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighEngineering" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="LowLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighLimit" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="Offset" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="FaultValue" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="ProgValue" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="FaultFinalState" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
<StructureMember Name="Ch01" DataType="AB:5000_AO_Channel:C:0">
<DataValueMember Name="Range" DataType="SINT" Radix="Decimal" Value="4"/>
<DataValueMember Name="AlarmDisable" DataType="BOOL" Value="0"/>
<DataValueMember Name="LimitAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="Disable" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultMode" DataType="BOOL" Value="1"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="1"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampInRun" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampToProg" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampToFault" DataType="BOOL" Value="0"/>
<DataValueMember Name="HoldForInit" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="MaxRampRate" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="LowSignal" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighSignal" DataType="REAL" Radix="Float" Value="20.0"/>
<DataValueMember Name="LowEngineering" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighEngineering" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="LowLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighLimit" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="Offset" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="FaultValue" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="ProgValue" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="FaultFinalState" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
<StructureMember Name="Ch02" DataType="AB:5000_AO_Channel:C:0">
<DataValueMember Name="Range" DataType="SINT" Radix="Decimal" Value="4"/>
<DataValueMember Name="AlarmDisable" DataType="BOOL" Value="0"/>
<DataValueMember Name="LimitAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="Disable" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultMode" DataType="BOOL" Value="1"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="1"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampInRun" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampToProg" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampToFault" DataType="BOOL" Value="0"/>
<DataValueMember Name="HoldForInit" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="MaxRampRate" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="LowSignal" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighSignal" DataType="REAL" Radix="Float" Value="20.0"/>
<DataValueMember Name="LowEngineering" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighEngineering" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="LowLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighLimit" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="Offset" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="FaultValue" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="ProgValue" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="FaultFinalState" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
<StructureMember Name="Ch03" DataType="AB:5000_AO_Channel:C:0">
<DataValueMember Name="Range" DataType="SINT" Radix="Decimal" Value="4"/>
<DataValueMember Name="AlarmDisable" DataType="BOOL" Value="0"/>
<DataValueMember Name="LimitAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="Disable" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultMode" DataType="BOOL" Value="1"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="1"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampInRun" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampToProg" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampToFault" DataType="BOOL" Value="0"/>
<DataValueMember Name="HoldForInit" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="MaxRampRate" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="LowSignal" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighSignal" DataType="REAL" Radix="Float" Value="20.0"/>
<DataValueMember Name="LowEngineering" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighEngineering" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="LowLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighLimit" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="Offset" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="FaultValue" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="ProgValue" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="FaultFinalState" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
</Structure>
</Data>
</ConfigTag>
<ConfigScript Size="324">
<Data Format="L5K">
<![CDATA[[64,1,0,0,4,0,0,0,0,0,0,0,0,0,0,0,46,1,0,0,7,1,0,0,0,3,0,0,0,-64,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,8,15,0,0,0,0,0,0,0,0,0,0,0
		,112,1,0,0,16,0,0,0,16,0,0,0,15,0,0,0,-128,1,0,0,-128,1,0,0,112,1,0,0,-112,1,0,0,-112,1,0,0,15,0,0,0,0,3,0,0,0,3,0,0,112,1,0,0,16,3,0,0,16
		,3,0,0,15,0,0,0,-128,4,0,0,-128,4,0,0,112,1,0,0,-112,4,0,0,-112,4,0,0,0,0]]]>
</Data>
</ConfigScript>
<Connections>
<Connection Name="OutputData" RPI="80000" Type="StandardDataDriven" OutputSize="32" InputSize="52" EventID="0" ProgrammaticallySendEventTrigger="false" Priority="Scheduled" InputConnectionType="Unicast" InputProductionTrigger="Cyclic" ConnectionPath="20 04 24 ac 2c 72 2c 94"
 InputTagSuffix="I" OutputTagSuffix="O">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:5000_AO4:I:0">
<DataValueMember Name="RunMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="0"/>
<DataValueMember Name="DiagnosticActive" DataType="BOOL" Value="0"/>
<DataValueMember Name="DiagnosticSequenceCount" DataType="SINT" Radix="Decimal" Value="0"/>
<StructureMember Name="Ch00" DataType="CHANNEL_AO_DIAG:I:0">
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoad" DataType="BOOL" Value="0"/>
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0"/>
<DataValueMember Name="OverTemperature" DataType="BOOL" Value="0"/>
<DataValueMember Name="FieldPowerOff" DataType="BOOL" Value="0"/>
<DataValueMember Name="InHold" DataType="BOOL" Value="0"/>
<DataValueMember Name="NotANumber" DataType="BOOL" Value="0"/>
<DataValueMember Name="Underrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="Overrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="LLimitAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="HLimitAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="CalFault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Calibrating" DataType="BOOL" Value="0"/>
<DataValueMember Name="Data" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="RollingTimestamp" DataType="INT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Ch01" DataType="CHANNEL_AO_DIAG:I:0">
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoad" DataType="BOOL" Value="0"/>
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0"/>
<DataValueMember Name="OverTemperature" DataType="BOOL" Value="0"/>
<DataValueMember Name="FieldPowerOff" DataType="BOOL" Value="0"/>
<DataValueMember Name="InHold" DataType="BOOL" Value="0"/>
<DataValueMember Name="NotANumber" DataType="BOOL" Value="0"/>
<DataValueMember Name="Underrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="Overrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="LLimitAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="HLimitAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="CalFault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Calibrating" DataType="BOOL" Value="0"/>
<DataValueMember Name="Data" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="RollingTimestamp" DataType="INT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Ch02" DataType="CHANNEL_AO_DIAG:I:0">
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoad" DataType="BOOL" Value="0"/>
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0"/>
<DataValueMember Name="OverTemperature" DataType="BOOL" Value="0"/>
<DataValueMember Name="FieldPowerOff" DataType="BOOL" Value="0"/>
<DataValueMember Name="InHold" DataType="BOOL" Value="0"/>
<DataValueMember Name="NotANumber" DataType="BOOL" Value="0"/>
<DataValueMember Name="Underrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="Overrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="LLimitAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="HLimitAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="CalFault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Calibrating" DataType="BOOL" Value="0"/>
<DataValueMember Name="Data" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="RollingTimestamp" DataType="INT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Ch03" DataType="CHANNEL_AO_DIAG:I:0">
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoad" DataType="BOOL" Value="0"/>
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0"/>
<DataValueMember Name="OverTemperature" DataType="BOOL" Value="0"/>
<DataValueMember Name="FieldPowerOff" DataType="BOOL" Value="0"/>
<DataValueMember Name="InHold" DataType="BOOL" Value="0"/>
<DataValueMember Name="NotANumber" DataType="BOOL" Value="0"/>
<DataValueMember Name="Underrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="Overrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="LLimitAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="HLimitAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="CalFault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Calibrating" DataType="BOOL" Value="0"/>
<DataValueMember Name="Data" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="RollingTimestamp" DataType="INT" Radix="Decimal" Value="0"/>
</StructureMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<EngineeringUnits>
<EngineeringUnit Operand=".CH00.DATA">
<![CDATA[%]]>
</EngineeringUnit>
<EngineeringUnit Operand=".CH01.DATA">
<![CDATA[%]]>
</EngineeringUnit>
<EngineeringUnit Operand=".CH02.DATA">
<![CDATA[%]]>
</EngineeringUnit>
<EngineeringUnit Operand=".CH03.DATA">
<![CDATA[%]]>
</EngineeringUnit>
</EngineeringUnits>
<Data Format="L5K">
<![CDATA[[[0,0,0,0.00000000e+000],[0,0,0,0.00000000e+000],[0,0,0,0.00000000e+000],[0,0,0,0.00000000e+000]]]]>
</Data>
<Data Format="Decorated">
<Structure DataType="AB:5000_AO4:O:0">
<StructureMember Name="Ch00" DataType="CHANNEL_AO:O:0">
<DataValueMember Name="LLimitAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="HLimitAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="Data" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
<StructureMember Name="Ch01" DataType="CHANNEL_AO:O:0">
<DataValueMember Name="LLimitAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="HLimitAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="Data" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
<StructureMember Name="Ch02" DataType="CHANNEL_AO:O:0">
<DataValueMember Name="LLimitAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="HLimitAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="Data" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
<StructureMember Name="Ch03" DataType="CHANNEL_AO:O:0">
<DataValueMember Name="LLimitAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="HLimitAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="Data" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
<ExtendedProperties>
<public><Vendor>Rockwell Automation/Allen-Bradley</Vendor><CatNum>5069-OF4</CatNum><ConfigID>401</ConfigID><ADDAVersion>1</ADDAVersion></public>
</ExtendedProperties>
</Module>
""",
    '5069-OF8/A': """\
<Module CatalogNumber="5069-OF8/A" Vendor="1" ProductType="115" ProductCode="313" Major="2" Minor="1" ParentModule="AENT" ParentModPortId="1" Inhibited="false" MajorFault="false" SafetyEnabled="false"
 AutoDiagsEnabled="true">
<EKey State="CompatibleModule"/>
<Ports>
<Port Id="1" Address="9" Type="5069" Upstream="true"/>
</Ports>
<Communications>
<ConfigTag ConfigSize="384" ExternalAccess="Read/Write">
<Data Format="L5K">
<![CDATA[[388,166,[4,0,3,0,0.00000000e+000,0.00000000e+000,2.00000000e+001,0.00000000e+000,1.00000000e+002
		,0.00000000e+000,1.00000000e+002,0.00000000e+000,0.00000000e+000,0.00000000e+000,0.00000000e+000
		],[4,0,3,0,0.00000000e+000,0.00000000e+000,2.00000000e+001,0.00000000e+000,1.00000000e+002,0.00000000e+000
		,1.00000000e+002,0.00000000e+000,0.00000000e+000,0.00000000e+000,0.00000000e+000],[4,0,3,0,0.00000000e+000
		,0.00000000e+000,2.00000000e+001,0.00000000e+000,1.00000000e+002,0.00000000e+000,1.00000000e+002
		,0.00000000e+000,0.00000000e+000,0.00000000e+000,0.00000000e+000],[4,0,3,0,0.00000000e+000,0.00000000e+000
		,2.00000000e+001,0.00000000e+000,1.00000000e+002,0.00000000e+000,1.00000000e+002,0.00000000e+000
		,0.00000000e+000,0.00000000e+000,0.00000000e+000],[4,0,3,0,0.00000000e+000,0.00000000e+000,2.00000000e+001
		,0.00000000e+000,1.00000000e+002,0.00000000e+000,1.00000000e+002,0.00000000e+000,0.00000000e+000
		,0.00000000e+000,0.00000000e+000],[4,0,3,0,0.00000000e+000,0.00000000e+000,2.00000000e+001,0.00000000e+000
		,1.00000000e+002,0.00000000e+000,1.00000000e+002,0.00000000e+000,0.00000000e+000,0.00000000e+000
		,0.00000000e+000],[4,0,3,0,0.00000000e+000,0.00000000e+000,2.00000000e+001,0.00000000e+000,1.00000000e+002
		,0.00000000e+000,1.00000000e+002,0.00000000e+000,0.00000000e+000,0.00000000e+000,0.00000000e+000
		],[4,0,3,0,0.00000000e+000,0.00000000e+000,2.00000000e+001,0.00000000e+000,1.00000000e+002,0.00000000e+000
		,1.00000000e+002,0.00000000e+000,0.00000000e+000,0.00000000e+000,0.00000000e+000]]]]>
</Data>
<Data Format="Decorated">
<Structure DataType="AB:5000_AO8:C:0">
<StructureMember Name="Ch00" DataType="AB:5000_AO_Channel:C:0">
<DataValueMember Name="Range" DataType="SINT" Radix="Decimal" Value="4"/>
<DataValueMember Name="AlarmDisable" DataType="BOOL" Value="0"/>
<DataValueMember Name="LimitAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="Disable" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultMode" DataType="BOOL" Value="1"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="1"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampInRun" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampToProg" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampToFault" DataType="BOOL" Value="0"/>
<DataValueMember Name="HoldForInit" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="MaxRampRate" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="LowSignal" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighSignal" DataType="REAL" Radix="Float" Value="20.0"/>
<DataValueMember Name="LowEngineering" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighEngineering" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="LowLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighLimit" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="Offset" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="FaultValue" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="ProgValue" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="FaultFinalState" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
<StructureMember Name="Ch01" DataType="AB:5000_AO_Channel:C:0">
<DataValueMember Name="Range" DataType="SINT" Radix="Decimal" Value="4"/>
<DataValueMember Name="AlarmDisable" DataType="BOOL" Value="0"/>
<DataValueMember Name="LimitAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="Disable" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultMode" DataType="BOOL" Value="1"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="1"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampInRun" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampToProg" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampToFault" DataType="BOOL" Value="0"/>
<DataValueMember Name="HoldForInit" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="MaxRampRate" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="LowSignal" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighSignal" DataType="REAL" Radix="Float" Value="20.0"/>
<DataValueMember Name="LowEngineering" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighEngineering" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="LowLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighLimit" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="Offset" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="FaultValue" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="ProgValue" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="FaultFinalState" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
<StructureMember Name="Ch02" DataType="AB:5000_AO_Channel:C:0">
<DataValueMember Name="Range" DataType="SINT" Radix="Decimal" Value="4"/>
<DataValueMember Name="AlarmDisable" DataType="BOOL" Value="0"/>
<DataValueMember Name="LimitAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="Disable" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultMode" DataType="BOOL" Value="1"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="1"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampInRun" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampToProg" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampToFault" DataType="BOOL" Value="0"/>
<DataValueMember Name="HoldForInit" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="MaxRampRate" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="LowSignal" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighSignal" DataType="REAL" Radix="Float" Value="20.0"/>
<DataValueMember Name="LowEngineering" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighEngineering" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="LowLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighLimit" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="Offset" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="FaultValue" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="ProgValue" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="FaultFinalState" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
<StructureMember Name="Ch03" DataType="AB:5000_AO_Channel:C:0">
<DataValueMember Name="Range" DataType="SINT" Radix="Decimal" Value="4"/>
<DataValueMember Name="AlarmDisable" DataType="BOOL" Value="0"/>
<DataValueMember Name="LimitAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="Disable" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultMode" DataType="BOOL" Value="1"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="1"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampInRun" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampToProg" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampToFault" DataType="BOOL" Value="0"/>
<DataValueMember Name="HoldForInit" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="MaxRampRate" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="LowSignal" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighSignal" DataType="REAL" Radix="Float" Value="20.0"/>
<DataValueMember Name="LowEngineering" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighEngineering" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="LowLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighLimit" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="Offset" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="FaultValue" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="ProgValue" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="FaultFinalState" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
<StructureMember Name="Ch04" DataType="AB:5000_AO_Channel:C:0">
<DataValueMember Name="Range" DataType="SINT" Radix="Decimal" Value="4"/>
<DataValueMember Name="AlarmDisable" DataType="BOOL" Value="0"/>
<DataValueMember Name="LimitAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="Disable" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultMode" DataType="BOOL" Value="1"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="1"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampInRun" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampToProg" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampToFault" DataType="BOOL" Value="0"/>
<DataValueMember Name="HoldForInit" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="MaxRampRate" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="LowSignal" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighSignal" DataType="REAL" Radix="Float" Value="20.0"/>
<DataValueMember Name="LowEngineering" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighEngineering" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="LowLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighLimit" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="Offset" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="FaultValue" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="ProgValue" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="FaultFinalState" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
<StructureMember Name="Ch05" DataType="AB:5000_AO_Channel:C:0">
<DataValueMember Name="Range" DataType="SINT" Radix="Decimal" Value="4"/>
<DataValueMember Name="AlarmDisable" DataType="BOOL" Value="0"/>
<DataValueMember Name="LimitAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="Disable" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultMode" DataType="BOOL" Value="1"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="1"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampInRun" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampToProg" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampToFault" DataType="BOOL" Value="0"/>
<DataValueMember Name="HoldForInit" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="MaxRampRate" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="LowSignal" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighSignal" DataType="REAL" Radix="Float" Value="20.0"/>
<DataValueMember Name="LowEngineering" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighEngineering" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="LowLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighLimit" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="Offset" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="FaultValue" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="ProgValue" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="FaultFinalState" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
<StructureMember Name="Ch06" DataType="AB:5000_AO_Channel:C:0">
<DataValueMember Name="Range" DataType="SINT" Radix="Decimal" Value="4"/>
<DataValueMember Name="AlarmDisable" DataType="BOOL" Value="0"/>
<DataValueMember Name="LimitAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="Disable" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultMode" DataType="BOOL" Value="1"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="1"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampInRun" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampToProg" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampToFault" DataType="BOOL" Value="0"/>
<DataValueMember Name="HoldForInit" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="MaxRampRate" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="LowSignal" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighSignal" DataType="REAL" Radix="Float" Value="20.0"/>
<DataValueMember Name="LowEngineering" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighEngineering" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="LowLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighLimit" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="Offset" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="FaultValue" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="ProgValue" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="FaultFinalState" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
<StructureMember Name="Ch07" DataType="AB:5000_AO_Channel:C:0">
<DataValueMember Name="Range" DataType="SINT" Radix="Decimal" Value="4"/>
<DataValueMember Name="AlarmDisable" DataType="BOOL" Value="0"/>
<DataValueMember Name="LimitAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="Disable" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultMode" DataType="BOOL" Value="1"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="1"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampInRun" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampToProg" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampToFault" DataType="BOOL" Value="0"/>
<DataValueMember Name="HoldForInit" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="MaxRampRate" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="LowSignal" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighSignal" DataType="REAL" Radix="Float" Value="20.0"/>
<DataValueMember Name="LowEngineering" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighEngineering" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="LowLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="HighLimit" DataType="REAL" Radix="Float" Value="100.0"/>
<DataValueMember Name="Offset" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="FaultValue" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="ProgValue" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="FaultFinalState" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
</Structure>
</Data>
</ConfigTag>
<ConfigScript Size="612">
<Data Format="L5K">
<![CDATA[[96,2,0,0,4,0,0,0,0,0,0,0,0,0,0,0,78,2,0,0,7,1,0,0,0,3,0,0,0,-128,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,16,15,0,0,0,0,0,0,0,0,0,0,0,112,1,0,0,16,0,0,0,16,0,0,0,15,0,0,0,-128,1,0,0,-128,1,0,0,112,1,0,0,-112,1,0,0,-112
		,1,0,0,15,0,0,0,0,3,0,0,0,3,0,0,112,1,0,0,16,3,0,0,16,3,0,0,15,0,0,0,-128,4,0,0,-128,4,0,0,112,1,0,0,-112,4,0,0,-112,4,0,0,15,0,0,0,0,6,0,0,0
		,6,0,0,112,1,0,0,16,6,0,0,16,6,0,0,15,0,0,0,-128,7,0,0,-128,7,0,0,112,1,0,0,-112,7,0,0,-112,7,0,0,15,0,0,0,0,9,0,0,0,9,0,0,112,1,0,0,16,9,0
		,0,16,9,0,0,15,0,0,0,-128,10,0,0,-128,10,0,0,112,1,0,0,-112,10,0,0,-112,10,0,0,0,0]]]>
</Data>
</ConfigScript>
<Connections>
<Connection Name="OutputData" RPI="80000" Type="StandardDataDriven" OutputSize="64" InputSize="100" EventID="0" ProgrammaticallySendEventTrigger="false" Priority="Scheduled" InputConnectionType="Unicast" InputProductionTrigger="Cyclic" ConnectionPath="20 04 24 a6 2c 6b 2c 8c"
 InputTagSuffix="I" OutputTagSuffix="O">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:5000_AO8:I:0">
<DataValueMember Name="RunMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="0"/>
<DataValueMember Name="DiagnosticActive" DataType="BOOL" Value="0"/>
<DataValueMember Name="DiagnosticSequenceCount" DataType="SINT" Radix="Decimal" Value="0"/>
<StructureMember Name="Ch00" DataType="CHANNEL_AO_DIAG:I:0">
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoad" DataType="BOOL" Value="0"/>
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0"/>
<DataValueMember Name="OverTemperature" DataType="BOOL" Value="0"/>
<DataValueMember Name="FieldPowerOff" DataType="BOOL" Value="0"/>
<DataValueMember Name="InHold" DataType="BOOL" Value="0"/>
<DataValueMember Name="NotANumber" DataType="BOOL" Value="0"/>
<DataValueMember Name="Underrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="Overrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="LLimitAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="HLimitAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="CalFault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Calibrating" DataType="BOOL" Value="0"/>
<DataValueMember Name="Data" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="RollingTimestamp" DataType="INT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Ch01" DataType="CHANNEL_AO_DIAG:I:0">
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoad" DataType="BOOL" Value="0"/>
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0"/>
<DataValueMember Name="OverTemperature" DataType="BOOL" Value="0"/>
<DataValueMember Name="FieldPowerOff" DataType="BOOL" Value="0"/>
<DataValueMember Name="InHold" DataType="BOOL" Value="0"/>
<DataValueMember Name="NotANumber" DataType="BOOL" Value="0"/>
<DataValueMember Name="Underrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="Overrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="LLimitAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="HLimitAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="CalFault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Calibrating" DataType="BOOL" Value="0"/>
<DataValueMember Name="Data" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="RollingTimestamp" DataType="INT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Ch02" DataType="CHANNEL_AO_DIAG:I:0">
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoad" DataType="BOOL" Value="0"/>
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0"/>
<DataValueMember Name="OverTemperature" DataType="BOOL" Value="0"/>
<DataValueMember Name="FieldPowerOff" DataType="BOOL" Value="0"/>
<DataValueMember Name="InHold" DataType="BOOL" Value="0"/>
<DataValueMember Name="NotANumber" DataType="BOOL" Value="0"/>
<DataValueMember Name="Underrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="Overrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="LLimitAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="HLimitAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="CalFault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Calibrating" DataType="BOOL" Value="0"/>
<DataValueMember Name="Data" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="RollingTimestamp" DataType="INT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Ch03" DataType="CHANNEL_AO_DIAG:I:0">
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoad" DataType="BOOL" Value="0"/>
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0"/>
<DataValueMember Name="OverTemperature" DataType="BOOL" Value="0"/>
<DataValueMember Name="FieldPowerOff" DataType="BOOL" Value="0"/>
<DataValueMember Name="InHold" DataType="BOOL" Value="0"/>
<DataValueMember Name="NotANumber" DataType="BOOL" Value="0"/>
<DataValueMember Name="Underrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="Overrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="LLimitAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="HLimitAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="CalFault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Calibrating" DataType="BOOL" Value="0"/>
<DataValueMember Name="Data" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="RollingTimestamp" DataType="INT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Ch04" DataType="CHANNEL_AO_DIAG:I:0">
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoad" DataType="BOOL" Value="0"/>
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0"/>
<DataValueMember Name="OverTemperature" DataType="BOOL" Value="0"/>
<DataValueMember Name="FieldPowerOff" DataType="BOOL" Value="0"/>
<DataValueMember Name="InHold" DataType="BOOL" Value="0"/>
<DataValueMember Name="NotANumber" DataType="BOOL" Value="0"/>
<DataValueMember Name="Underrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="Overrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="LLimitAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="HLimitAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="CalFault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Calibrating" DataType="BOOL" Value="0"/>
<DataValueMember Name="Data" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="RollingTimestamp" DataType="INT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Ch05" DataType="CHANNEL_AO_DIAG:I:0">
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoad" DataType="BOOL" Value="0"/>
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0"/>
<DataValueMember Name="OverTemperature" DataType="BOOL" Value="0"/>
<DataValueMember Name="FieldPowerOff" DataType="BOOL" Value="0"/>
<DataValueMember Name="InHold" DataType="BOOL" Value="0"/>
<DataValueMember Name="NotANumber" DataType="BOOL" Value="0"/>
<DataValueMember Name="Underrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="Overrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="LLimitAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="HLimitAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="CalFault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Calibrating" DataType="BOOL" Value="0"/>
<DataValueMember Name="Data" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="RollingTimestamp" DataType="INT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Ch06" DataType="CHANNEL_AO_DIAG:I:0">
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoad" DataType="BOOL" Value="0"/>
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0"/>
<DataValueMember Name="OverTemperature" DataType="BOOL" Value="0"/>
<DataValueMember Name="FieldPowerOff" DataType="BOOL" Value="0"/>
<DataValueMember Name="InHold" DataType="BOOL" Value="0"/>
<DataValueMember Name="NotANumber" DataType="BOOL" Value="0"/>
<DataValueMember Name="Underrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="Overrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="LLimitAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="HLimitAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="CalFault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Calibrating" DataType="BOOL" Value="0"/>
<DataValueMember Name="Data" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="RollingTimestamp" DataType="INT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Ch07" DataType="CHANNEL_AO_DIAG:I:0">
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoad" DataType="BOOL" Value="0"/>
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0"/>
<DataValueMember Name="OverTemperature" DataType="BOOL" Value="0"/>
<DataValueMember Name="FieldPowerOff" DataType="BOOL" Value="0"/>
<DataValueMember Name="InHold" DataType="BOOL" Value="0"/>
<DataValueMember Name="NotANumber" DataType="BOOL" Value="0"/>
<DataValueMember Name="Underrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="Overrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="LLimitAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="HLimitAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="CalFault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Calibrating" DataType="BOOL" Value="0"/>
<DataValueMember Name="Data" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="RollingTimestamp" DataType="INT" Radix="Decimal" Value="0"/>
</StructureMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<EngineeringUnits>
<EngineeringUnit Operand=".CH00.DATA">
<![CDATA[%]]>
</EngineeringUnit>
<EngineeringUnit Operand=".CH01.DATA">
<![CDATA[%]]>
</EngineeringUnit>
<EngineeringUnit Operand=".CH02.DATA">
<![CDATA[%]]>
</EngineeringUnit>
<EngineeringUnit Operand=".CH03.DATA">
<![CDATA[%]]>
</EngineeringUnit>
<EngineeringUnit Operand=".CH04.DATA">
<![CDATA[%]]>
</EngineeringUnit>
<EngineeringUnit Operand=".CH05.DATA">
<![CDATA[%]]>
</EngineeringUnit>
<EngineeringUnit Operand=".CH06.DATA">
<![CDATA[%]]>
</EngineeringUnit>
<EngineeringUnit Operand=".CH07.DATA">
<![CDATA[%]]>
</EngineeringUnit>
</EngineeringUnits>
<Data Format="L5K">
<![CDATA[[[0,0,0,0.00000000e+000],[0,0,0,0.00000000e+000],[0,0,0,0.00000000e+000],[0,0,0,0.00000000e+000],[0,0,0,0.00000000e+000
		],[0,0,0,0.00000000e+000],[0,0,0,0.00000000e+000],[0,0,0,0.00000000e+000]]]]>
</Data>
<Data Format="Decorated">
<Structure DataType="AB:5000_AO8:O:0">
<StructureMember Name="Ch00" DataType="CHANNEL_AO:O:0">
<DataValueMember Name="LLimitAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="HLimitAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="Data" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
<StructureMember Name="Ch01" DataType="CHANNEL_AO:O:0">
<DataValueMember Name="LLimitAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="HLimitAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="Data" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
<StructureMember Name="Ch02" DataType="CHANNEL_AO:O:0">
<DataValueMember Name="LLimitAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="HLimitAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="Data" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
<StructureMember Name="Ch03" DataType="CHANNEL_AO:O:0">
<DataValueMember Name="LLimitAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="HLimitAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="Data" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
<StructureMember Name="Ch04" DataType="CHANNEL_AO:O:0">
<DataValueMember Name="LLimitAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="HLimitAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="Data" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
<StructureMember Name="Ch05" DataType="CHANNEL_AO:O:0">
<DataValueMember Name="LLimitAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="HLimitAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="Data" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
<StructureMember Name="Ch06" DataType="CHANNEL_AO:O:0">
<DataValueMember Name="LLimitAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="HLimitAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="Data" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
<StructureMember Name="Ch07" DataType="CHANNEL_AO:O:0">
<DataValueMember Name="LLimitAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="HLimitAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="RampAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="Data" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
<ExtendedProperties>
<public><Vendor>Rockwell Automation/Allen-Bradley</Vendor><CatNum>5069-OF8</CatNum><ConfigID>301</ConfigID><ADDAVersion>1</ADDAVersion></public>
</ExtendedProperties>
</Module>
""",
    '5069-OW16/C': """\
<Module CatalogNumber="5069-OW16/C" Vendor="1" ProductType="7" ProductCode="1214" Major="5" Minor="1" ParentModule="AENT" ParentModPortId="1" Inhibited="false" MajorFault="false" SafetyEnabled="false"
>
<EKey State="CompatibleModule"/>
<Ports>
<Port Id="1" Address="10" Type="5069" Upstream="true"/>
</Ports>
<Communications>
<ConfigTag ConfigSize="64" ExternalAccess="Read/Write">
<Data Format="L5K">
<![CDATA[[68,171,[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]]]]>
</Data>
<Data Format="Decorated">
<Structure DataType="AB:5000_DO16:C:0">
<StructureMember Name="Pt00" DataType="AB:5000_DO_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt01" DataType="AB:5000_DO_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt02" DataType="AB:5000_DO_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt03" DataType="AB:5000_DO_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt04" DataType="AB:5000_DO_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt05" DataType="AB:5000_DO_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt06" DataType="AB:5000_DO_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt07" DataType="AB:5000_DO_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt08" DataType="AB:5000_DO_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt09" DataType="AB:5000_DO_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt10" DataType="AB:5000_DO_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt11" DataType="AB:5000_DO_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt12" DataType="AB:5000_DO_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt13" DataType="AB:5000_DO_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt14" DataType="AB:5000_DO_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Pt15" DataType="AB:5000_DO_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="OutputData" RPI="5000" Type="StandardDataDriven" OutputSize="64" InputSize="68" EventID="0" ProgrammaticallySendEventTrigger="false" Priority="Scheduled" InputConnectionType="Unicast" InputProductionTrigger="Cyclic" ConnectionPath="20 04 24 ab 2c 64 2d 00 45 03"
 InputTagSuffix="I" OutputTagSuffix="O">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:5000_DO16:I:0">
<DataValueMember Name="RunMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="0"/>
<DataValueMember Name="DiagnosticActive" DataType="BOOL" Value="0"/>
<DataValueMember Name="DiagnosticSequenceCount" DataType="SINT" Radix="Decimal" Value="0"/>
<StructureMember Name="Pt00" DataType="CHANNEL_DO:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt01" DataType="CHANNEL_DO:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt02" DataType="CHANNEL_DO:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt03" DataType="CHANNEL_DO:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt04" DataType="CHANNEL_DO:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt05" DataType="CHANNEL_DO:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt06" DataType="CHANNEL_DO:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt07" DataType="CHANNEL_DO:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt08" DataType="CHANNEL_DO:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt09" DataType="CHANNEL_DO:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt10" DataType="CHANNEL_DO:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt11" DataType="CHANNEL_DO:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt12" DataType="CHANNEL_DO:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt13" DataType="CHANNEL_DO:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt14" DataType="CHANNEL_DO:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt15" DataType="CHANNEL_DO:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
</StructureMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
<![CDATA[[[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]]]>
</Data>
<Data Format="Decorated">
<Structure DataType="AB:5000_DO16:O:0">
<StructureMember Name="Pt00" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt01" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt02" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt03" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt04" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt05" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt06" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt07" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt08" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt09" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt10" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt11" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt12" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt13" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt14" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Pt15" DataType="CHANNEL_DO:O:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
</StructureMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
<ExtendedProperties>
<public><ConfigID>111</ConfigID><CatNum>5069-OW16</CatNum></public>
</ExtendedProperties>
</Module>
""",
    '5069-SERIAL/A': """\
<Module CatalogNumber="5069-SERIAL/A" Vendor="1" ProductType="12" ProductCode="320" Major="2" Minor="1" ParentModule="AENT" ParentModPortId="1" Inhibited="false" MajorFault="false" SafetyEnabled="false"
>
<EKey State="CompatibleModule"/>
<Ports>
<Port Id="1" Address="11" Type="5069" Upstream="true"/>
</Ports>
<ExtendedProperties>
<public><Vendor>Rockwell Automation/Allen-Bradley</Vendor><CatNum>5069-SERIAL</CatNum><ConfigID>4325481</ConfigID></public>
</ExtendedProperties>
</Module>
""",
    '5069-HSC2XOB4/A': """\
<Module CatalogNumber="5069-HSC2XOB4/A" Vendor="1" ProductType="109" ProductCode="90" Major="3" Minor="1" ParentModule="AENT" ParentModPortId="1" Inhibited="false" MajorFault="false" SafetyEnabled="false"
 AutoDiagsEnabled="true">
<EKey State="CompatibleModule"/>
<Ports>
<Port Id="1" Address="12" Type="5069" Upstream="true"/>
</Ports>
<Communications>
<ConfigTag ConfigSize="112" ExternalAccess="Read/Write">
<Data Format="L5K">
<![CDATA[[116,164,[1,1,1,1,13,13,1,0,1.00000000e+000,1.00000000e+006,1.00000000e+007,0.00000000e+000,0.00000000e+000
		],[1,1,1,1,13,13,1,0,1.00000000e+000,1.00000000e+006,1.00000000e+007,0.00000000e+000,0.00000000e+000
		],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]]]]>
</Data>
<Data Format="Decorated">
<Structure DataType="AB:5000_HSC2_CC:C:0">
<StructureMember Name="Counter00" DataType="AB:5000_HSC_Channel:C:0">
<DataValueMember Name="InputOffOnFilterA" DataType="SINT" Radix="Decimal" Value="1"/>
<DataValueMember Name="InputOnOffFilterA" DataType="SINT" Radix="Decimal" Value="1"/>
<DataValueMember Name="InputOffOnFilterB" DataType="SINT" Radix="Decimal" Value="1"/>
<DataValueMember Name="InputOnOffFilterB" DataType="SINT" Radix="Decimal" Value="1"/>
<DataValueMember Name="InputOffOnFilterZ" DataType="SINT" Radix="Decimal" Value="13"/>
<DataValueMember Name="InputOnOffFilterZ" DataType="SINT" Radix="Decimal" Value="13"/>
<DataValueMember Name="AvgOverPulses" DataType="INT" Radix="Decimal" Value="1"/>
<DataValueMember Name="InvertInputA" DataType="BOOL" Value="0"/>
<DataValueMember Name="InvertInputB" DataType="BOOL" Value="0"/>
<DataValueMember Name="InvertInputZ" DataType="BOOL" Value="0"/>
<DataValueMember Name="InvertDirectionInput" DataType="BOOL" Value="0"/>
<DataValueMember Name="LocalControlEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="ZeroFrequencyAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="ResetTimeDerivedValues" DataType="BOOL" Value="0"/>
<DataValueMember Name="MissingPulseAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="Scaling" DataType="REAL" Radix="Float" Value="1.0"/>
<DataValueMember Name="FrequencyAlarmLimit" DataType="REAL" Radix="Float" Value="1000000.0"/>
<DataValueMember Name="PulseWidthAlarmLimit" DataType="REAL" Radix="Float" Value="10000000.0"/>
<DataValueMember Name="AccelAlarmLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="DecelAlarmLimit" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
<StructureMember Name="Counter01" DataType="AB:5000_HSC_Channel:C:0">
<DataValueMember Name="InputOffOnFilterA" DataType="SINT" Radix="Decimal" Value="1"/>
<DataValueMember Name="InputOnOffFilterA" DataType="SINT" Radix="Decimal" Value="1"/>
<DataValueMember Name="InputOffOnFilterB" DataType="SINT" Radix="Decimal" Value="1"/>
<DataValueMember Name="InputOnOffFilterB" DataType="SINT" Radix="Decimal" Value="1"/>
<DataValueMember Name="InputOffOnFilterZ" DataType="SINT" Radix="Decimal" Value="13"/>
<DataValueMember Name="InputOnOffFilterZ" DataType="SINT" Radix="Decimal" Value="13"/>
<DataValueMember Name="AvgOverPulses" DataType="INT" Radix="Decimal" Value="1"/>
<DataValueMember Name="InvertInputA" DataType="BOOL" Value="0"/>
<DataValueMember Name="InvertInputB" DataType="BOOL" Value="0"/>
<DataValueMember Name="InvertInputZ" DataType="BOOL" Value="0"/>
<DataValueMember Name="InvertDirectionInput" DataType="BOOL" Value="0"/>
<DataValueMember Name="LocalControlEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="ZeroFrequencyAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="ResetTimeDerivedValues" DataType="BOOL" Value="0"/>
<DataValueMember Name="MissingPulseAlarmLatchEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="Scaling" DataType="REAL" Radix="Float" Value="1.0"/>
<DataValueMember Name="FrequencyAlarmLimit" DataType="REAL" Radix="Float" Value="1000000.0"/>
<DataValueMember Name="PulseWidthAlarmLimit" DataType="REAL" Radix="Float" Value="10000000.0"/>
<DataValueMember Name="AccelAlarmLimit" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="DecelAlarmLimit" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
<StructureMember Name="Window00" DataType="AB:5000_Window_Struct:C:0">
<DataValueMember Name="CounterSelect" DataType="SINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="Output00Select" DataType="BOOL" Value="0"/>
<DataValueMember Name="Output01Select" DataType="BOOL" Value="0"/>
<DataValueMember Name="Output02Select" DataType="BOOL" Value="0"/>
<DataValueMember Name="Output03Select" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Window01" DataType="AB:5000_Window_Struct:C:0">
<DataValueMember Name="CounterSelect" DataType="SINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="Output00Select" DataType="BOOL" Value="0"/>
<DataValueMember Name="Output01Select" DataType="BOOL" Value="0"/>
<DataValueMember Name="Output02Select" DataType="BOOL" Value="0"/>
<DataValueMember Name="Output03Select" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Window02" DataType="AB:5000_Window_Struct:C:0">
<DataValueMember Name="CounterSelect" DataType="SINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="Output00Select" DataType="BOOL" Value="0"/>
<DataValueMember Name="Output01Select" DataType="BOOL" Value="0"/>
<DataValueMember Name="Output02Select" DataType="BOOL" Value="0"/>
<DataValueMember Name="Output03Select" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Window03" DataType="AB:5000_Window_Struct:C:0">
<DataValueMember Name="CounterSelect" DataType="SINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="Output00Select" DataType="BOOL" Value="0"/>
<DataValueMember Name="Output01Select" DataType="BOOL" Value="0"/>
<DataValueMember Name="Output02Select" DataType="BOOL" Value="0"/>
<DataValueMember Name="Output03Select" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Window04" DataType="AB:5000_Window_Struct:C:0">
<DataValueMember Name="CounterSelect" DataType="SINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="Output00Select" DataType="BOOL" Value="0"/>
<DataValueMember Name="Output01Select" DataType="BOOL" Value="0"/>
<DataValueMember Name="Output02Select" DataType="BOOL" Value="0"/>
<DataValueMember Name="Output03Select" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Window05" DataType="AB:5000_Window_Struct:C:0">
<DataValueMember Name="CounterSelect" DataType="SINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="Output00Select" DataType="BOOL" Value="0"/>
<DataValueMember Name="Output01Select" DataType="BOOL" Value="0"/>
<DataValueMember Name="Output02Select" DataType="BOOL" Value="0"/>
<DataValueMember Name="Output03Select" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Window06" DataType="AB:5000_Window_Struct:C:0">
<DataValueMember Name="CounterSelect" DataType="SINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="Output00Select" DataType="BOOL" Value="0"/>
<DataValueMember Name="Output01Select" DataType="BOOL" Value="0"/>
<DataValueMember Name="Output02Select" DataType="BOOL" Value="0"/>
<DataValueMember Name="Output03Select" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Window07" DataType="AB:5000_Window_Struct:C:0">
<DataValueMember Name="CounterSelect" DataType="SINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="Output00Select" DataType="BOOL" Value="0"/>
<DataValueMember Name="Output01Select" DataType="BOOL" Value="0"/>
<DataValueMember Name="Output02Select" DataType="BOOL" Value="0"/>
<DataValueMember Name="Output03Select" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Output00" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Output01" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Output02" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Output03" DataType="AB:5000_DO_Diag_Channel:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultFinalState" DataType="BOOL" Value="0"/>
<DataValueMember Name="ProgramToFaultEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoadEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="FaultValueStateDuration" DataType="SINT" Radix="Decimal" Value="0"/>
</StructureMember>
</Structure>
</Data>
</ConfigTag>
<ConfigScript Size="368">
<Data Format="L5K">
<![CDATA[[108,1,0,0,4,0,0,0,0,0,0,0,0,0,0,0,90,1,0,0,7,1,0,0,0,3,0,0,0,-116,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-1,0,-1,-1,-1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-1,0,-1,-1,-1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,16,96,0,0,0,0,0,0,0,0,0,0,0,-96,0,0,0,96,0,0,0,-96,0,0,0,96,0,0,0,0,1,0,0,64,1,0,0,-96,0,0,0,96,1,0
		,0,-32,1,0,0,24,0,0,0,8,2,0,0,-120,2,0,0,24,0,0,0,40,2,0,0,-88,2,0,0,24,0,0,0,72,2,0,0,-56,2,0,0,24,0,0,0,104,2,0,0,-24,2,0,0,24,0,0,0,-120
		,2,0,0,8,3,0,0,24,0,0,0,-88,2,0,0,40,3,0,0,24,0,0,0,-56,2,0,0,72,3,0,0,24,0,0,0,-24,2,0,0,104,3,0,0,16,0,0,0,0,3,0,0,-128,3,0,0,16,0,0,0,32,3,0
		,0,-96,3,0,0,16,0,0,0,64,3,0,0,-64,3,0,0,16,0,0,0,96,3,0,0,-32,3,0,0,0,0]]]>
</Data>
</ConfigScript>
<Connections>
<Connection Name="Data" RPI="80000" Type="StandardDataDriven" OutputSize="200" InputSize="236" EventID="0" ProgrammaticallySendEventTrigger="false" Priority="Scheduled" InputConnectionType="Unicast" InputProductionTrigger="Cyclic" ConnectionPath="20 04 24 a4 2c 69 2d 00 41 03"
 InputTagSuffix="I" OutputTagSuffix="O">
<InputTag ExternalAccess="Read/Write">
<EngineeringUnits>
<EngineeringUnit Operand=".COUNTER00.COUNT">
<![CDATA[Counts]]>
</EngineeringUnit>
<EngineeringUnit Operand=".COUNTER01.COUNT">
<![CDATA[Counts]]>
</EngineeringUnit>
</EngineeringUnits>
<Data Format="Decorated">
<Structure DataType="AB:5000_HSC2:I:0">
<DataValueMember Name="RunMode" DataType="BOOL" Value="0"/>
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="0"/>
<DataValueMember Name="DiagnosticActive" DataType="BOOL" Value="0"/>
<DataValueMember Name="DiagnosticSequenceCount" DataType="SINT" Radix="Decimal" Value="0"/>
<StructureMember Name="Counter00" DataType="CHANNEL_HSC:I:0">
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="RolloverLeqRollunder" DataType="BOOL" Value="0"/>
<DataValueMember Name="NotANumber" DataType="BOOL" Value="0"/>
<DataValueMember Name="MissingPulseAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="ZeroFrequencyAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="ZeroFrequencyAvgAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="FrequencyAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="FrequencyAvgAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="PulseWidthAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="PulseWidthAvgAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="AccelAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="AccelAvgAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="DecelAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="DecelAvgAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="FrequencyOverrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="PartialAvgFrequency" DataType="BOOL" Value="0"/>
<DataValueMember Name="PartialAvgPulseWidth" DataType="BOOL" Value="0"/>
<DataValueMember Name="Direction" DataType="BOOL" Value="0"/>
<DataValueMember Name="StoredDirection" DataType="BOOL" Value="0"/>
<DataValueMember Name="Rollover" DataType="BOOL" Value="0"/>
<DataValueMember Name="Rollunder" DataType="BOOL" Value="0"/>
<DataValueMember Name="DataA" DataType="BOOL" Value="0"/>
<DataValueMember Name="DataB" DataType="BOOL" Value="0"/>
<DataValueMember Name="DataZ" DataType="BOOL" Value="0"/>
<DataValueMember Name="DataAOverridden" DataType="BOOL" Value="0"/>
<DataValueMember Name="DataBOverridden" DataType="BOOL" Value="0"/>
<DataValueMember Name="DataZOverridden" DataType="BOOL" Value="0"/>
<DataValueMember Name="Count" DataType="DINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="StoredCount" DataType="DINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="ScaledCount" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="ScaledStoredCount" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="RevolutionCount" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="StoredRevolutionCount" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="Frequency" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="FrequencyAvg" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="StoredFrequency" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="ScaledFrequency" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="ScaledFrequencyAvg" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="ScaledStoredFrequency" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="PulseWidth" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="PulseWidthAvg" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="StoredPulseWidth" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="QuadratureErrorCount" DataType="SINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="CountChangeIndicator" DataType="SINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="Accel" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="AccelAvg" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="StoredAccel" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="ScaledAccel" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="ScaledAccelAvg" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="ScaledStoredAccel" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
<StructureMember Name="Counter01" DataType="CHANNEL_HSC:I:0">
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="RolloverLeqRollunder" DataType="BOOL" Value="0"/>
<DataValueMember Name="NotANumber" DataType="BOOL" Value="0"/>
<DataValueMember Name="MissingPulseAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="ZeroFrequencyAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="ZeroFrequencyAvgAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="FrequencyAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="FrequencyAvgAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="PulseWidthAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="PulseWidthAvgAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="AccelAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="AccelAvgAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="DecelAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="DecelAvgAlarm" DataType="BOOL" Value="0"/>
<DataValueMember Name="FrequencyOverrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="PartialAvgFrequency" DataType="BOOL" Value="0"/>
<DataValueMember Name="PartialAvgPulseWidth" DataType="BOOL" Value="0"/>
<DataValueMember Name="Direction" DataType="BOOL" Value="0"/>
<DataValueMember Name="StoredDirection" DataType="BOOL" Value="0"/>
<DataValueMember Name="Rollover" DataType="BOOL" Value="0"/>
<DataValueMember Name="Rollunder" DataType="BOOL" Value="0"/>
<DataValueMember Name="DataA" DataType="BOOL" Value="0"/>
<DataValueMember Name="DataB" DataType="BOOL" Value="0"/>
<DataValueMember Name="DataZ" DataType="BOOL" Value="0"/>
<DataValueMember Name="DataAOverridden" DataType="BOOL" Value="0"/>
<DataValueMember Name="DataBOverridden" DataType="BOOL" Value="0"/>
<DataValueMember Name="DataZOverridden" DataType="BOOL" Value="0"/>
<DataValueMember Name="Count" DataType="DINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="StoredCount" DataType="DINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="ScaledCount" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="ScaledStoredCount" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="RevolutionCount" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="StoredRevolutionCount" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="Frequency" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="FrequencyAvg" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="StoredFrequency" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="ScaledFrequency" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="ScaledFrequencyAvg" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="ScaledStoredFrequency" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="PulseWidth" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="PulseWidthAvg" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="StoredPulseWidth" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="QuadratureErrorCount" DataType="SINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="CountChangeIndicator" DataType="SINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="Accel" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="AccelAvg" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="StoredAccel" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="ScaledAccel" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="ScaledAccelAvg" DataType="REAL" Radix="Float" Value="0.0"/>
<DataValueMember Name="ScaledStoredAccel" DataType="REAL" Radix="Float" Value="0.0"/>
</StructureMember>
<StructureMember Name="Window00" DataType="AB:5000_Window_Struct:I:0">
<DataValueMember Name="InWindow" DataType="BOOL" Value="0"/>
<DataValueMember Name="NotANumber" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Window01" DataType="AB:5000_Window_Struct:I:0">
<DataValueMember Name="InWindow" DataType="BOOL" Value="0"/>
<DataValueMember Name="NotANumber" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Window02" DataType="AB:5000_Window_Struct:I:0">
<DataValueMember Name="InWindow" DataType="BOOL" Value="0"/>
<DataValueMember Name="NotANumber" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Window03" DataType="AB:5000_Window_Struct:I:0">
<DataValueMember Name="InWindow" DataType="BOOL" Value="0"/>
<DataValueMember Name="NotANumber" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Window04" DataType="AB:5000_Window_Struct:I:0">
<DataValueMember Name="InWindow" DataType="BOOL" Value="0"/>
<DataValueMember Name="NotANumber" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Window05" DataType="AB:5000_Window_Struct:I:0">
<DataValueMember Name="InWindow" DataType="BOOL" Value="0"/>
<DataValueMember Name="NotANumber" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Window06" DataType="AB:5000_Window_Struct:I:0">
<DataValueMember Name="InWindow" DataType="BOOL" Value="0"/>
<DataValueMember Name="NotANumber" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Window07" DataType="AB:5000_Window_Struct:I:0">
<DataValueMember Name="InWindow" DataType="BOOL" Value="0"/>
<DataValueMember Name="NotANumber" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Output00" DataType="CHANNEL_DO_DIAG:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoad" DataType="BOOL" Value="0"/>
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Output01" DataType="CHANNEL_DO_DIAG:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoad" DataType="BOOL" Value="0"/>
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Output02" DataType="CHANNEL_DO_DIAG:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoad" DataType="BOOL" Value="0"/>
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Output03" DataType="CHANNEL_DO_DIAG:I:0">
<DataValueMember Name="Data" DataType="BOOL" Value="0"/>
<DataValueMember Name="Fault" DataType="BOOL" Value="0"/>
<DataValueMember Name="Uncertain" DataType="BOOL" Value="0"/>
<DataValueMember Name="NoLoad" DataType="BOOL" Value="0"/>
<DataValueMember Name="ShortCircuit" DataType="BOOL" Value="0"/>
</StructureMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
<![CDATA[[[0,2147483647,-2147483648,1.00000000e-001,0,0,0,0,10000000],[0,2147483647,-2147483648,1.00000000e-001
		,0,0,0,0,10000000],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0],[0,0],[0,0],[0,0]]]]>
</Data>
<Data Format="Decorated">
<Structure DataType="AB:5000_HSC2_DDDDDDDD:O:0">
<StructureMember Name="Counter00" DataType="CHANNEL_HSC:O:0">
<DataValueMember Name="Reset" DataType="BOOL" Value="0"/>
<DataValueMember Name="Hold" DataType="BOOL" Value="0"/>
<DataValueMember Name="Load" DataType="BOOL" Value="0"/>
<DataValueMember Name="Store" DataType="BOOL" Value="0"/>
<DataValueMember Name="Direction" DataType="BOOL" Value="0"/>
<DataValueMember Name="RolloverAck" DataType="BOOL" Value="0"/>
<DataValueMember Name="RollunderAck" DataType="BOOL" Value="0"/>
<DataValueMember Name="FrequencyAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="FrequencyAvgAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="PulseWidthAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="PulseWidthAvgAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="ZeroFrequencyAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="ZeroFrequencyAvgAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="MissingPulseAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="MissingPulseAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="AccelAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="DecelAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="AccelAvgAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="DecelAvgAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="ResetFrequencyOverrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="ResetQuadratureErrorCount" DataType="BOOL" Value="0"/>
<DataValueMember Name="RolloverValue" DataType="DINT" Radix="Decimal" Value="2147483647"/>
<DataValueMember Name="RollunderValue" DataType="DINT" Radix="Decimal" Value="-2147483648"/>
<DataValueMember Name="ZeroFrequencyAlarmLimit" DataType="REAL" Radix="Float" Value="0.1"/>
<DataValueMember Name="LoadCountValue" DataType="DINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="LoadRevolutionValue" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="OverrideDataAEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="OverrideDataBEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="OverrideDataZEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="OverrideDataAValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="OverrideDataBValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="OverrideDataZValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="MissingPulseAlarmLimit" DataType="DINT" Radix="Decimal" Value="10000000"/>
</StructureMember>
<StructureMember Name="Counter01" DataType="CHANNEL_HSC:O:0">
<DataValueMember Name="Reset" DataType="BOOL" Value="0"/>
<DataValueMember Name="Hold" DataType="BOOL" Value="0"/>
<DataValueMember Name="Load" DataType="BOOL" Value="0"/>
<DataValueMember Name="Store" DataType="BOOL" Value="0"/>
<DataValueMember Name="Direction" DataType="BOOL" Value="0"/>
<DataValueMember Name="RolloverAck" DataType="BOOL" Value="0"/>
<DataValueMember Name="RollunderAck" DataType="BOOL" Value="0"/>
<DataValueMember Name="FrequencyAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="FrequencyAvgAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="PulseWidthAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="PulseWidthAvgAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="ZeroFrequencyAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="ZeroFrequencyAvgAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="MissingPulseAlarmEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="MissingPulseAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="AccelAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="DecelAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="AccelAvgAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="DecelAvgAlarmUnlatch" DataType="BOOL" Value="0"/>
<DataValueMember Name="ResetFrequencyOverrange" DataType="BOOL" Value="0"/>
<DataValueMember Name="ResetQuadratureErrorCount" DataType="BOOL" Value="0"/>
<DataValueMember Name="RolloverValue" DataType="DINT" Radix="Decimal" Value="2147483647"/>
<DataValueMember Name="RollunderValue" DataType="DINT" Radix="Decimal" Value="-2147483648"/>
<DataValueMember Name="ZeroFrequencyAlarmLimit" DataType="REAL" Radix="Float" Value="0.1"/>
<DataValueMember Name="LoadCountValue" DataType="DINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="LoadRevolutionValue" DataType="INT" Radix="Decimal" Value="0"/>
<DataValueMember Name="OverrideDataAEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="OverrideDataBEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="OverrideDataZEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="OverrideDataAValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="OverrideDataBValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="OverrideDataZValue" DataType="BOOL" Value="0"/>
<DataValueMember Name="MissingPulseAlarmLimit" DataType="DINT" Radix="Decimal" Value="10000000"/>
</StructureMember>
<StructureMember Name="Window00" DataType="AB:5000_Window_DINT_Struct:O:0">
<DataValueMember Name="On" DataType="DINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="Off" DataType="DINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="HysteresisOn" DataType="DINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="HysteresisOff" DataType="DINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Window01" DataType="AB:5000_Window_DINT_Struct:O:0">
<DataValueMember Name="On" DataType="DINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="Off" DataType="DINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="HysteresisOn" DataType="DINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="HysteresisOff" DataType="DINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Window02" DataType="AB:5000_Window_DINT_Struct:O:0">
<DataValueMember Name="On" DataType="DINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="Off" DataType="DINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="HysteresisOn" DataType="DINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="HysteresisOff" DataType="DINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Window03" DataType="AB:5000_Window_DINT_Struct:O:0">
<DataValueMember Name="On" DataType="DINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="Off" DataType="DINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="HysteresisOn" DataType="DINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="HysteresisOff" DataType="DINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Window04" DataType="AB:5000_Window_DINT_Struct:O:0">
<DataValueMember Name="On" DataType="DINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="Off" DataType="DINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="HysteresisOn" DataType="DINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="HysteresisOff" DataType="DINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Window05" DataType="AB:5000_Window_DINT_Struct:O:0">
<DataValueMember Name="On" DataType="DINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="Off" DataType="DINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="HysteresisOn" DataType="DINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="HysteresisOff" DataType="DINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Window06" DataType="AB:5000_Window_DINT_Struct:O:0">
<DataValueMember Name="On" DataType="DINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="Off" DataType="DINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="HysteresisOn" DataType="DINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="HysteresisOff" DataType="DINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Window07" DataType="AB:5000_Window_DINT_Struct:O:0">
<DataValueMember Name="On" DataType="DINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="Off" DataType="DINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="HysteresisOn" DataType="DINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="HysteresisOff" DataType="DINT" Radix="Decimal" Value="0"/>
</StructureMember>
<StructureMember Name="Output00" DataType="CHANNEL_DO_OVERRIDE:O:0">
<DataValueMember Name="OverrideDataEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="OverrideDataValue" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Output01" DataType="CHANNEL_DO_OVERRIDE:O:0">
<DataValueMember Name="OverrideDataEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="OverrideDataValue" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Output02" DataType="CHANNEL_DO_OVERRIDE:O:0">
<DataValueMember Name="OverrideDataEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="OverrideDataValue" DataType="BOOL" Value="0"/>
</StructureMember>
<StructureMember Name="Output03" DataType="CHANNEL_DO_OVERRIDE:O:0">
<DataValueMember Name="OverrideDataEn" DataType="BOOL" Value="0"/>
<DataValueMember Name="OverrideDataValue" DataType="BOOL" Value="0"/>
</StructureMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
<ExtendedProperties>
<public><Vendor>Rockwell Automation/Allen-Bradley</Vendor><CatNum>5069-HSC2XOB4</CatNum><ConfigID>100</ConfigID><ADDAVersion>1</ADDAVersion></public>
</ExtendedProperties>
</Module>
""",
}


import random
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from l5x_memory_analyzer.sizing.constants import load_memory_model
from l5x_memory_analyzer.sizing.report import build_report

from sample_gen.manifest import append_manifest_row, write_sample_unmodeled
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "modules"
_MODEL = load_memory_model()

_ALL_CHILDREN = [c for c in _5069_AENT_CHAIN_BLOCKS if c != "5069-AENTR"]


def _rack_xml(children: list[str], renumber: bool = False) -> str:
    """`renumber=True`: rewrite each selected child's own upstream Port
    Address to a sequential slot (1..len(children)) instead of using its
    real captured value verbatim. Needed for a genuinely RANDOM subset --
    _ALL_CHILDREN's own dict insertion order already tracks each catalog's
    real captured slot 1-12 in order, so every _PLANS entry above (built
    from plain Python slices of that list) is naturally a CONTIGUOUS real
    slot range with no gap; random.sample picks an unordered subset, which
    is a real gap almost every time -- caught by this project's own
    non_sequential_module_slots lint check (write_sample_unmodeled's
    lint_or_raise). Safe to touch only the Port Address: confirmed via
    every real ConnectionPath value in this file being catalog-specific
    (unique per module, not slot-derived), and each child's own I/O
    Connection/ConfigTag content is per-module data unrelated to which
    slot it physically occupies (unlike the PointIO adapter case, there is
    no per-adapter aggregate structure here that depends on slot count --
    the AENTR's own real Bus Size=32 comfortably covers any subset up to
    12, confirmed already by n12_full importing clean)."""
    parts = [_5069_AENT_CHAIN_BLOCKS["5069-AENTR"]]
    for slot, cat in enumerate(children, start=1):
        block = _5069_AENT_CHAIN_BLOCKS[cat]
        if renumber:
            block = re.sub(
                r'(<Port Id="1" Address=")\d+("\s*Type="5069"\s*Upstream="true"\s*/>)',
                rf"\g<1>{slot}\g<2>", block, count=1,
            )
        parts.append(block)
    return "\n".join(parts)


def _combined_racks_xml(plans: dict[str, list[str]]) -> str:
    """James, 2026-09-03, after the 10 random racks imported clean as
    separate files: "i want all 10 in one file" -- 10 independent
    5069-AENTR adapters in one project. Each _5069_AENT_CHAIN_BLOCKS
    adapter block carries the SAME real captured Name ("AENT") and IP
    (192.168.1.1) -- fine standalone (matches _rack_xml/_write above,
    each its own file), a real collision the instant 2+ land in the same
    file, the same class of bug already fixed elsewhere in this project
    for composite/PointIO catalogs. Renames only the adapter's own
    Name="AENT" declaration and each of its children's ParentModule="AENT"
    reference (both exact-quoted-attribute matches, scoped precisely --
    no child catalog name contains the substring "AENT", confirmed
    against _ALL_CHILDREN) to "AENT{n}", and the adapter's own IP to a
    unique 192.168.{n}.1 -- nothing else in any block is touched."""
    parts = []
    for i, (_label, children) in enumerate(plans.items(), start=1):
        rack = _rack_xml(children, renumber=True)
        rack = rack.replace('Name="AENT"', f'Name="AENT{i}"', 1)
        rack = rack.replace('ParentModule="AENT"', f'ParentModule="AENT{i}"')
        rack = rack.replace('Address="192.168.1.1"', f'Address="192.168.{i}.1"', 1)
        parts.append(rack)
    return "\n".join(parts)


def _floor_bytes(l5x_text: str) -> int:
    """Real computed total across every SIZED entry -- the AENTR adapter
    itself (no Connections of its own, a pure fan-out bridge) and
    5069-SERIAL/A both fall to the unmodeled/$0 SizeError path, but every
    other real child module here has real Connection/ConfigTag content
    fully computable today, so a real nonzero floor is worth logging, not
    predicted_bytes=0 (same reasoning as gen_composite_realistic_v3.py's
    _floor_bytes)."""
    root = ET.fromstring(l5x_text)
    entries, _errors = build_report(root, _MODEL)
    return sum(e.bytes for e in entries)


def _write(out_name: str, children: list[str], renumber: bool = False) -> None:
    l5x = build_l5x(
        target_name=f"Rack5069_{out_name}", tags_xml="", extra_modules_xml=_rack_xml(children, renumber=renumber),
    )
    out_path = OUT_ROOT / f"rack_5069_{out_name}.L5X"
    write_sample_unmodeled(l5x, out_path)
    total = _floor_bytes(l5x)
    renumber_note = (
        " Slot Addresses renumbered sequentially from 1 (real captured values would leave gaps for "
        "this non-contiguous a random subset -- see _rack_xml's docstring); everything else, "
        "including each module's own I/O Connection/ConfigTag content, is untouched." if renumber else ""
    )
    description = (
        f"5069-AENTR remote rack (James, 2026-09-02, real reference upload; random-composition batch "
        f"added 2026-09-03: \"I want 10 ethernet racks with random cards and random sizes to "
        f"validate\"): one real 5069-AENTR EtherNet/IP adapter hosting {len(children)} real 5069-family "
        f"child modules on its own local bus ({', '.join(children)}), genericized structurally "
        f"verbatim from that reference.{renumber_note} Real floor total {total} (AENTR itself and "
        f"5069-SERIAL/A are unmodeled zero-connection/unresolved shapes -- real Capacity will run "
        f"somewhat higher). See OQ-MODULEIO for the per-catalog/rack-scale module_overhead question "
        f"this feeds."
    )
    append_manifest_row(f"rack_5069_{out_name}", description, "modules", out_path, total)
    print(f"Wrote {out_path} (floor {total} bytes)")


def _write_combined(out_name: str, plans: dict[str, list[str]]) -> None:
    """James, 2026-09-03, confirmed clean in real Studio 5000: "no errors,
    valid ok. add to your arsenal for the next mass generation." Writes
    N independent 5069-AENTR racks (see _combined_racks_xml) into ONE
    project -- reusable for any future plans dict, not just _RANDOM_PLANS
    (e.g. a future "mass generation" combining many rack compositions
    into one bigger multi-adapter file)."""
    modules_xml = _combined_racks_xml(plans)
    l5x = build_l5x(target_name=f"Rack5069_{out_name}", tags_xml="", extra_modules_xml=modules_xml)
    out_path = OUT_ROOT / f"rack_5069_{out_name}.L5X"
    write_sample_unmodeled(l5x, out_path)
    total = _floor_bytes(l5x)
    catalogs_summary = "; ".join(f"{i}:[{', '.join(c)}]" for i, c in enumerate(plans.values(), start=1))
    description = (
        f"5069-AENTR combined multi-rack (James, 2026-09-03: \"i want all 10 in one file\" -- "
        f"confirmed real Studio 5000 clean, then \"add to your arsenal for the next mass "
        f"generation\"): {len(plans)} independent real 5069-AENTR EtherNet/IP adapters in one "
        f"project (AENT1..AENT{len(plans)}, each its own unique IP 192.168.N.1), each hosting its "
        f"own real 5069-family child modules -- {catalogs_summary}. Real floor total {total}. "
        f"See OQ-MODULEIO."
    )
    append_manifest_row(f"rack_5069_{out_name}", description, "modules", out_path, total)
    print(f"Wrote {out_path} (floor {total} bytes)")


# Rack size scaling (2/4/6/8/10/12, the full real set) plus alternate
# catalog-mix compositions at a couple of fixed sizes to vary content, not
# just count -- James: "10+ 5069 racks."
_PLANS: dict[str, list[str]] = {
    "n02": _ALL_CHILDREN[0:2],
    "n02_alt": _ALL_CHILDREN[2:4],
    "n04": _ALL_CHILDREN[0:4],
    "n04_alt": _ALL_CHILDREN[4:8],
    "n06": _ALL_CHILDREN[0:6],
    "n06_alt": _ALL_CHILDREN[6:12],
    "n08": _ALL_CHILDREN[0:8],
    "n08_alt": _ALL_CHILDREN[2:10],
    "n10": _ALL_CHILDREN[0:10],
    "n10_alt": _ALL_CHILDREN[1:11],
    "n12_full": _ALL_CHILDREN[0:12],
}

# James, 2026-09-03, after confirming n12_full imports clean: "i think you
# just copied my file. i want 10 ethernet racks with random cards and
# random sizes to validate" -- fair: n12_full uses all 12 children in the
# same fixed docstring order as the uploaded reference, and every _PLANS
# entry above is a deterministic FIXED slice of _ALL_CHILDREN, not a real
# mix of card selection and rack size. Fixed seed so this batch is
# reproducible (re-running main() regenerates byte-identical files), but
# each of the 10 picks its own random size (3..12) and random subset (no
# repeats -- only 12 distinct real catalogs exist in this pool).
_RANDOM_PLANS: dict[str, list[str]] = {}
_rng = random.Random(20260903)
for _i in range(1, 11):
    _size = _rng.randint(3, len(_ALL_CHILDREN))
    _RANDOM_PLANS[f"rand{_i:02d}"] = _rng.sample(_ALL_CHILDREN, _size)


def _catalog_slug(catalog: str) -> str:
    return catalog.lower().replace("-", "_").replace("/", "_")


# One file per real 5069 child catalog, each holding the AENTR adapter and
# exactly ONE child (2026-09-04). Reason: a full-corpus recompute found the
# rack_5069_* family to be the single worst category error left (+28% to
# +35%, always under-predicting) because NO 5069 catalog had its own real
# per-catalog module_overhead point -- every one fell back to the flat
# 1,672 cross-catalog default. Only four 5069 catalogs (IB16/A, IB8S/A,
# IY4/A, OBV8S/A) had dedicated single-module captures to derive a real
# value from; the rest appear only inside multi-child racks where several
# ALWAYS co-occur (OA16+OB16, OB8+OF4, OF8+OW16 never appear apart), so a
# least-squares split between the members of those pairs is arbitrary
# rather than measured. These files break every one of those ties by
# isolating one catalog at a time -- the same single-module methodology
# behind every other real entry in module_overhead_by_catalog.
_SINGLE_PLANS: dict[str, list[str]] = {
    f"single_{_catalog_slug(c)}": [c] for c in _ALL_CHILDREN
}


def main() -> None:
    for label, children in _PLANS.items():
        _write(label, children)
    for label, children in _RANDOM_PLANS.items():
        _write(label, children, renumber=True)
    _write_combined("rand_combined10", _RANDOM_PLANS)
    for label, children in _SINGLE_PLANS.items():
        _write(label, children)
    print(f"\nDone. {len(_PLANS) + len(_RANDOM_PLANS) + 1 + len(_SINGLE_PLANS)} files.")


if __name__ == "__main__":
    main()
