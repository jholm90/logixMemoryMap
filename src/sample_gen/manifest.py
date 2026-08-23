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

from sample_gen.lint import lint_or_raise

REPO_ROOT = Path(__file__).parent.parent.parent
MANIFEST_PATH = REPO_ROOT / "samples" / "manifest.csv"
MANIFEST_COLUMNS = (
    "sample_id,description,category,l5x_path,predicted_bytes,actual_bytes,"
    "delta,delta_pct,controller_model,firmware_rev,date_tested,notes,"
    "error_count,warning_count,message_value,window_title"
).split(",")


def predicted_bytes(l5x_text: str) -> int:
    root = ET.fromstring(l5x_text)
    model = load_memory_model()
    entries, errors = build_report(root, model)
    if errors:
        raise RuntimeError(f"sample has unsized tags, fix the generator: {errors}")
    return sum(e.bytes for e in entries)


def write_sample(l5x_text: str, out_path: Path) -> int:
    """Writes the L5X file and returns its predicted byte total.

    Runs the local heuristic pre-flight lint first (sample_gen/lint.py,
    2026-08-22) -- catches the two known real error classes (missing array
    subscript, instruction/AOI reference with no matching definition)
    before the file ever ships, since l5x2acd conversion succeeding does
    NOT mean the ladder logic would actually verify in Studio 5000
    (confirmed empirically, see lint.py's docstring)."""
    lint_or_raise(l5x_text, context=str(out_path))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(l5x_text, encoding="utf-8")
    return predicted_bytes(l5x_text)


def write_sample_unmodeled(l5x_text: str, out_path: Path) -> None:
    """Like write_sample(), for a file containing an AXIS_*/MOTION_GROUP tag
    -- those are unmodeled predefined structures (OQ-AXISSTRUCT), so the
    sizing engine can't compute predicted_bytes for them at all (confirmed:
    explicit SizeError, not a crash). Still runs the lint pre-flight check;
    just skips the strict predicted_bytes requirement. Caller logs its own
    manifest row (predicted_bytes=0, category, description) since those
    vary per generator -- this only writes the file."""
    lint_or_raise(l5x_text, context=str(out_path))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(l5x_text, encoding="utf-8")


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
        rows.append([sample_id, description, category, rel_path, str(bytes_predicted), "", "", "", "", "", "", "", "", "", "", ""])

    with open(MANIFEST_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(MANIFEST_COLUMNS)
        writer.writerows(rows)
