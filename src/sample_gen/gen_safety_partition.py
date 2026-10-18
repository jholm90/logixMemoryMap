"""OQ-SAFETYPARTITION: what safety content costs, in the safety partition and in standard memory.

A safety controller keeps safety tags and safety logic in a partition of its own. Its
Capacity tab shows the standard used memory (Edit3) and the safety used memory (Edit6);
the capture tooling records both, as actual_bytes and safety_bytes. Two Studio-made seeds
fixed everything below: a v34 File > New L81ES with FPMS, ROUT and RIN, and a v35 L81ES
routine with every other safety-routine instruction filled in. Every rung here is one of
those call shapes (docs/SAFETY_INSTRUCTIONS.md) and every safety tag carries Studio's own
data block for its type (samples/proven_blocks.json, "safety_tags"); nothing is composed.

Platform: 1756-L81ES at v35, SIL2/PLd, the File > New pair SafetyTask (periodic 20 ms) /
SafetyProgram / MainRoutine, ConfigureSafetyIOAlways="false" as Studio writes it, on the
realism floor. Lint pins the SafePart controller-name prefix to exactly that platform.

Files (sample ids, all differenced against their own control):

  safe_n00                       the plant and an empty safety task/program/routine
  safe_tag_<type>_<n>            controller-scope Class="Safety" tags, no logic: BOOL and
                                 DINT at 10/50/200, REAL, INT and SINT at 50
  safe_tag_dint_50_len<k>        the 50 DINTs with 4-, 20- and 40-character names (12 in
                                 safe_tag_dint_50)
  safe_tag_dint_50_prog          the same 50 DINTs at SafetyProgram scope
  safe_<mn>_tags_<n>             n backing tags of instruction <mn>, no logic
  safe_<mn>_<n>                  the same tags and n rungs, one instruction per rung on its own
                                 tag: ESTOP, RIN, ROUT and LC (the four with real uses) at
                                 10/50/200, every other safety-routine instruction at 20. The
                                 drive-safety instructions also carry one shared SFX tag and
                                 their output tags in both files of the pair.
  safe_std_ctl_r2, safe_std_<x>_r2  XIC+OTE at 10/50/200, TON 50, MOV 50 and ATAN2 20 inside the
                                 safety routine, on safety arrays declared in full in all six
  safe_ref_ctl, safe_ref_<n>     the standard MainRoutine reading safety BOOLs,
                                 XIC(safety)OTE(standard), at 10/50/200

Run: python -m sample_gen.gen_safety_partition [--only REGEX]
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from sample_gen.builders import rung_xml, tag_xml, validate_logix_name
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.realism import with_baseline
from sample_gen.wrapper import build_l5x

REPO = Path(__file__).parent.parent.parent
OUT_ROOT = REPO / "samples" / "generated" / "safety"
CATEGORY = "safety"
PROCESSOR = "1756-L81ES"

_BLOCKS = json.loads((REPO / "samples" / "proven_blocks.json").read_text())["safety_tags"]

# Instruction -> (backing type, call). {t} is the instruction's own tag, {sfx} the shared
# SFX tag a drive-safety instruction reads, {o0}.. its output tags. Each is the exported
# call with two corrections: outputs get their own tags (the source wired one BOOL to all
# of them), and THRSe's Reset goes to its own Reset member (the source used InputStatus).
SHAPES: dict[str, tuple[str, str]] = {
    "RIN": ("REDUNDANT_INPUT", "RIN({t},AUTOMATIC,{t}.ChannelA,{t}.ChannelB,{t}.CircuitReset,{t}.FaultReset)"),
    "ROUT": ("REDUNDANT_OUTPUT", "ROUT({t},NEGATIVE,{t}.Enable,{t}.Feedback1,{t}.Feedback2,{t}.FaultReset)"),
    "FPMS": ("FIVE_POS_MODE_SELECTOR",
             "FPMS({t},{t}.Input1,{t}.Input2,{t}.Input3,{t}.Input4,{t}.Input5,{t}.FaultReset)"),
    "ESTOP": ("EMERGENCY_STOP", "ESTOP({t},MANUAL,{t}.ChannelA,{t}.ChannelB,{t}.CircuitReset,{t}.FaultReset)"),
    "ENPEN": ("ENABLE_PENDANT", "ENPEN({t},MANUAL,{t}.ChannelA,{t}.ChannelB,{t}.CircuitReset,{t}.FaultReset)"),
    "DIN": ("DIVERSE_INPUT", "DIN({t},MANUAL,{t}.ChannelA,{t}.ChannelB,{t}.CircuitReset,{t}.FaultReset)"),
    "LC": ("LIGHT_CURTAIN",
           "LC({t},MANUAL,{t}.ChannelA,{t}.ChannelB,0,{t}.MuteLightCurtain,{t}.CircuitReset,{t}.FaultReset)"),
    "CROUT": ("CONFIGURABLE_ROUT",
              "CROUT({t},NEGATIVE,100,{t}.Actuate,{t}.Feedback1,{t}.Feedback2,{t}.InputStatus,"
              "{t}.OutputStatus,{t}.Reset)"),
    "SMAT": ("SAFETY_MAT", "SMAT({t},MANUAL,100,{t}.ChannelA,{t}.ChannelB,{t}.InputStatus,{t}.Reset)"),
    "THRS": ("TWO_HAND_RUN_STATION",
             "THRS({t},DISABLED,{t}.ActivePin,{t}.RightButtonNormallyOpen,{t}.RightButtonNormallyClosed,"
             "{t}.LeftButtonNormallyOpen,{t}.LeftButtonNormallyClosed,{t}.FaultReset)"),
    "THRSe": ("THRS_ENHANCED",
              "THRSe({t},500,{t}.Enable,{t}.Disconnected,{t}.RightButtonNormallyOpen,"
              "{t}.RightButtonNormallyClosed,{t}.LeftButtonNormallyOpen,{t}.LeftButtonNormallyClosed,"
              "{t}.InputStatus,{t}.Reset)"),
    "DCS": ("DCI_STOP",
            "DCS({t},EMERGENCY STOP,EQUIVALENT - ACTIVE HIGH,500,MANUAL,MANUAL,{t}.ChannelA,{t}.ChannelB,"
            "{t}.InputStatus,{t}.Reset)"),
    "DCST": ("DCI_STOP_TEST",
             "DCST({t},EMERGENCY STOP,EQUIVALENT - ACTIVE HIGH,500,MANUAL,MANUAL,{t}.ChannelA,{t}.ChannelB,"
             "{t}.TestRequest,{t}.InputStatus,{t}.Reset)"),
    "DCSTL": ("DCI_STOP_TEST_LOCK",
              "DCSTL({t},SAFETY GATE,EQUIVALENT - ACTIVE HIGH,500,MANUAL,MANUAL,{t}.ChannelA,{t}.ChannelB,"
              "{t}.TestRequest,{t}.UnlockRequest,{t}.LockFeedback,{t}.HazardStopped,{t}.InputStatus,{t}.Reset)"),
    "DCSTM": ("DCI_STOP_TEST_MUTE",
              "DCSTM({t},LIGHT CURTAIN,EQUIVALENT - ACTIVE HIGH,500,MANUAL,MANUAL,NONE,500,{t}.ChannelA,"
              "{t}.ChannelB,{t}.TestRequest,{t}.Mute,{t}.MutingLampStatus,{t}.InputStatus,{t}.Reset)"),
    "DCSRT": ("DCI_START",
              "DCSRT({t},ENABLE PENDANT,EQUIVALENT - ACTIVE HIGH,500,{t}.Enable,{t}.ChannelA,{t}.ChannelB,"
              "{t}.InputStatus,{t}.Reset)"),
    "DCM": ("DCI_MONITOR",
            "DCM({t},POSITION LIMIT SWITCH,EQUIVALENT - ACTIVE HIGH,500,{t}.ChannelA,{t}.ChannelB,"
            "{t}.InputStatus,{t}.Reset)"),
    "DCA": ("DCA_INPUT",
            "DCA({t},MANUAL,MANUAL,{t}.ChannelA,{t}.ChannelB,{t}.Tolerance,500,{t}.HighLimit,{t}.LowLimit,"
            "{t}.InputStatus,{t}.Reset)"),
    "DCAF": ("DCAF_INPUT",
             "DCAF({t},MANUAL,MANUAL,{t}.ChannelA,{t}.ChannelB,{t}.Tolerance,{t}.DiscrepancyTime,{t}.HighLimit,"
             "{t}.LowLimit,{t}.InputStatus,{t}.Reset)"),
    "TSAM": ("MUTING_TWO_SENSOR_ASYM",
             "TSAM({t},MANUAL,500,500,500,10,{t}.LightCurtain,{t}.Sensor1,{t}.Sensor2,{t}.EnableMute,"
             "{t}.Override,{t}.InputStatus,{t}.MutingLampStatus,{t}.Reset)"),
    "TSSM": ("MUTING_TWO_SENSOR_SYM",
             "TSSM({t},MANUAL,500,500,500,500,10,{t}.LightCurtain,{t}.Sensor1,{t}.Sensor2,{t}.EnableMute,"
             "{t}.Override,{t}.InputStatus,{t}.MutingLampStatus,{t}.Reset)"),
    "FSBM": ("MUTING_FOUR_SENSOR_BIDIR",
             "FSBM({t},MANUAL,500,500,500,500,500,10,{t}.Direction,{t}.LightCurtain,{t}.Sensor1,{t}.Sensor2,"
             "{t}.Sensor3,{t}.Sensor4,{t}.EnableMute,{t}.Override,{t}.InputStatus,{t}.MutingLampStatus,"
             "{t}.Reset)"),
    "CPM": ("CB_CRANKSHAFT_POS_MONITOR",
            "CPM({t},A,{t}.Enable,{t}.BrakeCam,{t}.TakeoverCam,{t}.DynamicCam,{t}.InputStatus,{t}.Reverse,"
            "{t}.PressMotionStatus,{t}.Reset)"),
    "CBIM": ("CB_INCH_MODE",
             "CBIM({t},MANUAL,500,{t}.Enable,{t}.SafetyEnable,{t}.StandardEnable,{t}.Start,{t}.PressInMotion,"
             "{t}.MotionMonitorFault,{t}.SlideZone,{t}.SafetyEnableAck)"),
    "CBSSM": ("CB_SINGLE_STROKE_MODE",
              "CBSSM({t},MANUAL,ENABLED,{t}.Enable,{t}.SafetyEnable,{t}.StandardEnable,{t}.Start,"
              "{t}.PressInMotion,{t}.MotionMonitorFault,{t}.SlideZone,{t}.SafetyEnableAck)"),
    "CBCM": ("CB_CONTINUOUS_MODE",
             "CBCM({t},MANUAL,IMMEDIATE,DISABLED,{t}.Enable,{t}.SafetyEnable,{t}.StandardEnable,"
             "{t}.ArmContinuous,{t}.Start,{t}.StopAtTop,{t}.PressInMotion,{t}.MotionMonitorFault,"
             "{t}.SlideZone,{t}.SafetyEnableAck)"),
    "CSM": ("CAMSHAFT_MONITOR",
            "CSM({t},{t}.MechanicalDelayTime,{t}.MaxPulsePeriod,{t}.MotionRequest,{t}.ChannelA,{t}.ChannelB,"
            "{t}.InputStatus,{t}.Reset)"),
    "EPMS": ("EIGHT_POS_MODE_SELECTOR",
             "EPMS({t},{t}.Input1,{t}.Input2,{t}.Input3,{t}.Input4,{t}.Input5,{t}.Input6,{t}.Input7,{t}.Input8,"
             "{t}.InputStatus,{t}.Lock,{t}.Reset)"),
    "AVC": ("AUX_VALVE_CONTROL",
            "AVC({t},NEGATIVE,500,OFF,500,False,{t}.Actuate,{t}.DelayEnable,{t}.Feedback1,{t}.InputStatus,"
            "{t}.OutputStatus,{t}.Reset)"),
    "MMVC": ("MANUAL_VALVE_CONTROL",
             "MMVC({t},{t}.Enable,{t}.Keyswitch,{t}.Bottom,{t}.FlywheelStopped,{t}.SafetyEnable,{t}.Actuate,"
             "{t}.InputStatus,{t}.OutputStatus,{t}.Reset)"),
    "MVC": ("MAIN_VALVE_CONTROL",
            "MVC({t},NEGATIVE,500,{t}.Actuate,{t}.Feedback1,{t}.Feedback2,{t}.InputStatus,{t}.OutputStatus,"
            "{t}.Reset)"),
    "SFX": ("SAFETY_FEEDBACK_INTERFACE",
            "SFX({t},Seconds,{t}.PositionScaling,{t}.FeedbackResolution,{t}.Unwind,{t}.HomePosition,"
            "{t}.FeedbackPosition,{t}.FeedbackVelocity,{t}.FeedbackValid,{t}.ConnectionFaulted,"
            "{t}.HomeTrigger,{t}.Reset,{t}.SFH,{t}.FP)"),
    "SS1": ("SAFE_STOP_1",
            "SS1({t},MANUAL,MANUAL,{t}.StopMonitorDelay,{t}.StopDelay,{t}.StandstillSpeed,{t}.DecelRefSpeed,"
            "{t}.DecelSpeedTolerance,{sfx},{t}.Request,{t}.Reset,{o0},{o1})"),
    "SS2": ("SAFE_STOP_2",
            "SS2({t},MANUAL,MANUAL,{t}.StopMonitorDelay,{t}.StopDelay,{t}.SS2StandstillSpeed,{t}.DecelRefSpeed,"
            "{t}.DecelSpeedTolerance,{t}.Mode,{t}.CheckDelay,{t}.SOSStandstillSpeed,{t}.StandstillDeadband,"
            "{sfx},{t}.Request,{t}.Reset,{o0},{o1},{o2},{o3},{o4})"),
    "SBC": ("SAFE_BRAKE_CONTROL",
            "SBC({t},MANUAL,{t}.STOtoSBCDelay,{t}.BrakeFeedbackCheckDelay,{t}.BrakeFeedback1,{t}.BrakeFeedback2,"
            "{t}.InputStatus,{t}.OutputStatus,{t}.BrakeEngageL,{t}.Reset,{o0},{o1},{o2})"),
    "SOS": ("SAFE_OPERATING_STOP",
            "SOS({t},MANUAL,MANUAL,{t}.Mode,{t}.CheckDelay,{t}.StandstillSpeed,{t}.StandstillDeadband,{sfx},"
            "{t}.Request,{t}.Reset,{o0},{o1},{o2})"),
    "SDI": ("SAFE_DIRECTION",
            "SDI({t},MANUAL,MANUAL,{t}.PositionWindow,{sfx},{t}.PositiveRequest,{t}.NegativeRequest,{t}.Reset,"
            "{o0},{o1},{o2})"),
    "SLS": ("SAFELY_LIMITED_SPEED",
            "SLS({t},MANUAL,MANUAL,{t}.CheckDelay,{t}.ActiveLimit,{sfx},{t}.Request,{t}.Reset,{o0},{o1},{o2})"),
    "SLP": ("SAFELY_LIMITED_POSITION",
            "SLP({t},MANUAL,MANUAL,{t}.CheckDelay,{t}.PositiveTravelLimit,{t}.NegativeTravelLimit,{sfx},"
            "{t}.Request,{t}.Reset,{o0},{o1},{o2})"),
}
REAL_USE = ("ESTOP", "RIN", "ROUT", "LC")   # the only safety instructions real programs use
REAL_USE_COUNTS = (10, 50, 200)
OTHER_COUNT = 20
SFX_TAG = "SfxFb"


def _members(data_type: str) -> set[str]:
    return set(re.findall(r'DataValueMember Name="([^"]+)"', _BLOCKS[data_type]))


def check_shapes() -> None:
    """Every member a call names exists in Studio's block for the type, and every call
    has the operand count Studio exported."""
    from sample_gen.lint import _NATIVE_ARG_COUNTS, _split_top_level_args
    for mn, (data_type, call) in SHAPES.items():
        members = _members(data_type)
        for member in re.findall(r"\{t\}\.(\w+)", call):
            assert member in members, f"{mn}: {data_type} has no member {member}"
        args = _split_top_level_args(call[len(mn) + 1:-1])
        assert len(args) == _NATIVE_ARG_COUNTS[mn], f"{mn}: {len(args)} operands"


def _outputs(call: str) -> int:
    return len(re.findall(r"\{o\d\}", call))


def _studio_tag(name: str, data_type: str, controller_scope: bool) -> str:
    """A safety tag carrying Studio's own data block for its type. Controller scope is
    the v34 seed's form (Class="Safety", Read/Write); program scope is the v35 safety
    program's (no Class, Read Only)."""
    validate_logix_name(name, "tag")
    cls = ' Class="Safety"' if controller_scope else ""
    access = "Read/Write" if controller_scope else "Read Only"
    radix = ' Radix="Decimal"' if data_type == "BOOL" else ""
    return (f'<Tag Name="{name}"{cls} TagType="Base" DataType="{data_type}"{radix} Constant="false" '
            f'ExternalAccess="{access}">\n{_BLOCKS[data_type]}\n</Tag>')


