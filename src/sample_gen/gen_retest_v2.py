"""Retest batch for the 6 rows flagged by the 2026-08-25 manifest audit as
capture-race casualties (docs/OPEN_QUESTIONS.md OQ-CAPTURERACE) -- James's
own AHK/PowerShell capture tooling self-flagged these via a "WINDOW TITLE
MISMATCH" note, meaning the Capacity value logged for each was very likely
read off a still-open PREVIOUS project's window, not the target file's own.

Re-issued here under new `_v2` sample_ids/filenames (and, for the two AOI-
based ones, a distinct internal AOI/UDT name too) so this is a genuinely
new, unique file -- not a same-named regeneration that could get silently
skipped/excluded by whatever de-dup logic the capture pipeline uses, and
so the original (contaminated) row stays in manifest.csv side by side with
the new one for the audit trail (manifest.append_manifest_row upserts on
sample_id, so a new sample_id always adds a new row rather than overwriting).

Content is otherwise byte-identical in intent to the original:
  - array_dint_0000{1,2,5}_v2 -- DINT array, Dimensions=1/2/5 (unchanged
    from the original gen_sweep_batch.py group_d call)
  - paramcount_n0{4,8}_def_only_v2 -- AOI with 4/8 DINT Input params, 0
    instances (unchanged from gen_aoi_sweep.py group_param_count), AOI
    renamed ParamCountN04V2/ParamCountN08V2 for a maximally distinct
    window title
  - udttagcomment_len000_v2 -- UDT tag-level Description, length 0
    (unchanged from gen_comment_sweep.py group_j), UDT renamed CommentJV2

Run: python -m sample_gen.gen_retest_v2
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, aoi_xml
from sample_gen.cli import main as cli_main
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

_AOI_OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "aoi"


def _run_cli(argv: list[str]) -> None:
    rc = cli_main(argv)
    if rc != 0:
        raise RuntimeError(f"sample_gen.cli {argv} exited {rc}")


def retest_array_dint() -> int:
    n = 0
    for size in [1, 2, 5]:
        out = f"array_dint_{size:05d}_v2"
        _run_cli(["tags", "--type", "DINT", "--dims", str(size), "--out", out])
        n += 1
    return n


def retest_paramcount() -> int:
    n = 0
    for count in [4, 8]:
        aoi_name = f"ParamCountN{count:02d}V2"
        out = f"paramcount_n{count:02d}_def_only_v2"
        params = [MemberSpec(f"P{i}", "DINT") for i in range(count)]
        definition, _ = aoi_xml(aoi_name, params, [], [], [])
        l5x = build_l5x(target_name=aoi_name, tags_xml="", extra_aoi_xml=definition)
        out_path = _AOI_OUT_ROOT / f"{out}.L5X"
        bytes_ = write_sample(l5x, out_path)
        append_manifest_row(
            out, f"AOI with {count} DINT Input params, 0 instances (RETEST v2, see OQ-CAPTURERACE)",
            "aoi", out_path, bytes_,
        )
        print(f"Wrote {out_path} (predicted {bytes_} bytes)")
        n += 1
    return n


def retest_udttagcomment() -> int:
    out = "udttagcomment_len000_v2"
    _run_cli(["udt", "--name", "CommentJV2", "--member", "M0:DINT",
              "--tag-desc-len", "0", "--instances", "1", "--out", out])
    return 1


def main() -> None:
    total = 0
    for fn in [retest_array_dint, retest_paramcount, retest_udttagcomment]:
        count = fn()
        print(f"{fn.__name__}: {count} file(s)")
        total += count
    print(f"\nTotal: {total} retest sample(s) generated.")


if __name__ == "__main__":
    main()
