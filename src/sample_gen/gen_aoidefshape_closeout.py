"""Breaks the last confound in the itemised AOI-definition formula.

Written (capture-batch segment 4) after the `aoimix_*` grid and 124
captured def-only files replaced four fitted AOI-definition terms with one
itemised form (memory_model.yaml aoi_definition):

    base + 12/member + the member's own data bytes + 24 per packed BOOL word
         + the members' names pooled and 8-aligned + name_length(type name)

70 of the 124 instrument files land EXACTLY on it and 122 of 124 within the
project's +-8 band. What is left is a single 8-byte term: exactly 0 on 70 files
and exactly +8 on 35 more. It is not usage, not member count, not composition
and not type. THREE candidate explanations remain, and every captured file
confounds at least two of them:

  1. The AOI TYPE NAME bucket boundary. The wired law is
     8*max(0,(len-8)//4) - 8, fitted 7/7 on lengths 8, 9, 13, 16, 20, 25, 30 --
     which leaves 10-12, 14-15 and 17-19 unsampled. Two pairs that differ only
     in name length across those gaps disagree by exactly 8:
       paramcount_n04_def_only (13 chars) vs _v2 (15) -- byte-identical
         otherwise, and the ONLY difference in the whole file
       aoidefcost_typeint_n08_def_only (16) vs paramtype_dint_n8_def_only (14)
         -- same 8 DINT params, same member names, 8 bytes apart
  2. The member-name POOL carrying a fixed offset before it rounds. On the
     localcount family the +8 appears exactly when the character total is
     congruent to 0, 6 or 7 mod 8 and not when it is 3 or 4, which is what an
     8*ceil((chars + 4)/8) pool would do. That fits all six localcount points
     and then contradicts aoidefcost_typeint_n08.
  3. Member ORDER. aoi_boolpack_clean_alternating_def_only (0) and
     aoi_boolpack_clean_grouped_def_only (+8) are the same 10 BOOL + 10 DINT
     with the same member names in a different order.

Fitting any one of them on the existing corpus would be fitting a
three-variable confound, which is how this cost got four separate terms in the
first place. Every file below is def-only -- an AOI definition with no instance
tag anywhere and no internal rungs -- so the definition is the only AOI cost in
the file and its true value reads straight off the capture.

GROUP A -- `aoidshape_tname_len{08..32}`, 25 files. The AOI type name at every
    single length from 8 to 32 characters, with 4 DINT Input parameters named
    P0..P3 held byte-for-byte identical. The CONTROLLER name is pinned to one
    fixed string across all 25, which the existing `aoiname_len*` sweep did not
    do: there the project name tracked the AOI name, so a project-name cost
    would have been invisible. This reads the bucket boundary directly at every
    length instead of at 7 of them.

GROUP B -- `aoidshape_pool_c{06..21}`, 16 files. Two complete cycles of the
    8-byte pool residue: 4 DINT Input parameters whose names grow one character
    at a time from a 6-character total to 21, with the AOI type name pinned at
    12 characters. Member count, types and data bytes are constant, so the only
    thing moving is the pool's input, and both cycles read the same residue
    twice. If candidate 2 is the answer the steps land at a different residue
    than the wired pool predicts, at every one of the 16 points.

GROUP C -- `aoidshape_count_n{01..08}`, 8 files. Member count 1 to 8 with
    single-character member names, so the character total is 2*n and stays
    inside one 8-byte chunk for n=1..4 and the next for n=5..8. The
    localcount_n01 (0) vs localcount_n02 (+8) step happens here with the pool
    held constant, which separates candidate 2 from a genuine per-member step.

GROUP D -- `aoidshape_order_*`, 5 files. 10 BOOL + 10 DINT in five
    arrangements -- bools first, dints first, strictly alternating, in pairs,
    in blocks of five -- with identical member names and one pinned type name.
    Composition, count, pool and word count are all identical by construction,
    so any spread here is candidate 3 and nothing else.

54 files. Every one differences straight against the existing def-only corpus:
same builders, same wrapper, same 1756-L81E at v35.

Run: python -m sample_gen.gen_aoidefshape_closeout
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, aoi_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT = Path(__file__).parent.parent.parent / "samples" / "generated" / "aoi"

# One fixed controller/target name for every file in the batch. The existing
# aoiname_len* sweep let the project name track the AOI name, so the two could
# never be told apart; pinning it here is the whole point of group A.
TARGET = "AoiDefShapeProbe"

CATEGORY = "aoi_def_shape"


def _write(name: str, l5x: str, description: str) -> None:
    out = OUT / f"{name}.L5X"
    predicted = write_sample(l5x, out)
    append_manifest_row(name, description, CATEGORY, out, predicted)


def _def_only(aoi_name: str, members: list[MemberSpec]) -> str:
    """An AOI definition with no instance tag and no internal logic."""
    definition, _storage = aoi_xml(aoi_name, members, [], [], [])
    return build_l5x(target_name=TARGET, tags_xml="", extra_aoi_xml=definition)


def _group_a() -> int:
    """AOI type name length, every length 8..32, everything else pinned."""
    members = [MemberSpec(f"P{i}", "DINT") for i in range(4)]
    written = 0
    for length in range(8, 33):
        # "AoiTn" + digits + filler, so the name is unique and exactly `length`.
        stem = f"AoiTn{length:02d}"
        aoi_name = stem + "X" * (length - len(stem))
        assert len(aoi_name) == length, aoi_name
        _write(
            f"aoidshape_tname_len{length:02d}",
            _def_only(aoi_name, members),
            f"Def-only AOI, 4 DINT Input parameters named P0..P3, type name exactly "
            f"{length} characters. Group A of the AOI-definition shape closeout: the "
            f"wired type-name law 8*max(0,(len-8))//4 - 8 was fitted 7/7 on lengths 8, "
            f"9, 13, 16, 20, 25 and 30, leaving 10-12, 14-15 and 17-19 unsampled, and "
            f"two pairs differing only across those gaps (paramcount_n04_def_only at 13 "
            f"vs _v2 at 15; aoidefcost_typeint_n08_def_only at 16 vs "
            f"paramtype_dint_n8_def_only at 14) disagree by exactly the 8 bytes one "
            f"bucket is worth. Controller name pinned to {TARGET} across all 25 files, "
            f"which the aoiname_len* sweep did not do -- there the project name tracked "
            f"the AOI name, so a project-name cost was invisible. OQ-AOIDEFSHAPE.",
        )
        written += 1
    return written


def _group_b() -> int:
    """Member-name character total, one character at a time, two full cycles
    of the 8-byte pool residue."""
    written = 0
    for total_chars in range(6, 22):
        # Four members. The first absorbs the remainder, the rest are 1 char,
        # so `total_chars` is exactly the sum of the four name lengths.
        first = total_chars - 3
        names = ["M" * first, "A", "B", "C"]
        members = [MemberSpec(n, "DINT") for n in names]
        assert sum(len(n) for n in names) == total_chars
        _write(
            f"aoidshape_pool_c{total_chars:02d}",
            _def_only("AoiPoolProbe", members),
            f"Def-only AOI, 4 DINT Input parameters whose names total exactly "
            f"{total_chars} characters, type name pinned at 12. Group B of the "
            f"AOI-definition shape closeout: member count, types and data bytes are "
            f"constant across all 16 files, so the only thing moving is the input to "
            f"the 8-aligned member-name pool, and 6..21 covers two complete residue "
            f"cycles so every residue is read twice. On the localcount family the "
            f"unexplained +8 appears exactly when the character total is congruent to "
            f"0, 6 or 7 mod 8 and not when it is 3 or 4 -- what an "
            f"8*ceil((chars + 4)/8) pool would do -- which fits all six localcount "
            f"points and then contradicts aoidefcost_typeint_n08_def_only. "
            f"OQ-AOIDEFSHAPE.",
        )
        written += 1
    return written


def _group_c() -> int:
    """Member count with the name pool held inside one chunk."""
    alphabet = "ABCDEFGH"
    written = 0
    for n in range(1, 9):
        members = [MemberSpec(alphabet[i], "DINT") for i in range(n)]
        _write(
            f"aoidshape_count_n{n:02d}",
            _def_only("AoiCntProbe", members),
            f"Def-only AOI, {n} DINT Input parameters with single-character names, type "
            f"name pinned at 12. Group C of the AOI-definition shape closeout: the "
            f"character total is 2*n with the one pool byte per name, so it stays "
            f"inside one 8-byte chunk for n=1..4 and the next for n=5..8. "
            f"localcount_n01_def_only reads 0 against the itemised formula and "
            f"localcount_n02_def_only reads +8, which is either a genuine per-member "
            f"step or the pool offset; holding the pool constant across n separates "
            f"the two. OQ-AOIDEFSHAPE.",
        )
        written += 1
    return written


def _group_d() -> int:
    """Member ORDER at identical composition, count, names and word count."""
    bools = [f"B{i:02d}" for i in range(10)]
    dints = [f"D{i:02d}" for i in range(10)]
    arrangements = {
        "boolsfirst": [(n, "BOOL") for n in bools] + [(n, "DINT") for n in dints],
        "dintsfirst": [(n, "DINT") for n in dints] + [(n, "BOOL") for n in bools],
        "alternating": [x for pair in zip(
            [(n, "BOOL") for n in bools], [(n, "DINT") for n in dints]) for x in pair],
        "pairs": [x for i in range(0, 10, 2) for x in (
            (bools[i], "BOOL"), (bools[i + 1], "BOOL"),
            (dints[i], "DINT"), (dints[i + 1], "DINT"))],
        "blocks5": [x for i in (0, 5) for x in (
            [(n, "BOOL") for n in bools[i:i + 5]]
            + [(n, "DINT") for n in dints[i:i + 5]])],
    }
    written = 0
    for label, spec in arrangements.items():
        # blocks5 nests one level deeper than the others; flatten uniformly.
        flat: list[tuple[str, str]] = []
        for item in spec:
            if isinstance(item, list):
                flat.extend(item)
            else:
                flat.append(item)
        assert len(flat) == 20, (label, len(flat))
        assert sum(1 for _, t in flat if t == "BOOL") == 10, label
        members = [MemberSpec(n, t) for n, t in flat]
        _write(
            f"aoidshape_order_{label}",
            _def_only("AoiOrdProbe", members),
            f"Def-only AOI, 10 BOOL + 10 DINT Input parameters arranged {label}, type "
            f"name pinned at 12. Group D of the AOI-definition shape closeout: "
            f"composition, member count, member names, name-pool total and packed-word "
            f"count are identical by construction across all five files, so any spread "
            f"is member ORDER and nothing else. "
            f"aoi_boolpack_clean_alternating_def_only reads 0 against the itemised "
            f"formula and aoi_boolpack_clean_grouped_def_only reads +8 on the same 10 "
            f"BOOL + 10 DINT with the same names, which is the whole reason this group "
            f"exists. OQ-AOIDEFSHAPE.",
        )
        written += 1
    return written


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    total = _group_a() + _group_b() + _group_c() + _group_d()
    print(f"Total: {total}")


if __name__ == "__main__":
    main()
