"""Servo-axis COUNT scaling, single-axis vs dual-axis drive modules
(James, 2026-09-02: "generate 10+ tests to validate this. compare the
difference between s/d modules that are dual/single axis. Overall requires
a power supply, optional regen module and 1..20 axis per rack").

Every file: one 2198-P208 power supply (its own on-board axis = the real
"DC BUS axis" pattern, gen_module_motion.py) + N total servo axes, built
EITHER from single-axis 2198-S086-ERS3 drives (1 real axis/module, "S" =
single inverter) OR dual-axis 2198-Dxxx-ERS3 drives (2 real axes/module via
2 axis tags riding one module, "D" = dual inverter -- real shape already
confirmed in gen_module_motion.py's docstring: "A 'dual axis' drive module
doesn't add a second Module element -- it's the SAME module with a second
AXIS_CIP_DRIVE tag"). Real corpus blocks reused verbatim from
gen_module_sweep_variants.py's own 2conn (non-safety) variants -- the ONLY
change made per instance is a unique Module Name/Ethernet IP (each
variant's block was extracted assuming it's the only networked device in
its own file, same real IP-collision class already fixed elsewhere in this
project) and a unique per-axis AxisID (gen_module_motion.py's `_axis_tag`
already hashes the tag name for this).

Comparison pairs at matched total axis count (2/4/6/8/12/16/20) isolate
whether Studio 5000 charges the same real memory for N axes regardless of
whether they come from N single-axis modules or N/2 dual-axis modules, or
whether the module-count itself (not just axis-count) drives cost --
directly answers James's question, not just "does axis count scale."

Regen module (2198-RP200, real corpus, no axis of its own -- shares the
power supply's DC bus) included on 3 files as an explicit on/off toggle to
isolate its own real cost separately from axis count.

Run: python -m sample_gen.gen_module_axis_scale
"""

from __future__ import annotations

import re
from pathlib import Path

from sample_gen.gen_axis_composite import _AXIS_TAG_XML  # noqa: F401 (re-exported convention)
from sample_gen.gen_module_motion import _P208_MODULE_XML, _MOTION_GROUP_TAG_XML, _axis_tag, _dcbus_axis_tag
from sample_gen.gen_module_sweep import _MODULE_CHAINS
from sample_gen.gen_module_sweep_variants import _MODULE_VARIANTS
from sample_gen.manifest import append_manifest_row, write_sample_unmodeled
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "modules"

_SINGLE_AXIS_CATALOG = "2198-S086-ERS3"
_DUAL_AXIS_CATALOGS = ["2198-D012-ERS3", "2198-D020-ERS3", "2198-D032-ERS3", "2198-D057-ERS3"]
_RP200_XML, _RP200_SOURCE, _RP200_CHAIN_LEN = _MODULE_CHAINS["2198-RP200"]

_IP_RE = re.compile(r"192\.168\.1\.\d+")
_NAME_RE = re.compile(r'(<Module Name=")([^"]+)(")')


def _variant_xml(catalog: str, label: str = "2conn") -> str:
    for entry_label, xml, _source, _chain_len in _MODULE_VARIANTS[catalog]:
        if entry_label == label:
            return xml
    raise KeyError(f"{catalog} has no '{label}' variant")


def _unique_instance(xml: str, new_name: str, ip_last_octet: int) -> str:
    """Real per-catalog block extracted assuming it's the only networked
    device in its own file -- gives every instance a unique Name and
    Ethernet IP so N copies of the SAME catalog can coexist in one file,
    same real IP-collision class _modules_xml_unique_ips already fixes."""
    xml = _NAME_RE.sub(rf"\g<1>{new_name}\g<3>", xml, count=1)
    xml = _IP_RE.sub(f"192.168.9.{ip_last_octet}", xml, count=1)
    return xml


