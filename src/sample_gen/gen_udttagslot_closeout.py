"""Is a standalone UDT tag's data slot padded to 8 bytes? -- OQ-UDTTAGSLOT.

Written (capture-batch segment 5). Two captured families disagreed
about what one UDT-typed tag costs, and they disagreed only because they sit on
opposite sides of an 8-byte boundary:

    dscale2_udt_u001_t001..t500   9-byte UDT, 1 to 500 tags    EXACT (14/18 rows 0)
    addit_dm_ln / addit_dh_ln    40-byte UDT, 40 and 400 tags  -7.000/tag, exact slope

One hypothesis fits both with zero residual: a standalone (non-array) UDT tag's
DATA slot is padded up to 8 bytes -- 40 stays 40, 9 becomes 16 -- and
definition_scale_correction.udt_tag_extra is -4 rather than the +3 that held for
as long as only the 9-byte family existed. Both are now wired
(memory_model.yaml standalone_udt_tag_slot); corpus mean absolute error went
1.853% -> 1.841% and the `udt` category picked up 7 more rows inside the band.

WHY IT IS STILL OPEN. The padding constant and the -4 are not separable from
either family alone, and the corpus contains exactly TWO UDT sizes that bear on
it: 9 and 40. Two points, one on each side, with a 2-parameter hypothesis fitted
to them. That is the shape of fit this project has had to undo four times in the
AOI-definition cost alone. It needs every residue, at a slope rather than a
single count.

A second, separate reading is recorded here rather than fitted: padding the UDT
ELEMENT size instead of the tag slot improves the sixteen real programs more
(2.13% -> 1.88%) but costs the `tags` category its accuracy outright (0.27% ->
2.03% mean absolute error) and is flatly contradicted by
dscale2_udt_arr002/arr010/arr100/arr500, which read +1 at every length against a
12-byte 4-aligned element. So the real-file gain is absorbing some OTHER missing
term and must not be spent on element padding -- see OQ-REALUNDER.

GROUP A -- `udtslot_s{01..16}_t{050,400}`, 32 files. A UDT of k SINT members for
    k = 1..16, which packs to exactly k bytes (confirmed against the engine's own
    compute_udt_size at every k), instantiated at 50 and at 400 tags. Every
    residue mod 8 appears twice, on both sides of the boundary, and the two tag
    counts give the per-tag cost as a SLOPE -- 350 tags apart -- rather than as a
    single count that a one-time term could masquerade as. If the slot is padded
    to 8 the per-tag cost is flat across k = 1..8 and flat again across k = 9..16,
    stepping once; if it is not, it rises by 1 at every k.

GROUP B -- `udtslot_d{01,02,03,04,05,06,08,10}_t{050,400}`, 16 files. The same
    two counts over DINT-member UDTs of 4, 8, 12, 16, 20, 24, 32 and 40 bytes.
    All are already 4-aligned and half are already 8-aligned, so this arm says
    whether the step is really at 8 and not at 4 -- and 40 reproduces the
    additivity D axis exactly, which is the cross-check that the slope measured
    there was not an artifact of the grid.

GROUP C -- `udtslot_arr_s{03,05}_n{050,400}`, 4 files. Arrays of the 3-byte and
    5-byte UDTs at 50 and 400 elements. If the padding were on the element rather
    than the tag slot these would move by 5 and 3 bytes per element respectively;
    the wired rule says they do not move at all beyond the element's own packed
    size. dscale2_udt_arr* only ever tested one UDT size, so this is the first
    array arm that can see an element-padding rule at two different residues.

52 files. Every UDT here is plain DINT or SINT members with 8-character tag names
so the tag_overhead bucket is identical across the batch, and nothing else varies.

Run: python -m sample_gen.gen_udttagslot_closeout
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, tag_xml, udt_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT = Path(__file__).parent.parent.parent / "samples" / "generated" / "udt"
CATEGORY = "udt_tag_slot"

SINT_SIZES = tuple(range(1, 17))
DINT_MEMBERS = (1, 2, 3, 4, 5, 6, 8, 10)
TAG_COUNTS = (50, 400)
ARRAY_COUNTS = (50, 400)


def _write(name: str, l5x: str, description: str) -> None:
    out = OUT / f"{name}.L5X"
    append_manifest_row(name, description, CATEGORY, out, write_sample(l5x, out))


def _build(udt_name: str, members: list[MemberSpec], count: int,
           dimensions: tuple[int, ...] | None = None) -> str:
    # Eight-character tag names throughout, so tag_overhead's floor(len/8)
    # bucket is identical in every file of the batch.
    if dimensions:
        tags = [tag_xml("SlotArr0", udt_name, dimensions=dimensions, udt_members=members)]
    else:
        tags = [tag_xml(f"Slt{i:05d}", udt_name, udt_members=members) for i in range(count)]
    return build_l5x(
        target_name="UdtSlotProbe",
        tags_xml="\n".join(tags),
        extra_datatypes_xml=udt_xml(udt_name, members),
    )


def _group_a() -> int:
    for k in SINT_SIZES:
        members = [MemberSpec(f"M{i:02d}", "SINT") for i in range(k)]
        for count in TAG_COUNTS:
            _write(
                f"udtslot_s{k:02d}_t{count:03d}",
                _build(f"UdtS{k:02d}", members, count),
                f"{count} tags of a UDT with {k} SINT members, which packs to exactly "
                f"{k} bytes. Group A of the UDT-tag-slot closeout: the wired rule pads a "
                f"standalone UDT tag's data slot to 8, so the per-tag cost should be flat "
                f"across k=1..8 and flat again across k=9..16 with one step between, "
                f"while an unpadded slot rises by 1 at every k. Derived from only two UDT "
                f"sizes in the whole corpus -- a 9-byte UDT that measures exactly right "
                f"over 500 tags (dscale2_udt_u001_t*) and a 40-byte one that measures "
                f"-7.000/tag over 360 (addit_dm_ln/addit_dh_ln) -- with a 2-parameter "
                f"hypothesis fitted to them. The two tag counts 50 and 400 give the "
                f"per-tag cost as a slope 350 tags apart rather than a single count a "
                f"one-time term could masquerade as. Eight-character tag names so the "
                f"tag_overhead bucket never moves. OQ-UDTTAGSLOT.",
            )
    return len(SINT_SIZES) * len(TAG_COUNTS)


def _group_b() -> int:
    for k in DINT_MEMBERS:
        members = [MemberSpec(f"M{i:02d}", "DINT") for i in range(k)]
        for count in TAG_COUNTS:
            _write(
                f"udtslot_d{k:02d}_t{count:03d}",
                _build(f"UdtD{k:02d}", members, count),
                f"{count} tags of a UDT with {k} DINT members, {4 * k} bytes packed. "
                f"Group B of the UDT-tag-slot closeout: all eight sizes are already "
                f"4-aligned and half are already 8-aligned, so this arm says whether the "
                f"step is really at 8 and not at 4. The 40-byte point (10 DINT) "
                f"reproduces the additivity grid's D axis exactly, which is the "
                f"cross-check that the -7.000/tag slope measured there was not an "
                f"artifact of that grid. OQ-UDTTAGSLOT.",
            )
    return len(DINT_MEMBERS) * len(TAG_COUNTS)


def _group_c() -> int:
    for k in (3, 5):
        members = [MemberSpec(f"M{i:02d}", "SINT") for i in range(k)]
        for count in ARRAY_COUNTS:
            _write(
                f"udtslot_arr_s{k:02d}_n{count:03d}",
                _build(f"UdtAS{k:02d}", members, 1, dimensions=(count,)),
                f"ONE tag that is an array of {count} elements of a {k}-byte "
                f"({k} SINT member) UDT. Group C of the UDT-tag-slot closeout: if the "
                f"8-byte padding were on the ELEMENT rather than on the tag slot this "
                f"file would carry {8 - k} extra bytes per element, {count * (8 - k)} in "
                f"total; the wired rule says it carries none. That reading matters "
                f"because padding elements improves the sixteen real programs more than "
                f"padding the slot does (2.13% -> 1.88% mean absolute error) while "
                f"destroying the `tags` category (0.27% -> 2.03%) -- so the real-file "
                f"gain is absorbing some other missing term, see OQ-REALUNDER. "
                f"dscale2_udt_arr* only ever tested one UDT size; two residues here are "
                f"the first array arm that can see an element rule. OQ-UDTTAGSLOT.",
            )
    return 2 * len(ARRAY_COUNTS)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    total = _group_a() + _group_b() + _group_c()
    print(f"Total: {total}")


if __name__ == "__main__":
    main()
