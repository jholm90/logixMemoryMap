"""OQ-SAFETYPARTITION, round 2: whole safety programs, safety tags at both scopes.

Round 1 (gen_safety_partition.py, 112 files captured) fixed the laws for scalar safety
tags, the safety-instruction backing structures and one rung per safety instruction. This
round tests every other shape a real safety program has, each at controller and program
scope where both exist, and ends with four whole safety programs predicted blind.

Same platform, plant and builder as round 1 (1756-L81ES v35, SIL2/PLd, the File > New
SafetyTask/SafetyProgram/MainRoutine on the realism floor), so every file differences
against round 1's captured safe_n00 or a control in its own family. Spec: TASKS 0u.

  safe_ptag_dint_50_len<k>       50 safety-program DINTs, names of 4/8/16/24/40 characters
  safe_arr_<shape>_<ctl|prog>    20 safety arrays of one shape, controller or program scope
  safe_struct_<type>_<ctl|prog>  20 TIMER / COUNTER / CONTROL / LINT safety tags
  safe_udt_<s|l>_<def|ctl20|prog20>  a 12- and a 40-byte safety UDT: definition, then tags
  safe_alias_*                   20 aliases: controller -> controller, program -> controller,
                                 program -> program, beside the targets alone
  safe_rtn_<jsr|idle>_<n>        JSR-called and uncalled safety subroutines
  safe_prg_*                     extra safety programs, a long name, tags in a second one
  safe_<estop|rin>_<form>_20     operands and backing tags in other places, each with its
                                 tags-only file
  safe_sref_*                    standard logic reading safety tags, and its all-standard twin
  safe_comp_<1..4>               whole safety programs, both partitions predicted blind

Run: python -m sample_gen.gen_safety_round2 [--only REGEX]
"""

from __future__ import annotations

import argparse
import re
import xml.etree.ElementTree as ET

from sample_gen import gen_safety_partition as G
from sample_gen.builders import MemberSpec, alias_tag_xml, rung_xml, tag_xml, udt_xml, validate_logix_name
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.realism import with_baseline
from sample_gen.wrapper import build_l5x

OQ = "OQ-SAFETYPARTITION"
MAIN = "SafetyProgram"

UDT_S = ("SafeUdtS", [MemberSpec("D", "DINT"), MemberSpec("R", "REAL"),
                      MemberSpec("B1", "BOOL"), MemberSpec("B2", "BOOL")])
UDT_L = ("SafeUdtL", [MemberSpec(f"D{k}", "DINT") for k in range(10)])


# --- builders ------------------------------------------------------------------------

def ctl_tag(name: str, data_type: str, dims: tuple[int, ...] = (), **kw) -> str:
    """A controller-scope safety tag (Class="Safety", as round 1 and the seeds)."""
    return tag_xml(name, data_type, dimensions=dims, **kw).replace(
        f'<Tag Name="{name}"', f'<Tag Name="{name}" Class="Safety"', 1)


def prog_tag(name: str, data_type: str, dims: tuple[int, ...] = (), **kw) -> str:
    """A safety-program tag: no Class of its own, Read Only, as Studio writes it."""
    return tag_xml(name, data_type, dimensions=dims, **kw).replace(
        'ExternalAccess="Read/Write"', 'ExternalAccess="Read Only"', 1)


def ctl_alias(name: str, target: str) -> str:
    return alias_tag_xml(name, target).replace(f'<Tag Name="{name}"', f'<Tag Name="{name}" Class="Safety"', 1)


def _routine(name: str, rungs: list[str]) -> str:
    validate_logix_name(name, "routine")
    rungs_xml = "\n".join(rung_xml(i, r) for i, r in enumerate(rungs)) or rung_xml(0, "NOP();")
    return f'<Routine Name="{name}" Type="RLL">\n<RLLContent>\n{rungs_xml}\n</RLLContent>\n</Routine>'


