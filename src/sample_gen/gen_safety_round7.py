"""OQ-SAFETYLOGICIO, safety batch B (the last of two, TASKS 0zd): the content only RS-02 /
RS-03 / RS-17 carry in the safety partition, one candidate per family, and a realistic
mixed-rung family for the per-rung residual every real safety program shows.

A census of every real safety program (scripts/safety_census.py) bounds module-tag
operands in ordinary safety instructions at ~1.4 bytes each; what is left on those three
is content nothing has measured (OPEN_QUESTIONS Section 8). Each file below states the
control it differences against; every AOI is the project's own design.

1756-L81ES v35 on the realism plant with the safety task (gen_safety_round2.build):

  A  safe_aoiarg_a8_inst20       a safety AOI with 8 Required BOOL parameters (6 in, 2 out),
                                 20 program instances and its operand arrays, no calls
     safe_aoiarg_a8tag_5 / _20   and 5 / 20 calls on safety program BOOL elements: the
                                 per-call slope against safe_aoi_call_*'s two operands
     safe_aoiarg_p16_inst20      a safety AOI with 16 parameters, 2 Required, 20 instances
     safe_aoiarg_p16_call20      and 20 calls of its 2 operands: per parameter or per operand
     safe_aoiarg_a8mod_ctl       (local) a8_inst20 and a 2198-D012-ERS3 with integrated
                                 safety, its axes and bus, no calls
     safe_aoiarg_a8mod_20        (local) and 20 calls: five operands the drive's SI members,
                                 two its SO members, one a program BOOL
  B  safe_aoitmr_def             a safety AOI with 12 BOOL and 2 DINT parameters, a BOOL and
                                 four TIMER locals, eight rungs of TON / TOF / ONS / MOV
     safe_aoitmr_inst20          and 20 program instances, no calls (instance layout)
  C  safe_par_local50            50 safety program BOOLs, no Usage
     safe_par_public50 / _output50 / _input50   the same 50 as Public / Output / Input
     safe_par_aoiout20           safe_aoitmr_inst20 with its instances Usage="Output"
  D  safe_desc_ctl50_l50 / _l200 safe_tag_bool_50's 50 tags, each with a 50 / 200-character
                                 description
     safe_desc_prg50_l200        safe_par_local50's 50 with 200-character descriptions
  E  safe_dcs_chain5x4           safe_dcs_20's 20 DCS as 4 rungs of 5 chained
  F  safe_rtn_idle_dcs20         safe_dcs_20's 20 rungs in a safety routine nothing calls
  G  safe_op_ctl_100 / _slot_100 a 1734-IB8S/B without a module name in a further rack; 100
                                 rungs reading program BOOLs / its points by slot path
  H  safe_mix_ctl                a program tag pool for mixed rungs, no logic
     safe_mix_50 / _100          50 / 100 rungs mixing the shapes real safety routines use
     safe_mix_100_cmt            safe_mix_100 with a comment on every rung

and the v32 baseline on content (firmware-matrix exemption: SafeBase):

  safe_base_5069l320_v32         the safety File > New shell on 5069-L320ERMS2 v32 on the
                                 plant, against safe_base_5069l320_v35

The two drive files use the integrated-safety drive template from samples/local (the
2026-10-19 exception route): built into samples/local/safety_io/ and captured from
samples/generated/safety/.

Run: python -m sample_gen.gen_safety_round7 [--local] [--only REGEX]
"""

from __future__ import annotations

import argparse
import json
import re

from sample_gen import gen_safety_io as IO
from sample_gen import gen_safety_partition as G
from sample_gen import gen_safety_round2 as R
from sample_gen import gen_safety_round4 as R4
from sample_gen.builders import MemberSpec, aoi_xml, program_tag_xml, rung_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.predefined_members import predef_member

OQ = "OQ-SAFETYLOGICIO"


def _safety_class(xml: str, name: str) -> str:
    return xml.replace(f'<AddOnInstructionDefinition Name="{name}"',
                       f'<AddOnInstructionDefinition Name="{name}" Class="Safety"', 1)


def _rungs(rungs: list[str]) -> str:
    return "\n".join(rung_xml(i, r) for i, r in enumerate(rungs))


