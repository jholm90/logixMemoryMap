"""OQ-MODREPEAT: what a module with no connection costs, by the catalogs real programs carry.

A module with no connection of its own and no measured rate is charged the flat
zero_connection_module rate, 2,344, a median fitted over noisy files. Every zero-connection
catalog measured in isolation costs far less: an ETHERNET-BRIDGE placeholder 320, a
1756-L8SP partner 528, a peer 5069-L306ERS2 560, a 5069-AENTR 625, a 5069-SERIAL/A 367.
The real safety-controller programs carry three catalogs still on the flat rate: inhibited
generic ETHERNET-MODULE placeholders with no connection (an HMI or NAT address kept in the
tree; two, four and one in three programs), a 1756-L75 peer controller, and a 1783-NATR.
One program carries seven, 16,408 bytes at the flat rate.

Each file is the realism plant plus the modules below, against realism_base_f25. The module
identity fields (catalog, product type and code, revision, the NATR's profile properties)
are the catalog's own, as Studio exports them; names, addresses and parents are this
project's:

  zcm_eth_n{01,02,04}   inhibited ETHERNET-MODULE, no connection, on the controller's Ethernet port
  zcm_natr_n{01,02}     1783-NATR on the controller's Ethernet port
  zcm_l75_n{01,02}      1756-L75 in the local chassis, slots 1 and 2

1756-L81E v35, realism floor.

Run: python -m sample_gen.gen_zero_conn_modules [--only REGEX]
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.realism import with_baseline
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "zcm"
CATEGORY = "modules"
OQ = "OQ-MODREPEAT"
FLAT = 2344


def ethernet_module_xml(name: str, ip: str) -> str:
    return (
        f'<Module Name="{name}" CatalogNumber="ETHERNET-MODULE" Vendor="1" ProductType="0" ProductCode="18" '
        f'Major="1" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="true" MajorFault="false">\n'
        f'<EKey State="Disabled"/>\n<Ports>\n'
        f'<Port Id="2" Address="{ip}" Type="Ethernet" Upstream="true"/>\n</Ports>\n'
        f'<Communications CommMethod="536870932">\n<Connections/>\n</Communications>\n</Module>'
    )


def natr_xml(name: str, ip: str) -> str:
    return (
        f'<Module Name="{name}" CatalogNumber="1783-NATR" Vendor="1" ProductType="12" ProductCode="309" '
        f'Major="1" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false" '
        f'SafetyEnabled="false">\n<EKey State="CompatibleModule"/>\n<Ports>\n'
        f'<Port Id="2" Address="{ip}" Type="Ethernet" Upstream="true"/>\n</Ports>\n'
        f'<ExtendedProperties>\n<public><PL>02<Version Name="1.3"/></PL><CatNum>1783-NATR</CatNum></public>\n'
        f'</ExtendedProperties>\n</Module>'
    )


def l75_xml(name: str, slot: int) -> str:
    return (
        f'<Module Name="{name}" CatalogNumber="1756-L75" Vendor="1" ProductType="14" ProductCode="96" '
        f'Major="28" Minor="1" ParentModule="Local" ParentModPortId="1" Inhibited="false" MajorFault="false">\n'
        f'<EKey State="Disabled"/>\n<Ports>\n'
        f'<Port Id="1" Address="{slot}" Type="ICP" Upstream="true"/>\n</Ports>\n</Module>'
    )


def plan() -> list[tuple[str, str, list[str]]]:
    files = []
    for n in (1, 2, 4):
        files.append((f"zcm_eth_n{n:02d}", f"{n} inhibited ETHERNET-MODULE placeholder(s) with no connection",
                      [ethernet_module_xml(f"ZcmEth{i:02d}", f"192.168.1.{210 + i}") for i in range(1, n + 1)]))
    for n in (1, 2):
        files.append((f"zcm_natr_n{n:02d}", f"{n} 1783-NATR",
                      [natr_xml(f"ZcmNat{i:02d}", f"192.168.1.{220 + i}") for i in range(1, n + 1)]))
    for n in (1, 2):
        files.append((f"zcm_l75_n{n:02d}", f"{n} 1756-L75 peer controller(s) in the local chassis",
                      [l75_xml(f"ZcmL75{i:02d}", i) for i in range(1, n + 1)]))
    return files


def make(sample_id: str, modules: list[str]) -> str:
    target = "".join(p.capitalize() for p in sample_id.split("_"))
    return build_l5x(target_name=target, **with_baseline(tags_xml="", extra_modules_xml="\n".join(modules)))


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", metavar="REGEX", help="build only the sample_ids this matches")
    args = ap.parse_args([] if argv is None else argv)
    for sample_id, what, modules in plan():
        if args.only and not re.search(args.only, sample_id):
            continue
        out = OUT_ROOT / f"{sample_id}.L5X"
        predicted = write_sample(make(sample_id, modules), out)
        n = len(modules)
        append_manifest_row(
            sample_id,
            f"{OQ}: the realism plant plus {what}; 1756-L81E v35, against realism_base_f25. Priced at the "
            f"flat zero-connection rate ({FLAT:,} a module): the reading is the engine's less the plant's "
            f"1,794 if that rate is right, {n * (FLAT - 320):,} less again if each costs what an "
            f"ETHERNET-BRIDGE placeholder does (320).",
            CATEGORY, out, predicted)
        print(f"Wrote {out.name} (predicted {predicted:,})")


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
