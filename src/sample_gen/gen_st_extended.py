"""OQ-STEXTENDED: the Structured Text constructs the most ST-heavy real program writes and no
file has measured.

realprog_44 is 123 ST routines and 3,051 statements, the one standard program outside 2%
(-2.32% once instruction calls in any letter case are priced). Against every other real
program its ST carries what none of theirs does: function-block timers driven over several
lines (`T.PRE := ...; T.TimerEnable := ...; T.Reset := ...; TONR(T); D := T.ACC;`), JSR with
parameters into ST subroutines that take them with SBR and give them back with RET, AOI calls
from ST, CASE blocks, three-deep member paths behind a tag index, the `&` operator, string
instructions (CONCAT, DTOS, DELETE, FIND, SIZE), GSV and CPS, and lower-case instruction names
and keywords. The engine prices TONR / TOFR / RTOR at nothing (no weight), counts no JSR
parameter from an ST caller, and until 2026-10-24 priced a lower-case instruction at nothing.

One JSR-called ST routine on the realism floor, 1756-L81E v35. Every file carries the same
tags, UDTs, AOI and ST subroutines, so each differences against `ste_n00`:

  timers      ste_tonr_full50, _call50, _set50, _dnif50; ste_tofr_full50; ste_rtor_full50
  JSR         ste_jsr0_50; ste_jsr3_50; ste_jsr3deep_50; ste_jsr3lower_50
  AOI         ste_aoi_p2_50; ste_aoi_p6_50; ste_aoi_p6deep_50
  CASE        ste_case20x5; ste_case20x10; ste_casemember20x5
  paths       ste_dot3_400; ste_vidxdot3_400; ste_innerarr400; ste_amp400
  strings     ste_concat100; ste_dtos100; ste_delete100; ste_find100; ste_size50
  COP         ste_cop200; ste_coplower200
  system      ste_gsv50; ste_cps50
  keywords    ste_ifupper200; ste_iflower200

Every shape is the instruction set's own syntax over this project's tags; nothing is taken
from a real export.

Run: python -m sample_gen.gen_st_extended [--only REGEX]
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from sample_gen.builders import MemberSpec, aoi_xml, rung_xml, tag_xml, udt_xml
from sample_gen.gen_st_sizing import _st_routine
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.realism import with_baseline
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "stext"
CATEGORY = "st_shape"
OQ = "OQ-STEXTENDED"
N = 400
TIMERS = 50

INNER = "SteInner"
INNER_MEMBERS = [MemberSpec("A", "DINT"), MemberSpec("B", "DINT")]
UDT = "SteUdt"
UDT_MEMBERS = [MemberSpec("A", "DINT"), MemberSpec("B", "DINT"), MemberSpec("S", INNER),
               MemberSpec("Arr", "DINT", 10), MemberSpec("F", "BOOL")]
AOI = "SteAoi"
AOI_PARAMS = [MemberSpec(f"In{k}", "DINT", required=True) for k in range(6)]
AOI2 = "SteAoiTwo"
AOI2_PARAMS = [MemberSpec("InA", "DINT", required=True), MemberSpec("InB", "DINT", required=True)]


def tags() -> list[str]:
    out = [tag_xml("SteD", "DINT", (N,)), tag_xml("SteE", "DINT", (N,)), tag_xml("SteB", "BOOL", (N,)),
           tag_xml("SteC", "BOOL", (N,)), tag_xml("SteF", "BOOL", (N,)),
           tag_xml("Ix", "DINT"), tag_xml("Jx", "DINT"), tag_xml("Kx", "DINT"), tag_xml("SteRet", "DINT"),
           tag_xml("SteUa", UDT, (N,), udt_members=UDT_MEMBERS), tag_xml("SteUb", UDT, (N,), udt_members=UDT_MEMBERS),
           tag_xml("SteP", UDT, udt_members=UDT_MEMBERS),
           tag_xml("SteS", "STRING", (100,)), tag_xml("SteS2", "STRING", (100,)), tag_xml("SteS3", "STRING", (100,))]
    out += [tag_xml(f"SteT{i:03d}", "FBD_TIMER") for i in range(TIMERS)]
    out += [tag_xml(f"SteA{i:03d}", AOI) for i in range(50)] + [tag_xml(f"SteW{i:03d}", AOI2) for i in range(50)]
    return out


def subroutines() -> str:
    """Two ST subroutines in every file: one taking three parameters and returning one, one
    taking none (both uncalled in the control)."""
    sub3 = ["SBR(Ix, Jx, Kx);", "SteD[0] := Ix + Jx + Kx;", "RET(SteD[0]);"]
    sub0 = ["SteD[1] := SteD[1] + 1;"]
    return _st_routine("SteSub3", sub3) + "\n" + _st_routine("SteSub0", sub0)


def _timer(kind: str, i: int) -> list[str]:
    t = f"SteT{i:03d}"
    return [f"{t}.PRE := 1000;", f"{t}.TimerEnable := SteB[{i}];", f"{t}.Reset := SteC[{i}];",
            f"{kind}({t});", f"SteD[{i}] := {t}.ACC;"]


def _case(blocks: int, selectors: int, selector: str, with_else: bool = False) -> list[str]:
    lines = []
    for b in range(blocks):
        lines.append(f"CASE {selector.format(b=b)} OF")
        for k in range(selectors):
            lines.append(f"    {k}: SteD[{b * selectors + k}] := SteE[{b * selectors + k}] + 1;")
        if with_else:
            lines.append("ELSE")
            lines.append(f"    SteE[{N - 1 - b}] := SteE[{N - 1 - b}] + 1;")
        lines.append("END_CASE;")
    return lines


def plan() -> list[tuple[str, list[str], str]]:
    rng = range
    f = [
        ("n00", ["SteD[0] := SteD[0] + 1;"], "control: one assignment"),
        ("tonr_full50", [ln for i in rng(TIMERS) for ln in _timer("TONR", i)],
         "50 FBD_TIMER timers each driven over five lines: PRE, TimerEnable, Reset, TONR, the ACC read"),
        ("tonr_call50", [f"TONR(SteT{i:03d});" for i in rng(TIMERS)], "50 TONR calls alone"),
        ("tonr_set50", [ln for i in rng(TIMERS) for ln in _timer("TONR", i) if not ln.startswith("TONR(")],
         "the same four member lines on each timer without the TONR call"),
        ("tonr_dnif50", [ln for i in rng(TIMERS) for ln in (
            f"TONR(SteT{i:03d});", f"IF NOT SteT{i:03d}.DN AND SteB[{i}] THEN", f"    SteF[{i}] := 1;",
            "ELSE", f"    SteF[{i}] := 0;", "END_IF;")],
         "50 TONR calls each followed by an IF on its DN bit with an ELSE"),
        ("tofr_full50", [ln for i in rng(TIMERS) for ln in _timer("TOFR", i)], "the five-line timer with TOFR"),
        ("rtor_full50", [ln for i in rng(TIMERS) for ln in _timer("RTOR", i)], "the five-line timer with RTOR"),
        ("jsr0_50", ["JSR(SteSub0, 0);"] * 50, "50 JSR without parameters to an ST subroutine"),
        ("jsr3_50", [f"JSR(SteSub3, 3, SteD[{i}], SteE[{i}], Ix, SteRet);" for i in rng(50)],
         "50 JSR passing three parameters and taking one back, into the ST subroutine that takes them with SBR and returns with RET"),
        ("jsr3deep_50", [f"JSR(SteSub3, 3, SteUa[SteP.A].S.A, SteUa[{i}].Arr[Ix], SteUa[{i}].B, SteRet);" for i in rng(50)],
         "the same with the parameters written as member paths behind tag indexes"),
        ("jsr3lower_50", [f"jsr(SteSub3, 3, SteD[{i}], SteE[{i}], Ix, SteRet);" for i in rng(50)],
         "ste_jsr3_50 written in lower case"),
        ("aoi_p2_50", [f"{AOI2}(SteW{i:03d}, SteD[{i}], SteE[{i}]);" for i in rng(50)],
         "50 calls of an AOI with two Required DINT inputs"),
        ("aoi_p6_50", [f"{AOI}(SteA{i:03d}, SteD[{i}], SteE[{i}], Ix, Jx, Kx, SteRet);" for i in rng(50)],
         "50 calls of an AOI with six Required DINT inputs"),
        ("aoi_p6deep_50", [f"{AOI}(SteA{i:03d}, SteUa[{i}].A, SteUa[{i}].S.B, SteUa[Ix].B, SteUa[{i}].Arr[Jx], SteP.S.A, SteRet);"
                           for i in rng(50)], "the same with member-path arguments"),
        ("case20x5", _case(20, 5, "SteD[{b}]"), "20 CASE blocks of five selectors, one statement each"),
        ("case20x10", _case(20, 10, "SteD[{b}]"), "20 CASE blocks of ten selectors"),
        ("casemember20x5", _case(20, 5, "SteUa[{b}].A"), "20 CASE blocks of five selectors on a member-path selector"),
        # Batch H (2026-10-31): the AOI call from ST at two more counts, on the same 50 declared
        # instances (100 calls use each twice), so whether the -36 is a call or the routine comes
        # out; and the CASE block over-determined, with a CASE's ELSE on its own.
        ("aoi_p2_10", [f"{AOI2}(SteW{i:03d}, SteD[{i}], SteE[{i}]);" for i in rng(10)],
         "10 calls of the two-input AOI, against ste_aoi_p2_50"),
        ("aoi_p2_100", [f"{AOI2}(SteW{i % 50:03d}, SteD[{i}], SteE[{i}]);" for i in rng(100)],
         "100 calls of the two-input AOI, each of its 50 instances called twice, against ste_aoi_p2_50"),
        ("case40x5", _case(40, 5, "SteD[{b}]"), "40 CASE blocks of five selectors, against ste_case20x5"),
        ("case20x5else", _case(20, 5, "SteD[{b}]", with_else=True),
         "20 CASE blocks of five selectors each with an ELSE and its statement, against ste_case20x5"),
        ("dot3_400", [f"SteUa[{i}].S.A := SteUa[{i}].S.B + 1;" for i in rng(N)],
         "400 assignments through a nested UDT's members (three deep)"),
        ("vidxdot3_400", [f"SteUa[SteP.A].S.A := SteUa[{i}].S.B + 1;" for i in rng(N)],
         "the same with the destination behind an index written as a member path"),
        ("innerarr400", [f"SteUa[{i}].Arr[Ix] := SteUa[{i}].Arr[Jx] + 1;" for i in rng(N)],
         "400 assignments on a UDT member's array element indexed by a tag"),
        ("amp400", [f"SteB[{i}] := SteC[{i}] & SteF[{i}];" for i in rng(N)], "400 BOOL destinations from an & "),
        ("concat100", [f"CONCAT(SteS[{i}], SteS2[{i}], SteS3[{i}]);" for i in rng(100)], "100 CONCAT"),
        ("dtos100", [f"DTOS(SteD[{i}], SteS[{i}]);" for i in rng(100)], "100 DTOS"),
        ("delete100", [f"DELETE(SteS[{i}], 2, 1, SteS2[{i}]);" for i in rng(100)], "100 DELETE"),
        ("find100", [f"FIND(SteS[{i}], SteS2[{i}], 1, SteD[{i}]);" for i in rng(100)], "100 FIND"),
        ("size50", [f"SIZE(SteUa, 0, SteD[{i}]);" for i in rng(50)], "50 SIZE on a UDT array"),
        ("cop200", [f"COP(SteUa[{i}], SteUb[{i}], 1);" for i in rng(200)], "200 COP of a UDT element"),
        ("coplower200", [f"cop(SteUa[{i}], SteUb[{i}], 1);" for i in rng(200)], "ste_cop200 written in lower case"),
        ("gsv50", [f"GSV(WallClockTime, , LocalDateTime, SteD[{i * 7}]);" for i in rng(50)],
         "50 GSV of the wall clock into a DINT array"),
        ("cps50", [f"CPS(SteUa[{i}], SteUb[{i}], 1);" for i in rng(50)], "50 CPS of a UDT element"),
        ("ifupper200", [ln for i in rng(200) for ln in (f"IF SteB[{i}] THEN", f"    SteD[{i}] := SteD[{i}] + 1;", "END_IF;")],
         "200 IF blocks, keywords in upper case"),
        ("iflower200", [ln for i in rng(200) for ln in (f"if SteB[{i}] then", f"    SteD[{i}] := SteD[{i}] + 1;", "end_if;")],
         "the same with keywords in lower case"),
    ]
    return [(f"ste_{k}", lines, what) for k, lines, what in f]


def make(sample_id: str, lines: list[str]) -> str:
    target = "".join(p.capitalize() for p in sample_id.split("_"))
    aoi1, _ = aoi_xml(AOI, input_params=AOI_PARAMS, logic_rungs_xml=rung_xml(0, "NOP();"))
    aoi2, _ = aoi_xml(AOI2, input_params=AOI2_PARAMS, logic_rungs_xml=rung_xml(0, "NOP();"))
    return build_l5x(target_name=target, **with_baseline(
        tags_xml="\n".join(tags()),
        extra_datatypes_xml=udt_xml(INNER, INNER_MEMBERS) + "\n" + udt_xml(UDT, UDT_MEMBERS),
        extra_aoi_xml=aoi1 + "\n" + aoi2,
        extra_rungs_xml=rung_xml(0, "JSR(SteTarget,0);"),
        extra_routines_xml=_st_routine("SteTarget", lines) + "\n" + subroutines()))


def _make(job: tuple[str, list[str]]) -> int:
    sample_id, lines = job
    return write_sample(make(sample_id, lines), OUT_ROOT / f"{sample_id}.L5X")


def main(argv: list[str] | None = None) -> None:
    from sample_gen.progress import run
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", metavar="REGEX")
    args = ap.parse_args([] if argv is None else argv)
    jobs = [(sid, lines, what) for sid, lines, what in plan() if not args.only or re.search(args.only, sid)]
    predicted = run(((sid, (sid, lines)) for sid, lines, _ in jobs), _make, label="st-extended")
    for sid, _lines, what in jobs:
        append_manifest_row(sid, f"{OQ}: {what}; one JSR-called ST routine on the realism floor, 1756-L81E v35, "
                                 f"the same tags, UDTs, AOIs and ST subroutines in every file; against ste_n00.",
                            CATEGORY, OUT_ROOT / f"{sid}.L5X", predicted[sid])
        print(f"{sid}: predicted {predicted[sid]:,}")


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
