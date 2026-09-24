"""OQ-BRIDGEPH: a bridge left in the I/O tree as an IP-address placeholder.

Programmers leave a bridge module in the tree with nothing beneath it -- often
inhibited -- purely so the plant's IP addresses are visible in the project. No
connection runs through it and no device sits under it, so it carries no data;
it should cost its own node overhead and nothing else. The engine used to
charge every such module the flat zero_connection_module rate (2,344, a median
over noisy real files) and raise a coverage notice.

The real shape, taken from a real 1756-L81E v35 export: an ETHERNET-BRIDGE on
the controller's Ethernet port, Inhibited="true", a CIPBus port (Bus Size 100)
and an Ethernet port carrying only its IP address, no <Communications> at all.
A gateway module (a 1756-EN2T fronting another network) is NOT this case and is
not measured here.

What exists already: bridge_placeholder_single / _ten (NOT inhibited,
near-empty controller) read 320 per bridge. This batch measures the real shape
on the realism floor:

  bridgeph_n00                     control: the realism baseline alone
  bridgeph_ebr_inh_n{01,02,04,08}  ETHERNET-BRIDGE, inhibited, 6-char names
  bridgeph_ebr_act_n04             the same four, NOT inhibited
  bridgeph_ebr_long_n04            the same four inhibited, 16-char names

Each file differences against bridgeph_n00 and against its own other counts:
flat per-module marginals across the counts confirm a per-module rate; _act vs
_inh says whether inhibiting matters; _long vs _inh_n04 is the name.

Run: python -m sample_gen.gen_bridge_placeholder
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.realism import with_baseline
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "bridgeph"
CATEGORY = "bridge_placeholder"


def ethernet_bridge_xml(name: str, ip: str, inhibited: bool) -> str:
    return (
        f'<Module Name="{name}" CatalogNumber="ETHERNET-BRIDGE" Vendor="1" ProductType="0" '
        f'ProductCode="23" Major="1" Minor="1" ParentModule="Local" ParentModPortId="2" '
        f'Inhibited="{"true" if inhibited else "false"}" MajorFault="false">\n'
        f'<EKey State="Disabled"/>\n<Ports>\n'
        f'<Port Id="1" Type="CIPBus" Upstream="false">\n<Bus Size="100"/>\n</Port>\n'
        f'<Port Id="2" Address="{ip}" Type="Ethernet" Upstream="true"/>\n'
        f'</Ports>\n</Module>'
    )


def _write(sample_id: str, modules: list[str], description: str) -> None:
    out = OUT_ROOT / f"{sample_id}.L5X"
    target = "".join(part.capitalize() for part in sample_id.split("_"))
    l5x = build_l5x(target_name=target, **with_baseline(extra_modules_xml="\n".join(modules)))
    predicted = write_sample(l5x, out)
    append_manifest_row(sample_id, description + " OQ-BRIDGEPH.", CATEGORY, out, predicted)
    print(f"Wrote {out} (predicted {predicted:,})")


def main() -> None:
    _write("bridgeph_n00", [],
           "Control: the realism baseline alone, no bridge. Every other bridgeph_* file "
           "differences against this one.")
    for n in (1, 2, 4, 8):
        _write(f"bridgeph_ebr_inh_n{n:02d}",
               [ethernet_bridge_xml(f"BrPh{i:02d}", f"192.168.1.{200 + i}", True)
                for i in range(1, n + 1)],
               f"{n} ETHERNET-BRIDGE placeholder(s), Inhibited=\"true\", nothing beneath, no "
               f"Communications, 6-character names -- the real shape. Per-bridge cost is "
               f"(this - bridgeph_n00) / {n}; flat across n confirms a per-module rate.")
    _write("bridgeph_ebr_act_n04",
           [ethernet_bridge_xml(f"BrPh{i:02d}", f"192.168.1.{200 + i}", False) for i in range(1, 5)],
           "4 ETHERNET-BRIDGE placeholders exactly as bridgeph_ebr_inh_n04 but NOT inhibited: "
           "differenced against it, isolates what inhibiting costs.")
    _write("bridgeph_ebr_long_n04",
           [ethernet_bridge_xml(f"BridgePlaceho{i:03d}", f"192.168.1.{200 + i}", True)
            for i in range(1, 5)],
           "4 inhibited ETHERNET-BRIDGE placeholders exactly as bridgeph_ebr_inh_n04 but with "
           "16-character names: differenced against it, the name-length term "
           "(OQ-MODULENAMELEN law: roundup8(L+3)+roundup8(L+5) per module).")


if __name__ == "__main__":
    main()
