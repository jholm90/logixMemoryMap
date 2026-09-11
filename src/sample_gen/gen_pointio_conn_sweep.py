"""POINT I/O connection-format cost sweep (OQ-POINTIOCONN).

Three real captures on 2026-09-11 -- one adapter and sixteen 1734-IB8/C
cards, in each of the three connection formats -- showed the model over-
predicting by 45% and 27% on two of them and under-predicting by 30% on
the third, and gave one clean single-variable result: a card's own
connection costs exactly 294 bytes more than no connection (Enhanced Data
minus Enhanced, 4,704 over 16 cards).

What those three points CANNOT separate is the adapter's own cost from the
per-card cost, because all three have sixteen cards, and the Optimized arm
changes the adapter catalog at the same time as the format. That needs a
count sweep per format, which is what this builds: N = 1, 2, 4, 8, 16
cards in each of the three formats, everything else held identical.
Differencing consecutive counts within one format gives the per-card cost
as the slope and that adapter's own cost as the intercept, each
independent of the other.

Every module block below is VERBATIM from the real 2026-09-11 exports --
the same donor convention gen_fw_catalog_matrix.py uses. Only what genuinely
depends on the card count is rewritten, and the three formats need
different rewrites because they carry the rack differently:

  - **Enhanced Data** is the easy one. The adapter's own InputTag is just
    the two status DINTs and every card carries its own self-contained
    InputData Connection, so nothing but the card count and the adapter's
    Bus Size changes.

  - **Enhanced** puts one StructureMember per card (Slot01..SlotNN) inside
    the adapter's InputTag, and the file DEFINES that module-scoped type
    itself in <ExtendedProperties> -- so the slot list is rewritten in both
    places, along with the status-array lengths and the output pad
    dimension. The type NAME carries a Studio-computed hash
    ("AB:1734_ERACK_649387C8:I:0") which is not derivable, so it is kept
    verbatim; the file supplies the matching definition, and whether
    Studio 5000 accepts a self-described type whose hash it would have
    computed differently is exactly the kind of thing a real conversion
    answers and guesswork does not.

  - **Optimized** aliases every card into the adapter's own SINT array and
    names the profile after the slot count ("AB:1734_17SLOT:I:0"). That
    name is systematic rather than hashed, so it is rewritten to match the
    count along with the array dimensions and element lists. Unlike the
    Enhanced case this type is NOT defined in the file -- it is a catalog
    profile -- so if AB:1734_<n>SLOT does not exist for some n, that file
    will fail to import. A failure there is a result, not a defect: it
    says the rack-optimized profile only exists at certain sizes.

A conversion failure in either of the latter two arms is therefore
informative on its own terms, and is logged rather than worked around.
"""

from __future__ import annotations

import re
from pathlib import Path

from sample_gen.lint import lint_or_raise
from sample_gen.manifest import append_manifest_row, predicted_bytes
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "modules"

ADAPTER_NAME = "PioAdapter"

# Powers of two plus the real 16-card point, so consecutive differences stay
# clean and the 16-card file reproduces the shape of the real capture.
CARD_COUNTS = (1, 2, 4, 8, 16)


