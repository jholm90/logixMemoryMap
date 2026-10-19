"""OQ-SAFETYPARTITION, round 5: safety I/O -- what a CIP Safety I/O module costs in each
partition. Every real safety program carries 2 to 25 safety modules and the engine prices
none of them in the safety partition; the blind readings of 2026-10-19 put that gap at 18
to 66% of the safety figure (TASKS 0z).

Module blocks are the repository's own module-sweep blocks (gen_module_sweep,
gen_module_sweep_variants), each completed with the <ExtendedProperties> block every
compiled export of the catalog carries: with it, each block's structure is identical to
the compiled shape of its catalog (the 1734-IB8S/B two-connection block to 19 real
instances, its one-connection block to 6). The ConfigID in it is the catalog profile's
identifier, like ProductCode. Nothing else is taken from a real export.

  safe_io_ib8s_<n>              n 1734-IB8S/B in a further 1734-AENTR/C rack on the L81ES plant
                                (SafetyInput + SafetyOutput test outputs), against safe_n00
  safe_io_ib8s1c_4              4 1734-IB8S/B with the SafetyInput connection only
  safe_io_ob8s_<n>              n 1734-OB8S/B in it
  safe_io_mix_4_4               4 IB8S and 4 OB8S in one rack (additivity)
  safe_io_racks_2x2             2 IB8S in this rack and 2 in an eighth (per-rack cost)
  safe_io_5069_<ib8s|obv8s>_<n> n 5069-IB8S/A or 5069-OBV8S/A on a 5069-L330ERMS2's own bus,
                                against round 4's captured safe_base_5069l330_v35

A 1734 rack carries its own safety network number, shared by its safety cards and
independent of the controller's; a module on the controller's own bus carries that bus
port's number (both as compiled exports have them).

Not here, each for want of a block proven or compiled in this repository: the Kinetix 2198
safety drive, 1756-IB16S / OBV8S, and the PowerFlex 527 (every real one carries an axis
and a motion group).

Run: python -m sample_gen.gen_safety_io [--only REGEX]
"""

from __future__ import annotations

import argparse
import json
import re

from sample_gen import gen_module_sweep as MS
from sample_gen import gen_module_sweep_variants as MV
from sample_gen import gen_safety_partition as G
from sample_gen import gen_safety_round2 as R
from sample_gen import gen_safety_round4 as R4
from sample_gen.manifest import REPO_ROOT, append_manifest_row, write_sample
from sample_gen.realism import _ADAPTER_BLOCK, _resize_slot_structure

OQ = "OQ-SAFETYPARTITION"

# (catalog, major, connection count) -> the ExtendedProperties every compiled export of
# that shape carries: the profile's ConfigID, then CatNum.
EXTENDED = {
    ("1734-IB8S/B", "2", 2): ("102", "1734-IB8S"),
    ("1734-IB8S/B", "2", 1): ("108", "1734-IB8S"),
    ("1734-OB8S/B", "2", 2): ("205", "1734-OB8S"),
    ("5069-IB8S/A", "2", 1): ("16777344", "5069-IB8S"),
    ("5069-OBV8S/A", "3", 2): ("16777452", "5069-OBV8S"),
}

# Each 1734 rack's own safety network number: the ones the repository's blocks carry.
RACK_SNN = ("16#0000_4cd9_030d_7a8a", "16#0000_447d_042b_b261")


def _module(xml: str, catalog: str) -> str:
    for block in re.findall(r"<Module\b.*?</Module>", xml, re.S):
        if f'CatalogNumber="{catalog}"' in block:
            return block
    raise KeyError(catalog)


def _variant(catalog: str, label: str) -> str:
    for lab, xml, _src, _n in MV._MODULE_VARIANTS[catalog]:
        if lab == label:
            return _module(xml, catalog)
    raise KeyError((catalog, label))


TEMPLATES = {
    "ib8s": _variant("1734-IB8S/B", "2conn"),
    "ib8s1c": _variant("1734-IB8S/B", "1conn"),
    "ob8s": _module(MS._MODULE_CHAINS["1734-OB8S/B"][0], "1734-OB8S/B"),
    "5069ib8s": _module(MS._MODULE_CHAINS["5069-IB8S/A"][0], "5069-IB8S/A"),
    "5069obv8s": _module(MS._MODULE_CHAINS["5069-OBV8S/A"][0], "5069-OBV8S/A"),
}


def with_extended(block: str) -> str:
    """The block with its catalog's ExtendedProperties, as compiled exports carry it."""
    catalog = re.search(r'CatalogNumber="([^"]+)"', block).group(1)
    major = re.search(r'\bMajor="(\d+)"', block).group(1)
    conns = len(re.findall(r"<Connection\b", block))
    config_id, catnum = EXTENDED[(catalog, major, conns)]
    ext = (f"<ExtendedProperties>\n<public><ConfigID>{config_id}</ConfigID><CatNum>{catnum}</CatNum>"
           f"</public>\n</ExtendedProperties>\n</Module>")
    assert "<ExtendedProperties>" not in block
    return block[: block.rindex("</Module>")] + ext


