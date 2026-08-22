"""Instruction operand-TYPE sweep (James, 2026-08-21): "lots of these
instructions accept multiple data types as inputs and outputs... EQU(string1,
string2) will occupy different memory possibly from EQU(dint1,dint2). Of
course it would be more exaggerated for instructions with multiple data
parameters."

The first instruction sweep (gen_logic_sweep.py) tested one representative
operand type per instruction. This one holds the instruction and rung count
FIXED (1000 rungs, a scale already covered elsewhere for comparison) and
varies only the operand TYPE -- mirrors the atomic-type sweep that worked
for tags, now applied to logic operands. Prioritizes instructions with more
than 2 operands (ADD/SUB/MUL/DIV/MOD/LIM) since James's own reasoning is
that a type effect would show up more there, plus every comparison
instruction (his own EQU example) and MOV/CPT.

Uses its own small dedicated tag pool (separate from gen_logic_sweep.py's,
kept untouched for comparability with what's already been captured) with
5 tags of each type: SINT/INT/DINT/LINT/REAL/STRING.

Run: python -m sample_gen.gen_logic_typesweep
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import rungs_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"

RUNG_COUNT = 1000
NUMERIC_TYPES = ["SINT", "INT", "DINT", "LINT", "REAL"]
TYPE_PREFIX = {"SINT": "TS", "INT": "TI", "DINT": "TD", "LINT": "TL", "REAL": "TR"}


def _pool_tags_xml() -> str:
    parts = []
    for t in NUMERIC_TYPES:
        prefix = TYPE_PREFIX[t]
        for i in range(5):
            parts.append(tag_xml(f"{prefix}{i}", t))
    for i in range(5):
        parts.append(tag_xml(f"TSTR{i}", "STRING", string_max_len=82))
    return "\n".join(parts)


_POOL_TAGS_XML = _pool_tags_xml()


def _tag(t: str, i: int) -> str:
    return f"{TYPE_PREFIX[t]}{i % 5}"


# Two-operand comparisons: condition + trailing OTE (needs a BOOL output --
# reuse TS0 truncated? no, comparisons don't write a BOOL tag in real usage,
# they gate an output instruction -- use the type's own tag 0 as a stand-in
# "something changed" flag isn't needed; just need *a* BOOL to close the
# rung, borrow one fixed BOOL-typed... simplest: declare a few BOOL flags
# too, separate from the numeric pool, purely for closing comparison rungs.
def _bool_tag(i: int) -> str:
    return f"TB{i % 5}"


_POOL_TAGS_XML += "\n" + "\n".join(tag_xml(f"TB{i}", "BOOL") for i in range(5))

COMPARISON_INSTR = ["EQU", "NEQ", "GRT", "GEQ", "LES", "LEQ"]
MATH3_INSTR = ["ADD", "SUB", "MUL", "DIV", "MOD"]


def _write(l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "logic_instr", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


def group_comparison_type_sweep() -> None:
    for instr in COMPARISON_INSTR:
        for t in NUMERIC_TYPES:
            fn = lambda i, instr=instr, t=t: f"{instr}({_tag(t,i)},{_tag(t,i+1)})OTE({_bool_tag(i)});"
            rungs = rungs_xml(RUNG_COUNT, fn)
            l5x = build_l5x(target_name=f"{instr}{t}", tags_xml=_POOL_TAGS_XML, extra_rungs_xml=rungs)
            out_name = f"typesweep_{instr.lower()}_{t.lower()}_n{RUNG_COUNT:05d}"
            _write(l5x, out_name, f"{RUNG_COUNT} rungs of {instr} with {t} operands")


def group_math3_type_sweep() -> None:
    for instr in MATH3_INSTR:
        for t in NUMERIC_TYPES:
            fn = lambda i, instr=instr, t=t: f"{instr}({_tag(t,i)},{_tag(t,i+1)},{_tag(t,i+2)});"
            rungs = rungs_xml(RUNG_COUNT, fn)
            l5x = build_l5x(target_name=f"{instr}{t}", tags_xml=_POOL_TAGS_XML, extra_rungs_xml=rungs)
            out_name = f"typesweep_{instr.lower()}_{t.lower()}_n{RUNG_COUNT:05d}"
            _write(l5x, out_name, f"{RUNG_COUNT} rungs of {instr} with {t} operands")


def group_mov_type_sweep() -> None:
    for t in NUMERIC_TYPES:
        fn = lambda i, t=t: f"MOV({_tag(t,i)},{_tag(t,i+1)});"
        rungs = rungs_xml(RUNG_COUNT, fn)
        l5x = build_l5x(target_name=f"MOV{t}", tags_xml=_POOL_TAGS_XML, extra_rungs_xml=rungs)
        out_name = f"typesweep_mov_{t.lower()}_n{RUNG_COUNT:05d}"
        _write(l5x, out_name, f"{RUNG_COUNT} rungs of MOV with {t} operands")


def group_lim_type_sweep() -> None:
    # LIM has 3 operands (low/test/high) -- James: type effects "more
    # exaggerated" with multiple data parameters.
    for t in NUMERIC_TYPES:
        fn = lambda i, t=t: f"LIM({_tag(t,i)},{_tag(t,i+1)},{_tag(t,i+2)})OTE({_bool_tag(i)});"
        rungs = rungs_xml(RUNG_COUNT, fn)
        l5x = build_l5x(target_name=f"LIM{t}", tags_xml=_POOL_TAGS_XML, extra_rungs_xml=rungs)
        out_name = f"typesweep_lim_{t.lower()}_n{RUNG_COUNT:05d}"
        _write(l5x, out_name, f"{RUNG_COUNT} rungs of LIM with {t} operands")


def group_string_comparison() -> None:
    # James's own example: EQU(string1,string2) vs EQU(dint1,dint2) --
    # already have the DINT variant from group_comparison_type_sweep(),
    # this adds the STRING side directly.
    for instr in ["EQU", "NEQ"]:
        fn = lambda i, instr=instr: f"{instr}(TSTR{i%5},TSTR{(i+1)%5})OTE({_bool_tag(i)});"
        rungs = rungs_xml(RUNG_COUNT, fn)
        l5x = build_l5x(target_name=f"{instr}String", tags_xml=_POOL_TAGS_XML, extra_rungs_xml=rungs)
        out_name = f"typesweep_{instr.lower()}_string_n{RUNG_COUNT:05d}"
        _write(l5x, out_name, f"{RUNG_COUNT} rungs of {instr} with STRING operands (vs numeric types above)")


def group_cpt_type_sweep() -> None:
    # CPT's expression can mix types freely in real code -- test an
    # all-DINT expression vs an all-REAL one as a simpler 2-point check
    # (a full 5-type sweep isn't meaningful here since CPT's "operand" is
    # a whole expression, not fixed positional args).
    fn_dint = lambda i: f"CPT(TD{i%5},TD{(i+1)%5}+TD{(i+2)%5}*TD{(i+3)%5}-TD{(i+4)%5});"
    rungs = rungs_xml(RUNG_COUNT, fn_dint)
    l5x = build_l5x(target_name="CPTDintExpr", tags_xml=_POOL_TAGS_XML, extra_rungs_xml=rungs)
    _write(l5x, f"typesweep_cpt_dint_n{RUNG_COUNT:05d}", f"{RUNG_COUNT} rungs of CPT, all-DINT expression")

    fn_real = lambda i: f"CPT(TR{i%5},TR{(i+1)%5}+TR{(i+2)%5}*TR{(i+3)%5}-TR{(i+4)%5});"
    rungs = rungs_xml(RUNG_COUNT, fn_real)
    l5x = build_l5x(target_name="CPTRealExpr", tags_xml=_POOL_TAGS_XML, extra_rungs_xml=rungs)
    _write(l5x, f"typesweep_cpt_real_n{RUNG_COUNT:05d}", f"{RUNG_COUNT} rungs of CPT, all-REAL expression")


def main() -> None:
    group_comparison_type_sweep()
    group_math3_type_sweep()
    group_mov_type_sweep()
    group_lim_type_sweep()
    group_string_comparison()
    group_cpt_type_sweep()
    total = len(COMPARISON_INSTR) * 5 + len(MATH3_INSTR) * 5 + 5 + 5 + 2 + 2
    print(f"\nDone. {total} files.")


if __name__ == "__main__":
    main()
