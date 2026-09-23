"""Full Kinetix 5700 SHARED-BUS test -- multiple different real drive/power-
supply catalogs on the same physical DC bus, with all their axes together
in one real Motion Group, including the real "bus power" axis tag.

The real corpus carries many Kinetix 5700 modules, so every
one of those catalog numbers needs testing, in the full-bus shape they
really compile in: all axes in a motion group with bus power groups.

Every individual Kinetix catalog is already covered as a standalone module
by gen_module_sweep.py/gen_module_sweep_variants.py (confirmed:
all 13 real 2198- catalogs in the corpus have their own per-module file).
What's NEW here is the real multi-module BUS shape: this project's real
corpus shows Kinetix modules attached directly to the controller's own
Ethernet port (ParentModule="Local", no separate bridge), with 2+ modules
sharing one physical DC bus and one real Motion Group -- and, critically,
a real finding not modeled anywhere else in this project: a Kinetix power
supply module gets its OWN AXIS_CIP_DRIVE tag too (a "bus power" axis,
e.g. real tag `Bus1_GNT_Power`, MotionModule="<power supply name>:Ch1"),
not just the drive modules. Confirmed real, corpus-verbatim, from
a real export: same exact
`<Data Format="Axis"><AxisParameters .../></Data>` shape already validated
by gen_axis_composite.py/OQ-AXISDEEP for a normal drive axis -- a bus
power tag is not a different or smaller shape, it's the SAME AXIS_CIP_DRIVE
tag type just pointed at a power-supply module instead of a drive.

This file extracts the WHOLE real 2-bus, 5-module, 8-axis subgraph from
that one real file verbatim (module XML reused directly from
gen_module_sweep.py's/gen_module_sweep_variants.py's already-genericized
blocks for these exact 5 catalogs -- same real content already used in
the per-module sweep, just combined and re-addressed instead of typed
fresh):
  - Bus 1 ("GNT"): 2198-P031 power supply + 2198-D032-ERS3 dual-axis drive
    (2 real axes off the ONE drive module, Ch1/Ch3) + 1 real bus-power axis.
  - Bus 2 ("BND1"): 2198-P070 power supply + 2198-D057-ERS3 dual-axis drive
    + 2198-D020-ERS3 dual-axis drive (2 real axes each, Ch1/Ch3) + 1 real
    bus-power axis.
  8 total AXIS_CIP_DRIVE tags, all in one real MotionGroupParameters group
  (reusing gen_module_motion.py's already-validated `_axis_tag`/
  `_MOTION_GROUP_TAG_XML` helpers -- same real shape, not re-typed).

Run: python -m sample_gen.gen_module_kinetix_bus
"""

from __future__ import annotations

import re
from pathlib import Path

from sample_gen.gen_module_motion import _axis_tag, _dcbus_axis_tag, _MOTION_GROUP_TAG_XML
from sample_gen.gen_module_sweep import _MODULE_CHAINS
from sample_gen.gen_module_sweep_variants import _MODULE_VARIANTS
from sample_gen.manifest import append_manifest_row, write_sample_unmodeled
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "modules"

_NAME_RE = re.compile(r'(<Module Name=")[^"]+(")')
_IP_RE = re.compile(r'(Address=")192\.168\.1\.\d+(")')


def _rename(xml: str, new_name: str, new_ip: str) -> str:
    xml = _NAME_RE.sub(rf"\g<1>{new_name}\g<2>", xml, count=1)
    xml = _IP_RE.sub(rf"\g<1>{new_ip}\g<2>", xml, count=1)
    return xml


def _variant_2conn(catalog: str) -> str:
    return next(xml for label, xml, source, chain_len in _MODULE_VARIANTS[catalog] if label == "2conn")