# --- A: a safety AOI call's operands ---------------------------------------------------------

ARG8 = "SafeArg8"


def arg8_aoi() -> tuple[str, list[MemberSpec]]:
    """8 Required BOOL parameters, 6 in and 2 out, two rungs."""
    ins = [MemberSpec(f"In{k}", "BOOL", required=True) for k in range(1, 7)]
    outs = [MemberSpec(f"Out{k}", "BOOL", required=True) for k in (1, 2)]
    xml, storage = aoi_xml(ARG8, input_params=ins, output_params=outs, logic_rungs_xml=_rungs(
        ["XIC(In1)XIC(In2)XIC(In3)OTE(Out1);", "XIC(In4)XIO(In5)XIC(In6)OTE(Out2);"]))
    return _safety_class(xml, ARG8), storage


P16 = "SafeArgP16"


def p16_aoi() -> tuple[str, list[MemberSpec]]:
    """16 parameters with EnableIn / EnableOut, 2 of them Required: InA and OutQ as
    SafeAoiA's, ten more BOOLs and two DINTs that a call does not pass."""
    ins = ([MemberSpec("InA", "BOOL", required=True)] + [MemberSpec(f"InX{k}", "BOOL") for k in range(6)]
           + [MemberSpec("PresetA", "DINT"), MemberSpec("PresetB", "DINT")])
    outs = [MemberSpec("OutQ", "BOOL", required=True)] + [MemberSpec(f"OutX{k}", "BOOL") for k in range(4)]
    xml, storage = aoi_xml(P16, input_params=ins, output_params=outs,
                           logic_rungs_xml=_rungs(["XIC(InA)OTE(OutQ);"]))
    return _safety_class(xml, P16), storage


def _instances(aoi: str, storage: list[MemberSpec], n: int, usage: str | None = None) -> list[str]:
    tags = [R.prog_tag(f"{aoi}_{i:03d}", aoi, udt_members=storage) for i in range(n)]
    if usage:
        tags = [t.replace(f'DataType="{aoi}"', f'DataType="{aoi}" Usage="{usage}"', 1)
                 .replace('ExternalAccess="Read Only"', 'ExternalAccess="Read/Write"', 1) for t in tags]
    return tags


ARG_IN, ARG_OUT = R.prog_tag("AgIn", "BOOL", (128,)), R.prog_tag("AgOut", "BOOL", (64,))


def arg8_calls(n: int, module: str | None = None, so_members: list[str] = ()) -> list[str]:
    """n calls, each instance its own; operands distinct BOOL elements, or with a drive,
    five of its SI members, one program BOOL and two of its SO members, every
    destination distinct."""
    calls = []
    for i in range(n):
        if module is None:
            args = [f"AgIn[{6 * i + k}]" for k in range(6)] + [f"AgOut[{2 * i + k}]" for k in range(2)]
        else:
            args = ([f"{module}:SI.{m}" for m in ("RunMode", "ConnectionFaulted", "STOActive1", "SafetyFault1",
                                                    "TorqueDisabled1")]
                    + [f"AgIn[{i}]"] + [f"{module}:SO.{m}" for m in so_members[2 * i: 2 * i + 2]])
        calls.append(f"{ARG8}({ARG8}_{i:03d},{','.join(args)});")
    return calls


# --- B: timers inside a safety AOI ---------------------------------------------------------------

TMR = "SafeTmrAoi"


