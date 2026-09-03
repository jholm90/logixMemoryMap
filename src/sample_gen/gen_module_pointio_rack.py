"""Real multi-child PointIO racks (James, 2026-09-02: "you can generate up
10+ pointIO racks"). Every 1734-family catalog already in gen_module_sweep.py
was extracted with its OWN independent single-slot adapter (real, but each
one a SEPARATE standalone node -- e.g. 1734-AENTR/C's own real Bus Size is
exactly 1, a genuine 1-slot adapter product). That's a different real shape
from a true multi-card PointIO rack, which this project has never built.

Real fix: '1734-AENT/B' (source: BAI10048_TrimmerTally_20250704.L5X) is
ALSO already in this project's own corpus with a real Bus Size="8" -- an
8-slot PointIO adapter. Reusing it as the shared rack host, this generator
takes ONLY the real CHILD module (the 2nd Module in each existing 1734
catalog's own chain -- structurally verbatim, untouched) from up to 7 other
1734-family catalogs, re-points its ParentModule to the shared adapter's
own Name, and assigns it a real sequential PointIO bus slot (1-7 -- slot 0
is the adapter's OWN root Port, confirmed real 2026-09-03 via James's actual
"Slot number in use by another module" error, same off-by-one already fixed
for the 1756 local backplane's CPU-at-slot-0 convention) -- the same real
per-file uniqueness convention already used elsewhere in this project
(composite generator's ICP-slot remap), just applied to the PointIO bus
instead of a 1756 backplane. 1734-OB8S/A and /B excluded
(_UNDIAGNOSED_RETEST_CATALOGS -- real, still-undiagnosed CIP Safety
connection failure, not this generator's concern).

Run: python -m sample_gen.gen_module_pointio_rack
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

from l5x_memory_analyzer.sizing.constants import load_memory_model
from l5x_memory_analyzer.sizing.report import build_report

from sample_gen.gen_composite_realistic import _resize_slot_structure
from sample_gen.gen_module_sweep import _MODULE_CHAINS, _UNDIAGNOSED_RETEST_CATALOGS
from sample_gen.manifest import append_manifest_row, write_sample_unmodeled
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "modules"
_MODEL = load_memory_model()

_ADAPTER_XML, _ADAPTER_SOURCE, _ = _MODULE_CHAINS["1734-AENT/B"]
_ADAPTER_NAME = "TestMod1_1734AENTB"  # real Name already in the extracted block
_ADAPTER_REAL_BUS_SIZE = 8  # the real captured value -- see _rack_xml

_CHILD_CATALOGS = sorted(
    cat for cat in _MODULE_CHAINS
    if cat.startswith("1734-")
    and not cat.startswith("1734-AENT")
    and cat not in _UNDIAGNOSED_RETEST_CATALOGS
)


def _extract_child(catalog: str, new_slot: int) -> str:
    xml, _source, chain_len = _MODULE_CHAINS[catalog]
    assert chain_len == 2, f"{catalog}: expected a 2-module [adapter, child] chain"
    mods = re.findall(r"<Module\b.*?</Module>", xml, re.DOTALL)
    child = mods[1]
    child = re.sub(r'ParentModule="[^"]+"', f'ParentModule="{_ADAPTER_NAME}"', child, count=1)
    child = re.sub(
        r'(<Port Id="1" Address=")\d+(" Type="PointIO" Upstream="true" ?/>)',
        rf"\g<1>{new_slot}\g<2>", child, count=1,
    )
    return child


def _floor_bytes(l5x_text: str) -> int:
    root = ET.fromstring(l5x_text)
    entries, _errors = build_report(root, _MODEL)
    return sum(e.bytes for e in entries)


def _rack_xml(children: list[str]) -> str:
    # Slot 0 is the adapter's OWN root Port ("<Port Id="1" Address="0"...")
    # -- real, confirmed 2026-09-03 (James's actual Studio 5000 "Slot number
    # in use by another module" on this exact generator's first child, which
    # this generator had put at slot 0). Same off-by-one already fixed for
    # the 1756 local backplane (CPU's own ICP port sits at Address="0", so
    # the first real expansion module is physically slot 1) -- child slots
    # here start at 1 too.
    new_bus_size = len(children) + 1
    adapter = _ADAPTER_XML
    if new_bus_size != _ADAPTER_REAL_BUS_SIZE:
        # James, 2026-09-03: "I want to see some 14+ racks now" -- more real
        # children than this adapter's own real 8-slot capture happened to
        # have. Bus Size and the adapter's own Connection I/O structure
        # (DataType slot-number, Dimensions, Element count) have to move
        # together or Studio rejects the import -- see
        # _resize_slot_structure's docstring (same real bug class James
        # caught on the composite generator's rack samples).
        adapter = adapter.replace(
            f'<Bus Size="{_ADAPTER_REAL_BUS_SIZE}" />', f'<Bus Size="{new_bus_size}" />', 1,
        )
        adapter = _resize_slot_structure(adapter, new_bus_size)
    parts = [adapter]
    parts.extend(_extract_child(cat, slot) for slot, cat in enumerate(children, start=1))
    return "\n".join(parts)


def _write(out_name: str, children: list[str]) -> None:
    assert len(children) <= len(_CHILD_CATALOGS)
    l5x = build_l5x(target_name=f"RackPointIO_{out_name}", tags_xml="", extra_modules_xml=_rack_xml(children))
    out_path = OUT_ROOT / f"rack_pointio_{out_name}.L5X"
    write_sample_unmodeled(l5x, out_path)
    total = _floor_bytes(l5x)
    description = (
        f"PointIO rack (James, 2026-09-02, 14+ racks added 2026-09-03): one real 1734-AENT/B "
        f"adapter ({_ADAPTER_SOURCE}, real captured Bus Size=8) hosting {len(children)} real "
        f"1734-family child cards on its own PointIO bus ({', '.join(children)}) -- each child's "
        f"real Module content reused verbatim from its own existing gen_module_sweep.py chain, "
        f"only ParentModule/slot Address remapped onto this shared adapter. Bus Size={len(children) + 1} "
        f"(adapter itself + real children); when this exceeds the adapter's own real 8-slot "
        f"capture, its Connection I/O structure is also resized (DataType slot-number/Dimensions/"
        f"Element count) via _resize_slot_structure -- see that function's docstring. Real floor "
        f"total {total}. See OQ-MODULEIO."
    )
    append_manifest_row(f"rack_pointio_{out_name}", description, "modules", out_path, total)
    print(f"Wrote {out_path} (floor {total} bytes)")


_PLANS: dict[str, list[str]] = {
    "n02": _CHILD_CATALOGS[0:2],
    "n02_alt": _CHILD_CATALOGS[2:4],
    "n03": _CHILD_CATALOGS[0:3],
    "n03_alt": _CHILD_CATALOGS[4:7],
    "n04": _CHILD_CATALOGS[0:4],
    "n04_alt": _CHILD_CATALOGS[7:11],
    "n05": _CHILD_CATALOGS[0:5],
    "n06": _CHILD_CATALOGS[0:6],
    "n06_alt": _CHILD_CATALOGS[3:9],
    "n07_full": _CHILD_CATALOGS[0:7],
    "n07_full_alt": _CHILD_CATALOGS[8:15],
    # James, 2026-09-03: "I want to see some 14+ racks now" -- every real
    # distinct 1734-family child catalog in the pool, one adapter (real Bus
    # Size grown from its own captured 8 up to 16 -- see _rack_xml).
    "n15_full": _CHILD_CATALOGS,
}


def main() -> None:
    for label, children in _PLANS.items():
        _write(label, children)
    print(f"\nDone. {len(_PLANS)} files.")


if __name__ == "__main__":
    main()