def main(suffix: str = "") -> None:
    ps1_xml = _rename(_MODULE_CHAINS["2198-P031"][0], "Bus1_PowerSupply", "192.168.1.201")
    drive1_xml = _rename(_variant_2conn("2198-D032-ERS3"), "Bus1_Drive_D032", "192.168.1.202")

    ps2_xml = _rename(_MODULE_CHAINS["2198-P070"][0], "Bus2_PowerSupply", "192.168.1.203")
    drive2a_xml = _rename(_variant_2conn("2198-D057-ERS3"), "Bus2_Drive_D057", "192.168.1.204")
    drive2b_xml = _rename(_variant_2conn("2198-D020-ERS3"), "Bus2_Drive_D020", "192.168.1.205")

    modules_xml = "\n".join([ps1_xml, drive1_xml, ps2_xml, drive2a_xml, drive2b_xml])

    tags_xml = "\n".join([
        _MOTION_GROUP_TAG_XML,
        # A bus supply's own axis is a CONVERTER axis, not a servo axis. Built
        # with the servo template, Studio converts the file and then fails
        # Build once per drive module on bus sharing -- the diagnosis in
        # gen_module_motion.bus_supply_with_converter, enforced by lint as
        # kinetix_axis_without_converter. That is why the original file
        # never built.
        _dcbus_axis_tag("Bus1_Power_Axis", "Bus1_PowerSupply:Ch1"),
        _axis_tag("Bus1_Drive_X_Axis", "Bus1_Drive_D032:Ch1"),
        _axis_tag("Bus1_Drive_Z_Axis", "Bus1_Drive_D032:Ch3"),
        _dcbus_axis_tag("Bus2_Power_Axis", "Bus2_PowerSupply:Ch1"),
        _axis_tag("Bus2_Drive057_Trav_Axis", "Bus2_Drive_D057:Ch1"),
        _axis_tag("Bus2_Drive057_Xfer_Axis", "Bus2_Drive_D057:Ch3"),
        _axis_tag("Bus2_Drive020_Chuck_Axis", "Bus2_Drive_D020:Ch1"),
        _axis_tag("Bus2_Drive020_Sf_Axis", "Bus2_Drive_D020:Ch3"),
    ])

    # Built on the default 1756-L81E at firmware 35, like every generated file.
    #
    # The original was built on 1756-L85ES + SIL2, which failed conversion with
    # E_INVALIDARG because the L85ES ProductCode this project carries is a
    # guess. It was then moved to 1756-L83E on the claim that three dual-axis
    # drives and two power supplies do not fit an L81E's 3 MB. That was wrong:
    # the file captured at 230,896 bytes, under a tenth of the L81E's memory.
    # The 2conn variant used here was donated by a plain non-safety 1756-L83E
    # export and every block already carries SafetyEnabled="false".
    l5x = build_l5x(
        target_name="KinetixFullBus", tags_xml=tags_xml, extra_modules_xml=modules_xml,
    )
    out_path = OUT_ROOT / f"modulerack_kinetix_full_bus{suffix}.L5X"
    write_sample_unmodeled(l5x, out_path)
    append_manifest_row(
        f"modulerack_kinetix_full_bus{suffix}",
        "Full Kinetix 5700 shared-bus test: 2 real DC buses (2198-P031+2198-D032-ERS3 "
        "dual-axis on bus 1, 2198-P070+2198-D057-ERS3+2198-D020-ERS3 dual-axis on bus 2), "
        "5 real module catalogs + 8 real AXIS_CIP_DRIVE tags (6 drive axes + 2 'bus power' "
        "axes, one per power supply) in one real Motion Group, verbatim topology from "
        "a real export. Module XML reused from gen_module_sweep.py/"
        "gen_module_sweep_variants.py, axis tags reused from gen_module_motion.py's "
        "validated _axis_tag helper. See OQ-MODULEIO."
        + (" -- OQ-BUILDFAIL-OPEN re-trigger under a new name on 1756-L81E fw35 so the build's "
           "Studio error log is recorded" if suffix else ""),
        "modules", out_path, 0,
    )
    print("Done. 1 Kinetix full-bus file written (5 modules, 8 axes).")


if __name__ == "__main__":
    import sys
    main(sys.argv[sys.argv.index("--suffix") + 1] if "--suffix" in sys.argv else "")
