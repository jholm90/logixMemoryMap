"""Per-module I/O extraction table, built from the real corpus.

Walks every real L5X in `samples/local/` through `parser/modules.py` and writes
one row per Module found to `samples/local/module_extraction.csv`. That output is
also gitignored: it is derived from real customer programs, and file names and
module comments can be identifying, so it stays local-only. Never move it into
the tracked `samples/` tree.

The in, out and config tags are kept SEPARATE per direction rather than collapsed
into one number, so a stated size can be compared against a measured one.

Columns:
  source_file           which real L5X the module came from, relative to
                        `samples/local/`, so a row can be traced and re-checked
  module_name, catalog_number, slot
  input_*, output_*, config_*   the Rockwell module-profile string (for example
                        `AB:5000_DI16:C:0`) and the byte count L5X states for
                        each. These are exact stated attributes, not fitted --
                        see `parser/modules.py`.
  stated_total_bytes    sum of the three above: what L5X itself claims
  actual_module_bytes   DELIBERATELY BLANK. The comparison column. Once a real
                        controller's Capacity delta for adding or removing ONE
                        module is captured it goes here, and stated versus actual
                        is the per-module overhead question this table exists to
                        answer. See OQ-MODULEIO.
  notes                 free text for manual review

Nothing here is a sizing formula. This is reference data, not a wired result.

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
