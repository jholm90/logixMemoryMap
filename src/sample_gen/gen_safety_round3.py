"""OQ-SAFETYPARTITION, round 3: ordinary logic in a safety routine.

Every ordinary instruction the safety-routine palette offers, each alone at 20 rungs in
SafetyProgram/MainRoutine, on one fixed pool of SafetyProgram tags that every file
declares in full, so each file differences against safe_lg_ctl and nothing else. Then
operand forms (literals, mixed types, a tag-driven index, a timer member, scalar BOOLs,
controller-scope operands), rung composition, and a second count for the most-used
instructions. Spec: TASKS 0v. Call shapes are the captured standard ones (sample_gen's
instruction generators), with the pool's tags in place of theirs.

Platform and builder as rounds 1 and 2 (gen_safety_round2.build): 1756-L81ES v35 on the
realism plant.

Run: python -m sample_gen.gen_safety_round3 [--only REGEX]
"""

from __future__ import annotations

import argparse
import re

from sample_gen import gen_safety_partition as G
from sample_gen import gen_safety_round2 as R
from sample_gen.manifest import append_manifest_row, write_sample

OQ = "OQ-SAFETYPARTITION"


def _pool() -> list[str]:
    """The SafetyProgram tags every safe_lg_* file declares, used or not."""
    p = R.prog_tag
    tags = [p("LgB", "BOOL", (512,)), p("LgO", "BOOL", (512,)), p("LgS", "BOOL", (128,)),
            p("LgDa", "DINT", (128,)), p("LgDb", "DINT", (128,)), p("LgDc", "DINT", (128,)),
            p("LgRa", "REAL", (64,)), p("LgRb", "REAL", (64,)), p("LgRc", "REAL", (64,)),
            p("LgIa", "INT", (64,)), p("LgT", "TIMER", (128,)), p("LgC", "COUNTER", (32,)),
            p("LgArrA", "DINT", (64,)), p("LgArrB", "DINT", (64,)), p("LgIdx", "DINT")]
    tags += [p(f"LgX{i:02d}", "BOOL") for i in range(20)] + [p(f"LgY{i:02d}", "BOOL") for i in range(20)]
    return tags


def _cpool() -> list[str]:
    """The controller-scope safety pool of safe_lgc_*."""
    c = R.ctl_tag
    return [c("LcB", "BOOL", (64,)), c("LcO", "BOOL", (64,)),
            c("LcDa", "DINT", (32,)), c("LcDb", "DINT", (32,)), c("LcDc", "DINT", (32,))]


OUT = "OTE(LgO[{i}])"

INPUTS = {
    "xic": "XIC(LgB[{i}])" + OUT, "xio": "XIO(LgB[{i}])" + OUT, "ons": "ONS(LgS[{i}])" + OUT,
    "osr": "OSR(LgS[{i}],LgO[{i}])", "osf": "OSF(LgS[{i}],LgO[{i}])",
    "equ": "EQU(LgDa[{i}],LgDb[{i}])" + OUT, "neq": "NEQ(LgDa[{i}],LgDb[{i}])" + OUT,
    "grt": "GRT(LgDa[{i}],LgDb[{i}])" + OUT, "geq": "GEQ(LgDa[{i}],LgDb[{i}])" + OUT,
    "les": "LES(LgDa[{i}],LgDb[{i}])" + OUT, "leq": "LEQ(LgDa[{i}],LgDb[{i}])" + OUT,
    "lim": "LIM(LgDa[{i}],LgDb[{i}],LgDc[{i}])" + OUT,
    "meq": "MEQ(LgDa[{i}],16#0000_00FF,LgDb[{i}])" + OUT,
    "cmp": "CMP(LgDa[{i}]>LgDb[{i}])" + OUT, "afi": "AFI()" + OUT,
}

