"""OQ-LITREAL: an integer literal in a REAL call -- does it pay a conversion?

A Studio-made edit of one real rung (export 27's worst program, cam-correction rung,
kept alone in the plant): turning one DINT compare limit into a REAL tag and six
integer literals `1`/`-1` against REAL operands into `1.0`/`-1.0` saved **600** bytes;
the engine, which types a literal as nothing, expected **312** (the DINT tag's six
measured conversions, OQ-MIXEDTYPE). The other 288 is ~48 per literal. Charging an
integer literal in a REAL call like a DINT source (+52) moves the seventeen real
programs from 2.18% to 1.72% mean, 4.31% to 3.44% worst. 5,851 such literals sit in
the real set's typed calls (MOV 1,040, DIV 599, MUL 494, LES 446, GRT 407, ADD 317,
EQU 248, MOD 217, LIM 211, SUB 210, NEQ 120, GEQ 104, LEQ 65).

This batch measures it per instruction and position on the realism floor. Every file
carries the same inventory (REAL/DINT arrays of 400, REAL scalars) and 400 calls, one
per rung, every destination and output distinct. For each instruction three files:

  <mn>_tag    the literal's position holds a REAL tag -- uniform REAL, already priced
  <mn>_ilit   the same position holds the integer literal 5
  <mn>_flit   the same position holds the float literal 5.0

`_ilit - _tag` is what an integer literal costs against a REAL tag; `_flit - _tag` the
float literal's; `_ilit - _flit` the conversion. Plus: GRT with 0, 1000 and 100000 (a
literal's size class), GRT with the literal first, LIM with one and two literals, and
MUL on DINT with a float literal (the reverse case, 117 real uses).

1756-L81E at v35.

Run: python -m sample_gen.gen_literal_real
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import rung_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.realism import with_baseline
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "litreal"
CATEGORY = "literal_real"
N = 400

# mnemonic -> rung template; {x} is the operand under test, {i} the call index.
TEMPLATES = {
    "MOV": "MOV({x},LrD[{i}]);",
    "ADD": "ADD(LrA[{i}],{x},LrD[{i}]);",
    "SUB": "SUB(LrA[{i}],{x},LrD[{i}]);",
    "MUL": "MUL(LrA[{i}],{x},LrD[{i}]);",
    "DIV": "DIV(LrA[{i}],{x},LrD[{i}]);",
    "MOD": "MOD(LrA[{i}],{x},LrD[{i}]);",
    "GRT": "GRT(LrA[{i}],{x})OTE(LrQ[{i}]);",
    "LES": "LES(LrA[{i}],{x})OTE(LrQ[{i}]);",
    "GEQ": "GEQ(LrA[{i}],{x})OTE(LrQ[{i}]);",
    "LEQ": "LEQ(LrA[{i}],{x})OTE(LrQ[{i}]);",
    "EQU": "EQU(LrA[{i}],{x})OTE(LrQ[{i}]);",
    "NEQ": "NEQ(LrA[{i}],{x})OTE(LrQ[{i}]);",
    "LIM": "LIM(LrLo,LrA[{i}],{x})OTE(LrQ[{i}]);",
}
FORMS = {"tag": "LrK", "ilit": "5", "flit": "5.0"}


def _inventory() -> str:
    return "\n".join([
        tag_xml("LrA", "REAL", (N,)), tag_xml("LrD", "REAL", (N,)),
        tag_xml("LdA", "DINT", (N,)), tag_xml("LdD", "DINT", (N,)),
        tag_xml("LrQ", "BOOL", (N,)),
        tag_xml("LrK", "REAL"), tag_xml("LrLo", "REAL"), tag_xml("LdK", "DINT"),
    ])


def _files() -> dict[str, tuple[list[str], str]]:
    f: dict[str, tuple[list[str], str]] = {}
    for mn, tpl in TEMPLATES.items():
        for form, x in FORMS.items():
            what = {"tag": "a REAL tag (LrK) -- the uniform-REAL control",
                    "ilit": "the integer literal 5", "flit": "the float literal 5.0"}[form]
            f[f"{mn.lower()}_{form}"] = (
                [tpl.format(x=x, i=i) for i in range(N)],
                f"{N} x `{tpl.format(x=x, i='i')}` -- REAL operands, the tested position holding {what}"
                + ("" if form == "tag" else f"; vs litreal_{mn.lower()}_tag"))
    for v in ("0", "1000", "100000"):
        f[f"grt_ilit_v{v}"] = (
            [f"GRT(LrA[{i}],{v})OTE(LrQ[{i}]);" for i in range(N)],
            f"{N} x `GRT(LrA[i],{v})` -- integer literal size class; vs litreal_grt_ilit (5)")
    f["grt_ilit_first"] = (
        [f"GRT(5,LrA[{i}])OTE(LrQ[{i}]);" for i in range(N)],
        f"{N} x `GRT(5,LrA[i])` -- the literal as the first operand; vs litreal_grt_ilit")
    f["lim_ilit2"] = (
        [f"LIM(0,LrA[{i}],5)OTE(LrQ[{i}]);" for i in range(N)],
        f"{N} x `LIM(0,LrA[i],5)` -- two integer literals; vs litreal_lim_ilit (one) and _tag")
    f["mul_dint_ilit"] = (
        [f"MUL(LdA[{i}],2,LdD[{i}]);" for i in range(N)],
        f"{N} x `MUL(LdA[i],2,LdD[i])` -- DINT with an integer literal: the DINT control")
    f["mul_dint_flit"] = (
        [f"MUL(LdA[{i}],1.5,LdD[{i}]);" for i in range(N)],
        f"{N} x `MUL(LdA[i],1.5,LdD[i])` -- DINT with a float literal (the reverse case); "
        f"vs litreal_mul_dint_ilit")
    return f


def _write(sample_id: str, rungs: list[str], description: str, inventory: str) -> None:
    out = OUT_ROOT / f"{sample_id}.L5X"
    body = "\n".join(rung_xml(i, t) for i, t in enumerate(rungs))
    target = "".join(p.capitalize() for p in sample_id.split("_"))
    l5x = build_l5x(target_name=target, **with_baseline(tags_xml=inventory, extra_rungs_xml=body))
    predicted = write_sample(l5x, out)
    append_manifest_row(
        sample_id,
        f"OQ-LITREAL: {description}. Same inventory in every litreal_* file, realism floor; "
        f"only the tested operand differs between the files of one instruction.",
        CATEGORY, out, predicted)
    print(f"Wrote {out.name} (predicted {predicted:,})")


def main() -> None:
    inventory = _inventory()
    _write("litreal_n00", [], "control, no added rungs", inventory)
    for stem, (rungs, what) in _files().items():
        _write(f"litreal_{stem}", rungs, what, inventory)


if __name__ == "__main__":
    main()