AD_ENH = """<Module Name="{adapter}" CatalogNumber="1734-AENTR/C" Vendor="1" ProductType="12" ProductCode="196" Major="7" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false"
>
<EKey State="CompatibleModule"/>
<Ports>
<Port Id="1" Address="0" Type="PointIO" Upstream="false">
<Bus Size="17"/>
</Port>
<Port Id="2" Address="192.168.69.69" Type="Ethernet" Upstream="true"/>
</Ports>
<Communications>
<Connections>
<Connection Name="Output" RPI="20000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_ERACK_649387C8:I:0">
<DataValueMember Name="SlotStatusBits0_31" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000"/>
<DataValueMember Name="SlotStatusBits32_63" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000"/>
<StructureMember Name="Slot01" DataType="AB:1734_DI8_ERACK:I:0">
<DataValueMember Name="Data" DataType="SINT" Radix="Binary" Value="2#0000_0000"/>
</StructureMember>
<StructureMember Name="Slot02" DataType="AB:1734_DI8_ERACK:I:0">
<DataValueMember Name="Data" DataType="SINT" Radix="Binary" Value="2#0000_0000"/>
</StructureMember>
<StructureMember Name="Slot03" DataType="AB:1734_DI8_ERACK:I:0">
<DataValueMember Name="Data" DataType="SINT" Radix="Binary" Value="2#0000_0000"/>
</StructureMember>
<StructureMember Name="Slot04" DataType="AB:1734_DI8_ERACK:I:0">
<DataValueMember Name="Data" DataType="SINT" Radix="Binary" Value="2#0000_0000"/>
</StructureMember>
<StructureMember Name="Slot05" DataType="AB:1734_DI8_ERACK:I:0">
<DataValueMember Name="Data" DataType="SINT" Radix="Binary" Value="2#0000_0000"/>
</StructureMember>
<StructureMember Name="Slot06" DataType="AB:1734_DI8_ERACK:I:0">
<DataValueMember Name="Data" DataType="SINT" Radix="Binary" Value="2#0000_0000"/>
</StructureMember>
<StructureMember Name="Slot07" DataType="AB:1734_DI8_ERACK:I:0">
<DataValueMember Name="Data" DataType="SINT" Radix="Binary" Value="2#0000_0000"/>
</StructureMember>
<StructureMember Name="Slot08" DataType="AB:1734_DI8_ERACK:I:0">
<DataValueMember Name="Data" DataType="SINT" Radix="Binary" Value="2#0000_0000"/>
</StructureMember>
<StructureMember Name="Slot09" DataType="AB:1734_DI8_ERACK:I:0">
<DataValueMember Name="Data" DataType="SINT" Radix="Binary" Value="2#0000_0000"/>
</StructureMember>
<StructureMember Name="Slot10" DataType="AB:1734_DI8_ERACK:I:0">
<DataValueMember Name="Data" DataType="SINT" Radix="Binary" Value="2#0000_0000"/>
</StructureMember>
<StructureMember Name="Slot11" DataType="AB:1734_DI8_ERACK:I:0">
<DataValueMember Name="Data" DataType="SINT" Radix="Binary" Value="2#0000_0000"/>
</StructureMember>
<StructureMember Name="Slot12" DataType="AB:1734_DI8_ERACK:I:0">
<DataValueMember Name="Data" DataType="SINT" Radix="Binary" Value="2#0000_0000"/>
</StructureMember>
<StructureMember Name="Slot13" DataType="AB:1734_DI8_ERACK:I:0">
<DataValueMember Name="Data" DataType="SINT" Radix="Binary" Value="2#0000_0000"/>
</StructureMember>
<StructureMember Name="Slot14" DataType="AB:1734_DI8_ERACK:I:0">
<DataValueMember Name="Data" DataType="SINT" Radix="Binary" Value="2#0000_0000"/>
</StructureMember>
<StructureMember Name="Slot15" DataType="AB:1734_DI8_ERACK:I:0">
<DataValueMember Name="Data" DataType="SINT" Radix="Binary" Value="2#0000_0000"/>
</StructureMember>
<StructureMember Name="Slot16" DataType="AB:1734_DI8_ERACK:I:0">
<DataValueMember Name="Data" DataType="SINT" Radix="Binary" Value="2#0000_0000"/>
</StructureMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
<![CDATA[[0,0,[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]]]>
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_ERACK_86364FC6:O:0">
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
<ExtendedProperties>
<public><ConfigID>67108864</ConfigID><CatNum>1734-AENTR</CatNum><DataTypes><DataType Use="Target" Name="AB:1734_DI8_ERACK:I:0" Family="NoFamily" Class="IO" DeletionProhibited="false"><Members><Member Name="Data" DataType="SINT" Dimension="0" Radix="Binary" Hidden="false" ExternalAccess="Read/Write"/></Members></DataType><DataType Name="AB:1734_ERACK_649387C8:I:0" Class="IO"><Members><Member Name="SlotStatusBits0_31" DataType="DINT" Radix="Binary"/><Member Name="SlotStatusBits32_63" DataType="DINT" Radix="Binary"/><Member Name="Slot01" DataType="AB:1734_DI8_ERACK:I:0" Radix="NullType"/><Member Name="Slot02" DataType="AB:1734_DI8_ERACK:I:0" Radix="NullType"/><Member Name="Slot03" DataType="AB:1734_DI8_ERACK:I:0" Radix="NullType"/><Member Name="Slot04" DataType="AB:1734_DI8_ERACK:I:0" Radix="NullType"/><Member Name="Slot05" DataType="AB:1734_DI8_ERACK:I:0" Radix="NullType"/><Member Name="Slot06" DataType="AB:1734_DI8_ERACK:I:0" Radix="NullType"/><Member Name="Slot07" DataType="AB:1734_DI8_ERACK:I:0" Radix="NullType"/><Member Name="Slot08" DataType="AB:1734_DI8_ERACK:I:0" Radix="NullType"/><Member Name="Slot09" DataType="AB:1734_DI8_ERACK:I:0" Radix="NullType"/><Member Name="Slot10" DataType="AB:1734_DI8_ERACK:I:0" Radix="NullType"/><Member Name="Slot11" DataType="AB:1734_DI8_ERACK:I:0" Radix="NullType"/><Member Name="Slot12" DataType="AB:1734_DI8_ERACK:I:0" Radix="NullType"/><Member Name="Slot13" DataType="AB:1734_DI8_ERACK:I:0" Radix="NullType"/><Member Name="Slot14" DataType="AB:1734_DI8_ERACK:I:0" Radix="NullType"/><Member Name="Slot15" DataType="AB:1734_DI8_ERACK:I:0" Radix="NullType"/><Member Name="Slot16" DataType="AB:1734_DI8_ERACK:I:0" Radix="NullType"/></Members></DataType><DataType Name="AB:1734_ERACK_86364FC6:O:0" Class="IO"><Members><Member Name="SlotControlBits0_31" DataType="DINT" Radix="Decimal" Hidden="true"/><Member Name="SlotControlBits32_63" DataType="DINT" Radix="Decimal" Hidden="true"/><Member Name="pad" Radix="Decimal" DataType="SINT" Dimension="17" Hidden="true"/></Members></DataType></DataTypes></public>
</ExtendedProperties>
</Module>"""

