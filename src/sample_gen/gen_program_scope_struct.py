"""OQ-PROGSCOPESTRUCT: does a UDT or array tag cost the same at program scope?

Program-scoped DINT tags are exact (tagscope_* at 10, 100 and 1,000 tags). A
program-scoped UDT or array tag has never been built: the element sweep over the
standard-processor real programs found `Program/Tags/Tag/Data/Structure` and
`.../Data/Array` in 14 of 17 programs and in no generated file that captured
clean. They are densest in the three worst-predicted programs (exports 27, 06
and 33: 102, 118 and 157 of them).

The same tags at controller scope and at program scope, at three counts, so each
scope pair differs only in where the tags are declared and each count step
differs only in how many:

  progscope_{ctl,prog}_udt_n{010,050,200}   a 7-member UDT (4 DINT, 2 BOOL, REAL)
  progscope_{ctl,prog}_arr_n{010,050,200}   DINT[20] arrays

One MainRoutine rung (NOP) in every file. 1756-L81E at firmware 35.

Run: python -m sample_gen.gen_program_scope_struct
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, tag_xml, udt_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "tags"

COUNTS = (10, 50, 200)
_UDT = "ProgScopeUdt"
_MEMBERS = [
    MemberSpec("A", "DINT"), MemberSpec("B", "DINT"), MemberSpec("C", "DINT"),
    MemberSpec("D", "DINT"), MemberSpec("On", "BOOL"), MemberSpec("Off", "BOOL"),
    MemberSpec("Val", "REAL"),
]


def main() -> None:
    datatypes = udt_xml(_UDT, _MEMBERS)
    written = 0
    for kind in ("udt", "arr"):
        for n in COUNTS:
            if kind == "udt":
                tags = "\n".join(tag_xml(f"S{i:03d}", _UDT, udt_members=_MEMBERS) for i in range(n))
                what = f"{n} tags of a 7-member UDT (4 DINT, 2 BOOL, REAL)"
            else:
                tags = "\n".join(tag_xml(f"S{i:03d}", "DINT", dimensions=(20,)) for i in range(n))
                what = f"{n} DINT[20] array tags"
            for scope in ("ctl", "prog"):
                name = f"progscope_{scope}_{kind}_n{n:03d}"
                l5x = build_l5x(
                    target_name=f"ProgScope{scope.title()}{kind.title()}{n}",
                    tags_xml=tags if scope == "ctl" else "",
                    extra_program_tags_xml=tags if scope == "prog" else "",
                    extra_datatypes_xml=datatypes,
                )
                out = OUT_ROOT / f"{name}.L5X"
                predicted = write_sample(l5x, out)
                append_manifest_row(
                    name,
                    f"OQ-PROGSCOPESTRUCT: {what} declared at "
                    f"{'CONTROLLER' if scope == 'ctl' else 'PROGRAM (MainProgram)'} scope. "
                    f"Differenced against progscope_{'prog' if scope == 'ctl' else 'ctl'}_{kind}_n{n:03d}, "
                    f"which holds the identical tags at the other scope.",
                    "tags", out, predicted,
                )
                written += 1
    print(f"Done. {written} files.")


if __name__ == "__main__":
    main()
