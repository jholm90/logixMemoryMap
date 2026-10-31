"""OQ-STINSTR: every instruction callable from Structured Text, one file each.

Owner's request 2026-10-25: a test for every instruction ST can call, those ladder cannot
call included. Batch E (`gen_st_extended.py`) already carries TONR / TOFR / RTOR, JSR / SBR /
RET, AOI calls, CONCAT / DTOS / DELETE / FIND / SIZE, COP, CPS and GSV; this batch is the rest:

  function blocks   CTUD OSRI OSFI SETD RESD DFF JKFF BTDT MVMT SCL PIDE RMPS ALM DEDT FGEN
                    INTG PI PMUL SCRV SOC UPDN HPF LPF NTCH LDLG LDL2 DERV TOT D2SD D3SD
                    ESEL HLL RLIM SNEG SSUM MAVE MSTD MAXC MINC POSP SRTP IMC CC
                    MMC HMIBC -- each called with its backing tag (and the arrays a few take)
  operand calls     PID MSG SSV IOT EVENT UID UIE TND EOT SWPB INSERT MID STOD RTOS STOR
                    UPPER LOWER SRT
  functions         ABS SQRT LN LOG SIN COS TAN ASIN ACOS ATAN DEG RAD TRUNC, in a REAL assignment;
                    ATAN2 (two REAL arguments); TOD, FRD, IsINF and IsNAN were built too and
                    Studio refused all four in ST (2026-10-31), as it refused MUX and SEL
  motion            MAM MAJ MAH MAS MSO MRP MSF MAW MAR MDR on one axis, the operand lists the
                    ladder motion files proved, enumerations written as their numbers (ST)

The list is the general instruction reference's ST syntax lines, every instruction whose
"Structured Text" entry gives a call form, plus the operators and functions its expression
table marks usable in ST. AVE, STD, the timers TON / TOF / RTO, the counters CTU / CTD, RES,
FAL / FSC / FLL, BTD, MVM, CLR and the compare and math instructions are ladder-only by that
reference (ST writes them as operators or not at all) and are not here.

Not here, with the reason: ALMD / ALMA (parked, CLAUDE.md "Out of scope"); ASO (an alarm-set
operation: alarm instructions are parked and no real program has an alarm set); REF (its
operand is a REF_TO_AXIS reference type no file here has built and no real program uses);
SFP / SFR (SFC is never worked); the ASCII serial instructions (a 1756-L81E has no serial port); the equipment
phase and sequence instructions (they need phase programs and sequences); the motion
instructions whose operand lists no captured file has proved (the motion reference is needed).

One JSR-called ST routine on the realism floor, 1756-L81E v35; each file is the plant, the
instruction's own backing tags and N calls (50; 20 for CC / IMC / MMC, whose structures are 4 to
16 KB). Every backing structure is priced exactly by the engine, so the reading less the
engine's figure is what the calls cost in ST. Nothing is taken from a real export.

Run: python -m sample_gen.gen_st_instructions [--only REGEX]
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from sample_gen.builders import motion_instruction_tag_xml, rung_xml, tag_xml
from sample_gen.gen_st_sizing import _st_routine
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.realism import with_baseline
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "stinstr"
CATEGORY = "st_shape"
OQ = "OQ-STINSTR"
N = 50

# Function blocks called with their backing tag: mnemonic -> (structure, extra array arguments).
FB = {
    "CTUD": "FBD_COUNTER", "OSRI": "FBD_ONESHOT", "OSFI": "FBD_ONESHOT", "SETD": "DOMINANT_SET",
    "RESD": "DOMINANT_RESET", "DFF": "FLIP_FLOP_D", "JKFF": "FLIP_FLOP_JK", "BTDT": "FBD_BIT_FIELD_DISTRIBUTE",
    "MVMT": "FBD_MASKED_MOVE", "SCL": "SCALE", "PIDE": "PID_ENHANCED", "ALM": "ALARM", "INTG": "INTEGRATOR",
    "PI": "PROP_INT", "PMUL": "PULSE_MULTIPLIER", "SCRV": "S_CURVE", "SOC": "SEC_ORDER_CONTROLLER",
    "UPDN": "UP_DOWN_ACCUM", "HPF": "FILTER_HIGH_PASS", "LPF": "FILTER_LOW_PASS", "NTCH": "FILTER_NOTCH",
    "LDLG": "LEAD_LAG", "LDL2": "LEAD_LAG_SEC_ORDER", "DERV": "DERIVATIVE", "TOT": "TOTALIZER",
    "D2SD": "DISCRETE_2STATE", "D3SD": "DISCRETE_3STATE", "ESEL": "SELECT_ENHANCED", "HLL": "HL_LIMIT",
    "RLIM": "RATE_LIMITER", "SNEG": "SELECTABLE_NEGATE",
    "SSUM": "SELECTED_SUMMER", "MAXC": "MAXIMUM_CAPTURE", "MINC": "MINIMUM_CAPTURE", "POSP": "POSITION_PROP",
    "SRTP": "SPLIT_RANGE", "IMC": "IMC", "CC": "CC", "MMC": "MMC", "HMIBC": "HMIBC",
    # with arrays: the storage / table arguments these take
    "DEDT": "DEADTIME", "FGEN": "FUNCTION_GENERATOR", "MAVE": "MOVING_AVERAGE", "MSTD": "MOVING_STD_DEV",
    "RMPS": "RAMP_SOAK",
}
FB_ARRAYS = {"DEDT": ["Storage"], "FGEN": ["X1", "Y1", "X2", "Y2"], "MAVE": ["Storage", "Weight"],
             "MSTD": ["Storage"], "RMPS": ["Ramp", "Soak", "Time"]}
BIG = {"CC", "IMC", "MMC"}

FUNCTIONS = ("ABS", "SQRT", "LN", "LOG", "SIN", "COS", "TAN", "ASIN", "ACOS", "ATAN", "DEG", "RAD", "TRUNC")
# Functions whose operands are not one REAL: mnemonic -> (assignment, description).
FUNCTIONS_OTHER = {
    "ATAN2": ("SiQ[{i}] := ATAN2(SiR[{i}], SiRArr[{i}]);", "REAL := ATAN2(REAL, REAL)"),
}
# Captured 2026-10-31 and refused by Studio, so no longer built (lint refuses them, not_in_st):
# MUX and SEL are function-block-diagram only; TOD, FRD, IsINF and IsNAN are not ST functions.

# Motion, ST spelling: the ladder files' operand lists with enumerations as numbers.
MOTION = {
    "MAM": "MAM(Axis_Cip_Drive,SiMi{i},MoveType,Position,Speed,0,AccelRate,0,DecelRate,0,1,AccelJerk,DecelJerk,1,1,0,LockPosn,0,EventDistance[0],CalculatedData[0]);",
    "MAJ": "MAJ(Axis_Cip_Drive,SiMi{i},Direction,Speed,0,AccelRate,0,DecelRate,0,0,AccelJerk,DecelJerk,1,0,0,0,0);",
    "MAH": "MAH(Axis_Cip_Drive,SiMi{i});",
    "MAS": "MAS(Axis_Cip_Drive,SiMi{i},0,0,DecelRate,0,0,DecelJerk,2);",
    "MSO": "MSO(Axis_Cip_Drive,SiMi{i});",
    "MRP": "MRP(Axis_Cip_Drive,SiMi{i},0,0,0);",
    "MSF": "MSF(Axis_Cip_Drive,SiMi{i});",
    "MAW": "MAW(Axis_Cip_Drive,SiMi{i},0,0);",
    "MAR": "MAR(Axis_Cip_Drive,SiMi{i},0,0,0,0,1);",
    "MDR": "MDR(Axis_Cip_Drive,SiMi{i},1);",
}


def _common_tags() -> list[str]:
    return [tag_xml("SiD", "DINT", (N,)), tag_xml("SiE", "DINT", (N,)), tag_xml("SiR", "REAL", (N,)),
            tag_xml("SiQ", "REAL", (N,)), tag_xml("SiB", "BOOL", (64,)), tag_xml("SiS", "STRING", (N,)),
            tag_xml("SiS2", "STRING", (N,)), tag_xml("SiArr", "DINT", (100,)), tag_xml("SiRArr", "REAL", (100,))]


def _fb(mn: str) -> tuple[list[str], list[str]]:
    n = 20 if mn in BIG else N
    tags = [tag_xml(f"Si{mn.capitalize()}{i:02d}", FB[mn]) for i in range(n)]
    arrays = FB_ARRAYS.get(mn, [])
    tags += [tag_xml(f"Si{mn.capitalize()}{a}", "REAL", (10,)) for a in arrays]
    args = "".join(f", Si{mn.capitalize()}{a}" for a in arrays)
    return tags, [f"{mn}(Si{mn.capitalize()}{i:02d}{args});" for i in range(n)]


def _operand(mn: str) -> tuple[list[str], list[str]]:
    r = range(N)
    if mn == "PID":
        return ([tag_xml(f"SiPid{i:02d}", "PID") for i in r],
                [f"PID(SiPid{i:02d}, SiR[{i}], 0, SiQ[{i}], 0, 0, 0);" for i in r])
    if mn == "MSG":
        return [tag_xml(f"SiMsg{i:02d}", "MESSAGE") for i in r], [f"MSG(SiMsg{i:02d});" for i in r]
    if mn == "SSV":
        return [], [f"SSV(WallClockTime, , LocalDateTime, SiArr[{i}]);" for i in r]
    if mn == "IOT":
        return [], [f"IOT(RACK_{1 + i % 5}:O);" for i in r]
    if mn == "EVENT":
        return [], ["EVENT(SiEventTask);" for _ in r]
    if mn == "UID":
        return [], [ln for i in r for ln in ("UID();", f"SiD[{i}] := SiD[{i}] + 1;", "UIE();")]
    if mn == "TND":
        return [], [ln for i in r for ln in (f"IF SiB[{i}] THEN", "    TND();", "END_IF;")]
    if mn == "EOT":
        return [], [f"EOT(SiB[{i}]);" for i in r]
    if mn == "SWPB":
        return [], [f"SWPB(SiD[{i}], REVERSE, SiE[{i}]);" for i in r]
    if mn == "INSERT":
        return [], [f"INSERT(SiS[{i}], SiS2[{i}], 1, SiS[{i}]);" for i in r]
    if mn == "MID":
        return [], [f"MID(SiS[{i}], 2, 1, SiS2[{i}]);" for i in r]
    if mn in ("STOD", "STOR", "UPPER", "LOWER"):
        dst = {"STOD": "SiD[{i}]", "STOR": "SiR[{i}]", "UPPER": "SiS2[{i}]", "LOWER": "SiS2[{i}]"}[mn]
        return [], [f"{mn}(SiS[{i}], {dst.format(i=i)});" for i in r]
    if mn == "RTOS":
        return [], [f"RTOS(SiR[{i}], SiS[{i}]);" for i in r]
    if mn == "SRT":
        return [tag_xml(f"SiCtl{i:02d}", "CONTROL") for i in r], [f"SRT(SiArr[0], 0, SiCtl{i:02d});" for i in r]
    raise KeyError(mn)


OPERAND = ("PID", "MSG", "SSV", "IOT", "EVENT", "UID", "TND", "EOT", "SWPB", "INSERT", "MID", "STOD", "RTOS",
           "STOR", "UPPER", "LOWER", "SRT")


def plan() -> list[tuple[str, str, dict]]:
    files = [("stinstr_n00", "control: the plant, the common tags and one assignment", {"kind": "n00"})]
    files += [(f"stinstr_fb_{mn.lower()}", f"{(20 if mn in BIG else N)} {mn} calls, each on its own {FB[mn]}"
               + (f" with its {', '.join(FB_ARRAYS[mn])} REAL[10] arguments" if mn in FB_ARRAYS else ""),
               {"kind": "fb", "mn": mn}) for mn in FB]
    files += [(f"stinstr_op_{mn.lower()}", f"{N} {mn} calls" + (" each bracketed by UIE" if mn == "UID" else ""),
               {"kind": "op", "mn": mn}) for mn in OPERAND]
    files += [(f"stinstr_fn_{fn.lower()}", f"{N} REAL assignments `SiQ[i] := {fn}(SiR[i]);`", {"kind": "fn", "mn": fn})
              for fn in FUNCTIONS]
    files += [(f"stinstr_fn_{fn.lower()}", f"{N} assignments `{form}`", {"kind": "fn2", "mn": fn})
              for fn, (_line, form) in FUNCTIONS_OTHER.items()]
    files += [(f"stinstr_mo_{mn.lower()}", f"{N} {mn} calls on one axis, each on its own MOTION_INSTRUCTION",
               {"kind": "mo", "mn": mn}) for mn in MOTION]
    return [(sid, f"{OQ}: {what}", kw) for sid, what, kw in files]


# The EVENT task as every real one is written (lint event_task_shape): a Rate and a scheduled
# program. Without either, the first build failed to open in Studio twice (2026-10-30).
EVENT_TASK = ('<Task Name="SiEventTask" Type="EVENT" Rate="10" Priority="5" Watchdog="500" '
              'DisableUpdateOutputs="false" InhibitTask="false">\n'
              '<EventInfo EventTrigger="EVENT Instruction Only" EnableTimeout="false"/>\n'
              '<ScheduledPrograms>\n<ScheduledProgram Name="SiEventProgram"/>\n</ScheduledPrograms>\n</Task>')
EVENT_PROGRAM = ('<Program Name="SiEventProgram" TestEdits="false" MainRoutineName="MainRoutine" Disabled="false" '
                 'UseAsFolder="false">\n<Tags/>\n<Routines>\n<Routine Name="MainRoutine" Type="RLL">\n<RLLContent>\n'
                 '<Rung Number="0" Type="N">\n<Text><![CDATA[NOP();]]></Text>\n</Rung>\n</RLLContent>\n'
                 '</Routine>\n</Routines>\n</Program>')


def make(sample_id: str, kw: dict) -> str:
    from sample_gen.gen_axis_composite import _AXIS_TAG_XML
    from sample_gen.gen_motion_instructions import _MOTION_EXTRA_TAGS_XML
    kind, mn = kw["kind"], kw.get("mn")
    tags, lines, extra_tags_xml, tasks = _common_tags(), ["SiD[0] := SiD[0] + 1;"], "", ""
    if kind == "fb":
        t, lines = _fb(mn)
        tags += t
    elif kind == "op":
        t, lines = _operand(mn)
        tags += t
        if mn == "EVENT":
            tasks = EVENT_TASK
    elif kind == "fn":
        lines = [f"SiQ[{i}] := {mn}(SiR[{i}]);" for i in range(N)]
    elif kind == "fn2":
        lines = [FUNCTIONS_OTHER[mn][0].format(i=i) for i in range(N)]
    elif kind == "mo":
        tags += [motion_instruction_tag_xml(f"SiMi{i}") for i in range(N)]
        extra_tags_xml = _AXIS_TAG_XML + "\n" + _MOTION_EXTRA_TAGS_XML
        lines = [MOTION[mn].format(i=i) for i in range(N)]
    target = "".join(p.capitalize() for p in sample_id.split("_"))
    return build_l5x(target_name=target, **with_baseline(
        tags_xml="\n".join(tags) + ("\n" + extra_tags_xml if extra_tags_xml else ""),
        extra_rungs_xml=rung_xml(0, "JSR(SiTarget,0);"),
        extra_routines_xml=_st_routine("SiTarget", lines),
        **({"extra_tasks_xml": tasks, "extra_programs_xml": EVENT_PROGRAM} if tasks else {})))


def _make(job: tuple[str, dict]) -> int:
    sample_id, kw = job
    return write_sample(make(sample_id, kw), OUT_ROOT / f"{sample_id}.L5X")


def main(argv: list[str] | None = None) -> None:
    from sample_gen.progress import run
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", metavar="REGEX")
    args = ap.parse_args([] if argv is None else argv)
    jobs = [(sid, desc, kw) for sid, desc, kw in plan() if not args.only or re.search(args.only, sid)]
    predicted = run(((sid, (sid, kw)) for sid, _, kw in jobs), _make, label="st-instr")
    for sid, desc, _kw in jobs:
        append_manifest_row(sid, f"{desc}; one JSR-called ST routine on the realism floor, 1756-L81E v35; "
                                 f"against stinstr_n00 and the engine's price of its backing tags.",
                            CATEGORY, OUT_ROOT / f"{sid}.L5X", predicted[sid])
        print(f"{sid}: predicted {predicted[sid]:,}")


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
