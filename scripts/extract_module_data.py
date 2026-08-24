"""Module/IO extraction table (2026-08-27, James: "check your DB of
extracted io modules from existing programs - i want this table to have
the in/out/config controller tags separately marked in the data for these
modules and see how it compares to the actual module size... also add
records from the L5X module profile as a checkable item. i know you dont
have modules yet but i want you to prep this data").

Walks every real L5X in samples/local/ (gitignored, real/proprietary
program exports -- see samples/local/README.md) and runs each one through
parser/modules.py, writing one row per real Module found to
samples/local/module_extraction.csv (ALSO gitignored -- this table is
derived from real client program files, and file names/module comments
can be client-identifying, so it stays local-only, same policy as every
other real-corpus-derived artifact in this project; never move this into
the tracked samples/ tree).

Columns, per James's ask:
  - source_file: which real L5X this module came from (relative path
    under samples/local/), so a row can be traced back and re-checked.
  - module_name, catalog_number, slot: identifying info.
  - input_profile/input_bytes, output_profile/output_bytes,
    config_profile/config_bytes: kept SEPARATE per I/O direction, not
    collapsed into one number -- both the real Rockwell module-profile
    string (e.g. "AB:5000_DI16:C:0") AND the byte count L5X states
    directly for each (see parser/modules.py's docstring: these are
    exact, stated attributes, not fitted).
  - stated_total_bytes: sum of the three above -- what L5X itself claims.
  - actual_module_bytes: DELIBERATELY BLANK. This is the checkable
    comparison column James asked for -- once a real controller's
    Capacity-tab delta for adding/removing ONE specific module is
    captured, it goes here, and stated_total_bytes vs actual_module_bytes
    is the real per-module/per-connection overhead question (OQ-MODULEIO)
    this whole table exists to eventually answer. Nothing here is a
    sizing formula yet -- this is prep data, not a wired result.
  - notes: blank, free text for manual review.

Run: python scripts/extract_module_data.py
"""

from __future__ import annotations

import csv
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from l5x_memory_analyzer.parser.modules import parse_modules  # noqa: E402

LOCAL_ROOT = REPO_ROOT / "samples" / "local"
OUT_PATH = LOCAL_ROOT / "module_extraction.csv"

COLUMNS = [
    "source_file", "module_name", "catalog_number", "slot",
    "input_profile", "input_bytes",
    "output_profile", "output_bytes",
    "config_profile", "config_bytes",
    "stated_total_bytes", "actual_module_bytes", "notes",
]


def main() -> None:
    if not LOCAL_ROOT.exists():
        print(f"{LOCAL_ROOT} does not exist -- nothing to extract.")
        return

    rows: list[dict] = []
    l5x_files = sorted(LOCAL_ROOT.rglob("*.L5X")) + sorted(LOCAL_ROOT.rglob("*.l5x"))
    files_with_modules = 0
    files_failed = 0

    for path in l5x_files:
        try:
            tree = ET.parse(path)
        except ET.ParseError as exc:
            files_failed += 1
            print(f"SKIP (parse error): {path.relative_to(LOCAL_ROOT)} -- {exc}")
            continue

        modules = parse_modules(tree.getroot())
        if not modules:
            continue
        files_with_modules += 1

        rel_path = str(path.relative_to(LOCAL_ROOT))
        for m in modules:
            rows.append({
                "source_file": rel_path,
                "module_name": m.name,
                "catalog_number": m.catalog_number,
                "slot": m.slot if m.slot is not None else "",
                "input_profile": m.input_profile or "",
                "input_bytes": m.connection_input_bytes,
                "output_profile": m.output_profile or "",
                "output_bytes": m.connection_output_bytes,
                "config_profile": m.config_profile or "",
                "config_bytes": m.config_bytes,
                "stated_total_bytes": m.stated_total_bytes,
                "actual_module_bytes": "",
                "notes": "",
            })

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n{len(l5x_files)} L5X file(s) scanned, {files_failed} failed to parse, "
          f"{files_with_modules} contained at least one Module.")
    print(f"{len(rows)} module row(s) written to {OUT_PATH}")


if __name__ == "__main__":
    main()