CARD_ENH = """<Module CatalogNumber="1734-IB8/C" Vendor="1" ProductType="7" ProductCode="216" Major="3" Minor="1" ParentModule="{adapter}" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule"/>
<Ports>
<Port Id="1" Address="{slot}" Type="PointIO" Upstream="true"/>
</Ports>
<Communications>
<ConfigTag ConfigSize="48" ExternalAccess="Read/Write">
<Data Format="L5K">
<![CDATA[[52,103,0,4,1,0,190,0,1,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000]]]>
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_DI8_ERACK:C:0">
<DataValueMember Name="Pt0FilterOffOn" DataType="INT" Radix="Decimal" Value="1000"/>
<DataValueMember Name="Pt0FilterOnOff" DataType="INT" Radix="Decimal" Value="1000"/>
<DataValueMember Name="Pt1FilterOffOn" DataType="INT" Radix="Decimal" Value="1000"/>
<DataValueMember Name="Pt1FilterOnOff" DataType="INT" Radix="Decimal" Value="1000"/>
<DataValueMember Name="Pt2FilterOffOn" DataType="INT" Radix="Decimal" Value="1000"/>
<DataValueMember Name="Pt2FilterOnOff" DataType="INT" Radix="Decimal" Value="1000"/>
<DataValueMember Name="Pt3FilterOffOn" DataType="INT" Radix="Decimal" Value="1000"/>
<DataValueMember Name="Pt3FilterOnOff" DataType="INT" Radix="Decimal" Value="1000"/>
<DataValueMember Name="Pt4FilterOffOn" DataType="INT" Radix="Decimal" Value="1000"/>
<DataValueMember Name="Pt4FilterOnOff" DataType="INT" Radix="Decimal" Value="1000"/>
<DataValueMember Name="Pt5FilterOffOn" DataType="INT" Radix="Decimal" Value="1000"/>
<DataValueMember Name="Pt5FilterOnOff" DataType="INT" Radix="Decimal" Value="1000"/>
<DataValueMember Name="Pt6FilterOffOn" DataType="INT" Radix="Decimal" Value="1000"/>
<DataValueMember Name="Pt6FilterOnOff" DataType="INT" Radix="Decimal" Value="1000"/>
<DataValueMember Name="Pt7FilterOffOn" DataType="INT" Radix="Decimal" Value="1000"/>
<DataValueMember Name="Pt7FilterOnOff" DataType="INT" Radix="Decimal" Value="1000"/>
</Structure>
</Data>
</ConfigTag>
<Connections/>
</Communications>
<ExtendedProperties>
<public><ConfigID>67108866</ConfigID><CatNum>1734-IB8</CatNum><ModuleInformation><Input Values="00"/></ModuleInformation></public>
</ExtendedProperties>
</Module>"""

