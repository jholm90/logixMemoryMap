"""What the sizing engine cannot price, across any set of L5X files.

James, 2026-09-04: "I need to make sure that in the long run all of the
calculations are done inside the python logic for the total project scripts
and not just claude in depth testing." This is the operator-facing side of
that: `l5x_memory_analyzer.sizing.coverage.audit_coverage()` is what runs,
the same function `build_report()` calls on every single file it sizes --
this script only aggregates it across many files and sorts the result. No
analysis lives here that the engine does not already do on its own.

Run it on a batch of unseen real programs BEFORE trusting their totals: it
names every routine language and every instruction in them that this engine
charges 0 bytes for. A gap it lists is not an error in the file -- it is a
hole in the model, and the total for that file is understated by whatever
that content really costs.

Run: python scripts/coverage_audit.py <path-or-glob> [...] [--per-file]
"""

from __future__ import annotations

import argparse
import collections
import glob
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from l5x_memory_analyzer.sizing.constants import load_memory_model  # noqa: E402
from l5x_memory_analyzer.sizing.coverage import audit_coverage  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+", help="L5X files, directories, or globs")
    ap.add_argument("--per-file", action="store_true", help="list each file's own gaps too")
    args = ap.parse_args()

    files: list[str] = []
    for raw in args.paths:
        p = Path(raw)
        if p.is_dir():
            files += sorted(str(q) for q in p.rglob("*.L5X"))
        else:
            files += sorted(glob.glob(raw)) or ([raw] if p.exists() else [])
    if not files:
        print("No L5X files matched.", file=sys.stderr)
        return 1

    weights = load_memory_model().logic_instructions.weights
    routine_types: collections.Counter = collections.Counter()
    instr_count: collections.Counter = collections.Counter()
    instr_files: collections.Counter = collections.Counter()
    unreadable: list[str] = []
    clean = 0

    for path in files:
        try:
            gaps = audit_coverage(ET.parse(path).getroot(), weights)
        except Exception as exc:  # noqa: BLE001 - report, never abort the sweep
            unreadable.append(f"{path}: {type(exc).__name__}")
            continue
        if not gaps:
            clean += 1
        elif args.per_file:
            print(f"\n{path}")
            for g in gaps:
                print(f"  [{g.kind}] {g.detail} x{g.count}")
        for g in gaps:
            if g.kind == "instruction":
                instr_count[g.detail] += g.count
                instr_files[g.detail] += 1
            else:
                routine_types[g.detail] += g.count

    print(f"\n{len(files)} file(s) scanned; {clean} with no coverage gap at all.")
    if unreadable:
        print(f"{len(unreadable)} unreadable: " + "; ".join(unreadable[:5]))

    if routine_types:
        print("\nROUTINES IN A LANGUAGE THIS ENGINE CANNOT SIZE (charged 0 bytes):")
        for rtype, n in routine_types.most_common():
            print(f"  {rtype:<8}{n:>6} routine(s)")

    if instr_count:
        print(f"\nINSTRUCTIONS WITH NO WEIGHT (charged 0 bytes) -- {len(instr_count)} distinct:")
        print(f"  {'mnemonic':<26}{'uses':>8}{'files':>7}")
        for mnemonic, n in instr_count.most_common():
            print(f"  {mnemonic:<26}{n:>8}{instr_files[mnemonic]:>7}")

    if not routine_types and not instr_count:
        print("\nNo coverage gaps found -- every routine and instruction in these files "
              "is something the engine actually prices.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
