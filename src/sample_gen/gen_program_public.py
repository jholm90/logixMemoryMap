"""OQ-PUBLICTAG: does a program-scope tag cost more when it is Usage="Public"?

Program-scoped UDT and array tags cost exactly what controller tags cost
(`progscope_prog_{udt,arr}_n{010,050,200}`, OQ-PROGSCOPESTRUCT). Three real programs declare
public program tags (83, 41 and 23 of them), and two of those are among the five worst
predicted. A public tag is reachable from other programs, which may give it a cost a local
one does not carry.

The six captured `progscope_prog_*` files rebuilt identically except that every program tag
carries `Usage="Public"` (target names keep their length). Each differences against its
`progscope_prog_*` twin. 1756-L81E at v35, realism floor.

Run: python -m sample_gen.gen_program_public
"""

from __future__ import annotations

from pathlib import Path

from sample_gen import realism
from sample_gen.builders import tag_xml, udt_xml
from sample_gen.gen_program_scope_struct import _MEMBERS, _UDT, COUNTS
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "tags"


def _public(xml: str) -> str:
    return xml.replace(' TagType="Base" ', ' TagType="Base" Usage="Public" ')


def main() -> None:
    datatypes = udt_xml(_UDT, _MEMBERS)
    for kind in ("udt", "arr"):
        for n in COUNTS:
            if kind == "udt":
                tags = "\n".join(_public(tag_xml(f"S{i:03d}", _UDT, udt_members=_MEMBERS)) for i in range(n))
                what = f"{n} tags of a 7-member UDT (4 DINT, 2 BOOL, REAL)"
            else:
                tags = "\n".join(_public(tag_xml(f"S{i:03d}", "DINT", dimensions=(20,))) for i in range(n))
                what = f"{n} DINT[20] array tags"
            assert tags.count('Usage="Public"') == n
            name = f"progpub_{kind}_n{n:03d}"
            l5x = build_l5x(target_name=f"ProgScopePubs{kind.title()}{n}",
                            **realism.with_baseline(extra_program_tags_xml=tags, extra_datatypes_xml=datatypes))
            out = OUT_ROOT / f"{name}.L5X"
            predicted = write_sample(l5x, out)
            append_manifest_row(
                name, f"OQ-PUBLICTAG: {what} at PROGRAM (MainProgram) scope, every one Usage=\"Public\". "
                      f"Identical to progscope_prog_{kind}_n{n:03d} except the Usage attribute; differenced "
                      f"against it. Realism floor.", "tags", out, predicted)
            print(f"Wrote {out.name} (predicted {predicted:,})")


if __name__ == "__main__":
    main()