def _build(n_axes: int, shape: str, with_regen: bool, file_idx: int) -> tuple[str, str, list[str]]:
    """shape: 'single' (2198-S086-ERS3 x n_axes) or 'dual' (2198-Dxxx-ERS3
    x n_axes/2, real dual-axis modules only support even totals)."""
    modules = [_P208_MODULE_XML]
    tags = [_MOTION_GROUP_TAG_XML, _dcbus_axis_tag(f"DcBus{file_idx}", "P208:Ch1")]
    axis_names: list[str] = []
    ip = 10

    if with_regen:
        modules.append(_unique_instance(_RP200_XML, f"Regen{file_idx}", ip))
        ip += 1

    if shape == "single":
        base_xml = _variant_xml(_SINGLE_AXIS_CATALOG)
        for k in range(n_axes):
            mod_name = f"Drv{file_idx}_{k}"
            modules.append(_unique_instance(base_xml, mod_name, ip))
            ip += 1
            axis_name = f"Ax{file_idx}_{k}"
            tags.append(_axis_tag(axis_name, f"{mod_name}:Ch1"))
            axis_names.append(axis_name)
    elif shape == "dual":
        assert n_axes % 2 == 0, "dual-axis shape needs an even total axis count"
        n_modules = n_axes // 2
        for k in range(n_modules):
            catalog = _DUAL_AXIS_CATALOGS[k % len(_DUAL_AXIS_CATALOGS)]
            base_xml = _variant_xml(catalog)
            mod_name = f"Drv{file_idx}_{k}"
            modules.append(_unique_instance(base_xml, mod_name, ip))
            ip += 1
            axis_a = f"Ax{file_idx}_{k}A"
            axis_b = f"Ax{file_idx}_{k}B"
            tags.append(_axis_tag(axis_a, f"{mod_name}:Ch1"))
            tags.append(_axis_tag(axis_b, f"{mod_name}:Ch2"))
            axis_names.extend([axis_a, axis_b])
    else:
        raise ValueError(shape)

    l5x = build_l5x(
        target_name=f"AxisScale{file_idx}",
        tags_xml="\n".join(tags),
        extra_modules_xml="\n".join(modules),
    )
    return l5x, "\n".join(modules), axis_names


def _write(out_name: str, l5x: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    write_sample_unmodeled(l5x, out_path)
    append_manifest_row(out_name, description, "modules", out_path, 0)
    print(f"Wrote {out_path} (predicted N/A -- axis content unmodeled, see OQ-AXISSTRUCT)")


# (n_axes, shape, with_regen) -- comparison pairs at matched n_axes wherever
# both shapes divide evenly; n=1 is single-only (a dual module can't produce
# an odd axis count on its own).
_PLAN: list[tuple[int, str, bool]] = [
    (1, "single", False),
    (2, "single", False), (2, "dual", False),
    (4, "single", False), (4, "dual", False),
    (6, "single", False), (6, "dual", False),
    (8, "single", False), (8, "dual", False),
    (8, "single", True), (8, "dual", True),
    (12, "single", False), (12, "dual", False),
    (16, "single", False), (16, "dual", False),
    (20, "single", False), (20, "dual", False),
    (20, "dual", True),
]


def main() -> None:
    for file_idx, (n_axes, shape, with_regen) in enumerate(_PLAN, start=1):
        l5x, _modules_xml, axis_names = _build(n_axes, shape, with_regen, file_idx)
        regen_tag = "_regen" if with_regen else ""
        out_name = f"axis_scale_n{n_axes:02d}_{shape}{regen_tag}"
        description = (
            f"Servo-axis count scaling (James, 2026-09-02): {n_axes} total real servo axes built from "
            f"{'single-axis 2198-S086-ERS3 drives (1 axis/module)' if shape == 'single' else 'dual-axis 2198-Dxxx-ERS3 drives (2 axes/module, one module hosting two real AXIS_CIP_DRIVE tags)'}, "
            f"one 2198-P208 power supply (its own on-board axis = the real 'DC BUS axis'), "
            f"{'plus one 2198-RP200 regen module (no axis of its own)' if with_regen else 'no regen module'}, "
            f"one shared MOTION_GROUP. Compare against the matched-axis-count "
            f"{'dual' if shape == 'single' else 'single'}-shape file to isolate whether N axes cost the "
            f"same regardless of module count. Axis/MotionGroup content is unmodeled (OQ-AXISSTRUCT)."
        )
        _write(out_name, l5x, description)
    print(f"\nDone. {len(_PLAN)} files.")


if __name__ == "__main__":
    main()
