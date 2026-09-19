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
from sample_gen.manifest_store import (  # noqa: E402
    MANIFEST_PATH, SPEC_COLUMNS, load_manifest, write_specs,
)

# The manifest holds the SPEC only -- what a sample is. Results live in
# samples/captures.csv and are written solely by the capture tooling, so the
# generators and that tooling never write the same file. See manifest_store.
MANIFEST_COLUMNS = list(SPEC_COLUMNS)


def predicted_bytes(l5x_text: str) -> int:
    root = ET.fromstring(l5x_text)
    model = load_memory_model()
    entries, errors = build_report(root, model)
    # Coverage/scope notices are INFORMATIONAL, not sizing failures -- they
    # say "this file contains something the model doesn't price yet" (an ST
    # routine, an unweighted instruction, a tag-based alarm condition, a
    # partial export). Those are the whole point of the files that carry
    # them. Only a genuine unsized-tag error means the generator is wrong.
    #
    # Found the moment sizing/coverage.py started routing gaps
    # through the errors channel: every alarm-batch regeneration blew up
    # with "sample has unsized tags" on a file whose only problem was that
    # it contains the very thing it was built to measure.
    blocking = [e for e in errors if not e.path.startswith(("coverage/", "scope/"))]
    if blocking:
        raise RuntimeError(f"sample has unsized tags, fix the generator: {blocking}")
    return sum(e.bytes for e in entries)


def write_sample(l5x_text: str, out_path: Path) -> int:
    """Writes the L5X file and returns its predicted byte total.

    Runs the local heuristic pre-flight lint first (sample_gen/lint.py)
    -- catches the two known real error classes (missing array
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


def append_manifest_row(sample_id: str, description: str, category: str,
                        l5x_path: Path, bytes_predicted: int) -> None:
    """Upsert the SPEC row for one sample, keyed on sample_id.

    Regenerating a sample updates its description, category, path and
    predicted_bytes in place rather than piling up a duplicate. It cannot
    disturb any capture logged against that sample_id, because captures are a
    different file this function never opens -- which is the whole point of
    the split.
    """
    rel_path = str(l5x_path.relative_to(REPO_ROOT))
    rows = [{k: r[k] for k in SPEC_COLUMNS} for r in load_manifest()]
    row = {"sample_id": sample_id, "description": description, "category": category,
           "l5x_path": rel_path, "predicted_bytes": str(bytes_predicted)}
    for i, existing in enumerate(rows):
        if existing["sample_id"] == sample_id:
            rows[i] = row
            break
    else:
        rows.append(row)
    write_specs(rows)

