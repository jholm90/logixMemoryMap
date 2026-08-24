"""1756 LOCAL RACK test -- multiple real ControlLogix I/O modules mounted
together in the CPU's OWN local chassis (2026-08-27, James: "I also want to
see some 1756 local modules in the processor rack"). gen_module_sweep.py
already covers each 1756 catalog individually (one module + real parent
chain per file); this is the missing "many real local modules sharing one
rack" shape, matching how an actual ControlLogix panel looks.

Every module block is imported directly from gen_module_sweep.py /
gen_module_sweep_variants.py -- the SAME real, genericized, corpus-verbatim
XML already used in the individual sweep, not re-extracted or re-typed.
The only change made here is mechanical: each module's own Port Address
(its backplane slot number) is reassigned to a unique slot 1-16 so 16 real
local-shape catalogs can share one 17-slot chassis (slot 0 = the CPU)
without colliding -- same real <Port Id="1" Address="N" Type="ICP".../>
syntax every one of these already uses on its own, just packed onto one
shared rack instead of each getting its own.

16 catalogs chosen: every real 1756 catalog in the sweep whose own real
shape is ParentModule="Local"/Type="ICP" (the local-backplane shape, not a
remote/RackConnection/rack-aliased one) -- 15 standalone catalogs from
gen_module_sweep.py plus 1756-IA16's "1conn" variant from
gen_module_sweep_variants.py (its OWN real Connection, not the
rack-aliased variant of the same catalog) to round out to 16 and fill the
chassis exactly. Includes 4 local bridge/scanner cards (1756-CNB/D,
1756-DHRIO/E, 1756-DNB, 1756-EN4TR) alongside 12 I/O modules -- a real
ControlLogix local rack commonly carries both, not I/O-only.

Run: python -m sample_gen.gen_module_rack_1756local
"""

from __future__ import annotations

import re
from pathlib import Path

from sample_gen.gen_module_sweep import _MODULE_CHAINS
from sample_gen.gen_module_sweep_variants import _MODULE_VARIANTS
from sample_gen.manifest import append_manifest_row, write_sample_unmodeled
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "modules"

_PORT_RE = re.compile(r'(<Port Id="1" Address=")\d+(" Type="ICP" Upstream="true" ?/>)')
_NAME_RE = re.compile(r'(<Module Name=")[^"]+(")')

# 15 chain_len==1 local-shape catalogs straight from the sweep, plus
# 1756-IA16's real "1conn" variant (its own Connection, not rack-aliased).
_LOCAL_CATALOGS = [
    "1756-IB16", "1756-IF8/A", "1756-OA16", "1756-OA16I", "1756-OF4/A",
    "1756-OF8/B", "1756-IA32/A", "1756-IB16IF/A", "1756-HSC/A", "1756-HSC/B",
    "1756-HYD02", "1756-CNB/D", "1756-DHRIO/E", "1756-DNB", "1756-EN4TR",
]


def _reslot(xml: str, slot: int, new_name: str) -> str:
    xml = _PORT_RE.sub(rf"\g<1>{slot}\g<2>", xml, count=1)
    xml = _NAME_RE.sub(rf"\g<1>{new_name}\g<2>", xml, count=1)
    return xml


def _build_rack_xml() -> str:
    blocks = []
    slot = 1
    for catalog in _LOCAL_CATALOGS:
        xml, source, chain_len = _MODULE_CHAINS[catalog]
        assert chain_len == 1, catalog
        slug = "".join(c if c.isalnum() else "" for c in catalog)
        blocks.append(_reslot(xml, slot, f"Rack1756_{slug}"))
        slot += 1
    ia16_xml = next(xml for label, xml, source, chain_len in _MODULE_VARIANTS["1756-IA16"] if label == "1conn")
    blocks.append(_reslot(ia16_xml, slot, "Rack1756_1756IA16"))
    slot += 1
    assert slot - 1 == 16, f"expected exactly 16 slots filled, got {slot - 1}"
    return "\n".join(blocks)


def main() -> None:
    xml = _build_rack_xml()
    l5x = build_l5x(target_name="Rack1756Local", tags_xml="", extra_modules_xml=xml)
    out_path = OUT_ROOT / "modulerack_1756_local.L5X"
    write_sample_unmodeled(l5x, out_path)
    append_manifest_row(
        "modulerack_1756_local",
        "1756 local rack test: 16 real ControlLogix local-shape modules (12 I/O + 4 "
        "bridge/scanner cards) sharing one 17-slot chassis with the CPU, each module's "
        "own real XML from gen_module_sweep.py/gen_module_sweep_variants.py, re-slotted "
        "to unique addresses 1-16. See OQ-MODULEIO.",
        "modules", out_path, 0,
    )
    print("Done. 1 local-rack file written (16 modules).")


if __name__ == "__main__":
    main()
