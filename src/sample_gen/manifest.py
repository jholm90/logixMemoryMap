"""Shared helpers for writing a generated sample + its manifest.csv row.
Used by every sample_gen generator so predicted_bytes is always computed
the same way (via this project's own sizing engine) and manifest.csv rows
stay consistently formatted regardless of which generator produced them.
"""

from __future__ import annotations

import csv
import xml.etree.ElementTree as ET
from pathlib import Path

from l5x_memory_analyzer.sizing.constants import load_memory_model
from l5x_memory_analyzer.sizing.report import build_report

REPO_ROOT = Path(__file__).parent.parent.parent
MANIFEST_PATH = REPO_ROOT / "samples" / "manifest.csv"
MANIFEST_COLUMNS = (
    "sample_id,description,category,l5x_path,predicted_bytes,actual_bytes,"
    "delta,delta_pct,controller_model,firmware_rev,date_tested,notes"
).split(",")


def predicted_bytes(l5x_text: str) -> int:
    root = ET.fromstring(l5x_text)
    model = load_memory_model()
    entries, errors = build_report(root, model)
    if errors:
        raise RuntimeError(f"sample has unsized tags, fix the generator: {errors}")
    return sum(e.bytes for e in entries)


def write_sample(l5x_text: str, out_path: Path) -> int:
    """Writes the L5X file and returns its predicted byte total."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(l5x_text, encoding="utf-8")
    return predicted_bytes(l5x_text)


def append_manifest_row(sample_id: str, description: str, category: str, l5x_path: Path, bytes_predicted: int) -> None:
    """Upsert keyed on sample_id: regenerating a sample updates its existing
    row (description/category/predicted_bytes) in place rather than piling up
    a duplicate, so any actual_bytes already logged against that sample_id
    survives a regeneration untouched."""
    rel_path = str(l5x_path.relative_to(REPO_ROOT))
    rows = []
    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH, newline="", encoding="utf-8") as f:
            rows = list(csv.reader(f))[1:]  # drop header, rewritten below

    updated = False
    for row in rows:
        if row and row[0] == sample_id:
            row[1:5] = [description, category, rel_path, str(bytes_predicted)]
            updated = True
            break
    if not updated:
        rows.append([sample_id, description, category, rel_path, str(bytes_predicted), "", "", "", "", "", "", ""])

    with open(MANIFEST_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(MANIFEST_COLUMNS)
        writer.writerows(rows)
