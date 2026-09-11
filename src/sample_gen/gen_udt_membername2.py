"""Is a member NAME charged once per definition, or once per tag?

Written 2026-09-11, the same day as `gen_udt_membername.py`, to close a hole
in that batch found while reviewing it: all 24 `udtmn_*` files carry
`tags_xml=""`. Zero tags, in every arm. So whatever they measure, they
measure it PER DEFINITION, and they are structurally incapable of saying
whether the same term is also charged per tag of that type.

That distinction is the whole of the real-file exposure. Real programs carry
509-2,284 declared UDT members at 8-12 characters each, and tens of thousands
of tags of those types -- AccuTally alone has 33,574 UDT tags against 174 UDT
definitions, 193 tags per definition. A per-definition name term and a
per-tag name term differ by more than two orders of magnitude on that file.

This is the identical failure mode that OQ-DEFSCALE's captured sweeps hit
from the other direction: a sweep that varies one thing per definition cannot
attribute the cost to the definition rather than to its instances unless the
instance count moves independently. Here the instance count never moves at
all.

Everything is built from `gen_udt_membername`'s own `_member_name()` and
`_type_name()`, so the definitions are byte-identical to the 24 pending files
and every arm differences straight against them. Type names stay at exactly 8
characters throughout, so the already-modelled `name_per_8_chars` type-name
bucket is constant and cannot move.

ARM A -- `udtmn2_bool_len{02,16,32}_b04_t{01,05,25}`
    The same 4-BOOL UDT at three member-name lengths, with 1, 5 and 25 tags
    of it. The n=0 point already exists as `udtmn_bool_len{02,16,32}_b04`.
    Reading it two ways:
      - across TAG COUNT at fixed name length -> per-tag cost of a tag of
        this type, which the model already claims to know
      - across NAME LENGTH at fixed tag count -> whether the name term
        multiplies by the tag count or does not
    If the name term is per definition, the length effect is identical at
    t=1, 5 and 25. If it is per tag, it grows 25x across the arm.

ARM B -- `udtmn2_dint_len{02,32}_n04_t{01,25}`
    The same question on DINT members. BOOL is the one member kind with a
    hidden backing SINT, and a BOOL-specific explanation has already been
    wrongly assumed once in this thread (OQ-UDTBOOLMEMBER), so no
    name-length result gets believed on BOOL evidence alone.

ARM C -- `udtmn2_nest_len{02,32}`
    An outer UDT whose 4 members are each an INNER UDT that itself has 4
    members at the swept name length. Do the inner type's member names get
    charged again inside the outer definition that references it? Real
    programs nest UDTs heavily, and if a nested member name is charged once
    per containing type the cost compounds with nesting depth.

ARM D -- `udtmn2_bool_len32_b04_arr{010,100}`
    ONE tag that is an ARRAY of 10 / 100 elements of the long-named type. If
    the name term is per tag, an array is one tag and the term applies once;
    if it is per element it multiplies by the array length. Real programs are
    full of array-of-UDT tags, so these two readings are far apart.

ARM E -- `udtmn2_aoi_{plen,llen}{02,16,32}`
    The same question for an AOI's own PARAMETER and LOCAL TAG names, which
    nothing in the corpus has ever varied. An AOI definition's parameter
    table is the same kind of declared-member list as a UDT's, and the model
    charges nothing for either name. Kept to one axis each (4 members, three
    lengths) because this arm is establishing whether the effect exists at
    all, not tracing its shape.

Run: python -m sample_gen.gen_udt_membername2
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, aoi_xml, rung_xml, tag_xml, udt_xml
from sample_gen.gen_udt_membername import TYPE_NAME_LEN, _member_name, _type_name
from sample_gen.lint import lint_or_raise
from sample_gen.manifest import append_manifest_row, predicted_bytes
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "udt"

MEMBER_COUNT = 4
TAG_COUNTS = (1, 5, 25)
LENGTHS = (2, 16, 32)
ARRAY_LENGTHS = (10, 100)


def _write(l5x: str, name: str, description: str) -> None:
    out = OUT_ROOT / f"{name}.L5X"
    lint_or_raise(l5x, context=str(out))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(l5x, encoding="utf-8")
    append_manifest_row(name, description, "udt", out, predicted_bytes(l5x))


def _members(data_type: str, length: int, count: int = MEMBER_COUNT) -> list[MemberSpec]:
    return [MemberSpec(_member_name(i, length), data_type) for i in range(count)]


def arm_a_b_tag_counts() -> int:
    n = 0
    for data_type, stem, lengths, tag_counts in (
        ("BOOL", "T", LENGTHS, TAG_COUNTS),
        ("DINT", "U", (2, 32), (1, 25)),
    ):
        for length in lengths:
            members = _members(data_type, length)
            type_name = _type_name(f"{stem}{length:02d}")
            types = udt_xml(type_name, members)
            for t in tag_counts:
                tags = "\n".join(tag_xml(f"Tg{i:03d}", type_name, udt_members=members)
                                 for i in range(t))
                kind = "bool" if data_type == "BOOL" else "dint"
                count_key = "b" if data_type == "BOOL" else "n"
                sid = f"udtmn2_{kind}_len{length:02d}_{count_key}{MEMBER_COUNT:02d}_t{t:02d}"
                _write(
                    build_l5x(target_name=f"UdtMn2{stem}{length:02d}T{t:02d}"[:24],
                              tags_xml=tags, extra_datatypes_xml=types),
                    sid,
                    f"{MEMBER_COUNT} {data_type} members with {length}-character names, "
                    f"8-character type name, and {t} tag(s) of the type. The 24 pending udtmn_* "
                    f"files all carry ZERO tags, so they can only ever measure a PER-DEFINITION "
                    f"name term; this arm moves the tag count independently so a per-tag term "
                    f"cannot hide inside it. Differences against udtmn_{kind}_len{length:02d}_"
                    f"{count_key}{MEMBER_COUNT:02d} (the same file at t=0). If the name term is "
                    f"per definition the length effect is identical at every t; if it is per tag "
                    f"it grows with t. On AccuTally (33,574 UDT tags against 174 definitions) "
                    f"those two readings are two orders of magnitude apart.",
                )
                n += 1
    return n


def arm_c_nested() -> int:
    n = 0
    for length in (2, 32):
        inner_name = _type_name(f"I{length:02d}")
        inner_members = _members("DINT", length)
        outer_name = _type_name(f"O{length:02d}")
        outer_members = [MemberSpec(_member_name(i, length), inner_name)
                         for i in range(MEMBER_COUNT)]
        _write(
            build_l5x(
                target_name=f"UdtMn2Nest{length:02d}", tags_xml="",
                extra_datatypes_xml=udt_xml(inner_name, inner_members) + "\n"
                + udt_xml(outer_name, outer_members),
            ),
            f"udtmn2_nest_len{length:02d}",
            f"An inner UDT of {MEMBER_COUNT} DINT members at {length}-character names, and an "
            f"outer UDT whose {MEMBER_COUNT} members are each one of those inner types, also at "
            f"{length}-character names. No tags. Against the len02 twin this says whether a "
            f"nested type's member names are charged again inside every containing definition -- "
            f"if they are, the cost compounds with nesting depth, and real programs nest UDTs "
            f"heavily. OQ-UDTMEMBERNAME.",
        )
        n += 1
    return n


def arm_d_arrays() -> int:
    n = 0
    length = 32
    members = _members("BOOL", length)
    type_name = _type_name(f"A{length:02d}")
    for a in ARRAY_LENGTHS:
        _write(
            build_l5x(
                target_name=f"UdtMn2Arr{a:03d}",
                tags_xml=tag_xml("TgArr", type_name, dimensions=(a,), udt_members=members),
                extra_datatypes_xml=udt_xml(type_name, members),
            ),
            f"udtmn2_bool_len{length:02d}_b{MEMBER_COUNT:02d}_arr{a:03d}",
            f"ONE tag that is an array of {a} elements of a UDT with {MEMBER_COUNT} "
            f"{length}-character member names. A per-TAG name term applies once here; a "
            f"per-ELEMENT term multiplies by {a}. Read against "
            f"udtmn2_bool_len{length:02d}_b{MEMBER_COUNT:02d}_t01, which is the same type with "
            f"one scalar tag. Real programs are full of array-of-UDT tags. OQ-UDTMEMBERNAME.",
        )
        n += 1
    return n


def arm_e_aoi_names() -> int:
    """AOI parameter and local-tag names -- never varied by any generator."""
    n = 0
    for length in LENGTHS:
        params = [MemberSpec(_member_name(i, length), "DINT", required=True)
                  for i in range(MEMBER_COUNT)]
        aoi, storage = aoi_xml(f"AoiP{length:02d}", input_params=params,
                               output_params=[MemberSpec("OutBit", "BOOL", required=True)],
                               logic_rungs_xml=rung_xml(0, "OTE(OutBit);"))
        _write(
            build_l5x(target_name=f"UdtMn2AoiP{length:02d}", tags_xml="", extra_aoi_xml=aoi),
            f"udtmn2_aoi_plen{length:02d}",
            f"One AOI definition with {MEMBER_COUNT} Input parameters whose names are "
            f"{length} characters, no instances. An AOI's parameter table is the same kind of "
            f"declared-member list as a UDT's, and the model charges nothing for either name. "
            f"Nothing in the corpus has ever varied an AOI parameter name length, so this arm "
            f"establishes whether the effect exists there at all. OQ-UDTMEMBERNAME.",
        )
        n += 1

        locals_ = [MemberSpec(_member_name(i, length), "DINT") for i in range(MEMBER_COUNT)]
        aoi_l, _ = aoi_xml(f"AoiL{length:02d}",
                           input_params=[MemberSpec("InA", "DINT", required=True)],
                           output_params=[MemberSpec("OutBit", "BOOL", required=True)],
                           local_tags=locals_,
                           logic_rungs_xml=rung_xml(0, "OTE(OutBit);"))
        _write(
            build_l5x(target_name=f"UdtMn2AoiL{length:02d}", tags_xml="", extra_aoi_xml=aoi_l),
            f"udtmn2_aoi_llen{length:02d}",
            f"One AOI definition with {MEMBER_COUNT} Local Tags whose names are {length} "
            f"characters, no instances. Local tags are the AOI's own storage-only members, the "
            f"closest analogue to a UDT member there is, and the paired plen arm at the same "
            f"length separates a parameter effect from a local-tag one. OQ-UDTMEMBERNAME.",
        )
        n += 1
    return n


def main() -> None:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    assert TYPE_NAME_LEN == 8, "type-name bucket must stay constant across the batch"
    a = arm_a_b_tag_counts()
    c = arm_c_nested()
    d = arm_d_arrays()
    e = arm_e_aoi_names()
    print(f"Arms A+B (tag count x name length): {a}")
    print(f"Arm C (nested UDT member names):    {c}")
    print(f"Arm D (array-of-UDT tags):          {d}")
    print(f"Arm E (AOI param / local names):    {e}")
    print(f"Total: {a + c + d + e}")


if __name__ == "__main__":
    main()
