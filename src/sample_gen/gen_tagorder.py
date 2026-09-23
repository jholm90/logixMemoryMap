"""Does tag DECLARATION ORDER change what a tag multiset costs -- OQ-TAGORDER.

Raised from outside the model: "BOOL LINT INT DINT BOOL takes up different
space in the controller than another order." It has never been tested, and
that was confirmed by search rather than assumed. Every tag family in the
corpus declares tags GROUPED BY TYPE -- `type_bool_50tag` is 50 consecutive
BOOLs, `typesweep_*` draws from one fixed pool, `array_*` and `udtslot_*` the
same. Not one file in over 3,000 captured rows holds a MIXED tag multiset and
varies only the order.

This matters because an order effect is invisible to every test already run.
It changes cost without changing any count, so a per-tag rate, a per-type
rate and a category scale all read identically across the permutations. The
tag survey behind OQ-TAGSHAPE cleared name length, dimensionality, alias
share and tag type, and none of those sweeps could have seen an order effect
either.

The one order result that exists says order is free, at a DIFFERENT SCOPE:
`aoidshape_order_{boolsfirst,dintsfirst,alternating,pairs,blocks5}` permute
the same BOOL/DINT multiset five ways inside an AOI DEFINITION and read -12
on every one of the five -- identical, so definition member order is free.
That is not the same question. An AOI definition is a packed structure whose
layout Logix controls; a controller tag list is a series of independently
allocated slots, and the mechanism that would make order matter -- alignment
padding between adjacent tags of different widths -- only exists in the
second case.

WHY THESE TYPES. BOOL (1 bit), INT (2 bytes), DINT (4) and LINT (8) are the
four widths where alignment padding could bite, and BOOL and DINT together
are 58% of the 31,532 tags in the sixteen real programs. If adjacent-tag
padding exists, the widest-to-narrowest and narrowest-to-widest arrangements
bracket it: one should need the most padding and the other the least.

Six files, the SAME 400 tags in all six -- 100 BOOL, 100 INT, 100 DINT,
100 LINT -- with identical names, so nothing moves but the sequence:

    tgord_grouped      BOOL x100, INT x100, DINT x100, LINT x100
                       the corpus's own shape, and the control
    tgord_widefirst    LINT, DINT, INT, BOOL -- descending width
    tgord_narrowfirst  BOOL, INT, DINT, LINT -- ascending width
    tgord_alternating  BOOL, INT, DINT, LINT, BOOL, INT, ... one of each
    tgord_pairs        two of each type before moving on
    tgord_shuffled     a fixed seeded permutation, the realistic case

If all six capture identically, order is free at tag scope and this question
closes for good. If they split, the split itself says whether it is padding
(the two width-ordered files should be the extremes) or something else.

Run: python -m sample_gen.gen_tagorder
"""

from __future__ import annotations

import random
from pathlib import Path

from sample_gen.builders import tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT = Path(__file__).parent.parent.parent / "samples" / "generated" / "tags"
CATEGORY = "tag_order"

TYPES = ("BOOL", "INT", "DINT", "LINT")
PER_TYPE = 100
SHUFFLE_SEED = 20260918          # fixed, so the file is reproducible byte for byte


def _names() -> dict[str, list[str]]:
    """Identical names in every file, so name length and name count are held
    fixed and only the SEQUENCE moves."""
    return {ty: [f"{ty[:2].title()}Tag{i:03d}" for i in range(PER_TYPE)] for ty in TYPES}


def _sequences() -> dict[str, list[tuple[str, str]]]:
    names = _names()
    flat = {ty: list(names[ty]) for ty in TYPES}

    # The control must not accidentally BE one of the width orders. TYPES is
    # ascending width, so grouping in TYPES order reproduces narrowfirst
    # exactly and wastes a capture slot -- caught by confound_check before
    # this batch was committed. The control groups by type in an order that
    # is deliberately not sorted by width.
    def take(order: tuple[str, ...]) -> list[tuple[str, str]]:
        return [(ty, n) for ty in order for n in flat[ty]]

    def interleave(block: int) -> list[tuple[str, str]]:
        out, idx = [], {ty: 0 for ty in TYPES}
        while any(idx[ty] < PER_TYPE for ty in TYPES):
            for ty in TYPES:
                for _ in range(block):
                    if idx[ty] < PER_TYPE:
                        out.append((ty, flat[ty][idx[ty]]))
                        idx[ty] += 1
        return out

    shuffled = take(("DINT", "BOOL", "LINT", "INT"))
    random.Random(SHUFFLE_SEED).shuffle(shuffled)
    return {
        "grouped": take(("DINT", "BOOL", "LINT", "INT")),
        "widefirst": take(("LINT", "DINT", "INT", "BOOL")),
        "narrowfirst": take(("BOOL", "INT", "DINT", "LINT")),
        "alternating": interleave(1),
        "pairs": interleave(2),
        "shuffled": shuffled,
    }


_WHY = {
    "grouped": "grouped by type, in an order deliberately NOT sorted by width "
               "(DINT, BOOL, LINT, INT) -- the shape every existing tag family in the "
               "corpus uses, and the control the other five difference against; a "
               "width-sorted grouping would have duplicated narrowfirst exactly",
    "widefirst": "strictly descending width, LINT then DINT then INT then BOOL -- one "
                 "bracket of the adjacent-tag padding hypothesis",
    "narrowfirst": "strictly ascending width, BOOL then INT then DINT then LINT -- the "
                   "other bracket; if padding between adjacent tags of different widths "
                   "exists, this and widefirst are the extremes",
    "alternating": "one of each type in rotation, the maximum number of width "
                   "transitions the multiset allows",
    "pairs": "two of each type before moving on -- half the transitions of alternating, "
             "which separates a per-transition cost from a per-tag one",
    "shuffled": "a fixed seeded permutation -- the realistic case, since real programs "
                "declare tags in neither grouped nor rotating order",
}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for key, seq in _sequences().items():
        tags = [tag_xml(name, ty) for ty, name in seq]
        l5x = build_l5x(target_name="TagOrderProbe", tags_xml="\n".join(tags))
        name = f"tgord_{key}"
        out = OUT / f"{name}.L5X"
        append_manifest_row(
            name,
            f"The same 400 controller tags -- {PER_TYPE} each of BOOL, INT, DINT and "
            f"LINT, with identical names in every file -- declared {_WHY[key]}. "
            f"OQ-TAGORDER: whether declaration ORDER changes what a tag multiset costs "
            f"has never been tested, confirmed by search rather than assumed; every tag "
            f"family in over 3,000 captured rows groups by type. An order effect is "
            f"invisible to every test already run, because it changes cost without "
            f"changing any count -- a per-tag rate, a per-type rate and a category scale "
            f"all read identically across these six. The one existing order result says "
            f"order is free INSIDE an AOI definition (the five aoidshape_order files all "
            f"read -12), which is a different scope: a definition is a packed structure "
            f"whose layout Logix controls, while a controller tag list is a series of "
            f"independently allocated slots, and adjacent-tag alignment padding can only "
            f"exist in the second. BOOL, INT, DINT and LINT are the four widths where "
            f"padding could bite, and BOOL and DINT alone are 58% of the 31,532 tags in "
            f"the sixteen real programs.",
            CATEGORY, out, write_sample(l5x, out))
    print("Total: 6")


if __name__ == "__main__":
    main()