AD_ED = """<Module Name="{adapter}" CatalogNumber="1734-AENTR/C" Vendor="1" ProductType="12" ProductCode="196" Major="7" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false"
>
<EKey State="CompatibleModule"/>
<Ports>
<Port Id="1" Address="0" Type="PointIO" Upstream="false">
<Bus Size="17"/>
</Port>
<Port Id="2" Address="192.168.69.69" Type="Ethernet" Upstream="true"/>
</Ports>
<Communications>
<Connections>
<Connection Name="Output" RPI="20000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_ERACK_5FE9A870:I:0">
<DataValueMember Name="SlotStatusBits0_31" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000"/>
<DataValueMember Name="SlotStatusBits32_63" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000"/>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
<![CDATA[[0,0,[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]]]>
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_ERACK_86364FC6:O:0">
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
<ExtendedProperties>
<public><ConfigID>67108864</ConfigID><CatNum>1734-AENTR</CatNum><DataTypes><DataType Name="AB:1734_ERACK_5FE9A870:I:0" Class="IO"><Members><Member Name="SlotStatusBits0_31" DataType="DINT" Radix="Binary"/><Member Name="SlotStatusBits32_63" DataType="DINT" Radix="Binary"/><Member Name="pad" Radix="Decimal" DataType="SINT" Dimension="17" Hidden="true"/></Members></DataType><DataType Name="AB:1734_ERACK_86364FC6:O:0" Class="IO"><Members><Member Name="SlotControlBits0_31" DataType="DINT" Radix="Decimal" Hidden="true"/><Member Name="SlotControlBits32_63" DataType="DINT" Radix="Decimal" Hidden="true"/><Member Name="pad" Radix="Decimal" DataType="SINT" Dimension="17" Hidden="true"/></Members></DataType></DataTypes></public>
</ExtendedProperties>
</Module>"""

CARD_ED = """<Module CatalogNumber="1734-IB8/C" Vendor="1" ProductType="7" ProductCode="216" Major="3" Minor="1" ParentModule="{adapter}" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule"/>
<Ports>
<Port Id="1" Address="{slot}" Type="PointIO" Upstream="true"/>
</Ports>
<Communications CommMethod="536870913">
<ConfigTag ConfigSize="36" ExternalAccess="Read/Write">
<Data Format="L5K">
<![CDATA[[40,103,1,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000]]]>
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_DI8:C:0">
<DataValueMember Name="Pt0FilterOffOn" DataType="INT" Radix="Decimal" Value="1000"/>
<DataValueMember Name="Pt0FilterOnOff" DataType="INT" Radix="Decimal" Value="1000"/>
<DataValueMember Name="Pt1FilterOffOn" DataType="INT" Radix="Decimal" Value="1000"/>
<DataValueMember Name="Pt1FilterOnOff" DataType="INT" Radix="Decimal" Value="1000"/>
<DataValueMember Name="Pt2FilterOffOn" DataType="INT" Radix="Decimal" Value="1000"/>
<DataValueMember Name="Pt2FilterOnOff" DataType="INT" Radix="Decimal" Value="1000"/>
<DataValueMember Name="Pt3FilterOffOn" DataType="INT" Radix="Decimal" Value="1000"/>
<DataValueMember Name="Pt3FilterOnOff" DataType="INT" Radix="Decimal" Value="1000"/>
<DataValueMember Name="Pt4FilterOffOn" DataType="INT" Radix="Decimal" Value="1000"/>
<DataValueMember Name="Pt4FilterOnOff" DataType="INT" Radix="Decimal" Value="1000"/>
<DataValueMember Name="Pt5FilterOffOn" DataType="INT" Radix="Decimal" Value="1000"/>
<DataValueMember Name="Pt5FilterOnOff" DataType="INT" Radix="Decimal" Value="1000"/>
<DataValueMember Name="Pt6FilterOffOn" DataType="INT" Radix="Decimal" Value="1000"/>
<DataValueMember Name="Pt6FilterOnOff" DataType="INT" Radix="Decimal" Value="1000"/>
<DataValueMember Name="Pt7FilterOffOn" DataType="INT" Radix="Decimal" Value="1000"/>
<DataValueMember Name="Pt7FilterOnOff" DataType="INT" Radix="Decimal" Value="1000"/>
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="InputData" RPI="20000" Type="Input" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_DI8:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000"/>
<DataValueMember Name="Data" DataType="SINT" Radix="Binary" Value="2#0000_0000"/>
</Structure>
</Data>
</InputTag>
</Connection>
</Connections>
</Communications>
<ExtendedProperties>
<public><ConfigID>300</ConfigID><CatNum>1734-IB8</CatNum></public>
</ExtendedProperties>
</Module>"""

