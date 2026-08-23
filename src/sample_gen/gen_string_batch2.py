"""STRING accuracy batch 2 (James, 2026-08-25): "Sounds like you still
don't know what is going on with strings. Make another 20 tests to figure
this out. You need 100% accuracy for strings and custom length strings."

Targets real gaps left after the first STRING sweep (gen_string_
tagoverhead.py, OQ-STRINGTAGOVERHEAD): built-in STRING is fully resolved,
but custom-length strings are not, and several structural contexts (array-
of-STRING, STRING-as-UDT-member) were never tested at all -- not "assumed
the same as a scalar tag," genuinely never generated.

  A. group_mod4_bucket1 -- custom-string maxlen values congruent to 1 mod
     4 (49/101/501), a bucket the existing 3-point "maxlen mod 4"
     hypothesis (OQ-STRINGTAGOVERHEAD: mod4=2 -> k=2/tag, mod4=0 -> k=4/tag)
     has NO data for at all. 2 count points each (n=1, n=100) to read a
     marginal rate per maxlen.
  B. group_string_array -- array-of-STRING as ONE tag (Dimensions=N),
     never tested before (every prior STRING test was N separate scalar
     tags). Real shape confirmed against 2 independent corpus examples
     (see builders.string_array_tag_xml) -- structurally different XML
     from a scalar STRING tag (L5K+Decorated, not L5K+String), so the
     per-element cost inside an array could plausibly differ from the
     per-tag cost of N separate STRING tags. Both built-in and one custom
     type, at 2 count points each.
  C. group_string_udt_member -- STRING (built-in and custom) as a UDT
     member, not a standalone tag. The XML shape exists and is already
     coded (_string_structure_member_xml), but no real byte-size data has
     ever been captured for this context -- genuinely untested, not just
     unconfirmed.
  D. group_namelen_custom -- name-length x custom-maxlen interaction.
     The existing namelen cross-check (stringoverhead_namelen*) only
     tested built-in STRING; never confirmed the 8*floor(len/8) term
     still holds for a CUSTOM string type specifically.
  E. group_extreme_maxlen -- boundary/stress maxlens: 1/2/4 (tiny, below
     anything tested so far) and 4000 (2x the largest previously-confirmed
     working value, customstring_len* topped out at 2000 -- RESOLVED_
     QUESTIONS.md OQ-CUSTOMSTRINGDEF).

Run: python -m sample_gen.gen_string_batch2
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, custom_string_type_xml, string_array_tag_xml, tag_xml, udt_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

TAGS_OUT = Path(__file__).parent.parent.parent / "samples" / "generated" / "tags"
UDT_OUT = Path(__file__).parent.parent.parent / "samples" / "generated" / "udt"


def _write(out_root: Path, l5x: str, out_name: str, description: str, category: str) -> None:
    out_path = out_root / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, category, out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


def group_mod4_bucket1() -> int:
    n = 0
    for maxlen in [49, 101, 501]:
        datatype = custom_string_type_xml(f"CStrB2Mod1_{maxlen}", maxlen)
        for count in [1, 100]:
            tags = "\n".join(
                tag_xml(f"CS{i:04d}", f"CStrB2Mod1_{maxlen}", string_max_len=maxlen) for i in range(count)
            )
            l5x = build_l5x(target_name=f"CStrMod1N{count}L{maxlen}", tags_xml=tags, extra_datatypes_xml=datatype)
            _write(TAGS_OUT, l5x, f"stringoverhead_custom{maxlen}_n{count:05d}",
                   f"{count} instances of a {maxlen}-char custom string type -- maxlen mod 4 = 1 bucket "
                   f"(untested before this batch)",
                   "string_tagoverhead")
            n += 1
    return n


def group_string_array() -> int:
    n = 0
    for count in [5, 50]:
        tag = string_array_tag_xml("StrArr", count, max_len=82)
        l5x = build_l5x(target_name=f"StringArrayN{count}", tags_xml=tag)
        _write(TAGS_OUT, l5x, f"stringarray_builtin_n{count:03d}",
               f"ONE array-of-STRING tag, {count} built-in STRING elements (Dimensions={count}) -- "
               f"never tested before, structurally different XML from N separate scalar STRING tags",
               "string_array")
        n += 1

    datatype = custom_string_type_xml("CStrArrTest", 100)
    for count in [5, 50]:
        tag = string_array_tag_xml("CStrArr", count, max_len=100, data_type="CStrArrTest")
        l5x = build_l5x(target_name=f"CustomStringArrayN{count}", tags_xml=tag, extra_datatypes_xml=datatype)
        _write(TAGS_OUT, l5x, f"stringarray_custom100_n{count:03d}",
               f"ONE array-of-custom-string tag, {count} elements of a 100-char custom string type -- "
               f"never tested before",
               "string_array")
        n += 1
    return n


def group_string_udt_member() -> int:
    n = 0
    builtin_members = [MemberSpec("S0", "STRING")]
    for instances in [1, 10]:
        udt = udt_xml("UdtWithBuiltinString", builtin_members)
        tags = "\n".join(
            tag_xml(f"UBS{i}", "UdtWithBuiltinString", udt_members=builtin_members) for i in range(instances)
        )
        l5x = build_l5x(target_name=f"UdtBuiltinStrN{instances}", tags_xml=tags, extra_datatypes_xml=udt)
        _write(UDT_OUT, l5x, f"udtstring_builtin_n{instances:02d}",
               f"UDT with 1 built-in STRING member, {instances} instance(s) -- STRING-as-UDT-member byte "
               f"cost never captured before (XML shape existed, real size didn't)",
               "udt")
        n += 1

    custom_datatype = custom_string_type_xml("CStrUdtMember100", 100)
    custom_members = [MemberSpec("S0", "CStrUdtMember100")]
    for instances in [1, 10]:
        udt = udt_xml("UdtWithCustomString", custom_members)
        tags = "\n".join(
            tag_xml(f"UCS{i}", "UdtWithCustomString", udt_members=custom_members) for i in range(instances)
        )
        l5x = build_l5x(target_name=f"UdtCustomStrN{instances}", tags_xml=tags,
                         extra_datatypes_xml=custom_datatype + "\n" + udt)
        _write(UDT_OUT, l5x, f"udtstring_custom100_n{instances:02d}",
               f"UDT with 1 custom 100-char string member, {instances} instance(s) -- STRING-as-UDT-member "
               f"byte cost never captured before",
               "udt")
        n += 1
    return n


def group_namelen_custom() -> int:
    n = 0
    maxlen = 100
    datatype = custom_string_type_xml("CStrNameLen100", maxlen)
    count = 50
    for length in [4, 16, 40]:
        tags = []
        for i in range(count):
            suffix = f"_{i:02d}"
            base = f"S{suffix}"
            pad_needed = max(0, length - len(base))
            filler = ("_LONGNAME" * (pad_needed // 9 + 1))[:pad_needed]
            name = f"S{filler}{suffix}"
            tags.append(tag_xml(name, "CStrNameLen100", string_max_len=maxlen))
        l5x = build_l5x(target_name=f"CStrNameLen{length}", tags_xml="\n".join(tags), extra_datatypes_xml=datatype)
        _write(TAGS_OUT, l5x, f"stringoverhead_customnamelen{length:02d}_n{count:03d}",
               f"{count} custom string (maxlen=100) tags, name length {length} chars -- name-length x "
               f"custom-maxlen interaction, never tested (namelen cross-check only ever used built-in STRING)",
               "string_tagoverhead")
        n += 1
    return n


def group_extreme_maxlen() -> int:
    n = 0
    for maxlen in [1, 2, 4, 4000]:
        datatype = custom_string_type_xml(f"CStrExtreme{maxlen}", maxlen)
        tag = tag_xml("CS0000", f"CStrExtreme{maxlen}", string_max_len=maxlen)
        l5x = build_l5x(target_name=f"CStrExtreme{maxlen}", tags_xml=tag, extra_datatypes_xml=datatype)
        _write(TAGS_OUT, l5x, f"stringoverhead_extreme{maxlen:05d}_n00001",
               f"1 instance of a {maxlen}-char custom string type -- boundary/stress maxlen, "
               f"{'below anything tested before' if maxlen <= 4 else '2x the largest previously-confirmed working value (2000)'}",
               "string_tagoverhead")
        n += 1
    return n


def main() -> None:
    total = 0
    for fn in [group_mod4_bucket1, group_string_array, group_string_udt_member,
               group_namelen_custom, group_extreme_maxlen]:
        count = fn()
        print(f"{fn.__name__}: {count} file(s)")
        total += count
    print(f"\nTotal: {total} sample(s) generated.")


if __name__ == "__main__":
    main()
