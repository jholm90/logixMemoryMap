"""Every captured row whose measurement has never been acted on.

Written 2026-09-11 after three separate open questions in one session turned
out to be "the data has been sitting in the manifest, captured and clean, for
days". OQ-DEFSCALE (30 files), OQ-AOIARRAYLOCALTAG (27 files) and
OQ-MODULEMARGINAL (54 files) were all in that state, and all three were
answerable in minutes once the rows were differenced.

The failure mode is specific and it is not "we forgot to capture": a capture
run lands, `actual_bytes` is filled in, and nothing ever recomputes the
prediction against the CURRENT engine to see what the row now says. A stored
`delta` goes stale the moment any constant moves, so the manifest's own delta
column cannot be trusted to answer this -- every row here is recomputed live.

Run: python scripts/unreconciled.py [--threshold BYTES] [--csv OUT]
"""

from __future__ import annotations

import argparse
import collections
import csv
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from l5x_memory_analyzer.parser.export_scope import (  # noqa: E402
    context_names,
    detect_export_scope,
    split_totals,
)
from l5x_memory_analyzer.sizing.constants import load_memory_model  # noqa: E402
from l5x_memory_analyzer.sizing.report import build_report  # noqa: E402

MANIFEST = REPO_ROOT / "samples" / "manifest.csv"


def _family(sample_id: str) -> str:
    """Collapse a sample_id to its sweep family: trailing counts and indices
    are what a sweep varies, so they are exactly what must be stripped to see
    a sweep as one thing."""
    stem = re.sub(r"_?n?\d+$", "", sample_id)
    stem = re.sub(r"_[a-z]?\d+(_[a-z]+)?$", r"\1", stem)
    return stem or sample_id


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--threshold", type=int, default=8,
                    help="ignore rows within this many bytes (default 8: the "
                         "project-wide small-residual band)")
    ap.add_argument("--csv", help="write the full row-level table here")
    args = ap.parse_args()

    model = load_memory_model()
    rows = list(csv.DictReader(open(MANIFEST, newline="", encoding="utf-8-sig")))

    out: list[dict] = []
    for r in rows:
        if not r["actual_bytes"]:
            continue
        path = REPO_ROOT / r["l5x_path"]
        if not path.exists():
            out.append({"sample_id": r["sample_id"], "family": _family(r["sample_id"]),
                        "actual": int(r["actual_bytes"]), "predicted": 0, "delta": 0,
                        "note": "FILE MISSING"})
            continue
        try:
            root = ET.parse(path).getroot()
            entries, _errors = build_report(root, model)
            predicted = split_totals(
                entries, context_names(root, detect_export_scope(root)))["total"]
        except Exception as exc:  # noqa: BLE001 - report, never abort the sweep
            out.append({"sample_id": r["sample_id"], "family": _family(r["sample_id"]),
                        "actual": int(r["actual_bytes"]), "predicted": 0, "delta": 0,
                        "note": f"{type(exc).__name__}: {exc}"})
            continue
        actual = int(r["actual_bytes"])
        out.append({"sample_id": r["sample_id"], "family": _family(r["sample_id"]),
                    "actual": actual, "predicted": predicted,
                    "delta": predicted - actual, "note": ""})

    off = [o for o in out if o["note"] or abs(o["delta"]) > args.threshold]
    by_family: dict[str, list[dict]] = collections.defaultdict(list)
    for o in off:
        by_family[o["family"]].append(o)

    print(f"{len(out):,} captured rows recomputed against the current engine")
    print(f"{len(off):,} sit outside +-{args.threshold} bytes, in "
          f"{len(by_family)} families\n")
    print(f"{'family':44s}{'rows':>6}{'worst':>12}{'median':>10}  sign")
    for fam, group in sorted(by_family.items(), key=lambda kv: -len(kv[1])):
        deltas = sorted(o["delta"] for o in group)
        worst = max(deltas, key=abs)
        median = deltas[len(deltas) // 2]
        signs = {("+" if d > 0 else "-" if d < 0 else "0") for d in deltas}
        sign = "".join(sorted(signs))
        notes = sum(1 for o in group if o["note"])
        flag = f"  ({notes} error)" if notes else ""
        print(f"{fam[:43]:44s}{len(group):>6}{worst:>12,}{median:>10,}  {sign}{flag}")

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(out[0].keys()), quoting=csv.QUOTE_ALL)
            w.writeheader()
            w.writerows(sorted(off, key=lambda o: -abs(o["delta"])))
        print(f"\nwrote {args.csv}")

    print("\nA family with many rows, one sign, and a median far from zero is an\n"
          "unreconciled measurement, not noise -- that is the shape all three of\n"
          "2026-09-11's answered questions had before they were differenced.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
