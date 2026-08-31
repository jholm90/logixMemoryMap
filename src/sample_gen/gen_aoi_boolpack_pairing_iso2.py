"""OQ-AOIBOOLPACK-PAIRING per-boundary-crossing term isolation (2026-08-31,
James: "Once again you got a new data point for AOI but no way to resolve
it... if i get a test result that doesnt match my prediction i usually
check my existing work and devise new tests to fix it").

gen_aoi_boolpack_pairing.py's group_dense_membercount() found each
bool_count family (bc=10/20/60) carries its own FIXED offset B that's
flat across dense instance count (n=2..12) but differs BETWEEN families:
bc10 ~20-24, bc20 ~36-40, bc60 140. That result proves B doesn't scale
with instance count -- but only 3 bool_count values were ever tested
densely, so it can't say HOW B scales with bool_count, or whether the
jump from ~40 (bc20) to 140 (bc60) is smooth or a real step specifically
at the 32-bit packed-word boundary (bc60 needs 2 packed words, bc10/bc20
fit in 1).

This file holds n densely fixed (matching the already-confirmed-flat
n=2/4/8 subset of the dense range, not the full 6-value sweep -- B is
already known flat across n, so 3 points per bool_count is enough to
re-confirm flatness at each new bc without redundant generation) and
varies bool_count instead, deliberately bracketing the 32-bit word
boundary: 16, 24, 31, 32, 33, 40, 48. If B jumps sharply between bc=31
and bc=33 specifically, that's the per-boundary-crossing term; if it
climbs smoothly across the whole range, B is a real function of
bool_count itself, not a boundary-crossing effect.

21 files (7 bool_counts x 3 instance counts). Suffixed `_iso2` per
James's request to keep this follow-up round visually distinct from the
original dense-membercount batch.

Run: python -m sample_gen.gen_aoi_boolpack_pairing_iso2
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, aoi_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

AOI_OUT = Path(__file__).parent.parent.parent / "samples" / "generated" / "aoi"

N_VALUES = (2, 4, 8)
BOOL_COUNTS = (16, 24, 31, 32, 33, 40, 48)


def _write(l5x: str, out_name: str, description: str) -> int:
    out_path = AOI_OUT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "aoi_array_packing", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")
    return 1


def main() -> int:
    total = 0
    for bool_count in BOOL_COUNTS:
        aoi_name = f"AoiBpBoundaryIso2Bc{bool_count}"
        inputs = [MemberSpec(f"InB{i}", "BOOL") for i in range(bool_count)]
        definition, storage = aoi_xml(aoi_name, inputs, [], [], [])
        for count in N_VALUES:
            tag = tag_xml("TestInstanceArray", aoi_name, dimensions=(count,), udt_members=storage)
            l5x = build_l5x(target_name=aoi_name, tags_xml=tag, extra_aoi_xml=definition)
            total += _write(
                l5x, f"aoibp_boundary_bc{bool_count:02d}_n{count:02d}_iso2",
                f"AOI, {bool_count} BOOL Input params (single section), array of {count} instances -- "
                f"OQ-AOIBOOLPACK-PAIRING per-boundary-crossing isolation: bool_count brackets the "
                f"32-bit packed-word boundary (16/24/31/32/33/40/48) at dense n (2/4/8, matching the "
                f"already-confirmed-flat subset of the dense-membercount range) to isolate how the "
                f"flat per-array offset B scales with bool_count, and whether it steps sharply at the "
                f"31->33 word-crossing specifically.",
            )
    print(f"\nDone. {total} files.")
    return total


if __name__ == "__main__":
    main()
