"""MAM/MAJ/MAS/MRP keyword-combination validation (James, 2026-08-25):
"your next motion instruction test should be one L5X file per instruction
with one instruction each - after validating these results then we can do
a 10-pass for confirmation. you will need to investigate if we have stuff
like MAM is a merged move takes up more space compared to disabling a
merged move. something similar for MAS with use existing values compared
to using new values. you need to do investigations on syntax for these
instructions and make sure you can handle ANY combination."

Per James's explicit sequencing, this is a single-rung (n=1) validation
pass, deliberately BEFORE another rung-count sweep -- gen_motion_
instructions.py's existing n=10/n=100 files (built from ONE fixed real-
corpus-transplanted template per instruction) stay as-is, unconfirmed
until this pass validates the underlying keyword choices build clean.

Real corpus evidence (samples/local/L5X_Samples, same files read for the
original MAM/MAJ/MAS/MRP fix) for each keyword axis tested here:

  MAM -- Merge field (Enabled/Disabled): both values seen in the real
    corpus (`...S-Curve,Udt_Servo.MAJ_Jerk,Udt_Servo.MAJ_Jerk,% of
    Maximum,Disabled,Programmed,...` and James's own template used
    "Enabled"). James: does a merged move (Enabled) cost more than a
    disabled merge? Direct test.

  MAJ -- Profile field (Trapezoidal/S-Curve): both seen in the real
    corpus for MAJ specifically (2 of 3 real examples use Trapezoidal,
    1 uses S-Curve) -- same field MAM uses S-Curve for, worth confirming
    MAJ's cost doesn't depend on which profile is chosen.

  MAS -- two Yes/No fields (real corpus: `MAS(Drive_Axis,MAS,All,No,
    Udt_Servo.MAJ_Decel,Units per sec2,No,Udt_Servo.MAJ_Jerk,% of Time)`
    and `MAS(Drive_Axis,Udt_Servo.MAS_Jog,Jog,Yes,MAJ_Decel,Units per
    sec2,No,0,% of Time)`) -- James's "use existing values compared to
    using new values" maps to these: Yes = use the DecelRate/Jerk operand
    supplied in the call, No = use the axis's already-configured/existing
    value instead (the operand is still present in the text either way,
    per both real examples). Also a Stop Type field (All/Jog, both seen).
    Full 2x2x2 combination (Stop Type x Decel-Yes/No x Jerk-Yes/No) = 8
    files, all real keyword values, no guessed ones.

  MRP -- only ONE real value for the "Absolute" field ever found in the
    corpus (no alternate confirmed) -- NOT varied here, per this
    project's rule against guessing Rockwell keyword values without a
    real reference. What DOES vary in the 3 real examples is the last two
    operands (`Actual,0` vs `0,<axis>.ActualPosition`) -- both real
    patterns tested.

Run: python -m sample_gen.gen_motion_syntax_combos
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import motion_instruction_tag_xml, rung_xml, tag_xml
from sample_gen.gen_axis_composite import _AXIS_TAG_XML
from sample_gen.lint import lint_or_raise
from sample_gen.manifest import append_manifest_row
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "axis"

_EXTRA_TAGS_XML = "\n".join([
    tag_xml("MoveType", "DINT"),
    tag_xml("Direction", "DINT"),
    tag_xml("Position", "REAL"),
    tag_xml("Speed", "REAL"),
    tag_xml("AccelRate", "REAL"),
    tag_xml("DecelRate", "REAL"),
    tag_xml("AccelJerk", "REAL"),
    tag_xml("DecelJerk", "REAL"),
    tag_xml("LockPosn", "REAL"),
    tag_xml("EventDistance", "REAL", dimensions=(1,)),
    tag_xml("CalculatedData", "REAL", dimensions=(1,)),
])


def _write(l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    lint_or_raise(l5x, context=str(out_path))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(l5x, encoding="utf-8")
    append_manifest_row(out_name, f"{description} (unmodeled predefined structure)", "axis", out_path, 0)
    print(f"Wrote {out_path} (predicted N/A -- unmodeled axis structure)")


def _one_rung(instr_text: str, target_name: str, out_name: str, description: str) -> None:
    tags = "\n".join([_AXIS_TAG_XML, motion_instruction_tag_xml("MotionInstr1"), _EXTRA_TAGS_XML])
    rung = rung_xml(0, instr_text)
    l5x = build_l5x(target_name=target_name, tags_xml=tags, extra_rungs_xml=rung)
    _write(l5x, out_name, description)


def group_mam_merge() -> None:
    for merge in ["Enabled", "Disabled"]:
        instr = (f"MAM(Axis_Cip_Drive,MotionInstr1,MoveType,Position,Speed,Units per sec,AccelRate,"
                 f"Units per sec2,DecelRate,Units per sec2,S-Curve,AccelJerk,DecelJerk,% of Maximum,"
                 f"{merge},Programmed,LockPosn,None,EventDistance[0],CalculatedData[0]);")
        _one_rung(instr, f"MamMerge{merge}", f"motionsyntax_mam_merge{merge.lower()}_n01",
                  f"1 rung of MAM with Merge={merge} -- James: does a merged move cost more than a disabled merge?")


def group_maj_profile() -> None:
    for profile in ["Trapezoidal", "S-Curve"]:
        pname = profile.replace("-", "").lower()
        instr = (f"MAJ(Axis_Cip_Drive,MotionInstr1,Direction,Speed,Units per sec,AccelRate,Units per sec2,"
                 f"DecelRate,Units per sec2,{profile},AccelJerk,DecelJerk,% of Maximum,Disabled,Programmed,0,None);")
        _one_rung(instr, f"MajProfile{pname}", f"motionsyntax_maj_profile{pname}_n01",
                  f"1 rung of MAJ with Profile={profile} -- both real values confirmed in corpus")


def group_mas_combos() -> None:
    for stop_type in ["All", "Jog"]:
        for decel_yn in ["Yes", "No"]:
            for jerk_yn in ["Yes", "No"]:
                label = f"{stop_type.lower()}_decel{decel_yn.lower()}_jerk{jerk_yn.lower()}"
                instr = (f"MAS(Axis_Cip_Drive,MotionInstr1,{stop_type},{decel_yn},DecelRate,Units per sec2,"
                         f"{jerk_yn},DecelJerk,% of Time);")
                _one_rung(instr, f"MasCombo{label.title().replace('_', '')}", f"motionsyntax_mas_{label}_n01",
                          f"1 rung of MAS, StopType={stop_type}/UseNewDecel={decel_yn}/UseNewJerk={jerk_yn} -- "
                          f"James: 'use existing values compared to using new values', full combination coverage")


def group_mrp_variants() -> None:
    variants = [
        ("actualzero", "Absolute,Actual,0"),
        ("zeroactualpos", "Absolute,0,Position"),
    ]
    for label, tail in variants:
        instr = f"MRP(Axis_Cip_Drive,MotionInstr1,{tail});"
        _one_rung(instr, f"MrpVariant{label.title()}", f"motionsyntax_mrp_{label}_n01",
                  f"1 rung of MRP({tail}) -- both real operand-4/5 patterns seen in corpus")


def main() -> None:
    total = 0
    for fn in [group_mam_merge, group_maj_profile, group_mas_combos, group_mrp_variants]:
        fn()
    total = 2 + 2 + 8 + 2
    print(f"\nDone. {total} files.")


if __name__ == "__main__":
    main()
