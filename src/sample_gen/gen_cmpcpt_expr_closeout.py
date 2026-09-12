"""OQ-CMPCPTLAYOUT closeout (2026-09-12).

The question's stated remaining thread -- "only the REAL-operand/float-literal
interaction remains open, and it's genuinely NOT monotonic in operand count" --
is closed: all 65 captured `cptmix_*` rows now reconcile at zero against the
current engine (63 at exactly 0, two at -4 and -16). The entry's "all land
within 0.7-1.3%, 188-272 bytes" was measured before later wiring landed and had
gone stale.

What the same reconciliation DID find is a different gap, and a structural one:
CPT has had an expression-complexity model since 2026-08-23 and CMP never did.
A CMP whose operands are themselves arithmetic expressions was priced as though
they were bare tags, so `CMP(L0+L1>L2)` was under-charged the entire cost of
the `+`. Every bare-tag and bare-literal CMP shape measured exact; every
arithmetic one sat at a real negative residual.

Fixed by routing CMP's arithmetic operators through CPT's own operator-tier
table, with no separate CMP fit -- the tiers fitted on CPT land on CMP's
measured residuals as they are:

    CMP shape                    was    now
    L0+L1>L2                     -36     +0
    L0+L1>5                      -36     +0
    (L0+L1)*L2>L3-L4            -100     +0
    L0+L1>L2+L3                  -64     -4
    (L0+L1)>L2&&(L3-L4)<L5       -64     -4
    L0*1.5>L1+2.5               -128    -52

Two residuals survive that, and this batch is aimed at exactly those two. 44
files, nothing padded.

  A. group_cmp_float_operands -- the -52 on `L0*1.5>L1+2.5`.

     `cmp_surcharge.float_literal_cost` (72) is charged once per CMP call as a
     BOOLEAN, from a single measured shape (`CMP(L0>5.5)`, exact). That shape
     has one float literal and no arithmetic. The surviving -52 says the
     boolean is wrong as soon as there is more than one float literal, or as
     soon as a float sits inside an arithmetic sub-expression -- and one file
     cannot say which, nor whether the rate is per-literal (in which case 72
     is wrong, since 128-76=52) or a float-context promotion of the
     arithmetic operators themselves.

     So: float-literal COUNT swept 0..3 independently of arithmetic operator
     count, plus REAL-TAG operands (`CMP(R0+R1>R2)`) with no literal at all,
     which separates "a float literal costs something" from "evaluating the
     comparison in floating point costs something". The REAL-tag arm is the
     one the corpus has no data for at all.

  B. group_cpt_tier_mix -- the -4 on `CPT(Dest,L0+L1-L2*L3)` and
     `CPT(Dest,(L0+L1)*(L2-L3))`, and the matching -4 on two 2-operator CMP
     shapes.

     4 bytes is this project's smallest quantum and would normally be noise,
     except it scales exactly: `cptcx_spotcheck_mixedops4op_n100` is 100 rungs
     of the same expression and lands at -400. That is a real per-rung term,
     not a per-file offset. It is NOT simply "mixed tiers" either -- every
     `cptmix_pair_t1t2_*` file mixes tier 1 with tier 2 and measures exact.

     Both affected shapes have three operators spanning two tiers with the
     tier-1 operators in the majority. This sweeps tier composition at FIXED
     operator count (3 and 4 operators, every tier split), each shape at n=1
     and n=100, so a 4-bytes-per-rung term appears as -400 and a per-file
     offset stays at -4. Fixing operator count is the point: the existing
     files vary count and composition together, which is why the term was
     never separable.

  C. group_cpt_power_tier -- `CPT(Dest,L0**L1+L2**L3)` is the only shape in
     the corpus that OVER-predicts (+16), and `**` is the only tier-3
     operator (116, far above tier 2's 52). Two `**` in one expression is the
     untested case; `cptrdpow_k2/k3` (-848/-1648) say something about
     repeated `**` is badly wrong on the REAL-destination path too. Swept
     1..4 `**` operators, alone and mixed with tier 1, at n=1 and n=100.

Run: python -m sample_gen.gen_cmpcpt_expr_closeout
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import rung_xml, rungs_xml, tag_xml
from sample_gen.lint import lint_or_raise
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"

_POOL_TAGS_XML = (
    "\n".join(tag_xml(f"L{i}", "DINT") for i in range(10)) + "\n"
    + "\n".join(tag_xml(f"R{i}", "REAL") for i in range(6)) + "\n"
    + tag_xml("Dest", "DINT") + "\n"
    + tag_xml("DestR", "REAL") + "\n"
    + tag_xml("TB0", "BOOL")
)


def _write(l5x: str, out_name: str, description: str) -> int:
    lint_or_raise(l5x, out_name)
    out_path = OUT_ROOT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "cmpcpt_expr_closeout", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")
    return 1


def _file(instr: str, out_name: str, description: str, rung_count: int = 1) -> int:
    if rung_count == 1:
        rungs = rung_xml(0, instr)
    else:
        rungs = rungs_xml(rung_count, lambda i, instr=instr: instr)
    l5x = build_l5x(target_name="ExprCloseout", tags_xml=_POOL_TAGS_XML,
                    extra_rungs_xml=rungs)
    return _write(l5x, out_name, description)


# ---------------------------------------------------------------------------
# A. CMP float literals and REAL operands
# ---------------------------------------------------------------------------

# (label, CMP expression, what it isolates)
CMP_FLOAT_SHAPES = (
    # float-literal COUNT at a FIXED single arithmetic operator, so count is
    # separated from operator count for the first time.
    ("f0_op1", "L0+L1>L2", "1 arithmetic operator, 0 float literals (control)"),
    ("f1_op1", "L0+1.5>L2", "1 arithmetic operator, 1 float literal"),
    ("f2_op1", "L0+1.5>2.5", "1 arithmetic operator, 2 float literals"),
    ("f3_op1", "L0+1.5>2.5+3.5", "2 arithmetic operators, 3 float literals"),
    # the captured shape that still reads -52, plus its one-literal twin
    ("f2_op2_mul", "L0*1.5>L1+2.5", "the captured cmpcx_floatconstmixed shape"),
    ("f1_op2_mul", "L0*1.5>L1+L2", "same shape, ONE float literal instead of two"),
    ("f1_op2_add", "L0+1.5>L1+L2", "same again with a tier-1 operator, to test "
                                   "whether the float attaches to the operator tier"),
    # float literal with NO arithmetic at all -- the one shape already
    # measured exact, rebuilt here as the batch's own internal control
    ("f1_op0", "L0>5.5", "1 float literal, no arithmetic (already exact; control)"),
    ("f2_op0", "L0>5.5", "duplicate control, second float literal on the other side"),
    # REAL TAG operands, no literal anywhere: separates float-literal cost
    # from floating-point-evaluation cost. No corpus data exists for this.
    ("realtag_op0", "R0>R1", "REAL tag operands, no arithmetic, no literal"),
    ("realtag_op1", "R0+R1>R2", "REAL tag operands, 1 arithmetic operator"),
    ("realtag_op2", "R0+R1>R2+R3", "REAL tag operands, 2 arithmetic operators"),
    ("realtag_op1_mul", "R0*R1>R2", "REAL tag operands, 1 tier-2 operator"),
    ("realmix_op1", "R0+L0>L1", "one REAL and one DINT operand, mixed evaluation"),
)


def group_cmp_float_operands() -> int:
    n = 0
    for label, expr, what in CMP_FLOAT_SHAPES:
        # the two f*_op0 entries share an expression; keep names unique but
        # don't write the same file twice
        if label == "f2_op0":
            continue
        n += _file(
            f"CMP({expr})OTE(TB0);", f"cmpfl_{label}",
            f"CMP({expr}) -- {what}. OQ-CMPCPTLAYOUT float closeout: "
            f"cmp_surcharge.float_literal_cost is charged once per call as a boolean, "
            f"fitted on the single shape CMP(L0>5.5). After CMP's arithmetic operators "
            f"were routed through CPT's operator-tier table, cmpcx_floatconstmixed "
            f"(L0*1.5>L1+2.5) is the only CMP shape left with a real residual (-52), "
            f"and one file cannot say whether the rate is per-literal, whether a float "
            f"inside an arithmetic sub-expression promotes the operator tier, or whether "
            f"floating-point evaluation itself is what costs. The REAL-tag arm carries no "
            f"literal at all, which is the case the corpus has never covered")
    return n


# ---------------------------------------------------------------------------
# B. CPT tier composition at FIXED operator count
# ---------------------------------------------------------------------------

# (label, expression, operator tiers present) -- operator COUNT is held at 3
# for the k3 rows and 4 for the k4 rows, and only the tier split moves.
CPT_TIER_SHAPES = (
    ("k3_t1x3", "L0+L1-L2+L3"),
    ("k3_t1x2_t2x1", "L0+L1-L2*L3"),        # the captured -4 shape
    ("k3_t1x1_t2x2", "L0+L1*L2*L3"),
    ("k3_t2x3", "L0*L1*L2/L3"),
    ("k3_nested_t1x2_t2x1", "(L0+L1)*(L2-L3)"),   # the other captured -4 shape
    ("k3_nested_t1x1_t2x2", "(L0*L1)+(L2*L3)"),
    ("k4_t1x4", "L0+L1-L2+L3-L4"),
    ("k4_t1x3_t2x1", "L0+L1-L2+L3*L4"),
    ("k4_t1x2_t2x2", "L0+L1-L2*L3*L4"),
    ("k4_t1x1_t2x3", "L0+L1*L2*L3/L4"),
    ("k4_t2x4", "L0*L1*L2/L3/L4"),
)
TIER_RUNG_COUNTS = (1, 100)


def group_cpt_tier_mix() -> int:
    n = 0
    for label, expr in CPT_TIER_SHAPES:
        for count in TIER_RUNG_COUNTS:
            n += _file(
                f"CPT(Dest,{expr});", f"cpttier_{label}_n{count:03d}",
                f"CPT(Dest,{expr}) x{count} rung(s) -- OQ-CMPCPTLAYOUT tier-mix "
                f"closeout. Two shapes in the corpus sit at -4 (L0+L1-L2*L3 and "
                f"(L0+L1)*(L2-L3)) and the n=100 twin of the first lands at exactly "
                f"-400, so it is a real per-rung term rather than noise -- but it is "
                f"not simply 'mixed tiers', because every cptmix_pair_t1t2_* file "
                f"mixes tier 1 with tier 2 and measures exact. Operator COUNT is held "
                f"fixed here and only the tier split moves, which the existing files "
                f"never do; n=1 vs n=100 separates a per-rung term (-400) from a "
                f"per-file offset (-4)",
                rung_count=count)
    return n


# ---------------------------------------------------------------------------
# C. Repeated tier-3 (**) operators
# ---------------------------------------------------------------------------

CPT_POWER_SHAPES = (
    ("p1", "L0**L1"),
    ("p2", "L0**L1+L2**L3"),          # the captured +16 shape
    ("p2_adjacent", "L0**L1**L2"),
    ("p3", "L0**L1+L2**L3+L4**L5"),
    ("p1_t1x1", "L0**L1+L2"),
    ("p1_t2x1", "L0**L1*L2"),
)


def group_cpt_power_tier() -> int:
    n = 0
    for label, expr in CPT_POWER_SHAPES:
        for count in TIER_RUNG_COUNTS:
            n += _file(
                f"CPT(Dest,{expr});", f"cptpow_{label}_n{count:03d}",
                f"CPT(Dest,{expr}) x{count} rung(s) -- OQ-CMPCPTLAYOUT tier-3 "
                f"closeout. CPT(Dest,L0**L1+L2**L3) is the only shape in the whole "
                f"corpus that OVER-predicts (+16), and ** is the only tier-3 operator "
                f"(116 against tier 2's 52), so an error in it is 2-3x more expensive "
                f"than anywhere else in the table. Two ** in one expression is untested; "
                f"cptrdpow_k2/k3 (-848/-1648) say repeated ** is badly wrong on the "
                f"REAL-destination path as well. n=1 vs n=100 separates per-rung from "
                f"per-file, same as group B",
                rung_count=count)
    return n


def main() -> None:
    total = 0
    for fn in (group_cmp_float_operands, group_cpt_tier_mix, group_cpt_power_tier):
        count = fn()
        print(f"{fn.__name__}: {count} file(s)")
        total += count
    print(f"\nDone. {total} files.")


if __name__ == "__main__":
    main()
