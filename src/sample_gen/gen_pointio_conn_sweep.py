"""POINT I/O connection-format cost sweep (OQ-POINTIOCONN).

Three real captures on 2026-09-11 -- one adapter and sixteen 1734-IB8/C
cards, in each of the three connection formats -- showed the model over-
predicting by 45% and 27% on two of them and under-predicting by 30% on
the third, and gave one clean single-variable result: a card's own
connection costs exactly 294 bytes more than no connection (Enhanced Data
minus Enhanced, 4,704 over 16 cards).

What those three points CANNOT separate is the adapter's own cost from the
per-card cost, because all three have sixteen cards. That needs a count
sweep, which is what this builds: N = 1, 2, 4, 8, 16 cards, everything
else held identical. Differencing consecutive points gives the per-card
cost as the slope and the adapter's own cost as the intercept, each
independent of the other.

ONLY the "Enhanced Data" format is generated here, and that restriction is
the point rather than an oversight. In that format the adapter's own
InputTag is just two status DINTs and every card carries its own
self-contained Connection, so changing the card count changes nothing but
the card count.

The other two formats cannot be synthesised honestly:

  - **Enhanced** -- the adapter's InputTag holds one StructureMember per
    card (Slot01..Slot16) inside a module-defined type whose name carries
    a Studio-5000-computed hash, "AB:1734_ERACK_649387C8:I:0". A different
    card count is a different type with a different hash, and that hash is
    not derivable from the L5X.
  - **Optimized** -- the adapter's type name encodes the slot count
    literally ("AB:1734_17SLOT:I:0") alongside a SINT[17] data array. The
    name is systematic rather than hashed, so it is guessable, but a
    guessed module profile that does not exist in the catalog fails the
    import, and a guessed one that does exist but differs in content would
    silently produce a wrong size -- the worse outcome of the two.

Both of those arms need real Studio 5000 exports at N = 1, 2, 4, 8 to
match this one. The module blocks below are verbatim from the real
2026-09-11 export, the same donor convention gen_fw_catalog_matrix.py
uses.
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.lint import lint_or_raise
from sample_gen.manifest import append_manifest_row, predicted_bytes
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "modules"

ADAPTER_NAME = "PioAdapter"

# Card counts. Powers of two plus the real 16-card point, so consecutive
# differences stay clean and the 16-card file reproduces the real capture.
CARD_COUNTS = (1, 2, 4, 8, 16)

_ADAPTER_XML = """<Module Name="{adapter}" CatalogNumber="1734-AENTR/C" Vendor="1" ProductType="12" ProductCode="196" Major="7" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false"
>
<EKey State="CompatibleModule"/>
<Ports>
<Port Id="1" Address="0" Type="PointIO" Upstream="false">
<Bus Size="{bus_size}"/>
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

_CARD_XML = """<Module CatalogNumber="1734-IB8/C" Vendor="1" ProductType="7" ProductCode="216" Major="3" Minor="1" ParentModule="{adapter}" ParentModPortId="1" Inhibited="false" MajorFault="false">
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


def _modules_xml(card_count: int) -> str:
    # A POINT I/O adapter's Bus Size counts itself plus its cards.
    parts = [_ADAPTER_XML.format(adapter=ADAPTER_NAME, bus_size=card_count + 1)]
    parts += [
        _CARD_XML.format(adapter=ADAPTER_NAME, slot=slot)
        for slot in range(1, card_count + 1)
    ]
    return "\n".join(parts)


def _write(l5x: str, name: str, description: str) -> None:
    out = OUT_ROOT / f"{name}.L5X"
    lint_or_raise(l5x, context=str(out))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(l5x, encoding="utf-8")
    append_manifest_row(name, description, "modules", out, predicted_bytes(l5x))
    print(f"Wrote {out}")


def main() -> None:
    for count in CARD_COUNTS:
        _write(
            build_l5x(
                target_name=f"PioEnhDataN{count:02d}",
                tags_xml="",
                extra_modules_xml=_modules_xml(count),
            ),
            f"pioconn_enhdata_n{count:02d}",
            f"1734-AENTR/C adapter with {count} 1734-IB8/C card(s), each on its "
            f"own Enhanced Data InputData connection. Differenced against the "
            f"other counts this separates the per-card cost from the adapter's "
            f"own -- the three real 16-card captures cannot, having the same "
            f"card count. OQ-POINTIOCONN.",
        )


if __name__ == "__main__":
    main()