def tmr_aoi() -> tuple[str, list[MemberSpec]]:
    ins = ([MemberSpec(n, "BOOL", required=True) for n in ("InRun", "InFault", "InFeedback", "InReset")]
           + [MemberSpec(n, "BOOL", visible=True) for n in ("InEnable", "InAux")]
           + [MemberSpec("PresetA", "DINT", visible=True), MemberSpec("PresetB", "DINT", visible=True)])
    outs = ([MemberSpec(n, "BOOL", required=True) for n in ("OutReady", "OutAlarm")]
            + [MemberSpec(n, "BOOL", visible=True) for n in ("OutActive", "OutRequest", "OutDone", "OutAux")])
    locs = [MemberSpec("LocOneShot", "BOOL")] + [predef_member(f"Tmr{k}", "TIMER") for k in "ABCD"]
    rungs = ["XIC(InEnable)MOV(PresetA,TmrA.PRE)MOV(PresetB,TmrB.PRE);",
             "XIC(InRun)XIO(InFault)TON(TmrA,?,?);",
             "XIC(TmrA.DN)TOF(TmrB,?,?);",
             "XIC(TmrB.DN)OTE(OutReady);",
             "XIC(OutReady)XIC(InFeedback)TON(TmrC,?,?);",
             "XIC(TmrC.DN)OTE(OutActive);",
             "[XIC(InFault) ONS(LocOneShot) ,XIC(TmrD.DN) ]OTE(OutAlarm);",
             "XIC(InReset)TON(TmrD,?,?);"]
    xml, storage = aoi_xml(TMR, input_params=ins, output_params=outs, local_tags=locs, logic_rungs_xml=_rungs(rungs))
    return _safety_class(xml, TMR), storage


# --- C, D: program parameters and descriptions -----------------------------------------------------

