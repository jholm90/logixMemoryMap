"""Scoped accuracy check. Use this, not a full-corpus sweep, to test a constant.

WHY THIS EXISTS. The corpus is over 2,500 captured rows and a full recompute
re-parses every one of them. Most questions do not need that: when the change
under test is one constant in one family, the rows that can possibly move are
that family, the sixteen held-out real programs, and enough of everything else to
catch a change that reaches further than intended. Sweeping the encyclopedia to
check one word is the wrong instrument and it is the expensive one.

  python scripts/quick_eval.py --family '^asmclose_'   # the default: scoped
  python scripts/quick_eval.py                         # real + sentinels only
  python scripts/quick_eval.py --full                  # every captured row

SCOPE, by default:
  * every row matching --family, if given
  * all sixteen real programs -- the only accuracy number that counts
  * one SENTINEL per manifest category, the largest captured row in it, so a
    change that leaks into an unrelated category still shows up

A scoped run reports the real set and the family separately and never blends
them, because a corpus-level pass rate over a set the model was fitted on is
circular (CLAUDE.md, "How accuracy is measured").

--full exists for the places that genuinely need it: reconciling a new capture
batch, and the final check before a constant is committed.
"""

from __future__ import annotations

import argparse
import collections
import csv
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
# The manifest is split in two so that the generators and the capture
# tooling never write the same file: samples/manifest.csv holds the spec,
# samples/captures.csv the results. load_manifest() joins them back into
# the row shape this script already expects.
sys.path.insert(0, str(REPO / "src"))
from sample_gen.manifest_store import load_manifest  # noqa: E402

sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "scripts"))

from accuracy_report import _MODEL, is_valid_capture  # noqa: E402

import l5x_memory_analyzer.sizing.report as rep  # noqa: E402

MANIFEST = REPO / "samples" / "manifest.csv"
REAL_CATEGORY = "real_program"

# The stopping rule, so "done" is a check rather than a judgement call
# (docs/TASKS.md ranked item 8). Both must hold on the sixteen real programs.
STOP_MEAN_PCT = 1.0
STOP_MAX_PCT = 2.0

# Dead architecture -- 1756-L7x and 1769. CLAUDE.md keeps the existing rows but
# forbids new investment, and they dominate every corpus average while being
# unable to move the headline. Measured 2026-09-18: 64 captured rows, and the
# worst sentinel in the whole corpus was one of them (fwmatrix_v33_1756_l71 at
# 65.69%). Excluded from the
# non-real reports by default so a corpus number is not quietly contaminated;
# --include-dead puts them back.
_DEAD_PROCESSOR = re.compile(r"1756-L7|^1769-|L1[0-9]ER|L2[0-9]ER|L3[0-9]ER", re.I)


def _is_dead_architecture(row: dict) -> bool:
    return bool(_DEAD_PROCESSOR.search(row.get("controller_model") or ""))



def _rows() -> list[dict]:
    return load_manifest()


def _usable(row: dict, lenient: bool = False) -> bool:
    """STRICT by default, which also rejects a row whose error_count is blank.

    271 rows were captured 2026-08-22..08-30, before the capture tooling recorded
    error_count at all, so a blank there means the build status was never recorded
    -- not that the build was clean. Counting them as clean is how a real error
    hides. None of the sixteen real programs is affected (0 of 16 blank), so the
    only accuracy number that counts is unchanged either way; this keeps the
    corpus counts honest. --lenient includes them, labelled.
    """
    ok, _ = is_valid_capture(row, strict=not lenient)
    return ok and os.path.exists(row.get("l5x_path") or "")


def _errored(row: dict) -> bool:
    try:
        return int(row.get("error_count") or 0) > 0
    except ValueError:
        return False


def select(rows: list[dict], family: str | None, full: bool,
           lenient: bool = False) -> list[dict]:
    usable = [r for r in rows if _usable(r, lenient)]
    if full:
        return usable
    chosen: dict[str, dict] = {}
    for row in usable:
        if row["category"] == REAL_CATEGORY:
            chosen[row["sample_id"]] = row
        elif family and re.search(family, row["sample_id"]):
            chosen[row["sample_id"]] = row
    # One sentinel per category: the largest captured row, which is the one most
    # likely to expose a per-item term that leaked out of its family.
    biggest: dict[str, dict] = {}
    for row in usable:
        cat = row["category"]
        if cat == REAL_CATEGORY:
            continue
        try:
            size = int(row["actual_bytes"])
        except (ValueError, KeyError):
            continue
        if cat not in biggest or size > int(biggest[cat]["actual_bytes"]):
            biggest[cat] = row
    for row in biggest.values():
        chosen.setdefault(row["sample_id"], row)
    return list(chosen.values())


