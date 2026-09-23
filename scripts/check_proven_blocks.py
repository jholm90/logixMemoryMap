"""Check that every Kinetix block in a generated file has a clean capture behind it.

A generated file can pass lint and convert cleanly and still fail Build: both
earlier modulerack_kinetix_full_bus builds did, twice, on drive blocks that had
already been proven to fail. This check asks a narrower, harder question than
lint: has this exact block -- every 2198 module and every AXIS_CIP_DRIVE tag,
compared with names, addresses, MotionModule and AxisID normalised away --
appeared in a file that captured with ZERO build errors?

A block with no such match is not necessarily wrong, but it is unproven, and an
unproven Kinetix block is the shape that has cost the most failed captures.

Run: python scripts/check_proven_blocks.py <file.L5X> [...]
Exit status is non-zero if any block has no clean match.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from sample_gen.manifest_store import load_manifest  # noqa: E402

_MODULE = re.compile(r'<Module Name="[^"]*" CatalogNumber="2198-[^"]*".*?</Module>', re.S)
_AXIS = re.compile(r'<Tag Name="[^"]*" TagType="Base" DataType="AXIS_CIP_DRIVE".*?</Tag>', re.S)


def blocks(text: str) -> list[str]:
    return _MODULE.findall(text) + _AXIS.findall(text)


def normalise(block: str) -> str:
    for attr in ("Name", "Address", "MotionModule", "AxisID"):
        block = re.sub(rf'{attr}="[^"]*"', f'{attr}=""', block)
    return re.sub(r"\s+", " ", block)


def proven_blocks() -> dict[str, str]:
    """Normalised block -> the first zero-error capture that contains it."""
    proven: dict[str, str] = {}
    for row in load_manifest(resolve_local=False):
        if not (row.get("actual_bytes") or "").strip():
            continue
        if (row.get("error_count") or "").strip() != "0":
            continue
        path = REPO_ROOT / row["l5x_path"]
        if "samples/generated/" not in row["l5x_path"] or not path.exists():
            continue
        text = path.read_text(encoding="utf-8-sig", errors="ignore")
        if "2198-" not in text and "AXIS_CIP_DRIVE" not in text:
            continue
        for block in blocks(text):
            proven.setdefault(normalise(block), row["sample_id"])
    return proven


def check(paths: list[Path], proven: dict[str, str]) -> list[str]:
    problems = []
    for path in paths:
        for block in blocks(path.read_text(encoding="utf-8-sig", errors="ignore")):
            if normalise(block) not in proven:
                name = re.search(r'Name="([^"]*)"', block).group(1)
                problems.append(f"{path.name}: {name} has no zero-error capture behind it")
    return problems


def main(argv: list[str]) -> int:
    paths = [Path(a) for a in argv[1:]]
    if not paths:
        print(__doc__)
        return 2
    proven = proven_blocks()
    problems = check(paths, proven)
    for p in problems:
        print(p)
    print(f"{len(paths)} file(s), {len(proven)} proven block shapes, {len(problems)} unproven block(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
