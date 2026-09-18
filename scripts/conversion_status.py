"""CLAUDE.md step 2: every committed generated L5X against its conversion status.

Cross-references `samples/generated/**/*.L5X` with the LAST recorded row per
filename in `samples/convert_log.csv` -- last row wins, so a later `ok`
supersedes an earlier `FAILED` and, just as importantly, a later `FAILED`
supersedes an earlier `ok`. Any committed file with no `ok` on record is listed
explicitly; the rule is that it is never silently dropped from a summary.

Three outcomes, and they need different handling:

  FAILED        the file was submitted and Studio refused it. Runs lint over it,
                because lint has grown a lot and often now names the cause that
                convert_log does not -- convert_log's message only ever says
                "The Import was cancelled due to errors ... See error log".
  NO RECORD     never submitted. Usually just generated after the last conversion
                run, not a defect.
  STALE CAPTURE a file whose last status is FAILED but whose manifest row still
                carries actual_bytes. That capture came from content the repo no
                longer holds and must not be used -- the same failure class as
                asmclose_1756_ob32_rackaliased, where a note said "cleared" and
                the values were still sitting there.

This existed as a written step with no tool, which is why it went unrun.

  python scripts/conversion_status.py            # summary
  python scripts/conversion_status.py --list     # every filename
"""

from __future__ import annotations

import argparse
import collections
import csv
import glob
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
# The manifest is split in two so that the generators and the capture
# tooling never write the same file: samples/manifest.csv holds the spec,
# samples/captures.csv the results. load_manifest() joins them back into
# the row shape this script already expects.
sys.path.insert(0, str(REPO / "src"))
from sample_gen.manifest_store import load_manifest  # noqa: E402

sys.path.insert(0, str(REPO / "src"))

from sample_gen.lint import lint_l5x  # noqa: E402

CONVERT_LOG = REPO / "samples" / "convert_log.csv"
MANIFEST = REPO / "samples" / "manifest.csv"


def _basename(path: str) -> str:
    """convert_log stores Windows paths, so Path().name will not split them."""
    return re.split(r"[\\/]", path)[-1]


def _family(name: str) -> str:
    match = re.match(r"([a-z0-9]+?)_", name)
    return match.group(1) if match else name


def last_status() -> dict[str, str]:
    status: dict[str, str] = {}
    with open(CONVERT_LOG, encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            status[_basename(row["l5x_path"])] = row["status"]
    return status


def manifest_rows() -> dict[str, dict]:
    return {row["sample_id"]: row for row in load_manifest()}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--list", action="store_true", help="name every affected file")
    args = ap.parse_args()

    status = last_status()
    rows = manifest_rows()
    committed = {
        _basename(p): p
        for p in glob.glob(str(REPO / "samples" / "generated" / "**" / "*.L5X"), recursive=True)
    }

    ok, failed, missing, stale = [], [], [], []
    for name in sorted(committed):
        state = status.get(name)
        if state is None:
            missing.append(name)
            continue
        if state == "ok":
            ok.append(name)
            continue
        failed.append(name)
        row = rows.get(name[:-4])
        if row and (row.get("actual_bytes") or "").strip():
            stale.append((name[:-4], row["actual_bytes"]))

    print(f"committed generated L5X : {len(committed)}")
    print(f"  last status ok        : {len(ok)}")
    print(f"  last status FAILED    : {len(failed)}")
    print(f"  no convert_log record : {len(missing)}")

    if failed:
        print("\nFAILED -- submitted and refused. Lint diagnosis where it has one:")
        by_diag = collections.defaultdict(list)
        for name in failed:
            text = Path(committed[name]).read_text(encoding="utf-8", errors="replace")
            kinds = tuple(sorted({f.kind for f in lint_l5x(text)})) or ("(lint clean)",)
            by_diag[kinds].append(name)
        for kinds, names in sorted(by_diag.items(), key=lambda kv: -len(kv[1])):
            fams = dict(collections.Counter(_family(n) for n in names).most_common())
            print(f"  [{len(names):>3}] {fams}")
            print(f"        {', '.join(kinds)}")
            if args.list:
                for n in names:
                    print(f"          {n}")

    if missing:
        fams = dict(collections.Counter(_family(n) for n in missing).most_common())
        print(f"\nNO RECORD -- never submitted: {fams}")
        if args.list:
            for n in missing:
                print(f"    {n}")

    if stale:
        print(f"\nSTALE CAPTURE -- last status FAILED but actual_bytes is present ({len(stale)}).")
        print("  That capture describes content the repo no longer holds. Clear it.")
        for sample_id, actual in stale:
            print(f"    {sample_id:<48} actual={actual}")

    return 1 if stale else 0


if __name__ == "__main__":
    raise SystemExit(main())
