"""CPT comprehensive batch (James, 2026-08-25): "you need to put priority
on getting this CPT working... I expect the next batch of generated tests
that you will have this 100% solved. no exceptions. CPT is very important."

Closes out every remaining gap identified in the CPT mining writeup
(OQ-CMPCPTLAYOUT) in one batch, reusing gen_cmpcpt_layout.py's exact
_POOL_TAGS_XML so every new file subtracts cleanly against the existing 27
real cmpcpt_* rows:

  A. group_mod_operator -- MOD is used 146 times in the real corpus
     (docs/CMP_CPT_REFERENCE.md) and had ZERO test coverage before this
     file -- the single largest real-usage gap in the whole CPT sweep, a
     bigger gap than POW (13 real uses, already tested) or ABS/ATN/TAN/SQR
     (single digits each, not attempted). Real syntax confirmed from
     corpus: `Wrk_Now.Yr MOD 100` and `(Wrk_Now.Mo+9)MOD 12` -- word
     operator with a space before the left operand's boundary, not a
     symbol. Tested at 3 rung counts (10/100/1000) so this operator gets
     the same linearity confidence as the established tiers from the
     start, not bolted on later.

  B. group_operator_n100_complete -- gen_cpt_confirm.py added an n=100
     point for barecopy/add/mul/pow but skipped sub/div (assumed same
     tier as add/mul respectively, per the mined ADD=SUB and MUL=DIV
     findings). This confirms that assumption holds at a second count
     point instead of leaving it inferred.

  C. group_n10_third_point -- every established tier (barecopy, all 5
     operators) currently has at most 2 count points (100, 1000). Two
     points can always be fit to a line; three actually tests linearity.
     Adds n=10 for all 6 shapes.

  D. group_chain_length_sweep -- the existing chain data is ONE data point
     (6-operand chain vs 2-operand baseline, both at n=1000). This adds
     operand counts 3/4/5/8/10 at n=1000 so the marginal per-operand cost
     can be fit against actual points, not extrapolated from a single
     one. Chains longer than the 8-tag pool (L0-L7, L7 reserved as dest)
     recycle earlier tags in the chain -- already-confirmed via
     group_cpt_dedup that a repeated tag reference costs the same as a
     distinct one, so this doesn't distort the operand-count signal.

  E. group_literal_linearity -- the mined int-literal (+264 flat across
     all 5 operators) and float-literal (operator-independent for
     ADD/SUB/MUL/DIV, NOT for POW) effects are both single-point findings
     at n=1000. Adds n=10/n=100 for int- and float-literal ADD to confirm
     these are genuine per-rung-independent effects and not artifacts of
     one specific count.

  F. group_compound_cmp_n100 -- second count point (n=100) for single/
     and_compound/or_compound/duplicate_cond, matching the existing
     n=1000 set, to confirm the compound-condition cost is linear too.

Run: python -m sample_gen.gen_cpt_comprehensive
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import rungs_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"

# Identical to gen_cmpcpt_layout.py's _POOL_TAGS_XML -- must match exactly
# so every subtraction against the existing 27 cmpcpt_* rows isolates only
# the variable actually under test.
_POOL_TAGS_XML = (
    "\n".join(tag_xml(f"L{i}", "DINT") for i in range(8)) + "\n"
    + "\n".join(tag_xml(f"R{i}", "REAL") for i in range(3)) + "\n"
    + tag_xml("TB0", "BOOL")
)

OPERATORS = ["+", "-", "*", "/", "**"]
_OPNAME = {"+": "add", "-": "sub", "*": "mul", "/": "div", "**": "pow"}


def _write(l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "logic_instr", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


def group_mod_operator() -> None:
    for n in [10, 100, 1000]:
        fn = lambda i: "CPT(L2,L0 MOD L1);"
        l5x = build_l5x(target_name=f"CptModN{n}", tags_xml=_POOL_TAGS_XML, extra_rungs_xml=rungs_xml(n, fn))
        _write(l5x, f"cmpcpt_cpt_op_mod_n{n:05d}",
               f"{n} rungs of CPT(L2,L0 MOD L1) -- MOD is 146/1533 real CPT calls, zero coverage before this file")


def group_operator_n100_complete() -> None:
    for op in ["-", "/"]:
        opname = _OPNAME[op]
        fn = lambda i, op=op: f"CPT(L2,L0{op}L1);"
        l5x = build_l5x(target_name=f"CptOperator{opname}N100", tags_xml=_POOL_TAGS_XML,
                         extra_rungs_xml=rungs_xml(100, fn))
        _write(l5x, f"cmpcpt_cpt_op_{opname}_n00100",
               f"100 rungs of CPT(L2,L0{op}L1) -- confirms {opname.upper()} tracks its tier-mate at a 2nd count point "
               f"(SUB=ADD, DIV=MUL per the n=1000 mining), not just assumed")


def group_n10_third_point() -> None:
    fn_bare = lambda i: "CPT(L2,L0);"
    l5x = build_l5x(target_name="CptBareCopyN10", tags_xml=_POOL_TAGS_XML, extra_rungs_xml=rungs_xml(10, fn_bare))
    _write(l5x, "cmpcpt_cpt_barecopy_n00010",
           "10 rungs of CPT(L2,L0) -- 3rd count point (10/100/1000) for genuine linearity confirmation, not just a 2-point fit")

    for op in OPERATORS:
        opname = _OPNAME[op]
        fn = lambda i, op=op: f"CPT(L2,L0{op}L1);"
        l5x = build_l5x(target_name=f"CptOperator{opname}N10", tags_xml=_POOL_TAGS_XML,
                         extra_rungs_xml=rungs_xml(10, fn))
        _write(l5x, f"cmpcpt_cpt_op_{opname}_n00010",
               f"10 rungs of CPT(L2,L0{op}L1) -- 3rd count point for the {opname.upper()} tier")


def group_chain_length_sweep() -> None:
    pool = ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]
    for length in [3, 4, 5, 8, 10]:
        operands = [pool[i % len(pool)] for i in range(length)]
        expr = "+".join(operands)
        fn = lambda i, expr=expr: f"CPT(L7,{expr});"
        l5x = build_l5x(target_name=f"CptChain{length}", tags_xml=_POOL_TAGS_XML, extra_rungs_xml=rungs_xml(1000, fn))
        _write(l5x, f"cmpcpt_cpt_chain{length}_n01000",
               f"1000 rungs of CPT(L7,{expr}) -- {length}-operand chain, operand-count scaling point "
               f"(vs 2-op baseline cmpcpt_cpt_op_add and 6-op cmpcpt_cpt_chain6)")


def group_literal_linearity() -> None:
    for n in [10, 100]:
        fn_int = lambda i: "CPT(L2,L0+5);"
        l5x = build_l5x(target_name=f"CptConstIntN{n}", tags_xml=_POOL_TAGS_XML, extra_rungs_xml=rungs_xml(n, fn_int))
        _write(l5x, f"cmpcpt_cpt_op_add_intliteral_n{n:05d}",
               f"{n} rungs of CPT(L2,L0+5) -- int-literal linearity check vs the n=1000 mined +264 flat delta")

        fn_float = lambda i: "CPT(R2,R0+5.5);"
        l5x = build_l5x(target_name=f"CptConstFloatN{n}", tags_xml=_POOL_TAGS_XML, extra_rungs_xml=rungs_xml(n, fn_float))
        _write(l5x, f"cmpcpt_cpt_op_add_floatliteral_n{n:05d}",
               f"{n} rungs of CPT(R2,R0+5.5) -- float-literal linearity check, operator-independence question")


def group_compound_cmp_n100() -> None:
    variants = {
        "single": "L0>L1",
        "and_compound": "L0>L1&&(L2<L3)",
        "or_compound": "L0>L1||(L2<L3)",
        "duplicate_cond": "L0>L1&&(L0>L1)",
    }
    for name, expr in variants.items():
        fn = lambda i, expr=expr: f"CMP({expr})OTE(TB0);"
        l5x = build_l5x(target_name=f"Cmp{name}N100", tags_xml=_POOL_TAGS_XML, extra_rungs_xml=rungs_xml(100, fn))
        _write(l5x, f"cmpcpt_cmp_{name}_n00100",
               f"100 rungs of CMP({expr}) -- 2nd count point for compound-condition linearity vs the n=1000 set")


def main() -> None:
    group_mod_operator()
    group_operator_n100_complete()
    group_n10_third_point()
    group_chain_length_sweep()
    group_literal_linearity()
    group_compound_cmp_n100()
    total = 3 + 2 + 6 + 5 + 4 + 4
    print(f"\nDone. {total} files.")


if __name__ == "__main__":
    main()