def _filler(i: int, length: int) -> str:
    """A distinct description of exactly `length` characters."""
    text = f"Zone {i:03d} safety input, dual channel, reset at the operator station. "
    return (text * (length // len(text) + 1))[:length]


def par_tags(usage: str | None, desc: int = 0) -> list[str]:
    out = []
    for i in range(50):
        xml = program_tag_xml(f"ParBool_{i:03d}", "BOOL", usage)
        if desc:
            xml = xml.replace(">\n", f">\n        <Description><![CDATA[{_filler(i, desc)}]]></Description>\n", 1)
        out.append(xml)
    return out


def desc_ctl_tags(length: int) -> list[str]:
    """safe_tag_bool_50's tags (names and form) with a description each."""
    return [tag_xml(f"SafeBool_{i:03d}", "BOOL", description=_filler(i, length)).replace(
        f'<Tag Name="SafeBool_{i:03d}"', f'<Tag Name="SafeBool_{i:03d}" Class="Safety"', 1) for i in range(50)]


# --- G: a safety card's points by slot path -------------------------------------------------------

RACK = "SRACK_1"


def slot_rack() -> list[str]:
    """A further 1734-AENTR/C with one 1734-IB8S/B in slot 1 and no module name: its tags
    are SRACK_1:1:I, the spelling the real programs use for unnamed cards."""
    return [IO.adapter(RACK, "192.168.1.200", 1), IO.place(IO.TEMPLATES["ib8s"], None, RACK, "1", 1, IO.RACK_SNN[0])]


OP_POOL = [R.prog_tag("OpB", "BOOL", (128,)), R.prog_tag("OpO", "BOOL", (128,))]


# --- H: mixed rungs --------------------------------------------------------------------------------

MIX_DCS = 13


def mix_pool() -> list[str]:
    p = R.prog_tag
    tags = [p("MxB", "BOOL", (512,)), p("MxO", "BOOL", (128,)), p("MxS", "BOOL", (128,)),
            p("MxD", "DINT", (64,)), p("MxT", "TIMER", (128,))]
    return tags + [G._studio_tag(f"MxDcs_{k:03d}", "DCI_STOP", controller_scope=False) for k in range(MIX_DCS)]


def mix_rung(i: int) -> str:
    """Rung i of the mixed family: eight shapes real safety routines use, in turn, every
    output distinct (own design, built from instruction signatures)."""
    a, b, e, f = 4 * i, 4 * i + 1, 4 * i + 2, 4 * i + 3
    k = i // 8
    shape = i % 8
    if shape == 0:
        t = f"MxDcs_{k:03d}"
        return (f"XIC(MxB[{a}])[OTE(MxO[{i}]) ,DCS({t},EMERGENCY STOP,EQUIVALENT - ACTIVE HIGH,500,MANUAL,MANUAL,"
                f"{t}.ChannelA,{t}.ChannelB,{t}.InputStatus,{t}.Reset) ];")
    if shape == 1:
        return f"XIC(MxB[{a}])XIO(MxB[{b}])[OTE(MxO[{i}]) ,TON(MxT[{i}],500,0) ];"
    if shape == 2:
        return f"[XIC(MxB[{a}]) ,XIC(MxO[{i}]) ]XIO(MxB[{b}])OTE(MxO[{i}]);"
    if shape == 3:
        return f"XIC(MxT[{i - 2}].DN)ONS(MxS[{i}])OTL(MxO[{i}]);"
    if shape == 4:
        return f"XIC(MxB[{a}])MOV(MxD[{k}],MxD[{32 + k}]);"
    if shape == 5:
        return f"XIC(MxB[{a}])XIC(MxB[{b}])XIO(MxB[{e}])XIC(MxB[{f}])OTE(MxO[{i}]);"
    if shape == 6:
        return f"[XIC(MxB[{a}]) XIO(MxB[{b}]) ,XIC(MxB[{e}]) ]OTU(MxO[{i}]);"
    return f"EQU(MxD[{k}],5)OTE(MxO[{i}]);"


def mix_comment(i: int) -> str:
    return (f"Rung {i:03d}: guard door and e-stop chain for the cell, reset from the operator station."
            + " " * 60)[:60]


# --- the roster ------------------------------------------------------------------------------------

def plan() -> list[tuple[str, str, dict]]:
    arg8, arg8_store = arg8_aoi()
    p16, p16_store = p16_aoi()
    tmr, tmr_store = tmr_aoi()
    a8_tags = _instances(ARG8, arg8_store, 20) + [ARG_IN, ARG_OUT]
    p16_tags = _instances(P16, p16_store, 20) + [R.prog_tag("AiIn", "BOOL", (32,)), R.prog_tag("AiOut", "BOOL", (32,))]
    p16_calls = [f"{P16}({P16}_{i:03d},AiIn[{i}],AiOut[{i}]);" for i in range(20)]
    dcs_tags, dcs_rungs = G.instruction_pair("DCS", 20)
    chained = ["".join(r.rstrip(";") for r in dcs_rungs[5 * k: 5 * k + 5]) + ";" for k in range(4)]
    files = [
        ("safe_aoiarg_a8_inst20", "a safety AOI with 8 Required BOOL parameters (6 in, 2 out), 20 SafetyProgram "
         "instances and its operand arrays, no calls; against safe_n00", {"aoi": arg8, "tags": a8_tags}),
        ("safe_aoiarg_a8tag_5", "the same and 5 calls, operands on safety program BOOL elements",
         {"aoi": arg8, "tags": a8_tags, "rungs": arg8_calls(5)}),
        ("safe_aoiarg_a8tag_20", "the same and 20 calls: the per-call slope against safe_aoi_call_*'s two operands",
         {"aoi": arg8, "tags": a8_tags, "rungs": arg8_calls(20)}),
        ("safe_aoiarg_p16_inst20", "a safety AOI with 16 parameters, 2 Required (InA, OutQ), 20 instances, no calls",
         {"aoi": p16, "tags": p16_tags}),
        ("safe_aoiarg_p16_call20", "the same and 20 calls of its 2 operands, as safe_aoi_call_20 calls SafeAoiA",
         {"aoi": p16, "tags": p16_tags, "rungs": p16_calls}),
        ("safe_aoitmr_def", "a safety AOI with 12 BOOL and 2 DINT parameters, a BOOL and four TIMER locals, eight "
         "rungs of TON / TOF / ONS / MOV / XIC / XIO / OTE, no instances; against safe_n00", {"aoi": tmr}),
        ("safe_aoitmr_inst20", "the same and 20 SafetyProgram instances, no calls (instance layout)",
         {"aoi": tmr, "tags": _instances(TMR, tmr_store, 20)}),
        ("safe_par_aoiout20", "safe_aoitmr_inst20 with its 20 instances Usage=\"Output\" (program parameters)",
         {"aoi": tmr, "tags": _instances(TMR, tmr_store, 20, "Output")}),
        ("safe_par_local50", "50 SafetyProgram BOOLs, no Usage, Read/Write; against safe_n00",
         {"tags": par_tags(None)}),
        ("safe_par_public50", "safe_par_local50's 50 as Usage=\"Public\"", {"tags": par_tags("Public")}),
        ("safe_par_output50", "safe_par_local50's 50 as Usage=\"Output\"", {"tags": par_tags("Output")}),
        ("safe_par_input50", "safe_par_local50's 50 as Usage=\"Input\"", {"tags": par_tags("Input")}),
        ("safe_desc_prg50_l200", "safe_par_local50's 50, each with a 200-character description",
         {"tags": par_tags(None, desc=200)}),
        ("safe_desc_ctl50_l50", "safe_tag_bool_50's 50 controller-scope safety BOOLs, each with a 50-character "
         "description", {"controller_tags": desc_ctl_tags(50)}),
        ("safe_desc_ctl50_l200", "the same with 200-character descriptions", {"controller_tags": desc_ctl_tags(200)}),
        ("safe_dcs_chain5x4", "safe_dcs_20's 20 DCS as 4 rungs of 5 chained, nothing else; against safe_dcs_20",
         {"tags": dcs_tags, "rungs": chained}),
        ("safe_rtn_idle_dcs20", "safe_dcs_20's 20 DCS rungs in a safety routine nothing calls; against safe_dcs_20 "
         "and the routine shell", {"tags": dcs_tags, "subs": [("IdleDcs", dcs_rungs)]}),
        ("safe_op_ctl_100", "a 1734-IB8S/B without a module name in a further rack; 100 rungs XIC(OpB[i]) "
         "OTE(OpO[i])", {"tags": OP_POOL, "rungs": [f"XIC(OpB[{i}])OTE(OpO[{i}]);" for i in range(100)],
                         "modules": "slot"}),
        ("safe_op_slot_100", "the same card; 100 rungs reading its points by slot path, XIC(SRACK_1:1:I.PtnnData) "
         "OTE(OpO[i])", {"tags": OP_POOL, "modules": "slot",
                         "rungs": [f"XIC({RACK}:1:I.Pt{i % 8:02d}Data)OTE(OpO[{i}]);" for i in range(100)]}),
        ("safe_mix_ctl", "the mixed-rung tag pool, no logic; control for safe_mix_*", {"tags": mix_pool()}),
        ("safe_mix_50", "50 rungs mixing eight shapes real safety routines use (DCS beside XIC / OTE in a branch, "
         "TON in a branch, seal-in, ONS / OTL, MOV, four in series, OTU after a branch, EQU)",
         {"tags": mix_pool(), "rungs": [mix_rung(i) for i in range(50)]}),
        ("safe_mix_100", "the same at 100 rungs", {"tags": mix_pool(), "rungs": [mix_rung(i) for i in range(100)]}),
        ("safe_mix_100_cmt", "safe_mix_100 with a 60-character comment on every rung",
         {"tags": mix_pool(), "rungs": [mix_rung(i) for i in range(100)], "comments": True}),
        ("safe_base_5069l320_v32", "the safety File > New shell on 5069-L320ERMS2 v32 on the plant, against "
         "safe_base_5069l320_v35 (the v32 baseline on content, TASKS 0zd Part 4)", {"base_v32": True}),
    ]
    return [(sid, f"{OQ}: {desc}", kw) for sid, desc, kw in files]


def local_plan() -> list[tuple[str, str, dict]]:
    arg8, arg8_store = arg8_aoi()
    a8_tags = _instances(ARG8, arg8_store, 20) + [ARG_IN, ARG_OUT]
    files = [
        ("safe_aoiarg_a8mod_ctl", "safe_aoiarg_a8_inst20 and a 2198-D012-ERS3 with integrated safety, its two "
         "axes and the proven 2198-P208 bus, no calls", {"aoi": arg8, "tags": a8_tags}),
        ("safe_aoiarg_a8mod_20", "the same and 20 calls: five operands the drive's SI members, one a program BOOL, "
         "two its SO members (every one distinct); against safe_aoiarg_a8mod_ctl and safe_aoiarg_a8tag_20",
         {"aoi": arg8, "tags": a8_tags, "drive_calls": 20}),
    ]
    return [(sid, f"{OQ}: {desc}", kw) for sid, desc, kw in files]


def _so_members() -> list[str]:
    """The D012's SO BOOL members (its local template), in order."""
    block = json.loads(IO.LOCAL_BLOCKS.read_text(encoding="utf-8"))["2198d012s"]
    so = re.search(r'<Structure DataType="AB:CIP_Motion_Device_Safety2:SO:0">(.*?)</Structure>', block, re.S).group(1)
    return re.findall(r'<DataValueMember Name="([^"]+)" DataType="BOOL"', so)


def make(sample_id: str, kw: dict) -> str:
    if kw.get("base_v32"):
        return R4.build_base("SafeBase5069l320V32", "5069-L320ERMS2", "32", "32.04", content=False)
    rungs = list(kw.get("rungs", []))
    if kw.get("drive_calls"):
        rungs = arg8_calls(kw["drive_calls"], "Drv1", _so_members())
    program = R.main_program(kw.get("tags", []), rungs, kw.get("subs", []))
    l5x = R.build(sample_id, controller_tags=kw.get("controller_tags", []), programs=[program],
                  aoi_defs_xml=kw.get("aoi", ""))
    if kw.get("comments"):
        # Only the safety program's rungs: the plant's own programs number theirs from 0 too.
        start = l5x.index(f'<Program Name="{R.MAIN}"')
        end = l5x.index("</Program>", start)
        seg = l5x[start:end]
        for i in range(len(rungs)):
            old = f'<Rung Number="{i}" Type="N">\n                <Text>'
            assert seg.count(old) == 1, (sample_id, i)
            seg = seg.replace(old, f'<Rung Number="{i}" Type="N">\n                <Comment><![CDATA[{mix_comment(i)}]]>'
                                   f'</Comment>\n                <Text>', 1)
        l5x = l5x[:start] + seg + l5x[end:]
    if kw.get("modules") == "slot":
        l5x = IO.with_modules(l5x, slot_rack())
    return l5x


def local_make(sample_id: str, kw: dict) -> str:
    """make()'s file with one 2198-D012-ERS3 with integrated safety, as gen_safety_io builds
    safe_iol_kx_d012_saf_1: the proven bus, its converter axis, the motion group, two axes."""
    from sample_gen.gen_module_motion import _MOTION_GROUP_TAG_XML, _axis_tag, bus_supply_with_converter
    l5x = make(sample_id, kw)
    snn = IO.local_snn(l5x, "2")
    supply, converter = bus_supply_with_converter(name="Bus_Supply", address="192.168.1.10",
                                                  axis_name="Bus_Converter_Axis")
    drive = IO._motion_rpi(IO.local_block("2198d012s", "Drv1", "Local", "2", "192.168.1.20", snn))
    axes = [_MOTION_GROUP_TAG_XML, converter] + [_axis_tag(f"Drv1_{ch}_Axis", f"Drv1:{ch}")
                                                 for ch in IO.AXIS_CHANNELS["2198-D012-ERS3"]]
    return IO.with_tags(IO.with_modules(l5x, [supply, drive]), axes)


def _make(job: tuple[str, dict]) -> int:
    sample_id, kw = job
    return write_sample(make(sample_id, kw), G.OUT_ROOT / f"{sample_id}.L5X")


def _make_local(job: tuple[str, dict]) -> int:
    sample_id, kw = job
    return write_sample(local_make(sample_id, kw), IO.LOCAL_OUT / f"{sample_id}.L5X")


def main(argv: list[str] | None = None) -> None:
    from sample_gen.progress import run
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", metavar="REGEX", help="build only the sample_ids this matches")
    ap.add_argument("--local", action="store_true",
                    help="build the drive files into samples/local/safety_io/ (needs the templates there)")
    args = ap.parse_args([] if argv is None else argv)
    roster, build = (local_plan(), _make_local) if args.local else (plan(), _make)
    jobs = [(sid, desc, kw) for sid, desc, kw in roster if not args.only or re.search(args.only, sid)]
    predicted = run(((sid, (sid, kw)) for sid, _, kw in jobs), build, label="safety-r7")
    # A local file is captured from samples/generated/safety/ (CLAUDE.md exception), so its
    # spec row names that path, as gen_safety_io's do.
    for sample_id, description, _ in jobs:
        append_manifest_row(sample_id, description, G.CATEGORY, G.OUT_ROOT / f"{sample_id}.L5X", predicted[sample_id])


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