def _program(name: str, tags: list[str], routines: list[tuple[str, list[str]]]) -> str:
    """A Class="Safety" program; the first routine is its main routine. With one routine
    this is byte-identical to round 1's _safety_program."""
    validate_logix_name(name, "program")
    return (f'<Program Name="{name}" TestEdits="false" MainRoutineName="{routines[0][0]}" '
            'Disabled="false" Class="Safety" UseAsFolder="false">\n<Tags>\n' + "\n".join(tags)
            + '\n</Tags>\n<Routines>\n' + "\n".join(_routine(n, r) for n, r in routines)
            + '\n</Routines>\n</Program>')


def _task(program_names: list[str]) -> str:
    """The safety task scheduling every safety program; round 1's _SAFETY_TASK for one."""
    return ('<Task Name="SafetyTask" Type="PERIODIC" Rate="20" Priority="10" Watchdog="20" '
            'DisableUpdateOutputs="false" InhibitTask="false" Class="Safety">\n<ScheduledPrograms>\n'
            + "\n".join(f'<ScheduledProgram Name="{p}"/>' for p in program_names)
            + '\n</ScheduledPrograms>\n</Task>')


Program = tuple[str, list[str], list[tuple[str, list[str]]]]


def build(sample_id: str, controller_tags: list[str] = (), programs: list[Program] | None = None,
          standard_rungs: list[str] = (), datatypes_xml: str = "") -> str:
    """Round 1's build, generalised to several safety programs and routines and to UDTs."""
    programs = programs or [(MAIN, [], [("MainRoutine", [])])]
    name = "SafePart" + "".join(w.capitalize() for w in sample_id.split("_")[1:])
    arm = {
        "extra_programs_xml": "\n".join(_program(*p) for p in programs),
        "extra_tasks_xml": _task([p[0] for p in programs]),
        "extra_rungs_xml": "\n".join(rung_xml(i, r) for i, r in enumerate(standard_rungs)),
        "tags_xml": "\n".join(controller_tags),
    }
    if datatypes_xml:
        arm["extra_datatypes_xml"] = datatypes_xml
    l5x = build_l5x(name, processor_type=G.PROCESSOR, safety_level="SIL2", **with_baseline(**arm))
    return l5x.replace('ConfigureSafetyIOAlways="true"', 'ConfigureSafetyIOAlways="false"', 1)


def main_program(tags: list[str] = (), rungs: list[str] = (), subs: list[tuple[str, list[str]]] = ()) -> Program:
    return (MAIN, list(tags), [("MainRoutine", list(rungs))] + list(subs))


# --- the roster --------------------------------------------------------------------------

ARRAY_SHAPES = (("dint2", "DINT", (2,)), ("dint3", "DINT", (3,)), ("dint64", "DINT", (64,)),
                ("int3", "INT", (3,)), ("sint10", "SINT", (10,)), ("real10", "REAL", (10,)),
                ("bool64", "BOOL", (64,)), ("bool96", "BOOL", (96,)), ("dint4x4", "DINT", (4, 4)),
                ("timer4", "TIMER", (4,)))
STRUCT_TYPES = ("TIMER", "COUNTER", "CONTROL", "LINT")


def _names(prefix: str, n: int) -> list[str]:
    """n names of 12 characters, the length round 1's tag sweeps used."""
    return [f"{prefix}{i:0{12 - len(prefix)}d}" for i in range(n)]


