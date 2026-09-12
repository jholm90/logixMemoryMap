"""The BOOL/atomic mix at fixed member total, swept densely.

Written 2026-09-12 from a full reconciliation of the 178 captured
`aoibp_*`/`aoipack_*` rows, then REWRITTEN the same day when the reconciliation
that motivated it turned out to have a simpler answer than the one this batch
was built to chase. Both readings are kept below, because the wrong one is the
instructive part.

WHAT THIS WAS BUILT FOR, AND WHY THAT PREMISE IS DEAD. The captured rows split
into families where an odd-length instance array cost 4 bytes more than an even
one and families where it cost nothing extra, and the split tracked BOOL/atomic
composition closely enough to look causal: `mc10` gave -4 at b00, 0 at b01/b05/
b09, -4 at b10 -- both PURE shapes carrying the term and the mixed ones not.
That reading died on `mc20`, which carries it at b00, b02, b10, b18 AND b20. The
conclusion drawn at that point was "a two-variable surface in (bool_count,
atomic_count), sampled far too sparsely", and this grid is what that conclusion
asked for.

It is not a two-variable surface. It is one constant. The whole instance-array
block is padded up to an 8-byte boundary, so the extra 4 bytes appear exactly
when the per-instance size is congruent to 4 mod 8 and never otherwise -- 48 of
48 captured families agree with zero exceptions, across per-instance sizes of
4, 8, 12, 20, 24, 32, 40, 44, 48, 64, 76, 84, 104, 120, 124, 220 and 244 bytes.
Composition was never the variable; it only moved the per-instance size. Wired
as memory_model.yaml aoi_array.block_alignment_bytes, and 49 of the 52 captured
families are now flat in instance count.

WHAT THE GRID IS FOR NOW. It is still worth generating, for two reasons that do
not depend on the dead premise:

  1. It is the densest available test of the alignment rule. Every point is
     built at an even AND an odd array length, so each of the 17 mixes reads the
     padding term directly instead of inheriting it from a neighbour. A rule
     fitted on 48 families that happen to be in the corpus should be confirmed
     on a grid designed to vary only the thing it depends on.

  2. Holding the member TOTAL constant while sweeping the BOOL fraction is
     exactly the axis the leftover residual now lives on. After the alignment
     wiring the remaining error is a per-family CONSTANT ranging -38 to +180,
     and the five families with a def_only control put that constant on the AOI
     DEFINITION rather than the array. bool_count is what the definition-cost
     model handles worst (mixed-type AOI defs fall back to a flat 20/item rate
     precisely because per-type rates do not compose once BOOL is present -- see
     memory_model.yaml aoi_definition), so a fixed-total BOOL-fraction sweep is
     the right instrument for that too.

THE GRID. Member TOTAL is held constant while the BOOL fraction is swept, which
is exactly the axis the recorded finding says "does not extrapolate cleanly
across bool_count". Each point is built at an even AND an odd array length so
the parity term is read at every mix rather than inferred from neighbours.

    aoimix_t32_b{00,02,04,08,12,16,20,24,28,30,32}_n{02,03}   22 files
    aoimix_t08_b{00,04,08}_n{02,03}                            6 files
    aoimix_t64_b{00,32,64}_n{02,03}                            6 files

34 files. t32 is the dense sweep -- eleven mixes at one total, which no existing
family provides -- and t08/t64 are the two flanking totals that say whether the
switch depends on the mix RATIO or on the absolute BOOL count. t64 also puts two
points past the 2-packed-word boundary that `bool_boundary` already showed is
parity-neutral, so if the surface is really about packed words this grid sees it.

Every file is one AOI with `total` Input parameters of which `bools` are BOOL and
the rest DINT, and one array tag of instances -- the same shape as
`aoibp_dense_*` and `aoipack_mc*`, so every point differences straight against
them.

Run: python -m sample_gen.gen_aoi_boolmix_grid
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, aoi_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT = Path(__file__).parent.parent.parent / "samples" / "generated" / "aoi"

# One even and one odd array length at every grid point: the parity term is the
# thing being switched on and off, so it is measured at each mix rather than
# carried over from a neighbouring one.
ARRAY_LENGTHS = (2, 3)

GRID = {
    32: (0, 2, 4, 8, 12, 16, 20, 24, 28, 30, 32),   # the dense sweep
    8: (0, 4, 8),                                   # flanking total, low
    64: (0, 32, 64),                                # flanking total, high
}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    written = 0
    for total, bool_counts in GRID.items():
        for bools in bool_counts:
            atomics = total - bools
            aoi_name = f"AoiMixT{total:02d}B{bools:02d}"
            inputs = (
                [MemberSpec(f"InB{i}", "BOOL") for i in range(bools)]
                + [MemberSpec(f"InD{i}", "DINT") for i in range(atomics)]
            )
            definition, storage = aoi_xml(aoi_name, inputs, [], [], [])
            for length in ARRAY_LENGTHS:
                tag = tag_xml("TestInstanceArray", aoi_name, dimensions=(length,),
                              udt_members=storage)
                l5x = build_l5x(target_name=aoi_name, tags_xml=tag, extra_aoi_xml=definition)
                name = f"aoimix_t{total:02d}_b{bools:02d}_n{length:02d}"
                out = OUT / f"{name}.L5X"
                bytes_ = write_sample(l5x, out)
                append_manifest_row(
                    name,
                    f"AOI with {total} Input parameters -- {bools} BOOL and {atomics} DINT -- and an "
                    f"array of {length} instances. Member TOTAL held at {total} while the BOOL "
                    f"fraction is swept, which is exactly the axis OQ-AOIBOOLPACK-PAIRING records as "
                    f"not extrapolating cleanly. Reconciling the 178 captured aoibp_/aoipack_ rows "
                    f"shows the odd-length-array +4 term is present in some mixes and absent in "
                    f"others: mc10 gives -4 at b00, 0 at b01/b05/b09 and -4 again at b10, which "
                    f"looks like pure-versus-mixed until mc20 carries it at b00, b02, b10, b18 AND "
                    f"b20. It is a two-variable surface in (bool_count, atomic_count) and the "
                    f"existing files sample three totals at four or five mixes each. Built at an "
                    f"even AND an odd array length so the parity term is measured at this mix rather "
                    f"than inferred from a neighbour. Same AOI and array-tag shape as aoibp_dense_* "
                    f"and aoipack_mc*, so it differences straight against them. "
                    f"OQ-AOIBOOLPACK-PAIRING.",
                    "aoi_array_packing", out, bytes_,
                )
                written += 1
    print(f"Total: {written}")


if __name__ == "__main__":
    main()