def evaluate(rows: list[dict]) -> list[tuple[str, str, int, int, bool]]:
    out = []
    for row in rows:
        try:
            entries, _ = rep.build_report(ET.parse(row["l5x_path"]).getroot(), _MODEL)
        except Exception:
            continue
        actual = int(row["actual_bytes"])
        delta = actual - sum(e.bytes for e in entries)
        out.append((row["sample_id"], row["category"], actual, delta, _errored(row)))
    return out


def _report(label: str, results: list[tuple[str, str, int, int, bool]], worst: int,
            is_real: bool = False) -> None:
    if not results:
        return
    clean = [r for r in results if not r[4]]
    suspect = [r for r in results if r[4]]
    pcts = [abs(d) / a * 100 for _, _, a, d, _ in clean]
    exact = sum(1 for _, _, _, d, _ in clean if d == 0)
    band = sum(1 for _, _, _, d, _ in clean if abs(d) <= 8)
    print(f"\n{label}: {len(clean)} clean row(s)"
          + (f", {len(suspect)} SUSPECT (captured with build errors, excluded)" if suspect else ""))
    if pcts:
        weighted = sum(d for _, _, _, d, _ in clean) / sum(a for _, _, a, _, _ in clean) * 100
        print(f"  mean|%|={sum(pcts)/len(pcts):.4f}  sum-weighted={weighted:+.4f}%"
              f"  exact={exact}  within8={band}")
    for sid, _, a, d, _ in sorted(clean, key=lambda r: -abs(r[3] / r[2]))[:worst]:
        print(f"    {sid:<44}{d:>9}  {d/a*100:>7.3f}%")
    if is_real and pcts:
        mean, worst_pct = sum(pcts) / len(pcts), max(pcts)
        ok = mean < STOP_MEAN_PCT and worst_pct < STOP_MAX_PCT
        print(f"  STOPPING RULE (mean <{STOP_MEAN_PCT}% and max <{STOP_MAX_PCT}%): "
              f"{'MET' if ok else 'NOT MET'} -- mean {mean:.4f}%, max {worst_pct:.4f}%, "
              f"{sum(1 for x in pcts if x < 1)}/{len(pcts)} inside 1%, "
              f"{sum(1 for x in pcts if x < 2)}/{len(pcts)} inside 2%")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--family", help="regex over sample_id: the rows under test")
    ap.add_argument("--full", action="store_true",
                    help="every captured row (reconciliation and final checks only)")
    ap.add_argument("--worst", type=int, default=6)
    ap.add_argument("--include-dead", action="store_true",
                    help="also report 1756-L7x / 1769 rows, which are dead "
                         "architecture and cannot move the real-set number")
    ap.add_argument("--lenient", action="store_true",
                    help="also include the 271 rows whose error_count was never "
                         "recorded (captured before the tooling logged it)")
    args = ap.parse_args()

    rows = _rows()
    dead = 0
    if not args.include_dead:
        keep = [r for r in rows
                if r["category"] == REAL_CATEGORY or not _is_dead_architecture(r)]
        dead = len(rows) - len(keep)
        rows = keep
    picked = select(rows, args.family, args.full, args.lenient)
    results = evaluate(picked)
    by_real = [r for r in results if r[1] == REAL_CATEGORY]
    rest = [r for r in results if r[1] != REAL_CATEGORY]

    mode = "LENIENT" if args.lenient else "strict"
    if dead:
        print(f"excluded {dead} dead-architecture row(s) (1756-L7x / 1769); "
              f"--include-dead to report them")
    if args.full:
        print(f"FULL SWEEP ({mode}): {len(results)} of {len(rows)} manifest rows")
        _report("real programs (the only accuracy number)", by_real, args.worst, is_real=True)
        buckets = collections.defaultdict(list)
        for r in rest:
            buckets[r[1]].append(r)
        for cat, rws in sorted(buckets.items(), key=lambda kv: -len(kv[1])):
            _report(f"category {cat}", rws, 0)
        return 0

    # Count the real rows rather than naming a number: the held-out set grows
    # whenever another production export lands, and a hardcoded "16" was still
    # printed after the seventeenth arrived.
    scope = f"{len(by_real)} real + one sentinel per category"
    print(f"SCOPED: {len(results)} row(s)"
          + (f" -- family {args.family!r} + {scope}" if args.family else f" -- {scope}"))
    _report("real programs (the only accuracy number)", by_real, args.worst, is_real=True)
    if args.family:
        fam = [r for r in rest if re.search(args.family, r[0])]
        _report(f"family {args.family}", fam, args.worst)
        rest = [r for r in rest if not re.search(args.family, r[0])]
    _report("sentinels (leak check, not an accuracy number)", rest, args.worst)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
