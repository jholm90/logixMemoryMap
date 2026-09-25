"""OQ-V36MNEMONIC: the eight renamed instructions not yet built into a v36+ file.

The L9/v38 batch built and captured EQ, NE, GT, GE, LT, LE, MOVE and LIMIT at v38 --
every one imported clean and cost exactly what its v35 spelling costs. The other
eight renames (SQR->SQRT, TRN->TRUNC, XPY->EXPT, ACS->ACOS, ASN->ASIN, ATN->ATAN,
TOD->TO_BCD, FRD->BCD_TO) come from the conversion table alone. One file each:

    1756-L81E at v38.02, realism baseline, 1,000 rungs of the instruction in the
    operand shape its v35 weight was measured with (instrfirst_* / gen_logic_sweep),
    every destination a distinct array element.

A clean import says v38 takes the new name. For SQRT, TRUNC, EXPT and ATAN, whose
v35 forms carry a measured weight, the residual against the baseline's own (-1,794)
says whether the cost is unchanged. ACOS, ASIN, TO_BCD and BCD_TO have no v35 weight
on file, so their files measure the weight.

PLATFORM LINT EXEMPTION: firmware is the variable under test; target names start
"PlatNine", the prefix the L9/v38 batch already carries.

Run: python -m sample_gen.gen_v36_renames
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import rung_xml, tag_xml
from sample_gen.lint import to_v36_spelling
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.realism import with_baseline
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "v36renames"
CATEGORY = "v36_renames"
RUNGS = 1000

# v35 spelling -> (rung template, what the v35 weight was measured on)
INSTRUCTIONS = {
    "SQR": ("SQR(VrR[{i}],VrRo[{i}]);", "REAL source, REAL destination (instrfirst_sqr)"),
    "TRN": ("TRN(VrR[{i}],VrDo[{i}]);", "REAL source, DINT destination (instrfirst_trn)"),
    "XPY": ("XPY(2,VrD[{i}],VrRo[{i}]);", "literal base, DINT exponent, REAL destination (logic sweep)"),
    "ACS": ("ACS(VrR[{i}],VrRo[{i}]);", "REAL source, REAL destination; no v35 weight on file"),
    "ASN": ("ASN(VrR[{i}],VrRo[{i}]);", "REAL source, REAL destination; no v35 weight on file"),
    "ATN": ("ATN(VrR[{i}],VrRo[{i}]);", "REAL source, REAL destination (instrfirst_atn)"),
    "TOD": ("TOD(VrD[{i}],VrDo[{i}]);", "DINT source, DINT destination; no v35 weight on file"),
    "FRD": ("FRD(VrD[{i}],VrDo[{i}]);", "DINT source, DINT destination; no v35 weight on file"),
}
V36_NAME = {"SQR": "SQRT", "TRN": "TRUNC", "XPY": "EXPT", "ACS": "ACOS", "ASN": "ASIN",
            "ATN": "ATAN", "TOD": "TO_BCD", "FRD": "BCD_TO"}


def _inventory() -> str:
    return "\n".join([
        tag_xml("VrR", "REAL", (RUNGS,)), tag_xml("VrRo", "REAL", (RUNGS,)),
        tag_xml("VrD", "DINT", (RUNGS,)), tag_xml("VrDo", "DINT", (RUNGS,)),
    ])


def main() -> None:
    inventory = _inventory()
    for old, (template, basis) in INSTRUCTIONS.items():
        new = V36_NAME[old]
        sample_id = f"v36ren_{new.lower()}"
        out = OUT_ROOT / f"{sample_id}.L5X"
        rungs = "\n".join(rung_xml(i, template.format(i=i)) for i in range(RUNGS))
        l5x = to_v36_spelling(build_l5x(
            target_name=f"PlatNine_v36_{new}", major_rev="38", software_revision="38.02",
            **with_baseline(tags_xml=inventory, extra_rungs_xml=rungs)))
        assert f"{new}(" in l5x and f"{old}(" not in l5x.replace(f"{new}(", "")
        predicted = write_sample(l5x, out)
        append_manifest_row(
            sample_id,
            f"OQ-V36MNEMONIC: 1756-L81E at v38.02, realism baseline, {RUNGS} rungs of {new} "
            f"(v35 {old}), {basis}. A clean import confirms v38 accepts {new}; the residual "
            f"against the baseline's own (-1,794) gives its cost per rung.",
            CATEGORY, out, predicted)
        print(f"Wrote {out} (predicted {predicted:,})")


if __name__ == "__main__":
    main()
