"""OQ-LDGAPS: every ladder instruction of the general instruction reference no ladder file measures.

Owner's request 2026-10-29: every instruction tested in ladder and in ST, wherever it can be
written. The audit (`docs/INSTRUCTION_COVERAGE.md`, "Every instruction, ladder and ST") found
these ladder instructions with no captured ladder isolation, most with no weight at all, so a
call is priced at its operands only:

  ATAN2 LN STD LOWER CTD LFL DDT SQI SQL SQO EOT IOT IsINF IsNAN LV

(CTD and ATAN2 have only safety-routine captures; CTD's 20 is borrowed from CTU.) Their ST
side, where ST can call them, is batch F (`gen_st_instructions.py`).

Not here, with the reason: ALMA / ASO (alarm instructions, parked); SFP / SFR (SFC is never
worked); REF (its operand is a REF_TO_AXIS reference type no file has built); UNK (the
placeholder Studio writes for an instruction it cannot read, not one a program writes).

Each file: the realism-floor plant, 1756-L81E v35, plus one JSR-called ladder routine of N
rungs, each one call on its own backing tags (a condition instruction ends in an OTE on its own
bit, weight 16, measured). N = 50 and 100, so the per-call cost is the slope and the tags,
priced exactly by the engine, drop out. Control: `ldgap_n00`, the plant, the common tags and
one MOV rung. Operand order and formats are the reference's ladder operand tables; nothing is
taken from a real export.

Run: python -m sample_gen.gen_ld_gaps [--only REGEX]
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from sample_gen.builders import control_tag_xml, counter_tag_xml, rung_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.realism import with_baseline
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "ldgap"
CATEGORY = "logic_instr"
OQ = "OQ-LDGAPS"
COUNTS = (50, 100)
NMAX = max(COUNTS)


def _common_tags() -> list[str]:
    return [tag_xml("LgD", "DINT", (NMAX,)), tag_xml("LgE", "DINT", (NMAX,)), tag_xml("LgR", "REAL", (NMAX,)),
            tag_xml("LgQ", "REAL", (NMAX,)), tag_xml("LgZ", "REAL", (NMAX,)), tag_xml("LgB", "BOOL", (NMAX,)),
            tag_xml("LgS", "STRING", (NMAX,)), tag_xml("LgS2", "STRING", (NMAX,)),
            tag_xml("LgArr", "DINT", (10,)), tag_xml("LgRArr", "REAL", (10,))]


def _per(name: str, n: int, fn) -> list[str]:
    return [fn(f"{name}{i:03d}") for i in range(n)]


# mnemonic -> (rung text for call i, own tags for n calls, what the call is)
def _arm(mn: str, n: int) -> tuple[list[str], list[str], str]:
    r = range(n)
    if mn == "ATAN2":
        return [f"ATAN2(LgR[{i}],LgQ[{i}],LgZ[{i}]);" for i in r], [], "ATAN2(REAL, REAL, REAL)"
    if mn == "LN":
        return [f"LN(LgR[{i}],LgQ[{i}]);" for i in r], [], "LN(REAL, REAL)"
    if mn == "STD":
        return ([f"STD(LgRArr[0],0,LgQ[{i}],LgCtl{i:03d},10,0);" for i in r],
                _per("LgCtl", n, control_tag_xml), "STD(REAL[10], 0, REAL, CONTROL, 10, 0)")
    if mn == "LOWER":
        return [f"LOWER(LgS[{i}],LgS2[{i}]);" for i in r], [], "LOWER(STRING, STRING)"
    if mn == "CTD":
        return ([f"CTD(LgCnt{i:03d},10,0);" for i in r], _per("LgCnt", n, lambda t: counter_tag_xml(t, 10)),
                "CTD(COUNTER, 10, 0)")
    if mn == "LFL":
        return ([f"LFL(LgD[{i}],LgLifo{i:03d}[0],LgCtl{i:03d},10,0);" for i in r],
                _per("LgLifo", n, lambda t: tag_xml(t, "DINT", (10,))) + _per("LgCtl", n, control_tag_xml),
                "LFL(DINT, DINT[10], CONTROL, 10, 0)")
    if mn == "DDT":
        return ([f"DDT(LgArr[0],LgRef{i:03d}[0],LgRes{i:03d}[0],LgCmp{i:03d},10,0,LgRc{i:03d},10,0);" for i in r],
                _per("LgRef", n, lambda t: tag_xml(t, "DINT", (10,))) + _per("LgRes", n, lambda t: tag_xml(t, "DINT", (10,)))
                + _per("LgCmp", n, control_tag_xml) + _per("LgRc", n, control_tag_xml),
                "DDT(DINT[10], DINT[10], DINT[10], CONTROL, 10, 0, CONTROL, 10, 0)")
    if mn == "SQI":
        return ([f"SQI(LgArr[0],LgE[{i}],LgD[{i}],LgCtl{i:03d},10,0)OTE(LgB[{i}]);" for i in r],
                _per("LgCtl", n, control_tag_xml), "SQI(DINT[10], DINT, DINT, CONTROL, 10, 0) OTE")
    if mn == "SQL":
        return ([f"SQL(LgSeq{i:03d}[0],LgD[{i}],LgCtl{i:03d},10,0);" for i in r],
                _per("LgSeq", n, lambda t: tag_xml(t, "DINT", (10,))) + _per("LgCtl", n, control_tag_xml),
                "SQL(DINT[10], DINT, CONTROL, 10, 0)")
    if mn == "SQO":
        return ([f"SQO(LgArr[0],LgE[{i}],LgD[{i}],LgCtl{i:03d},10,0);" for i in r],
                _per("LgCtl", n, control_tag_xml), "SQO(DINT[10], DINT, DINT, CONTROL, 10, 0)")
    if mn == "EOT":
        return [f"EOT(LgB[{i}]);" for i in r], [], "EOT(BOOL)"
    if mn == "IOT":
        return [f"IOT(RACK_{1 + i % 5}:O);" for i in r], [], "IOT(module output tag)"
    if mn in ("IsINF", "IsNAN"):
        return [f"{mn}(LgR[{i}])OTE(LgB[{i}]);" for i in r], [], f"{mn}(REAL) OTE"
    if mn == "LV":
        return [f"LV({1 + i},{1 + i});" for i in r], [], "LV(vendor code, product code)"
    raise KeyError(mn)


INSTRUCTIONS = ("ATAN2", "LN", "STD", "LOWER", "CTD", "LFL", "DDT", "SQI", "SQL", "SQO", "EOT", "IOT",
                "IsINF", "IsNAN", "LV")


def plan() -> list[tuple[str, str, dict]]:
    files = [("ldgap_n00", f"{OQ}: control: the plant, the common tags and one MOV rung", {"mn": None, "n": 0})]
    for mn in INSTRUCTIONS:
        for n in COUNTS:
            what = _arm(mn, 1)[2]
            files.append((f"ldgap_{mn.lower()}_{n}", f"{OQ}: {n} ladder rungs of {what}, each on its own tags",
                          {"mn": mn, "n": n}))
    return files


def make(sample_id: str, kw: dict) -> str:
    tags = _common_tags()
    if kw["mn"] is None:
        rungs = ["MOV(LgD[0],LgE[0]);"]
    else:
        rungs, own, _ = _arm(kw["mn"], kw["n"])
        tags += own
    body = "\n".join(rung_xml(i, t) for i, t in enumerate(rungs))
    routine = f'<Routine Name="LgTarget" Type="RLL">\n<RLLContent>\n{body}\n</RLLContent>\n</Routine>'
    target = "".join(p.capitalize() for p in sample_id.split("_"))
    return build_l5x(target_name=target, **with_baseline(
        tags_xml="\n".join(tags), extra_rungs_xml=rung_xml(0, "JSR(LgTarget,0);"), extra_routines_xml=routine))


def _make(job: tuple[str, dict]) -> int:
    sample_id, kw = job
    return write_sample(make(sample_id, kw), OUT_ROOT / f"{sample_id}.L5X")


def main(argv: list[str] | None = None) -> None:
    from sample_gen.progress import run
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", metavar="REGEX")
    args = ap.parse_args([] if argv is None else argv)
    jobs = [(sid, desc, kw) for sid, desc, kw in plan() if not args.only or re.search(args.only, sid)]
    predicted = run(((sid, (sid, kw)) for sid, _, kw in jobs), _make, label="ld-gaps")
    for sid, desc, _kw in jobs:
        append_manifest_row(sid, f"{desc}; one JSR-called ladder routine on the realism floor, 1756-L81E v35; "
                                 f"against ldgap_n00 and the engine's price of its backing tags.",
                            CATEGORY, OUT_ROOT / f"{sid}.L5X", predicted[sid])
        print(f"{sid}: predicted {predicted[sid]:,}")


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
