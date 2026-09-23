"""Report export -- CSV/XLSX (docs/TASKS.md Phase 6).

Both formats dump the same flat SizeEntry/SizeError contract report.py
already produces for the UI/CLI -- no new sizing logic, just a different
serialization. CSV is always available (stdlib `csv`); XLSX needs
`openpyxl` (optional dependency -- see pyproject.toml).
"""

from __future__ import annotations

import csv
import io

from l5x_memory_analyzer.sizing.report import SizeEntry, SizeError

_COLUMNS = ("path", "category", "data_type", "bytes", "pct_of_total", "tier", "basis")


def write_csv(entries: list[SizeEntry], errors: list[SizeError]) -> str:
    """Returns CSV text: the sized entries first, then a blank line and an
    ERRORS section for any tag report.py couldn't size (same two-part shape
    the CLI's `size` command already prints to stdout/stderr)."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(_COLUMNS)
    for e in sorted(entries, key=lambda e: e.bytes, reverse=True):
        writer.writerow([e.path, e.category, e.data_type, e.bytes,
                          f"{e.pct_of_total:.4f}", e.tier, e.basis])
    if errors:
        writer.writerow([])
        writer.writerow(["ERRORS", "path", "message"])
        for err in errors:
            writer.writerow(["", err.path, err.message])
    return buf.getvalue()


def write_xlsx(entries: list[SizeEntry], errors: list[SizeError]) -> bytes:
    """Raises ImportError with a clear message if openpyxl isn't installed
    -- caller decides how to surface that (CLI exits non-zero, UI returns
    a 501 rather than a broken download)."""
    try:
        from openpyxl import Workbook
    except ImportError as exc:
        raise ImportError(
            "XLSX export requires the optional 'openpyxl' package "
            "(pip install openpyxl, or use CSV export instead)"
        ) from exc

    wb = Workbook()
    ws = wb.active
    ws.title = "Report"
    ws.append(list(_COLUMNS))
    for e in sorted(entries, key=lambda e: e.bytes, reverse=True):
        ws.append([e.path, e.category, e.data_type, e.bytes, e.pct_of_total, e.tier, e.basis])

    if errors:
        err_ws = wb.create_sheet("Errors")
        err_ws.append(["path", "message"])
        for err in errors:
            err_ws.append([err.path, err.message])

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()
