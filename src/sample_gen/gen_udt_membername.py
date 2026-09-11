"""UDT MEMBER NAME LENGTH -- an unmodelled variable, found 2026-09-11.

The `alarmsep` batch came back short by a law that fits its own 15 points
with zero residual:

    deficit = udt_definitions x (8 + 8 * floor(bool_members / 2))

That reads as a BOOL-member cost, and it is wrong. `udttype_bool_n4` is a
STRUCTURAL TWIN of `alarmsep_u01_b04` -- one UDT, one hidden backing SINT,
four BIT members, no tags, both type names bucketing to the same
ceil(len/8) -- and it predicts EXACTLY, while alarmsep_u01_b04 is 24 short.
The only thing that differs is the member names: `M0`..`M3` against
`Sts_A00`..`Sts_A03`, two characters against seven.

So the driver is member name length, or something else that travels with
it, and the alarmsep files cannot separate the two because they vary BOOL
count and total name length together. Nothing is wired off that law until
this batch says which it is.

The stake is not small. `udt_definition` charges for the TYPE name
(name_per_8_chars) and nothing at all for member names, and every
generator this model was ever fitted against used two- or three-character
member names. Real programs do not:

    311DGeneratedProgram          689 members, avg  8.2 chars
    BaillieLeitchField_Edger      619 members, avg 10.2 chars
    Elmsdale                      877 members, avg 10.7 chars
    SJ_Gormley                    509 members, avg  9.8 chars
    FlareFunction_311D          2,284 members, avg  9.7 chars
    BAI10048_TrimmerTally       1,861 members, avg 12.3 chars

If a member name costs anything, every real file is systematically
under-charged in proportion to how many members it declares, and the whole
corpus is blind to it by construction.

Five arms, type name held at exactly 8 characters throughout so the
already-modelled type-name bucket cannot move:

  A  udtmn_bool_short_b*   BOOL count, 2-char names   -- the control.
                           Should predict exactly, matching udttype_bool_n4.
  B  udtmn_bool_l07_b*     BOOL count, 7-char names   -- reproduces the
                           alarmsep deficit with no alarm definitions
                           anywhere near it.
  C  udtmn_bool_len*_b04   name length at 4 BOOLs     -- the pure
                           name-length sweep. Flat, per character, or
                           bucketed by 8 the way every other name cost in
                           this model is?
  D  udtmn_dint_len*_n04   name length at 4 DINTs     -- is it a member
                           cost or specifically a BOOL cost? BOOLs are the
                           one member kind with a hidden backing SINT, so
                           this is the arm that rules that in or out.
  E  udtmn_bool_len*_b16   name length at 16 BOOLs    -- 16 is where the
                           alarmsep law needed floor(b/2) rather than a
                           flat per-member rate, and where a second
                           backing SINT appears. If the length cost is
                           per-member it should be independent of b.
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, udt_xml
from sample_gen.lint import lint_or_raise
from sample_gen.manifest import append_manifest_row, predicted_bytes
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "udt"

# Every type name is exactly 8 characters, so ceil(len/8) is 1 in every
# file and the modelled type-name term is constant across the whole batch.
TYPE_NAME_LEN = 8

BOOL_COUNTS = (1, 2, 4, 8, 16)
NAME_LENGTHS = (2, 4, 8, 12, 16, 24, 32)

# 2-character names have to stay unique out to 16 members, so the index
# runs 0-9 then a-f rather than zero-padding.
_SHORT_SUFFIX = "0123456789abcdef"


def _member_name(index: int, length: int) -> str:
    """A unique member name of exactly `length` characters.

    Padded with LETTERS, never underscores -- a trailing or doubled
    underscore is rejected by Studio 5000 outright, see
    builders.validate_logix_name.
    """
    if length == 2:
        return "M" + _SHORT_SUFFIX[index]
    stem = f"M{index:02d}"
    if length < len(stem):
        raise ValueError(f"name length {length} is below the {len(stem)}-char stem")
    return stem + "x" * (length - len(stem))


def _type_name(stem: str) -> str:
    name = f"Udt{stem}"
    if len(name) > TYPE_NAME_LEN:
        raise ValueError(f"type name {name!r} exceeds {TYPE_NAME_LEN} characters")
    return name + "z" * (TYPE_NAME_LEN - len(name))


def _write(l5x: str, name: str, description: str) -> None:
    out = OUT_ROOT / f"{name}.L5X"
    lint_or_raise(l5x, context=str(out))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(l5x, encoding="utf-8")
    append_manifest_row(name, description, "udt", out, predicted_bytes(l5x))
    print(f"Wrote {out}")


def _emit(sample_id: str, type_stem: str, data_type: str, count: int,
          name_length: int, description: str) -> None:
    members = [
        MemberSpec(_member_name(i, name_length), data_type)
        for i in range(count)
    ]
    _write(
        build_l5x(
            target_name="UdtMemNam",
            tags_xml="",
            extra_datatypes_xml=udt_xml(_type_name(type_stem), members),
        ),
        sample_id,
        description,
    )


def main() -> None:
    # A: control -- BOOL count at the 2-character names every earlier
    # generator used. Predicts exactly today; any deviation would mean the
    # contradiction is not about names at all.
    for b in BOOL_COUNTS:
        _emit(
            f"udtmn_bool_short_b{b:02d}", f"S{b:02d}", "BOOL", b, 2,
            f"{b} BOOL member(s) with 2-character names, 8-character type name. "
            f"The control arm: this is the shape the udt_definition formula was "
            f"fitted on, and it should predict exactly. OQ-UDTMEMBERNAME.",
        )

    # B: the same counts at alarmsep's own 7-character names, with no
    # alarm definitions anywhere in the file.
    for b in BOOL_COUNTS:
        _emit(
            f"udtmn_bool_l07_b{b:02d}", f"L{b:02d}", "BOOL", b, 7,
            f"{b} BOOL member(s) with 7-character names -- alarmsep's exact "
            f"member shape with no alarm definitions in the file. Against "
            f"udtmn_bool_short_b{b:02d} the difference is the name length alone. "
            f"OQ-UDTMEMBERNAME.",
        )

    # C: the pure name-length sweep.
    for length in NAME_LENGTHS:
        _emit(
            f"udtmn_bool_len{length:02d}_b04", f"B{length:02d}", "BOOL", 4, length,
            f"4 BOOL members with {length}-character names. Swept against the "
            f"other lengths this says whether a member name is free, charged "
            f"per character, or bucketed by 8 the way the type name and every "
            f"alias tag already are. OQ-UDTMEMBERNAME.",
        )

    # D: same sweep on DINT, to separate "member name" from "BOOL".
    for length in (2, 7, 16, 32):
        _emit(
            f"udtmn_dint_len{length:02d}_n04", f"D{length:02d}", "DINT", 4, length,
            f"4 DINT members with {length}-character names. BOOLs are the one "
            f"member kind carrying a hidden backing SINT, so this arm rules a "
            f"BOOL-specific explanation in or out. OQ-UDTMEMBERNAME.",
        )

    # E: name length at the count where a second backing SINT appears.
    for length in (2, 7, 16):
        _emit(
            f"udtmn_bool_len{length:02d}_b16", f"X{length:02d}", "BOOL", 16, length,
            f"16 BOOL members with {length}-character names -- two backing "
            f"SINTs. If the name cost is per member it is independent of the "
            f"count; the alarmsep law needed floor(b/2), which is not. "
            f"OQ-UDTMEMBERNAME.",
        )


if __name__ == "__main__":
    main()
