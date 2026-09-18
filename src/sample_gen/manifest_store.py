"""Two files, two writers, no merge conflicts.

`samples/manifest.csv` used to hold everything, and BOTH producers rewrote
all ~3,600 rows on every run: the generators when a sample is built, and
`batch_memory_capture.ps1` when a capture lands (its `Export-Csv` rewrites the
whole file). Two whole-file rewrites of the same file from two machines is a
guaranteed conflict on every single pull, and it cost more time than the
measurements did.

The fix is ownership, not merge skill. The columns split cleanly by who
writes them, so they now live in separate files and neither writer ever
touches the other's:

    samples/manifest.csv   THE SPEC -- what a sample IS.
                           sample_id, description, category, l5x_path,
                           predicted_bytes. Written by generators only.

    samples/captures.csv   THE RESULT -- what the controller reported.
                           sample_id, actual_bytes, controller_model,
                           firmware_rev, date_tested, notes, error_count,
                           warning_count, message_value, window_title,
                           error_log. Written by the capture tooling only.

`delta` and `delta_pct` are GONE, not moved. CLAUDE.md already forbids
trusting a stored delta -- it goes stale the moment any constant changes, and
every reader recomputes it live. Keeping them was storing a derived value in
the one place two writers fought over.

`.gitattributes` marks both `merge=union`, so even two appends racing at the
end of the same file resolve without a conflict; `load_manifest()` collapses
any duplicate sample_id that results, last row winning.

Readers should call `load_manifest()` and get the joined row dict they always
got, so nothing downstream has to know the file was split.
"""

from __future__ import annotations

import csv
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
MANIFEST_PATH = REPO_ROOT / "samples" / "manifest.csv"
CAPTURES_PATH = REPO_ROOT / "samples" / "captures.csv"

SPEC_COLUMNS = ["sample_id", "description", "category", "l5x_path", "predicted_bytes"]
CAPTURE_COLUMNS = [
    "sample_id", "actual_bytes", "controller_model", "firmware_rev", "date_tested",
    "notes", "error_count", "warning_count", "message_value", "window_title", "error_log",
]
# What a joined row looks like, so a reader that wants every key gets them all
# even for a sample that has never been captured.
JOINED_COLUMNS = SPEC_COLUMNS + [c for c in CAPTURE_COLUMNS if c != "sample_id"]


def _read(path: Path) -> list[dict]:
    """utf-8-SIG, not utf-8: the capture tooling is PowerShell `Export-Csv`,
    which writes UTF-8 with a BOM. Read as plain utf-8 the BOM lands inside the
    first header cell and every DictReader consumer fails with a KeyError."""
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return [r for r in csv.DictReader(fh) if (r.get("sample_id") or "").strip()]


def _dedupe(rows: list[dict]) -> dict[str, dict]:
    """Last row wins. A union merge can leave the same sample_id twice when
    both sides appended it; the later write is the more recent truth."""
    out: dict[str, dict] = {}
    for r in rows:
        out[r["sample_id"]] = r
    return out


def load_manifest() -> list[dict]:
    """Every sample, spec joined to its capture, in manifest order.

    A sample with no capture yet carries the capture keys as empty strings
    rather than missing them, so `row["actual_bytes"]` is always safe.
    """
    specs = _read(MANIFEST_PATH)
    caps = _dedupe(_read(CAPTURES_PATH))
    joined = []
    seen = set()
    for spec in specs:
        sid = spec["sample_id"]
        if sid in seen:
            continue                      # union-merge duplicate; first spec wins
        seen.add(sid)
        row = {k: (spec.get(k) or "") for k in SPEC_COLUMNS}
        cap = caps.get(sid, {})
        for k in CAPTURE_COLUMNS[1:]:
            row[k] = cap.get(k) or ""
        joined.append(row)
    return joined


def write_specs(rows: list[dict]) -> None:
    _write(MANIFEST_PATH, SPEC_COLUMNS, rows)


def write_captures(rows: list[dict]) -> None:
    _write(CAPTURES_PATH, CAPTURE_COLUMNS, rows)


def _write(path: Path, columns: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=columns, quoting=csv.QUOTE_ALL)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in columns})


def upsert_capture(row: dict) -> None:
    """Add or replace one capture result, leaving every other row untouched."""
    caps = _dedupe(_read(CAPTURES_PATH))
    caps[row["sample_id"]] = {c: row.get(c, "") for c in CAPTURE_COLUMNS}
    write_captures(list(caps.values()))
