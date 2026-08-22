"""Per-instruction logic-sizing sweep (James, 2026-08-21): "examine the
difference between XIC/OTE and MVM/MEQ/CPT/MAM all the big juicy ones...
hammer each individual instruction and make sure you can compile it
properly. we have 30% of the instructions in the sample code so i'd just
work with those."

Instruction list and every operand shape below is taken directly from real
usage in samples/local/ (47 real production files, 115 distinct mnemonics
found) -- not guessed. Scoped to the ~46 non-motion instructions used >=50
times in that corpus; the real motion instructions (MAM/MAJ/MAH/MAS/MSO/
MRP/MAPC/MCCP, all real and all needing an actual Axis tag as their first
operand) are left for the Phase 4d motion-structures work instead of forced
into this generic sweep with fake operands.

Every instruction-type file shares one small, fixed, fully-DECLARED tag
pool (see _POOL_TAGS) -- this is a deliberate fix over the earlier
xic_ote_1000 sample, which referenced 2000 tags (In0..In999/Out0..Out999)
that were never declared anywhere in the file's Tags section, making its
"zero measurable cost" result ambiguous. With a fixed, known, always-
declared pool, tag-data cost is constant across every file in this sweep,
so any Capacity movement across the count sweep is attributable to the
instruction/rung text itself.

**T_ADD removed 2026-08-22 (James's catch):** T_ADD is a real, common
Rockwell-authored AddOnInstructionDefinition ("DateTime := DateTime +
Time", found in 18+ of James's real corpus files), not a native
instruction -- a real research failure earlier in this project mis-
classified it during the corpus mnemonic scan. The removed test called
`T_ADD(D0,D1,D2,D3)` with 4 plain DINTs and no AOI definition anywhere in
the file and no instance tag -- structurally guaranteed not to compile,
not a useful data point at any rung count. T_ADD belongs with AOI-sizing
work (Phase 4c) if it's ever tested, using its real call shape
(`T_ADD(InstanceTag,Ref_DT,Ref_Time,ResultDT)`), not this native-
instruction sweep. The 5 already-generated `instr_t_add_n*` files and
their manifest rows are removed, not just flagged for re-capture --
there's no fix that makes the original test meaningful.

Also confirmed the same day (James: "Curious if the SDK had L5X->ACD with
controller validation/program checking"): `samples/convert_log.csv` shows
every T_ADD/CPS/COP/FLL/BTD/SIZE file (including the ones with the
array-subscript bug fixed nearby) converted with `l5x2acd` status "ok" --
the SDK's L5X->ACD conversion does NOT perform ladder-logic verification,
only catches structural/schema-level failures (e.g. an unsupported
ProcessorType). A file that converts cleanly can still contain rung-level
errors (an undefined instruction/AOI reference, a missing array
subscript) that only a real Studio 5000 Verify would catch. See
`sample_gen/lint.py` for the local heuristic pre-flight check this
finding motivated.

Run: python -m sample_gen.gen_logic_sweep
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import (
    counter_tag_xml, rung_xml, rungs_xml, tag_xml, timer_tag_xml,
)
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"

# Count sweep applied to every instruction -- mirrors the tag-count-sweep
# methodology that produced an exact 92.000-blocks/tag fit (docs/OPEN_QUESTIONS.md
# OQ-TAGOVERHEAD): enough points to fit a real per-instruction rate, not
# just a single before/after delta.
COUNTS = [10, 50, 100, 1000, 5000]


def _d(i, n=10): return f"D{i % n}"
def _r(i, n=10): return f"R{i % n}"
def _b(i, n=10): return f"B{i % n}"
def _s(i, n=5): return f"S{i % n}"
def _sd(i, n=5): return f"STR{i % n}"
def _tmr(i, n=3): return f"TMR{i % n}"
def _ctr(i, n=3): return f"CTR{i % n}"
def _arr(i, n=2): return f"ARR{i % n}"


def _pool_tags_xml() -> str:
    parts = []
    for i in range(10):
        parts.append(tag_xml(f"D{i}", "DINT"))
    for i in range(10):
        parts.append(tag_xml(f"R{i}", "REAL"))
    for i in range(10):
        parts.append(tag_xml(f"B{i}", "BOOL"))
    for i in range(5):
        parts.append(tag_xml(f"S{i}", "SINT"))
    for i in range(5):
        parts.append(tag_xml(f"STR{i}", "STRING", string_max_len=82))
    for i in range(3):
        parts.append(timer_tag_xml(f"TMR{i}"))
    for i in range(3):
        parts.append(counter_tag_xml(f"CTR{i}"))
    for i in range(2):
        parts.append(tag_xml(f"ARR{i}", "DINT", dimensions=(20,)))
    return "\n".join(parts)


_POOL_TAGS_XML = _pool_tags_xml()

# name -> rung-text-fn(i). Every operand shape taken from a real example in
# samples/local/ (see gen_logic_sweep.py's module docstring / commit
# message for the corpus scan). A handful (T_ADD, GSV, SSV, BTD) use
# best-effort atomic-typed operands where the real usage involved a
# specialized structure this project doesn't model yet -- if Studio 5000
# rejects one of those specifically, that's useful signal on its own
# ("hammer each individual instruction and make sure you can compile it").
INSTRUCTIONS: dict[str, "callable"] = {
    "XIC": lambda i: f"XIC({_b(i)})OTE({_b(i+1)});",
    "XIO": lambda i: f"XIO({_b(i)})OTE({_b(i+1)});",
    "OTE": lambda i: f"OTE({_b(i)});",
    "OTL": lambda i: f"OTL({_b(i)});",
    "OTU": lambda i: f"OTU({_b(i)});",
    "ONS": lambda i: f"XIC({_b(i)})ONS({_b((i+1)%10)})OTE({_b((i+2)%10)});",
    "AFI": lambda i: f"AFI()OTE({_b(i)});",
    "NOP": lambda i: "NOP();",
    "CLR": lambda i: f"CLR({_d(i)});",
    "MOV": lambda i: f"MOV({i % 1000},{_d(i)});",
    "ADD": lambda i: f"ADD({_d(i)},{_d((i+1)%10)},{_d((i+2)%10)});",
    "SUB": lambda i: f"SUB({_d(i)},{_d((i+1)%10)},{_d((i+2)%10)});",
    "MUL": lambda i: f"MUL({_d(i)},{_d((i+1)%10)},{_d((i+2)%10)});",
    "DIV": lambda i: f"DIV({_d(i)},2,{_d((i+1)%10)});",
    "MOD": lambda i: f"MOD({_d(i)},2,{_d((i+1)%10)});",
    "EQU": lambda i: f"EQU({_d(i)},{i % 50})OTE({_b(i)});",
    "NEQ": lambda i: f"NEQ({_d(i)},{_d((i+1)%10)})OTE({_b(i)});",
    "GRT": lambda i: f"GRT({_d(i)},{i % 10})OTE({_b(i)});",
    "GEQ": lambda i: f"GEQ({_d(i)},{i % 10})OTE({_b(i)});",
    "LES": lambda i: f"LES({_d(i)},{i % 10})OTE({_b(i)});",
    "LEQ": lambda i: f"LEQ({_d(i)},{i % 10})OTE({_b(i)});",
    "LIM": lambda i: f"LIM({_d(i)},{_d((i+1)%10)},{_d((i+2)%10)})OTE({_b(i)});",
    "CPT": lambda i: f"CPT({_r(i)},({_d(i)}+{_d((i+1)%10)})*{_r((i+1)%10)}-{_r((i+2)%10)}/2+1.5);",
    # Real corpus (2026-08-22 re-check, James's spot-check catch): an
    # ARRAY-typed tag reference always needs an explicit [index] subscript
    # -- bare "ARR0" (no bracket) is only valid Rockwell syntax when the
    # tag itself is a scalar UDT/AOI instance (real examples:
    # CPS(ASV603,Valve,1)), never when it's actually declared as an array
    # like ARR0/ARR1 here (DINT[20]). The original bare-name versions of
    # CPS/COP/FLL/BTD below were invalid syntax -- see git history for
    # what shipped before this fix, and docs/OPEN_QUESTIONS.md for what
    # this explains about the "stuck at an identical value" rows.
    "CPS": lambda i: f"CPS({_arr(i)}[0],{_arr((i+1)%2)}[0],5);",
    "COP": lambda i: f"COP({_arr(i)}[0],{_arr((i+1)%2)}[0],5);",
    "FLL": lambda i: f"FLL({i % 100},{_arr(i)}[0],5);",
    "MVM": lambda i: f"MVM({_d(i)},16#0000_00FF,{_d((i+1)%10)});",
    "MEQ": lambda i: f"MEQ({_d(i)},16#0000_00FF,{i % 50})OTE({_b(i)});",
    "CONCAT": lambda i: f"CONCAT({_sd(i)},{_sd((i+1)%5)},{_sd((i+2)%5)});",
    "MID": lambda i: f"MID({_sd(i)},2,1,{_sd((i+1)%5)});",
    "DELETE": lambda i: f"DELETE({_sd(i)},1,1,{_sd((i+1)%5)});",
    # James's own Studio-5000-verified sample (COP_Samples.L5X, 2026-08-22)
    # compiles SIZE(COP_Source,0,COP_Size); against a plain DINT[10] array
    # -- bare tag name, NO [index] subscript and no .DATA reach-in. That
    # directly contradicts the bracketed/`.DATA[0]` version this used to
    # test (based on an ambiguous, unconfirmed STRING-specific corpus
    # reference) -- SIZE is the one array-taking instruction in this file
    # that does NOT follow the CPS/COP/FLL/BTD bracket rule below, since
    # unlike those it operates on the whole array, not one element of it.
    # Switched off the STRING pool (_sd) onto the plain-array pool (_arr)
    # to match the confirmed sample exactly.
    "SIZE": lambda i: f"SIZE({_arr(i)},0,{_d(i)});",
    "STOD": lambda i: f"STOD({_sd(i)},{_d(i)});",
    "DTOS": lambda i: f"DTOS({_d(i)},{_sd(i)});",
    "ABS": lambda i: f"ABS({_d(i)},{_r(i)});",
    "XPY": lambda i: f"XPY(2,{_d(i)},{_r(i)});",
    "BTD": lambda i: f"BTD({_arr(i)}[0],0,{_d(i)},0,8);",
    "TON": lambda i: f"TON({_tmr(i)},?,?);",
    "TOF": lambda i: f"TOF({_tmr(i)},?,?);",
    "RTO": lambda i: f"RTO({_tmr(i)},?,?);",
    "CTU": lambda i: f"CTU({_ctr(i)},?,?);",
    "RES": lambda i: f"RES({_tmr(i)});",
    "GSV": lambda i: f"GSV(Task,MainTask,Priority,{_d(i)});",
    "SSV": lambda i: f"SSV(Task,MainTask,Priority,{_d(i)});",
    "CMP": lambda i: f"CMP({_d(i)}>{_d((i+1)%10)})OTE({_b(i)});",
}


def _write(l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "logic_instr", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


def group_instruction_sweep() -> None:
    for name, fn in INSTRUCTIONS.items():
        for count in COUNTS:
            rungs = rungs_xml(count, fn)
            l5x = build_l5x(target_name=f"Instr{name}", tags_xml=_POOL_TAGS_XML, extra_rungs_xml=rungs)
            out_name = f"instr_{name.lower()}_n{count:05d}"
            _write(l5x, out_name, f"{count} rungs of {name} alone, shared fixed tag pool")


def group_jsr() -> None:
    # JSR needs a real target routine to exist -- one dummy subroutine
    # (single NOP) added via extra_routines_xml, called repeatedly.
    sub_routine = (
        '<Routine Name="SubTest" Type="RLL">'
        '<RLLContent><Rung Number="0" Type="N"><Text><![CDATA[NOP();]]></Text></Rung></RLLContent>'
        "</Routine>"
    )
    for count in COUNTS:
        rungs = rungs_xml(count, lambda i: "JSR(SubTest,0);")
        l5x = build_l5x(target_name="InstrJSR", tags_xml=_POOL_TAGS_XML, extra_rungs_xml=rungs,
                         extra_routines_xml=sub_routine)
        out_name = f"instr_jsr_n{count:05d}"
        _write(l5x, out_name, f"{count} rungs of JSR to a real dummy subroutine")


def group_lbl_jmp() -> None:
    # LBL/JMP as a pair -- each "count" unit is one LBL rung + one JMP rung
    # jumping to it, so labels stay locally satisfied.
    for count in COUNTS:
        rungs = []
        for i in range(count):
            rungs.append(rung_xml(2 * i, f"LBL(L{i});"))
            rungs.append(rung_xml(2 * i + 1, f"JMP(L{i});"))
        l5x = build_l5x(target_name="InstrLBLJMP", tags_xml=_POOL_TAGS_XML, extra_rungs_xml="\n".join(rungs))
        out_name = f"instr_lbljmp_n{count:05d}"
        _write(l5x, out_name, f"{count} LBL/JMP pairs")


def group_tag_vs_literal() -> None:
    # Does populating an instruction with real tag operands vs pure literal
    # constants change anything? Same CPT pattern, only the operand source
    # differs. James: "i think theres even a level we should test if the
    # instructions are populated with tags."
    count = 1000
    rungs_tags = rungs_xml(count, lambda i: f"CPT({_r(i)},({_d(i)}+{_d((i+1)%10)})*{_r((i+1)%10)}-{_r((i+2)%10)}/2+1.5);")
    l5x = build_l5x(target_name="CptTags", tags_xml=_POOL_TAGS_XML, extra_rungs_xml=rungs_tags)
    _write(l5x, "instr_cpt_tagoperands_n01000", f"{count} rungs of CPT with real tag operands (vs literal below)")

    rungs_literal = rungs_xml(count, lambda i: f"CPT(R0,({i}+3)*2.5-1.2/4+2.5);")
    l5x = build_l5x(target_name="CptLiteral", tags_xml=_POOL_TAGS_XML, extra_rungs_xml=rungs_literal)
    _write(l5x, "instr_cpt_literaloperands_n01000", f"{count} rungs of CPT with literal constant operands (vs tags above)")


def group_comment_spotcheck() -> None:
    # 1-2 spot checks at real scale (not the whole matrix again) -- James:
    # "i think we can assume (do one/two spot tests) that rung comments are
    # not going to count."
    count = 5000
    rungs_no_comment = rungs_xml(count, INSTRUCTIONS["CPT"])
    l5x = build_l5x(target_name="CptNoComment", tags_xml=_POOL_TAGS_XML, extra_rungs_xml=rungs_no_comment)
    _write(l5x, "instr_cpt_n05000_nocomment", f"{count} rungs of CPT, no comments (spot check vs commented below)")

    comment_fn = lambda i: "x" * 100
    rungs_comment = rungs_xml(count, INSTRUCTIONS["CPT"], comment_fn)
    l5x = build_l5x(target_name="CptComment", tags_xml=_POOL_TAGS_XML, extra_rungs_xml=rungs_comment)
    _write(l5x, "instr_cpt_n05000_comment100", f"{count} rungs of CPT, 100-char comment on every rung (spot check)")


def main() -> None:
    group_instruction_sweep()
    group_jsr()
    group_lbl_jmp()
    group_tag_vs_literal()
    group_comment_spotcheck()
    n_instr = len(INSTRUCTIONS) + 2  # + JSR, LBL_JMP
    total = n_instr * len(COUNTS) + 2 + 2
    print(f"\nDone. {n_instr} instruction groups x {len(COUNTS)} counts + 2 tag-vs-literal + 2 comment spot-checks = {total} files.")


if __name__ == "__main__":
    main()