def place(template: str, name: str | None, parent: str, parent_port: str, slot: int, snn: str) -> str:
    """One safety module: its name (None for a card on a 5069 controller's own bus, which
    compiled exports write without one), parent, slot and safety network number."""
    head, rest = template.split(">", 1)
    head = re.sub(r'\s+Name="[^"]*"', "", head, count=1)
    if name is not None:
        head = head.replace("<Module ", f'<Module Name="{name}" ', 1)
    head = re.sub(r'ParentModule="[^"]*"', f'ParentModule="{parent}"', head, count=1)
    head = re.sub(r'ParentModPortId="[^"]*"', f'ParentModPortId="{parent_port}"', head, count=1)
    head = re.sub(r'SafetyNetwork="[^"]*"', f'SafetyNetwork="{snn}"', head, count=1)
    rest = re.sub(r'(<Port Id="1" Address=")\d+(" Type="(?:PointIO|5069)" Upstream="true")', rf"\g<1>{slot}\g<2>",
                  rest, count=1)
    return with_extended(head + ">" + rest)


def adapter(name: str, ip: str, cards: int) -> str:
    """The plant's own 1734-AENTR/C block, its backplane sized to its cards plus itself
    (lint chassis_size_mismatch; the plant's racks are 8 cards, size 9)."""
    size = cards + 1
    block = re.sub(r'Name="[^"]+"', f'Name="{name}"', _ADAPTER_BLOCK, count=1)
    block = re.sub(r'<Bus Size="\d+" ?/>', f'<Bus Size="{size}" />', block, count=1)
    block = re.sub(r'Address="192\.168\.[0-9.]+"', f'Address="{ip}"', block, count=1)
    return _resize_slot_structure(block, size)


def rack(name: str, ip: str, snn: str, cards: list[str]) -> list[str]:
    """The adapter and its safety cards in slots 1, 2, ..."""
    return [adapter(name, ip, len(cards))] + [
        place(TEMPLATES[kind], f"{name}_S{slot}", name, "1", slot, snn) for slot, kind in enumerate(cards, start=1)]


def with_modules(l5x: str, modules: list[str]) -> str:
    return l5x.replace("</Modules>", "\n".join(modules) + "\n</Modules>", 1) if modules else l5x


def local_snn(l5x: str, port: str) -> str:
    local = re.search(r'<Module Name="Local".*?</Module>', l5x, re.S).group(0)
    return re.search(rf'<Port Id="{port}"[^>]*SafetyNetwork="([^"]+)"', local).group(1)


# --- the roster --------------------------------------------------------------------------

def plan() -> list[tuple[str, str, dict]]:
    files: list[tuple[str, str, dict]] = []
    for n in (1, 2, 4, 8):
        files.append((f"safe_io_ib8s_{n}", f"{n} 1734-IB8S/B (SafetyInput and SafetyOutput test outputs) in that rack",
                      {"racks": [["ib8s"] * n]}))
    files.append(("safe_io_ib8s1c_4", "4 1734-IB8S/B with the SafetyInput connection only",
                  {"racks": [["ib8s1c"] * 4]}))
    for n in (1, 2, 4, 8):
        files.append((f"safe_io_ob8s_{n}", f"{n} 1734-OB8S/B in that rack", {"racks": [["ob8s"] * n]}))
    files.append(("safe_io_mix_4_4", "4 1734-IB8S/B and 4 1734-OB8S/B in one rack",
                  {"racks": [["ib8s"] * 4 + ["ob8s"] * 4]}))
    files.append(("safe_io_racks_2x2", "2 1734-IB8S/B in that rack and 2 in a further rack with its own safety network",
                  {"racks": [["ib8s"] * 2, ["ib8s"] * 2]}))
    for kind, catalog in (("ib8s", "5069-IB8S/A"), ("obv8s", "5069-OBV8S/A")):
        for n in (1, 2, 4):
            files.append((f"safe_io_5069_{kind}_{n}", f"{n} {catalog} on a 5069-L330ERMS2 v35's own bus, against "
                          f"safe_base_5069l330_v35", {"local": [f"5069{kind}"] * n}))
    return [(sid, f"{OQ}: {desc}", kw) for sid, desc, kw in files]


def make(sample_id: str, kw: dict) -> str:
    if "local" in kw:
        name = "SafeBase" + "".join(w.capitalize() for w in sample_id.split("_")[1:])
        l5x = R4.build_base(name, "5069-L330ERMS2", "35", "35.05", content=False)
        snn = local_snn(l5x, "1")
        return with_modules(l5x, [place(TEMPLATES[kind], None, "Local", "1", slot, snn)
                                  for slot, kind in enumerate(kw["local"], start=1)])
    l5x = R.build(sample_id)
    modules: list[str] = []
    for i, cards in enumerate(kw["racks"]):
        modules += rack(f"SRACK_{i + 1}", f"192.168.1.{200 + i}", RACK_SNN[i], cards)
    return with_modules(l5x, modules)


