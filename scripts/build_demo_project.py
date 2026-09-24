"""Build the synthetic demo project the README screenshots are taken from.

Not a test sample (no manifest row, never captured) and not derived from any
real export: generated names only. It carries what a screenshot needs to show --
a Kinetix 5700 bus with six servo axes, a PowerFlex 525 and a generic Ethernet
device, four line programs of stations, a valve AOI with sixty instances, and
one deliberately bloated recipe-history array to be the "memory hog" the
treemap is built to find.

It must open with ZERO unpriced items, so every block in it is one the engine
prices and one with a zero-error capture behind it:

  - the Kinetix bus is gen_module_kinetix_bus.build()'s own supply, drives and
    axes -- `modulerack_kinetix_full_bus_r3`, captured at 0 errors, and every
    2198 block passes scripts/check_proven_blocks.py;
  - the PowerFlex 525 and the generic Ethernet module are the module blocks of
    `modulevfd_powerflex525` and `module_genericeth_in0008_out0008`, both
    captured at 0 errors, renamed and re-addressed only;
  - no POINT I/O: a rack-optimized card is listed as unpriced.

main() refuses to write a file the engine reports any unpriced item for.

Run: python scripts/build_demo_project.py [out.L5X]   (default docs/demo/DemoLine.L5X)
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

import re  # noqa: E402
import xml.etree.ElementTree as ET  # noqa: E402

from l5x_memory_analyzer.sizing.constants import load_memory_model  # noqa: E402
from l5x_memory_analyzer.sizing.report import build_report  # noqa: E402
from sample_gen import realism  # noqa: E402
from sample_gen.gen_module_kinetix_bus import DRIVES  # noqa: E402
from sample_gen.gen_module_motion import (  # noqa: E402
    _MOTION_GROUP_TAG_XML, _axis_tag, _drive_module_xml, bus_supply_with_converter,
)
from sample_gen.builders import MemberSpec, aoi_xml, rung_xml, tag_xml, udt_xml  # noqa: E402
from sample_gen.wrapper import build_l5x  # noqa: E402

VALVES = 60
RECIPES = 400
STATIONS = 320

_RECIPE = ([MemberSpec("Id", "DINT"), MemberSpec("Grade", "DINT"), MemberSpec("Length", "REAL"),
            MemberSpec("Width", "REAL"), MemberSpec("Thickness", "REAL")]
           + [MemberSpec("PieceCounts", "DINT", dimension=16), MemberSpec("Setpoints", "REAL", dimension=32)]
           + [MemberSpec(f"Flag{i}", "BOOL") for i in range(8)])


_GENERATED = REPO_ROOT / "samples" / "generated" / "modules"


def _proven_module(sample: str, name: str, address: str) -> str:
    """The one non-controller Module of a zero-error capture, renamed and re-addressed."""
    text = (_GENERATED / f"{sample}.L5X").read_text(encoding="utf-8-sig")
    block = [m for m in re.findall(r"<Module\b.*?</Module>", text, re.S) if 'Name="Local"' not in m][0]
    block = re.sub(r'Name="[^"]+"', f'Name="{name}"', block, count=1)
    return re.sub(r'Address="\d+\.\d+\.\d+\.\d+"', f'Address="{address}"', block, count=1)


def _motion() -> tuple[list[str], list[str]]:
    supply, converter = bus_supply_with_converter(
        name="Bus_Supply", address="192.168.1.10", axis_name="Bus_Converter_Axis")
    modules, axes = [supply], [_MOTION_GROUP_TAG_XML, converter]
    for i, (name, catalog) in enumerate(DRIVES):
        modules.append(_drive_module_xml(name, catalog, "false", address=f"192.168.1.{20 + i}"))
        axes += [_axis_tag(f"{name}_{ch}_Axis", f"{name}:{ch}") for ch in ("Ch1", "Ch3")]
    modules.append(_proven_module("modulevfd_powerflex525", "Infeed_VFD", "192.168.1.40"))
    modules.append(_proven_module("module_genericeth_in0008_out0008", "Scanner_Gateway", "192.168.1.50"))
    return modules, axes


def build() -> str:
    definition, storage = aoi_xml(
        "Valve_Ctrl",
        [MemberSpec("Cmd", "BOOL"), MemberSpec("Interlock", "BOOL")],
        [MemberSpec("Open", "BOOL"), MemberSpec("Fault", "BOOL")],
        [], [MemberSpec("Travel", "DINT")],
        logic_rungs_xml="\n".join([
            rung_xml(0, "XIC(Cmd)XIO(Interlock)OTE(Open);"),
            rung_xml(1, "XIC(Cmd)XIO(Open)ADD(Travel,1,Travel);"),
            rung_xml(2, "GRT(Travel,500)OTE(Fault);"),
        ]),
    )
    modules, axes = _motion()
    tags = [tag_xml(f"V{i:03d}", "Valve_Ctrl", udt_members=storage) for i in range(1, VALVES + 1)]
    tags += axes
    tags.append(tag_xml("RecipeHistory", "RecipeRecord", dimensions=(RECIPES,), udt_members=_RECIPE))
    tags.append(tag_xml("RecipeIndex", "DINT"))
    valve_rungs = "\n".join(rung_xml(i - 1, f"Valve_Ctrl(V{i:03d});") for i in range(1, VALVES + 1))
    valves_program = (
        '<Program Name="Valves" TestEdits="false" MainRoutineName="MainRoutine" Disabled="false" '
        'UseAsFolder="false">\n<Tags>\n</Tags>\n<Routines>\n<Routine Name="MainRoutine" Type="RLL">\n'
        f"<RLLContent>\n{valve_rungs}\n</RLLContent>\n</Routine>\n</Routines>\n</Program>")
    plant = realism.plant(STATIONS)
    return build_l5x(
        target_name="DemoLine",
        tags_xml="\n".join(tags) + "\n" + plant["tags_xml"],
        extra_datatypes_xml=udt_xml("RecipeRecord", _RECIPE) + "\n" + plant["extra_datatypes_xml"],
        extra_aoi_xml=definition,
        extra_modules_xml="\n".join(modules),
        extra_programs_xml=valves_program + "\n" + plant["extra_programs_xml"],
        extra_scheduled_programs_xml='<ScheduledProgram Name="Valves"/>\n' + plant["extra_scheduled_programs_xml"],
        extra_rungs_xml=rung_xml(0, "MOV(RecipeHistory[RecipeIndex].Id,RecipeIndex);"),
    )


def main(argv: list[str]) -> int:
    out = Path(argv[1]) if len(argv) > 1 else REPO_ROOT / "docs" / "demo" / "DemoLine.L5X"
    text = build()
    from sample_gen.lint import lint_l5x
    findings = lint_l5x(text)
    _entries, errors = build_report(ET.fromstring(text), load_memory_model())
    if findings or errors:
        raise SystemExit(f"demo refused: {len(findings)} lint finding(s), {len(errors)} unpriced item(s): "
                         f"{[f.kind for f in findings][:5]} {[e.path for e in errors][:5]}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
