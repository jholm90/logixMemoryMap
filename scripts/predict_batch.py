"""Predicted total + coverage gaps for a batch of L5X files, in one table.

James, 2026-09-04: "You also have a directory of samples files I uploaded
with no sizes." These are complete real programs with no captured Capacity
reading, so nothing in manifest.csv covers them and scripts/accuracy_report.py
(which needs an actual_bytes to compare against) skips them entirely.

This runs the real engine -- the same build_report() the CLI, the UI and the
export call -- and prints what it predicts for each file plus what it could
NOT price in that file, so a real number can be dropped alongside it the
moment one exists. The coverage column is the important half: a total with
297 unpriced ST routines behind it is not the same claim as a total with
none, and this makes that visible before anyone compares it to a real
reading.

Run: python scripts/predict_batch.py <path-or-glob> [...] [--csv OUT]
"""

from __future__ import annotations

import argparse
import csv
import glob
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from l5x_memory_analyzer.sizing.constants import load_memory_model  # noqa: E402
from l5x_memory_analyzer.sizing.coverage import audit_coverage  # noqa: E402
from l5x_memory_analyzer.sizing.report import build_report  # noqa: E402


def _expand(paths: list[str]) -> list[str]:
    out: list[str] = []
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            out += sorted(str(q) for q in p.rglob("*.L5X"))
        else:
            out += sorted(glob.glob(raw)) or ([raw] if p.exists() else [])
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+", help="L5X files, directories, or globs")
    ap.add_argument("--csv", help="also write the table to this CSV")
    args = ap.parse_args()

    files = _expand(args.paths)
    if not files:
        print("No L5X files matched.", file=sys.stderr)
        return 1

    model = load_memory_model()
    rows: list[dict] = []
    for path in files:
        try:
            root = ET.parse(path).getroot()
        except Exception as exc:  # noqa: BLE001 - report, never abort the sweep
            rows.append({"file": Path(path).name, "error": f"{type(exc).__name__}: {exc}"})
            continue
        controller = root.find("Controller")
        entries, errors = build_report(root, model)
        gaps = audit_coverage(root, model.logic_instructions.weights)
        unpriced_routines = sum(g.count for g in gaps if g.kind == "routine_type")
        unpriced_instr = sum(g.count for g in gaps if g.kind == "instruction")
        rows.append({
            "file": Path(path).name,
            "processor": (controller.get("ProcessorType") if controller is not None else "") or "",
            "fw": (controller.get("MajorRev") if controller is not None else "") or "",
            "predicted": sum(e.bytes for e in entries),
            "unsized_items": len([e for e in errors if not e.path.startswith("coverage/")]),
            "unpriced_routines": unpriced_routines,
            "unpriced_instr_uses": unpriced_instr,
            "error": "",
        })

    ok = [r for r in rows if not r["error"]]
    print(f"{'file':<44}{'processor':<18}{'fw':>3}{'predicted':>12}"
          f"{'unsized':>9}{'0-cost rtn':>12}{'0-cost instr':>14}")
    for r in sorted(ok, key=lambda r: -r["predicted"]):
        print(f"{r['file']:<44}{r['processor']:<18}{r['fw']:>3}{r['predicted']:>12,}"
              f"{r['unsized_items']:>9}{r['unpriced_routines']:>12}{r['unpriced_instr_uses']:>14}")
    for r in rows:
        if r["error"]:
            print(f"{r['file']:<44}{r['error']}", file=sys.stderr)

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), quoting=csv.QUOTE_ALL)
            w.writeheader()
            w.writerows(rows)
        print(f"\nwrote {args.csv}")

    print("\n'0-cost rtn' = routines in a language this engine cannot size (ST/FBD/SFC).")
    print("'0-cost instr' = instruction USES with no weight in the model.")
    print("Both are charged 0 bytes, so any predicted total above is a FLOOR, not an estimate,")
    print("for every file whose counts are nonzero. Run scripts/coverage_audit.py for detail.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
