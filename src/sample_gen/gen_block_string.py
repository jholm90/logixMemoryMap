"""OQ-BLOCKSTR: block moves, string instructions and jumps in real context.

The exactly-priced transplants of real programs carry almost none of these, while real
program logic is full of them (per 1,000 instructions, transplants vs the seventeen):
COP 5.3 vs 12.0 (3,822 calls), CONCAT 0 vs 5.6 (1,778), JMP 0.9 vs 4.2 (1,340), LBL 0.9 vs
3.5 (1,120), CPS 0 vs 1.6 (504), DTOS 0 vs 1.3 (423), FLL 2.7 vs 3.7 (1,181). Their weights
were fitted on near-empty calibration files. Real shapes, seventeen programs: COP UDT->UDT
2,393 / DINT->DINT 641 / STRING->STRING 380 / REAL->REAL 104, length 1 in 2,931 of 3,822;
FLL a literal into a UDT 849 / DINT 182 / STRING 63 / REAL 61; CPS UDT->UDT 324; CONCAT
STRING x3; DTOS DINT->STRING 260, literal->STRING 140.

One inventory: BkUdt (DINT, REAL, INT, four BOOLs) arrays BkA/BkB[400], DINT/REAL arrays,
STRING arrays BsA/BsB/BsC[400]; 400 calls per file, every destination distinct; realism
floor; 1756-L81E at v35. Control `blkstr_n00`.

Run: python -m sample_gen.gen_block_string
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, rung_xml, string_array_tag_xml, tag_xml, udt_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.realism import with_baseline
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "blkstr"
CATEGORY = "block_string"
N = 400
M = 10 * N  # long arrays for the length-10 copies

_UDT = [MemberSpec("D", "DINT"), MemberSpec("R", "REAL"), MemberSpec("I", "INT")] + \
       [MemberSpec(f"B{j}", "BOOL") for j in range(4)]


def _inventory() -> dict[str, str]:
    tags = [tag_xml("BkA", "BkUdt", (M,), udt_members=_UDT), tag_xml("BkB", "BkUdt", (M,), udt_members=_UDT),
            tag_xml("BdA", "DINT", (M,)), tag_xml("BdB", "DINT", (M,)),
            tag_xml("BrA", "REAL", (M,)), tag_xml("BrB", "REAL", (M,)),
            string_array_tag_xml("BsA", N), string_array_tag_xml("BsB", N), string_array_tag_xml("BsC", N),
            tag_xml("BkLen", "DINT"), tag_xml("BkC", "BOOL", (N,))]
    return {"tags_xml": "\n".join(tags), "extra_datatypes_xml": udt_xml("BkUdt", _UDT)}


def _files() -> dict[str, tuple[list[str], str]]:
    f: dict[str, tuple[list[str], str]] = {}
    for src, dst, kind in (("BdA", "BdB", "DINT"), ("BkA", "BkB", "UDT"), ("BrA", "BrB", "REAL"),
                           ("BsA", "BsB", "STRING")):
        f[f"cop_{kind.lower()}_l1"] = ([f"COP({src}[{i}],{dst}[{i}],1);" for i in range(N)],
                                       f"COP {kind} -> {kind}, length 1")
    f["cop_dint_l10"] = ([f"COP(BdA[{10 * i}],BdB[{10 * i}],10);" for i in range(N)], "COP DINT, length 10")
    f["cop_udt_l10"] = ([f"COP(BkA[{10 * i}],BkB[{10 * i}],10);" for i in range(N)], "COP UDT, length 10")
    f["cop_udt_lentag"] = ([f"COP(BkA[{i}],BkB[{i}],BkLen);" for i in range(N)], "COP UDT, length a DINT tag")
    f["cps_udt_l1"] = ([f"CPS(BkA[{i}],BkB[{i}],1);" for i in range(N)], "CPS UDT -> UDT, length 1")
    f["cps_dint_l1"] = ([f"CPS(BdA[{i}],BdB[{i}],1);" for i in range(N)], "CPS DINT -> DINT, length 1")
    f["fll_dint_l10"] = ([f"FLL(0,BdB[{10 * i}],10);" for i in range(N)], "FLL literal 0 into DINT, length 10")
    f["fll_real_l10"] = ([f"FLL(0,BrB[{10 * i}],10);" for i in range(N)], "FLL literal 0 into REAL, length 10")
    f["fll_udt_l1"] = ([f"FLL(0,BkB[{i}],1);" for i in range(N)], "FLL literal 0 into a UDT, length 1")
    f["fll_udt_l10"] = ([f"FLL(0,BkB[{10 * i}],10);" for i in range(N)], "FLL literal 0 into a UDT, length 10")
    f["concat"] = ([f"CONCAT(BsA[{i}],BsB[{i}],BsC[{i}]);" for i in range(N)], "CONCAT STRING, STRING -> STRING")
    f["dtos_dint"] = ([f"DTOS(BdA[{i}],BsC[{i}]);" for i in range(N)], "DTOS DINT -> STRING")
    f["dtos_lit"] = ([f"DTOS({i + 1},BsC[{i}]);" for i in range(N)], "DTOS integer literal -> STRING")
    f["size_udt"] = ([f"SIZE(BkA,0,BdB[{i}]);" for i in range(N)], "SIZE of a UDT array, dimension 0")
    jl = []
    for i in range(N):
        jl.append(f"XIC(BkC[{i}])JMP(Lb{i:03d});")
        jl.append(f"LBL(Lb{i:03d})NOP();")
    f["jmplbl"] = (jl, "400 JMP / LBL pairs, each JMP skipping to its own LBL on the next rung (800 rungs)")
    return f


def _write(sample_id: str, rungs: list[str], description: str, inv: dict[str, str]) -> None:
    out = OUT_ROOT / f"{sample_id}.L5X"
    body = "\n".join(rung_xml(i, r) for i, r in enumerate(rungs))
    target = "".join(p.capitalize() for p in sample_id.split("_"))
    l5x = build_l5x(target_name=target, **with_baseline(extra_rungs_xml=body, **inv))
    predicted = write_sample(l5x, out)
    append_manifest_row(sample_id, f"OQ-BLOCKSTR: {description}. Same inventory in every blkstr_* file, "
                                   f"realism floor; differenced against blkstr_n00.", CATEGORY, out, predicted)
    print(f"Wrote {out.name} (predicted {predicted:,})")


def main() -> None:
    inv = _inventory()
    _write("blkstr_n00", [], "control, no added rungs", inv)
    for stem, (rungs, what) in _files().items():
        _write(f"blkstr_{stem}", rungs, f"{N} x `{rungs[1] if stem != 'jmplbl' else rungs[0]}` -- {what}", inv)


if __name__ == "__main__":
    main()
