"""LBL/JMP validation-rule sweep (James, 2026-08-23): "you can have
multiple jmp to one lbl but you must always have at least one lbl. You can
have a lbl with no jmp, but you cannot have a jmp with no lbl. Jmp/lbl are
limited to the same subroutine."

The existing confirmed data (docs/MEMORY_MODEL.md, RESOLVED_QUESTIONS.md
OQ-LBLJMP-STALE) is a combined 104-blocks/pair weight from a strict 1:1
LBL:JMP pairing (`gen_logic_sweep.py`'s `group_lbl_jmp`) -- explicitly
flagged as unvalidated for any other ratio. This generator tests the
ratios James describes that the 1:1 sweep can't distinguish:

  A. group_many_jmp_one_lbl -- N JMPs all targeting the SAME single LBL
     (2/5/10). If LBL's own cost is genuinely a flat one-time thing and
     JMP's is genuinely a flat per-instruction thing, total cost should be
     lbl_fixed + N*jmp_marginal -- directly separates LBL's cost from
     JMP's for the first time (the 1:1 sweep couldn't, since count scaled
     both together).
  B. group_lbl_no_jmp -- LBL rungs with ZERO corresponding JMPs (1/5/10).
     A legal shape per James ("You can have a lbl with no jmp") -- isolates
     LBL's own per-instance marginal cost directly, no JMP mixed in at all.
  C. group_samename_different_routines -- the "same subroutine" scoping
     constraint: two separate subroutines, each with its own LBL/JMP pair
     using the IDENTICAL label name. Not really a byte-size question, but
     cheap to confirm alongside the others -- validates labels are scoped
     per-routine (no collision), which matters for realistic multi-
     subroutine programs that reuse common label names like "Start"/"End".

Deliberately does NOT attempt a JMP with no matching LBL anywhere in the
same routine (James: "you cannot have a jmp with no lbl") -- that's not a
real, buildable program, so there's nothing to generate; noted here for
completeness rather than as a test case.

Run: python -m sample_gen.gen_lbljmp_rules
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import program_xml, rung_xml
from sample_gen.gen_logic_sweep import _POOL_TAGS_XML
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"


def _write(l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "lbljmp_rules", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


def group_many_jmp_one_lbl() -> None:
    for n_jmp in [2, 5, 10]:
        rungs = [rung_xml(0, "LBL(Target)NOP();")]
        for i in range(n_jmp):
            rungs.append(rung_xml(i + 1, "JMP(Target);"))
        l5x = build_l5x(target_name="LblManyJmp", tags_xml=_POOL_TAGS_XML, extra_rungs_xml="\n".join(rungs))
        out_name = f"lbljmp_manytoone_n{n_jmp:02d}"
        _write(l5x, out_name, f"1 LBL, {n_jmp} JMPs all targeting it -- isolates LBL cost from JMP's own per-instance cost")


def group_lbl_no_jmp() -> None:
    for n_lbl in [1, 5, 10]:
        rungs = [rung_xml(i, f"LBL(L{i})NOP();") for i in range(n_lbl)]
        l5x = build_l5x(target_name="LblNoJmp", tags_xml=_POOL_TAGS_XML, extra_rungs_xml="\n".join(rungs))
        out_name = f"lbljmp_lblonly_n{n_lbl:02d}"
        _write(l5x, out_name, f"{n_lbl} LBL rungs, zero JMPs -- isolates LBL's own marginal cost with no JMP mixed in")


def group_samename_different_routines() -> None:
    main_rungs = "\n".join([
        rung_xml(0, "LBL(Common)NOP();"),
        rung_xml(1, "JMP(Common);"),
    ])
    second_routine_rungs = "\n".join([
        rung_xml(0, "LBL(Common)NOP();"),
        rung_xml(1, "JMP(Common);"),
    ])
    second_program = program_xml("SecondProgram", rungs_xml_body=second_routine_rungs)
    l5x = build_l5x(
        target_name="LblSameName", tags_xml=_POOL_TAGS_XML, extra_rungs_xml=main_rungs,
        extra_programs_xml=second_program,
    )
    _write(l5x, "lbljmp_samename_diffroutines",
           "Two separate programs/routines, each with its own LBL(Common)/JMP(Common) pair using the "
           "identical label name -- confirms per-routine label scoping, no collision")


def main() -> None:
    group_many_jmp_one_lbl()
    group_lbl_no_jmp()
    group_samename_different_routines()
    print("\nDone. 7 files.")


if __name__ == "__main__":
    main()
