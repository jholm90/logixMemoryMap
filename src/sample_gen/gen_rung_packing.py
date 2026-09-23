"""OQ-RUNGSHAPE: separate the per-rung cost from the per-instruction weights.

Every calibration file the weights were fitted on carries one instruction per
rung, so a per-rung cost and a per-instruction cost are perfectly confounded
in every weight. The one earlier attempt to separate them packed OTE, an
output, and so built series-output cascades that moved in lockstep with the
rung count -- a total confound.

This family packs NON-OUTPUT instructions. The instruction count is held at
4,000 in every file and only how many sit on each rung moves: k per rung,
k in 1/2/4/8/16/40 (all divisors of 4,000), so the rung count runs 4,000 ->
100. Each rung is closed with one NOP(), the only instruction that ends a
conditional rung without writing anything, so no series outputs appear at any
k. NOP's own weight is measured exactly by the empty-rung sweep and moves one
per rung, which is the variable under test.

Two arms, so the answer does not rest on one instruction:

  rungpack_xic_k{kk}   XIC(PackBit)        -- the most common real instruction
  rungpack_equ_k{kk}   EQU(PackA,PackB)    -- a two-operand compare

Operand text is identical in every file of an arm, and the tag inventory is
fixed, so confound_check.py sees one moving dimension per consecutive pair.

What the slope says. Removing rungs removes their NOPs and whatever per-rung
cost exists. If actual bytes per removed rung equal the NOP weight the engine
already charges, the instruction weights carry no hidden per-rung share and
the per-rung term is fully inside the empty-rung measurement. If the slope is
larger, the difference is the per-rung cost that has been folded into every
instruction weight, and it is read directly, not fitted.

Run: python -m sample_gen.gen_rung_packing
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import rung_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"

TOTAL_INSTRUCTIONS = 4000
PER_RUNG = (1, 2, 4, 8, 16, 40)

ARMS = {
    "xic": ("XIC(PackBit)", [tag_xml("PackBit", "BOOL")]),
    "equ": ("EQU(PackA,PackB)", [tag_xml("PackA", "DINT"), tag_xml("PackB", "DINT")]),
}


def main() -> None:
    for arm, (instr, tags) in ARMS.items():
        for k in PER_RUNG:
            n_rungs = TOTAL_INSTRUCTIONS // k
            rungs = "\n".join(rung_xml(i, instr * k + "NOP();") for i in range(n_rungs))
            l5x = build_l5x(target_name=f"RungPack{arm.upper()}{k:02d}",
                            tags_xml="\n".join(tags), extra_rungs_xml=rungs)
            out_name = f"rungpack_{arm}_k{k:02d}"
            out_path = OUT_ROOT / f"{out_name}.L5X"
            bytes_ = write_sample(l5x, out_path)
            append_manifest_row(
                out_name,
                f"OQ-RUNGSHAPE rung-packing isolation: {TOTAL_INSTRUCTIONS} x {instr} packed {k} per "
                f"rung ({n_rungs} rungs), each rung closed by one NOP(). Instruction count, operand "
                f"text and tag inventory are identical across the arm; only rung count (and its one "
                f"NOP per rung) moves. Non-output instruction, so no series-output cascade -- the "
                f"design error that confounded the earlier OTE packing sweep.",
                "logic", out_path, bytes_)
            print(f"Wrote {out_path} ({n_rungs} rungs, predicted {bytes_} bytes)")
    print(f"\nDone. {len(ARMS) * len(PER_RUNG)} files.")


if __name__ == "__main__":
    main()
