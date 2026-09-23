"""Corpus-wide predicted-versus-actual accuracy report.

Recomputes every prediction LIVE against the current engine for every manifest
row that has a real capture, and reports error by category. The stored
predicted_bytes column is never read -- it goes stale the moment any constant
changes.

THE VALIDITY FILTER. A row is a valid fitting point only if all of these hold:

  * `actual_bytes` is a real integer.
  * `error_count` is 0 or blank. A project that BUILT WITH ERRORS did not fully
    compile, so its Capacity reading is of an incomplete project. This is not a
    small effect -- it manufactures a fake over-prediction signal, because the
    real project is missing whatever content failed to build. It cost one wrong
    model change: an 18-file axis sweep, every file at `error_count = drives+1`,
    was fitted into a multi-module marginal discount that had to be reverted.
  * `actual_bytes` is at least the empty-project baseline. A capture below it is
    physically impossible -- no project uses less memory than an empty one on
    the same controller -- and this class of bad read passes every other check:
    error_count 0, no warning, a matching window title. One capture run returned
    2,976 bytes for 24 separate 1769 files against a baseline of 69,600-98,944;
    left in, those 30 rows moved the corpus mean absolute error from 0.68% to
    32.17%. The floor comes from the model's own `empty_project_baseline_bytes`,
    so it tracks the model.
  * `notes` carries neither WINDOW TITLE MISMATCH nor ZERO CAPACITY, both
    established bad-read markers. See `docs/TESTING_PLAN.md`.

A BLANK error_count is weaker evidence than an explicit 0: 268 captured rows
predate the column entirely, and for those, "no errors recorded" means "nobody
recorded" -- absence of evidence, not evidence of a clean build. They are counted
by default, because reclassifying 268 rows as invalid on a hunch is its own
unforced error; `--strict` excludes them so the difference is measurable rather
than assumed. Prefer an explicit-0 row whenever a single row anchors a new
measurement.

Run: python scripts/accuracy_report.py [--json OUT] [--category CAT] [--strict]
"""

from __future__ import annotations

import argparse
import collections
import csv
import json
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
# The manifest is split in two so that the generators and the capture
# tooling never write the same file: samples/manifest.csv holds the spec,
# samples/captures.csv the results. load_manifest() joins them back into
# the row shape this script already expects.
sys.path.insert(0, str(REPO_ROOT / "src"))
from sample_gen.manifest_store import load_manifest  # noqa: E402

sys.path.insert(0, str(REPO_ROOT / "src"))

from l5x_memory_analyzer.sizing.constants import load_memory_model  # noqa: E402
from l5x_memory_analyzer.sizing.report import build_report  # noqa: E402

MANIFEST = REPO_ROOT / "samples" / "manifest.csv"
_BAD_NOTE_MARKERS = ("WINDOW TITLE MISMATCH", "ZERO CAPACITY")


_MODEL = load_memory_model()
# Physical floor: an empty project on the SMALLEST-baseline controller this
# model knows. Anything under it did not come from a real Capacity reading.
IMPLAUSIBLE_BELOW = _MODEL.empty_project_baseline_bytes


def is_valid_capture(row: dict, strict: bool = False) -> tuple[bool, str]:
    """(valid, reason_if_not) -- see this module's docstring.

    strict=True additionally rejects a row whose error_count is blank
    rather than an explicit 0 (a capture predating the error_count column,
    so its build status was never recorded either way)."""
    actual = (row.get("actual_bytes") or "").strip()
    if not actual.isdigit():
        return False, "no capture"
    if int(actual) < IMPLAUSIBLE_BELOW:
        return False, f"implausible capture (< empty-project baseline {IMPLAUSIBLE_BELOW})"
    notes = row.get("notes") or ""
    for marker in _BAD_NOTE_MARKERS:
        if marker in notes:
            return False, marker
    error_count = (row.get("error_count") or "").strip()
    if error_count not in ("", "0"):
        return False, f"built with {error_count} error(s)"
    if strict and error_count == "":
        return False, "error_count never recorded"
    return True, ""


def collect(category_filter: str | None = None, strict: bool = False) -> tuple[list[dict], collections.Counter]:
    model = _MODEL
    rows = load_manifest()

    results: list[dict] = []
    excluded: collections.Counter = collections.Counter()
    for row in rows:
        valid, reason = is_valid_capture(row, strict)
        if not valid:
            if reason != "no capture":
                excluded[reason] += 1
            continue
        if category_filter and row.get("category") != category_filter:
            continue
        path = row.get("l5x_path") or ""
        if not os.path.exists(path):
            excluded["file missing"] += 1
            continue
        try:
            entries, errors = build_report(ET.parse(path).getroot(), model)
        except Exception as exc:  # noqa: BLE001 - report, never abort the sweep
            excluded[f"unparseable ({type(exc).__name__})"] += 1
            continue
        predicted = sum(e.bytes for e in entries)
        actual = int(row["actual_bytes"])
        results.append({
            "sample_id": row["sample_id"], "category": row.get("category", ""),
            "actual": actual, "predicted": predicted, "delta": actual - predicted,
            "pct": (actual - predicted) / actual * 100, "size_errors": len(errors),
        })
    return results, excluded


def _summarize(rows: list[dict]) -> tuple[float, float, int]:
    total_actual = sum(r["actual"] for r in rows)
    total_pred = sum(r["predicted"] for r in rows)
    sum_pct = (total_actual - total_pred) / total_actual * 100 if total_actual else 0.0
    mean_abs = sum(abs(r["pct"]) for r in rows) / len(rows)
    within1 = sum(1 for r in rows if abs(r["pct"]) < 1)
    return sum_pct, mean_abs, within1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", help="write the per-file results to this path")
    ap.add_argument("--category", help="only report this manifest category")
    ap.add_argument("--worst", type=int, default=10, help="list this many worst files")
    ap.add_argument("--strict", action="store_true",
                    help="also exclude rows whose error_count was never recorded (blank)")
    args = ap.parse_args()

    results, excluded = collect(args.category, args.strict)
    if not results:
        print("No valid capture rows matched.")
        return 1

    if args.json:
        Path(args.json).write_text(json.dumps(results, indent=1))

    sum_pct, mean_abs, within1 = _summarize(results)
    print(f"Valid capture rows: {len(results)}")
    if excluded:
        print("Excluded as invalid: " + ", ".join(f"{v} {k}" for k, v in excluded.most_common()))
    print(f"Overall (sum-weighted): {sum_pct:+.3f}%")
    print(f"Mean |error| per file:  {mean_abs:.3f}%")
    print(f"Within +/-1%:           {within1}/{len(results)} ({within1 / len(results) * 100:.1f}%)")

    by_cat: dict[str, list[dict]] = collections.defaultdict(list)
    for r in results:
        by_cat[r["category"]].append(r)
    print(f"\n{'category':<22}{'n':>5}{'sum%':>10}{'mean|%|':>10}{'within1%':>12}")
    for cat, rows in sorted(by_cat.items(), key=lambda kv: -sum(abs(r["delta"]) for r in kv[1])):
        s, m, w = _summarize(rows)
        print(f"{cat:<22}{len(rows):>5}{s:>+9.2f}%{m:>9.2f}%{w:>7}/{len(rows):<5}")

    if args.worst:
        print(f"\nWorst {args.worst} by |% error|:")
        for r in sorted(results, key=lambda r: -abs(r["pct"]))[: args.worst]:
            print(f"  {r['sample_id']:<44}{r['actual']:>10,}{r['predicted']:>11,}"
                  f"{r['delta']:>+10,}{r['pct']:>+8.2f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
