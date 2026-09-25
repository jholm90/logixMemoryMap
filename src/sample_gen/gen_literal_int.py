"""OQ-LITREAL, integer operands: literals against SINT, INT and DINT tags.

The controller handles every immediate value as a DINT, and a call mixing operand
types converts them to the highest-ranked type among them (SINT < INT < DINT < REAL);
SINT and INT sources are promoted to DINT by sign extension. So an integer literal
against a DINT tag should cost nothing, against an INT or SINT tag it makes the call a
mixed DINT/INT or DINT/SINT one, and a float literal makes any integer call a REAL
one. Captured so far: MOV(5,INT) and MOV(5,SINT) only (`litop_type_*_lit`), the one
instruction and position measured.

This batch covers the thirteen typed instructions `gen_literal_real` covers, for each
of SINT, INT and DINT, with the tested operand a tag of the call's own type (the
uniform control), the integer literal 5, or the float literal 5.0. Every file carries
the same inventory (SINT/INT/DINT arrays of 400 and scalars), 400 calls, every
destination and output distinct, realism floor, 1756-L81E at v35.

  litint_<type>_<mn>_tag    uniform <type>
  litint_<type>_<mn>_ilit   integer literal 5 in the tested position
  litint_<type>_<mn>_flit   float literal 5.0 in the tested position

`_ilit - _tag` and `_flit - _tag` per type and instruction; the DINT set is the
control that an integer literal against DINT is free.

Run: python -m sample_gen.gen_literal_int
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import rung_xml, tag_xml
from sample_gen.gen_literal_real import TEMPLATES
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.realism import with_baseline
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "litint"
CATEGORY = "literal_int"
N = 400
TYPES = {"SINT": "Ls", "INT": "Li", "DINT": "Ld"}


def _inventory() -> str:
    tags = []
    for t, p in TYPES.items():
        tags += [tag_xml(f"{p}A", t, (N,)), tag_xml(f"{p}D", t, (N,)),
                 tag_xml(f"{p}K", t), tag_xml(f"{p}Lo", t)]
    tags.append(tag_xml("LtQ", "BOOL", (N,)))
    return "\n".join(tags)


def _template(mn: str, prefix: str) -> str:
    return (TEMPLATES[mn].replace("LrA", f"{prefix}A").replace("LrD", f"{prefix}D")
            .replace("LrLo", f"{prefix}Lo").replace("LrQ", "LtQ"))


def _files() -> dict[str, tuple[list[str], str]]:
    f: dict[str, tuple[list[str], str]] = {}
    for t, p in TYPES.items():
        forms = {"tag": f"{p}K", "ilit": "5", "flit": "5.0"}
        for mn in TEMPLATES:
            tpl = _template(mn, p)
            for form, x in forms.items():
                what = {"tag": f"a {t} tag -- the uniform-{t} control",
                        "ilit": "the integer literal 5 (an immediate, handled as DINT)",
                        "flit": "the float literal 5.0"}[form]
                f[f"{t.lower()}_{mn.lower()}_{form}"] = (
                    [tpl.format(x=x, i=i) for i in range(N)],
                    f"{N} x `{tpl.format(x=x, i='i')}` -- {t} operands, the tested position holding "
                    f"{what}" + ("" if form == "tag" else f"; vs litint_{t.lower()}_{mn.lower()}_tag"))
    return f


def _write(sample_id: str, rungs: list[str], description: str, inventory: str) -> None:
    out = OUT_ROOT / f"{sample_id}.L5X"
    body = "\n".join(rung_xml(i, t) for i, t in enumerate(rungs))
    target = "".join(p.capitalize() for p in sample_id.split("_"))
    l5x = build_l5x(target_name=target, **with_baseline(tags_xml=inventory, extra_rungs_xml=body))
    predicted = write_sample(l5x, out)
    append_manifest_row(
        sample_id,
        f"OQ-LITREAL: {description}. Same inventory in every litint_* file, realism floor; "
        f"only the tested operand differs between the files of one type and instruction.",
        CATEGORY, out, predicted)
    print(f"Wrote {out.name} (predicted {predicted:,})")


def main() -> None:
    inventory = _inventory()
    _write("litint_n00", [], "control, no added rungs", inventory)
    for stem, (rungs, what) in _files().items():
        _write(f"litint_{stem}", rungs, what, inventory)


if __name__ == "__main__":
    main()