def _controller_safety_tag(name: str, data_type: str, dimensions: tuple[int, ...] = ()) -> str:
    return tag_xml(name, data_type, dimensions=dimensions).replace(
        f'<Tag Name="{name}"', f'<Tag Name="{name}" Class="Safety"', 1)


def _program_safety_tag(name: str, data_type: str, dimensions: tuple[int, ...] = ()) -> str:
    return tag_xml(name, data_type, dimensions=dimensions).replace(
        'ExternalAccess="Read/Write"', 'ExternalAccess="Read Only"', 1)


def _safety_program(tags: list[str], rungs: list[str]) -> str:
    rungs_xml = "\n".join(rung_xml(i, r) for i, r in enumerate(rungs)) or rung_xml(0, "NOP();")
    return ('<Program Name="SafetyProgram" TestEdits="false" MainRoutineName="MainRoutine" '
            'Disabled="false" Class="Safety" UseAsFolder="false">\n<Tags>\n' + "\n".join(tags)
            + '\n</Tags>\n<Routines>\n<Routine Name="MainRoutine" Type="RLL">\n<RLLContent>\n'
            + rungs_xml + '\n</RLLContent>\n</Routine>\n</Routines>\n</Program>')


_SAFETY_TASK = (
    '<Task Name="SafetyTask" Type="PERIODIC" Rate="20" Priority="10" Watchdog="20" '
    'DisableUpdateOutputs="false" InhibitTask="false" Class="Safety">\n<ScheduledPrograms>\n'
    '<ScheduledProgram Name="SafetyProgram"/>\n</ScheduledPrograms>\n</Task>'
)


