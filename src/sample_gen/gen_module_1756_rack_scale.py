"""1756 local-rack SIZE scaling (James, 2026-09-02: "you can generate up
10+ 1756 rack tests"). gen_module_rack_1756local.py already built ONE
16-module full-chassis rack; this generator varies rack SIZE (2/4/6/8/10/
12/14/16 real modules) and composition (alternate subsets at a few sizes)
using the SAME real catalog pool and re-slot mechanism, so the marginal
cost of the Nth module sharing one backplane can be measured at more than
one data point -- the same open question (OQ-MODULEIO: "the SAME catalog's
2nd, 3rd, ... Nth instance costs LESS than the 1st, not the same") this
project has only ever tested at n=1/3/10 for ONE catalog.

Run: python -m sample_gen.gen_module_1756_rack_scale
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from l5x_memory_analyzer.sizing.constants import load_memory_model
from l5x_memory_analyzer.sizing.report import build_report

from sample_gen.gen_module_rack_1756local import _LOCAL_CATALOGS, _reslot
from sample_gen.gen_module_sweep import _MODULE_CHAINS
from sample_gen.gen_module_sweep_variants import _MODULE_VARIANTS
from sample_gen.manifest import append_manifest_row, write_sample_unmodeled
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "modules"
_MODEL = load_memory_model()

_IA16_1CONN_XML = next(xml for label, xml, _source, _chain_len in _MODULE_VARIANTS["1756-IA16"] if label == "1conn")
_ALL_16 = _LOCAL_CATALOGS + ["1756-IA16"]


def _rack_xml(catalogs: list[str]) -> str:
    blocks = []
    for slot, catalog in enumerate(catalogs, start=1):
        if catalog == "1756-IA16":
            xml = _IA16_1CONN_XML
        else:
            xml, _source, chain_len = _MODULE_CHAINS[catalog]
            assert chain_len == 1, catalog
        slug = "".join(c if c.isalnum() else "" for c in catalog)
        blocks.append(_reslot(xml, slot, f"RackScale_{slug}_{slot}"))
    return "\n".join(blocks)


def _floor_bytes(l5x_text: str) -> int:
    root = ET.fromstring(l5x_text)
    entries, _errors = build_report(root, _MODEL)
    return sum(e.bytes for e in entries)


def _write(out_name: str, catalogs: list[str]) -> None:
    l5x = build_l5x(target_name=f"Rack1756_{out_name}", tags_xml="", extra_modules_xml=_rack_xml(catalogs))
    out_path = OUT_ROOT / f"rack_1756_{out_name}.L5X"
    write_sample_unmodeled(l5x, out_path)
    total = _floor_bytes(l5x)
    description = (
        f"1756 local rack, {len(catalogs)} real ControlLogix modules sharing one chassis with the "
        f"CPU ({', '.join(catalogs)}), each module's own real XML from gen_module_sweep.py/"
        f"gen_module_sweep_variants.py re-slotted to unique sequential addresses. Real floor total "
        f"{total}. Rack-size scaling point for OQ-MODULEIO's multi-module marginal-cost question "
        f"(James, 2026-09-02)."
    )
    append_manifest_row(f"rack_1756_{out_name}", description, "modules", out_path, total)
    print(f"Wrote {out_path} (floor {total} bytes)")


_PLANS: dict[str, list[str]] = {
    "n02": _ALL_16[0:2],
    "n02_alt": _ALL_16[2:4],
    "n04": _ALL_16[0:4],
    "n04_alt": _ALL_16[4:8],
    "n06": _ALL_16[0:6],
    "n06_alt": _ALL_16[6:12],
    "n08": _ALL_16[0:8],
    "n08_alt": _ALL_16[2:10],
    "n10": _ALL_16[0:10],
    "n12": _ALL_16[0:12],
    "n14": _ALL_16[0:14],
    "n16_full": _ALL_16[0:16],
}


def main() -> None:
    for label, catalogs in _PLANS.items():
        _write(label, catalogs)
    print(f"\nDone. {len(_PLANS)} files.")


if __name__ == "__main__":
    main()
