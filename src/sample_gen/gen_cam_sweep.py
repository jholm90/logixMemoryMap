"""CAM structure byte-size count sweep (James, 2026-08-26: "touch these and
finalize them now" -- includes the CAM sweep flagged in OPEN_QUESTIONS.md
OQ-PREDEFINED item 8 as the one remaining concrete next step).

Mechanistic research (2026-08-25, see OPEN_QUESTIONS.md) already confirmed
CAM's real field shape by reading `samples/local/L5X_Samples/
RobbinsGrn_2026_05_13r00.L5X` directly: 3 fields per array element
(Master:REAL, Slave:REAL, SegmentType:DINT), and -- unlike CAM_PROFILE,
which hides 14 real L5K values behind 1 visible Decorated field -- CAM's
own L5K format shows the SAME 3 numbers per element as Decorated. No
hidden fields. That's a real structural finding, not a guess, but it is
NOT itself a byte-count formula -- "12 raw bytes/element" is a plausible
starting hypothesis (a clean base + 12*count), not something to wire
without a real count sweep, per this project's standing rule against
extrapolating from structural inspection alone.

This sweep: 1/5/10/20/50 CAM elements, one tag per file, isolates the
per-element marginal rate the same way every other array-of-something
sweep in this project has (array_dint, aoipack_atomic, etc). CAM has no
sizing-engine formula yet (OQ-PREDEFINED), so every file here goes through
write_sample_unmodeled (predicted_bytes=0, not a guess) -- same convention
already used for the AXIS_*/MOTION_GROUP predefined-structure files before
those got their own formula wired.

`cam_tag_xml()` (builders.py, already built 2026-08-25 from the same real
corpus file) reproduces the confirmed real shape exactly.

Run: python -m sample_gen.gen_cam_sweep
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import cam_tag_xml
from sample_gen.manifest import append_manifest_row, write_sample_unmodeled
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "predefined"


def _write_unmodeled(l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    write_sample_unmodeled(l5x, out_path)
    append_manifest_row(out_name, description, "cam_structure", out_path, 0)
    print(f"Wrote {out_path} (unmodeled, predicted_bytes=0)")


def group_cam_count_sweep() -> int:
    n = 0
    for count in [1, 5, 10, 20, 50]:
        tag_xml = cam_tag_xml("CamData", count)
        l5x = build_l5x(target_name=f"CamSweepN{count:02d}", tags_xml=tag_xml)
        _write_unmodeled(
            l5x, f"cam_structure_n{count:02d}",
            f"1x CAM[{count}] tag -- Master:REAL/Slave:REAL/SegmentType:DINT per element (confirmed "
            f"real shape, no hidden fields unlike CAM_PROFILE), count-sweep point for the byte-size formula",
        )
        n += 1
    return n


if __name__ == "__main__":
    total = group_cam_count_sweep()
    print(f"\nTotal files: {total}")
