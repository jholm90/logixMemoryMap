"""CPT MIXED-OPERATOR-TIER cost sweep (James, 2026-08-26: "Add the mixed
operator test batch for cpt instructions. Mix up to 15 operands per
expression as needed. This needs to be 100% solved closed and no
revisiting.").

Context (docs/OPEN_QUESTIONS.md OQ-CMPCPTLAYOUT): the UNIFORM case (every
operator in a CPT expression the same tier -- e.g. a straight chain of +)
is now CONFIRMED EXACT (base 88 + tier cost + 24/extra operand, 0 residual
across 24 real manifest rows). The MIXED case (more than one operator tier
in one expression) is NOT -- the engine's additive-sum fallback is off by
only ~20 bytes/call on 2 simple 3-operator test points, but off by ~150
bytes/call on a real, more complex corpus expression
((D0+D1)*R1-R2/2+1.5 -- 5 operators, 3 tiers, a literal divisor, a float
literal, REAL operands, all stacked at once). 3 data points can't isolate
which factor(s) drive that gap.

This sweep isolates each suspect factor independently instead of guessing
from one compound example, following the same "vary ONE thing, cheap n=1
single-rung files" method that solved the uniform case:

  A. group_pairwise_tier_mix -- every distinct pair of the 3 tiers
     (T1=ADD/SUB, T2=MUL/DIV/MOD, T3=POW), 2 operators/3 operands, BOTH
     orders (T1-first vs T2-first) -- isolates whether operator ORDER
     matters, not just which tiers are present (a bag-of-tiers hypothesis
     predicts order-independence; if real data disagrees, that's a real,
     needed correction). 3 pairs x 2 orders = 6 files.
  B. group_operand_count_scaling -- a FIXED tier pair (T1+T2, the same
     pair as the existing mixedops/nested points) scaled from 3 up to 15
     operands, at 2 arrangements each (alternating T1/T2/T1/T2..., vs
     grouped all-T1-then-all-T2) -- isolates the operand-COUNT scaling
     rate for a mixed expression, the mixed-case analog of the
     cptcx_operandcount sweep that solved the uniform case. 5 counts x 2
     arrangements = 10 files, directly satisfies "up to 15 operands."
  C. group_three_tier_mix -- all 3 tiers present in one expression,
     alternating arrangement, operand counts 3/5/8/10 -- the uniform-pair
     sweeps above can't reveal a 3-way interaction if one exists.
  D. group_literal_position -- a fixed 3-operand 2-tier mixed expression
     (L0+L1*L2) with an integer literal substituted at each operand
     position in turn (first/middle/last) plus the all-tag baseline --
     isolates whether literal POSITION matters within a mixed expression
     (the uniform case already confirmed literal PRESENCE alone doesn't
     matter; this checks position specifically, since the compound corpus
     expression's literal wasn't in the leading position).
  E. group_real_operand_crosscheck -- the same clean 2-tier 3-operand
     expression shape, once in DINT (already exists as cptcx_operatormix_
     mixedops) and once in REAL -- isolates whether REAL operands add a
     mixed-expression-specific cost on top of OQ-OPERANDTYPE's already-
     separately-confirmed flat per-instruction REAL surcharge, or whether
     that surcharge alone explains the difference.
  F. group_stacked_factors -- rebuilds the exact problematic corpus shape
     ((D0+D1)*R1-R2/2+1.5) as a controlled ladder, changing exactly one
     factor at a time: all-DINT/no-literal -> +int-literal -> +float-
     literal -> DINT+REAL-mixed-operands(no literal) -> the original
     REAL+literal shape -- isolates which factor(s) actually drive the
     ~150-byte/call gap instead of guessing.
  G. group_near_fifteen_operand -- 2 files near the requested ceiling: a
     3-tier, 15-operand mixed expression at n=1 (cheap, fine-grained) AND
     the SAME expression at n=100 (rung-count linearity check for a
     genuinely large mixed expression -- the original corpus expression
     was only ever captured at n=1000/5000, so its rung-linearity was
     never actually confirmed, just assumed).

Own tag pool: L0-L15 (16 DINT operands, headroom for a 15-operand chain
without reusing the destination), R0-R5 (6 REAL operands for E/F), Dest/
DestR destinations (never also an operand).

Run: python -m sample_gen.gen_cpt_mixed_operators
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import rung_xml, rungs_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"

_POOL_TAGS_XML = (
    "\n".join(tag_xml(f"L{i}", "DINT") for i in range(16)) + "\n"
    + "\n".join(tag_xml(f"R{i}", "REAL") for i in range(6)) + "\n"
    + tag_xml("Dest", "DINT") + "\n"
    + tag_xml("DestR", "REAL")
)

# Word operators (MOD) need surrounding spaces in real Logix syntax
# ("L0 MOD L1"); symbol operators (+ - * / **) don't.
_WORD_OPERATORS = {"MOD"}


def _join_expr(operands: list[str], operators: list[str]) -> str:
    """operands=[a,b,c], operators=[op1,op2] -> 'a op1 b op2 c', spacing
    each operator correctly for word vs symbol operators."""
    assert len(operands) == len(operators) + 1
    parts = [operands[0]]
    for op, operand in zip(operators, operands[1:]):
        if op in _WORD_OPERATORS:
            parts.append(f" {op} {operand}")
        else:
            parts.append(f"{op}{operand}")
    return "".join(parts)


def _write(l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "cpt_mixed_operators", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


def _one_rung_file(expr: str, target_name: str, out_name: str, description: str, dest: str = "Dest") -> None:
    instr = f"CPT({dest},{expr});"
    rungs = rung_xml(0, instr)
    l5x = build_l5x(target_name=target_name, tags_xml=_POOL_TAGS_XML, extra_rungs_xml=rungs)
    _write(l5x, out_name, f"1 rung of {instr} -- {description}")


def _n_rung_file(expr: str, n: int, target_name: str, out_name: str, description: str, dest: str = "Dest") -> None:
    fn = lambda i: f"CPT({dest},{expr});"
    rungs = rungs_xml(n, fn)
    l5x = build_l5x(target_name=target_name, tags_xml=_POOL_TAGS_XML, extra_rungs_xml=rungs)
    _write(l5x, out_name, f"{n} rungs of CPT({dest},{expr}) -- {description}")


# ---------------------------------------------------------------------------
# A. Pairwise tier mixing, both orders.
# ---------------------------------------------------------------------------

_TIERS = {"T1": "+", "T2": "*", "T3": "**"}


def group_pairwise_tier_mix() -> int:
    n = 0
    pairs = [("T1", "T2"), ("T1", "T3"), ("T2", "T3")]
    for a, b in pairs:
        op_a, op_b = _TIERS[a], _TIERS[b]
        # order 1: a-tier operator first
        expr1 = _join_expr(["L0", "L1", "L2"], [op_a, op_b])
        _one_rung_file(
            expr1, f"CptPair{a}{b}First", f"cptmix_pair_{a.lower()}{b.lower()}_{a.lower()}first",
            f"pairwise tier mix {a}+{b}, {a}-tier operator first -- operator-order isolation",
        )
        n += 1
        # order 2: b-tier operator first
        expr2 = _join_expr(["L0", "L1", "L2"], [op_b, op_a])
        _one_rung_file(
            expr2, f"CptPair{a}{b}Second", f"cptmix_pair_{a.lower()}{b.lower()}_{b.lower()}first",
            f"pairwise tier mix {a}+{b}, {b}-tier operator first -- operator-order isolation",
        )
        n += 1
    return n


# ---------------------------------------------------------------------------
# B. Operand-count scaling for a fixed T1+T2 mix, 2 arrangements, up to 15.
# ---------------------------------------------------------------------------

def group_operand_count_scaling() -> int:
    n = 0
    for count in [3, 5, 8, 11, 15]:
        operands = [f"L{i}" for i in range(count)]

        # Alternating: +,*,+,*,... (T1,T2,T1,T2,...)
        alt_ops = [("+" if i % 2 == 0 else "*") for i in range(count - 1)]
        expr_alt = _join_expr(operands, alt_ops)
        _one_rung_file(
            expr_alt, f"CptMixAltN{count:02d}", f"cptmix_scaling_alternating_n{count:02d}",
            f"{count}-operand T1/T2-alternating mix -- mixed-expression operand-count scaling",
        )
        n += 1

        # Grouped: all T1 (+) first, then all T2 (*) -- same operator bag
        # and same operand count as "alternating" above, different order.
        half = (count - 1) // 2
        grouped_ops = ["+"] * half + ["*"] * (count - 1 - half)
        expr_grp = _join_expr(operands, grouped_ops)
        _one_rung_file(
            expr_grp, f"CptMixGrpN{count:02d}", f"cptmix_scaling_grouped_n{count:02d}",
            f"{count}-operand T1-then-T2-grouped mix -- same operator bag as the alternating "
            f"n{count:02d} point, tests whether arrangement (not just which tiers/how many) matters",
        )
        n += 1
    return n


# ---------------------------------------------------------------------------
# C. All-3-tier mix, alternating, several operand counts.
# ---------------------------------------------------------------------------

def group_three_tier_mix() -> int:
    n = 0
    for count in [3, 5, 8, 10]:
        operands = [f"L{i}" for i in range(count)]
        tiers = ["+", "*", "**"]
        ops = [tiers[i % 3] for i in range(count - 1)]
        expr = _join_expr(operands, ops)
        _one_rung_file(
            expr, f"CptMix3TierN{count:02d}", f"cptmix_threetier_n{count:02d}",
            f"{count}-operand all-3-tier (+,*,**) alternating mix -- 3-way tier interaction",
        )
        n += 1
    return n


# ---------------------------------------------------------------------------
# I. All-3-tier scaling extension, up to 15 operands (2026-08-27 follow-up,
# James: "run all available tests on 4b at this time").
#
# group_three_tier_mix above only went to 10 operands -- every OTHER
# tier-pair scaling sweep in this file (Groups B and H) went all the way
# to 15, per James's original "mix up to 15 operands per expression"
# instruction. The all-3-tier case was the one left short. Real captured
# data at n=3/5/8/10 already showed "doesn't fit any simple model tried"
# (see OQ-CMPCPTLAYOUT) -- these 2 extra points (11, 15) extend the same
# alternating (+,*,**) pattern already used for the first 4, giving 6
# total count points instead of 4 for whatever formula search comes next,
# and directly closes the "up to 15" gap for this one remaining tier
# combination.
# ---------------------------------------------------------------------------

def group_three_tier_scaling_extended() -> int:
    n = 0
    for count in [11, 15]:
        operands = [f"L{i}" for i in range(count)]
        tiers = ["+", "*", "**"]
        ops = [tiers[i % 3] for i in range(count - 1)]
        expr = _join_expr(operands, ops)
        _one_rung_file(
            expr, f"CptMix3TierN{count:02d}", f"cptmix_threetier_n{count:02d}",
            f"{count}-operand all-3-tier (+,*,**) alternating mix -- extends group_three_tier_mix's "
            f"n=3/5/8/10 points to the full 15-operand range every other tier-pair scaling sweep in "
            f"this file already covers",
        )
        n += 1
    return n


# ---------------------------------------------------------------------------
# D. Literal position within a fixed 3-operand 2-tier mixed expression.
# ---------------------------------------------------------------------------

def group_literal_position() -> int:
    n = 0
    variants = {
        "alltag_baseline": "L0+L1*L2",
        "literal_first": "5+L1*L2",
        "literal_middle": "L0+5*L2",
        "literal_last": "L0+L1*5",
    }
    for name, expr in variants.items():
        _one_rung_file(
            expr, f"CptMixLitPos{name.title().replace('_', '')}", f"cptmix_litpos_{name}",
            f"literal-operand position sweep on a fixed 2-tier mixed expression -- {name}",
        )
        n += 1
    return n


# ---------------------------------------------------------------------------
# E. REAL vs DINT operand cross-check on a clean mixed-tier shape.
# ---------------------------------------------------------------------------

def group_real_operand_crosscheck() -> int:
    n = 0
    # DINT version deliberately duplicates cptcx_operatormix_mixedops'
    # shape (L0+L1*L2, though that file used 4 operands/L0+L1-L2*L3 --
    # here 3 operands to exactly match the REAL version below) so the two
    # differ ONLY in operand type, nothing else.
    _one_rung_file(
        "L0+L1*L2", "CptMixRealcheckDint", "cptmix_realcheck_dint",
        "2-tier 3-operand mixed expression, DINT operands -- REAL-vs-DINT cross-check baseline",
    )
    n += 1
    _one_rung_file(
        "R0+R1*R2", "CptMixRealcheckReal", "cptmix_realcheck_real",
        "2-tier 3-operand mixed expression, REAL operands -- REAL-vs-DINT cross-check",
        dest="DestR",
    )
    n += 1
    return n


# ---------------------------------------------------------------------------
# F. Stacked-factors ladder, rebuilding the exact problematic corpus shape
#    one factor at a time: (D0+D1)*R1-R2/2+1.5
# ---------------------------------------------------------------------------

def group_stacked_factors() -> int:
    n = 0
    variants = [
        ("alldint_noliteral", "(L0+L1)*L2-L3/L4+L5", "Dest",
         "all-DINT, no literal -- pure structural shape of the corpus expression"),
        ("dint_intliteral", "(L0+L1)*L2-L3/2+5", "Dest",
         "all-DINT + int literal (divisor position + trailing) -- adds literals only"),
        ("dint_floatliteral", "(L0+L1)*L2-L3/2.0+1.5", "DestR",
         "all-DINT operands + float literals -- adds float literal only, no REAL operands"),
        ("mixed_dint_real_noliteral", "(L0+L1)*R1-R2/L4+L5", "DestR",
         "DINT+REAL mixed operands, no literal -- adds REAL-operand mixing only"),
        ("original_shape", "(L0+L1)*R1-R2/2+1.5", "DestR",
         "the exact original corpus shape -- DINT+REAL mixed, int literal divisor, float literal"),
    ]
    for name, expr, dest, desc in variants:
        _one_rung_file(expr, f"CptMixStacked{name.title().replace('_', '')}", f"cptmix_stacked_{name}",
                        desc, dest=dest)
        n += 1
    return n


# ---------------------------------------------------------------------------
# G. Near-15-operand 3-tier mix, n=1 and n=100 for rung-count linearity.
# ---------------------------------------------------------------------------

def group_near_fifteen_operand() -> int:
    n = 0
    operands = [f"L{i}" for i in range(15)]
    tiers = ["+", "*", "**"]
    ops = [tiers[i % 3] for i in range(14)]
    expr = _join_expr(operands, ops)

    _one_rung_file(
        expr, "CptMix15N1", "cptmix_fifteen_n00001",
        "15-operand all-3-tier alternating mix, single rung -- upper-bound complexity point",
    )
    n += 1
    _n_rung_file(
        expr, 100, "CptMix15N100", "cptmix_fifteen_n00100",
        "15-operand all-3-tier alternating mix, 100 rungs -- rung-count linearity check for a "
        "genuinely large mixed expression (the original corpus expression was never confirmed "
        "linear below n=1000)",
    )
    n += 1
    return n


# ---------------------------------------------------------------------------
# H. T1T3 and T2T3 operand-count scaling (2026-08-26 follow-up).
#
# The T1(ADD/SUB)+T2(MUL/DIV/MOD) pair got the full Group B treatment
# (3/5/8/11/15 operands) and came back SOLVED: 100 + 32*operator_count,
# 4/5 points exact. The 2 remaining tier pairs -- T1T3(ADD/SUB+POW) and
# T2T3(MUL/DIV/MOD+POW) -- only have a single 2-operand data point each
# (both =288, from group_pairwise_tier_mix above) with no operand-count
# scaling data at all, so no per-operator rate can be derived for either
# yet. This mirrors group_operand_count_scaling exactly, just swapping
# which two tiers alternate, to close that gap the same way T1T2 got
# closed. Alternating arrangement only -- T1T2 already confirmed
# arrangement doesn't matter, no reason to expect these 2 pairs differ.
# ---------------------------------------------------------------------------

def group_t1t3_t2t3_scaling() -> int:
    n = 0
    pairs = {"t1t3": ("+", "**"), "t2t3": ("*", "**")}
    for pair_name, (op_a, op_b) in pairs.items():
        for count in [3, 5, 8, 11, 15]:
            operands = [f"L{i}" for i in range(count)]
            ops = [(op_a if i % 2 == 0 else op_b) for i in range(count - 1)]
            expr = _join_expr(operands, ops)
            _one_rung_file(
                expr, f"CptMix{pair_name.title()}AltN{count:02d}",
                f"cptmix_scaling_{pair_name}_alternating_n{count:02d}",
                f"{count}-operand {pair_name.upper()}-alternating mix -- operand-count scaling for "
                f"the pair T1T2 got (100+32k), to see if the same or a different rate/formula applies "
                f"here (2-operand point already shows {pair_name.upper()}=288, different from T1T2's "
                f"164, so a different base and/or rate is expected, not assumed identical)",
            )
            n += 1
    return n


if __name__ == "__main__":
    total = 0
    total += group_pairwise_tier_mix()
    total += group_operand_count_scaling()
    total += group_three_tier_mix()
    total += group_literal_position()
    total += group_real_operand_crosscheck()
    total += group_stacked_factors()
    total += group_near_fifteen_operand()
    total += group_t1t3_t2t3_scaling()
    print(f"\nTotal files: {total}")
