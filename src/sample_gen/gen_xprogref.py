"""OQ-XPROGREF round 2 (2026-08-26, self-initiated per CLAUDE.md step 5 --
this project's standing rule is to decide and generate the next batch of
tests automatically once an open item is identified, not wait to be asked).

xprogref_twoprog_shared_alias showed a real, unexplained NEGATIVE gap
(-3948, engine over-predicts) -- the only finding in the whole project
running that direction. Hypothesis (unconfirmed): the second program's
alias to the same Controller-scoped global doesn't carry its own full
alias_overhead cost (some sharing/dedup at the tag-table level for repeat
references to the same underlying global). A single 2-program data point
can't distinguish "each additional program's alias costs less than the
first" from "there's a one-time discount that only applies once, at the
second reference." 3- and 4-program versions of the exact same pattern
(same 1000-rung XIC/OTE body, same global, one more program's own Local
alias to it each time) give the two more points needed: if the per-
program marginal gap keeps shrinking, it's linear-in-program-count; if it
plateaus after program 2, it's a one-time discount.

Original round 1 docs below, unchanged.

---

OQ-XPROGREF (James, 2026-08-22: "add it to the next batch"). Real Logix
has no direct cross-program tag-addressing syntax in ladder logic --
confirmed by searching the entire real corpus (47 files, including several
with real `Usage="Public"` program tags) for any `Program:Tag`-style
reference inside rung Text: none exists. What James actually described
earlier in this project ("my 311D program has a couple gGlobal tags and
local program alias inside each program referencing that controller tag")
is the real mechanism: a Controller-scoped global tag, with each program
that needs it declaring its own same-purpose Local alias pointing at that
global (alias_tag_xml, already confirmed real shape from OQ-ALIASSIZE).

Three files, all at RUNG_COUNT=1000 (directly comparable to the confirmed
XIC weight from the 244-file sweep: 20 blocks/rung marginal, no alias):

  1. xprogref_singleprog_alias -- ONE program, logic references a
     Controller-scoped global via a Local alias (not directly). Isolates
     "does routing through an alias cost extra in logic" from
     "cross-program-ness" specifically.
  2. xprogref_twoprog_shared_alias -- TWO programs, each with its OWN Local
     alias pointing at the SAME Controller-scoped global, each running the
     same 1000-rung XIC/OTE pattern. The real-world cross-program-sharing
     pattern. Compare each program's per-rung marginal cost against file 1
     -- does a second program aliasing the same global change anything?

Run: python -m sample_gen.gen_xprogref
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import alias_tag_xml, program_xml, program_tag_xml, rungs_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"
RUNG_COUNT = 1000


def _write(l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "logic_instr", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


def group_singleprog_alias() -> None:
    global_tag = tag_xml("gGlobalFlag", "BOOL")
    prog_tags = alias_tag_xml("LocalAliasA", "gGlobalFlag") + "\n" + program_tag_xml("OutA", "BOOL")
    fn = lambda i: "XIC(LocalAliasA)OTE(OutA);"
    rungs = rungs_xml(RUNG_COUNT, fn)
    l5x = build_l5x(target_name="XProgRefSingle", tags_xml=global_tag, extra_program_tags_xml=prog_tags,
                     extra_rungs_xml=rungs)
    _write(l5x, f"xprogref_singleprog_alias_n{RUNG_COUNT:05d}",
           f"{RUNG_COUNT} rungs of XIC/OTE, single program, referencing a Controller-scoped global via a Local alias")


def group_twoprog_shared_alias() -> None:
    global_tag = tag_xml("gGlobalFlag", "BOOL")

    a_tags = alias_tag_xml("LocalAliasA", "gGlobalFlag") + "\n" + program_tag_xml("OutA", "BOOL")
    fn_a = lambda i: "XIC(LocalAliasA)OTE(OutA);"
    rungs_a = rungs_xml(RUNG_COUNT, fn_a)

    b_tags = alias_tag_xml("LocalAliasB", "gGlobalFlag") + "\n" + program_tag_xml("OutB", "BOOL")
    fn_b = lambda i: "XIC(LocalAliasB)OTE(OutB);"
    rungs_b = rungs_xml(RUNG_COUNT, fn_b)
    prog_b = program_xml("ProgB", tags_xml=b_tags, rungs_xml_body=rungs_b)

    l5x = build_l5x(target_name="XProgRefTwo", tags_xml=global_tag, extra_program_tags_xml=a_tags,
                     extra_rungs_xml=rungs_a, extra_programs_xml=prog_b,
                     extra_scheduled_programs_xml='<ScheduledProgram Name="ProgB"/>')
    _write(l5x, f"xprogref_twoprog_shared_alias_n{RUNG_COUNT:05d}",
           f"Two programs, each {RUNG_COUNT} rungs of XIC/OTE via its own Local alias to the SAME Controller-scoped "
           f"global -- the real cross-program-sharing pattern, vs xprogref_singleprog_alias baseline")


def _group_nprog_shared_alias(program_letters: list[str]) -> None:
    # program_letters e.g. ["A", "B", "C"] -> 3 programs total, A is the
    # "primary" program (its rungs/tags go in the top-level Controller
    # Program block, matching group_twoprog_shared_alias's ProgA shape),
    # B/C/... are extra <Program> blocks.
    global_tag = tag_xml("gGlobalFlag", "BOOL")

    a_tags = alias_tag_xml("LocalAliasA", "gGlobalFlag") + "\n" + program_tag_xml("OutA", "BOOL")
    fn_a = lambda i: "XIC(LocalAliasA)OTE(OutA);"
    rungs_a = rungs_xml(RUNG_COUNT, fn_a)

    extra_programs = []
    extra_scheduled = []
    for letter in program_letters[1:]:
        tags = alias_tag_xml(f"LocalAlias{letter}", "gGlobalFlag") + "\n" + program_tag_xml(f"Out{letter}", "BOOL")
        fn = lambda i, letter=letter: f"XIC(LocalAlias{letter})OTE(Out{letter});"
        rungs = rungs_xml(RUNG_COUNT, fn)
        extra_programs.append(program_xml(f"Prog{letter}", tags_xml=tags, rungs_xml_body=rungs))
        extra_scheduled.append(f'<ScheduledProgram Name="Prog{letter}"/>')

    n = len(program_letters)
    l5x = build_l5x(
        target_name=f"XProgRef{n}",
        tags_xml=global_tag,
        extra_program_tags_xml=a_tags,
        extra_rungs_xml=rungs_a,
        extra_programs_xml="\n".join(extra_programs),
        extra_scheduled_programs_xml="\n".join(extra_scheduled),
    )
    _write(
        l5x, f"xprogref_{n}prog_shared_alias_n{RUNG_COUNT:05d}",
        f"{n} programs, each {RUNG_COUNT} rungs of XIC/OTE via its own Local alias to the SAME "
        f"Controller-scoped global -- disentangles xprogref_twoprog_shared_alias's unexplained -3948 "
        f"negative gap: is the per-program marginal discount linear-in-count, or a one-time thing that "
        f"only applies once?",
    )


def group_threeprog_shared_alias() -> None:
    _group_nprog_shared_alias(["A", "B", "C"])


def group_fourprog_shared_alias() -> None:
    _group_nprog_shared_alias(["A", "B", "C", "D"])


def main() -> None:
    group_singleprog_alias()
    group_twoprog_shared_alias()
    group_threeprog_shared_alias()
    group_fourprog_shared_alias()
    print("\nDone. 4 files.")


if __name__ == "__main__":
    main()