def build(sample_id: str, controller_tags: list[str] = (), safety_tags: list[str] = (),
          safety_rungs: list[str] = (), standard_rungs: list[str] = ()) -> str:
    name = "SafePart" + "".join(w.capitalize() for w in sample_id.split("_")[1:])
    arm = {
        "extra_programs_xml": _safety_program(list(safety_tags), list(safety_rungs)),
        "extra_tasks_xml": _SAFETY_TASK,
        "extra_rungs_xml": "\n".join(rung_xml(i, r) for i, r in enumerate(standard_rungs)),
        "tags_xml": "\n".join(controller_tags),
    }
    l5x = build_l5x(name, processor_type=PROCESSOR, safety_level="SIL2", **with_baseline(**arm))
    # Studio's File > New safety project writes "false" (both seeds); build_l5x's SIL2
    # default is "true".
    return l5x.replace('ConfigureSafetyIOAlways="true"', 'ConfigureSafetyIOAlways="false"', 1)


def instruction_pair(mn: str, n: int) -> tuple[list[str], list[str]]:
    """n backing tags (plus the shared SFX tag and output tags a drive-safety
    instruction needs) and n rungs, one instruction each on its own tag."""
    data_type, call = SHAPES[mn]
    tags, rungs = [], []
    needs_sfx = "{sfx}" in call
    if needs_sfx:
        tags.append(_studio_tag(SFX_TAG, "SAFETY_FEEDBACK_INTERFACE", controller_scope=False))
    for i in range(n):
        t = f"{mn}_{i:03d}"
        tags.append(_studio_tag(t, data_type, controller_scope=False))
        outs = {}
        for k in range(_outputs(call)):
            outs[f"o{k}"] = f"{t}_O{k}"
            tags.append(_studio_tag(f"{t}_O{k}", "BOOL", controller_scope=False))
        rungs.append(call.format(t=t, sfx=SFX_TAG, **outs) + ";")
    return tags, rungs


