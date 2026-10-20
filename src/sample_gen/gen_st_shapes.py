"""OQ-STSHAPE: the Structured Text shapes real programs use and no file has measured.

The ST law (memory_model.yaml structured_text) was measured on bare tags and literal array
indexes: `D0 := D1 + D2;`, `IF B0 THEN`, `FOR StIdx := 0 TO 9 DO`. Real ST is written in
member paths, variable indexes, compound conditions, BOOL destinations and ELSE branches.
Three real safety-controller programs with 576 to 1,126 executable ST lines each read 3.0%
to 3.7% under on the standard figure, about 77 bytes per executable ST line, while the
programs around them land inside 1% (OPEN_QUESTIONS OQ-STSHAPE).

One JSR-called ST routine on the realism floor, 1756-L81E v35. Every file carries the same
tags and UDT, so each differences against `stshape_n00` (and the noted sibling):

  stshape_n00                one assignment: the control
  stshape_assign400          `StD[i] := StE[i] + 1;`               (ties to streal_assign400)
  stshape_member400          `StU[i].A := StU[i].B + 1;`           member after a literal index
  stshape_scalarmember400    `StP.A := StP.B + 1;`                 member of a scalar UDT tag
  stshape_vidx_src400        `StD[i] := StE[Ix] + 1;`              tag index, source
  stshape_vidx_dst400        `StD[Ix] := StE[i] + 1;`              tag index, destination
  stshape_vidx_both400       `StD[Ix] := StE[Jx] + 1;`             both (additivity)
  stshape_vidx_member400     `StU[Ix].A := StU[i].B + 1;`          tag index then member
  stshape_vidx_bymember400   `StD[i] := StE[StP.A] + 1;`           index written as a member
  stshape_vidx_offset400     `StD[i] := StE[Ix + 1] + 1;`          index expression
  stshape_real400            `StR[i] := StR[i] + 1.5;`             REAL destination, float literal
  stshape_real_member400     `StU[i].R := StU[i].R + 1.5;`         the same through a member path
  stshape_real_mul400        `StR[i] := StR[i] * 1.5;`             REAL, one multiplicative operator
  stshape_bool_{lit,copy,not,and,cmp}400   BOOL destination: `1`, `StC[i]`, `NOT StC[i]`,
                             `StC[i] AND StF[i]`, `StD[i] > 5`
  stshape_if_*200            200 IF blocks, body `StD[i] := StD[i] + 1;`, conditions: BOOL
                             (control), `> 5`, `= 5`, `>= Lim`, AND, AND of three, OR, NOT,
                             `>= 1 AND <= 12`, REAL `> 1.5`, members, a tag-indexed BOOL; and
                             two statements, ELSE, nested IF
  stshape_cop200 / _cop_vidx200   COP with a literal / tag-indexed source
  stshape_for_{lit,tag,vidx}50    50 FOR blocks: literal bound, tag bound, body indexed by the
                             loop variable
  stshape_cmt400             stshape_assign400 with a /* */ comment line after each statement

Inside an AOI (37% of real ST is an AOI's own Logic), one instance called once from
the plant's MainRoutine; each against `stshape_aoi_n00`, then against its program twin:

  stshape_aoi_n00            the AOI with one ST statement: the control
  stshape_aoi_assign400      `LD[i] := LE[i] + 1;` on local DINT arrays   (vs stshape_assign400)
  stshape_aoi_if200          `IF LB[i] THEN LD[i] := LD[i] + 1; END_IF;`  (vs stshape_if_bool200)
  stshape_aoi_param400       `LD[i] := InA + InB;` on two Input parameters

Run: python -m sample_gen.gen_st_shapes
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, aoi_xml, rung_xml, tag_xml, udt_xml
from sample_gen.gen_st_sizing import _st_routine
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.realism import with_baseline
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "stshape"
CATEGORY = "st_shape"
OQ = "OQ-STSHAPE"
N = 400
IFS = 200
FORS = 50

UDT = "StShapeU"
MEMBERS = [MemberSpec("A", "DINT"), MemberSpec("B", "DINT"), MemberSpec("R", "REAL"),
           MemberSpec("F", "BOOL"), MemberSpec("G", "BOOL")]


def tags() -> str:
    return "\n".join([
        tag_xml("StD", "DINT", (N,)), tag_xml("StE", "DINT", (N,)), tag_xml("StR", "REAL", (N,)),
        tag_xml("StB", "BOOL", (N,)), tag_xml("StC", "BOOL", (N,)), tag_xml("StF", "BOOL", (N,)),
        tag_xml("Ix", "DINT"), tag_xml("Jx", "DINT"), tag_xml("Lim", "DINT"),
        tag_xml("StU", UDT, (N,), udt_members=MEMBERS), tag_xml("StP", UDT, udt_members=MEMBERS),
    ])


def _assign(fmt: str) -> list[str]:
    return [fmt.format(i=i) for i in range(N)]


def _ifs(cond: str, body: tuple[str, ...] = ("    StD[{i}] := StD[{i}] + 1;",)) -> list[str]:
    return [line.format(i=i) for i in range(IFS) for line in (f"IF {cond} THEN", *body, "END_IF;")]


def _fors(head: str, body: str) -> list[str]:
    return [line.format(i=i) for i in range(FORS) for line in (head, body, "END_FOR;")]


def plan() -> list[tuple[str, list[str], str]]:
    one = "StD[{i}] := StD[{i}] + 1;"
    files = [
        ("n00", ["StD[0] := StD[0] + 1;"], "control: one assignment"),
        ("assign400", _assign("StD[{i}] := StE[{i}] + 1;"), "400 DINT assignments, literal indexes"),
        ("member400", _assign("StU[{i}].A := StU[{i}].B + 1;"), "400 assignments through UDT members after a literal index"),
        ("scalarmember400", ["StP.A := StP.B + 1;"] * N, "400 assignments through members of a scalar UDT tag"),
        ("vidx_src400", _assign("StD[{i}] := StE[Ix] + 1;"), "400 assignments, the source indexed by a tag"),
        ("vidx_dst400", _assign("StD[Ix] := StE[{i}] + 1;"), "400 assignments, the destination indexed by a tag"),
        ("vidx_both400", ["StD[Ix] := StE[Jx] + 1;"] * N, "400 assignments, both operands indexed by tags"),
        ("vidx_member400", _assign("StU[Ix].A := StU[{i}].B + 1;"), "400 assignments, the destination a member after a tag index"),
        ("vidx_bymember400", _assign("StD[{i}] := StE[StP.A] + 1;"), "400 assignments, the source indexed by a member path"),
        ("vidx_offset400", _assign("StD[{i}] := StE[Ix + 1] + 1;"), "400 assignments, the source indexed by an expression"),
        ("real400", _assign("StR[{i}] := StR[{i}] + 1.5;"), "400 REAL assignments with a float literal"),
        ("real_member400", _assign("StU[{i}].R := StU[{i}].R + 1.5;"), "the same through a REAL UDT member"),
        ("real_mul400", _assign("StR[{i}] := StR[{i}] * 1.5;"), "400 REAL assignments, one multiplicative operator"),
        ("bool_lit400", _assign("StB[{i}] := 1;"), "400 BOOL destinations from a literal"),
        ("bool_copy400", _assign("StB[{i}] := StC[{i}];"), "400 BOOL destinations from a BOOL"),
        ("bool_not400", _assign("StB[{i}] := NOT StC[{i}];"), "400 BOOL destinations from NOT a BOOL"),
        ("bool_and400", _assign("StB[{i}] := StC[{i}] AND StF[{i}];"), "400 BOOL destinations from an AND"),
        ("bool_cmp400", _assign("StB[{i}] := StD[{i}] > 5;"), "400 BOOL destinations from a comparison"),
        ("if_bool200", _ifs("StB[{i}]"), "200 IF blocks on a BOOL: the control for the IF family"),
        ("if_cmp200", _ifs("StD[{i}] > 5"), "200 IF blocks on a DINT > literal"),
        ("if_eq200", _ifs("StD[{i}] = 5"), "200 IF blocks on a DINT = literal"),
        ("if_cmptag200", _ifs("StD[{i}] >= Lim"), "200 IF blocks on a DINT >= tag"),
        ("if_and200", _ifs("StB[{i}] AND StC[{i}]"), "200 IF blocks on two BOOLs ANDed"),
        ("if_and3_200", _ifs("StB[{i}] AND StC[{i}] AND StF[{i}]"), "200 IF blocks on three BOOLs ANDed"),
        ("if_or200", _ifs("StB[{i}] OR StC[{i}]"), "200 IF blocks on two BOOLs ORed"),
        ("if_not200", _ifs("NOT StB[{i}]"), "200 IF blocks on NOT a BOOL"),
        ("if_range200", _ifs("StD[{i}] >= 1 AND StD[{i}] <= 12"), "200 IF blocks on two comparisons ANDed"),
        ("if_real200", _ifs("StR[{i}] > 1.5"), "200 IF blocks on a REAL > float literal"),
        ("if_member200", _ifs("StU[{i}].F AND StU[{i}].G"), "200 IF blocks on two BOOL UDT members ANDed"),
        ("if_vidx200", _ifs("StB[Ix]"), "200 IF blocks on a tag-indexed BOOL"),
        ("if_two200", _ifs("StB[{i}]", ("    StD[{i}] := StD[{i}] + 1;", "    StE[{i}] := StE[{i}] - 1;")),
         "200 IF blocks on a BOOL with two statements: the control for ELSE"),
        ("if_else200", _ifs("StB[{i}]", ("    StD[{i}] := StD[{i}] + 1;", "ELSE", "    StE[{i}] := StE[{i}] - 1;")),
         "200 IF / ELSE blocks, one statement each side"),
        ("if_nested200", _ifs("StB[{i}]", ("    IF StC[{i}] THEN", "        StD[{i}] := StD[{i}] + 1;", "    END_IF;")),
         "200 IF blocks each holding a nested IF"),
        ("cop200", _assign("COP(StD[{i}], StE[{i}], 1);")[:IFS], "200 COP, literal-indexed source"),
        ("cop_vidx200", _assign("COP(StD[Ix], StE[{i}], 1);")[:IFS], "200 COP, tag-indexed source"),
        ("for_lit50", _fors("FOR Ix := 0 TO 9 DO", "    " + one), "50 FOR blocks, literal bound, literal-indexed body"),
        ("for_tag50", _fors("FOR Ix := 0 TO Lim DO", "    " + one), "50 FOR blocks, tag bound"),
        ("for_vidx50", _fors("FOR Ix := 0 TO 9 DO", "    StD[Ix] := StE[Ix] + 1;"),
         "50 FOR blocks, the body indexed by the loop variable"),
        ("cmt400", [ln for i in range(N) for ln in (f"StD[{i}] := StE[{i}] + 1;",
                                                     "/* IF StB[0] THEN FOR Ix := 0 TO 9 DO StD[0] := 1; END_FOR; END_IF; */")],
         "stshape_assign400 with a /* */ comment line after every statement"),
    ]
    aoi = [
        ("aoi_n00", ["LD[0] := LD[0] + 1;"], "control: the AOI with one ST statement"),
        ("aoi_assign400", _assign("LD[{i}] := LE[{i}] + 1;"), "400 assignments on local DINT arrays inside the AOI"),
        ("aoi_if200", [ln.format(i=i) for i in range(IFS) for ln in
                       ("IF LB[{i}] THEN", "    LD[{i}] := LD[{i}] + 1;", "END_IF;")],
         "200 IF blocks on a local BOOL array inside the AOI"),
        ("aoi_param400", _assign("LD[{i}] := InA + InB;"), "400 assignments from two Input parameters inside the AOI"),
    ]
    return [(f"stshape_{key}", lines, what) for key, lines, what in files + aoi]


AOI = "StShapeAoi"
AOI_INPUTS = [MemberSpec("InA", "DINT"), MemberSpec("InB", "DINT")]
AOI_LOCALS = [MemberSpec("LD", "DINT", N), MemberSpec("LE", "DINT", N), MemberSpec("LB", "BOOL", 416)]


def aoi_definition(lines: list[str]) -> tuple[str, list[MemberSpec]]:
    """An AOI whose Logic routine is ST, as real AOI definitions carry it."""
    definition, storage = aoi_xml(AOI, input_params=AOI_INPUTS, local_tags=AOI_LOCALS)
    rll = '        <Routine Name="Logic" Type="RLL"/>\n'
    assert definition.count(rll) == 1
    return definition.replace(rll, _st_routine("Logic", lines) + "\n"), storage


def make(sample_id: str, lines: list[str]) -> str:
    target = "".join(p.capitalize() for p in sample_id.split("_"))
    if sample_id.startswith("stshape_aoi_"):
        definition, storage = aoi_definition(lines)
        return build_l5x(target_name=target, **with_baseline(
            tags_xml=tag_xml("StAoiInst", AOI, udt_members=storage), extra_aoi_xml=definition,
            extra_rungs_xml=rung_xml(0, f"{AOI}(StAoiInst);")))
    return build_l5x(target_name=target, **with_baseline(
        tags_xml=tags(), extra_datatypes_xml=udt_xml(UDT, MEMBERS),
        extra_rungs_xml=rung_xml(0, "JSR(StTarget,0);"),
        extra_routines_xml=_st_routine("StTarget", lines)))


def main(only: str | None = None) -> None:
    for sample_id, lines, what in plan():
        if only and not sample_id.startswith(only):
            continue
        out = OUT_ROOT / f"{sample_id}.L5X"
        predicted = write_sample(make(sample_id, lines), out)
        where = ("one instance of an AOI whose Logic is ST, called once, on the realism floor, 1756-L81E v35; "
                 "differenced against stshape_aoi_n00" if sample_id.startswith("stshape_aoi_") else
                 "one JSR-called ST routine on the realism floor, 1756-L81E v35. Same tags and UDT in every "
                 "program-routine stshape_* file; differenced against stshape_n00")
        append_manifest_row(sample_id, f"{OQ}: {what}, {where}.", CATEGORY, out, predicted)
        print(f"Wrote {out.name} (predicted {predicted:,})")


if __name__ == "__main__":
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else None)
