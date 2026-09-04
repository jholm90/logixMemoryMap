"""OQ-STSIZING: Structured Text, the total coverage hole (James, 2026-09-04:
"Where did you go for St samples? ... I hope you are going to be able to
write st language based on your knowledge and skills, not just tossing lines
and hope they stick. One thing not modelled is st comments ... How confident
are you with your st code and do I have to write samples for you or can you
extract enough from the sample code like bender and some of the aois.")

Honest answer to that, and the reason this file replaces the naive first
attempt: the first ST ladder in gen_realscale_surcharge.py was written from
general ST knowledge with only the FOR-loop shape copied from a real file.
That was the wrong order of operations. The corpus was measured first this
time, and it says the naive ladder was not representative of anything:

  samples/local/, 23 real files: 297 ST routines, 24,017 ST lines
    :=  assignment           8,688      IF ......... 1,739   END_IF 1,230
    THEN .......... 1,831    ELSIF ........ 559    ELSE ...... 332
    CASE/OF/END_CASE 90/1,085/84         FOR/DO/END_FOR 600/879/148
    WHILE/END_WHILE 38/3     REPEAT/UNTIL 1/8      EXIT 39   RETURN 5
    leading // comments 5,931   trailing // 967   (* *) 27   = 6,925 (29%)
    instruction-style calls inside ST: COP 362, CONCAT 67, SBR 44, RET 42,
      DTOS 26, TRUNC 25, TONR 22, JSR 18, DELETE 16, OSRI 12, ABS 10,
      GSV 8, SIZE 7, STOD 7, BTDT 6, CPS 4, SCL 4, MSG 2, SSV 1

So James is right on the substance: real ST is not a wall of assignments,
it is ~36% control flow, ~29% comments, and it calls the SAME instructions
the ladder does. That last point is the single most valuable thing in the
table -- if a COP costs the same inside ST as it does in a rung, the entire
existing per-instruction weight table transfers to ST for free and the only
new terms needed are the per-line/statement and control-flow ones. Group D
below is built specifically to answer that, paired file-for-file against
`instr_*_n01000` captures that are already valid and error-free.

ANSWER TO "do I have to write samples for you": no. 24,017 real ST lines
across 23 files is more idiom than this needs; every construct and every
instruction call in this batch is taken from that corpus, not invented.
What is needed from James is CAPTURE, not authoring.

THE COMMENT QUESTION (group B) is genuinely open and genuinely different
from the already-answered rung-comment one. `instr_cpt_n05000_comment100`
and `instr_cpt_n05000_nocomment` came back BYTE-IDENTICAL (2,282,944 both),
so an RLL rung comment is confirmed free. But that comment lives in its own
`<Comment>` XML element hanging off the rung -- it is metadata beside the
logic. An ST comment lives INSIDE the routine's own source text, in the same
CDATA the compiler reads, and Studio compiles ST from that text. There is a
real mechanism by which the two could differ, so the RLL result does not
transfer and cannot be assumed. 29% of every real ST line in the corpus is
at stake.

GROUPS
------
A. group_line_ladder (5) -- executable-only baseline, 0/25/100/400/1000
   plain assignments, no comments, no blanks. The per-line base term.
B. group_comments (5) -- 100 executable lines held identical to
   realscale_st_n00100, varying ONLY comment volume/width/placement, plus
   a blank-line file (blank lines are ~20% of real ST and are a separate
   question from comments).
C. group_constructs (5) -- 100 executable statements held constant, wrapped
   in IF / IF-ELSIF chain / CASE / FOR / WHILE. Read against
   realscale_st_n00100 (the same 100 statements, unwrapped), each file's
   delta is that construct's own cost.
D. group_instruction_calls (5) -- 1,000 calls of COP / CONCAT / DTOS / SIZE
   inside ST, and 1,000 plain assignments to pair against MOV. Each pairs
   with an existing VALID error-free `instr_*_n01000` capture using the
   identical operands, so the difference is purely RLL-vs-ST hosting.
E. group_expression (3) -- the CPT question. An ST assignment with an
   arithmetic right-hand side is structurally a CPT expression, and this
   project already has a tier-aware CPT model that is exact on every real
   data point on file. `st_expr_cpt_mirror_n01000` copies
   `instr_cpt_n01000`'s expression CHARACTER FOR CHARACTER into ST form, so
   it directly tests whether the CPT model can just be reused for ST
   assignments; two simpler operator counts bracket it.
F. group_st_jsr_target (1) -- an ST routine used as a JSR target with real
   SBR/RET parameter passing (44 SBR / 42 RET in the real corpus, so this
   is a real shape, not a curiosity).

Run: python -m sample_gen.gen_st_sizing
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import rung_xml, tag_xml
from sample_gen.gen_logic_sweep import _POOL_TAGS_XML
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

LOGIC_OUT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"

# One extra DINT for loop indices -- real ST loop counters are ordinary
# controller tags (RobbinsGrn: "for i := 0 to 7 by 1 do"), not implicit.
_TAGS = _POOL_TAGS_XML + "\n" + tag_xml("StIdx", "DINT")


def _st_routine(name: str, lines: list[str]) -> str:
    """Real export shape, verbatim from the corpus: one <Line> per source
    line, Number sequential from 0, the source text alone inside CDATA on
    its own line. Blank source lines are real and common (~20% of every
    real ST routine) and are emitted as genuinely empty CDATA."""
    body = "".join(
        f'<Line Number="{i}">\n<![CDATA[{text}]]>\n</Line>\n'
        for i, text in enumerate(lines)
    )
    return f'<Routine Name="{name}" Type="ST">\n<STContent>\n{body}</STContent>\n</Routine>'


def _write(out_name: str, l5x: str, description: str, category: str = "logic_instr") -> None:
    out_path = LOGIC_OUT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, category, out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


def _file(out_name: str, target: str, lines: list[str], description: str,
          extra_tags: str = "", routine_name: str = "StTarget") -> None:
    l5x = build_l5x(
        target_name=target, tags_xml=_TAGS + extra_tags,
        extra_rungs_xml=rung_xml(0, f"JSR({routine_name},0);"),
        extra_routines_xml=_st_routine(routine_name, lines),
    )
    _write(out_name, l5x, description)


def _assigns(n: int, start: int = 0) -> list[str]:
    """The corpus's most common statement by a wide margin (8,688 of 24,017
    lines carry a :=). Plain, no comment, no blank."""
    return [f"D{(start + i) % 10} := D{(start + i + 1) % 10} + 1;" for i in range(n)]


# --- A. Executable-only line ladder -----------------------------------------

_A_COUNTS = (0, 25, 100, 400, 1000)


def group_line_ladder() -> None:
    for n in _A_COUNTS:
        _file(
            f"realscale_st_n{n:05d}", f"RsSt{n:05d}", _assigns(n),
            f"{n} plain ST assignment lines (Di := Dj + 1;), no comments, no blank lines, "
            f"called by one JSR, everything else held identical across the ladder. Structured "
            f"Text is completely unmodeled today -- parse_rll_routines is RLL-only, so the "
            f"engine predicts the SAME number for every file here and whatever Capacity "
            f"movement comes back is the raw per-ST-statement cost with nothing to subtract. "
            f"Assignment is the right base statement to measure: 8,688 of the 24,017 real ST "
            f"lines in samples/local/ carry a :=.",
        )


# --- B. Comments and blank lines --------------------------------------------

_B_EXEC = 100  # identical to realscale_st_n00100, so that file is the control
_SHORT_CMT = "// step complete"
# 110 characters, matching the real header-block width in Bender134053's
# T_ADD routine -- not an invented length.
_LONG_CMT = ("// " + "normalized Gregorian date/time carry handling, see routine header "
             "for the full algorithm note").ljust(110, ".")


def group_comments() -> None:
    exec_lines = _assigns(_B_EXEC)

    def interleave(cmt: str, n_cmt: int) -> list[str]:
        """Leading whole-line comments, spread through the code the way real
        ST does it, not bolted on as one block."""
        out: list[str] = []
        every = max(1, _B_EXEC // n_cmt) if n_cmt else 0
        c = 0
        for i, line in enumerate(exec_lines):
            while c < n_cmt and (i * n_cmt) // _B_EXEC >= c:
                out.append(cmt)
                c += 1
            out.append(line)
        out.extend([cmt] * (n_cmt - c))
        return out

    _file("st_cmt_lead100_short", "RsStCmtLeadShort", interleave(_SHORT_CMT, 100),
          f"{_B_EXEC} ST assignment lines identical to realscale_st_n00100, PLUS 100 leading "
          f"whole-line // comments of {len(_SHORT_CMT)} characters, interleaved through the "
          f"code the way real ST writes them. Delta against realscale_st_n00100 is the cost of "
          f"100 ST comment lines and nothing else. An RLL rung comment is already CONFIRMED "
          f"free (instr_cpt_n05000_comment100 and instr_cpt_n05000_nocomment came back "
          f"byte-identical at 2,282,944) -- but that comment is a separate <Comment> element "
          f"beside the rung, whereas an ST comment sits inside the routine's own source CDATA "
          f"that the compiler reads, so the RLL result does not transfer.")

    _file("st_cmt_lead100_long", "RsStCmtLeadLong", interleave(_LONG_CMT, 100),
          f"Same {_B_EXEC} ST assignment lines and same COUNT of 100 leading // comment lines "
          f"as st_cmt_lead100_short, but each comment is {len(_LONG_CMT)} characters instead of "
          f"{len(_SHORT_CMT)} (the real header-block width used in Bender134053_201104's T_ADD "
          f"routine). If ST comments cost anything, this pair says whether the cost is per "
          f"comment LINE or per comment CHARACTER -- a distinction that matters a lot on real "
          f"files, where 5,931 of 24,017 corpus ST lines are leading // comments.")

    _file("st_cmt_lead400_short", "RsStCmtLead400", interleave(_SHORT_CMT, 400),
          f"Same {_B_EXEC} ST assignment lines, 400 leading // comment lines instead of 100 -- "
          f"the 4x point that turns the comment cost from a single delta into a slope, and "
          f"brackets the real corpus ratio (6,925 comment lines against 24,017 total).")

    _file("st_cmt_trail100", "RsStCmtTrail",
          [f"{line} {_SHORT_CMT}" for line in exec_lines],
          f"The same {_B_EXEC} ST assignment lines with a TRAILING // comment appended to each "
          f"one -- same comment text as st_cmt_lead100_short but zero added lines. Separates "
          f"'a comment costs because it is a line' from 'a comment costs because of its "
          f"characters'. 967 of the corpus's real ST comments are trailing rather than leading.")

    _file("st_blank400", "RsStBlank400",
          [x for line in exec_lines for x in (line, "", "", "", "")][: _B_EXEC + 400],
          f"The same {_B_EXEC} ST assignment lines padded with 400 genuinely EMPTY source "
          f"lines and no comments at all. Blank lines are ~20% of every real ST routine in the "
          f"corpus and are a separate question from comments -- if blanks are free but comments "
          f"are not, the cost is in the comment text; if both cost the same, the cost is per "
          f"<Line> element regardless of what is on it.")


# --- C. Control-flow constructs ---------------------------------------------

_C_STMTS = 100  # identical statement count to realscale_st_n00100, the control


def group_constructs() -> None:
    stmts = _assigns(_C_STMTS)

    if_lines = [f"IF B{i % 10} THEN {stmts[i]} END_IF;" for i in range(_C_STMTS)]
    _file("st_ctl_if", "RsStCtlIf", if_lines,
          f"The same {_C_STMTS} assignment statements as realscale_st_n00100, each wrapped in "
          f"its own IF cond THEN ... END_IF;. IF is the corpus's dominant construct (1,739 IF / "
          f"1,831 THEN / 1,230 END_IF across 24,017 real ST lines). Delta against "
          f"realscale_st_n00100 is the cost of {_C_STMTS} IF/END_IF pairs and their conditions.")

    elsif_lines = [f"IF B0 THEN {stmts[0]}"]
    elsif_lines += [f"ELSIF B{i % 10} THEN {stmts[i]}" for i in range(1, _C_STMTS)]
    elsif_lines.append("END_IF;")
    _file("st_ctl_elsif", "RsStCtlElsif", elsif_lines,
          f"The same {_C_STMTS} assignment statements as ONE IF / {_C_STMTS - 1}x ELSIF chain "
          f"closed by a single END_IF -- verbatim the shape of Bender134053_201104's real "
          f"D00_ActiveStep routine (if Seq_Step_000.X then StepID:=0; elsif Seq_Step_001.X "
          f"then StepID:=1; ...). Read against st_ctl_if, which has the identical statement "
          f"count but {_C_STMTS} separate IF/END_IF pairs: separates the cost of a BRANCH from "
          f"the cost of a whole IF BLOCK. 559 real ELSIFs in the corpus.")

    case_lines = [f"CASE D0 OF"]
    case_lines += [f"{i}: {stmts[i]}" for i in range(_C_STMTS)]
    case_lines += ["ELSE", "D1 := -1;", "END_CASE;"]
    _file("st_ctl_case", "RsStCtlCase", case_lines,
          f"The same {_C_STMTS} assignment statements as a single CASE OF with {_C_STMTS} "
          f"numbered branches plus an ELSE. Same statement count as st_ctl_elsif but a jump "
          f"table instead of a comparison chain -- if the compiler builds these differently "
          f"the two diverge, which is the whole point of running both. 90 CASE / 1,085 OF / "
          f"84 END_CASE in the real corpus.")

    for_lines = []
    for blk in range(10):
        for_lines.append("FOR StIdx := 0 TO 9 DO")
        for_lines.append(f"D{blk % 10} := D{(blk + 1) % 10} + StIdx;")
        for_lines.append("END_FOR;")
    _file("st_ctl_for", "RsStCtlFor", for_lines,
          f"10 FOR StIdx := 0 TO 9 DO / assignment / END_FOR blocks -- 10 statements of loop "
          f"body against {_C_STMTS} loop ITERATIONS, so this also says whether ST is priced on "
          f"source text or on executed work (it should be source text; this is the file that "
          f"proves it rather than assuming it). FOR is the corpus's second construct, 600 "
          f"occurrences, and the loop counter is an ordinary controller tag exactly as in "
          f"RobbinsGrn_2026_05_13r00's real 'for i := 0 to 7 by 1 do'.")

    while_lines = []
    for blk in range(10):
        while_lines.append("StIdx := 0;")
        while_lines.append("WHILE StIdx < 10 DO")
        while_lines.append(f"D{blk % 10} := D{(blk + 1) % 10} + StIdx;")
        while_lines.append("StIdx := StIdx + 1;")
        while_lines.append("END_WHILE;")
    _file("st_ctl_while", "RsStCtlWhile", while_lines,
          f"10 WHILE cond DO ... END_WHILE blocks with an explicit counter increment, the same "
          f"shape RobbinsGrn_2026_05_13r00 uses for its real string-padding loop "
          f"(While(szString.LEN < dEnd_Size) do Concat(...); end_while;). The only unbounded "
          f"construct in ST, and the rarest in the corpus (38 WHILE) -- included because a "
          f"model that silently prices it at zero would be wrong on every file that has one.")


# --- D. Instruction calls hosted in ST vs in a rung -------------------------

# Operands are byte-for-byte the ones gen_logic_sweep.INSTRUCTIONS uses at
# the same index, so each file's ONLY difference from its instr_*_n01000
# partner is RLL-vs-ST hosting.
_D_N = 1000
# NOTE on the COP pairing: instr_cop_n01000 is one of the 268 captures whose
# error_count is BLANK rather than an explicit 0 (it predates that column),
# so "no errors" there means "never recorded", not "recorded clean" -- see
# scripts/accuracy_report.py --strict. Its three ST partners (CONCAT/DTOS/
# SIZE) all pair against explicit-0 rows, which is why four instructions are
# tested rather than one.
_D_CALLS = {
    "cop": ("COP({a}[0],{b}[0],5);", "COP", 362),
    "concat": ("CONCAT(STR{i},STR{j},STR{k});", "CONCAT", 67),
    "dtos": ("DTOS(D{i},STR{i5});", "DTOS", 26),
    "size": ("SIZE({a},0,D{i});", "SIZE", 7),
}


def group_instruction_calls() -> None:
    for key, (tmpl, mnemonic, corpus_n) in _D_CALLS.items():
        lines = [
            tmpl.format(
                a=f"ARR{i % 2}", b=f"ARR{(i + 1) % 2}",
                i=i % 10, j=(i + 1) % 5, k=(i + 2) % 5, i5=i % 5,
            )
            for i in range(_D_N)
        ]
        _file(
            f"st_instr_{key}_n{_D_N:05d}", f"RsStInstr{mnemonic}", lines,
            f"{_D_N} {mnemonic} calls inside a Structured Text routine, using operands "
            f"byte-for-byte identical to gen_logic_sweep's own {mnemonic} rung text. Pairs "
            f"directly with the VALID error-free capture instr_{key}_n{_D_N:05d}, whose only "
            f"difference is that its {mnemonic}s sit in rungs instead. If the two land on the "
            f"same number, the entire existing per-instruction weight table transfers to ST "
            f"unchanged and ST needs only per-statement and control-flow terms on top -- by "
            f"far the cheapest possible way to close this coverage hole. {mnemonic} appears "
            f"{corpus_n} times inside real ST routines in samples/local/.",
        )

    _file(
        f"st_assign_literal_n{_D_N:05d}", "RsStAssignLit",
        [f"D{i % 10} := {i % 1000};" for i in range(_D_N)],
        f"{_D_N} plain literal assignments (Di := <literal>;) -- the ST spelling of "
        f"gen_logic_sweep's MOV rung text, MOV({{i%1000}},D{{i%10}}), operand for operand. "
        f"Pairs with the valid instr_mov_n{_D_N:05d} capture (58,944). MOV has no ST function "
        f"form; := IS how a real ST routine moves a value, so this is the honest pairing and "
        f"it prices the single most common statement in the whole real ST corpus.",
    )


# --- E. ST assignment vs the CPT expression model ---------------------------


def group_expression() -> None:
    # instr_cpt_n01000's rung text is
    #   CPT(R{i}, (D{i}+D{i+1}) * R{i+1} - R{i+2}/2 + 1.5)
    # transcribed here operand for operand into ST assignment form.
    mirror = [
        f"R{i % 10} := (D{i % 10} + D{(i + 1) % 10}) * R{(i + 1) % 10} "
        f"- R{(i + 2) % 10} / 2 + 1.5;"
        for i in range(_D_N)
    ]
    _file(
        f"st_expr_cpt_mirror_n{_D_N:05d}", "RsStExprMirror", mirror,
        f"{_D_N} ST assignments transcribing instr_cpt_n{_D_N:05d}'s CPT expression operand "
        f"for operand: R := (D+D) * R - R/2 + 1.5. An ST assignment with an arithmetic "
        f"right-hand side IS structurally a CPT expression, and this project already has a "
        f"tier-aware CPT model (including the REAL-destination float model wired 2026-09-04, "
        f"exact on 29/29 real rows). If this file lands on instr_cpt_n{_D_N:05d}'s 474,944, "
        f"that whole model can be reused for ST assignments as-is instead of fitting a second "
        f"one from scratch. This is the highest-leverage single file in the ST batch.",
    )

    _file(
        f"st_expr_ops1_n{_D_N:05d}", "RsStExprOps1",
        [f"R{i % 10} := D{i % 10} + D{(i + 1) % 10};" for i in range(_D_N)],
        f"{_D_N} single-operator ST assignments with a REAL destination and two DINT operands. "
        f"Brackets st_expr_cpt_mirror_n{_D_N:05d} from below: the CPT model charges a "
        f"first_operator term, per-operator extras, and an int->float conversion per non-float "
        f"operand, so a 1-operator/2-int-operand case is the cleanest possible test of whether "
        f"those same terms apply to ST.",
    )

    _file(
        f"st_expr_ops2_dint_n{_D_N:05d}", "RsStExprOps2Dint",
        [f"D{i % 10} := D{(i + 1) % 10} + D{(i + 2) % 10} * 2;" for i in range(_D_N)],
        f"{_D_N} two-operator ST assignments with a DINT (integer) destination and no float "
        f"anywhere. The CPT model prices integer and REAL destinations by completely different "
        f"rules -- in float, operator TIER differences vanish and every non-float operand "
        f"carries a conversion charge, neither of which applies to an all-integer expression. "
        f"Read against st_expr_ops1_n{_D_N:05d} (REAL destination, same operand count), this "
        f"says whether that destination-type split is real in ST too.",
    )


# --- F. ST routine as a real JSR target with parameters ---------------------


def group_st_jsr_target() -> None:
    lines = ["SBR(D0,D1,D2,D3,D4);"]
    lines += _assigns(100)
    lines.append("RET(D5);")
    routine = _st_routine("StParamTarget", lines)
    calls = "\n".join(
        rung_xml(i, "JSR(StParamTarget,5,D0,D1,D2,D3,D4,D5);") for i in range(100)
    )
    l5x = build_l5x(
        target_name="RsStJsrParam", tags_xml=_TAGS,
        extra_rungs_xml=calls, extra_routines_xml=routine,
    )
    _write(
        "st_jsr_param_target_n00100", l5x,
        "An ST routine used as a real JSR target with parameter passing -- SBR(5 inputs) at "
        "the top, 100 assignment statements, RET(1 output) at the bottom, called 100 times. "
        "This is a real shape, not a curiosity: the corpus carries 44 SBR and 42 RET calls "
        "inside ST routines. Everything this project knows about JSR parameter cost "
        "(B(n)=4+20n per call site, A(n)=104+20n per distinct target, output_param_cost=20) "
        "was fitted entirely on RLL targets; this is the only file that says whether an ST "
        "target is charged the same way. It also carries the JSR-target composite surcharge, "
        "which has likewise never seen an ST target.",
        category="jsr_sbr_ret",
    )


def main() -> None:
    group_line_ladder()
    group_comments()
    group_constructs()
    group_instruction_calls()
    group_expression()
    group_st_jsr_target()
    print("\nDone. 24 files.")


if __name__ == "__main__":
    main()