AD_OPT = """<Module Name="{adapter}" CatalogNumber="1734-AENT/A" Vendor="1" ProductType="12" ProductCode="108" Major="3" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false"
>
<EKey State="CompatibleModule"/>
<Ports>
<Port Id="1" Address="0" Type="PointIO" Upstream="false">
<Bus Size="17"/>
</Port>
<Port Id="2" Address="192.168.69.69" Type="Ethernet" Upstream="true"/>
</Ports>
<Communications CommMethod="805306369">
<Connections>
<Connection Name="Output" RPI="20000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_17SLOT:I:0">
<DataValueMember Name="SlotStatusBits0_31" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000"/>
<DataValueMember Name="SlotStatusBits32_63" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000"/>
<ArrayMember Name="Data" DataType="SINT" Dimensions="17" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000"/>
<Element Index="[1]" Value="2#0000_0000"/>
<Element Index="[2]" Value="2#0000_0000"/>
<Element Index="[3]" Value="2#0000_0000"/>
<Element Index="[4]" Value="2#0000_0000"/>
<Element Index="[5]" Value="2#0000_0000"/>
<Element Index="[6]" Value="2#0000_0000"/>
<Element Index="[7]" Value="2#0000_0000"/>
<Element Index="[8]" Value="2#0000_0000"/>
<Element Index="[9]" Value="2#0000_0000"/>
<Element Index="[10]" Value="2#0000_0000"/>
<Element Index="[11]" Value="2#0000_0000"/>
<Element Index="[12]" Value="2#0000_0000"/>
<Element Index="[13]" Value="2#0000_0000"/>
<Element Index="[14]" Value="2#0000_0000"/>
<Element Index="[15]" Value="2#0000_0000"/>
<Element Index="[16]" Value="2#0000_0000"/>
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
<![CDATA[[0,0,[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]]]>
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_17SLOT:O:0">
<ArrayMember Name="Data" DataType="SINT" Dimensions="17" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000"/>
<Element Index="[1]" Value="2#0000_0000"/>
<Element Index="[2]" Value="2#0000_0000"/>
<Element Index="[3]" Value="2#0000_0000"/>
<Element Index="[4]" Value="2#0000_0000"/>
<Element Index="[5]" Value="2#0000_0000"/>
<Element Index="[6]" Value="2#0000_0000"/>
<Element Index="[7]" Value="2#0000_0000"/>
<Element Index="[8]" Value="2#0000_0000"/>
<Element Index="[9]" Value="2#0000_0000"/>
<Element Index="[10]" Value="2#0000_0000"/>
<Element Index="[11]" Value="2#0000_0000"/>
<Element Index="[12]" Value="2#0000_0000"/>
<Element Index="[13]" Value="2#0000_0000"/>
<Element Index="[14]" Value="2#0000_0000"/>
<Element Index="[15]" Value="2#0000_0000"/>
<Element Index="[16]" Value="2#0000_0000"/>
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
<ExtendedProperties>
<public><ConfigID>262145</ConfigID><CatNum>1734-AENT</CatNum></public>
</ExtendedProperties>
</Module>"""

