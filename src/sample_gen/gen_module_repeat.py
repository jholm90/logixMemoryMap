"""OQ-MODREPEAT: what a second and later module costs, for every class of module.

Round 1 -- five Ethernet catalogs measured only once (`modulesweep_*`) and carried by the
real safety-controller programs repeated: 6 to 7 1732E-IB16M12R/A, 3 to 4
1732E-OB16M12R/A and 3 EX260-SEN1/A in each of RS-06 and RS-09, 4 EX260-SEN3/A in RS-10,
4 PowerFlex 525-EENET in each of RS-02, RS-03 and RS-17. RS-06 and RS-09, the same
program with two more IB16M12R, differ by about 700 a copy where the engine charged 1,432.
Each catalog at 1, 2 and 4 copies (`modrep_<catalog>_n0N`).

Round 2 -- the law the engine now applies to every module (memory_model.yaml
module_type_sharing): a vendor-prefixed module-defined type ("AB:1756_DI:I:0") is defined
once per project, so a later module carrying it pays its overhead less that definition; a
type without a vendor prefix ("CHANNEL_DO:O:0") is the module's own and is paid again,
76 more for each copy; an unseen catalog is a base plus its new types. Fitted on 1756,
1734, 1794 and 5069 sweeps built without the realism floor. These files test it on the
floor, one class of module at a time, each a blind prediction:

  * 1756 chassis analog, 1756-IF8/A and 1756-OF8/B at 1 / 2 / 4: the law has a further
    OF8/B costing 554 of its 5,066 first-copy overhead.
  * 843E-MIPxxBAx/A encoders at 1 / 2 / 4: two prefixed and two prefix-less types on an
    Ethernet device, the module-scoped rule outside a 5069 rack.
  * PowerFlex 755-EENET drives at 1 / 2 / 4.
  * POINT I/O on its own connection: 1 / 2 / 4 1734-IE2C/C in a sixth 1734-AENTR/C rack.
  * 5069 Compact I/O behind a 5069-AENTR: 5069-OB16/B, one rack with one card, one rack
    with four, four racks with one each -- the last pair separates a per-card cost inside
    a rack from a per-copy cost of the card.
  * Generic ETHERNET-MODULE, one at In 10 / Out 4, a second with the same input and a
    different output (shares two of its three types), a second with neither (shares the
    configuration type only).

Every file on the realism floor, 1756-L81E v35, against `realism_base_f25`, the plant
alone. Module blocks are proven clean captures (`modulesweep_*`, `rack_5069_*`,
`genem_*`, the realism floor's own rack), placed with gen_assumed_closeout._place_copies
(each copy its own name and address).

Run: python -m sample_gen.gen_module_repeat [--only REGEX]
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Callable

from sample_gen.gen_assumed_closeout import _place_copies, _slug
from sample_gen.gen_composite_realistic import _resize_slot_structure
from sample_gen.gen_generic_ethernet_module import _module_xml as generic_module_xml
from sample_gen.gen_module_5069_aent_rack import _5069_AENT_CHAIN_BLOCKS
from sample_gen.gen_module_sweep import _MODULE_CHAINS
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.realism import with_baseline
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "modrep"
CATEGORY = "modules"
OQ = "OQ-MODREPEAT"
CATALOGS = ("1732E-IB16M12R/A", "1732E-OB16M12R/A", "EX260-SEN1/A", "EX260-SEN3/A", "PowerFlex 525-EENET")
# Round 2: one module block each, placed whole.
SINGLE_BLOCKS = ("1756-IF8/A", "1756-OF8/B", "843E-MIPxxBAx/A", "PowerFlex 755-EENET")
COUNTS = (1, 2, 4)


def _modules(catalog: str) -> list[str]:
    xml, _source, _n = _MODULE_CHAINS[catalog]
    return re.findall(r"<Module\b.*?</Module>", xml, re.DOTALL)


def copies_xml(catalog: str, count: int) -> str:
    xml, _source, chain_len = _MODULE_CHAINS[catalog]
    assert chain_len == 1, catalog
    return _place_copies(xml, count)


def point_rack_xml(count: int, name: str = "PtRack6", ip: str = "192.168.1.160") -> str:
    """A 1734-AENTR/C rack, the realism floor's own adapter block sized to its cards, holding
    `count` 1734-IE2C/C (each on its own connection) in slots 1..count."""
    from sample_gen.realism import _ADAPTER_BLOCK
    adapter = re.sub(r'Name="[^"]+"', f'Name="{name}"', _ADAPTER_BLOCK, count=1)
    adapter = re.sub(r'<Bus Size="\d+" ?/>', f'<Bus Size="{count + 1}" />', adapter, count=1)
    adapter = re.sub(r'Address="192\.168\.[0-9.]+"', f'Address="{ip}"', adapter, count=1)
    adapter = _resize_slot_structure(adapter, count + 1)
    card = _modules("1734-IE2C/C")[1]
    parts = [adapter]
    for slot in range(1, count + 1):
        c = re.sub(r'Name="[^"]+"', f'Name="{name}_IE2C{slot}"', card, count=1)
        c = re.sub(r'ParentModule="[^"]+"', f'ParentModule="{name}"', c, count=1)
        c = re.sub(r'(<Port Id="1" Address=")\d+(" Type="PointIO" Upstream="true")', rf"\g<1>{slot}\g<2>", c, count=1)
        parts.append(c)
    return "\n".join(parts)


def racks_5069_xml(racks: int, cards: int, catalog: str = "5069-OB16/B") -> str:
    """`racks` 5069-AENTR adapters (the rack_5069_* block, Bus Size 32 as captured), each
    with `cards` copies of `catalog` in slots 1..cards."""
    parts = []
    for r in range(1, racks + 1):
        adapter = _5069_AENT_CHAIN_BLOCKS["5069-AENTR"]
        adapter = adapter.replace('Name="AENT"', f'Name="AENT{r}"', 1)
        adapter = adapter.replace('Address="192.168.1.1"', f'Address="192.168.1.{170 + r}"', 1)
        parts.append(adapter)
        for slot in range(1, cards + 1):
            card = _5069_AENT_CHAIN_BLOCKS[catalog].replace('ParentModule="AENT"', f'ParentModule="AENT{r}"', 1)
            card = re.sub(r'(<Port Id="1" Address=")\d+("\s*Type="5069"\s*Upstream="true")',
                          rf"\g<1>{slot}\g<2>", card, count=1)
            parts.append(card)
    return "\n".join(parts)


def generics_xml(shapes: list[tuple[int, int]]) -> str:
    return "\n".join(generic_module_xml(f"GenEm{i + 1}", f"192.168.1.{180 + i}", inp, out)
                     for i, (inp, out) in enumerate(shapes))


def plan() -> list[tuple[str, str, Callable[[], str]]]:
    files: list[tuple[str, str, Callable[[], str]]] = []
    for catalog in CATALOGS + SINGLE_BLOCKS:
        for n in COUNTS:
            files.append((f"modrep_{_slug(catalog)}_n{n:02d}",
                          f"{n} {catalog} (the repository's module-sweep block, each copy its own name and address)",
                          lambda c=catalog, k=n: copies_xml(c, k)))
    for n in COUNTS:
        files.append((f"modrep_1734_ie2c_c_rack_n{n:02d}",
                      f"a sixth 1734-AENTR/C rack (the realism floor's adapter, Bus Size {n + 1}) holding {n} "
                      "1734-IE2C/C, each on its own connection",
                      lambda k=n: point_rack_xml(k)))
    for racks, cards in ((1, 1), (1, 4), (4, 1)):
        files.append((f"modrep_5069_ob16_b_r{racks}x{cards}",
                      f"{racks} 5069-AENTR rack(s) (the rack_5069_* block, Bus Size 32) each holding {cards} "
                      "5069-OB16/B",
                      lambda r=racks, k=cards: racks_5069_xml(r, k)))
    for key, shapes, what in (("n01", [(10, 4)], "one ETHERNET-MODULE at In 10 / Out 4"),
                              ("same_in", [(10, 4), (10, 8)], "two ETHERNET-MODULE, In 10 / Out 4 and In 10 / Out 8"),
                              ("diff", [(10, 4), (32, 8)], "two ETHERNET-MODULE, In 10 / Out 4 and In 32 / Out 8")):
        files.append((f"modrep_genem_{key}", f"{what} (the genem_* block)", lambda s=shapes: generics_xml(s)))
    return files


def target_name(sample_id: str) -> str:
    """The controller name: round 1's scheme for a plain copy file (unchanged, so those files
    stay as built), the sample's own words for the rest."""
    m = re.fullmatch(r"modrep_(.+)_n0(\d)", sample_id)
    catalog = next((c for c in CATALOGS + SINGLE_BLOCKS if m and _slug(c) == m.group(1)), None)
    if catalog:
        return ("ModRep" + "".join(ch for ch in catalog if ch.isalnum())[:16] + f"N{m.group(2)}")[:40]
    return re.sub(r"[^A-Za-z0-9]", "", "ModRep" + "".join(p.capitalize() for p in sample_id.split("_")[1:]))[:40]


def make(sample_id: str, modules: Callable[[], str]) -> str:
    return build_l5x(target_name=target_name(sample_id), **with_baseline(extra_modules_xml=modules()))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", metavar="REGEX", help="build only the sample_ids this matches")
    args = ap.parse_args()
    for sample_id, what, modules in plan():
        if args.only and not re.search(args.only, sample_id):
            continue
        out = OUT_ROOT / f"{sample_id}.L5X"
        predicted = write_sample(make(sample_id, modules), out)
        append_manifest_row(sample_id, f"{OQ}: {what} on the realism floor, 1756-L81E v35, against "
                                       f"realism_base_f25: the first copy and each further copy.",
                            CATEGORY, out, predicted)
        print(f"Wrote {out.name} (predicted {predicted:,})")


if __name__ == "__main__":
    main()
