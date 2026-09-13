"""The four things the ST assignment law assumes rather than measures.

Written 2026-09-13 (capture-batch segment 6), after the 30-file `stx_*` grid
replaced `structured_text.assignment_expression_cost` -- a five-entry table keyed
on operator COUNT, confidence MEASURED_SPARSE -- with one law:

    per_statement = base(n_operators, destination type)
                  + each operator's own CPT tier premium above tier 1
                  + 48 per INTEGER-typed NAMED source read into a REAL destination

Every one of the grid's 26 assignment and opkind rows now lands EXACTLY, and so
do all three of the shapes the old table had measured -- 152, 164 and 452 come
back from the law rather than from stored entries, which is what says the old
table was mis-parameterised rather than merely incomplete. An AOI called as a
bare statement from ST, which cost NOTHING before, is `120 + 16 per parameter`:
the same two constants as a call from a rung.

FOUR THINGS ARE STILL ASSUMED, each because every file that pins the constant
happens to hold another variable fixed:

  A. The operator premium at exactly ONE operator. Every file that measures a
     premium (stx_opkind_*, st_expr_ops2_dint) has two operators or more, and the
     one-operator row is a lookup (40 for DINT, 56 for REAL) rather than
     base-plus-rate. A single `D0 := D0 * D1;` may or may not pay the 16.
  B. The premium on the REAL row. All six opkind files write to a DINT
     destination, so a multiplicative operator's premium has never been measured
     against a REAL destination -- where the per-operator rate is already 40
     rather than 24, so the premium could plausibly scale with it.
  C. `**` and `OR`. The tier table prices `**` at 116, a premium of 80, which
     nothing in ST has tested; `OR` is absent from the table entirely and so
     falls to tier 1 alongside AND and XOR, which ARE measured there.
  D. The conversion rate for integer types other than DINT. 48 comes from DINT
     sources only (`R0 := D0 + D1;` and the cpt_mirror). A SINT or an INT source
     is a narrower conversion and a LINT a wider one.

A FIFTH item is measured and deliberately left alone: all four `stx_call_aoi_p*`
files land at +256, +260, +268 and +268 once the call law is applied -- the same
one-time ~264 a routine containing AOI calls carries in RLL (see
memory_model.yaml aoi_call_site). Group E separates per-call from per-routine for
it, which no existing file does in either language.

AND A CORRECTION, because it justified one of the arms above and was wrong.
`gen_st_expression_grid.py` states that the real corpus holds "128 ST routines,
6,586 ST lines" of which "call statements 2,094 -- the single largest shape, and
the table says nothing about it at all". Re-counted 2026-09-13 against the
current parser:

    the 16 held-out programs    26 ST routines   3,994 lines   2,499 assignments
                                 0 AOI call statements
    all 91 files in samples/local  307 routines  24,745 lines  8,099 assignments
                                82 AOI call statements

Of 758 bare call statements across all of `samples/local`, **690 are built-in
instructions** -- COP 325, CONCAT 61, JSR 46, SBR 63, RET 42, TONR 22, DTOS 17,
DELETE 15 -- every one of which the RLL instruction weight table already prices
through the routine's own `code_text`. Only 68 are AOI calls. So the genuinely
unpriced shape was real but two orders of magnitude smaller than claimed, and
segment 6 moves the sixteen real programs by essentially nothing (2.073% ->
2.074%) while moving the corpus from 1.833% to 1.545%. That gap is the honest
headline and the reason this batch is small.

GROUP A -- `stc_prem1_{add,sub,mul,div,mod,pow,and,or,xor}`, 9 files. ONE operator,
    DINT destination, 1,000 statements, varying only which operator. Against
    `stx_ops01_dint` (measured 40) each file reads that operator's premium at a
    count where the law currently applies none.

GROUP B -- `stc_premreal_{add,mul,pow}`, 3 files. FOUR operators, REAL
    destination and REAL sources so no conversion term intrudes. Differences
    straight against `stx_ops04_real` (measured 284) and against
    `stc_premdint_*`'s DINT twins in group A's idiom.

GROUP C -- `stc_opkind_{pow,or}`, 2 files. Four operators, DINT destination --
    the two entries `stx_opkind_*` left out, in the identical shape so they
    difference against its measured 196 (tier 1) and 260 (tier 2) directly.

GROUP D -- `stc_conv_{sint,int,lint,mixed}`, 4 files. One operator, REAL
    destination, both sources of one integer type, so the conversion rate is read
    per type: `R0 := S0 + S1;` against the DINT-source 152 that fixed the 48. The
    `mixed` file reads one DINT and one SINT source in the same statement, which
    says whether the rate is per source or per statement.

GROUP E -- `stc_callone_n{00010,00100,01000}`, 3 files. ONE AOI call statement
    per routine at 10, 100 and 1,000 statements of padding, so the per-call cost
    is pinned at 1 and only the routine's own size moves. Against
    `stx_call_aoi_p*` this separates the +264 one-time from anything per-call, in
    ST, for the first time in either language.

21 files, 1,000 statements each except group E, all differencing against the
existing `stx_*`/`st_*` captures with the identical tag pool and routine shape.

Run: python -m sample_gen.gen_st_closeout
"""

