"""OQ item 12 (roadmap 2026-08-22): motion instructions themselves (MAM/MAJ/
MAH/MAS/MSO/MRP), the real 2-operand call pattern confirmed against the
corpus: `MSO(Axis_BND1_Chuck_Drive,Axis_BND1_Chuck.MSO);`,
`MAH(EM48_Multichain1,MC1.Homing.MAH_Immediate);` -- (Axis, MotionInstruction
tag), same shape across every MAH/MSO/MAFR/MASR real example found. MAPC/
MCCP (camming, needs a CAM_PROFILE tag too) are NOT included here -- no real
corpus example of their call syntax turned up in the search, and this
project's own real CAM_PROFILE finding (the "voodoo" hidden-field one) means
guessing wrong here risks more than usual. Left for a follow-up once a real
reference turns up.

Real AXIS_CIP_DRIVE + MotionGroup tags copied from gen_axis_composite.py's
_AXIS_TAG_XML (same real reference already used and working there). One
shared MOTION_INSTRUCTION backing tag reused across all rungs in a given
file, same pool-reuse methodology as the main 244-file sweep.

Run: python -m sample_gen.gen_motion_instructions
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import motion_instruction_tag_xml, rungs_xml, tag_xml
from sample_gen.gen_axis_composite import _AXIS_TAG_XML
from sample_gen.lint import lint_or_raise
from sample_gen.manifest import append_manifest_row
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "axis"
COUNTS = [10, 100]

# Real 2-operand (Axis, MotionInstruction) call, confirmed for MAH/MSO/
# MAFR/MASR in the corpus.
CORPUS_CONFIRMED = {"MAH", "MSO"}

# MAM/MAJ/MAS/MRP -- FIXED 2026-08-25. James: "You need to put parameters
# in for motion instructions... you need to have all of the parameters
# populated" (the bare 2-operand call these 4 previously used built the
# rung shape MAH/MSO actually use, not theirs -- that mismatch, not a
# syntax typo, is why every rung failed). Real corpus operand COUNTS
# confirmed by reading samples/local/L5X_Samples directly (MAM=20 operands,
# MAJ=17, MAS=9, MRP=5 -- four genuinely different real shapes, not one
# family): MAM's template is James's own, given verbatim in his message
# (tag names his choice, matches the real corpus's real MAM operand
# sequence/keyword positions exactly). MAJ/MAS/MRP templates built the
# same way this project already handles NEAR_VERBATIM transplants
# elsewhere (MAPC) -- position-for-position from one real corpus example
# each, real keywords/literals kept verbatim, only tag names substituted
# with this generator's own synthetic tags:
#   MAJ, real: MAJ(Drive_Axis,Udt_Servo.MAJ,MAJ_Direction,MAJ_Velocity,
#     Units per sec,MAJ_Accel,Units per sec2,MAJ_Decel,Units per sec2,
#     Trapezoidal,Udt_Servo.MAJ_Jerk,Udt_Servo.MAJ_Jerk,% of Maximum,
#     Disabled,Programmed,0,None)
#   MAS, real: MAS(Drive_Axis,MAS,All,No,Udt_Servo.MAJ_Decel,
#     Units per sec2,No,Udt_Servo.MAJ_Jerk,% of Time)
#   MRP, real: MRP(EM40_Stacker_Virtual,Stacker.CycleReset.MRP_CarriageVirt,
#     Absolute,Actual,0)
_MOTION_RUNGS = {
    "MAM": "MAM(Axis_Cip_Drive,MotionInstr1,MoveType,Position,Speed,Units per sec,AccelRate,Units per sec2,"
           "DecelRate,Units per sec2,S-Curve,AccelJerk,DecelJerk,% of Maximum,Enabled,Programmed,LockPosn,"
           "None,EventDistance[0],CalculatedData[0]);",
    "MAJ": "MAJ(Axis_Cip_Drive,MotionInstr1,Direction,Speed,Units per sec,AccelRate,Units per sec2,DecelRate,"
           "Units per sec2,Trapezoidal,AccelJerk,DecelJerk,% of Maximum,Disabled,Programmed,0,None);",
    "MAS": "MAS(Axis_Cip_Drive,MotionInstr1,All,No,DecelRate,Units per sec2,No,DecelJerk,% of Time);",
    "MRP": "MRP(Axis_Cip_Drive,MotionInstr1,Absolute,Actual,0);",
    # Added 2026-09-05 (James: "you can do the generation for unweighted
    # instructions. MCSV is a motion instruction so be cautious it will need
    # an axis... just like the MAJ MSF etc"). Every shape below is copied
    # from a REAL call site in samples/local/, not composed from the manual
    # -- the corpus reference is given per instruction. All four are
    # single-axis, so they reuse the same Axis_Cip_Drive/MotionInstr1 pair
    # the confirmed MAH/MSO files already use.
    #
    #   MSF, real: MSF(Inp_Axis,Motion[5])
    #   MAW, real: MAW(EM108_GradingLC,Grading_LC_MAW_DataShift,Forward,0)
    #   MAR, real: MAR(Axis_BND1_Trav_Drive,Reg_MAR,Positive_Edge,Disabled,0,0,1)
    #   MDR, real: MDR(Axis_BND1_Trav_Drive,Reg_MDR,1)
    #
    # DELIBERATELY NOT ADDED, and why -- each needs structure this
    # generator does not build, and inventing it is what produced the
    # rejected alarm ConditionTypes:
    #   MAG   needs a MASTER and a SLAVE axis (real: MAG(slave,master,...))
    #   MCD   needs a real motion-instruction merge shape with 15+ operands
    #   MCS   needs a COORDINATE_SYSTEM tag
    #   MCLM  needs a COORDINATE_SYSTEM plus a target-position array
    #   MCSV  needs a CAM_PROFILE array pair (master/slave cam)
    "MSF": "MSF(Axis_Cip_Drive,MotionInstr1);",
    "MAW": "MAW(Axis_Cip_Drive,MotionInstr1,Forward,0);",
    "MAR": "MAR(Axis_Cip_Drive,MotionInstr1,Positive_Edge,Disabled,0,0,1);",
    "MDR": "MDR(Axis_Cip_Drive,MotionInstr1,1);",
}
# Extra tags MAM/MAJ/MAS/MRP's real parameter lists reference beyond the
# shared Axis_Cip_Drive/MotionInstr1 pair -- declared once, harmless if a
# given instruction's own rung text doesn't reference all of them.
_MOTION_EXTRA_TAGS_XML = "\n".join([
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
INSTRUCTIONS = ["MAM", "MAJ", "MAH", "MAS", "MSO", "MRP", "MSF", "MAW", "MAR", "MDR"]


def _write_unmodeled(l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    lint_or_raise(l5x, context=str(out_path))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(l5x, encoding="utf-8")
    append_manifest_row(out_name, f"{description} (unmodeled predefined structure)", "axis", out_path, 0)
    print(f"Wrote {out_path} (predicted N/A -- unmodeled axis structure)")


def main() -> None:
    motion_instr_tag = motion_instruction_tag_xml("MotionInstr1")
    base_tags = "\n".join([_AXIS_TAG_XML, motion_instr_tag])

    for instr in INSTRUCTIONS:
        if instr in CORPUS_CONFIRMED:
            confirmed_note = "corpus-confirmed call syntax"
            rung_text = f"{instr}(Axis_Cip_Drive,MotionInstr1);"
            # MAH/MSO's own real 2-operand call doesn't reference any of
            # _MOTION_EXTRA_TAGS_XML -- declaring them anyway would add
            # real, unused tag_overhead cost to files that already have
            # confirmed, wired real data (60 blocks/rung each), so they
            # deliberately do NOT get the extra tag pool.
            tags = base_tags
        elif instr in _MOTION_RUNGS:
            confirmed_note = "FIXED 2026-08-25 -- full real parameter list, not the bare 2-operand call that " \
                              "built as MAH/MSO's shape instead of this instruction's own and failed every rung"
            rung_text = _MOTION_RUNGS[instr]
            tags = "\n".join([base_tags, _MOTION_EXTRA_TAGS_XML])
        else:
            confirmed_note = "standard documented 2-operand signature, not independently corpus-confirmed for this exact mnemonic"
            rung_text = f"{instr}(Axis_Cip_Drive,MotionInstr1);"
            tags = base_tags
        for n in COUNTS:
            fn = lambda i, rung_text=rung_text: rung_text
            rungs = rungs_xml(n, fn)
            l5x = build_l5x(target_name=f"{instr}N{n}", tags_xml=tags, extra_rungs_xml=rungs)
            out_name = f"motioninstr_{instr.lower()}_n{n:05d}"
            _write_unmodeled(l5x, out_name, f"{n} rungs of {rung_text[:-1]} -- {confirmed_note}")

    print(f"\nDone. {len(INSTRUCTIONS) * len(COUNTS)} files.")


if __name__ == "__main__":
    main()
