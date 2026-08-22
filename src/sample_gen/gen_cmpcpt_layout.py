"""CPT/CMP operand-layout and background-optimization sweep (James,
2026-08-22): "test the cmp/cpt instructions with different quantities and
layouts of tags. Does tag**tag differ in size from tag*tag or tag-tag? Does
tag+tag+tag+tag+tag+tag line up with your estimated sizes? Is there
background optimization for cpt/CMP instructions?"

Fixed at RUNG_COUNT=1000 (same scale as gen_logic_typesweep.py, so results
are directly comparable to the already-confirmed CPT weight from the
244-file sweep: CPT(A+B) = 452 blocks/rung marginal, 4816 fixed). Own
8-DINT-tag pool (L0-L7), separate from every other sweep's pool, kept
minimal since the whole point here is isolating operator/layout/dedup
effects, not operand type (already covered by gen_logic_typesweep.py).

  A. group_cpt_operator -- same two operands (L0,L1), five different
     operators (+,-,*,/,**). Answers "does tag**tag differ from tag*tag or
     tag-tag."
  B. group_cpt_chain -- a single CPT with a 6-operand chain
     (L0+L1+L2+L3+L4+L5). Compare against group A's 2-operand '+' result:
     if CPT's cost really is per-operand, the chain's marginal cost should
     come out to roughly (operand_count-1) x (marginal_2op - fixed_dest_cost)
     -- i.e. does it "line up with your estimated sizes."
  C. group_cpt_dedup -- CPT(Dest,X+X) (literally the same tag reference
     twice) vs the group A baseline CPT(Dest,X+Y) (two different tags,
     already captured). Tests whether repeating the same tag reference
     costs less than two distinct references (a form of the "background
     optimization" question).
  D. group_cpt_noop -- CPT(Dest,X+0) (a literal zero operand that's a
     mathematical no-op) vs CPT(Dest,X) (a bare copy, no operator at all).
     Tests whether Logix folds away a provably-redundant operation or
     charges for the literal operand regardless.
  E. group_cmp_layout -- CMP(A>B) single condition, CMP(A>B&C<D) AND-joined
     compound, CMP(A>B|C<D) OR-joined compound, and CMP(A>B&A>B) (the same
     condition duplicated) -- extends the optimization question to CMP's
     boolean-expression operand instead of CPT's arithmetic one.

Run: python -m sample_gen.gen_cmpcpt_layout
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import rungs_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"
RUNG_COUNT = 1000

_POOL_TAGS_XML = "\n".join(tag_xml(f"L{i}", "DINT") for i in range(8)) + "\n" + tag_xml("TB0", "BOOL")

OPERATORS = ["+", "-", "*", "/", "**"]


def _write(l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "logic_instr", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


def group_cpt_operator() -> None:
    for op in OPERATORS:
        fn = lambda i, op=op: f"CPT(L2,L0{op}L1);"
        rungs = rungs_xml(RUNG_COUNT, fn)
        l5x = build_l5x(target_name="CptOperator", tags_xml=_POOL_TAGS_XML, extra_rungs_xml=rungs)
        opname = {"+": "add", "-": "sub", "*": "mul", "/": "div", "**": "pow"}[op]
        _write(l5x, f"cmpcpt_cpt_op_{opname}_n{RUNG_COUNT:05d}", f"{RUNG_COUNT} rungs of CPT(L2,L0{op}L1) -- operator layout sweep")


def group_cpt_chain() -> None:
    fn = lambda i: "CPT(L7,L0+L1+L2+L3+L4+L5);"
    rungs = rungs_xml(RUNG_COUNT, fn)
    l5x = build_l5x(target_name="CptChain", tags_xml=_POOL_TAGS_XML, extra_rungs_xml=rungs)
    _write(l5x, f"cmpcpt_cpt_chain6_n{RUNG_COUNT:05d}",
           f"{RUNG_COUNT} rungs of CPT(L7,L0+L1+L2+L3+L4+L5) -- 6-operand chain, vs 2-operand baseline in cmpcpt_cpt_op_add")


def group_cpt_dedup() -> None:
    fn = lambda i: "CPT(L2,L0+L0);"
    rungs = rungs_xml(RUNG_COUNT, fn)
    l5x = build_l5x(target_name="CptDedup", tags_xml=_POOL_TAGS_XML, extra_rungs_xml=rungs)
    _write(l5x, f"cmpcpt_cpt_samematag_n{RUNG_COUNT:05d}",
           f"{RUNG_COUNT} rungs of CPT(L2,L0+L0) -- same tag referenced twice, vs distinct-tag baseline in cmpcpt_cpt_op_add")


def group_cpt_noop() -> None:
    fn_zero = lambda i: "CPT(L2,L0+0);"
    rungs = rungs_xml(RUNG_COUNT, fn_zero)
    l5x = build_l5x(target_name="CptNoopZero", tags_xml=_POOL_TAGS_XML, extra_rungs_xml=rungs)
    _write(l5x, f"cmpcpt_cpt_pluszero_n{RUNG_COUNT:05d}",
           f"{RUNG_COUNT} rungs of CPT(L2,L0+0) -- mathematically-redundant +0 literal operand")

    fn_bare = lambda i: "CPT(L2,L0);"
    rungs = rungs_xml(RUNG_COUNT, fn_bare)
    l5x = build_l5x(target_name="CptBareCopy", tags_xml=_POOL_TAGS_XML, extra_rungs_xml=rungs)
    _write(l5x, f"cmpcpt_cpt_barecopy_n{RUNG_COUNT:05d}",
           f"{RUNG_COUNT} rungs of CPT(L2,L0) -- bare copy expression, no operator at all")


def group_cmp_layout() -> None:
    variants = {
        "single": "L0>L1",
        "and_compound": "L0>L1&L2<L3",
        "or_compound": "L0>L1|L2<L3",
        "duplicate_cond": "L0>L1&L0>L1",
    }
    for name, expr in variants.items():
        fn = lambda i, expr=expr: f"CMP({expr})OTE(TB0);"
        rungs = rungs_xml(RUNG_COUNT, fn)
        l5x = build_l5x(target_name=f"Cmp{name}", tags_xml=_POOL_TAGS_XML, extra_rungs_xml=rungs)
        _write(l5x, f"cmpcpt_cmp_{name}_n{RUNG_COUNT:05d}", f"{RUNG_COUNT} rungs of CMP({expr}) -- boolean-expression layout sweep")


def main() -> None:
    group_cpt_operator()
    group_cpt_chain()
    group_cpt_dedup()
    group_cpt_noop()
    group_cmp_layout()
    total = len(OPERATORS) + 1 + 1 + 2 + 4
    print(f"\nDone. {total} files.")


if __name__ == "__main__":
    main()