from __future__ import annotations

from sample_gen.builders import MemberSpec, aoi_xml, rung_xml, tag_xml
from sample_gen.gen_st_sizing import _TAGS, _st_routine, _write
from sample_gen.wrapper import build_l5x

N = 1000
CATEGORY = "st_closeout"

# Tier 1 in cpt_expression.operator_tier_costs, tier 2, tier 3, and the
# bitwise operators that table does not price at all.
ONE_OP = ("add", "sub", "mul", "div", "mod", "pow", "and", "or", "xor")
OP_TOKEN = {"add": "+", "sub": "-", "mul": "*", "div": "/", "mod": "MOD",
            "pow": "**", "and": "AND", "or": "OR", "xor": "XOR"}
CONV_TYPES = {"sint": "SINT", "int": "INT", "lint": "LINT"}

AOI_NAME = "StcCallAoi"


def _file(out_name: str, target: str, lines: list[str], description: str,
          extra_tags: str = "", extra_aoi: str = "") -> None:
    l5x = build_l5x(
        target_name=target,
        tags_xml=_TAGS + extra_tags,
        extra_rungs_xml=rung_xml(0, "JSR(StTarget,0);"),
        extra_routines_xml=_st_routine("StTarget", lines),
        extra_aoi_xml=extra_aoi,
    )
    _write(out_name, l5x, description, CATEGORY)


def _group_a() -> int:
    for label in ONE_OP:
        op = OP_TOKEN[label]
        lines = [f"D{i % 10} := D{i % 10} {op} D{(i + 1) % 10};" for i in range(N)]
        _file(
            f"stc_prem1_{label}", f"StcPrem1{label.title()}", lines,
            f"{N} single-operator ST assignments, DINT destination, operator {op}. "
            f"Group A of the ST closeout: the wired law reads a one-operator "
            f"assignment from a lookup (40 for DINT) and applies NO operator premium "
            f"there, because every file that pins a premium -- stx_opkind_* and "
            f"st_expr_ops2_dint -- has two operators or more. Against stx_ops01_dint's "
            f"measured 40 this file reads {op}'s premium at a count where the law "
            f"currently assumes none. Nine operators covers all three CPT tiers plus "
            f"the three bitwise operators that tier table does not price. OQ-STEXPR.",
        )
    return len(ONE_OP)


def _group_b() -> int:
    for label in ("add", "mul", "pow"):
        op = OP_TOKEN[label]
        lines = [
            "R{0} := R{0} {1} R{2} {1} R{3} {1} R{4} {1} R{5};".format(
                i % 10, op, (i + 1) % 10, (i + 2) % 10, (i + 3) % 10, (i + 4) % 10)
            for i in range(N)
        ]
        _file(
            f"stc_premreal_{label}", f"StcPremReal{label.title()}", lines,
            f"{N} four-operator ST assignments with a REAL destination and REAL "
            f"sources only, operator {op}. Group B of the ST closeout: all six "
            f"stx_opkind_* files write to a DINT destination, so an operator's premium "
            f"has never been measured against a REAL destination -- where the "
            f"per-operator rate is already 40 rather than 24, so the premium could "
            f"plausibly scale with it rather than staying at a flat 16. REAL sources "
            f"throughout so the integer-conversion term cannot intrude. Differences "
            f"against stx_ops04_real's measured 284. OQ-STEXPR.",
        )
    return 3


