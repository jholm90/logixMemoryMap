"""Second AOI sweep, closing remaining open items (James, 2026-08-21: "add
the open aoi items to the next run... be productive and analyze the most
possible"). Builds on real data already captured from gen_aoi_sweep.py:

  - AOI param-count: marginal cost stabilizes at exactly 20 blocks/param
    for n>=4 (168+16n was the UDT-definition formula; AOI's own formula
    looks like 1184 + 20*n, small-N anomaly at n=1,2 same pattern seen
    everywhere else in this project). Not yet formally logged.
  - AOI param-type (4 params, def-only): does NOT match the UDT pattern
    (flat except BOOL costs more) -- looks WIDTH-driven instead: SINT(1B)/
    BOOL both 1248, INT(2B) 1256, DINT(4B)/REAL(4B) both 1264, LINT(8B)
    1280. Only one count point (n=4) tested so far.

This batch:
  A. AOI type-NAME-length sweep (James asked about this explicitly
     earlier: "just thinking of stuff that could be an issue" -- couldn't
     test it until aoi_xml() existed. Now it does. Mirrors the UDT-name-
     length test exactly: 4 DINT params held constant, only the AOI's own
     name length varies.
  B. Denser BOOL-run-length sweep (4/8/12/16/20 consecutive BOOL Input
     params, def-only) -- the original OQ-AOIBOOLPACK test only had one
     run length (20); if real data from that shows packing, this gives
     enough granularity to find the bucket size the same way the tag-name
     sweep found its 8-character bucket.
  C. Param-type sweep at a SECOND count (n=8) -- is the width-driven
     offset a flat per-parameter constant (doubles at n=8) or does it
     scale differently? Can't tell from one count point alone.
  D. LocalTag-type sweep (n=4, mirrors param-type) -- is the width-driven
     pattern specific to Parameters, or does it show up for LocalTags too?

Run: python -m sample_gen.gen_aoi_sweep2
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, aoi_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "aoi"
ATOMIC_TYPES = ["SINT", "INT", "DINT", "LINT", "REAL", "BOOL"]


def _write(l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "aoi", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


# ---------------------------------------------------------------------------
# A. AOI type-name-length sweep, 4 DINT params held constant.
# ---------------------------------------------------------------------------

def _name_of_length(n: int) -> str:
    base = "A"
    filler = ("OINAME" * (n // 6 + 1))[: n - len(base)]
    return base + filler


def group_name_length() -> None:
    for n in [8, 13, 20, 30]:
        name = _name_of_length(n)
        assert len(name) == n
        params = [MemberSpec(f"P{i}", "DINT") for i in range(4)]
        definition, _ = aoi_xml(name, params, [], [], [])
        l5x = build_l5x(target_name=name, tags_xml="", extra_aoi_xml=definition)
        _write(l5x, f"aoiname_len{n:02d}_def_only", f"AOI (4 DINT params) with AOI type name length={n}, 0 instances")


# ---------------------------------------------------------------------------
# B. Denser BOOL-run-length sweep, def-only.
# ---------------------------------------------------------------------------

def group_bool_run_length() -> None:
    for n in [4, 8, 12, 16, 20]:
        params = [MemberSpec(f"B{i}", "BOOL") for i in range(n)]
        aoi_name = f"BoolRunN{n:02d}"
        definition, _ = aoi_xml(aoi_name, params, [], [], [])
        l5x = build_l5x(target_name=aoi_name, tags_xml="", extra_aoi_xml=definition)
        _write(l5x, f"aoi_boolrun_n{n:02d}_def_only", f"AOI with {n} consecutive BOOL Input params, 0 instances")


# ---------------------------------------------------------------------------
# C. Param-type sweep at n=8 (second count point vs the existing n=4 data).
# ---------------------------------------------------------------------------

def group_param_type_n8() -> None:
    for t in ATOMIC_TYPES:
        params = [MemberSpec(f"P{i}", t) for i in range(8)]
        aoi_name = f"ParamType8{t}"
        definition, _ = aoi_xml(aoi_name, params, [], [], [])
        l5x = build_l5x(target_name=aoi_name, tags_xml="", extra_aoi_xml=definition)
        _write(l5x, f"paramtype_{t.lower()}_n8_def_only", f"AOI with 8 {t} Input params, 0 instances")


# ---------------------------------------------------------------------------
# D. LocalTag-type sweep at n=4 (mirrors the existing param-type test).
# ---------------------------------------------------------------------------

def group_localtag_type() -> None:
    for t in ATOMIC_TYPES:
        locals_ = [MemberSpec(f"L{i}", t) for i in range(4)]
        aoi_name = f"LocalType{t}"
        definition, _ = aoi_xml(aoi_name, [], [], [], locals_)
        l5x = build_l5x(target_name=aoi_name, tags_xml="", extra_aoi_xml=definition)
        _write(l5x, f"localtype_{t.lower()}_n4_def_only", f"AOI with 4 {t} LocalTags, 0 instances")


def main() -> None:
    for group_fn in [group_name_length, group_bool_run_length, group_param_type_n8, group_localtag_type]:
        group_fn()
    total = 4 + 5 + len(ATOMIC_TYPES) + len(ATOMIC_TYPES)
    print(f"\nDone. {total} files.")


if __name__ == "__main__":
    main()
