"""CPT/CMP expression-COMPLEXITY sweep (James, 2026-08-23): "You will need
to generate different complexities of cpt/CMP instruction of course. I'd
make 10-20 files with one cpt instruction and see how differing
expressions change size. Do the same with CMP instructions. After analysis
of that then do a couple of spot checks in files with multiple rungs with
the same expressions and a couple of spot checks with combinations of
random rungs/expressions to validate. Be sure to put constants as well as
tags."

Directly targets the MAJOR finding from the 2026-08-23 rebase (see
docs/OPEN_QUESTIONS.md OQ-CMPCPTLAYOUT): the existing "CPT=452/rung, 0.00%
residual" constant is confirmed WRONG as a general number -- it was fit
against one specific complex expression, and real per-rung CPT cost is
expression-complexity-dependent. `gen_cmpcpt_layout.py` (2026-08-22)
already swept OPERATOR type and a few structural variants at a FIXED
2-operand complexity, 1000 rungs each -- this sweeps operand COUNT itself
(the actual complexity axis the CPT finding says matters), one CPT/CMP
instruction per file (1 rung), so each file's real Capacity delta is a
direct, uncontaminated read of that one expression's true cost -- no
rung-count division or linearity assumption needed to compare files
against each other.

  A. group_cpt_operand_count -- CPT(Dest,L0+L1+...+Ln), same operator (+)
     throughout, n=1..10 operands. Isolates "does cost scale with operand
     count" independent of operator type.
  B. group_cpt_operator_mix -- fixed at 4 operands, but mixed operators
     (+-*), parenthesized/nested, and power-mixed. Isolates "does operator
     TYPE matter, once operand count is held fixed" (group A's complement).
  C. group_cpt_constants -- integer and float literal operands mixed with
     tags, at increasing complexity (2/3/4-operand). Directly answers
     James's "be sure to put constants as well as tags."
  D. group_cmp_complexity -- CMP's own complexity ladder: bare tag-tag,
     expressions on one or both sides of the comparison, int/float
     literals, compound (&&) conditions with simple and expression-bearing
     clauses.
  E. group_multirung_spotcheck -- "a couple of spot checks in files with
     multiple rungs with the same expression": 3 representative expressions
     from A-D, each repeated across 100 identical rungs, to check whether
     the per-rung marginal cost implied by the single-rung file times 100
     actually matches a real 100-rung capture (linearity check for the
     complexity axis specifically, distinct from the already-confirmed
     rung-count linearity of the ORIGINAL fixed-complexity sweep).
  F. group_random_mix -- "a couple of spot checks with combinations of
     random rungs/expressions to validate": 2 files, each mixing several
     different CPT/CMP expression shapes from A-D at randomized rung
     counts, matching the realistic-mixed-file validation pattern already
     used for plain instructions (gen_logic_random_mix.py) but for
     CPT/CMP complexity specifically. NOT validated against the engine's
     own prediction the way that file is (there's no correct per-operand
     CPT/CMP model yet to validate against) -- these exist purely to give
     James a realistic mixed file to capture real data on.

Own tag pool, separate from every other sweep's (gen_cmpcpt_layout.py's
8-DINT/3-REAL pool didn't have headroom for a 10-operand chain without
reusing the destination tag as an operand) -- L0-L9 (10 DINT operands),
R0-R4 (5 REAL operands), dedicated Dest/DestR destinations (never also an
operand, avoids any self-reference ambiguity), TB0 (BOOL, CMP's OTE
companion, matching the already-confirmed CMP+OTE combined-rung shape).

Run: python -m sample_gen.gen_cmpcpt_complexity
"""

from __future__ import annotations

import random
from pathlib import Path

from sample_gen.builders import rung_xml, rungs_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"

_POOL_TAGS_XML = (
    "\n".join(tag_xml(f"L{i}", "DINT") for i in range(10)) + "\n"
    + "\n".join(tag_xml(f"R{i}", "REAL") for i in range(5)) + "\n"
    + tag_xml("Dest", "DINT") + "\n"
    + tag_xml("DestR", "REAL") + "\n"
    + tag_xml("TB0", "BOOL")
)

RNG_SEED = 20260823


