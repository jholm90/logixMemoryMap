"""OQ-STRSHAPE: STRING operands the way real programs write them, and the string
instructions measured only near-empty.

The string instructions' weights were confirmed on the realism floor for CONCAT, DTOS,
COP and SIZE on STRING array elements (`blkstr_*`), and MOV of a STRING costs a DINT MOV
(OQ-STRINGMOV). Real programs write their strings as UDT members and behind tag indexes,
in custom string types, and lean on instructions the calibration set met once: across
the counted real safety-controller programs, 2,424 STRING operands of EQU and 2,151 of
MOV are members behind an index, 777 INSERT calls (weighed on one near-empty file), 709
CONCAT (264 operands custom-typed), 185 MID; the seventeen standard programs carry 1,850
CONCAT and OQ-REALUNDER's one string-heavy lead (CONCAT count tracking the residual at
ten times CONCAT's own weight) was never explained.

One inventory in every file: STRING arrays SsA / SsB / SsC [400], a UDT StrxU (S, T
STRING; C a 40-character custom string StrX40; D DINT; R REAL) in arrays SuA / SuB / SuC
[400], DINT / REAL arrays, index tag Ix. 400 calls each, one a rung, every destination
distinct; realism floor; 1756-L81E v35; each against `strx_n00`.

The EQU / NEQ files write a bit of the UDT's DINT member: a bit of its REAL member, as
first built, is refused by Studio (lint `bit_specifier_on_real`); rebuilt 2026-10-22 as `_r2` (the
first build's rows keep their suspect readings) with the inventory unchanged, so they still
difference against the captured `strx_n00`.

Run: python -m sample_gen.gen_string_shapes
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import (MemberSpec, custom_string_type_xml, rung_xml, string_array_tag_xml, tag_xml,
                                 udt_xml)
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.realism import with_baseline
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "strx"
CATEGORY = "string_shape"
OQ = "OQ-STRSHAPE"
N = 400
UDT = "StrxU"
CUSTOM = "StrX40"
MEMBERS = [MemberSpec("S", "STRING"), MemberSpec("T", "STRING"), MemberSpec("C", CUSTOM),
           MemberSpec("D", "DINT"), MemberSpec("R", "REAL")]


def inventory() -> dict[str, str]:
    tags = [string_array_tag_xml(n, N) for n in ("SsA", "SsB", "SsC")]
    tags += [tag_xml(n, UDT, (N,), udt_members=MEMBERS) for n in ("SuA", "SuB", "SuC")]
    tags += [tag_xml("Dn", "DINT", (N,)), tag_xml("Rn", "REAL", (N,)), tag_xml("Ix", "DINT")]
    return {"tags_xml": "\n".join(tags),
            "extra_datatypes_xml": custom_string_type_xml(CUSTOM, 40) + "\n" + udt_xml(UDT, MEMBERS)}


def plan() -> list[tuple[str, list[str], str]]:
    def calls(fmt: str) -> list[str]:
        return [fmt.format(i=i) for i in range(N)]
    files = [
        ("n00", [], "control, no added rungs"),
        ("equ_elem_r2", calls("EQU(SsA[{i}],SsB[{i}])OTE(SuC[{i}].D.0);"), "EQU on STRING array elements"),
        ("equ_member_r2", calls("EQU(SuA[{i}].S,SuB[{i}].S)OTE(SuC[{i}].D.0);"), "EQU on STRING UDT members"),
        ("equ_vidx_r2", calls("EQU(SsA[Ix],SsB[{i}])OTE(SuC[{i}].D.0);"), "EQU, one STRING behind a tag index"),
        ("neq_member_r2", calls("NEQ(SuA[{i}].S,SuB[{i}].S)OTE(SuC[{i}].D.0);"), "NEQ on STRING UDT members"),
        ("mov_member", calls("MOV(SuA[{i}].S,SuB[{i}].S);"), "MOV STRING member to STRING member"),
        ("mov_vidx_member", calls("MOV(SuA[Ix].S,SuB[{i}].S);"), "MOV, the source a STRING member behind a tag index"),
        ("cop_member", calls("COP(SuA[{i}].S,SuB[{i}].S,1);"), "COP STRING member to STRING member, length 1"),
        ("concat_member", calls("CONCAT(SuA[{i}].S,SuA[{i}].T,SuB[{i}].S);"), "CONCAT on STRING members"),
        ("concat_custom", calls("CONCAT(SuA[{i}].C,SuB[{i}].C,SuC[{i}].C);"), "CONCAT on custom-string members"),
        ("insert_elem", calls("INSERT(SsA[{i}],SsB[{i}],5,SsC[{i}]);"), "INSERT on STRING array elements"),
        ("insert_member", calls("INSERT(SuA[{i}].S,SuB[{i}].S,5,SuC[{i}].S);"), "INSERT on STRING members"),
        ("mid_elem", calls("MID(SsA[{i}],2,1,SsC[{i}]);"), "MID on STRING array elements"),
        ("mid_member_vidx", calls("MID(SuA[Ix].S,2,1,SuC[{i}].S);"), "MID, the source a member behind a tag index"),
        ("delete_elem", calls("DELETE(SsA[{i}],1,1,SsC[{i}]);"), "DELETE on STRING array elements"),
        ("find_elem", calls("FIND(SsA[{i}],SsB[{i}],1,Dn[{i}]);"), "FIND on STRING array elements"),
        ("dtos_member", calls("DTOS(SuA[{i}].D,SuC[{i}].S);"), "DTOS DINT member to STRING member"),
        ("stod_elem", calls("STOD(SsA[{i}],Dn[{i}]);"), "STOD STRING to DINT"),
        ("rtos_elem", calls("RTOS(Rn[{i}],SsC[{i}]);"), "RTOS REAL to STRING"),
        ("stor_elem", calls("STOR(SsA[{i}],Rn[{i}]);"), "STOR STRING to REAL"),
        ("upper_elem", calls("UPPER(SsA[{i}],SsC[{i}]);"), "UPPER STRING to STRING"),
    ]
    return [(f"strx_{key}", rungs, what) for key, rungs, what in files]


def make(sample_id: str, rungs: list[str]) -> str:
    target = "".join(p.capitalize() for p in sample_id.split("_"))
    body = "\n".join(rung_xml(i, r) for i, r in enumerate(rungs))
    return build_l5x(target_name=target, **with_baseline(extra_rungs_xml=body, **inventory()))


def main(argv: list[str] | None = None) -> None:
    import argparse
    import re
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", metavar="REGEX", help="build only the sample_ids this matches")
    args = ap.parse_args([] if argv is None else argv)
    for sample_id, rungs, what in plan():
        if args.only and not re.search(args.only, sample_id):
            continue
        out = OUT_ROOT / f"{sample_id}.L5X"
        predicted = write_sample(make(sample_id, rungs), out)
        shown = f"{N} x `{rungs[1]}` -- {what}" if rungs else what
        append_manifest_row(sample_id, f"{OQ}: {shown}. Same inventory in every strx_* file, realism floor, "
                                       f"1756-L81E v35; differenced against strx_n00.", CATEGORY, out, predicted)
        print(f"Wrote {out.name} (predicted {predicted:,})")


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
