"""CIP-MODULE (generic CIP device) declared-I/O-size scaling (James,
2026-09-02: "sure you can learn some more stuff about the CIP-MODULE
generate up some more tests for those too" -- direct follow-up to his own
real TitusvilleTrimmer file, whose 3 real "CIP-MODULE" instances (all
496/496-byte connections) flagged this project's flat ~1,672-byte
module_overhead default as a real risk: `ETHERNET-MODULE`/`ETHERNET-
PANELVIEW` are already documented as "overhead scales with declared I/O
size, not flat at all" -- this tests whether CIP-MODULE (a different
generic-catalog placeholder, used for devices with no native Studio 5000
AOP) shows the same real pattern.

Real shape extracted directly from that production file's own `IO_Optm`
module (structurally verbatim, only the ParentModule changed from a named
bridge to Local's own Ethernet port for isolation -- see the docstring on
`_bridge_xml` for why that substitution is safe): CatalogNumber="CIP-MODULE",
ParentModPortId="1" Type="CIPBus" (riding a parent bridge's virtual CIP
bus, not a physical port of its own), one "Standard" Connection with
matched Input/OutputSize, and a real, size-named Decorated shape
(`AB:1756_MODULE_DINT_{n}Bytes:I:0`/`:O:0`, a DINT-typed generic array
whose Dimensions = size/4 -- confirmed at n=496 in the real file, 124
elements = 496/4 exactly, zero packing ambiguity, no different from any
other DINT array). Every element's real value is 0 in the source file, so
synthesizing more zero elements at other sizes is not fabricating data,
just extending the exact same real, already-confirmed pattern to sizes
this project has never captured.

Size sweep: 64/128/256/496 (real, anchoring point)/1024/2048 bytes, one
instance per file, isolating I/O size as the only variable. Plus one
3-instance file (matching Titusville's own real usage of 3 same-catalog
CIP-MODULE nodes) at the confirmed 496-byte size, to test whether multiple
same-size instances also show the already-documented non-additive
multi-module marginal cost.

Run: python -m sample_gen.gen_module_cip_generic_scale
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from l5x_memory_analyzer.sizing.constants import load_memory_model
from l5x_memory_analyzer.sizing.report import build_report

from sample_gen.manifest import append_manifest_row, write_sample_unmodeled
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "modules"
_MODEL = load_memory_model()

# Real shape, gen_module_bridge_placeholder.py's own bridge template (same
# ETHERNET-BRIDGE catalog, same CIPBus host port) -- reused here rather than
# re-deriving, since it's already confirmed lint-clean and structurally
# real.
_BRIDGE_XML = (
    '<Module Name="{name}" CatalogNumber="ETHERNET-BRIDGE" Vendor="1" ProductType="0" '
    'ProductCode="23" Major="1" Minor="1" ParentModule="Local" ParentModPortId="2" '
    'Inhibited="false" MajorFault="false">\n'
    '<EKey State="Disabled" />\n'
    '<Ports>\n'
    '<Port Id="1" Type="CIPBus" Upstream="false">\n<Bus Size="100" />\n</Port>\n'
    '<Port Id="2" Address="192.168.201.{ip} " Type="Ethernet" Upstream="true" />\n'
    '</Ports>\n'
    '</Module>\n'
)


def _bridge_xml(name: str, ip_last_octet: int) -> str:
    return _BRIDGE_XML.format(name=name, ip=ip_last_octet).replace(" \"", "\"")


def _dint_array_xml(size_bytes: int) -> str:
    assert size_bytes % 4 == 0, "CIP-MODULE generic DINT data must be a whole number of DINTs"
    n = size_bytes // 4
    elements = "".join(f'<Element Index="[{i}]" Value="0" />' for i in range(n))
    return elements


def _cip_module_xml(name: str, parent: str, size_bytes: int, cip_address: int = 1) -> str:
    data = _dint_array_xml(size_bytes)
    return (
        f'<Module Name="{name}" CatalogNumber="CIP-MODULE" Vendor="1" ProductType="0" ProductCode="24" '
        f'Major="1" Minor="1" ParentModule="{parent}" ParentModPortId="1" Inhibited="false" MajorFault="false">\n'
        f'<EKey State="Disabled" />\n'
        f'<Ports>\n<Port Id="1" Address="{cip_address}" Type="CIPBus" Upstream="true" />\n</Ports>\n'
        f'<Communications CommMethod="536870913" PrimCxnInputSize="{size_bytes}" PrimCxnOutputSize="{size_bytes}">\n'
        f'<ConfigTag ConfigSize="0" ExternalAccess="Read/Write">\n'
        f'<Data Format="L5K"><![CDATA[[4,103,[{",".join(["0"] * 400)}]]]]></Data>\n'
        f'<Data Format="Decorated"><Structure DataType="AB:1756_MODULE:C:0">'
        f'<ArrayMember Name="Data" DataType="SINT" Dimensions="400" Radix="Hex">'
        + "".join(f'<Element Index="[{i}]" Value="16#00" />' for i in range(400))
        + '</ArrayMember></Structure></Data>\n'
        f'</ConfigTag>\n'
        f'<Connections>\n'
        f'<Connection Name="Standard" RPI="10000" Type="Output" InputCxnPoint="102" OutputCxnPoint="101" '
        f'OutputSize="{size_bytes}" InputSize="{size_bytes}" EventID="0" '
        f'ProgrammaticallySendEventTrigger="false" Unicast="true">\n'
        f'<InputTag ExternalAccess="Read/Write">\n<Data Format="Decorated">'
        f'<Structure DataType="AB:1756_MODULE_DINT_{size_bytes}Bytes:I:0">'
        f'<ArrayMember Name="Data" DataType="DINT" Dimensions="{size_bytes // 4}" Radix="Decimal">{data}</ArrayMember>'
        f'</Structure></Data>\n</InputTag>\n'
        f'<OutputTag ExternalAccess="Read/Write">\n<Data Format="Decorated">'
        f'<Structure DataType="AB:1756_MODULE_DINT_{size_bytes}Bytes:O:0">'
        f'<ArrayMember Name="Data" DataType="DINT" Dimensions="{size_bytes // 4}" Radix="Decimal">{data}</ArrayMember>'
        f'</Structure></Data>\n</OutputTag>\n'
        f'</Connection>\n</Connections>\n</Communications>\n</Module>'
    )


def _floor_bytes(l5x_text: str) -> int:
    root = ET.fromstring(l5x_text)
    entries, _errors = build_report(root, _MODEL)
    return sum(e.bytes for e in entries)


def _write(out_name: str, modules_xml: str, description: str) -> None:
    l5x = build_l5x(target_name=f"CipGeneric{out_name}", tags_xml="", extra_modules_xml=modules_xml)
    out_path = OUT_ROOT / f"cipmodule_scale_{out_name}.L5X"
    write_sample_unmodeled(l5x, out_path)
    total = _floor_bytes(l5x)
    append_manifest_row(f"cipmodule_scale_{out_name}", f"{description} Real floor total {total}.",
                         "modules", out_path, total)
    print(f"Wrote {out_path} (floor {total} bytes)")


# 1024 and 2048 REMOVED 2026-09-04 -- real Studio 5000 error, both files:
# "Failed to set the 'PrimCxnInputSize' property (Value too large.)". A
# generic Ethernet/CIP connection tops out at 500 bytes, confirmed two
# independent ways: the largest PrimCxnInputSize anywhere in the real corpus
# is exactly 500 (next values down 496, 450, 448), and 496 is the largest
# size in this sweep that ever converted. They were never valid sizes, so
# there is nothing to regenerate -- the two files are deleted and
# skip-listed. 496 remains the anchoring real-file size.
_SIZES = [64, 128, 256, 496]


def main() -> None:
    for size in _SIZES:
        bridge = _bridge_xml("Bridge1", 1)
        cip = _cip_module_xml("CipDev1", "Bridge1", size)
        _write(
            f"{size:04d}b",
            bridge + "\n" + cip,
            f"CIP-MODULE (generic CIP device, real shape from a production file's own instance) with "
            f"declared Connection I/O size {size} bytes (both directions), riding a real ETHERNET-BRIDGE "
            f"host's CIPBus. Isolates whether module_overhead scales with declared I/O size for this "
            f"catalog the way it already does for ETHERNET-MODULE/ETHERNET-PANELVIEW.",
        )

    bridge = _bridge_xml("Bridge1", 1)
    triple = "\n".join(_cip_module_xml(f"CipDev{i}", "Bridge1", 496, cip_address=i) for i in range(1, 4))
    _write(
        "0496b_x3",
        bridge + "\n" + triple,
        "Three real CIP-MODULE instances at the confirmed real 496-byte size (matching "
        "TitusvilleTrimmer's own real usage of 3 same-catalog CIP-MODULE nodes on one bridge) -- "
        "tests whether the multi-module non-additive marginal cost already documented for other "
        "catalogs (OQ-MODULEIO) also applies here.",
    )
    print(f"\nDone. {len(_SIZES) + 1} files.")


if __name__ == "__main__":
    main()