def _write(l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "cmpcpt_complexity", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


def _one_rung_file(instr: str, target_name: str, out_name: str, description: str) -> None:
    rungs = rung_xml(0, instr)
    l5x = build_l5x(target_name=target_name, tags_xml=_POOL_TAGS_XML, extra_rungs_xml=rungs)
    _write(l5x, out_name, description)


# ---------------------------------------------------------------------------
# A. CPT operand-count ladder, single rung per file, same operator (+).
# ---------------------------------------------------------------------------

def group_cpt_operand_count() -> None:
    for n in [1, 2, 3, 4, 5, 6, 8, 10]:
        operands = "+".join(f"L{i}" for i in range(n))
        instr = f"CPT(Dest,{operands});"
        _one_rung_file(instr, f"CptOperandN{n:02d}", f"cptcx_operandcount_n{n:02d}",
                        f"1 rung of CPT(Dest,{operands}) -- {n}-operand complexity, same operator throughout")


# ---------------------------------------------------------------------------
# B. Operator-type variation at fixed 4-operand complexity.
# ---------------------------------------------------------------------------

def group_cpt_operator_mix() -> None:
    variants = {
        "mixedops": "L0+L1-L2*L3",
        "nested": "(L0+L1)*(L2-L3)",
        "powermix": "L0**L1+L2**L3",
    }
    for name, expr in variants.items():
        instr = f"CPT(Dest,{expr});"
        _one_rung_file(instr, f"CptOpMix{name.capitalize()}", f"cptcx_operatormix_{name}",
                        f"1 rung of CPT(Dest,{expr}) -- 4-operand, mixed/nested/power operator shape")


# ---------------------------------------------------------------------------
# C. Constant (literal) operands, integer and float, mixed with tags.
# ---------------------------------------------------------------------------

def group_cpt_constants() -> None:
    variants = {
        "intconst_n2": ("Dest", "L0+5"),
        "intconst_n3": ("Dest", "L0+L1+5"),
        "intconst_n4": ("Dest", "L0+5+L1+10"),
        "floatconst_n2": ("DestR", "R0*1.5+R1"),
        "floatconst_n4": ("DestR", "R0*1.5+R1*2.5-R2/3.5"),
    }
    for name, (dest, expr) in variants.items():
        instr = f"CPT({dest},{expr});"
        _one_rung_file(instr, f"CptConst{name.capitalize()}", f"cptcx_constants_{name}",
                        f"1 rung of CPT({dest},{expr}) -- literal-constant operand(s) mixed with tags")


# ---------------------------------------------------------------------------
# D. CMP complexity ladder.
# ---------------------------------------------------------------------------

def group_cmp_complexity() -> None:
    variants = {
        "baretags": "L0>L1",
        "exprleft": "L0+L1>L2",
        "exprboth": "L0+L1>L2+L3",
        "complex": "(L0+L1)*L2>L3-L4",
        "intliteral": "L0>5",
        "floatliteral": "L0>5.5",
        "exprplusliteral": "L0+L1>5",
        "floatconstmixed": "L0*1.5>L1+2.5",
        "compound_simple": "L0>L1&&L2>L3",
        "compound_expr": "(L0+L1)>L2&&(L3-L4)<L5",
    }
    for name, expr in variants.items():
        instr = f"CMP({expr})OTE(TB0);"
        _one_rung_file(instr, f"CmpCx{name.capitalize()}", f"cmpcx_{name}",
                        f"1 rung of CMP({expr}) -- CMP complexity ladder")


# ---------------------------------------------------------------------------
# E. Multi-rung spot checks -- 3 representative expressions at n=100 rungs,
#    to cross-check the single-rung complexity read against a real
#    multi-rung capture (a genuinely new rung-count point, between the
#    n=1 files above and the existing 1000-rung cmpcpt_* baseline).
# ---------------------------------------------------------------------------

def group_multirung_spotcheck() -> None:
    checks = [
        ("Dest", "L0+L1", "CPT", "cptcx_spotcheck_simple2op"),
        ("Dest", "L0+L1-L2*L3", "CPT", "cptcx_spotcheck_mixedops4op"),
        (None, "L0>L1", "CMP", "cmpcx_spotcheck_baretags"),
    ]
    n = 100
    for dest, expr, kind, out_prefix in checks:
        instr = f"CPT({dest},{expr});" if kind == "CPT" else f"CMP({expr})OTE(TB0);"
        rungs = rungs_xml(n, lambda i, instr=instr: instr)
        l5x = build_l5x(target_name=f"Spot{out_prefix}", tags_xml=_POOL_TAGS_XML, extra_rungs_xml=rungs)
        _write(l5x, f"{out_prefix}_n{n:03d}",
               f"{n} identical rungs of {instr.rstrip(chr(59))} -- multi-rung spot check vs the n=1 single-rung file")


# ---------------------------------------------------------------------------
# F. Random-mix validation files -- realistic combinations of several
#    different CPT/CMP expression shapes at randomized rung counts.
# ---------------------------------------------------------------------------

_MIX_CANDIDATES = [
    ("CPT(Dest,L0+L1);", "cpt_2op"),
    ("CPT(Dest,L0+L1+L2+L3);", "cpt_4op"),
    ("CPT(Dest,L0+L1-L2*L3);", "cpt_mixedop"),
    ("CPT(Dest,L0+5);", "cpt_intconst"),
    ("CPT(DestR,R0*1.5+R1);", "cpt_floatconst"),
    ("CMP(L0>L1)OTE(TB0);", "cmp_baretags"),
    ("CMP(L0+L1>L2)OTE(TB0);", "cmp_exprleft"),
    ("CMP(L0>L1&&L2>L3)OTE(TB0);", "cmp_compound"),
]


def _one_random_mix_file(rng: random.Random, index: int) -> None:
    chosen = rng.sample(_MIX_CANDIDATES, rng.randint(4, len(_MIX_CANDIDATES)))
    counts = {name: rng.randint(20, 150) for _, name in chosen}
    rung_blocks = []
    total_rungs = 0
    for instr, name in chosen:
        c = counts[name]
        rung_blocks.append(rungs_xml(c, lambda i, instr=instr: instr))
        total_rungs += c
    l5x = build_l5x(target_name=f"CmpCptMix{index}", tags_xml=_POOL_TAGS_XML,
                     extra_rungs_xml="\n".join(rung_blocks))
    mix_desc = ", ".join(f"{counts[n]}x{n}" for _, n in chosen)
    out_name = f"cmpcpt_randommix_{index:02d}_n{total_rungs:05d}rungs"
    _write(l5x, out_name, f"Random CPT/CMP complexity mix ({len(chosen)} shapes, {total_rungs} total rungs): {mix_desc}")


def group_random_mix() -> None:
    rng = random.Random(RNG_SEED)
    for i in range(2):
        _one_random_mix_file(rng, i)


def main() -> None:
    group_cpt_operand_count()
    group_cpt_operator_mix()
    group_cpt_constants()
    group_cmp_complexity()
    group_multirung_spotcheck()
    group_random_mix()
    total = 8 + 3 + 5 + 10 + 3 + 2
    print(f"\nDone. {total} files.")


if __name__ == "__main__":
    main()