# --- local-only families -----------------------------------------------------------------
# The Kinetix integrated-safety drive, 1756 safety I/O and the BNI00HN have no block in this
# repository. Their templates are taken from compiled real exports (owner's permission,
# 2026-10-19), with every name, address, safety network number, description and comment
# replaced, and live in the git-ignored samples/local/ with the files built from them:
# customer-derived content never enters the repository, and the files move over chat.

LOCAL_BLOCKS = REPO_ROOT / "samples" / "local" / "safety_io_blocks.json"
LOCAL_OUT = REPO_ROOT / "samples" / "local" / "safety_io"


def local_block(key: str, name: str, parent: str, parent_port: str, address: str, snn: str) -> str:
    out = json.loads(LOCAL_BLOCKS.read_text(encoding="utf-8"))[key]
    for token, value in (("{NAME}", name), ("{PARENT}", parent), ("{PARENT_PORT}", parent_port),
                         ("{ADDRESS}", address), ("{SNN}", snn)):
        assert out.count(token) == 1, (key, token)
        out = out.replace(token, value)
    return out


def local_plan() -> list[tuple[str, str, dict]]:
    files: list[tuple[str, str, dict]] = []
    for key, catalog in (("1756ib16s", "1756-IB16S/A"), ("1756obv8s", "1756-OBV8S/A")):
        for n in (1, 2, 4):
            files.append((f"safe_iol_{key}_{n}", f"{n} {catalog} in the 1756-L81ES local chassis, against safe_n00",
                          {"chassis": [key] * n}))
    for n in (1, 2, 4):
        files.append((f"safe_iol_kinstd_{n}", f"a 2198-P208 supply and {n} 2198-D032-ERS3 without safety on the "
                      "L81ES plant: the control for safe_iol_kinsafe", {"drives": n, "safety": False}))
        files.append((f"safe_iol_kinsafe_{n}", f"the same {n} drives with integrated safety (CIP_Motion_Device_Safety2)",
                      {"drives": n, "safety": True}))
    for n in (1, 2, 4):
        files.append((f"safe_iol_bni00hn_{n}", f"{n} Balluff BNI00HN safety blocks on a 5069-L330ERMS2's Ethernet port "
                      "4, against safe_base_5069l330_v35", {"bni": n}))
    return [(sid, f"{OQ}: {desc}", kw) for sid, desc, kw in files]


def local_make(sample_id: str, kw: dict) -> str:
    from sample_gen.gen_module_motion import _drive_module_xml, bus_supply_with_converter
    if "bni" in kw:
        name = "SafeBase" + "".join(w.capitalize() for w in sample_id.split("_")[1:])
        l5x = R4.build_base(name, "5069-L330ERMS2", "35", "35.05", content=False)
        snn = local_snn(l5x, "4")
        return with_modules(l5x, [local_block("bni00hn", f"SafeBni{i + 1}", "Local", "4", f"192.168.1.{60 + i}", snn)
                                  for i in range(kw["bni"])])
    l5x = R.build(sample_id)
    if "chassis" in kw:
        snn = local_snn(l5x, "1")
        return with_modules(l5x, [local_block(key, f"SafeCard{slot}", "Local", "1", str(slot), snn)
                                  for slot, key in enumerate(kw["chassis"], start=1)])
    snn = local_snn(l5x, "2")
    supply, _converter = bus_supply_with_converter()
    drives = [local_block("2198d032s", f"Drv{i + 1}", "Local", "2", f"192.168.1.{20 + i}", snn) if kw["safety"]
              else _drive_module_xml(f"Drv{i + 1}", "2198-D032-ERS3", "false", address=f"192.168.1.{20 + i}")
              for i in range(kw["drives"])]
    return with_modules(l5x, [supply] + drives)


def _make_local(job: tuple[str, dict]) -> int:
    sample_id, kw = job
    return write_sample(local_make(sample_id, kw), LOCAL_OUT / f"{sample_id}.L5X")


def _make(job: tuple[str, dict]) -> int:
    sample_id, kw = job
    return write_sample(make(sample_id, kw), G.OUT_ROOT / f"{sample_id}.L5X")


def main() -> None:
    from sample_gen.progress import run
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", metavar="REGEX", help="build only the sample_ids this matches")
    ap.add_argument("--local", action="store_true",
                    help="build the local-only families into samples/local/safety_io/ (needs the templates there)")
    args = ap.parse_args()
    roster, build, out = (local_plan(), _make_local, LOCAL_OUT) if args.local else (plan(), _make, G.OUT_ROOT)
    jobs = [(sid, desc, kw) for sid, desc, kw in roster if not args.only or re.search(args.only, sid)]
    predicted = run(((sid, (sid, kw)) for sid, _, kw in jobs), build, label="safety-io")
    for sample_id, description, _ in jobs:
        append_manifest_row(sample_id, description, G.CATEGORY, out / f"{sample_id}.L5X", predicted[sample_id])


if __name__ == "__main__":
    main()
