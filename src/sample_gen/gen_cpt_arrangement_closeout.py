"""CPT arrangement: a non-effect, one exception, and a +348 nobody had seen.

Written 2026-09-12. The 28 captured `cptarrange_*` rows had never been
reconciled. Read against the current engine they answer the question the family
was built for, and turn up something else.

WHAT IS ANSWERED. Operator ARRANGEMENT does not change CPT cost. Four arms --
alternating, frontloaded, grouped, split -- sweep operand counts 3 to 9 with the
multiplications in completely different places, and 26 of the 28 rows land on
the IDENTICAL residual. The slopes agree exactly too: alternating n03 -> n04
steps +4,000 in both prediction and actual, n04 -> n05 steps +2,400 in both. The
arrangement-blind expression model is right.

THE ONE EXCEPTION, and it is a clean rule. Five rows sit 400 bytes higher in
actual than the other 23, and they are exactly the five whose expression begins
with TWO additions before the first multiplication:

    cptarrange_grouped_n03   L0+L1+L2*L3
    cptarrange_grouped_n04   L0+L1+L2*L3*L4
    cptarrange_split_n07     L0+L1+L2*L3*L4*L5+L6+L7
    cptarrange_split_n08     L0+L1+L2*L3*L4*L5*L6+L7+L8
    cptarrange_split_n09     L0+L1+L2*L3*L4*L5*L6+L7+L8+L9

Every other row -- including `grouped_n05` at `L0+L1+L2+L3*L4*L5` (THREE leading
additions) and `split_n03` at `L0+L1*L2+L3` (ONE) -- is in the majority group. So
the trigger is not "grouped" or "split" as a style, it is the POSITION of the
first multiplication: the third operand specifically, and no other. Two of the
four arms happen to produce that prefix at some counts and not others, which is
why it reads as arm-specific noise until the rung text is lined up.

ARM A -- `cptpos_m{1..8}_n09` plus `cptpos_add_n09`. Nine DINT operands, every
operator an addition except ONE multiplication, swept across all eight possible
positions, plus an all-addition control. Everything else is held identical:
same operand count, same tag pool, same destination, same rung count. If the
rule is "first multiplication at operand 3", `cptpos_m3_n09` stands alone and
the other seven agree. Nothing in the corpus can say that today because no
existing file varies position with the count held fixed.

THE +348. The majority residual is not zero, it is +348, identical on all 26
rows regardless of operand count -- a flat per-file over-charge, not a slope
error. The neighbouring `cptrd_*` families, same generator and same tag pool,
sit at +4. Two things differ between them and either could be the cause:

    cptarrange   destination `Dest` (DINT)   operands L0..L9 (DINT)
    cptrd        destination `R2`   (REAL)   operands R*/N* (REAL/LINT)

ARM B -- `cptdest_d{dint,real}o{dint,real}_n{010,100,1000}`. Destination type
crossed with operand type crossed with RUNG count, 12 files, expression shape
held identical at `A+B*C+D` throughout. Reading it three ways at once:
destination type across the d-arms, operand type across the o-arms, and -- the
part neither existing family can give -- whether 348 is per FILE or per RUNG,
since every captured file in both families has exactly 100 rungs and cannot
distinguish 348 once from 3.48 each.

Run: python -m sample_gen.gen_cpt_arrangement_closeout
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import rungs_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"

OPERAND_COUNT = 9           # arm A, matching cptarrange's largest point
POSITIONS = range(1, 9)     # first multiplication between operand k and k+1
RUNG_COUNTS = (10, 100, 1000)
ARM_A_RUNGS = 100           # identical to every captured cptarrange file

# The captured families' own pool, unchanged, so arm A differences straight
# against cptarrange and arm B against both it and cptrd.
_POOL = "\n".join(
    [tag_xml("R2", "REAL"), tag_xml("R0", "REAL"), tag_xml("R1", "REAL"),
     tag_xml("R3", "REAL"), tag_xml("R4", "REAL")]
    + [tag_xml(f"S{i}", "SINT") for i in range(4)]
    + [tag_xml(f"I{i}", "INT") for i in range(4)]
    + [tag_xml(f"L{i}", "DINT") for i in range(12)]
    + [tag_xml(f"N{i}", "LINT") for i in range(4)]
    + [tag_xml("Dest", "DINT")]
)

_DEST = {"dint": "Dest", "real": "R2"}
_OPERANDS = {"dint": ("L0", "L1", "L2", "L3"), "real": ("R0", "R1", "R3", "R4")}


def _expression(mul_position: int | None) -> str:
    """Nine DINT operands, all additions except one multiplication.

    `mul_position=k` puts the multiplication between operand k and k+1, so k=3
    reproduces the `L0+L1+L2*L3...` prefix that the five outlier rows share.
    `None` is the all-addition control.
    """
    ops = [f"L{i}" for i in range(OPERAND_COUNT)]
    out = ops[0]
    for i in range(1, OPERAND_COUNT):
        out += ("*" if mul_position == i else "+") + ops[i]
    return out


def _write(name: str, l5x: str, description: str) -> None:
    out = OUT / f"{name}.L5X"
    bytes_ = write_sample(l5x, out)
    append_manifest_row(name, description, "logic_instr", out, bytes_)


def arm_a_position() -> int:
    n = 0
    for pos in list(POSITIONS) + [None]:
        expr = _expression(pos)
        label = "add" if pos is None else f"m{pos}"
        rung = f"CPT(Dest,{expr});"
        _write(
            f"cptpos_{label}_n{OPERAND_COUNT:02d}",
            build_l5x(target_name=f"CptPos{label.title()}", tags_xml=_POOL,
                      extra_rungs_xml=rungs_xml(ARM_A_RUNGS, lambda _i: rung)),
            f"{ARM_A_RUNGS} rungs of {rung} -- {OPERAND_COUNT} DINT operands, every operator an "
            f"addition except "
            + ("NONE: the all-addition control." if pos is None else
               f"ONE multiplication, between operand {pos} and {pos + 1}.")
            + f" Arm A sweeps that position across all eight possibilities with operand count, tag "
            f"pool, destination and rung count all held identical. The 28 captured cptarrange_* "
            f"rows say arrangement is a NON-EFFECT -- 26 of them land on the identical residual and "
            f"their slopes agree exactly -- except five that sit 400 bytes higher, and those five "
            f"are precisely the ones whose expression begins with TWO additions before the first "
            f"multiplication (L0+L1+L2*...). grouped_n05 with THREE leading additions and "
            f"split_n03 with ONE are both in the majority, so the trigger is the POSITION of the "
            f"first multiplication rather than any arrangement style. If that reading is right, "
            f"cptpos_m3_n09 stands alone here and the other seven agree. No existing file varies "
            f"position with the count held fixed. OQ-CPTARRANGE.",
        )
        n += 1
    return n


def arm_b_dest_and_rungs() -> int:
    n = 0
    for dest_kind, dest in _DEST.items():
        for op_kind, ops in _OPERANDS.items():
            expr = f"{ops[0]}+{ops[1]}*{ops[2]}+{ops[3]}"
            rung = f"CPT({dest},{expr});"
            for count in RUNG_COUNTS:
                _write(
                    f"cptdest_d{dest_kind}o{op_kind}_n{count:05d}",
                    build_l5x(target_name=f"CptD{dest_kind[:2]}O{op_kind[:2]}{count}"[:24],
                              tags_xml=_POOL,
                              extra_rungs_xml=rungs_xml(count, lambda _i: rung)),
                    f"{count} rungs of {rung} -- a {dest_kind.upper()} destination with "
                    f"{op_kind.upper()} operands, expression shape held identical at A+B*C+D. The "
                    f"majority cptarrange residual is not zero, it is +348, identical on all 26 "
                    f"rows regardless of operand count -- a flat per-file over-charge, not a slope "
                    f"error -- while the neighbouring cptrd_* families, same generator and same "
                    f"tag pool, sit at +4. Two things differ between them: cptarrange has a DINT "
                    f"destination and DINT operands, cptrd a REAL destination and REAL/LINT "
                    f"operands. This arm crosses both and adds the RUNG count, which neither "
                    f"family can vary: every captured file in both has exactly 100 rungs, so 348 "
                    f"once and 3.48 each are indistinguishable there. OQ-CPTARRANGE.",
                )
                n += 1
    return n


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    a = arm_a_position()
    b = arm_b_dest_and_rungs()
    print(f"Arm A (first-multiplication position): {a}")
    print(f"Arm B (dest x operand x rung count):   {b}")
    print(f"Total: {a + b}")


if __name__ == "__main__":
    main()
