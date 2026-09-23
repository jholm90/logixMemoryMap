"""OQ-OPERANDSHAPE: does a member-path operand cost more than a plain tag?

Why this family exists. With the JSR caller base corrected (OQ-JSRCALLERBASE),
the eighteen real programs under-predict by about 3.2%, and the residual scales
with logic size rather than with any one category. The generated composites
that now fit within +-1% differ from real programs in one gross way:

    operand shape          real programs    composites
    plain tag                  48.7%          ~75%
    member path (A.B)          32.6%            0%
    nested member (A.B.C)      15.4%            0%
    deeper                      3.2%            0%

Every instruction weight in the model was fitted on plain-tag operands. Half of
all real operands are member paths, and none has ever been measured.

Each family holds ONE instruction and varies ONE operand's shape, at two rung
counts so the per-rung difference reads as a slope rather than a single point.
The tag inventory is identical in every file of the batch -- every tag and the
UDT definitions are declared everywhere -- so only the rung text moves.

  opshape_xic_{plain,mem,nest,arrmem,bitword}   XIC(<op>)OTE(Out)
  opshape_ote_{plain,mem,nest,arrmem}           XIC(In)OTE(<op>)
  opshape_mov_{plain,srcmem,dstmem,nest}        MOV(<src>,<dst>)

Differenced within each family against its own `plain` file at the same count.
Array-element (constant index) and bit-of-word operands are already in the
composites that fit; `arrmem` and `bitword` are included only as controls.

1756-L81E at firmware 35, like every generated file.

Run: python -m sample_gen.gen_operand_shape
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, collect_nested_datatypes, rung_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"

COUNTS = (250, 1000)

_SUB = [MemberSpec("Bit", "BOOL"), MemberSpec("Val", "DINT")]
_UDT = [
    MemberSpec("Bit", "BOOL"),
    MemberSpec("Val", "DINT"),
    MemberSpec("Sub", "OpShapeSub", nested_members=tuple(_SUB)),
]

ARMS: dict[str, tuple[str, dict[str, str]]] = {
    "xic": ("XIC({op})OTE(Out);", {
        "plain": "PB", "mem": "U.Bit", "nest": "U.Sub.Bit",
        "arrmem": "UA[2].Bit", "bitword": "PD.5",
    }),
    "ote": ("XIC(In)OTE({op});", {
        "plain": "PB", "mem": "U.Bit", "nest": "U.Sub.Bit", "arrmem": "UA[2].Bit",
    }),
    "mov": ("MOV({op});", {
        "plain": "PD,PD2", "srcmem": "U.Val,PD2", "dstmem": "PD,U.Val", "nest": "U.Sub.Val,PD2",
    }),
}


def _tags() -> str:
    return "\n".join([
        tag_xml("In", "BOOL"),
        tag_xml("Out", "BOOL"),
        tag_xml("PB", "BOOL"),
        tag_xml("PD", "DINT"),
        tag_xml("PD2", "DINT"),
        tag_xml("U", "OpShapeUdt", udt_members=_UDT),
        tag_xml("UA", "OpShapeUdt", dimensions=(4,), udt_members=_UDT),
    ])


def main() -> None:
    datatypes = collect_nested_datatypes("OpShapeUdt", _UDT)
    tags = _tags()
    written = 0
    for arm, (template, shapes) in ARMS.items():
        for shape, op in shapes.items():
            text = template.format(op=op)
            for n in COUNTS:
                rungs = "\n".join(rung_xml(i, text) for i in range(n))
                name = f"opshape_{arm}_{shape}_n{n:04d}"
                l5x = build_l5x(target_name=f"OpShape{arm.title()}{shape.title()}"[:24],
                                tags_xml=tags, extra_datatypes_xml=datatypes,
                                extra_rungs_xml=rungs)
                out = OUT_ROOT / f"{name}.L5X"
                predicted = write_sample(l5x, out)
                append_manifest_row(
                    name,
                    f"OQ-OPERANDSHAPE: {n} rungs of `{text}` -- the {arm.upper()} family's "
                    f"'{shape}' operand shape. Same tags and UDTs in every file of the batch; "
                    f"differenced against opshape_{arm}_{next(iter(shapes))}_n{n:04d}, which "
                    f"passes plain tags, and against its own other count for the slope.",
                    "logic_instr", out, predicted,
                )
                written += 1
    print(f"Done. {written} files.")


if __name__ == "__main__":
    main()
