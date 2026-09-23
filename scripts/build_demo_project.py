"""Build the synthetic demo project the README screenshots are taken from.

Not a test sample (no manifest row, never captured) and not derived from any
real export: generated names only. It carries what a screenshot needs to show --
five POINT I/O racks, four line programs of stations, a valve AOI with sixty
instances, and one deliberately bloated recipe-history array to be the
"memory hog" the treemap is built to find.

Run: python scripts/build_demo_project.py [out.L5X]   (default docs/demo/DemoLine.L5X)
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from sample_gen import realism  # noqa: E402
from sample_gen.builders import MemberSpec, aoi_xml, rung_xml, tag_xml, udt_xml  # noqa: E402
from sample_gen.wrapper import build_l5x  # noqa: E402

VALVES = 60
RECIPES = 400
STATIONS = 320

_RECIPE = ([MemberSpec("Id", "DINT"), MemberSpec("Grade", "DINT"), MemberSpec("Length", "REAL"),
            MemberSpec("Width", "REAL"), MemberSpec("Thickness", "REAL")]
           + [MemberSpec("PieceCounts", "DINT", dimension=16), MemberSpec("Setpoints", "REAL", dimension=32)]
           + [MemberSpec(f"Flag{i}", "BOOL") for i in range(8)])


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
    tags = [tag_xml(f"V{i:03d}", "Valve_Ctrl", udt_members=storage) for i in range(1, VALVES + 1)]
    tags.append(tag_xml("RecipeHistory", "RecipeRecord", dimensions=(RECIPES,), udt_members=_RECIPE))
    tags.append(tag_xml("RecipeIndex", "DINT"))
    valve_rungs = "\n".join(rung_xml(i - 1, f"Valve_Ctrl(V{i:03d});") for i in range(1, VALVES + 1))
    valves_program = (
        '<Program Name="Valves" TestEdits="false" MainRoutineName="MainRoutine" Disabled="false" '
        'UseAsFolder="false">\n<Tags>\n</Tags>\n<Routines>\n<Routine Name="MainRoutine" Type="RLL">\n'
        f"<RLLContent>\n{valve_rungs}\n</RLLContent>\n</Routine>\n</Routines>\n</Program>")
    return build_l5x(
        target_name="DemoLine",
        **realism.with_baseline(
            STATIONS,
            tags_xml="\n".join(tags),
            extra_datatypes_xml=udt_xml("RecipeRecord", _RECIPE),
            extra_aoi_xml=definition,
            extra_programs_xml=valves_program,
            extra_scheduled_programs_xml='<ScheduledProgram Name="Valves"/>',
            extra_rungs_xml=rung_xml(0, "MOV(RecipeHistory[RecipeIndex].Id,RecipeIndex);"),
        ),
    )


def main(argv: list[str]) -> int:
    out = Path(argv[1]) if len(argv) > 1 else REPO_ROOT / "docs" / "demo" / "DemoLine.L5X"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build(), encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