CARD_OPT = """<Module CatalogNumber="1734-IB8/C" Vendor="1" ProductType="7" ProductCode="216" Major="3" Minor="1" ParentModule="{adapter}" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="ExactMatch"/>
<Ports>
<Port Id="1" Address="{slot}" Type="PointIO" Upstream="true"/>
</Ports>
<Communications CommMethod="1073741824">
<ConfigTag ConfigSize="36" ExternalAccess="Read/Write">
<Data Format="L5K">
<![CDATA[[40,103,1,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000]]]>
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_DI8:C:0">
<DataValueMember Name="Pt0FilterOffOn" DataType="INT" Radix="Decimal" Value="1000"/>
<DataValueMember Name="Pt0FilterOnOff" DataType="INT" Radix="Decimal" Value="1000"/>
<DataValueMember Name="Pt1FilterOffOn" DataType="INT" Radix="Decimal" Value="1000"/>
<DataValueMember Name="Pt1FilterOnOff" DataType="INT" Radix="Decimal" Value="1000"/>
<DataValueMember Name="Pt2FilterOffOn" DataType="INT" Radix="Decimal" Value="1000"/>
<DataValueMember Name="Pt2FilterOnOff" DataType="INT" Radix="Decimal" Value="1000"/>
<DataValueMember Name="Pt3FilterOffOn" DataType="INT" Radix="Decimal" Value="1000"/>
<DataValueMember Name="Pt3FilterOnOff" DataType="INT" Radix="Decimal" Value="1000"/>
<DataValueMember Name="Pt4FilterOffOn" DataType="INT" Radix="Decimal" Value="1000"/>
<DataValueMember Name="Pt4FilterOnOff" DataType="INT" Radix="Decimal" Value="1000"/>
<DataValueMember Name="Pt5FilterOffOn" DataType="INT" Radix="Decimal" Value="1000"/>
<DataValueMember Name="Pt5FilterOnOff" DataType="INT" Radix="Decimal" Value="1000"/>
<DataValueMember Name="Pt6FilterOffOn" DataType="INT" Radix="Decimal" Value="1000"/>
<DataValueMember Name="Pt6FilterOnOff" DataType="INT" Radix="Decimal" Value="1000"/>
<DataValueMember Name="Pt7FilterOffOn" DataType="INT" Radix="Decimal" Value="1000"/>
<DataValueMember Name="Pt7FilterOnOff" DataType="INT" Radix="Decimal" Value="1000"/>
</Structure>
</Data>
</ConfigTag>
<Connections>
<RackConnection>
<InAliasTag/>
</RackConnection>
</Connections>
</Communications>
<ExtendedProperties>
<public><ConfigID>262147</ConfigID><CatNum>1734-IB8</CatNum></public>
</ExtendedProperties>
</Module>"""


def _resize_l5k_slot_array(block: str, slots: int) -> str:
    """The adapter's L5K status blob carries one zero per slot.

    Real shape "[0,0,[0,0,...]]" -- two status words then a per-slot array
    sized to the rack. Left at 17 on a 4-card rack it would describe a rack
    that is not there.
    """
    return re.sub(
        r"\[0,0,\[0(?:,0)*\]\]",
        "[0,0,[" + ",".join(["0"] * slots) + "]]",
        block,
    )


def _keep_first_slots(block: str, cards: int) -> str:
    """Drop the Slot<NN> entries above the card count, in both places the
    Enhanced adapter lists them: the Decorated StructureMembers and the
    module-scoped DataType definition in <ExtendedProperties>."""
    def drop_structure(m: re.Match) -> str:
        return m.group(0) if int(m.group(1)) <= cards else ""

    block = re.sub(
        r'<StructureMember Name="Slot(\d+)".*?</StructureMember>\n?',
        drop_structure, block, flags=re.S,
    )
    return re.sub(
        r'<Member Name="Slot(\d+)"[^>]*/>',
        drop_structure, block,
    )


def _resize_element_list(block: str, slots: int) -> str:
    """Trim each ArrayMember's <Element> list to the new dimension."""
    def fix(m: re.Match) -> str:
        head, elements, tail = m.group(1), m.group(2), m.group(3)
        kept = [
            el.group(0)
            for el in re.finditer(r'<Element Index="\[(\d+)\]"[^>]*/>\n?', elements)
            if int(el.group(1)) < slots
        ]
        return head + "".join(kept) + tail

    return re.sub(
        r'(<ArrayMember Name="Data"[^>]*>\n?)(.*?)(</ArrayMember>)',
        fix, block, flags=re.S,
    )