OUTPUTS = {
    "ote": "OTE(LgO[{i}])", "otl": "OTL(LgO[{i}])", "otu": "OTU(LgO[{i}])",
    "ton": "TON(LgT[{i}],1000,0)", "tof": "TOF(LgT[{i}],1000,0)", "rto": "RTO(LgT[{i}],1000,0)",
    "res": "RES(LgT[{i}])", "ctu": "CTU(LgC[{i}],10,0)", "ctd": "CTD(LgC[{i}],10,0)",
    "mov": "MOV(LgDa[{i}],LgDb[{i}])",
    **{mn.lower(): f"{mn}(LgDa[{{i}}],LgDb[{{i}}],LgDc[{{i}}])"
       for mn in ("ADD", "SUB", "MUL", "DIV", "MOD", "AND", "OR", "XOR")},
    "neg": "NEG(LgDa[{i}],LgDb[{i}])", "abs": "ABS(LgDa[{i}],LgDb[{i}])", "not": "NOT(LgDa[{i}],LgDb[{i}])",
    "sqr": "SQR(LgRa[{i}],LgRb[{i}])", "atan2": "ATAN2(LgRa[{i}],LgRb[{i}],LgRc[{i}])",
    "cpt": "CPT(LgDc[{i}],LgDa[{i}]+LgDb[{i}])", "clr": "CLR(LgDa[{i}])",
    "mvm": "MVM(LgDa[{i}],16#0000_00FF,LgDb[{i}])", "swpb": "SWPB(LgDa[{i}],REVERSE,LgDb[{i}])",
    "cop": "COP(LgArrA[{i}],LgArrB[{i}],1)", "fll": "FLL(0,LgArrB[{i}],1)", "size": "SIZE(LgArrA,0,LgDb[{i}])",
}

OPERANDS = {
    "movlit": ("MOV(5,LgDb[{i}])", "a literal DINT source"),
    "movflit": ("MOV(1.5,LgRb[{i}])", "a literal REAL source"),
    "addlit": ("ADD(LgDa[{i}],1,LgDc[{i}])", "ADD with a literal operand"),
    "equlit": ("EQU(LgDa[{i}],5)" + OUT, "EQU against a literal, with its OTE"),
    "addmix": ("ADD(LgDa[{i}],LgRa[{i}],LgRc[{i}])", "ADD of a DINT and a REAL into a REAL"),
    "movdr": ("MOV(LgDa[{i}],LgRb[{i}])", "MOV of a DINT into a REAL"),
    "movid": ("MOV(LgIa[{i}],LgDb[{i}])", "MOV of an INT into a DINT"),
    "xicind": ("XIC(LgB[LgIdx])" + OUT, "XIC on a tag-indexed BOOL element, with its OTE"),
    "movind": ("MOV(LgDa[LgIdx],LgDb[{i}])", "MOV from a tag-indexed DINT element"),
    "xicdn": ("XIC(LgT[{i}].DN)" + OUT, "XIC on a timer's .DN, with its OTE"),
    "xicotesc": ("XIC(LgX{i:02d})OTE(LgY{i:02d})", "XIC+OTE on scalar BOOLs"),
}

SHAPES = {
    "series4": ("XIC(LgB[{i}])XIC(LgB[{j1}])XIO(LgB[{j2}])XIC(LgB[{j3}])" + OUT, "four inputs in series and an OTE"),
    "branch2": ("[XIC(LgB[{i}]),XIC(LgB[{j1}])]" + OUT, "a two-leg branch of XICs and an OTE"),
    "branch3": ("[XIC(LgB[{i}]),XIC(LgB[{j1}]),XIC(LgB[{j2}])]" + OUT, "a three-leg branch of XICs and an OTE"),
    "twoout": ("XIC(LgB[{i}])OTE(LgO[{i}])OTE(LgO[{k}])", "XIC and two OTEs"),
    "sealin": ("[XIC(LgB[{i}]),XIC(LgO[{i}])]XIO(LgB[{j1}])" + OUT, "a seal-in: start or self, not stop, OTE"),
}

