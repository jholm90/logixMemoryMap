"""No real program, and no real program's name, in a tracked file.

Drawn after a capture run committed 23 customer programs placed under
samples/generated/Customer/ and wrote their names, window titles and build messages into
samples/captures.csv and samples/convert_log.csv, all pushed to the public repository. The
capture scripts now refuse it (scripts/_autopush.ps1, Test-SafeToCommit); this pins the
same rules on the tree itself.
"""

from __future__ import annotations

import csv
import os
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SAMPLES = REPO / "samples"


def _manifest() -> dict[str, str]:
    with open(SAMPLES / "manifest.csv", encoding="utf-8-sig") as f:
        return {r["sample_id"]: r["category"] for r in csv.DictReader(f)}


def _tracked() -> list[str]:
    out = subprocess.run(["git", "ls-files"], cwd=REPO, capture_output=True, text=True, check=True).stdout
    return out.splitlines()


def test_every_capture_row_names_a_manifest_sample():
    known = _manifest()
    with open(SAMPLES / "captures.csv", encoding="utf-8-sig") as f:
        unknown = sorted({r["sample_id"] for r in csv.DictReader(f)} - known.keys())
    assert not unknown, f"captures.csv rows for files no manifest row names: {unknown[:10]}"


def test_every_conversion_row_names_a_manifest_sample():
    known = _manifest()
    lines = (SAMPLES / "convert_log.csv").read_text(encoding="utf-8").splitlines()[1:]
    stems = {os.path.splitext(line.split(",", 1)[0].strip('"').replace("\\", "/").rsplit("/", 1)[-1])[0]
             for line in lines if line}
    unknown = sorted(stems - known.keys())
    assert not unknown, f"convert_log.csv rows for files no manifest row names: {unknown[:10]}"


def test_no_real_program_is_tracked():
    known = _manifest()
    bad = []
    for path in _tracked():
        parts = path.split("/")
        if path.startswith("samples/local/") or "Customer" in parts or "PROGRAMS" in parts:
            bad.append(path)
        elif path.lower().endswith((".l5x", ".l5k", ".acd")) and path.startswith("samples/"):
            stem = os.path.splitext(parts[-1])[0]
            if known.get(stem, "real_program") == "real_program":
                bad.append(path)
    assert not bad, f"tracked files that no generator wrote: {bad[:10]}"