def _enhanced_adapter(cards: int) -> str:
    slots = cards + 1
    block = AD_ENH.format(adapter=ADAPTER_NAME)
    block = block.replace('<Bus Size="17"/>', f'<Bus Size="{slots}"/>')
    block = _resize_l5k_slot_array(block, slots)
    block = _keep_first_slots(block, cards)
    # The output image's pad array is sized to the rack, same as the status
    # array above.
    block = block.replace('DataType="SINT" Dimension="17"',
                          f'DataType="SINT" Dimension="{slots}"')
    return block


def _enhanced_data_adapter(cards: int) -> str:
    slots = cards + 1
    block = AD_ED.format(adapter=ADAPTER_NAME)
    block = block.replace('<Bus Size="17"/>', f'<Bus Size="{slots}"/>')
    # Its InputTag is only the two status DINTs, but BOTH its input and
    # output module-scoped types still carry a rack-sized "pad" SINT array,
    # and both L5K blobs carry a per-slot zero list. Missed on the first
    # pass, which left every count in this arm describing a 17-slot rack.
    block = _resize_l5k_slot_array(block, slots)
    block = block.replace('DataType="SINT" Dimension="17"',
                          f'DataType="SINT" Dimension="{slots}"')
    return block


def _optimized_adapter(cards: int) -> str:
    slots = cards + 1
    block = AD_OPT.format(adapter=ADAPTER_NAME)
    block = block.replace('<Bus Size="17"/>', f'<Bus Size="{slots}"/>')
    block = block.replace("AB:1734_17SLOT", f"AB:1734_{slots}SLOT")
    block = _resize_l5k_slot_array(block, slots)
    block = block.replace('DataType="SINT" Dimensions="17"',
                          f'DataType="SINT" Dimensions="{slots}"')
    block = _resize_element_list(block, slots)
    return block


FORMATS = {
    "enhanced": (
        _enhanced_adapter, CARD_ENH, "1734-AENTR/C",
        "no connection of its own, ConfigTag only; the adapter's InputTag "
        "carries one StructureMember per card",
    ),
    "enhdata": (
        _enhanced_data_adapter, CARD_ED, "1734-AENTR/C",
        "each card on its own InputData Connection; the adapter's InputTag "
        "is just the two status DINTs",
    ),
    "optimized": (
        _optimized_adapter, CARD_OPT, "1734-AENT/A",
        "each card rack-aliased into the adapter's own SINT array via "
        "RackConnection/InAliasTag",
    ),
}


# --- naming dimension -----------------------------------------------------
#
# Every 1734-IB8/C card in all three real exports carries NO Name attribute
# at all -- catalog and slot only. That is the unusual shape, not the
# normal one: a module you name in the I/O tree gets module-defined tags of
# its own, and this project already knows that a tag's NAME LENGTH costs
# real bytes (memory_model.yaml alias_tag, and the AOI/UDT type-name-length
# buckets). So naming a card plausibly costs something, plausibly scales
# with the name, and plausibly differs by connection format -- a
# rack-aliased card has no tag of its own to name, so it may well be free
# there and not free in the other two.
#
# None of that is measured. These arms measure it, holding everything else
# at the values the unnamed files already use so the difference is the name
# and nothing else.

# Minimum 5: the "Crd<nn>" stem itself is 5 characters. Padded with
# letters, never underscores -- see builders.validate_logix_name.
NAME_LENGTHS = (5, 8, 16, 24, 32)
DEFAULT_NAME_LENGTH = 8


def _card_name(index: int, length: int) -> str:
    stem = f"Crd{index:02d}"
    if length < len(stem):
        raise ValueError(f"name length {length} is shorter than the {len(stem)}-char stem")
    return stem + "X" * (length - len(stem))


def _modules_xml(fmt: str, cards: int, name_length: int | None = None) -> str:
    """`name_length` None leaves the cards nameless, exactly as the real
    exports have them."""
    adapter_fn, card_xml, _catalog, _note = FORMATS[fmt]
    parts = [adapter_fn(cards)]
    for slot in range(1, cards + 1):
        card = card_xml.format(adapter=ADAPTER_NAME, slot=slot)
        if name_length is not None:
            name = _card_name(slot, name_length)
            card = card.replace("<Module ", f'<Module Name="{name}" ', 1)
        parts.append(card)
    return "\n".join(parts)