COUNT = 20
SECOND_COUNT = {"ote": OUTPUTS["ote"], "xio": INPUTS["xio"], "mov": OUTPUTS["mov"],
                "equ": INPUTS["equ"], "ton": OUTPUTS["ton"]}


def _rungs(template: str, n: int) -> list[str]:
    return [template.format(i=i, j1=100 + i, j2=200 + i, j3=300 + i, k=256 + i) + ";" for i in range(n)]


def _file(sid: str, desc: str, rungs: list[str], cpool: bool = False) -> tuple[str, str, dict]:
    kw = {"controller_tags": _cpool(), "programs": [R.main_program(rungs=rungs)]} if cpool \
        else {"programs": [R.main_program(_pool(), rungs)]}
    return sid, f"{OQ}: {desc}", kw


def plan() -> list[tuple[str, str, dict]]:
    files = [_file("safe_lg_ctl", "control for safe_lg_*: the SafetyProgram tag pool, no logic", []),
             _file("safe_lgc_ctl", "control for safe_lgc_*: the controller-scope safety pool, no logic", [], cpool=True)]
    for name, tpl in INPUTS.items():
        files.append(_file(f"safe_lg_{name}_{COUNT}", f"{COUNT} safety-routine rungs: {tpl.format(i='i')}",
                           _rungs(tpl, COUNT)))
    for name, tpl in OUTPUTS.items():
        files.append(_file(f"safe_lg_{name}_{COUNT}", f"{COUNT} safety-routine rungs: {tpl.format(i='i')} alone",
                           _rungs(tpl, COUNT)))
    mcr = [("XIC(LgB[{0}])MCR();".format(k) if half == 0 else "MCR();") for k in range(10) for half in (0, 1)]
    files.append(_file("safe_lg_mcr_20", "10 MCR zones in the safety routine (an XIC+MCR rung, an MCR rung)", mcr))
    jl = [(f"JMP(Lb{k:02d});" if half == 0 else f"LBL(Lb{k:02d})OTE(LgO[{k}]);") for k in range(10) for half in (0, 1)]
    files.append(_file("safe_lg_jmplbl_20", "10 JMP / LBL+OTE pairs in the safety routine", jl))
    for name, (tpl, what) in OPERANDS.items():
        files.append(_file(f"safe_lg_{name}_{COUNT}", f"{COUNT} safety-routine rungs, {what}", _rungs(tpl, COUNT)))
    for name, tpl in (("xicote", "XIC(LcB[{i}])OTE(LcO[{i}])"), ("mov", "MOV(LcDa[{i}],LcDb[{i}])"),
                      ("add", "ADD(LcDa[{i}],LcDb[{i}],LcDc[{i}])")):
        files.append(_file(f"safe_lgc_{name}_{COUNT}", f"{COUNT} safety-routine rungs on controller-scope safety "
                           f"tags: {tpl.format(i='i')}", _rungs(tpl, COUNT), cpool=True))
    for name, (tpl, what) in SHAPES.items():
        files.append(_file(f"safe_lg_{name}_{COUNT}", f"{COUNT} safety-routine rungs, {what}", _rungs(tpl, COUNT)))
    for name, tpl in SECOND_COUNT.items():
        files.append(_file(f"safe_lg_{name}_100", f"100 safety-routine rungs: {tpl.format(i='i')}", _rungs(tpl, 100)))
    return files


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", metavar="REGEX", help="build only the sample_ids this matches")
    args = ap.parse_args()
    for sample_id, description, kwargs in plan():
        if args.only and not re.search(args.only, sample_id):
            continue
        out = G.OUT_ROOT / f"{sample_id}.L5X"
        predicted = write_sample(R.build(sample_id, **kwargs), out)
        append_manifest_row(sample_id, description, G.CATEGORY, out, predicted)
        print(f"{sample_id}: predicted {predicted:,}")


if __name__ == "__main__":
    main()