def _group_c() -> int:
    for label in ("pow", "or"):
        op = OP_TOKEN[label]
        lines = [
            "D{0} := D{0} {1} D{2} {1} D{3} {1} D{4} {1} D{5};".format(
                i % 10, op, (i + 1) % 10, (i + 2) % 10, (i + 3) % 10, (i + 4) % 10)
            for i in range(N)
        ]
        _file(
            f"stc_opkind_{label}", f"StcOpkind{label.title()}", lines,
            f"{N} four-operator ST assignments, DINT destination, operator {op} -- the "
            f"identical shape to stx_opkind_* so it differences straight against its "
            f"measured 196 for tier 1 (+, AND, XOR) and 260 for tier 2 (*, /, MOD). "
            f"Group C of the ST closeout: these are the two entries that sweep left "
            f"out. The tier table prices ** at 116, a premium of 80, which nothing in "
            f"ST has tested; OR is absent from the table entirely and so currently "
            f"falls to tier 1 beside AND and XOR. OQ-STEXPR.",
        )
    return 2


def _group_d() -> int:
    extra = "\n".join(
        tag_xml(f"{prefix}{i}", data_type)
        for prefix, data_type in (("Sx", "SINT"), ("Ix", "INT"), ("Lx", "LINT"))
        for i in range(2)
    )
    shapes = {
        "sint": ("Sx0", "Sx1"), "int": ("Ix0", "Ix1"), "lint": ("Lx0", "Lx1"),
        "mixed": ("D0", "Sx0"),
    }
    for label, (a, b) in shapes.items():
        lines = [f"R{i % 10} := {a} + {b};" for i in range(N)]
        note = (
            "one DINT and one SINT source in the same statement, which says whether "
            "the conversion rate is per SOURCE or per statement"
            if label == "mixed" else
            f"both sources {CONV_TYPES[label]}, so the conversion rate is read for "
            f"that type alone"
        )
        _file(
            f"stc_conv_{label}", f"StcConv{label.title()}", lines, extra_tags=extra,
            description=(
                f"{N} single-operator ST assignments with a REAL destination and "
                f"{note}. Group D of the ST closeout: the wired 48 bytes per "
                f"integer-typed named source read into a REAL destination comes from "
                f"DINT sources only -- st_expr_ops1_n01000 (R0 := D0 + D1, measured "
                f"152 against the 56 a pure-REAL statement costs) and the cpt_mirror. "
                f"A SINT or INT source is a narrower conversion and a LINT a wider "
                f"one, and nothing has measured any of them. Integer LITERALS "
                f"deliberately do not pay the rate, which is what makes the mirror "
                f"land exactly, so none appears here. OQ-STEXPR."
            ),
        )
    return len(shapes)


def _group_e() -> int:
    aoi_def, storage = aoi_xml(
        AOI_NAME,
        input_params=[MemberSpec("InA", "DINT", required=True)],
        output_params=[MemberSpec("OutA", "BOOL", required=True)],
        local_tags=[MemberSpec("Wrk", "DINT")],
        logic_rungs_xml=rung_xml(0, "OTE(OutA);"),
    )
    extra = tag_xml("StcInst", AOI_NAME, udt_members=storage)
    for pad in (10, 100, 1000):
        lines = [f"{AOI_NAME}(StcInst,D0,B0);"]
        lines += [f"D{i % 10} := D{i % 10} + 1;" for i in range(pad - 1)]
        _file(
            f"stc_callone_n{pad:05d}", f"StcCallOne{pad}", lines,
            extra_tags=extra, extra_aoi=aoi_def,
            description=(
                f"Exactly ONE AOI call statement in an ST routine of {pad} statements, "
                f"the rest single-operator DINT assignments already measured exactly. "
                f"Group E of the ST closeout: with the call law applied all four "
                f"stx_call_aoi_p* files land at +256 to +268, the same one-time ~264 a "
                f"routine containing AOI calls carries in RLL (memory_model.yaml "
                f"aoi_call_site) -- and no file in EITHER language separates that "
                f"one-time from anything per-call, because every existing file scales "
                f"the two together. Holding the call count at 1 while the routine grows "
                f"10x and 100x does separate them. OQ-STEXPR."
            ),
        )
    return 3


def main() -> None:
    total = _group_a() + _group_b() + _group_c() + _group_d() + _group_e()
    print(f"Total: {total}")


if __name__ == "__main__":
    main()