def _estop_forms(n: int) -> dict[str, tuple[list[str], list[str], list[str]]]:
    """form -> (controller tags, program tags, rungs) for ESTOP with its inputs elsewhere."""
    forms = {}
    backing = [G._studio_tag(f"ESTOP_{i:03d}", "EMERGENCY_STOP", controller_scope=False) for i in range(n)]
    ins = [[f"EsIn{k}_{i:03d}" for k in "ABCF"] for i in range(n)]
    rung = "ESTOP(ESTOP_{i:03d},MANUAL,{a},{b},{c},{f});"
    forms["opprog"] = ([], backing + [prog_tag(t, "BOOL") for row in ins for t in row],
                       [rung.format(i=i, a=r[0], b=r[1], c=r[2], f=r[3]) for i, r in enumerate(ins)])
    forms["opctl"] = ([ctl_tag(t, "BOOL") for row in ins for t in row], backing,
                      [rung.format(i=i, a=r[0], b=r[1], c=r[2], f=r[3]) for i, r in enumerate(ins)])
    width = 32 * -(-4 * n // 32)
    forms["oparr"] = ([], backing + [prog_tag("EsIn", "BOOL", (width,))],
                      [rung.format(i=i, a=f"EsIn[{4 * i}]", b=f"EsIn[{4 * i + 1}]", c=f"EsIn[{4 * i + 2}]",
                                   f=f"EsIn[{4 * i + 3}]") for i in range(n)])
    for mn, form in (("ESTOP", "estop_bctl"), ("RIN", "rin_bctl")):
        data_type, call = G.SHAPES[mn]
        tags = [G._studio_tag(f"{mn}_{i:03d}", data_type, controller_scope=True) for i in range(n)]
        forms[form] = (tags, [], [call.format(t=f"{mn}_{i:03d}") + ";" for i in range(n)])
    return forms


def _sref_tags() -> list[str]:
    return ([ctl_tag("SRefA", "BOOL", (64,)), ctl_tag("SRefB", "BOOL", (64,)), ctl_tag("SRefD", "DINT", (64,))]
            + [ctl_tag(f"SRefS{i:03d}", "BOOL") for i in range(50)]
            + [tag_xml("StdIn", "BOOL", dimensions=(64,)), tag_xml("StdOut", "BOOL", dimensions=(64,)),
               tag_xml("StdD", "DINT", dimensions=(64,))])


def _drive(prefix: str, mn: str, n: int, sfx: str) -> tuple[list[str], list[str]]:
    """n drive-safety instructions on their own backing and output tags, one shared SFX."""
    data_type, call = G.SHAPES[mn]
    tags, rungs = [], []
    for i in range(n):
        t = f"{prefix}{mn}_{i:02d}"
        tags.append(G._studio_tag(t, data_type, controller_scope=False))
        outs = {f"o{k}": f"{t}_O{k}" for k in range(G._outputs(call))}
        tags += [prog_tag(o, "BOOL") for o in outs.values()]
        rungs.append(call.format(t=t, sfx=sfx, **outs) + ";")
    return tags, rungs


def _instances(prefix: str, mn: str, n: int, controller: bool = False) -> tuple[list[str], list[str]]:
    data_type, call = G.SHAPES[mn]
    names = [f"{prefix}{mn}_{i:02d}" for i in range(n)]
    tags = [G._studio_tag(t, data_type, controller_scope=controller) for t in names]
    return tags, [call.format(t=t) + ";" for t in names]


def _composites() -> list[tuple[str, str, dict]]:
    """Four whole safety programs. Content only from shapes rounds 1 and 2 measure alone."""
    out = []
    udt_s, udt_l = udt_xml(*UDT_S), udt_xml(*UDT_L)

    # 1: a small cell. Two programs, ESTOP / RIN / ROUT on members, one subroutine each,
    # controller and program tags, a safety UDT, standard logic reading safety status.
    ctl = ([ctl_tag(f"CellOk{i:02d}", "BOOL") for i in range(16)] + [ctl_tag(f"CellDi{i:02d}", "DINT") for i in range(8)]
           + [ctl_tag("CellBits", "BOOL", (32,))]
           + [ctl_tag(f"CellU{i}", UDT_S[0], udt_members=UDT_S[1]) for i in range(4)]
           + [tag_xml("HmiOk", "BOOL", dimensions=(32,))])
    progs = []
    for p in range(2):
        pre = f"P{p}"
        t1, r1 = _instances(pre, "ESTOP", 3)
        t2, r2 = _instances(pre, "RIN", 2)
        t3, r3 = _instances(pre, "ROUT", 2)
        tags = t1 + t2 + t3 + [prog_tag(f"{pre}Flag{i:02d}", "BOOL") for i in range(10)] \
            + [prog_tag(f"{pre}Cnt{i}", "DINT") for i in range(4)] + [prog_tag(f"{pre}Ana", "REAL", (4,))]
        name = MAIN if p == 0 else "SafetyCell1"
        progs.append((name, tags, [("MainRoutine", r1 + ["JSR(Outputs,0);"]), ("Outputs", r2 + r3)]))
    std = [f"XIC(CellOk{i:02d})OTE(HmiOk[{i}]);" for i in range(10)]
    out.append(("safe_comp_1", "a small cell: 2 safety programs, 3 ESTOP, 2 RIN, 2 ROUT and a subroutine "
                "each, 16 BOOL / 8 DINT / BOOL[32] / 4 UDT controller safety tags, program BOOLs, DINTs "
                "and a REAL[4], 10 standard rungs reading safety BOOLs",
                {"controller_tags": ctl, "programs": progs, "standard_rungs": std, "datatypes_xml": udt_s}))

    # 2: three programs; ESTOP inputs as program BOOLs, LC, a 40-byte UDT in program
    # scope, aliases, standard MOV of safety DINTs.
    ctl = ([ctl_tag(f"ZoneSt{i:02d}", "DINT") for i in range(12)] + [ctl_tag(f"ZoneOk{i:02d}", "BOOL") for i in range(24)]
           + [ctl_alias(f"ZoneAl{i:02d}", f"ZoneOk{i:02d}") for i in range(4)]
           + [tag_xml("HmiSt", "DINT", dimensions=(12,)), tag_xml("HmiZone", "BOOL", dimensions=(32,))])
    progs = []
    for p in range(3):
        pre = f"Z{p}"
        n_e = (4, 2, 2)[p]
        ins = [[f"{pre}E{i}{k}" for k in "ABCF"] for i in range(n_e)]
        e_tags = [G._studio_tag(f"{pre}ESTOP_{i:02d}", "EMERGENCY_STOP", controller_scope=False) for i in range(n_e)]
        e_tags += [prog_tag(t, "BOOL") for row in ins for t in row]
        e_rungs = [f"ESTOP({pre}ESTOP_{i:02d},MANUAL,{r[0]},{r[1]},{r[2]},{r[3]});" for i, r in enumerate(ins)]
        t2, r2 = _instances(pre, "RIN", (2, 1, 1)[p])
        t3, r3 = _instances(pre, "ROUT", 2)
        t4, r4 = _instances(pre, "LC", 1 if p < 2 else 0)
        tags = e_tags + t2 + t3 + t4 + [prog_tag(f"{pre}Rec{i}", UDT_L[0], udt_members=UDT_L[1]) for i in range(2)] \
            + [prog_tag(f"{pre}Als{i}", "BOOL") for i in range(2)]
        tags += [alias_tag_xml(f"{pre}Map{i}", f"{pre}Als{i}") for i in range(2)]
        name = MAIN if p == 0 else f"SafetyZone{p}"
        progs.append((name, tags, [("MainRoutine", e_rungs + t_r(r2, r3, r4))]))
    std = [f"MOV(ZoneSt{i:02d},HmiSt[{i}]);" for i in range(12)] + [f"XIC(ZoneOk{i:02d})OTE(HmiZone[{i}]);" for i in range(20)]
    out.append(("safe_comp_2", "three safety programs: ESTOP inputs on program BOOLs, RIN, ROUT, LC, a 40-byte "
                "safety UDT in program scope, controller and program aliases, 12 standard MOVs of safety "
                "DINTs and 20 standard rungs reading safety BOOLs",
                {"controller_tags": ctl, "programs": progs, "standard_rungs": std, "datatypes_xml": udt_l}))

    # 3: a large line. Five programs, two subroutines each, every real-use instruction at
    # volume, safety arrays at both scopes, standard rungs with two safety operands.
    ctl = ([ctl_tag(f"LineArr{i:02d}", "DINT", (16,)) for i in range(10)] + [ctl_tag("LineA", "BOOL", (64,)),
           ctl_tag("LineB", "BOOL", (64,))] + [tag_xml("HmiLine", "BOOL", dimensions=(64,))])
    progs = []
    for p in range(5):
        pre = f"L{p}"
        t1, r1 = _instances(pre, "ESTOP", 6)
        t2, r2 = _instances(pre, "RIN", 4)
        t3, r3 = _instances(pre, "ROUT", 6)
        t4, r4 = _instances(pre, "LC", 2)
        t5, r5 = _instances(pre, "DCS", 1)
        tags = t1 + t2 + t3 + t4 + t5 + [prog_tag(f"{pre}Arr{i}", "DINT", (16,)) for i in range(2)] \
            + [prog_tag(f"{pre}Bits", "BOOL", (32,))]
        name = MAIN if p == 0 else f"SafetyLine{p}"
        progs.append((name, tags, [("MainRoutine", r1 + ["JSR(Inputs,0);", "JSR(Outputs,0);"]),
                                   ("Inputs", r2 + r4 + r5), ("Outputs", r3)]))
    std = [f"XIC(LineA[{i}])XIC(LineB[{i}])OTE(HmiLine[{i}]);" for i in range(50)]
    out.append(("safe_comp_3", "a large line: 5 safety programs with 2 subroutines each, 30 ESTOP, 20 RIN, "
                "30 ROUT, 10 LC, 5 DCS, DINT[16] safety arrays at both scopes, 50 standard rungs with two "
                "safety operands", {"controller_tags": ctl, "programs": progs, "standard_rungs": std}))

    # 4: drive safety. Two axes' worth of SFX / SS1 / SLS / SBC / SOS beside ESTOP and ROUT.
    progs = []
    for p in range(2):
        pre = f"A{p}"
        sfx = f"{pre}Sfx"
        tags = [G._studio_tag(sfx, "SAFETY_FEEDBACK_INTERFACE", controller_scope=False)]
        sfx_call = G.SHAPES["SFX"][1].format(t=sfx) + ";"
        rungs = [sfx_call]
        for mn, n in (("SS1", 2), ("SLS", 2), ("SBC", 2), ("SOS", 1)):
            t, r = _drive(pre, mn, n, sfx)
            tags += t
            rungs += r
        t1, r1 = _instances(pre, "ESTOP", 3)
        t3, r3 = _instances(pre, "ROUT", 3)
        tags += t1 + t3
        name = MAIN if p == 0 else "SafetyAxis1"
        progs.append((name, tags, [("MainRoutine", r1 + rungs + r3)]))
    out.append(("safe_comp_4", "drive safety: 2 safety programs, each an SFX with 2 SS1, 2 SLS, 2 SBC and 1 SOS "
                "on it, 3 ESTOP and 3 ROUT", {"programs": progs}))
    return out


def t_r(*rung_lists: list[str]) -> list[str]:
    return [r for rungs in rung_lists for r in rungs]


def plan() -> list[tuple[str, str, dict]]:
    files: list[tuple[str, str, dict]] = []

    for k in (4, 8, 16, 24, 40):
        tags = [prog_tag(n, "DINT") for n in G._padded_names("SafeDint", k, 50)]
        files.append((f"safe_ptag_dint_50_len{k}", f"50 SafetyProgram-scope DINTs, {k}-character names",
                      {"programs": [main_program(tags)]}))

    for label, typ, dims in ARRAY_SHAPES:
        shape = f"{typ}[{','.join(map(str, dims))}]"
        files.append((f"safe_arr_{label}_ctl", f"20 controller-scope safety {shape}",
                      {"controller_tags": [ctl_tag(n, typ, dims) for n in _names("SafeArr", 20)]}))
        files.append((f"safe_arr_{label}_prog", f"20 SafetyProgram-scope {shape}",
                      {"programs": [main_program([prog_tag(n, typ, dims) for n in _names("SafeArr", 20)])]}))

    for typ in STRUCT_TYPES:
        files.append((f"safe_struct_{typ.lower()}_ctl", f"20 controller-scope safety {typ}",
                      {"controller_tags": [ctl_tag(n, typ) for n in _names("SafeStr", 20)]}))
        files.append((f"safe_struct_{typ.lower()}_prog", f"20 SafetyProgram-scope {typ}",
                      {"programs": [main_program([prog_tag(n, typ) for n in _names("SafeStr", 20)])]}))

    for size, (udt, members) in (("s", UDT_S), ("l", UDT_L)):
        dt = udt_xml(udt, members)
        files.append((f"safe_udt_{size}_def", f"the {udt} definition alone, no tags", {"datatypes_xml": dt}))
        files.append((f"safe_udt_{size}_ctl20", f"{udt} and 20 controller-scope safety tags of it",
                      {"datatypes_xml": dt,
                       "controller_tags": [ctl_tag(n, udt, udt_members=members) for n in _names("SafeUdt", 20)]}))
        files.append((f"safe_udt_{size}_prog20", f"{udt} and 20 SafetyProgram-scope tags of it",
                      {"datatypes_xml": dt, "programs": [main_program(
                          [prog_tag(n, udt, udt_members=members) for n in _names("SafeUdt", 20)])]}))

    targets, aliases = _names("SafeTgt", 20), _names("SafeAls", 20)
    ctl_targets = [ctl_tag(n, "DINT") for n in targets]
    prog_targets = [prog_tag(n, "DINT") for n in targets]
    files.append(("safe_alias_tctl", "control: 20 controller-scope safety DINTs, the alias targets",
                  {"controller_tags": ctl_targets}))
    files.append(("safe_alias_tctl_actl", "the 20 controller targets and 20 controller-scope aliases of them",
                  {"controller_tags": ctl_targets + [ctl_alias(a, t) for a, t in zip(aliases, targets)]}))
    files.append(("safe_alias_tctl_aprog", "the 20 controller targets and 20 SafetyProgram-scope aliases of them",
                  {"controller_tags": ctl_targets,
                   "programs": [main_program([alias_tag_xml(a, t) for a, t in zip(aliases, targets)])]}))
    files.append(("safe_alias_tprog", "control: 20 SafetyProgram-scope DINTs, the alias targets",
                  {"programs": [main_program(prog_targets)]}))
    files.append(("safe_alias_tprog_aprog", "the 20 program targets and 20 SafetyProgram-scope aliases of them",
                  {"programs": [main_program(prog_targets + [alias_tag_xml(a, t) for a, t in zip(aliases, targets)])]}))

    for n in (1, 2, 5, 10):
        subs = [(f"SubRtn{j:02d}", []) for j in range(1, n + 1)]
        files.append((f"safe_rtn_jsr_{n}", f"{n} safety subroutine(s), one NOP each, each JSR-called from MainRoutine",
                      {"programs": [main_program(rungs=[f"JSR({s},0);" for s, _ in subs], subs=subs)]}))
    for n in (1, 5):
        subs = [(f"SubRtn{j:02d}", []) for j in range(1, n + 1)]
        files.append((f"safe_rtn_idle_{n}", f"{n} uncalled safety routine(s), one NOP each",
                      {"programs": [main_program(subs=subs)]}))

    for n in (2, 3, 5):
        extra = [(f"SafetyPrg{j:02d}", [], [("MainRoutine", [])]) for j in range(2, n + 1)]
        files.append((f"safe_prg_{n}", f"{n} safety programs in SafetyTask, each a MainRoutine with one NOP",
                      {"programs": [main_program()] + extra}))
    long_name = "SafetyPrg" + "X" * 29 + "02"
    files.append(("safe_prg_2_len40", "2 safety programs, the second named with 40 characters",
                  {"programs": [main_program(), (long_name, [], [("MainRoutine", [])])]}))
    files.append(("safe_prg_2_tags50", "2 safety programs, 50 DINTs in the second program's scope",
                  {"programs": [main_program(), ("SafetyPrg02", [prog_tag(n, "DINT") for n in _names("SafeDint", 50)],
                                                 [("MainRoutine", [])])]}))

    for form, (ctl, prog, rungs) in _estop_forms(20).items():
        mn, rest = ("rin", "bctl") if form == "rin_bctl" else ("estop", form.replace("estop_", ""))
        what = {"opprog": "ESTOP inputs on SafetyProgram BOOLs", "opctl": "ESTOP inputs on controller safety BOOLs",
                "oparr": "ESTOP inputs on SafetyProgram BOOL-array elements",
                "bctl": f"{mn.upper()} backing tags at controller scope, inputs on their members"}[rest]
        files.append((f"safe_{mn}_{rest}_tags_20", f"{what}: the tags alone",
                      {"controller_tags": ctl, "programs": [main_program(prog)]}))
        files.append((f"safe_{mn}_{rest}_20", f"{what}: the tags and 20 rungs",
                      {"controller_tags": ctl, "programs": [main_program(prog, rungs)]}))

    ref = _sref_tags()
    files.append(("safe_sref_ctl", "control for safe_sref_*: safety BOOL[64] x2, DINT[64], 50 scalar BOOLs; "
                  "standard BOOL[64] x2, DINT[64]", {"controller_tags": ref}))
    for sid, what, rung in (
            ("safe_sref_two_50", "two safety operands", "XIC(SRefA[{i}])XIC(SRefB[{i}])OTE(StdOut[{i}]);"),
            ("safe_sref_scalar_50", "a scalar safety BOOL", "XIC(SRefS{i:03d})OTE(StdOut[{i}]);"),
            ("safe_sref_mov_50", "MOV from a safety DINT", "MOV(SRefD[{i}],StdD[{i}]);"),
            ("safe_sref_std_50", "the all-standard twin", "XIC(StdIn[{i}])OTE(StdOut[{i}]);")):
        files.append((sid, f"50 standard MainRoutine rungs, {what}",
                      {"controller_tags": ref, "standard_rungs": [rung.format(i=i) for i in range(50)]}))

    files += _composites()
    return [(sid, f"{OQ}: {desc}", kw) for sid, desc, kw in files]


def predict(l5x: str) -> tuple[int, int]:
    """Both partitions, from the current engine."""
    from l5x_memory_analyzer.sizing.constants import load_memory_model
    from l5x_memory_analyzer.sizing.report import build_report
    from l5x_memory_analyzer.sizing.safety import build_safety_report
    model = load_memory_model()
    root = ET.fromstring(l5x)
    return (sum(e.bytes for e in build_report(root, model)[0]),
            sum(e.bytes for e in build_safety_report(root, model)[0]))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", metavar="REGEX", help="build only the sample_ids this matches")
    args = ap.parse_args()
    for sample_id, description, kwargs in plan():
        if args.only and not re.search(args.only, sample_id):
            continue
        out = G.OUT_ROOT / f"{sample_id}.L5X"
        l5x = build(sample_id, **kwargs)
        if sample_id.startswith("safe_comp_"):
            std, saf = predict(l5x)
            description += f" -- BLIND, predicted before capture: standard {std:,}, safety {saf:,}"
        predicted = write_sample(l5x, out)
        append_manifest_row(sample_id, description, G.CATEGORY, out, predicted)
        print(f"{sample_id}: predicted {predicted:,}")


if __name__ == "__main__":
    main()
