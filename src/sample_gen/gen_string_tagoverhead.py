"""STRING/custom-string tag_overhead resolution sweep (James, 2026-08-25):
"Your final notes on strings and aois need more work. Generate as many
l5x files as needed to resolve all possible scenarios for 100% accuracy."

Follows up OQ-STRINGTAGOVERHEAD (2026-08-24): `string_builtin_x1000` and
`customstring_250char_x1000` both showed the engine over-predicting by
almost exactly -2 bytes/tag at n=1000 -- real and consistent across two
independent STRING families, but only ONE count point each, so it wasn't
possible to tell a genuine flat -2/tag rate from some other count-
dependent shape that happens to look flat at n=1000.

Three axes, all isolating whether `tag_overhead`'s confirmed atomic-type
formula (`84 + 8*floor(name_len/8)`, KNOWN, type-independent across SINT/
INT/DINT/LINT/REAL/BOOL) needs a STRING-specific correction:

  A. group_builtin_count -- built-in STRING (82-byte default), tag count
     1/2/5/10/25/50/100/500/1000. Dense enough to catch a non-linear shape
     if one exists, not just confirm a straight line between 2 points.
  B. group_customstring_count -- custom string type, count 1/10/100/1000,
     at TWO different max-lengths (50 and 500 chars) -- if the per-tag
     effect is identical regardless of max-length, that rules out "it's
     actually a DATA-length effect in disguise" and confirms it's a pure
     per-tag-declaration effect, same as the base formula's own type-
     independence.
  C. group_namelen -- STRING tag name length 4/8/16/32/40, fixed count
     (50 tags) -- confirms whether the *shape* of the name-length term is
     unchanged for STRING (same `8*floor(len/8)` step pattern) with only
     the flat base needing correction, vs. something structurally
     different.

All three groups together should be enough to write a confirmed,
STRING-specific `tag_overhead` correction (or confirm none is needed if
the count sweep reveals the -2/tag reading was itself noise/an artifact).

Run: python -m sample_gen.gen_string_tagoverhead
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import custom_string_type_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "tags"


def _write(l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "string_tagoverhead", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


def group_builtin_count() -> None:
    for n in [1, 2, 5, 10, 25, 50, 100, 500, 1000]:
        tags = "\n".join(tag_xml(f"Str{i:04d}", "STRING", string_max_len=82) for i in range(n))
        l5x = build_l5x(target_name=f"StrCountN{n}", tags_xml=tags)
        _write(l5x, f"stringoverhead_builtin_n{n:05d}",
               f"{n} built-in STRING (82-byte) tag instances -- per-tag overhead count sweep")


def group_customstring_count() -> None:
    for maxlen in [50, 500]:
        datatype = custom_string_type_xml(f"CStr{maxlen}", maxlen)
        for n in [1, 10, 100, 1000]:
            tags = "\n".join(tag_xml(f"CS{i:04d}", f"CStr{maxlen}", string_max_len=maxlen) for i in range(n))
            l5x = build_l5x(target_name=f"CStrN{n}L{maxlen}", tags_xml=tags, extra_datatypes_xml=datatype)
            _write(l5x, f"stringoverhead_custom{maxlen}_n{n:05d}",
                   f"{n} instances of a {maxlen}-char custom string type -- per-tag overhead count sweep, "
                   f"maxlen={maxlen} cross-check")


def group_namelen() -> None:
    n = 50
    for length in [4, 8, 16, 32, 40]:
        tags = []
        for i in range(n):
            suffix = f"_{i:02d}"
            base = f"S{suffix}"
            pad_needed = max(0, length - len(base))
            filler = ("_LONGNAME" * (pad_needed // 9 + 1))[:pad_needed]
            name = f"S{filler}{suffix}"
            tags.append(tag_xml(name, "STRING", string_max_len=82))
        l5x = build_l5x(target_name=f"StrNameLen{length}", tags_xml="\n".join(tags))
        _write(l5x, f"stringoverhead_namelen{length:02d}_n{n:03d}",
               f"{n} built-in STRING tags, name length {length} chars -- tag-name-length term cross-check for STRING")


def main() -> None:
    group_builtin_count()
    group_customstring_count()
    group_namelen()
    total = 9 + 8 + 5
    print(f"\nDone. {total} files.")


if __name__ == "__main__":
    main()