def _padded_names(prefix: str, length: int, n: int) -> list[str]:
    stem = (prefix + "X" * length)[:length - 3]
    return [f"{stem}{i:03d}" for i in range(n)]


def plan() -> list[tuple[str, str, dict]]:
    """(sample_id, description, build kwargs) for every file in the batch."""
    files: list[tuple[str, str, dict]] = []
    tag = "OQ-SAFETYPARTITION"

    files.append(("safe_n00", f"{tag}: control -- plant + empty SafetyTask/SafetyProgram/MainRoutine", {}))

    for typ, counts in (("BOOL", (10, 50, 200)), ("DINT", (10, 50, 200)),
                        ("REAL", (50,)), ("INT", (50,)), ("SINT", (50,))):
        for n in counts:
            names = [f"Safe{typ.capitalize()}_{i:03d}" for i in range(n)]
            files.append((f"safe_tag_{typ.lower()}_{n}",
                          f"{tag}: {n} controller-scope Class=Safety {typ} tags, no logic",
                          {"controller_tags": [_controller_safety_tag(x, typ) for x in names]}))
    for length in (4, 20, 40):
        names = _padded_names("SafeDintNameLength", length, 50)
        files.append((f"safe_tag_dint_50_len{length}",
                      f"{tag}: 50 controller-scope Class=Safety DINT tags, {length}-character names",
                      {"controller_tags": [_controller_safety_tag(x, "DINT") for x in names]}))
    files.append(("safe_tag_dint_50_prog", f"{tag}: 50 SafetyProgram-scope DINT tags, no logic",
                  {"safety_tags": [_program_safety_tag(f"SafeDint_{i:03d}", "DINT") for i in range(50)]}))

    for mn in SHAPES:
        for n in (REAL_USE_COUNTS if mn in REAL_USE else (OTHER_COUNT,)):
            tags, rungs = instruction_pair(mn, n)
            low = mn.lower()
            files.append((f"safe_{low}_tags_{n}",
                          f"{tag}: {n} {SHAPES[mn][0]} backing tags for {mn}, no logic (control for safe_{low}_{n})",
                          {"safety_tags": tags}))
            files.append((f"safe_{low}_{n}",
                          f"{tag}: {n} {mn} rungs, one instruction each on its own {SHAPES[mn][0]} tag",
                          {"safety_tags": tags, "safety_rungs": rungs}))

    std_tags = [
        _program_safety_tag("SfIn", "BOOL", (256,)), _program_safety_tag("SfOut", "BOOL", (256,)),
        _program_safety_tag("SfTmr", "TIMER", (64,)),
        _program_safety_tag("SfDa", "DINT", (64,)), _program_safety_tag("SfDb", "DINT", (64,)),
        _program_safety_tag("SfRa", "REAL", (32,)), _program_safety_tag("SfRb", "REAL", (32,)),
        _program_safety_tag("SfRc", "REAL", (32,)),
    ]
    # The first build of these seven named a safety BOOL array `SIn`, which
    # Studio rejects as the SIN function; all seven failed conversion and none
    # was captured. Rebuilt under _r2 names, the old ones abandoned, so the
    # conversion and capture tooling treat them as new work.
    files.append(("safe_std_ctl_r2", f"{tag}: control for safe_std_*_r2 -- the safety arrays, no logic",
                  {"safety_tags": std_tags}))
    std_arms = [("xicote_10", 10, "XIC(SfIn[{i}])OTE(SfOut[{i}])"), ("xicote_50", 50, "XIC(SfIn[{i}])OTE(SfOut[{i}])"),
                ("xicote_200", 200, "XIC(SfIn[{i}])OTE(SfOut[{i}])"), ("ton_50", 50, "TON(SfTmr[{i}],1000,0)"),
                ("mov_50", 50, "MOV(SfDa[{i}],SfDb[{i}])"), ("atan2_20", 20, "ATAN2(SfRa[{i}],SfRb[{i}],SfRc[{i}])")]
    for suffix, n, call in std_arms:
        files.append((f"safe_std_{suffix}_r2", f"{tag}: {n} rungs of {call.split('(')[0]} in the safety routine "
                      f"on safety arrays", {"safety_tags": std_tags,
                                            "safety_rungs": [call.format(i=i) + ";" for i in range(n)]}))

    ref_tags = [_controller_safety_tag("SRefIn", "BOOL", (256,)), tag_xml("StdRefOut", "BOOL", dimensions=(256,))]
    files.append(("safe_ref_ctl", f"{tag}: control for safe_ref_* -- a Class=Safety BOOL[256] and a standard "
                  f"BOOL[256], no logic", {"controller_tags": ref_tags}))
    for n in (10, 50, 200):
        files.append((f"safe_ref_{n}", f"{tag}: {n} standard MainRoutine rungs XIC(safety BOOL)OTE(standard BOOL)",
                      {"controller_tags": ref_tags,
                       "standard_rungs": [f"XIC(SRefIn[{i}])OTE(StdRefOut[{i}]);" for i in range(n)]}))
    return files


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", metavar="REGEX",
                    help="build only the sample_ids this matches; a full rebuild restamps every "
                         "file's dates and queues the captured ones for reconversion")
    args = ap.parse_args()
    check_shapes()
    for sample_id, description, kwargs in plan():
        if args.only and not re.search(args.only, sample_id):
            continue
        out = OUT_ROOT / f"{sample_id}.L5X"
        predicted = write_sample(build(sample_id, **kwargs), out)
        append_manifest_row(sample_id, description, CATEGORY, out, predicted)
        print(f"{sample_id}: predicted {predicted:,}")


if __name__ == "__main__":
    main()
