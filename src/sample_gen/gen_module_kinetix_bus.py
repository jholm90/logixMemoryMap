"""Kinetix 5700 shared-bus file -- several real 2198 drive catalogs on one DC
bus, all their axes in one Motion Group, with the bus supply's own converter
axis.

BUILT ONLY FROM BLOCKS WITH CLEAN CAPTURES BEHIND THEM.

  - Drives: gen_module_motion._drive_module_xml, which emits each catalog's real
    identity and ConfigData (sample_gen/data/kinetix.py) and the real
    <ExtendedProperties> ConfigID block. `asmclose_2198_*` and `axmarg_*` are
    built from it and captured at zero errors.
  - Bus supply and converter axis: gen_module_motion.bus_supply_with_converter,
    a 2198-P208 with its "Non-Regenerative AC/DC Converter" axis on Ch1 -- the
    supply every `axmarg_*` file uses.
  - Servo axes: gen_module_motion._axis_tag, on the channels DRIVE_CHANNELS
    allows for each catalog.

What the earlier builds got wrong, so it is not rebuilt that way:

  1. The drives came from the `2conn` blocks in gen_module_sweep_variants.py,
     which had no ConfigID. Studio configures such a drive for networked safety
     and fails Build on a standard controller with "Tag '<drive>:SI': Invalid
     data type for safety tag" once per drive, plus "Project size exceeds
     controller capacity". Both captures of this file recorded exactly that.
     Those blocks are now replaced at import, and lint's
     kinetix_drive_missing_configid refuses any file that bypasses them.
  2. The supplies were 2198-P031 and 2198-P070, which occur in none of the
     eighteen real programs (real supplies: P208 x22, RP200 x3, P141 x2), and
     their converter axes were first built with the servo template, then with
     the P208 converter shape on a non-P208 module.
  3. The processor was 1756-L85ES, then 1756-L83E; every generated file is
     1756-L81E at firmware 35.

ONE bus, not two. A second bus needs its supply and drives in a second bus
sharing group, which is set inside ConfigData, and no verified two-group payload
exists in this project. A guessed one is how the defects above were made.

Run: python -m sample_gen.gen_module_kinetix_bus [--suffix _rN]
"""

from __future__ import annotations

import sys
from pathlib import Path

from sample_gen.data.kinetix import DRIVE_CHANNELS
from sample_gen.gen_module_motion import (
    _MOTION_GROUP_TAG_XML,
    _axis_tag,
    _drive_module_xml,
    bus_supply_with_converter,
)
from sample_gen.manifest import append_manifest_row, write_sample_unmodeled
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "modules"

# The three dual-axis catalogs of the original design, each on its two real
# channels.
DRIVES = (
    ("Bus_Drive_D032", "2198-D032-ERS3"),
    ("Bus_Drive_D057", "2198-D057-ERS3"),
    ("Bus_Drive_D020", "2198-D020-ERS3"),
)


def build() -> str:
    supply_module, converter_axis = bus_supply_with_converter(
        name="Bus_Supply", address="192.168.1.10", axis_name="Bus_Converter_Axis")
    modules = [supply_module]
    axes = [_MOTION_GROUP_TAG_XML, converter_axis]
    for i, (name, catalog) in enumerate(DRIVES):
        modules.append(_drive_module_xml(name, catalog, "false", address=f"192.168.1.{20 + i}"))
        for channel in ("Ch1", "Ch3"):
            if channel not in DRIVE_CHANNELS[catalog][0]:
                raise ValueError(f"{catalog} does not carry an axis on {channel}")
            axes.append(_axis_tag(f"{name}_{channel}_Axis", f"{name}:{channel}"))
    return build_l5x(target_name="KinetixFullBus", tags_xml="\n".join(axes),
                     extra_modules_xml="\n".join(modules))


def main(suffix: str = "") -> None:
    name = f"modulerack_kinetix_full_bus{suffix}"
    out_path = OUT_ROOT / f"{name}.L5X"
    write_sample_unmodeled(build(), out_path)
    append_manifest_row(
        name,
        "Kinetix 5700 shared bus on 1756-L81E fw35: one 2198-P208 supply with its converter "
        "axis, three dual-axis drives (2198-D032-ERS3, -D057-ERS3, -D020-ERS3) and six "
        "AXIS_CIP_DRIVE servo axes on Ch1/Ch3 in one Motion Group, every block from the "
        "builders behind the zero-error asmclose_2198_* and axmarg_* captures. See "
        "OQ-MODULEIO."
        + (" -- OQ-BUILDFAIL-OPEN re-trigger: rebuilt from proven blocks after both earlier "
           "builds failed on ConfigID-less drives ('Invalid data type for safety tag')"
           if suffix else ""),
        "modules", out_path, 0,
    )
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main(sys.argv[sys.argv.index("--suffix") + 1] if "--suffix" in sys.argv else "")
