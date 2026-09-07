"""Fail if any sizing constant carries a weaker confidence tier than its
own capture data supports.

Written 2026-09-06 after an audit found 174 of 185 ASSUMED predefined
structures already had error-free, exactly-0.0000% capture data on disk.
Nothing was wrong with the model's numbers; the tiers had simply never
been updated when the questions closed. That is not cosmetic, because
`weakest()` propagates a tier upward: one stale ASSUMED on a leaf type
marked 11.53% of all real-file bytes as assumed when the true figure was
4.33%.

A confidence tier is a claim about evidence, so it has to be checkable
rather than remembered. This script is the check.

  KNOWN    measured directly, or read straight out of the L5X. Two
           independent derivations agreeing, or a capture at 0.0000%
           residual across a range.
  FITTED   regressed from real capture data. Right on average, carries
           residual error, and can be wrong off the range it was fit on.
  ASSUMED  no capture behind it. Derived from documentation or inference.

Exit code 1 if any ASSUMED entry has a clean capture that would justify
KNOWN. Run it after every capture reconciliation.

Usage: python scripts/audit_confidence.py
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
MODEL = REPO_ROOT / "src" / "l5x_memory_analyzer" / "sizing" / "memory_model.yaml"
MANIFEST = REPO_ROOT / "samples" / "manifest.csv"

# A capture justifies KNOWN when it is error-free and lands either exactly
# on prediction or inside the universal per-file offset band this corpus
# shows everywhere (see MEMORY_MODEL.md).
NOISE_BAND_BYTES = 8


def _clean_capture(row: dict) -> bool:
    if not row or not row.get("actual_bytes", "").strip():
        return False
    if int((row.get("error_count") or "0") or 0) > 0:
        return False
    delta = (row.get("delta") or "").strip()
    pct = (row.get("delta_pct") or "").strip()
    if pct and abs(float(pct)) < 0.0005:
        return True
    return bool(delta) and abs(int(delta)) <= NOISE_BAND_BYTES


def main() -> int:
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    rows = {r["sample_id"]: r for r in csv.DictReader(MANIFEST.open(encoding="utf-8"))}

    stale: list[tuple[str, str]] = []
    for type_name, spec in (model.get("predefined_structures") or {}).items():
        if not isinstance(spec, dict) or spec.get("confidence") != "ASSUMED":
            continue
        row = rows.get(f"predefprobe_{type_name.lower()}")
        if _clean_capture(row):
            stale.append((f"predefined_structures.{type_name}", row["sample_id"]))

    if stale:
        print(f"{len(stale)} constant(s) tagged ASSUMED with a clean capture behind them:\n")
        for key, sample in stale:
            print(f"  {key:52} <- {sample}")
        print("\nUpgrade the tier to KNOWN or record why the capture does not count.")
        return 1

    print("Confidence audit clean: no ASSUMED constant has an unreconciled clean capture.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
