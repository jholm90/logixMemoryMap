"""Batch 3 follow-up sweep (2026-08-25) -- targeted extensions to close the
specific gaps flagged while mining the previous real-data batch, per the
standing procedure in CLAUDE.md ("group tests into a batch of at least 60
items, don't want short runs"). Six independent fronts, each answering one
open question from docs/OPEN_QUESTIONS.md rather than broad re-testing:

  A. AOI array-packing, pure-BOOL boundary crossing (OQ-AOIBOOLPACK). The
     pure-BOOL family's real per-instance marginal (~4/instance) wasn't
     cleanly linear across 1/5/10/25/50 -- consistent with genuine 32-bit
     packed-word behavior, but none of those counts actually straddle a
     32-element boundary. n=16/31/32/33/48/64/65/96 does.
  B. AOI array-packing, BOOL:non-BOOL ratio sweep (same OQ). The mixed
     shape's clean 64-bytes/instance was only tested at one ratio (15
     BOOL : 15 non-BOOL, i.e. 50%). 6 more ratios (1:29 through 29:1) at
     4 count points each, to see whether 64 is a genuine half-of-128
     relationship or an artifact of the 50% ratio specifically.
  C. Custom-string maxlen extension (OQ-STRINGTAGOVERHEAD). Only 3 maxlen
     points exist (50, 250, 500) fitting a "maxlen mod 4" 2-bucket
     hypothesis on marginal rate (-2/tag vs -4/tag). 4 more maxlens
     (100, 300, 51, 1000) at the same 1/10/100/1000 count sweep to
     actually test that hypothesis instead of assuming it from 3 points.
  D. Indirect addressing, more count points (OQ-INDIRECT). The tag-index
     and tag-offset-index variants only have ONE count point each
     (n=1000) -- can't confirm the ~84/~108-per-rung reading is really
     linear. n=10/50/100 for both.
  E. JSR per-parameter cost, more count points (OQ-JSRPARAMCOST). Only
     1/5/10 params exist (not evenly spaced, no confirmed intercept).
     2/3/4/6/8/12 params fill in the curve.
  F. Per-Task overhead, one more data point + a program-vs-task
     disentangling variant (OQ item 11). n=4 tasks extends the existing
     n=2/n=3 linear read; a 2-PROGRAM-same-TASK file (vs the existing
     2-task files, which are always 1 program each) is the only way to
     tell whether the -1,472/extra-task marginal is really about Tasks
     specifically or just Programs.

Run: python -m sample_gen.gen_batch3_followups
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import (
    MemberSpec,
    aoi_xml,
    custom_string_type_xml,
    program_xml,
    rung_xml,
    rungs_xml,
    tag_xml,
    task_xml,
)
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

AOI_OUT = Path(__file__).parent.parent.parent / "samples" / "generated" / "aoi"
TAGS_OUT = Path(__file__).parent.parent.parent / "samples" / "generated" / "tags"
LOGIC_OUT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"


def _write(out_root: Path, l5x: str, out_name: str, description: str, category: str) -> None:
    out_path = out_root / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, category, out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


# ---------------------------------------------------------------------------
# A. Pure-BOOL AOI array, 32-element packing-boundary crossing
# ---------------------------------------------------------------------------

def group_a_bool_boundary() -> int:
    inputs = [MemberSpec(f"In{i}", "BOOL") for i in range(10)]
    outputs = [MemberSpec(f"Out{i}", "BOOL") for i in range(10)]
    locals_ = [MemberSpec(f"Loc{i}", "BOOL") for i in range(10)]
    definition, storage = aoi_xml("AoiPureBoolBoundary", inputs, outputs, [], locals_)
    n = 0
    for count in [16, 31, 32, 33, 48, 64, 65, 96]:
        tag = tag_xml("TestInstanceArray", "AoiPureBoolBoundary", dimensions=(count,), udt_members=storage)
        l5x = build_l5x(target_name="AoiPureBoolBoundary", tags_xml=tag, extra_aoi_xml=definition)
        _write(AOI_OUT, l5x, f"aoipack_bool_boundary_n{count:02d}",
               f"AOI, 10 BOOL In/10 BOOL Out/10 BOOL Local, array of {count} instances -- "
               f"32-bit packed-word boundary crossing check",
               "aoi_array_packing")
        n += 1
    return n


# ---------------------------------------------------------------------------
# B. Mixed BOOL:non-BOOL ratio sweep (fixed 30 members, ratio varies)
# ---------------------------------------------------------------------------

def group_b_ratio_sweep() -> int:
    ratios = [(1, 29), (5, 25), (10, 20), (20, 10), (25, 5), (29, 1)]
    counts = [1, 10, 25, 50]
    n = 0
    for n_bool, n_atomic in ratios:
        aoi_name = f"AoiRatio{n_bool:02d}b{n_atomic:02d}a"
        inputs = ([MemberSpec(f"InB{i}", "BOOL") for i in range(n_bool)]
                  + [MemberSpec(f"InA{i}", "DINT") for i in range(n_atomic)])
        definition, storage = aoi_xml(aoi_name, inputs, [], [], [])
        out_prefix = f"aoipack_ratio_{n_bool:02d}b{n_atomic:02d}a"
        for count in counts:
            tag = tag_xml("TestInstanceArray", aoi_name, dimensions=(count,), udt_members=storage)
            l5x = build_l5x(target_name=aoi_name, tags_xml=tag, extra_aoi_xml=definition)
            _write(AOI_OUT, l5x, f"{out_prefix}_array_n{count:02d}",
                   f"AOI, {n_bool} BOOL + {n_atomic} DINT Input params (ratio {n_bool}:{n_atomic} of 30), "
                   f"array of {count} instances -- BOOL:non-BOOL ratio sweep",
                   "aoi_array_packing")
            n += 1
    return n


# ---------------------------------------------------------------------------
# C. Custom-string maxlen extension
# ---------------------------------------------------------------------------

def group_c_customstring_maxlen() -> int:
    n = 0
    for maxlen in [100, 300, 51, 1000]:
        datatype = custom_string_type_xml(f"CStrB3_{maxlen}", maxlen)
        for count in [1, 10, 100, 1000]:
            tags = "\n".join(
                tag_xml(f"CS{i:04d}", f"CStrB3_{maxlen}", string_max_len=maxlen) for i in range(count)
            )
            l5x = build_l5x(target_name=f"CStrB3N{count}L{maxlen}", tags_xml=tags, extra_datatypes_xml=datatype)
            _write(TAGS_OUT, l5x, f"stringoverhead_custom{maxlen}_n{count:05d}",
                   f"{count} instances of a {maxlen}-char custom string type -- maxlen-extension sweep "
                   f"(maxlen mod 4 = {maxlen % 4})",
                   "string_tagoverhead")
            n += 1
    return n


# ---------------------------------------------------------------------------
# D. Indirect addressing, more count points
# ---------------------------------------------------------------------------

def group_d_indirect_counts() -> int:
    tags_xml = "\n".join([
        tag_xml("Arr", "DINT", dimensions=(20,)),
        tag_xml("Dest", "DINT"),
        tag_xml("Idx", "DINT"),
    ])
    n = 0
    for count in [10, 50, 100]:
        fn_indirect = lambda i: "MOV(Arr[Idx],Dest);"
        rungs = rungs_xml(count, fn_indirect)
        l5x = build_l5x(target_name=f"IndirectTagN{count}", tags_xml=tags_xml, extra_rungs_xml=rungs)
        _write(LOGIC_OUT, l5x, f"indirect_tag_index_n{count:05d}",
               f"{count} rungs of MOV(Arr[Idx],Dest) -- indirect/tag-driven array index, count-sweep point",
               "logic_instr")
        n += 1

        fn_offset = lambda i: "MOV(Arr[Idx+1],Dest);"
        rungs = rungs_xml(count, fn_offset)
        l5x = build_l5x(target_name=f"IndirectTagOffsetN{count}", tags_xml=tags_xml, extra_rungs_xml=rungs)
        _write(LOGIC_OUT, l5x, f"indirect_tag_offset_index_n{count:05d}",
               f"{count} rungs of MOV(Arr[Idx+1],Dest) -- indirect index with arithmetic offset, count-sweep point",
               "logic_instr")
        n += 1
    return n


# ---------------------------------------------------------------------------
# E. JSR per-parameter cost, more count points
# ---------------------------------------------------------------------------

def _sub_routine_xml(routine_name: str, in_locals: list[str]) -> str:
    sbr_rung = rung_xml(0, f"SBR({','.join(in_locals)})NOP();" if in_locals else "SBR()NOP();")
    ret_rung = rung_xml(1, "RET();")
    return (
        f'<Routine Name="{routine_name}" Type="RLL">'
        f"<RLLContent>{sbr_rung}\n{ret_rung}</RLLContent>"
        "</Routine>"
    )


def group_e_jsr_paramcounts() -> int:
    rung_count = 100
    n = 0
    for param_count in [2, 3, 4, 6, 8, 12]:
        caller_args = [f"JIn{i}" for i in range(param_count)]
        callee_locals = [f"LIn{i}" for i in range(param_count)]
        caller_tags = "\n".join(tag_xml(t, "DINT") for t in caller_args)
        routine_name = f"JsrParamTargetN{param_count}"
        sub_xml = _sub_routine_xml(routine_name, callee_locals)

        call_args = ",".join([str(param_count)] + caller_args)
        fn = lambda i, call_args=call_args, routine_name=routine_name: f"JSR({routine_name},{call_args});"
        rungs = rungs_xml(rung_count, fn)
        l5x = build_l5x(target_name=f"JsrParamN{param_count}", tags_xml=caller_tags, extra_rungs_xml=rungs,
                         extra_routines_xml=sub_xml)
        _write(LOGIC_OUT, l5x, f"jsr_paramcount_n{param_count:02d}_r{rung_count:05d}",
               f"{rung_count} rungs of JSR to a subroutine with {param_count} pure-input params -- "
               f"per-param cost, additional count-sweep point",
               "jsr_sbr_ret")
        n += 1
    return n


# ---------------------------------------------------------------------------
# F. Per-Task overhead, one more point + program-vs-task disentangle
# ---------------------------------------------------------------------------

def group_f_task_overhead() -> int:
    n = 0
    # F1: n=4 total tasks (extends the existing n=2/n=3 linear read)
    programs, tasks = [], []
    for i in range(3):
        prog_name = f"ExtraProgramB3_{i}"
        programs.append(program_xml(prog_name))
        tasks.append(task_xml(f"ExtraTaskB3_{i}", prog_name, task_type="PERIODIC"))
    l5x = build_l5x(target_name="TaskOverheadN4", tags_xml="",
                     extra_programs_xml="\n".join(programs), extra_tasks_xml="\n".join(tasks))
    _write(LOGIC_OUT, l5x, "taskoverhead_n04tasks",
           "4 total Tasks (1 Continuous + 3 Periodic), each extra Task's Program has only a single NOP rung -- "
           "extends the n=2/n=3 per-Task marginal-cost sweep",
           "logic_instr")
    n += 1

    # F2: 1 Task, 2 Programs (disentangles per-Task vs per-Program overhead --
    # the existing n=2/n=3 files always add one Program PER extra Task, so
    # this is the first file that isolates an extra Program alone). The
    # extra Program must be registered as a second <ScheduledProgram> under
    # the SAME MainTask (extra_scheduled_programs_xml), not left unscheduled.
    extra_program = program_xml("ExtraProgramB3_SameTask")
    l5x = build_l5x(target_name="TaskOverheadSameTask2Prog", tags_xml="",
                     extra_programs_xml=extra_program,
                     extra_scheduled_programs_xml='<ScheduledProgram Name="ExtraProgramB3_SameTask"/>')
    _write(LOGIC_OUT, l5x, "programoverhead_n02progs_1task",
           "2 Programs under the SAME single Continuous Task (vs taskoverhead_n02tasks' 2 Tasks/2 Programs) -- "
           "isolates per-Program overhead from per-Task overhead",
           "logic_instr")
    n += 1
    return n


def main() -> None:
    total = 0
    for fn in [group_a_bool_boundary, group_b_ratio_sweep, group_c_customstring_maxlen,
               group_d_indirect_counts, group_e_jsr_paramcounts, group_f_task_overhead]:
        count = fn()
        print(f"{fn.__name__}: {count} file(s)")
        total += count
    print(f"\nTotal: {total} sample(s) generated.")


if __name__ == "__main__":
    main()
