"""OQ-AOIBOOLPACK-PAIRING closeout (2026-09-12).

The per-instance law is now derived and wired: an array-of-AOI-instances
block is padded up to an 8-byte boundary
(memory_model.yaml aoi_array.block_alignment_bytes). That single constant
replaced the whole "odd-length arrays cost 4 bytes more, except when they
don't" surface -- 48 of 48 captured aoibp_*/aoipack_* sweep families agree
with no exceptions, and 49 of 52 families are now FLAT in instance count.
What used to look like a two-variable (bool_count, atomic_count) surface was
per-instance-size mod 8 all along; BOOL/atomic composition only moved the
per-instance size.

Three things the existing corpus cannot settle, one group each. Nothing here
is padded: 46 files, every one of them differencing against a control that
already exists in the manifest.

  A. group_dword_boundary -- is the extra +4 bytes/INSTANCE a general
     32-bit-boundary effect or specific to bool_count 31/32?

     Those two families are 2 of the 3 that still vary with instance count:
     bc31 goes -40/-48/-64 and bc32 -46/-54/-70 at n=2/4/8, both a clean
     -4 per instance on top of their own flat offset, while bc16, bc24, bc33,
     bc40 and bc48 are all dead flat. So the engine under-charges 4 bytes
     per instance for a packed BOOL word at exactly 31-32 members and nowhere
     else measured.

     One reading is a real DINT-alignment rule that must recur at every
     32-member boundary (63/64, 95/96); the other is that the FIRST packed
     word is special and there is nothing to generalize. The existing corpus
     cannot tell them apart -- it has no data above bool_count=60 at more
     than one instance count. This sweeps bool_count 30..33, 62..65 and
     94..97 at n=2/4/8, which brackets three consecutive boundaries with the
     same shape (all-Input, single section) as the already-captured bc*_iso2
     data so the new points difference directly against it.

     Picking n=2/4/8 rather than consecutive counts is deliberate: the slope
     is what matters and doubling makes a 4-bytes/instance term unmistakable
     (+8 then +16) while a flat offset stays put.

  B. group_unaligned_per_instance -- per-instance sizes that are NOT
     congruent to 0 or 4 mod 8.

     Every family in the corpus lands on 0 or 4 mod 8 except one,
     aoipack_nonatomic_sint_20b10a (per-instance 14, so 6 mod 8), and that
     family is the third and last one still varying with instance count
     (+108 at n=1, +60 at n=25). With one family at one residue there is no
     way to tell whether the 8-byte block padding holds for arbitrary
     per-instance sizes or whether a non-4-aligned instance size triggers
     something else entirely -- and a real AOI with SINT or INT parameters
     lands there routinely, so this is not a corner case.

     SINT and INT parameter counts are chosen to put per-instance size at
     each of 1,2,3,5,6,7 mod 8, each at n=2 and n=3. If block padding is
     general, predicted-minus-actual is flat across the pair for every
     residue once the alignment term is applied.

  C. group_def_controls -- attribute the leftover flat offset.

     After the alignment wiring the residual is entirely a per-family
     constant, ranging -38 to +180, and the five families that HAVE a
     def_only control (a file with the same AOI definition and no instance
     tag at all) say where it lives: atomic -4/-8, bool -4/-8, mixed
     +59/+55, mix25_75 +19/+15, mix75_25 +42/+38 (def residual / array
     residual). All five sit exactly 4 bytes further under with the array
     tag present, which puts the rest of the offset on the DEFINITION, not
     the array.

     A flat +4 array-tag term was fitted and deliberately NOT wired: it
     moved 17 rows into the +-8 band but reduced total absolute residual
     over the 178 rows by only 40 bytes (5818 -> 5778) and cost 3 exact
     predictions, aoipack_mc20_b02_array_n01/n10/n25, which sat at exactly
     0. 5 controlled pairs for it and 1 uncontrolled family against it is
     not enough to ship a constant on.

     The mc*/ratio*/bc* families never got a def_only control, so their
     offsets cannot be split between definition and array at all. This adds
     the missing control for the eight families whose offsets are largest
     and therefore carry the most information.

Run: python -m sample_gen.gen_aoi_array_align_closeout
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, aoi_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

AOI_OUT = Path(__file__).parent.parent.parent / "samples" / "generated" / "aoi"


def _write(l5x: str, out_name: str, description: str) -> int:
    out_path = AOI_OUT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "aoi_array_packing", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")
    return 1


# ---------------------------------------------------------------------------
# A. Does the DWORD-boundary +4/instance recur at 63/64 and 95/96?
# ---------------------------------------------------------------------------

DWORD_BOOL_COUNTS = (30, 31, 32, 33, 62, 63, 64, 65, 94, 95, 96, 97)
DWORD_COUNTS = (2, 4, 8)


def group_dword_boundary() -> int:
    n = 0
    for bool_count in DWORD_BOOL_COUNTS:
        aoi_name = f"AoiAlgnBc{bool_count}"
        inputs = [MemberSpec(f"InB{i}", "BOOL") for i in range(bool_count)]
        definition, storage = aoi_xml(aoi_name, inputs, [], [], [])
        for count in DWORD_COUNTS:
            tag = tag_xml("TestInstanceArray", aoi_name, dimensions=(count,),
                          udt_members=storage)
            l5x = build_l5x(target_name=aoi_name, tags_xml=tag, extra_aoi_xml=definition)
            n += _write(
                l5x, f"aoialgn_bc{bool_count:02d}_n{count:02d}",
                f"AOI, {bool_count} BOOL Input params (single section, all-Input), array of "
                f"{count} instances -- OQ-AOIBOOLPACK-PAIRING DWORD-boundary closeout. bc31/bc32 "
                f"are the only captured families carrying a real +4 bytes/instance on top of "
                f"their flat offset; bc16/24/33/40/48 are flat. Same shape as the captured "
                f"bc*_iso2 sweep so these difference straight against it. n=2/4/8 so a "
                f"per-instance term shows as +8 then +16 while a flat offset stays put. Brackets "
                f"three consecutive 32-member boundaries (30-33, 62-65, 94-97) to separate a "
                f"general DINT-alignment rule from a first-packed-word special case")
    return n


# ---------------------------------------------------------------------------
# B. Per-instance sizes off the 4-byte grid (SINT/INT parameters)
# ---------------------------------------------------------------------------

# (label, SINT param count, INT param count) -- chosen so the per-instance
# size lands on a different residue mod 8 in each row. The residue is not
# asserted here: the engine's own per-instance size is what it is, and the
# reconciliation reads it back by differencing the two instance counts. What
# matters is that these six shapes cannot all share one residue.
UNALIGNED_SHAPES = (
    ("s01", 1, 0),
    ("s02", 2, 0),
    ("s03", 3, 0),
    ("s05", 5, 0),
    ("s01i01", 1, 1),
    ("s03i01", 3, 1),
    ("s01i03", 1, 3),
    ("i01", 0, 1),
    ("i03", 0, 3),
)
UNALIGNED_COUNTS = (2, 3)


def group_unaligned_per_instance() -> int:
    n = 0
    for label, sints, ints in UNALIGNED_SHAPES:
        aoi_name = f"AoiAlgnUn{label.upper()}"
        inputs = ([MemberSpec(f"InS{i}", "SINT") for i in range(sints)]
                  + [MemberSpec(f"InI{i}", "INT") for i in range(ints)])
        definition, storage = aoi_xml(aoi_name, inputs, [], [], [])
        l5x = build_l5x(target_name=aoi_name, tags_xml="", extra_aoi_xml=definition)
        n += _write(
            l5x, f"aoialgn_un_{label}_def_only",
            f"AOI, {sints} SINT + {ints} INT Input params, 0 instances -- "
            f"OQ-AOIBOOLPACK-PAIRING unaligned-per-instance control, isolates this "
            f"definition's own cost from the array term")
        for count in UNALIGNED_COUNTS:
            tag = tag_xml("TestInstanceArray", aoi_name, dimensions=(count,),
                          udt_members=storage)
            l5x = build_l5x(target_name=aoi_name, tags_xml=tag, extra_aoi_xml=definition)
            n += _write(
                l5x, f"aoialgn_un_{label}_n{count:02d}",
                f"AOI, {sints} SINT + {ints} INT Input params, array of {count} instances -- "
                f"OQ-AOIBOOLPACK-PAIRING unaligned-per-instance sweep. Every captured family "
                f"has a per-instance size congruent to 0 or 4 mod 8 except "
                f"aoipack_nonatomic_sint_20b10a (14 bytes, 6 mod 8), which is also one of only "
                f"three families still varying with instance count. SINT/INT params put the "
                f"per-instance size off the 4-byte grid so the 8-byte block padding is tested "
                f"at the other residues; n=2 and n=3 because the padding term differs between "
                f"them for any residue that is not 0")
    return n


# ---------------------------------------------------------------------------
# C. def_only controls for the families whose flat offset is unattributed
# ---------------------------------------------------------------------------

# Rebuilds of already-captured array families' DEFINITIONS only, matching the
# original member shapes exactly. (label, inputs, outputs, locals) -- the
# section split matters, so it is reproduced rather than flattened.
def _bools(prefix: str, count: int) -> list[MemberSpec]:
    return [MemberSpec(f"{prefix}{i}", "BOOL") for i in range(count)]


def _dints(prefix: str, count: int) -> list[MemberSpec]:
    return [MemberSpec(f"{prefix}{i}", "DINT") for i in range(count)]


DEF_CONTROLS = (
    # mc<total>_b<bools>: single-section all-Input, <total> members of which
    # <bools> are BOOL and the rest DINT. Residuals -14..+180.
    ("mc10_b00", _bools("InB", 0) + _dints("InA", 10), [], []),
    ("mc10_b05", _bools("InB", 5) + _dints("InA", 5), [], []),
    ("mc10_b10", _bools("InB", 10), [], []),
    ("mc20_b02", _bools("InB", 2) + _dints("InA", 18), [], []),
    ("mc20_b18", _bools("InB", 18) + _dints("InA", 2), [], []),
    ("mc60_b30", _bools("InB", 30) + _dints("InA", 30), [], []),
    ("mc60_b54", _bools("InB", 54) + _dints("InA", 6), [], []),
    ("mc60_b60", _bools("InB", 60), [], []),
)


def group_def_controls() -> int:
    n = 0
    for label, inputs, outputs, locals_ in DEF_CONTROLS:
        aoi_name = f"AoiAlgnDef{label.replace('_', '').upper()}"
        definition, _storage = aoi_xml(aoi_name, inputs, outputs, [], locals_)
        l5x = build_l5x(target_name=aoi_name, tags_xml="", extra_aoi_xml=definition)
        bools = sum(1 for m in inputs + outputs + locals_ if m.data_type == "BOOL")
        n += _write(
            l5x, f"aoialgn_def_{label}",
            f"AOI definition only ({len(inputs)} Input params, {bools} of them BOOL), 0 "
            f"instances -- OQ-AOIBOOLPACK-PAIRING definition-offset control for the captured "
            f"aoipack_{label}_array_n* family. After the 8-byte block-alignment wiring every "
            f"remaining residual is a per-family CONSTANT (-38 to +180) and the five families "
            f"that already have a def_only control put that constant on the definition, not the "
            f"array: each array file sits exactly 4 bytes further under than its own "
            f"definition-only twin. The mc*/ratio* families never got such a control, so their "
            f"offsets cannot be split between definition cost and array cost at all. This is "
            f"that missing control, same member shape as the captured array family")
    return n


def main() -> None:
    total = 0
    for fn in (group_dword_boundary, group_unaligned_per_instance, group_def_controls):
        count = fn()
        print(f"{fn.__name__}: {count} file(s)")
        total += count
    print(f"\nDone. {total} files.")


if __name__ == "__main__":
    main()
