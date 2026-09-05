"""The two things standing between CPT and 100%, isolated.

James, 2026-09-04: "close cpt and get 100% accuracy. Keep in mind that ints
will use a behind the scenes conversion to dint." That hint closed the
REAL-destination path -- 47/47 captured calls exact -- but it also exposed
exactly what the existing corpus cannot answer. Both gaps below are
ONE-VARIABLE questions that the current files happen to hold constant, which
is why no amount of re-fitting the existing data resolves them.

GROUP A -- cptnarrow_* : how does the SINT/INT widening scale?
    There is exactly ONE file in the whole corpus with narrow operands in a
    REAL-destination CPT (cptrd_operand_sint: 3 SINT operands, +256/rung
    over the all-REAL control). 256/3 is not an integer, so a pure
    per-operand rate is ruled out, but per-call, per-operand-plus-block and
    per-conversion-site all fit that single point identically. The model
    currently guesses 3*40 + 136.
    These files vary ONLY the narrow-operand COUNT, 0..4, at a fixed
    3-operator shape, so the slope is read directly:
      0 narrow -> must reproduce the 244 control
      1,2,3,4  -> if the cost is per-operand the steps are equal; if it is
                  a per-call block, 1 through 4 all cost the same.
    INT is swept alongside SINT because the model assumes they behave
    identically and that has never been tested -- both are narrow, but INT
    is 16-bit and SINT 8-bit, and this project has already been burned once
    assuming two types in a set behave the same (LINT was in the int-operand
    set for exactly that reason and turned out to cost nothing).

GROUP B -- cptarrange_* : does operator ARRANGEMENT change the cost?
    Four integer-destination points sit exactly -4 from the refit two-tier
    model, and no linear model in (tier1_count, tier2_count) can reach them
    -- the system is over-determined and inconsistent. The smoking gun:
      cptmix_scaling_alternating_n05  L0+L1*L2+L3*L4     -> 228
      cptmix_scaling_grouped_n05      L0+L1+L2*L3*L4     -> 232
    Identical tier counts (2 and 2), 4 bytes apart. Yet at 11 operators the
    same alternating/grouped pair measures IDENTICALLY. So arrangement
    matters at some sizes and not others, and two files is not enough to say
    which.
    These files hold the tier counts fixed and vary only the arrangement,
    at every operator count from 3 to 9 -- alternating, fully grouped,
    front-loaded and back-loaded. If arrangement is real, the four curves
    separate and the pattern is readable; if the n=5 pair was a one-off,
    they collapse and the -4 belongs to something else entirely.

Every expression here uses the same tag pool and the same rung shape as the
existing cptmix_*/cptrd_* files, so the new numbers are directly comparable
to the old ones rather than needing their own baseline.

Run: python -m sample_gen.gen_cpt_closeout
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import rung_xml, rungs_xml, tag_xml
from sample_gen.lint import lint_or_raise
from sample_gen.manifest import append_manifest_row, predicted_bytes
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "cpt"
N_RUNGS = 100

# Same pool shape the cptrd_* files use: a REAL destination, REAL operands to
# fill the non-narrow slots, and a bank of narrow tags to swap in.
_POOL = "\n".join(
    [tag_xml("R2", "REAL"), tag_xml("R0", "REAL"), tag_xml("R1", "REAL"),
     tag_xml("R3", "REAL"), tag_xml("R4", "REAL")]
    + [tag_xml(f"S{i}", "SINT") for i in range(4)]
    + [tag_xml(f"I{i}", "INT") for i in range(4)]
    + [tag_xml(f"L{i}", "DINT") for i in range(12)]
    + [tag_xml("Dest", "DINT")]
)


def _write(l5x: str, name: str, description: str) -> None:
    out = OUT_ROOT / f"{name}.L5X"
    lint_or_raise(l5x, context=str(out))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(l5x, encoding="utf-8")
    append_manifest_row(name, description, "cpt", out, predicted_bytes(l5x))
    print(f"Wrote {out}")


def _narrow_files() -> None:
    """3-operator REAL-dest shape, narrow-operand count swept 0..4.

    The shape is the cptrd_operand_* one exactly -- `CPT(R2,A+B*C-D)` -- so
    the 0-narrow file must reproduce the existing 244/rung control, which is
    the built-in check that this batch is comparable to the old one.
    """
    for kind, prefix in (("sint", "S"), ("int", "I")):
        for k in range(5):
            slots = [f"{prefix}{i}" for i in range(k)] + ["R0", "R1", "R3", "R4"]
            a, b, c, d = slots[0], slots[1], slots[2], slots[3]
            text = f"CPT(R2,{a}+{b}*{c}-{d});"
            _write(
                build_l5x(target_name=f"Narrow{kind.upper()}{k}", tags_xml=_POOL,
                          extra_rungs_xml=rungs_xml(N_RUNGS, lambda i, t=text: t)),
                f"cptnarrow_{kind}_k{k}",
                f"{N_RUNGS} rungs of {text[:-1]} -- {k} {kind.upper()} operand(s) among 4, "
                f"REAL destination, 3 operators held fixed. Isolates whether the "
                f"narrow->DINT widening is per-operand or once per call (k=0 must "
                f"reproduce the existing 244/rung all-REAL control)",
            )


def _arrangement_files() -> None:
    """Fixed tier counts, four arrangements, operator counts 3..9.

    tier1 = '+' (ADD/SUB), tier2 = '*' (MUL/DIV/MOD). For each operator
    count the tier split is held at as close to half as possible, and only
    the ORDER of the operators changes.
    """
    for n_ops in range(3, 10):
        n2 = n_ops // 2
        n1 = n_ops - n2
        patterns = {
            "alternating": [("+" if i % 2 == 0 else "*") for i in range(n_ops)],
            "grouped": ["+"] * n1 + ["*"] * n2,
            "frontloaded": ["*"] * n2 + ["+"] * n1,
            "split": ["+"] * (n1 // 2) + ["*"] * n2 + ["+"] * (n1 - n1 // 2),
        }
        for label, ops in patterns.items():
            expr = "L0"
            for i, op in enumerate(ops):
                expr += f"{op}L{i + 1}"
            text = f"CPT(Dest,{expr});"
            t1 = sum(1 for o in ops if o == "+")
            t2 = sum(1 for o in ops if o == "*")
            _write(
                build_l5x(target_name=f"Arr{label[:4].capitalize()}{n_ops}", tags_xml=_POOL,
                          extra_rungs_xml=rungs_xml(N_RUNGS, lambda i, t=text: t)),
                f"cptarrange_{label}_n{n_ops:02d}",
                f"{N_RUNGS} rungs of {text[:-1]} -- {n_ops} operators "
                f"(tier1={t1}, tier2={t2}) arranged '{label}', DINT destination. "
                f"Tier counts held fixed across the four arrangements at this "
                f"operator count; only the order varies",
            )


def _lint_files() -> None:
    """LINT operand count 1..4 at the same fixed 3-operator REAL-dest shape.

    "A LINT operand is free" currently rests on ONE file (3 LINT operands).
    That single point is what removed LINT from the int-operand set and
    fixed a 26.79% over-prediction, so it matters, and one point cannot
    distinguish "free at any count" from "free at 3". If the cost really is
    0 these four files all reproduce the 244/rung all-REAL control exactly.
    """
    for k in range(1, 5):
        slots = [f"N{i}" for i in range(k)] + ["R0", "R1", "R3", "R4"]
        a, b, c, d = slots[0], slots[1], slots[2], slots[3]
        text = f"CPT(R2,{a}+{b}*{c}-{d});"
        _write(
            build_l5x(target_name=f"WideLINT{k}", tags_xml=_POOL,
                      extra_rungs_xml=rungs_xml(N_RUNGS, lambda i, t=text: t)),
            f"cptwide_lint_k{k}",
            f"{N_RUNGS} rungs of {text[:-1]} -- {k} LINT operand(s) among 4, REAL "
            f"destination. Confirms LINT costs 0 at EVERY count, not just at the "
            f"one count (3) the single existing file happens to use",
        )
    # Narrow AND wide together: does a LINT alongside a SINT change the
    # widening block? Nothing in the corpus mixes integer widths.
    text = "CPT(R2,S0+N0*N1-R0);"
    _write(
        build_l5x(target_name="MixWidth", tags_xml=_POOL,
                  extra_rungs_xml=rungs_xml(N_RUNGS, lambda i, t=text: t)),
        "cptwide_mixed_sint_lint",
        f"{N_RUNGS} rungs of {text[:-1]} -- 1 SINT + 2 LINT operands, REAL "
        f"destination. Nothing in the corpus mixes integer WIDTHS; tests whether "
        f"the narrow widening block is charged per call regardless of the other "
        f"operands' widths",
    )


def _realdest_arrangement_files() -> None:
    """The arrangement question again, but on the REAL-destination path.

    cptarrange_* only covers integer destinations. The REAL-dest model
    carries its own unexplained constant (a 5-operator expression measures
    328 where the ladder says 324) and it has never been tested against
    arrangement at all -- so that 328 could be the same arrangement effect
    wearing a different hat, since every existing 5-operator REAL-dest file
    happens to share a similar shape.
    """
    for n_ops in (4, 5, 6):
        n2 = n_ops // 2
        n1 = n_ops - n2
        for label, ops in {
            "alternating": [("+" if i % 2 == 0 else "*") for i in range(n_ops)],
            "grouped": ["+"] * n1 + ["*"] * n2,
        }.items():
            expr = "R0"
            for i, op in enumerate(ops):
                expr += f"{op}R{(i % 4) + 1}"
            text = f"CPT(R2,{expr});"
            _write(
                build_l5x(target_name=f"RdArr{label[:4].capitalize()}{n_ops}", tags_xml=_POOL,
                          extra_rungs_xml=rungs_xml(N_RUNGS, lambda i, t=text: t)),
                f"cptrdarrange_{label}_n{n_ops:02d}",
                f"{N_RUNGS} rungs of {text[:-1]} -- {n_ops} operators arranged "
                f"'{label}', REAL destination, all-REAL operands. Tests whether the "
                f"unexplained 5-operator +4 on the REAL-dest path is an arrangement "
                f"effect (the integer path has one) rather than an operator-count one",
            )


def _realdest_gap_files() -> None:
    """The plain holes in the REAL-dest operator ladder and pow coverage."""
    # Operator counts 7, 9, 10 -- the ladder is measured at 1-6 and 8 only,
    # and the one anomaly sits at 5, so the shape either side matters.
    for n_ops in (7, 9, 10):
        expr = "R0"
        for i in range(n_ops):
            expr += f"{'+' if i % 2 == 0 else '*'}R{(i % 4) + 1}"
        text = f"CPT(R2,{expr});"
        _write(
            build_l5x(target_name=f"RdOps{n_ops}", tags_xml=_POOL,
                      extra_rungs_xml=rungs_xml(N_RUNGS, lambda i, t=text: t)),
            f"cptrdops_n{n_ops:02d}",
            f"{N_RUNGS} rungs of {text[:-1]} -- {n_ops} operators, REAL destination. "
            f"Fills the ladder holes at 7/9/10 (measured only at 1-6 and 8)",
        )
    # Multiple POW on the REAL-dest path: every existing real-dest pow file
    # has exactly one **, so pow_extra has never been tested as a per-operator
    # rate versus a per-call one.
    for n_pow, expr in ((2, "R0**R1+R3**R4"), (3, "R0**R1+R3**R4-R1**R3")):
        text = f"CPT(R2,{expr});"
        _write(
            build_l5x(target_name=f"RdPow{n_pow}", tags_xml=_POOL,
                      extra_rungs_xml=rungs_xml(N_RUNGS, lambda i, t=text: t)),
            f"cptrdpow_k{n_pow}",
            f"{N_RUNGS} rungs of {text[:-1]} -- {n_pow} ** operators, REAL "
            f"destination. Every existing real-dest pow file has exactly ONE **, so "
            f"pow_extra has never been tested as per-operator vs per-call",
        )
    # One DINT operand -- the int-operand rate is measured at 2..5 only.
    text = "CPT(R2,L0+R1*R3-R4);"
    _write(
        build_l5x(target_name="RdDint1", tags_xml=_POOL,
                  extra_rungs_xml=rungs_xml(N_RUNGS, lambda i, t=text: t)),
        "cptrddint_k1",
        f"{N_RUNGS} rungs of {text[:-1]} -- exactly 1 DINT operand, REAL "
        f"destination. per_int_operand is measured at counts 2-5 only; k=1 "
        f"confirms the rate is linear from the bottom rather than fitted mid-range",
    )


def _intdest_floatliteral_files() -> None:
    """A float literal with an INTEGER destination -- never once tested.

    Every one of the ~97 integer-destination CPT captures has zero float
    literals, so the integer path has no float-literal term at all and
    silently charges nothing. Real logic writes `CPT(Dest,A*1.5+B)` against
    a DINT destination routinely, so this is a real hole, not a corner.
    """
    for k, expr in ((1, "L0*1.5+L1"), (2, "L0*1.5+L1*2.5"), (3, "L0*1.5+L1*2.5-L2/3.5")):
        text = f"CPT(Dest,{expr});"
        _write(
            build_l5x(target_name=f"IdFlit{k}", tags_xml=_POOL,
                      extra_rungs_xml=rungs_xml(N_RUNGS, lambda i, t=text: t)),
            f"cptidflit_k{k}",
            f"{N_RUNGS} rungs of {text[:-1]} -- {k} float literal(s), INTEGER "
            f"destination. Every existing integer-dest CPT capture has zero float "
            f"literals, so this term is completely unmeasured on that path",
        )


def main() -> None:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    _narrow_files()
    _arrangement_files()
    _lint_files()
    _realdest_arrangement_files()
    _realdest_gap_files()
    _intdest_floatliteral_files()
    print("\nDone.")


if __name__ == "__main__":
    main()