def _write(l5x: str, name: str, description: str) -> None:
    out = OUT_ROOT / f"{name}.L5X"
    lint_or_raise(l5x, context=str(out))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(l5x, encoding="utf-8")
    append_manifest_row(name, description, "modules", out, predicted_bytes(l5x))
    print(f"Wrote {out}")


# Target names stay within Logix identifier rules (no trailing underscore,
# no sequential underscores, no leading digit) -- see builders.validate_logix_name.
_TARGET_STEM = {"enhanced": "PioEnh", "enhdata": "PioEnhData", "optimized": "PioOpt"}


def _connection_format_sweep() -> None:
    for fmt, (_fn, _card, catalog, note) in FORMATS.items():
        for count in CARD_COUNTS:
            _write(
                build_l5x(
                    target_name=f"{_TARGET_STEM[fmt]}N{count:02d}",
                    tags_xml="",
                    extra_modules_xml=_modules_xml(fmt, count),
                ),
                f"pioconn_{fmt}_n{count:02d}",
                f"{catalog} adapter with {count} 1734-IB8/C card(s), {note}. "
                f"Differenced against the other counts in this format this "
                f"separates the per-card cost from the adapter's own -- the "
                f"three real 16-card captures cannot, having the same card "
                f"count. OQ-POINTIOCONN.",
            )


def _naming_sweep() -> None:
    """Named vs nameless cards, and what a name costs.

    Three questions, one per arm, each differenced against a file that
    already exists rather than against a fresh control:

      1. Does naming a card cost anything, and does that depend on the
         connection format? One named file per format at 8 cards, against
         the nameless pioconn_<fmt>_n08. A rack-aliased card has no tag of
         its own, so Optimized may well be free where the other two are
         not -- that contrast is the point.
      2. Does the cost scale with the name, the way every other
         name-length cost in this model does? 5/8/16/24/32 characters at 8
         cards, Enhanced Data.
      3. Is it per-card or once per file? 1/2/4/16 cards at a fixed name
         length, against the 8-card point from arm 1.
    """
    # 1. name presence, across all three connection formats
    for fmt, (_fn, _card, catalog, note) in FORMATS.items():
        _write(
            build_l5x(
                target_name=f"{_TARGET_STEM[fmt]}Nm08",
                tags_xml="",
                extra_modules_xml=_modules_xml(fmt, 8, DEFAULT_NAME_LENGTH),
            ),
            f"pioname_{fmt}_named_n08",
            f"{catalog} adapter with 8 NAMED 1734-IB8/C cards "
            f"({DEFAULT_NAME_LENGTH}-character names), {note}. Against the "
            f"nameless pioconn_{fmt}_n08 this is the cost of naming a card, "
            f"per connection format -- every card in all three real exports "
            f"is nameless, which is the unusual shape and has never been "
            f"differenced against the normal one. OQ-POINTIOCONN.",
        )

    # 2. name length, Enhanced Data
    for length in NAME_LENGTHS:
        _write(
            build_l5x(
                target_name=f"PioNmLen{length:02d}",
                tags_xml="",
                extra_modules_xml=_modules_xml("enhdata", 8, length),
            ),
            f"pioname_enhdata_len{length:02d}_n08",
            f"8 named 1734-IB8/C cards with {length}-character names, Enhanced "
            f"Data. Swept against the other lengths this says whether a card "
            f"name is charged by the character the way every other "
            f"name-length cost in this model is, or at a flat rate. "
            f"OQ-POINTIOCONN.",
        )

    # 3. named-card count, Enhanced Data
    for count in (1, 2, 4, 16):
        _write(
            build_l5x(
                target_name=f"PioNmCnt{count:02d}",
                tags_xml="",
                extra_modules_xml=_modules_xml("enhdata", count, DEFAULT_NAME_LENGTH),
            ),
            f"pioname_enhdata_named_n{count:02d}",
            f"{count} named 1734-IB8/C card(s), Enhanced Data, "
            f"{DEFAULT_NAME_LENGTH}-character names. With the 8-card point "
            f"this separates a per-card naming cost from a once-per-file one, "
            f"and differences cleanly against the nameless "
            f"pioconn_enhdata_n{count:02d} at the same count. OQ-POINTIOCONN.",
        )


def main() -> None:
    _connection_format_sweep()
    _naming_sweep()


if __name__ == "__main__":
    main()
