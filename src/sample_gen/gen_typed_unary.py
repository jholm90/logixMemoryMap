"""OQ-LITREAL (types): typed instructions the operand-type surcharge does not cover.

The engine charges a type surcharge on thirteen instructions only (ADD SUB MUL DIV MOD
EQU NEQ GRT GEQ LES LEQ LIM MOV). Every other numeric instruction pays the DINT rate
whatever its operands are, though the instruction set documents SINT, INT, DINT and
REAL for them and converts non-DINT operands the same way. Real exposure, typed calls
with a non-DINT operand in instructions outside the table (seventeen programs): CLR on
REAL 4,120, CLR on SINT 239, BTD on SINT 231, CLR on INT 98, ABS on REAL 90, TRN on
REAL 33, NEG on REAL 13.

One inventory (SINT/INT/DINT/REAL arrays of 400), 400 calls per file, realism floor,
1756-L81E at v35:

  typun_<type>_clr    CLR(A[i])                     SINT INT DINT REAL
  typun_<type>_mov0   MOV(0,A[i])                   the same clear as a move (literal 0 is a DINT)
  typun_<type>_abs    ABS(A[i],D[i])                SINT INT DINT REAL
  typun_<type>_neg    NEG(A[i],D[i])                SINT INT DINT REAL
  typun_<type>_btd    BTD(A[i],0,D[i],0,4)          SINT INT DINT (no REAL: not allowed)
  typun_trn_real      TRN(RealA[i],RealD[i])        uniform REAL
  typun_trn_dintdest  TRN(RealA[i],DintD[i])        REAL source, DINT destination

Each non-DINT file against its DINT twin is that instruction's type surcharge.

Run: python -m sample_gen.gen_typed_unary
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import rung_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.realism import with_baseline
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "typun"
CATEGORY = "typed_unary"
N = 400
PREFIX = {"SINT": "Us", "INT": "Ui", "DINT": "Ud", "REAL": "Ur"}


def _inventory() -> str:
    return "\n".join(tag_xml(f"{p}{s}", t, (N,)) for t, p in PREFIX.items() for s in ("A", "D"))


def _files() -> dict[str, tuple[list[str], str]]:
    f: dict[str, tuple[list[str], str]] = {}
    for t, p in PREFIX.items():
        f[f"{t.lower()}_clr"] = ([f"CLR({p}A[{i}]);" for i in range(N)], f"CLR({p}A[i]) on {t}")
        f[f"{t.lower()}_mov0"] = ([f"MOV(0,{p}A[{i}]);" for i in range(N)],
                                  f"MOV(0,{p}A[i]) on {t} -- the same clear written as a move; vs typun_{t.lower()}_clr")
        f[f"{t.lower()}_abs"] = ([f"ABS({p}A[{i}],{p}D[{i}]);" for i in range(N)], f"ABS({p}A[i],{p}D[i]) on {t}")
        f[f"{t.lower()}_neg"] = ([f"NEG({p}A[{i}],{p}D[{i}]);" for i in range(N)], f"NEG({p}A[i],{p}D[i]) on {t}")
        if t != "REAL":
            f[f"{t.lower()}_btd"] = ([f"BTD({p}A[{i}],0,{p}D[{i}],0,4);" for i in range(N)],
                                     f"BTD({p}A[i],0,{p}D[i],0,4) on {t}")
    f["trn_real"] = ([f"TRN(UrA[{i}],UrD[{i}]);" for i in range(N)], "TRN(UrA[i],UrD[i]), uniform REAL")
    f["trn_dintdest"] = ([f"TRN(UrA[{i}],UdD[{i}]);" for i in range(N)],
                         "TRN(UrA[i],UdD[i]), REAL source into a DINT destination; vs typun_trn_real")
    return f


def _write(sample_id: str, rungs: list[str], description: str, inventory: str) -> None:
    out = OUT_ROOT / f"{sample_id}.L5X"
    body = "\n".join(rung_xml(i, t) for i, t in enumerate(rungs))
    target = "".join(p.capitalize() for p in sample_id.split("_"))
    l5x = build_l5x(target_name=target, **with_baseline(tags_xml=inventory, extra_rungs_xml=body))
    predicted = write_sample(l5x, out)
    append_manifest_row(
        sample_id,
        f"OQ-LITREAL (types): {N} x {description}. Same inventory in every typun_* file, "
        f"realism floor; each non-DINT file against its DINT twin is the type surcharge.",
        CATEGORY, out, predicted)
    print(f"Wrote {out.name} (predicted {predicted:,})")


def main() -> None:
    inventory = _inventory()
    _write("typun_n00", [], "control, no added rungs", inventory)
    for stem, (rungs, what) in _files().items():
        _write(f"typun_{stem}", rungs, what, inventory)


if __name__ == "__main__":
    main()
