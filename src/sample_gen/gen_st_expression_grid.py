"""ST assignment cost -- the table covers five shapes and real code uses many.

`structured_text.assignment_expression_cost` is keyed `<operators>|<dest is
REAL>` and holds exactly five measured entries:

    0|false  36      1|false  40      2|false  164
    1|true  152      5|true   452

Its confidence is literally MEASURED_SPARSE, and everything outside those
five falls back to the CPT model, which was fitted for ladder CPT and
over-predicts a 1-operator ST assignment by roughly 3x.

Scanned across the 10 real exports in samples/local: 128 ST routines,
6,586 ST lines, of which

    assign 0 ops   1,735      covered
    assign 1 op      502      covered
    assign 2 ops     392      covered
    assign 3 ops     120      NOT COVERED
    assign 4 ops      42      NOT COVERED
    assign 6 ops      26      NOT COVERED
    assign 8 ops       9      NOT COVERED
    call statements 2,094      the single largest shape, and the table
                               says nothing about it at all

So ~7% of real ST assignments are priced by a fallback that is known to be
wrong for ST, and the biggest single line shape in real ST -- a bare
function/AOI call statement -- has no entry of its own.

Three arms, all differencing against the existing `st_expr_*` captures
which used the identical 1000-statement shape and tag pool:

  A  stx_ops{NN}_{dint,real}   operator count 0..12 against BOTH destination
                               types. The table has DINT at 0/1/2 and REAL
                               at 1/5, so neither axis is complete and the
                               two cannot currently be compared at the same
                               count. This fills the grid.

  B  stx_opkind_{...}          FOUR operators every time, varying only WHICH
                               operators. The table keys on COUNT alone,
                               which assumes a multiply costs what an
                               addition costs and that AND costs what MOD
                               costs. Nothing has ever tested that; if it is
                               false the whole table is mis-parameterised.

  C  stx_call_aoi_p{N}         a bare AOI call statement in ST at 1/2/4/8
                               parameters. 2,094 real lines are call
                               statements. This is also the ST-AOI question
                               directly: an AOI called from ST rather than
                               from a rung.

Every file holds 1000 statements so the per-statement cost comes straight
out of the difference against the routine shell, the same way every
existing ST constant was derived.
"""

from __future__ import annotations

from sample_gen.builders import MemberSpec, aoi_xml, rung_xml, tag_xml
from sample_gen.gen_st_sizing import _TAGS, _st_routine, _write
from sample_gen.wrapper import build_l5x

N = 1000

# 0..12. 3/4/6/8 are the counts real code actually uses and the table
# lacks; 10 and 12 extend past them so a curve is distinguishable from a
# straight line.
OP_COUNTS = (0, 1, 2, 3, 4, 5, 6, 8, 10, 12)

AOI_NAME = "StxCallAoi"


def _expr(n_ops: int, dest_real: bool, i: int, op: str = "+") -> str:
    """One assignment with exactly n_ops binary operators."""
    src = "R" if dest_real else "D"
    dest = f"{src}{i % 10}"
    terms = [f"{src}{(i + k) % 10}" for k in range(n_ops + 1)]
    rhs = f" {op} ".join(terms) if n_ops else terms[0]
    return f"{dest} := {rhs};"


def _file(out_name: str, target: str, lines: list[str], description: str,
          extra_tags: str = "", extra_aoi: str = "") -> None:
    l5x = build_l5x(
        target_name=target,
        tags_xml=_TAGS + extra_tags,
        extra_rungs_xml=rung_xml(0, "JSR(StTarget,0);"),
        extra_routines_xml=_st_routine("StTarget", lines),
        extra_aoi_xml=extra_aoi,
    )
    _write(out_name, l5x, description)


def _arm_operator_count() -> None:
    for dest_real in (False, True):
        kind = "real" if dest_real else "dint"
        for n_ops in OP_COUNTS:
            covered = f"{n_ops}|{str(dest_real).lower()}" in (
                "0|false", "1|false", "2|false", "1|true", "5|true")
            _file(
                f"stx_ops{n_ops:02d}_{kind}",
                f"StxOps{n_ops:02d}{kind[:1].upper()}",
                [_expr(n_ops, dest_real, i) for i in range(N)],
                f"{N} ST assignments with exactly {n_ops} operator(s) and a "
                f"{'REAL' if dest_real else 'DINT'} destination. "
                + ("Reproduces an entry the table already has, so it is the "
                   "control that says this batch differences cleanly against "
                   "the existing st_expr_* captures."
                   if covered else
                   "This shape has NO entry in assignment_expression_cost and "
                   "falls back to the ladder CPT model, which over-predicts a "
                   "1-operator ST assignment about 3x.")
                + " OQ-STEXPR.",
            )


def _arm_operator_kind() -> None:
    # Four operators every time; only the operator itself changes.
    for tag, op, why in (
        ("add", "+", "the shape every existing ST expression capture used"),
        ("mul", "*", "a multiply is not obviously the same cost as an add"),
        ("div", "/", "division is the most expensive arithmetic op in the ladder weights"),
        ("mod", "MOD", "MOD has its own ladder weight and no ST entry"),
        ("and", "AND", "bitwise ops have no ST entry at any operator count"),
        ("xor", "XOR", "the other bitwise op real ST uses"),
    ):
        _file(
            f"stx_opkind_{tag}",
            f"StxOpKind{tag.title()}",
            [_expr(4, False, i, op=op) for i in range(N)],
            f"{N} ST assignments, FOUR operators in every one, all of them "
            f"'{op}'. assignment_expression_cost keys on operator COUNT alone, "
            f"which assumes every operator costs the same; differencing these "
            f"six against each other tests that assumption directly, at a "
            f"count the table does not cover anyway ({why}). OQ-STEXPR.",
        )


def _arm_call_statements() -> None:
    for n_params in (1, 2, 4, 8):
        inputs = [MemberSpec(f"InP{i:02d}", "DINT", required=True) for i in range(n_params)]
        definition, storage = aoi_xml(
            AOI_NAME,
            input_params=inputs,
            output_params=[MemberSpec("OutA", "BOOL", required=True)],
            logic_rungs_xml=rung_xml(0, "OTE(OutA);"),
        )
        args = ",".join(["StxInst"] + [f"D{i % 10}" for i in range(n_params)] + ["Bit0"])
        _file(
            f"stx_call_aoi_p{n_params:02d}",
            f"StxCallP{n_params:02d}",
            [f"{AOI_NAME}({args});" for _ in range(N)],
            f"{N} bare AOI call statements in ST, {n_params} input parameter(s) "
            f"each. A call statement is the single most common ST line shape in "
            f"the real corpus (2,094 of 6,586) and has no entry in the ST model "
            f"at all. Swept on parameter count so a per-argument term separates "
            f"from a flat per-call one, and directly answers whether an AOI "
            f"called from ST costs what one called from a rung costs. OQ-STEXPR.",
            extra_tags="\n" + tag_xml("StxInst", AOI_NAME, udt_members=storage)
                       + "\n" + tag_xml("Bit0", "BOOL"),
            extra_aoi=definition,
        )


def main() -> None:
    _arm_operator_count()
    _arm_operator_kind()
    _arm_call_statements()


if __name__ == "__main__":
    main()
