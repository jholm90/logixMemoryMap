"""Build the synthetic demo project the README screenshots are taken from.

Not a test sample (no manifest row, never captured) and not derived from any
real export: every name is invented. It is shaped like a small automated
assembly line -- eight stations (ST010 Load ... ST080 Unload) dispensing and
curing a bead, each a program with Sequence / Cylinders / Faults / Stats
routines, a `Station_t` status structure, part-present and cylinder position
sensors, solenoid outputs, a two-position cylinder AOI, a recipe library, shift
production data, a Kinetix 5700 motion bus, a PowerFlex 525 infeed conveyor and
a vision gateway.

About nine tenths of what it declares is used by its logic. The rest is left
unused on purpose, the way real projects accumulate it, for the usage flag to
find: an old recipe backup array, a recipe edit buffer, a spare trend buffer, a
legacy counts array, spare sensor inputs, an unwired horn and beacon, a light
curtain bypass bit, a debug step, a test bit, two legacy recipe fields, two
spare station members, a retired routine nothing calls, and the bus supply's
converter axis.

It must open with ZERO unpriced items, so every block in it is one the engine
prices and one with a zero-error capture behind it:

  - the Kinetix bus is gen_module_kinetix_bus's own supply, drives and axes --
    `modulerack_kinetix_full_bus_r3`, captured at 0 errors -- and every 2198
    block passes scripts/check_proven_blocks.py;
  - the PowerFlex 525 and the generic Ethernet module are the module blocks of
    `modulevfd_powerflex525` and `module_genericeth_in0008_out0008`, both
    captured at 0 errors, renamed and re-addressed only;
  - no POINT I/O: a rack-optimized card is listed as unpriced.

main() refuses to write a file that lint or the engine reports anything for.

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
from sample_gen.builders import (  # noqa: E402
    MemberSpec, aoi_xml, motion_instruction_tag_xml, program_tag_xml, rung_xml, tag_xml,
    timer_tag_xml, udt_xml,
)
from sample_gen.gen_module_motion import (  # noqa: E402
    _MOTION_GROUP_TAG_XML, _axis_tag, _drive_module_xml, bus_supply_with_converter,
)
from sample_gen.wrapper import build_l5x  # noqa: E402

_GENERATED = REPO_ROOT / "samples" / "generated" / "modules"

# (station tag, program name, cylinders, servo axes on this station)
STATIONS = [
    ("ST010", "ST010_Load", ["LiftTable", "PartStop"], []),
    ("ST020", "ST020_Locate", ["LocatePin1", "LocatePin2"], []),
    ("ST030", "ST030_Clamp", ["ClampA", "ClampB", "ClampC"], []),
    ("ST040", "ST040_Dispense", ["NozzleShutter"], ["Gantry_X", "Gantry_Y", "Nozzle_Z"]),
    ("ST050", "ST050_Cure", ["CureShutter", "CureLift"], []),
    ("ST060", "ST060_Vision", ["CameraSlide"], ["Camera_X"]),
    ("ST070", "ST070_Reject", ["RejectPusher", "RejectGate"], []),
    ("ST080", "ST080_Unload", ["Gripper", "UnloadLift"], ["Transfer_X", "Transfer_Z"]),
]

# Kinetix drives: (module name, catalog, (axis on Ch1, axis on Ch3)) -- the
# catalogs and channels of gen_module_kinetix_bus.DRIVES.
DRIVES = [
    ("KD1_ST040_Gantry", "2198-D032-ERS3", ("ST040_Gantry_X", "ST040_Gantry_Y")),
    ("KD2_ST040_ST060", "2198-D057-ERS3", ("ST040_Nozzle_Z", "ST060_Camera_X")),
    ("KD3_ST080_Transfer", "2198-D020-ERS3", ("ST080_Transfer_X", "ST080_Transfer_Z")),
]

STATION_T = [MemberSpec(n, "BOOL") for n in (
    "PartPresent", "PartInPosition", "AutoMode", "InCycle", "CycleComplete", "Faulted",
    "ResetReq", "SpareFlag")] + [
    MemberSpec("StepNo", "DINT"), MemberSpec("PartId", "DINT"), MemberSpec("GoodParts", "DINT"),
    MemberSpec("RejectParts", "DINT"), MemberSpec("CycleTime", "REAL"),
    MemberSpec("CycleTimeMax", "REAL"), MemberSpec("SpareWord", "DINT")]

RECIPE_T = [MemberSpec("RecipeId", "DINT"), MemberSpec("PartNumber", "DINT"),
            MemberSpec("BeadLength", "REAL"), MemberSpec("BeadWidth", "REAL"),
            MemberSpec("NozzleSpeed", "REAL"), MemberSpec("CureTime", "DINT"),
            MemberSpec("ConveyorSpeed", "DINT"), MemberSpec("VisionProgram", "DINT"),
            MemberSpec("PathSetpoints", "REAL", dimension=32),
            MemberSpec("LegacyOffsets", "REAL", dimension=16), MemberSpec("LegacyEnable", "BOOL")]

SHIFT_T = [MemberSpec("GoodParts", "DINT"), MemberSpec("RejectParts", "DINT"),
           MemberSpec("DowntimeMin", "REAL"), MemberSpec("HourlyGood", "DINT", dimension=24),
           MemberSpec("HourlyReject", "DINT", dimension=24)]


def _proven_module(sample: str, name: str, address: str) -> str:
    """The one non-controller Module of a zero-error capture, renamed and re-addressed."""
    text = (_GENERATED / f"{sample}.L5X").read_text(encoding="utf-8-sig")
    block = [m for m in re.findall(r"<Module\b.*?</Module>", text, re.S) if 'Name="Local"' not in m][0]
    block = re.sub(r'Name="[^"]+"', f'Name="{name}"', block, count=1)
    return re.sub(r'Address="\d+\.\d+\.\d+\.\d+"', f'Address="{address}"', block, count=1)


def _cylinder_aoi() -> tuple[str, list[MemberSpec]]:
    return aoi_xml(
        "Cylinder2Pos",
        [MemberSpec(n, "BOOL") for n in ("ExtendCmd", "RetractCmd", "ExtendedPS", "RetractedPS")],
        [MemberSpec(n, "BOOL") for n in ("ExtendSol", "RetractSol", "IsExtended", "IsRetracted", "Fault")],
        [], [MemberSpec("TravelScans", "DINT")],
        logic_rungs_xml="\n".join(rung_xml(i, t) for i, t in enumerate([
            "XIC(ExtendCmd)XIO(RetractCmd)OTE(ExtendSol);",
            "XIC(RetractCmd)XIO(ExtendCmd)OTE(RetractSol);",
            "XIC(ExtendedPS)XIO(RetractedPS)OTE(IsExtended);",
            "XIC(RetractedPS)XIO(ExtendedPS)OTE(IsRetracted);",
            "XIC(ExtendSol)XIO(ExtendedPS)ADD(TravelScans,1,TravelScans);",
            "XIO(ExtendSol)XIO(RetractSol)MOV(0,TravelScans);",
            "GRT(TravelScans,500)OTE(Fault);",
        ])),
    )


def _routine(name: str, texts: list[str]) -> str:
    body = "\n".join(rung_xml(i, t) for i, t in enumerate(texts))
    return f'<Routine Name="{name}" Type="RLL">\n<RLLContent>\n{body}\n</RLLContent>\n</Routine>'


def _program(name: str, tags: list[str], routines: list[str]) -> str:
    return (f'<Program Name="{name}" TestEdits="false" MainRoutineName="MainRoutine" Disabled="false" '
            f'UseAsFolder="false">\n<Tags>\n' + "\n".join(tags) + "\n</Tags>\n<Routines>\n"
            + "\n".join(routines) + "\n</Routines>\n</Program>")


def _station(k: int, s: str, prog: str, cyls: list[str], axes: list[str]) -> tuple[str, list[str]]:
    """One station program, and the controller tags it owns."""
    cyl = [f"{s}_{c}" for c in cyls]
    tags = [tag_xml(s, "Station_t", udt_members=STATION_T), tag_xml(f"{s}_PartPresent_PX", "BOOL")]
    for c in cyl:
        tags += [tag_xml(f"{c}_Ext_PX", "BOOL"), tag_xml(f"{c}_Ret_PX", "BOOL"),
                 tag_xml(f"{c}_Ext_Sol", "BOOL"), tag_xml(f"{c}_Ret_Sol", "BOOL")]

    seq = [
        f"XIC(Line_AutoMode)XIC(Line_EStopOK)OTE({s}.AutoMode);",
        f"XIC({s}_PartPresent_PX)OTE({s}.PartPresent);",
        f"EQU({s}.StepNo,0)XIC({s}.AutoMode)XIC({s}.PartPresent)XIO({s}.Faulted)MOV(10,{s}.StepNo);",
        f"NEQ({s}.StepNo,0)OTE({s}.InCycle);",
        f"XIC({s}.InCycle)TON(StepTmr,?,?);",
    ]
    step = 10
    for c in cyl:
        seq.append(f"EQU({s}.StepNo,{step})OTE({c}.ExtendCmd);")
        seq.append(f"EQU({s}.StepNo,{step})XIC({c}.IsExtended)MOV({step + 10},{s}.StepNo);")
        step += 10
    seq += [
        f"XIC({cyl[0]}.IsExtended)XIC({s}.PartPresent)OTE({s}.PartInPosition);",
        f"EQU({s}.StepNo,{step})XIC({s}.PartInPosition)OTL({s}.CycleComplete);",
        f"XIC({s}.CycleComplete)[" + ",".join(f"OTE({c}.RetractCmd)" for c in cyl) + "];",
        f"XIC({s}.CycleComplete)XIC({cyl[-1]}.IsRetracted)MOV(0,{s}.StepNo);",
        f"EQU({s}.StepNo,0)OTU({s}.CycleComplete);",
        (f"XIC({s}.CycleComplete)ONS(CompleteOS)MOV(PartTracking[{k}],PartTracking[{k + 1}])"
         f"MOV(PartTracking[{k + 1}],{s}.PartId);") if k < 7 else
        f"XIC({s}.CycleComplete)ONS(CompleteOS)MOV(PartTracking[{k}],{s}.PartId)CLR(PartTracking[{k}]);",
    ]
    cylinders = []
    for c in cyl:
        cylinders += [f"XIC({c}_Ext_PX)OTE({c}.ExtendedPS);", f"XIC({c}_Ret_PX)OTE({c}.RetractedPS);",
                      f"Cylinder2Pos({c});", f"XIC({c}.ExtendSol)OTE({c}_Ext_Sol);",
                      f"XIC({c}.RetractSol)OTE({c}_Ret_Sol);"]
    faults = [f"XIC({c}.Fault)OTL({s}.Faulted);" for c in cyl] + [
        f"GRT(StepTmr.ACC,20000)OTL({s}.Faulted);",
        f"XIC(Line_Reset)OTE({s}.ResetReq);",
        f"XIC({s}.ResetReq)OTU({s}.Faulted);",
        f"XIC({s}.ResetReq)RES(StepTmr);",
    ]
    stats = [
        f"XIC({s}.InCycle)TON(CycleTmr,?,?);",
        f"XIC({s}.CycleComplete)MOV(CycleTmr.ACC,{s}.CycleTime);",
        f"GRT({s}.CycleTime,{s}.CycleTimeMax)MOV({s}.CycleTime,{s}.CycleTimeMax);",
        f"XIC({s}.CycleComplete)ONS(StatsOS)ADD({s}.GoodParts,1,{s}.GoodParts)"
        f"ADD(ShiftData[ShiftNo].HourlyGood[HourNo],1,ShiftData[ShiftNo].HourlyGood[HourNo]);",
        f"XIC({s}.Faulted)ADD(ShiftData[ShiftNo].DowntimeMin,0.016,ShiftData[ShiftNo].DowntimeMin);",
    ]
    # Station-specific logic.
    if s == "ST010":
        seq += ["XIC(ST010.AutoMode)OTE(Infeed_VFD:O.Start);",
                "XIO(ST010.AutoMode)OTE(Infeed_VFD:O.Stop);",
                "MOV(ActiveRecipe.ConveyorSpeed,Infeed_VFD:O.FreqCommand);",
                "MOV(Infeed_VFD:I.OutputFreq,Conveyor_ActualFreq);"]
        faults.insert(0, "XIC(Infeed_VFD:I.Faulted)OTL(ST010.Faulted);")
        stats.append("XIC(ST080.CycleComplete)ONS(ShiftGoodOS)ADD(ShiftData[ShiftNo].GoodParts,1,"
                     "ShiftData[ShiftNo].GoodParts);")
    if s == "ST040":
        seq += ["MOV(ActiveRecipe.NozzleSpeed,ST040_NozzleSpeedCmd);",
                "MOV(ActiveRecipe.BeadLength,ST040_BeadLengthCmd);",
                "MOV(ActiveRecipe.BeadWidth,ST040_BeadWidthCmd);",
                "XIC(ST040.InCycle)MOV(ActiveRecipe.PathSetpoints[ST040_PathIndex],ST040_PathTarget);"]
        tags += [tag_xml(n, "REAL") for n in ("ST040_NozzleSpeedCmd", "ST040_BeadLengthCmd",
                                               "ST040_BeadWidthCmd", "ST040_PathTarget")]
        tags.append(tag_xml("ST040_PathIndex", "DINT"))
    if s == "ST050":
        seq.append("MOV(ActiveRecipe.CureTime,ST050_CureTimeSp);")
        tags.append(tag_xml("ST050_CureTimeSp", "DINT"))
    if s == "ST060":
        seq += ["MOV(ActiveRecipe.VisionProgram,Scanner_Gateway:O.Data[0]);",
                "MOV(Scanner_Gateway:I.Data[0],ST060_VisionResult);",
                "EQU(ST060_VisionResult,1)OTE(ST060_VisionPass);"]
        tags += [tag_xml("ST060_VisionResult", "DINT"), tag_xml("ST060_VisionPass", "BOOL")]
    if s == "ST070":
        stats.append("XIO(ST060_VisionPass)XIC(ST070.CycleComplete)ONS(RejectOS)ADD(ST070.RejectParts,1,"
                     "ST070.RejectParts)ADD(ShiftData[ShiftNo].RejectParts,1,ShiftData[ShiftNo].RejectParts)"
                     "ADD(ShiftData[ShiftNo].HourlyReject[HourNo],1,ShiftData[ShiftNo].HourlyReject[HourNo]);")
    motion = []
    for a in axes:
        axis = f"{s}_{a}"
        motion += [f"XIC({s}.AutoMode)MSO({axis},{axis}_MSO);", f"XIO({s}.AutoMode)MSF({axis},{axis}_MSF);"]
        tags += [motion_instruction_tag_xml(f"{axis}_MSO"), motion_instruction_tag_xml(f"{axis}_MSF")]

    main = ["JSR(Sequence,0);", "JSR(Cylinders,0);", "JSR(Faults,0);", "JSR(Stats,0);"]
    routines = [_routine("Sequence", seq), _routine("Cylinders", cylinders),
                _routine("Faults", faults), _routine("Stats", stats)]
    if motion:
        main.append("JSR(Motion,0);")
        routines.append(_routine("Motion", motion))
    if s == "ST080":
        # Left behind by an earlier homing scheme: nothing calls it any more.
        routines.append(_routine("Retired_Homing", [
            "XIC(ST080.ResetReq)ADD(Retired_HomeCount,1,Retired_HomeCount);",
            "GRT(Retired_HomeCount,1000)MOV(0,Retired_HomeCount);"]))
        tags.append(tag_xml("Retired_HomeCount", "DINT"))
    prog_tags = [timer_tag_xml("StepTmr"), timer_tag_xml("CycleTmr")] + [
        program_tag_xml(n, "BOOL") for n in ("CompleteOS", "StatsOS")
        + (("RejectOS",) if s == "ST070" else ()) + (("ShiftGoodOS",) if s == "ST010" else ())]
    return _program(prog, prog_tags, [_routine("MainRoutine", main)] + routines), tags


def build() -> str:
    aoi_def, cyl_storage = _cylinder_aoi()
    supply, converter = bus_supply_with_converter(
        name="Kinetix_BusSupply", address="192.168.1.10", axis_name="Bus_Converter_Axis")
    modules, tags = [supply], [_MOTION_GROUP_TAG_XML, converter]
    for i, (name, catalog, (ch1, ch3)) in enumerate(DRIVES):
        modules.append(_drive_module_xml(name, catalog, "false", address=f"192.168.1.{20 + i}"))
        tags += [_axis_tag(ch1, f"{name}:Ch1"), _axis_tag(ch3, f"{name}:Ch3")]
    modules.append(_proven_module("modulevfd_powerflex525", "Infeed_VFD", "192.168.1.40"))
    modules.append(_proven_module("module_genericeth_in0008_out0008", "Scanner_Gateway", "192.168.1.50"))

    tags += [tag_xml(n, "BOOL") for n in ("Line_AutoMode", "Line_EStopOK", "Line_Reset", "Line_LoadRecipe")]
    tags += [tag_xml(n, "DINT") for n in ("RecipeSelect", "ShiftNo", "HourNo")]
    tags += [tag_xml("Conveyor_ActualFreq", "INT"), tag_xml("PartTracking", "DINT", dimensions=(8,)),
             tag_xml("ActiveRecipe", "Recipe_t", udt_members=RECIPE_T),
             tag_xml("RecipeLibrary", "Recipe_t", dimensions=(200,), udt_members=RECIPE_T),
             tag_xml("ShiftData", "Shift_t", dimensions=(3,), udt_members=SHIFT_T)]
    # Left unused on purpose: what the usage flag is for.
    tags += [tag_xml("Old_Recipe_Backup", "Recipe_t", dimensions=(100,), udt_members=RECIPE_T),
             tag_xml("Recipe_EditBuffer", "Recipe_t", udt_members=RECIPE_T),
             tag_xml("Spare_Trend_Buffer", "REAL", dimensions=(2000,)),
             tag_xml("Legacy_ShiftCounts", "DINT", dimensions=(50,)),
             tag_xml("Maint_Debug_Step", "DINT")]
    tags += [tag_xml(n, "BOOL") for n in (
        "Test_Bit", "Line_Horn", "Line_Beacon_Amber", "ST020_Spare1_PX", "ST050_Spare_PX",
        "ST060_LightCurtain_Bypass", "ST070_Spare_PX")]
    tags += [tag_xml("ST080_LastPartNumber", "DINT"), tag_xml("Line_RecipeActive", "BOOL")]

    programs, scheduled = [], []
    for k, (s, prog, cyls, axes) in enumerate(STATIONS):
        program, station_tags = _station(k, s, prog, cyls, axes)
        programs.append(program)
        scheduled.append(f'<ScheduledProgram Name="{prog}"/>')
        tags += station_tags
        tags += [tag_xml(f"{s}_{c}", "Cylinder2Pos", udt_members=cyl_storage) for c in cyls]

    line_rungs = "\n".join(rung_xml(i, t) for i, t in enumerate([
        "XIC(Line_LoadRecipe)ONS(Line_LoadRecipeOS)COP(RecipeLibrary[RecipeSelect],ActiveRecipe,1);",
        "XIC(Line_Reset)CLR(ST010.StepNo);",
        "EQU(ActiveRecipe.RecipeId,RecipeSelect)OTE(Line_RecipeActive);",
        "XIC(ST080.CycleComplete)MOV(ActiveRecipe.PartNumber,ST080_LastPartNumber);",
    ]))
    return build_l5x(
        target_name="DemoLine",
        tags_xml="\n".join(tags),
        extra_datatypes_xml="\n".join([udt_xml("Station_t", STATION_T), udt_xml("Recipe_t", RECIPE_T),
                                       udt_xml("Shift_t", SHIFT_T)]),
        extra_aoi_xml=aoi_def,
        extra_modules_xml="\n".join(modules),
        extra_program_tags_xml=program_tag_xml("Line_LoadRecipeOS", "BOOL"),
        extra_programs_xml="\n".join(programs),
        extra_scheduled_programs_xml="\n".join(scheduled),
        extra_rungs_xml=line_rungs,
    )


def main(argv: list[str]) -> int:
    out = Path(argv[1]) if len(argv) > 1 else REPO_ROOT / "docs" / "demo" / "DemoLine.L5X"
    text = build()
    from sample_gen.lint import lint_l5x
    findings = lint_l5x(text)
    _entries, errors = build_report(ET.fromstring(text), load_memory_model())
    if findings or errors:
        raise SystemExit(f"demo refused: {len(findings)} lint finding(s), {len(errors)} unpriced item(s): "
                         f"{[(f.kind, f.detail[:120]) for f in findings][:5]} {[e.path for e in errors][:5]}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
