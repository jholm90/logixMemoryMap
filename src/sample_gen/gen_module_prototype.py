"""Module/IO prototype batch (2026-08-27, James: "generate me a sample with
a 1756-ib16 in the local rack at slot 1... make another with a known
ethernet module off of the local L81 ethernet port... make a 3rd file with
a local ethernet card and an ethernet device located on that port. i
refuse to generate you all the io stuff. you will need to make this work
on your own. i will test your generated files. dont spam me with all the
io module files right away youll need to validate your builder engines.").

Deliberately exactly 3 files, no more -- James's own instruction, and this
project's own discipline against padding a batch beyond what's actually
needed to validate something. Each Module element below is NOT invented --
it's a genericized (customer-identifying names/comments/real values
stripped, replaced with plain placeholders/zeros) but STRUCTURALLY
VERBATIM copy of a real Module found in samples/local/ during this same
session's research pass, chosen specifically because building this batch
surfaced real structural facts this project's module parser (parser/
modules.py) didn't yet account for:

  - InputTag/OutputTag/ConfigTag are usually nested INSIDE the relevant
    <Connection> element, not always direct <Communications> children.
  - A "simple" point-to-point Connection (no InputCxnPoint/OutputCxnPoint)
    often has NO InputSize/OutputSize attribute at all -- only
    Connections using explicit CIP connection-point addressing state size
    directly. real byte count for these has to come from the nested
    Structure's own member content, not an attribute (not yet wired --
    parser correctness is a SEPARATE, later task from generating valid
    files, see docs/OPEN_QUESTIONS.md OQ-MODULEIO).
  - A rack-optimized remote-chassis module (behind a 1756-EN2T-class
    bridge) uses <RackConnection><InAliasTag/></RackConnection> instead
    of <Connection> entirely -- its own real I/O data is aliased into the
    bridge's own big Slot array, not a separate allocation of its own.

  1. group_local_backplane -- a 1756-IB16 (16-pt DC input) at slot 1,
     processor at slot 0 (the default wrapper CPU). Genericized from a
     real 1756-IB16 module (ConfigTag ConfigSize=24 + a Decorated
     AB:1756_DI:C:0 config structure; one "StandardInput" Connection
     with a nested InputTag, Decorated AB:1756_DI:I:0 structure, no
     stated InputSize).
  2. group_ethernet_off_cpu_port -- a 1734-AENTR/C (Point I/O Ethernet
     adapter, real/known Rockwell catalog number, non-safety, non-motion)
     connected directly to the L81's own embedded Ethernet port
     (ParentModule="Local", ParentModPortId="2", matching wrapper.py's
     own default CPU Ethernet-port numbering). Genericized from a real
     1734-AENTR/C module -- a single "Output" Connection carrying BOTH
     InputTag and OutputTag nested inside it (rack-optimized Point I/O
     shape, AB:1734_14SLOT:I:0/O:0, no ConfigTag at all for this one).
  3. group_ethernet_bridge_with_downstream -- a "local ethernet card"
     (1756-EN2T, real catalog number, ParentModule="Local" off the CPU's
     embedded Ethernet port) hosting a small real remote chassis (Bus
     Size=4, matching a real 1756-A4 4-slot chassis) with exactly ONE
     downstream module actually populated (slot 1: a 1756-IA16, AC
     input) -- genericized from a real 1756-EN2T module (one "Output"
     Connection, InputTag+OutputTag nested, Decorated
     AB:1756_ENET_4SLOT:I:0/O:0 structures, a 4-element Slot ArrayMember
     matching the chassis's full rated size regardless of how many slots
     are actually populated -- confirmed real behavior, not guessed) plus
     one downstream 1756-IA16-shaped Module using the real RackConnection/
     InAliasTag shape (ConfigTag present, no separate connection data of
     its own -- its I/O is aliased into the bridge's own Slot[1] entry).

Run: python -m sample_gen.gen_module_prototype
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.manifest import append_manifest_row, write_sample_unmodeled
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "modules"


def _write_unmodeled(l5x: str, out_name: str, description: str) -> None:
    # Module sizing has no confirmed controller-memory formula yet
    # (OQ-MODULEIO) -- predicted_bytes=0 with the "unmodeled" convention
    # already used for AXIS_*/MOTION_GROUP, not a guess.
    out_path = OUT_ROOT / f"{out_name}.L5X"
    write_sample_unmodeled(l5x, out_path)
    append_manifest_row(out_name, description, "modules", out_path, 0)
    print(f"Wrote {out_path} (predicted N/A -- module cost unmodeled, see OQ-MODULEIO)")


# ---------------------------------------------------------------------------
# 1. Local backplane digital input module, slot 1.
# ---------------------------------------------------------------------------

_IB16_MODULE_XML = """\
<Module Name="Local_DC_Input" CatalogNumber="1756-IB16" Vendor="1" ProductType="7" ProductCode="11" Major="2" Minor="5" ParentModule="Local" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule"/>
<Ports>
<Port Id="1" Address="1" Type="ICP" Upstream="true"/>
</Ports>
<Communications CommMethod="536870913">
<ConfigTag ConfigSize="24" ExternalAccess="Read/Write">
<Data Format="L5K"><![CDATA[[28,16,1,0,0,0,1,1,1,1,0,0,0,0,65535,65535]]]></Data>
<Data Format="Decorated">
<Structure DataType="AB:1756_DI:C:0">
<DataValueMember Name="DiagCOSDisable" DataType="BOOL" Value="0"/>
<DataValueMember Name="FilterOffOn_0_7" DataType="SINT" Radix="Decimal" Value="1"/>
<DataValueMember Name="FilterOnOff_0_7" DataType="SINT" Radix="Decimal" Value="1"/>
<DataValueMember Name="FilterOffOn_8_15" DataType="SINT" Radix="Decimal" Value="1"/>
<DataValueMember Name="FilterOnOff_8_15" DataType="SINT" Radix="Decimal" Value="1"/>
<DataValueMember Name="FilterOffOn_16_23" DataType="SINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="FilterOnOff_16_23" DataType="SINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="FilterOffOn_24_31" DataType="SINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="FilterOnOff_24_31" DataType="SINT" Radix="Decimal" Value="0"/>
<DataValueMember Name="COSOnOffEn" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_1111_1111_1111_1111"/>
<DataValueMember Name="COSOffOnEn" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_1111_1111_1111_1111"/>
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="StandardInput" RPI="10000" Type="Input" EventID="0" ProgrammaticallySendEventTrigger="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1756_DI:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000"/>
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000"/>
</Structure>
</Data>
</InputTag>
</Connection>
</Connections>
</Communications>
</Module>"""


def group_local_backplane() -> None:
    l5x = build_l5x(target_name="ModuleProto1IB16", tags_xml="", extra_modules_xml=_IB16_MODULE_XML)
    _write_unmodeled(
        l5x, "moduleproto_1756ib16_slot1",
        "Local backplane: 1756-L81E (slot 0, the default wrapper CPU) + 1756-IB16 16-pt DC input "
        "module at slot 1 -- genericized from a real corpus module, structurally verbatim "
        "(ConfigTag ConfigSize=24 stated directly, one Connection with a nested InputTag whose "
        "InputSize is NOT stated -- real byte count would need computing from the Decorated "
        "Structure content, not read off an attribute; see OQ-MODULEIO)",
    )


# ---------------------------------------------------------------------------
# 2. Known Ethernet module directly off the CPU's own embedded Ethernet port.
# ---------------------------------------------------------------------------

_AENTR_MODULE_XML = """\
<Module Name="PointIO_Adapter" CatalogNumber="1734-AENTR/C" Vendor="1" ProductType="12" ProductCode="196" Major="6" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule"/>
<Ports>
<Port Id="1" Address="0" Type="PointIO" Upstream="false">
<Bus Size="14"/>
</Port>
<Port Id="2" Address="192.168.1.50" Type="Ethernet" Upstream="true"/>
</Ports>
<Communications CommMethod="805306369">
<Connections>
<Connection Name="Output" RPI="5000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_14SLOT:I:0">
<DataValueMember Name="SlotStatusBits0_31" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0001"/>
<DataValueMember Name="SlotStatusBits32_63" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000"/>
<ArrayMember Name="Data" DataType="SINT" Dimensions="14" Radix="Binary">
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
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K"><![CDATA[[-4065,-1,[0,0,0,0,0,0,0,0,0,0,0,0,0,0]]]]></Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_14SLOT:O:0">
<ArrayMember Name="Data" DataType="SINT" Dimensions="14" Radix="Binary">
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
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>"""


def group_ethernet_off_cpu_port() -> None:
    l5x = build_l5x(target_name="ModuleProto2AENTR", tags_xml="", extra_modules_xml=_AENTR_MODULE_XML)
    _write_unmodeled(
        l5x, "moduleproto_1734aentr_cpu_ethernet",
        "1734-AENTR/C (Point I/O Ethernet adapter, a known/real Rockwell catalog number, non-safety, "
        "non-motion) connected directly to the 1756-L81E's own embedded Ethernet port (ParentModPortId=2, "
        "not a backplane slot) -- genericized from a real corpus module, structurally verbatim (single "
        "rack-optimized Connection carrying BOTH InputTag and OutputTag, no ConfigTag at all, no stated "
        "InputSize/OutputSize -- see OQ-MODULEIO)",
    )


# ---------------------------------------------------------------------------
# 3. Local Ethernet bridge + one downstream device on that remote chassis.
# ---------------------------------------------------------------------------

_EN2T_WITH_DOWNSTREAM_MODULE_XML = """\
<Module Name="Remote_EN2T" CatalogNumber="1756-EN2T" Vendor="1" ProductType="12" ProductCode="166" Major="11" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="Disabled"/>
<Ports>
<Port Id="1" Address="1" Type="ICP" Upstream="false">
<Bus Size="4"/>
</Port>
<Port Id="2" Address="192.168.2.10" Type="Ethernet" Upstream="true"/>
</Ports>
<Communications CommMethod="805306369">
<Connections>
<Connection Name="Output" RPI="10000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1756_ENET_4SLOT:I:0">
<DataValueMember Name="SlotStatusBits" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0010"/>
<ArrayMember Name="Slot" DataType="AB:1756_ENET_SLOT:I:0" Dimensions="4">
<Element Index="[0]">
<Structure DataType="AB:1756_ENET_SLOT:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111"/>
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000"/>
</Structure>
</Element>
<Element Index="[1]">
<Structure DataType="AB:1756_ENET_SLOT:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000"/>
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000"/>
</Structure>
</Element>
<Element Index="[2]">
<Structure DataType="AB:1756_ENET_SLOT:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111"/>
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000"/>
</Structure>
</Element>
<Element Index="[3]">
<Structure DataType="AB:1756_ENET_SLOT:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111"/>
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000"/>
</Structure>
</Element>
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K"><![CDATA[[-1,[[0],[0],[0],[0]]]]]></Data>
<Data Format="Decorated">
<Structure DataType="AB:1756_ENET_4SLOT:O:0">
<ArrayMember Name="Slot" DataType="AB:1756_ENET_SLOT:O:0" Dimensions="4">
<Element Index="[0]">
<Structure DataType="AB:1756_ENET_SLOT:O:0">
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000"/>
</Structure>
</Element>
<Element Index="[1]">
<Structure DataType="AB:1756_ENET_SLOT:O:0">
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000"/>
</Structure>
</Element>
<Element Index="[2]">
<Structure DataType="AB:1756_ENET_SLOT:O:0">
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000"/>
</Structure>
</Element>
<Element Index="[3]">
<Structure DataType="AB:1756_ENET_SLOT:O:0">
<DataValueMember Name="Data" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000"/>
</Structure>
</Element>
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
<ExtendedProperties>
<public><Vendor>Rockwell Automation/Allen-Bradley</Vendor><CatNum>1756-EN2T</CatNum><ConfigID>4456551</ConfigID></public>
</ExtendedProperties>
</Module>
<Module Name="Remote_AC_Input" CatalogNumber="1756-IA16" Vendor="1" ProductType="7" ProductCode="9" Major="3" Minor="4" ParentModule="Remote_EN2T" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule"/>
<Ports>
<Port Id="1" Address="1" Type="ICP" Upstream="true"/>
</Ports>
<Communications CommMethod="1073741824">
<ConfigTag ConfigSize="24" ExternalAccess="Read/Write">
<Data Format="L5K"><![CDATA[[28,16,0,0,0,0,1,9,1,9,1,9,1,9,-1,-1]]]></Data>
<Data Format="Decorated">
<Structure DataType="AB:1756_DI:C:1">
<DataValueMember Name="FilterOffOn_0_7" DataType="SINT" Radix="Decimal" Value="1"/>
<DataValueMember Name="FilterOnOff_0_7" DataType="SINT" Radix="Decimal" Value="9"/>
<DataValueMember Name="FilterOffOn_8_15" DataType="SINT" Radix="Decimal" Value="1"/>
<DataValueMember Name="FilterOnOff_8_15" DataType="SINT" Radix="Decimal" Value="9"/>
<DataValueMember Name="FilterOffOn_16_23" DataType="SINT" Radix="Decimal" Value="1"/>
<DataValueMember Name="FilterOnOff_16_23" DataType="SINT" Radix="Decimal" Value="9"/>
<DataValueMember Name="FilterOffOn_24_31" DataType="SINT" Radix="Decimal" Value="1"/>
<DataValueMember Name="FilterOnOff_24_31" DataType="SINT" Radix="Decimal" Value="9"/>
<DataValueMember Name="COSOnOffEn" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111"/>
<DataValueMember Name="COSOffOnEn" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111"/>
</Structure>
</Data>
</ConfigTag>
<Connections>
<RackConnection>
<InAliasTag/>
</RackConnection>
</Connections>
</Communications>
</Module>"""


def group_ethernet_bridge_with_downstream() -> None:
    l5x = build_l5x(
        target_name="ModuleProto3EN2T", tags_xml="", extra_modules_xml=_EN2T_WITH_DOWNSTREAM_MODULE_XML
    )
    _write_unmodeled(
        l5x, "moduleproto_en2t_downstream_ia16",
        "1756-EN2T (\"local ethernet card\", off the 1756-L81E's own embedded Ethernet port) hosting a "
        "real 4-slot remote chassis (Bus Size=4, matching a real 1756-A4) with exactly ONE downstream "
        "module actually populated (slot 1: a 1756-IA16 AC input) -- genericized from real corpus "
        "modules, structurally verbatim. The downstream module uses RackConnection/InAliasTag (no "
        "separate connection data of its own -- its real I/O is aliased into the EN2T's own Slot[1] "
        "array entry, confirmed real Rockwell behavior, not guessed); only its ConfigTag is its own. "
        "The EN2T's own Slot array always spans the full 4-slot chassis size regardless of how many "
        "slots are actually populated (also confirmed real, not guessed) -- see OQ-MODULEIO.",
    )


def main() -> None:
    group_local_backplane()
    group_ethernet_off_cpu_port()
    group_ethernet_bridge_with_downstream()
    print("\nDone. 3 files -- deliberately no more, per James's own instruction not to spam a big "
          "IO batch before these validate the generator against real Studio 5000 import.")


if __name__ == "__main__":
    main()
