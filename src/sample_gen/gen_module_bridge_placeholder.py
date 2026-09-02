"""Ethernet-bridge PLACEHOLDER modules -- no Connections, no PLC logic tie,
just an IP-address bookkeeping entry (James, 2026-09-02, reviewing a real
production file's memory estimate: "the bridge with no modules i used as a
placeholder for IP addresses with no PLC logic connections. I suggest you
generate a sample test file for those").

Real shape confirmed against that same production file: a plain
CatalogNumber="ETHERNET-BRIDGE" module with a CIPBus Port (Bus Size="100")
and an Ethernet Port carrying only its own IP Address -- no <Communications>
element at all, so module_defined_bytes/stated_total_bytes are both 0.
report.py's build_report() already treats this as unmodeled (flagged via
SizeError, 2026-09-02 fix -- see that commit) rather than guessing an
overhead value; James's message confirms the real-world intent behind the
shape (a network-topology placeholder, not a real I/O device) but doesn't
by itself confirm what real Capacity cost, if any, it carries. This file
exists to get a real capture and settle that empirically instead of relying
on his description alone.

Two files: one placeholder alone (isolates its own real cost, if any) and
ten placeholders in one file (matches the real production file's actual
scale, and tests whether N placeholders cost N times as much or don't
compound at all -- the same open marginal-cost question OQ-MODULEIO already
flags for other module shapes).

Run: python -m sample_gen.gen_module_bridge_placeholder
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.manifest import append_manifest_row, write_sample_unmodeled
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "modules"
OUT_ROOT.mkdir(parents=True, exist_ok=True)


def _bridge_xml(name: str, ip_last_octet: int) -> str:
    return (
        f'<Module Name="{name}" CatalogNumber="ETHERNET-BRIDGE" Vendor="1" ProductType="0" '
        f'ProductCode="23" Major="1" Minor="1" ParentModule="Local" ParentModPortId="2" '
        f'Inhibited="false" MajorFault="false">\n'
        f'<EKey State="Disabled" />\n'
        f'<Ports>\n'
        f'<Port Id="1" Type="CIPBus" Upstream="false">\n<Bus Size="100" />\n</Port>\n'
        f'<Port Id="2" Address="192.168.200.{ip_last_octet}" Type="Ethernet" Upstream="true" />\n'
        f'</Ports>\n'
        f'</Module>\n'
    )


def main() -> None:
    single_xml = _bridge_xml("Bridge1", 1)
    l5x = build_l5x(target_name="BridgePlaceholderSingle", tags_xml="", extra_modules_xml=single_xml)
    out_name = "bridge_placeholder_single"
    write_sample_unmodeled(l5x, OUT_ROOT / f"{out_name}.L5X")
    append_manifest_row(
        sample_id=out_name,
        description=(
            "One ETHERNET-BRIDGE module, no Connections/Communications -- IP-address-only "
            "placeholder (no PLC logic connection). See gen_module_bridge_placeholder.py."
        ),
        category="modules",
        l5x_path=OUT_ROOT / f"{out_name}.L5X",
        bytes_predicted=0,
    )

    multi_xml = "\n".join(_bridge_xml(f"Bridge{i}", i) for i in range(1, 11))
    l5x = build_l5x(target_name="BridgePlaceholderTen", tags_xml="", extra_modules_xml=multi_xml)
    out_name = "bridge_placeholder_ten"
    write_sample_unmodeled(l5x, OUT_ROOT / f"{out_name}.L5X")
    append_manifest_row(
        sample_id=out_name,
        description=(
            "Ten ETHERNET-BRIDGE modules, same no-Connections IP-placeholder shape as "
            "bridge_placeholder_single, at the real-world scale (10) James's production file "
            "uses. See gen_module_bridge_placeholder.py."
        ),
        category="modules",
        l5x_path=OUT_ROOT / f"{out_name}.L5X",
        bytes_predicted=0,
    )
    print("Done. 2 files written.")


if __name__ == "__main__":
    main()
