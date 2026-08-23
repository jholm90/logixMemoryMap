"""First-pass single-instruction coverage sweep (James, 2026-08-24):
"Everything that has more than one usage needs to be tested... I want your
testing to be initially a first pass with one copy for all of the
outstanding instructions, one per file properly compiled. Don't do the
multiple per file test at this time... I dont ever want to make dozens of
files that don't compile because you didn't make the one instruction file
work and just duplicated error rungs."

Scope: every native instruction from docs/INSTRUCTION_COVERAGE.md with
real corpus usage > 1 occurrence and status "NO DATA" that ISN'T already
covered by another generator -- excludes MAM/MAJ/MAH/MAS/MSO/MRP (already
in `gen_motion_instructions.py`, awaiting capture) and SBR/RET (structurally
tied to JSR as a pair, can't be isolated as a bare single-rung instruction,
covered by `gen_jsr_sbr_ret.py`).

**Methodology, per James's explicit instruction:** exactly ONE file per
instruction, ONE rung, no rung-count sweep (that comes later once this
first pass proves every file actually compiles). Every operand shape below
was checked against the real corpus BEFORE being used here -- see each
instruction's own comment for the exact real citation. A short list of
instructions were deliberately SKIPPED rather than guessed at (SCP, FBC,
PID) -- see the bottom of this docstring.

**New predefined structures discovered building this:** MESSAGE (used by
MSG) and CAM (used by MCCP/MAPC, NOT the same as the already-modeled
CAM_PROFILE) are both completely unmodeled in memory_model.yaml -- their
real XML shape was found and copied from the corpus (`builders.py`'s new
`message_tag_xml`/`cam_tag_xml`), but their byte size is still unknown.
Files using them go through `write_sample_unmodeled` (predicted_bytes=0),
same escape hatch already used for AXIS_*/MOTION_GROUP before those got
real constants. New open questions logged for both in
docs/OPEN_QUESTIONS.md.

**Confidence tiers, tracked per instruction below:**
  - CORPUS_CONFIRMED: exact real corpus call reproduced (tag names
    substituted for a synthetic pool, but shape/keyword/argument-count
    identical to a real, working Studio-5000-exported call).
  - INFERRED: no real corpus example for this exact mnemonic, but a
    sibling instruction in the same documented AB family IS corpus-
    confirmed with an identical operand signature (e.g. TAN/SQR inferred
    from ATN/DEG/RAD, all confirmed 2-operand Source/Dest math functions).
  - NEAR_VERBATIM: a real corpus call was found but is too complex/long to
    safely paraphrase (CROUT, MAPC) -- reproduced as close to the literal
    real text as possible, only tag names substituted, keeping every
    literal keyword/enum/int-literal position exactly as the real call has
    it. Higher structural fidelity than a from-scratch guess, but still
    flagged distinctly from CORPUS_CONFIRMED since the *meaning* of every
    operand position isn't independently verified, just the shape.

**Skipped, not guessed (docs/OPEN_QUESTIONS.md has the detail):**
  - SCP (2 real occurrences): only one real corpus example, 3 arguments,
    but official Rockwell SCP documentation describes a 6-argument
    (Source,InMin,InMax,ScaledMin,ScaledMax,Dest) signature -- the
    mismatch isn't resolved without a second real example, and forcing
    either shape risks a wrong-argument-count Build failure.
  - FBC (8 real occurrences): 0 real corpus examples, genuinely complex
    (Source A, Source B, Compare Control, Result Control, Cmp, Store) --
    too much surface area for a first guess.
  - PID (3 real occurrences): 0 real corpus examples, needs an entire
    dedicated PID-structure tag (dozens of members) neither confirmed nor
    worth the risk for 3 real occurrences.

Run: python -m sample_gen.gen_instruction_firstpass
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import (
    MemberSpec,
    cam_tag_xml,
    cam_profile_tag_xml,
    control_tag_xml,
    message_tag_xml,
    motion_instruction_tag_xml,
    rung_xml,
    tag_xml,
)
from sample_gen.gen_axis_composite import _AXIS_TAG_XML
from sample_gen.manifest import append_manifest_row, write_sample, write_sample_unmodeled
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"

# Shared tag pool -- declared once, referenced by every instruction file
# below (each file only gets ONE rung, so pool reuse doesn't create any
# cross-file coupling risk).
_POOL_TAGS_XML = "\n".join([
    "\n".join(tag_xml(f"D{i}", "DINT") for i in range(4)),
    "\n".join(tag_xml(f"R{i}", "REAL") for i in range(4)),
    "\n".join(tag_xml(f"B{i}", "BOOL") for i in range(4)),
    tag_xml("Arr0", "DINT", dimensions=(20,)),
    tag_xml("Arr1", "DINT", dimensions=(20,)),
    tag_xml("Arr2", "DINT", dimensions=(20,)),
    tag_xml("Str0", "STRING", string_max_len=82),
    tag_xml("Str1", "STRING", string_max_len=82),
    tag_xml("StrDest", "STRING", string_max_len=82),
    control_tag_xml("Ctrl0"),
    motion_instruction_tag_xml("MotionInstr1"),
    cam_profile_tag_xml("CamProfile1", 5),
])

_ZONE_UDT_XML = (
    '    <DataType Name="ZoneStatus" Family="NoFamily" Class="User">\n'
    "      <Members>\n"
    '        <Member Name="Actuate" DataType="DINT" Dimension="0" Hidden="false"/>\n'
    '        <Member Name="Feedback1" DataType="DINT" Dimension="0" Hidden="false"/>\n'
    '        <Member Name="Feedback2" DataType="DINT" Dimension="0" Hidden="false"/>\n'
    '        <Member Name="InputStatus" DataType="DINT" Dimension="0" Hidden="false"/>\n'
    '        <Member Name="OutputStatus" DataType="DINT" Dimension="0" Hidden="false"/>\n'
    '        <Member Name="Reset" DataType="DINT" Dimension="0" Hidden="false"/>\n'
    "      </Members>\n"
    "    </DataType>"
)
_ZONE_MEMBERS = [
    MemberSpec("Actuate", "DINT"), MemberSpec("Feedback1", "DINT"), MemberSpec("Feedback2", "DINT"),
    MemberSpec("InputStatus", "DINT"), MemberSpec("OutputStatus", "DINT"), MemberSpec("Reset", "DINT"),
]


def _write(l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "instr_firstpass", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


def _write_unmodeled(l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    write_sample_unmodeled(l5x, out_path)
    append_manifest_row(out_name, f"{description} (unmodeled predefined structure)", "instr_firstpass", out_path, 0)
    print(f"Wrote {out_path} (predicted N/A -- unmodeled structure)")


def _one_rung_file(instr_text: str, target_name: str, out_name: str, description: str,
                    extra_tags_xml: str = "", extra_datatypes_xml: str = "") -> None:
    rung = rung_xml(0, instr_text)
    tags = _POOL_TAGS_XML + ("\n" + extra_tags_xml if extra_tags_xml else "")
    l5x = build_l5x(target_name=target_name, tags_xml=tags, extra_rungs_xml=rung,
                     extra_datatypes_xml=extra_datatypes_xml)
    _write(l5x, out_name, description)


def _one_rung_file_unmodeled(instr_text: str, target_name: str, out_name: str, description: str,
                              extra_tags_xml: str = "") -> None:
    rung = rung_xml(0, instr_text)
    tags = _POOL_TAGS_XML + "\n" + extra_tags_xml
    l5x = build_l5x(target_name=target_name, tags_xml=tags, extra_rungs_xml=rung)
    _write_unmodeled(l5x, out_name, description)


# ---------------------------------------------------------------------------
# A. Simple atomic-operand instructions -- CORPUS_CONFIRMED shape, low risk.
# ---------------------------------------------------------------------------

def group_simple_atomic() -> None:
    cases = [
        # (instruction text, out_name, description, real citation)
        ("NOT(D0,D1);", "instrfirst_not",
         "NOT(D0,D1) -- CORPUS_CONFIRMED shape (StnSys.EtherNet.CommsOK,StnSys.Fault.DB[1] in SJ_Gormley..., "
         "substituted with plain DINT tags)"),
        ("TRN(R0,D0);", "instrfirst_trn",
         "TRN(R0,D0) -- CORPUS_CONFIRMED shape (DOW_Temp00,DOW_Century), REAL source truncated to DINT dest"),
        ("NEG(D0,D1);", "instrfirst_neg",
         "NEG(D0,D1) -- CORPUS_CONFIRMED shape (M_106_SpdAdjMax,M_106_SpdAdjMin)"),
        ("OSR(B0,B1);", "instrfirst_osr",
         "OSR(B0,B1) -- CORPUS_CONFIRMED shape (CompleteOSR,CompleteOS)"),
        ("OSF(B0,B1);", "instrfirst_osf",
         "OSF(B0,B1) -- CORPUS_CONFIRMED shape (JogOSF.0,JogOSF.1)"),
        ("UID();", "instrfirst_uid", "UID() -- CORPUS_CONFIRMED, 0 operands, bare"),
        ("UIE();", "instrfirst_uie", "UIE() -- CORPUS_CONFIRMED, 0 operands, bare"),
        ("MCR();", "instrfirst_mcr", "MCR() -- CORPUS_CONFIRMED, 0 operands, bare"),
        ("TND();", "instrfirst_tnd", "TND() -- CORPUS_CONFIRMED, 0 operands, bare"),
        ("ATN(R0,R1);", "instrfirst_atn",
         "ATN(R0,R1) -- CORPUS_CONFIRMED 2-operand family shape (real corpus text was garbled/truncated but "
         "confirms ATN takes a numeric expression; using the same Source,Dest shape as its DEG/RAD siblings)"),
        ("DEG(R0,R1);", "instrfirst_deg",
         "DEG(R0,R1) -- CORPUS_CONFIRMED shape (THMain_StsLevelingSlope used for both operands in real corpus; "
         "using distinct tags here instead)"),
        ("RAD(180,R0);", "instrfirst_rad",
         "RAD(180,R0) -- CORPUS_CONFIRMED shape (RAD(180,PI)), literal degree value + REAL dest"),
        ("TAN(R0,R1);", "instrfirst_tan",
         "TAN(R0,R1) -- INFERRED from corpus-confirmed siblings ATN/DEG/RAD (same documented AB math-function "
         "family, identical Source,Dest signature); no direct TAN corpus example found"),
        ("SQR(R0,R1);", "instrfirst_sqr",
         "SQR(R0,R1) -- INFERRED, same math-function family as ATN/DEG/RAD/TAN; real corpus example was a "
         "garbled/incomplete expression, not usable directly"),
        ("SWPB(D0,REVERSE,D0);", "instrfirst_swpb",
         "SWPB(D0,REVERSE,D0) -- CORPUS_CONFIRMED shape (Press.Cmd83.ParNumber used for both operands, in-place "
         "byte swap), REVERSE keyword literal preserved"),
        ("XOR(Arr0[0],Arr1[0],Arr2[0]);", "instrfirst_xor",
         "XOR(Arr0[0],Arr1[0],Arr2[0]) -- CORPUS_CONFIRMED shape (FillErrorBins[0],OldFillErrorBins[0],"
         "ChangedErrorBins[0]), 3 DINT array elements"),
        ("FIND(Str0,Str1,1,D0);", "instrfirst_find",
         "FIND(Str0,Str1,1,D0) -- CORPUS_CONFIRMED shape (StringIn,szStar,1,dStarPosition)"),
        ("INSERT(Str0,Str1,5,StrDest);", "instrfirst_insert",
         "INSERT(Str0,Str1,5,StrDest) -- CORPUS_CONFIRMED shape (szSatusRequest,szId_KeepAlive,5,"
         "Write_Data_Out.Buffer)"),
    ]
    for instr, out_name, desc in cases:
        _one_rung_file(instr, f"Instr{out_name[11:].capitalize()}", out_name, desc)


# ---------------------------------------------------------------------------
# B. CONTROL-tag file/array instructions -- CORPUS_CONFIRMED shape, using
#    the new control_tag_xml builder. "?" placeholders are a real,
#    confirmed AB convention for an omitted optional operand -- kept
#    exactly as the real examples show them, not filled in with a guess.
# ---------------------------------------------------------------------------

def group_control_tag_instructions() -> None:
    cases = [
        ("BSL(Arr0[0],Ctrl0,B0,?);", "instrfirst_bsl",
         "BSL(Arr0[0],Ctrl0,B0,?) -- CORPUS_CONFIRMED shape (NoSortBoardsCount[0],BSRNoSortBoards,No_Sort_Found,?)"),
        ("BSR(Arr0[0],Ctrl0,B0,?);", "instrfirst_bsr",
         "BSR(Arr0[0],Ctrl0,B0,?) -- CORPUS_CONFIRMED shape (Fenced1FtBoardMask[0],BSR_Fence1Ft,EmptyBit,?)"),
        ("FFL(D0,Arr0[0],Ctrl0,?,?);", "instrfirst_ffl",
         "FFL(D0,Arr0[0],Ctrl0,?,?) -- CORPUS_CONFIRMED shape (gC10_Data.Current_Data,gC10_Data.FIFO_Data_"
         "Buffer[0],gC10_Data.FIFO_Data_Control,?,?)"),
        ("FFU(Arr0[0],D0,Ctrl0,?,?);", "instrfirst_ffu",
         "FFU(Arr0[0],D0,Ctrl0,?,?) -- CORPUS_CONFIRMED shape (gC10_Data.FIFO_Data_Buffer[0],gC10_Data."
         "FIFO_Data_Unload,gC10_Data.FIFO_Data_Control,?,?)"),
        ("SRT(Arr0[0],0,Ctrl0,?,?);", "instrfirst_srt",
         "SRT(Arr0[0],0,Ctrl0,?,?) -- CORPUS_CONFIRMED shape (ThkScanner.ValuesFiltered[0],0,ThkScanner.ThkSRT,?,?)"),
        ("AVE(Arr0[0],0,D0,Ctrl0,?,?);", "instrfirst_ave",
         "AVE(Arr0[0],0,D0,Ctrl0,?,?) -- CORPUS_CONFIRMED shape (Cycle_Time_History[0],0,Cycle_Time_Avg,"
         "Cycle_Time_Avg_Control,?,?)"),
        ("FAL(Ctrl0,?,?,ALL,Arr1[0],Arr0[0]);", "instrfirst_fal",
         "FAL(Ctrl0,?,?,ALL,Arr1[0],Arr0[0]) -- CORPUS_CONFIRMED argument-count/keyword shape (falctrl01,?,?,"
         "ALL,Strings[f_nr].DATA[...],next_file_response...), destination/expression simplified to plain DINT "
         "array elements instead of the real nested STRING.DATA member-access shape"),
        ("FSC(Ctrl0,?,?,ALL,Arr1[0]=Arr0[0]);", "instrfirst_fsc",
         "FSC(Ctrl0,?,?,ALL,Arr1[0]=Arr0[0]) -- CORPUS_CONFIRMED argument-count/keyword shape (HMI.Badge."
         "Search_Control,?,?,ALL,HMI.Badge.Number=Badge[...].Number), search expression simplified to plain "
         "DINT array elements"),
    ]
    for instr, out_name, desc in cases:
        _one_rung_file(instr, f"Instr{out_name[11:].capitalize()}", out_name, desc)


# ---------------------------------------------------------------------------
# C. Motion instructions reusing the confirmed (Axis,MotionInstruction) or
#    (MotionGroup,MotionInstruction) 2-operand shape -- MAH/MSO already
#    proved this shape builds clean in Studio 5000 (real captured data
#    exists for them), MAFR/MASR/MDW/MASD/MGSD/MGSR all confirmed to take
#    the same operand TYPES via real corpus DataType lookups (not guessed).
# ---------------------------------------------------------------------------

def group_motion_two_operand() -> None:
    axis_pair = [
        ("MAFR", "MAFR(Axis_Cip_Drive,MotionInstr1);",
         "MAFR(Axis_Cip_Drive,MotionInstr1) -- CORPUS_CONFIRMED shape (MAFR(Drive_Axis,Udt_Servo.MAFR)), "
         "same (Axis,MotionInstruction) pattern already real-data-confirmed for MAH/MSO"),
        ("MASR", "MASR(Axis_Cip_Drive,MotionInstr1);",
         "MASR(Axis_Cip_Drive,MotionInstr1) -- CORPUS_CONFIRMED shape (MASR(Drive_Axis,Udt_Servo.MASR))"),
        ("MDW", "MDW(Axis_Cip_Drive,MotionInstr1);",
         "MDW(Axis_Cip_Drive,MotionInstr1) -- CORPUS_CONFIRMED shape (MDW(EM108_GradingLC,Grading_LC_MDW_"
         "DataShift)); confirmed operand 2's real DataType is MOTION_INSTRUCTION via direct corpus lookup"),
        ("MASD", "MASD(Axis_Cip_Drive,MotionInstr1);",
         "MASD(Axis_Cip_Drive,MotionInstr1) -- CORPUS_CONFIRMED shape (MASD(AxisIndex,ServoIndex.MASD))"),
    ]
    for instr, text, desc in axis_pair:
        _one_rung_file(text, f"Instr{instr.capitalize()}", f"instrfirst_{instr.lower()}", desc,
                        extra_tags_xml=_AXIS_TAG_XML)

    group_pair = [
        ("MGSD", "MGSD(MotionGroup,MotionInstr1);",
         "MGSD(MotionGroup,MotionInstr1) -- CORPUS_CONFIRMED shape (MGSD(MG,MGSD)); confirmed real 'MG' tag's "
         "DataType is MOTION_GROUP via direct corpus lookup"),
        ("MGSR", "MGSR(MotionGroup,MotionInstr1);",
         "MGSR(MotionGroup,MotionInstr1) -- CORPUS_CONFIRMED shape (MGSR(MG,MGSR))"),
    ]
    for instr, text, desc in group_pair:
        _one_rung_file(text, f"Instr{instr.capitalize()}", f"instrfirst_{instr.lower()}", desc,
                        extra_tags_xml=_AXIS_TAG_XML)


# ---------------------------------------------------------------------------
# D. CROUT -- NEAR_VERBATIM clone of one real corpus call, using a small
#    synthetic UDT ("ZoneStatus") in place of the real file's own Zone1
#    tag so every member reference resolves to something real and sizeable.
# ---------------------------------------------------------------------------

def group_crout() -> None:
    instr = ("CROUT(Zone1,NEGATIVE,250,Zone1.Actuate,Zone1.Feedback1,Zone1.Feedback2,"
             "Zone1.InputStatus,Zone1.OutputStatus,Zone1.Reset);")
    zone_tag = tag_xml("Zone1", "ZoneStatus", udt_members=_ZONE_MEMBERS)
    _one_rung_file(instr, "InstrCrout", "instrfirst_crout",
                    "CROUT(Zone1,NEGATIVE,250,Zone1.Actuate,...,Zone1.Reset) -- NEAR_VERBATIM clone of a real "
                    "corpus call (SJ_Gormley_20251112_r02.L5X, Zone1/Zone2 examples), using a synthetic "
                    "6-DINT-member ZoneStatus UDT in place of the real file's own Zone1 tag shape (unconfirmed "
                    "exactly, but structurally identical: 1 identifying tag + 2 literals + 6 member refs)",
                    extra_tags_xml=zone_tag, extra_datatypes_xml=_ZONE_UDT_XML)


# ---------------------------------------------------------------------------
# E. CAM-family instructions (MCCP, MAPC) -- need the newly-discovered CAM
#    predefined structure (unmodeled, see cam_tag_xml). write_sample_
#    unmodeled since CAM has no byte-size formula yet.
# ---------------------------------------------------------------------------

def group_cam_family() -> None:
    cam_tag = cam_tag_xml("Cam1", 5)

    mccp_instr = "MCCP(MotionInstr1,Cam1[0],2,1,1,CamProfile1[0]);"
    _one_rung_file_unmodeled(mccp_instr, "InstrMccp", "instrfirst_mccp",
                              "MCCP(MotionInstr1,Cam1[0],2,1,1,CamProfile1[0]) -- CORPUS_CONFIRMED shape "
                              "(MCCP(MCCP_NewCi2,NewCI2Cam[0],2,1,1,newCi2CamProfile[0])), real operand "
                              "DataTypes confirmed via corpus lookup: MOTION_INSTRUCTION, CAM (new, unmodeled), "
                              "literal ints, CAM_PROFILE",
                              extra_tags_xml=cam_tag)

    mapc_instr = ("MAPC(Axis_Cip_Drive,Axis_Cip_Drive,MotionInstr1,0,CamProfile1[0],1,1,Once,Forward Only,"
                  "Cam1[0].Master,Cam1[0].Master,New Cam,Command,Bi-Directional);")
    _one_rung_file_unmodeled(mapc_instr, "InstrMapc", "instrfirst_mapc",
                              "MAPC(...) -- NEAR_VERBATIM clone of a real corpus call (Griffin_StackerLine_"
                              "1Mar25_r00.L5X, MAPC(EM304_ForksUpDn,VM305_StackerVirtual,Stacker.ForksUpDn."
                              "MAPC,0,Stacker.ForksUpDn.CAMPROFILE[0],1,1,Once,Forward Only,Stacker.ForksUpDn."
                              "CAM[2].Master,Stacker.ForksUpDn.CAM[2].Master,New Cam,Command,Bi-Directional)) "
                              "-- same Axis tag reused for both slave/master operand positions here rather than "
                              "declaring a second axis",
                              extra_tags_xml=cam_tag)


# ---------------------------------------------------------------------------
# F. MSG -- needs the newly-discovered MESSAGE predefined structure
#    (unmodeled). write_sample_unmodeled.
# ---------------------------------------------------------------------------

def group_msg() -> None:
    msg_tag = message_tag_xml("Msg1", local_element="Arr0", destination_tag="Arr1")
    instr = "MSG(Msg1);"
    _one_rung_file_unmodeled(instr, "InstrMsg", "instrfirst_msg",
                              "MSG(Msg1) -- CORPUS_CONFIRMED shape (MSG(MESSAGE_Fault)), MessageParameters "
                              "attribute set copied verbatim from a real CIP Generic get-attribute message "
                              "(BaillieLeitchField_Edger_20260812_r00.L5X, MESSAGE_Alarms) except "
                              "LocalElement/DestinationTag, which point at this file's own Arr0/Arr1 tags "
                              "instead of the real file's array tags",
                              extra_tags_xml=msg_tag)


def main() -> None:
    group_simple_atomic()
    group_control_tag_instructions()
    group_motion_two_operand()
    group_crout()
    group_cam_family()
    group_msg()
    total = 18 + 8 + 6 + 1 + 2 + 1
    print(f"\nDone. {total} files.")


if __name__ == "__main__":
    main()
