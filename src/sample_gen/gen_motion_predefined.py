"""OQ-PREDEFINED: MOTION_INSTRUCTION and CAM_PROFILE, James 2026-08-22:
"You need to refer to Logix documentation for this... I think your sample
projects have majority of them in place and you can reference them
yourself." Rockwell's own literature site is blocked by this session's
network egress proxy, so this went straight to the real corpus instead --
which turned out to have everything needed:

  - MOTION_INSTRUCTION: real full shape found in
    samples/local/BAI10048_TrimmerTally_20250704.L5X (AxisMotionControlMAG)
    -- a genuine 16-member Decorated Structure (FLAGS DINT, 10 status
    BOOLs, ERR INT, STATUS/STATE/EXERR SINT, SEGMENT DINT), dual L5K/
    Decorated format like TIMER/COUNTER. James: "used as a common tag type
    for most motion instructions... MAH, MSO, MASR... has the
    Motion_Instruction and the Axis" -- confirmed structurally, one tag per
    motion-instruction call site, alongside the Axis tag.
  - CAM_PROFILE: real 20-element array found in
    samples/local/L5X_Samples/CMU_2025_10_14r00.L5X (HoldCamProfile) --
    confirms exactly what James flagged ("some voodoo behind the scenes...
    hides stuff not visible in the tag browser"): the Decorated view shows
    only ONE member (Status, DINT) per element, but the real L5K row per
    element carries 14 numeric fields. No way to size this structurally --
    every generated element reuses real captured row data (see
    builders.py's _CAM_PROFILE_L5K_ROWS) rather than invented values.

Both are logged as unmodeled predefined structures (predicted_bytes=0),
same convention as the Axis tags -- real Capacity data is the only way
either gets a byte-size constant.

Run: python -m sample_gen.gen_motion_predefined
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import cam_profile_tag_xml, motion_instruction_tag_xml
from sample_gen.lint import lint_or_raise
from sample_gen.manifest import append_manifest_row
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "axis"


def _write_unmodeled(l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    lint_or_raise(l5x, context=str(out_path))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(l5x, encoding="utf-8")
    append_manifest_row(out_name, f"{description} (unmodeled predefined structure)", "axis", out_path, 0)
    print(f"Wrote {out_path} (predicted N/A -- unmodeled predefined structure)")


def group_motion_instruction() -> None:
    for n in [1, 5, 50]:
        tags = "\n".join(motion_instruction_tag_xml(f"MotionInstr{i}") for i in range(n))
        l5x = build_l5x(target_name=f"MotionInstrN{n}", tags_xml=tags)
        _write_unmodeled(l5x, f"motioninstr_n{n:05d}", f"{n} MOTION_INSTRUCTION tag(s)")


def group_cam_profile() -> None:
    for n in [1, 5, 20, 50]:
        tag = cam_profile_tag_xml("CamProfile1", n)
        l5x = build_l5x(target_name=f"CamProfileN{n}", tags_xml=tag)
        _write_unmodeled(l5x, f"camprofile_n{n:05d}", f"1 CAM_PROFILE tag, array of {n} elements")


def main() -> None:
    group_motion_instruction()
    group_cam_profile()
    print("\nDone. 7 files.")


if __name__ == "__main__":
    main()
