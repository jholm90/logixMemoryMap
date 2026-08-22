"""I/O Module sizing sweep, first batch (James, 2026-08-22): "let's go back
and play with some of the AB Io blocks, the balluff Io link block, local
1756 modules to start. You'll have to swap to a 5069 processor to test the
5069 modules (non safety stuff to start)... same catalog Phoenix rack with
2 input card or 30 input cards, you need to be careful looking at the data
sizes in the l5x module properties."

See docs/IO_MODULES.md for the full inventory and the three real module-
shape patterns this batch is built around (catalog-fixed, Point I/O
rack-alias, generic/config-driven). Every builder used here reproduces a
real shape found in the corpus (builders.py has the file/tag citations).

  A. group_1756_local -- 1/3/10 local 1756-IB16 backplane modules
     (default 1756-L81E processor, pattern 1).
  B. group_point_io -- 1734-AENT adapter + 2/8 1734-IB8 blocks behind it
     (pattern 2, rack-alias -- no independent per-block connection).
  C. group_generic_ethernet_configvariance -- THE key test for James's
     caution: same CatalogNumber="ETHERNET-MODULE" (the real Balluff/IFM
     IO-Link-master pattern), five files at different PrimCxnInputSize/
     OutputSize (2/2 up to 1000/1000, including the real 450/8 seen in the
     corpus). If size really is config-driven and not catalog-driven,
     these must NOT come back at the same real byte cost.
  D. group_5069_local -- 1/3 local 5069-IB16/A modules, processor swapped
     to 5069-L320ERMS2 (non-safety). Needs the wrapper's new 5069-family
     Local-module Ports shape (Type="5069", dual Ethernet, Bus Size=32).

Run: python -m sample_gen.gen_io_modules
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import (
    module_1756_digital_input_xml,
    module_5069_digital_input_xml,
    module_generic_ethernet_xml,
    module_point_io_xml,
)
from sample_gen.lint import lint_or_raise
from sample_gen.manifest import append_manifest_row
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "modules"


def _write_unmodeled(l5x: str, out_name: str, description: str) -> None:
    """Modules aren't parsed by the sizing engine at all yet (Phase 3's
    deferred item) -- predicted_bytes() only looks at Tags, so there's no
    SizeError to dodge here, but logging predicted=0 keeps these consistent
    with the Axis/CAM_PROFILE 'real Capacity data only' convention until
    module sizing is actually implemented."""
    out_path = OUT_ROOT / f"{out_name}.L5X"
    lint_or_raise(l5x, context=str(out_path))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(l5x, encoding="utf-8")
    append_manifest_row(out_name, f"{description} (module sizing not yet implemented)", "modules", out_path, 0)
    print(f"Wrote {out_path} (predicted N/A -- module sizing not yet implemented)")


def group_1756_local() -> None:
    for n in [1, 3, 10]:
        modules = "\n".join(module_1756_digital_input_xml(f"DC_Input{i}", slot=i + 1) for i in range(n))
        l5x = build_l5x(target_name=f"Local1756N{n}", tags_xml="", extra_modules_xml=modules)
        _write_unmodeled(l5x, f"module_1756_ib16_n{n:02d}", f"{n} local 1756-IB16 backplane module(s)")


def group_point_io() -> None:
    for n in [2, 8]:
        block_names = [f"PointBlock{i}" for i in range(n)]
        modules = module_point_io_xml("PointAdapter", "192.168.1.50", block_names)
        l5x = build_l5x(target_name=f"PointIoN{n}", tags_xml="", extra_modules_xml=modules)
        _write_unmodeled(l5x, f"module_pointio_1734_n{n:02d}",
                          f"1734-AENT adapter + {n} 1734-IB8 block(s) behind it")


def group_generic_ethernet_configvariance() -> None:
    # (input_bytes, output_bytes) -- 450/8 matches the real IFM_LugLoader1
    # example found in the corpus, the rest span the range James described.
    configs = [(2, 2), (8, 8), (32, 16), (450, 8), (1000, 1000)]
    for in_b, out_b in configs:
        module = module_generic_ethernet_xml("GenericEthDevice", "192.168.1.61", in_b, out_b)
        l5x = build_l5x(target_name=f"GenericEth{in_b}x{out_b}", tags_xml="", extra_modules_xml=module)
        _write_unmodeled(l5x, f"module_genericeth_in{in_b:04d}_out{out_b:04d}",
                          f"1 generic ETHERNET-MODULE device, PrimCxnInputSize={in_b} PrimCxnOutputSize={out_b} "
                          f"-- config-variance test, same catalog as every other file in this group")


def group_5069_local() -> None:
    for n in [1, 3]:
        modules = "\n".join(module_5069_digital_input_xml(slot=i + 1) for i in range(n))
        l5x = build_l5x(target_name=f"Local5069N{n}", tags_xml="", extra_modules_xml=modules,
                         processor_type="5069-L320ERMS2")
        _write_unmodeled(l5x, f"module_5069_ib16_n{n:02d}",
                          f"{n} local 5069-IB16/A module(s), 5069-L320ERMS2 processor (non-safety)")


def main() -> None:
    group_1756_local()
    group_point_io()
    group_generic_ethernet_configvariance()
    group_5069_local()
    total = 3 + 2 + 5 + 2
    print(f"\nDone. {total} files.")


if __name__ == "__main__":
    main()
