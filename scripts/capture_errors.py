"""Every capture that errored, routed to the open question that asked for it.

Step 2b of CLAUDE.md's capture sequence. Exists because a 31-row family with a
+10.5% systematic error sat unexamined for eight days: every one of its files
carried `error_count = n+1`, nobody could tell whether the rows were
trustworthy, and there was no place where that fact was written down against
the question the files were built to answer.

Two failure classes, both silent until now:

  BUILD ERRORS    the L5X imported and the project built, but Studio reported
                  errors. `actual_bytes` still gets filled in, so the row
                  looks like data. It may be fine (a benign warning counted as
                  an error) or it may mean part of the file never made it into
                  the controller, which silently inflates the model's apparent
                  over-prediction. Either way the row is SUSPECT, not bad, and
                  suspect rows must be labelled, not skipped.

  CONVERSION FAILURES   a committed generated file with no `ok` on record in
                  convert_log.csv. Step 2 already reports these; this step
                  additionally routes each one to its owning question.

The routing is by the `OQ-` identifier in the sample's own manifest
description, which is why every generator must name its question there. A row
whose owning question cannot be determined is reported as UNROUTED and is a
generator bug to fix at the source, not something to resolve by hand here.

THE GATE: for each question that owns errored rows, this script requires a
line in that question's OPEN_QUESTIONS.md entry of the form

    **CAPTURE ERRORS: <n> row(s)** ...

with <n> matching the current count. Exit code 1 if any question is missing
its line, has a stale count, or if any row is UNROUTED. That is what stops an
error being forgotten: the number cannot drift without failing this check.

Run: python scripts/capture_errors.py [--list]
"""

from __future__ import annotations

import argparse
import collections
import csv
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST = REPO_ROOT / "samples" / "manifest.csv"
RESOLVED_QUESTIONS = REPO_ROOT / "docs" / "RESOLVED_QUESTIONS.md"
OWNERS = REPO_ROOT / "samples" / "oq_owners.csv"
CONVERT_LOG = REPO_ROOT / "samples" / "convert_log.csv"
OPEN_QUESTIONS = REPO_ROOT / "docs" / "OPEN_QUESTIONS.md"

_OQ_RE = re.compile(r"OQ-[A-Z0-9][A-Z0-9-]*")
_GATE_RE = re.compile(r"\*\*CAPTURE ERRORS: (\d+) row\(s\)\*\*")


def _declared_owners() -> list[tuple[str, str]]:
    """Explicit sample-prefix -> question map, longest prefix first.

    A new generator names its question in the sample description and needs no
    entry here. This file exists for two cases the description cannot cover:
    a family whose question has since closed and whose errors belong to the
    successor, and a legacy family whose generator no longer exists to be
    edited. An explicit entry WINS over the description, because an incidental
    mention in prose is weaker evidence of ownership than a deliberate line.

    A prefix of the form `oq:OQ-OLD` reads as "any row whose description names
    OQ-OLD", which is how a closed question hands its errored rows to its
    successor without needing to know which sample families mention it.
    """
    if not OWNERS.exists():
        return []
    with open(OWNERS, newline="", encoding="utf-8-sig") as f:
        pairs = [(r["sample_id_prefix"], r["owning_oq"]) for r in csv.DictReader(f)]
    return sorted(pairs, key=lambda p: -len(p[0]))


_OWNERS_CACHE = _declared_owners()


_ALIASES = {p[3:]: oq for p, oq in _OWNERS_CACHE if p.startswith("oq:")}
_PREFIXES = [(p, oq) for p, oq in _OWNERS_CACHE if not p.startswith("oq:")]


def _owning_questions(row: dict) -> list[str]:
    sample_id = row.get("sample_id", "")
    for prefix, oq in _PREFIXES:
        if sample_id.startswith(prefix):
            return [oq]
    text = f"{row.get('description', '')} {row.get('notes', '')}"
    named = sorted(set(_OQ_RE.findall(text)))
    return sorted({_ALIASES.get(oq, oq) for oq in named})


def _errored_rows(rows: list[dict]) -> list[dict]:
    out = []
    for r in rows:
        count = (r.get("error_count") or "").strip()
        if count and count != "0":
            out.append(r)
    return out


def _conversion_failures(rows: list[dict]) -> list[dict]:
    """Committed generated files that were ATTEMPTED and did not reach `ok`.

    Last row per filename wins -- a later success supersedes an earlier
    failure. A file with no convert_log row at all is NOT a failure: it has
    simply never been submitted, which is the normal state of a batch built
    today. Conflating the two made every freshly generated file read as broken,
    which is exactly the kind of noise that trains people to ignore a report.
    """
    if not CONVERT_LOG.exists():
        return []
    status: dict[str, str] = {}
    with open(CONVERT_LOG, newline="", encoding="utf-8-sig") as f:
        for entry in csv.DictReader(f):
            # convert_log.csv is written on Windows, so its paths use
            # backslashes -- Path() on Linux treats those as ordinary
            # characters and Path(...).name returns the whole string, which
            # silently matched nothing and reported every committed file as
            # unconverted. Normalise the separator before splitting.
            name = (entry.get("l5x_path") or "").strip().replace("\\", "/")
            if name:
                status[Path(name).name] = (entry.get("status") or "").strip().lower()
    out = []
    for r in rows:
        path = (r.get("l5x_path") or "").replace("\\", "/")
        if "samples/generated/" not in path:
            continue
        recorded = status.get(Path(path).name)
        if recorded is not None and recorded != "ok":
            out.append(r)
    return out


def _entry_spans(text: str, heading: str) -> dict[str, str]:
    """Each question's own section of a questions document, keyed by its id."""
    spans: dict[str, str] = {}
    starts = list(re.finditer(heading, text, re.M))
    for i, m in enumerate(starts):
        end = starts[i + 1].start() if i + 1 < len(starts) else len(text)
        spans.setdefault(m.group(1), text[m.start():end])
    return spans


def _all_entry_spans() -> tuple[dict[str, str], dict[str, str]]:
    """Open entries and closed entries, separately.

    A CLOSED question can still own errored rows -- the rows outlive the
    question -- and those have to be written down where the question now
    lives, so RESOLVED_QUESTIONS.md is searched too rather than treating a
    closed question's errors as unrecordable.
    """
    open_spans = _entry_spans(
        OPEN_QUESTIONS.read_text(encoding="utf-8"),
        r"^\d+[a-z]?\. \*\*(OQ-[A-Z0-9][A-Z0-9-]*)\*\*")
    closed_spans: dict[str, str] = {}
    if RESOLVED_QUESTIONS.exists():
        closed_text = RESOLVED_QUESTIONS.read_text(encoding="utf-8")
        closed_spans = _entry_spans(closed_text, r"\*\*(OQ-[A-Z0-9][A-Z0-9-]*)\*\*")
    return open_spans, closed_spans


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true",
                    help="print every offending sample_id, not just the counts")
    args = ap.parse_args(argv)

    with open(MANIFEST, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    errored = _errored_rows(rows)
    unconverted = _conversion_failures(rows)

    by_oq: dict[str, list[tuple[str, str]]] = collections.defaultdict(list)
    unrouted: list[tuple[str, str]] = []
    for kind, group in (("build", errored), ("convert", unconverted)):
        for r in group:
            owners = _owning_questions(r)
            if owners:
                for oq in owners:
                    by_oq[oq].append((r["sample_id"], kind))
            else:
                unrouted.append((r["sample_id"], kind))

    no_text = [r["sample_id"] for r in errored if not (r.get("error_log") or "").strip()]

    print(f"{len(errored)} row(s) captured WITH build errors")
    print(f"{len(unconverted)} committed generated file(s) with no 'ok' in convert_log.csv")
    print(f"{len(no_text)} errored row(s) carry NO error text and cannot be diagnosed "
          f"without recapture\n")

    open_spans, closed_spans = _all_entry_spans()
    failures: list[str] = []

    print(f"{'open question':26s}{'rows':>6}  gate")
    for oq, items in sorted(by_oq.items(), key=lambda kv: -len(kv[1])):
        n = len(items)
        entry = open_spans.get(oq) or closed_spans.get(oq)
        where = "open" if oq in open_spans else "closed" if oq in closed_spans else "?"
        if entry is None:
            state = "NO ENTRY in either questions document"
            failures.append(
                f"{oq}: {n} errored row(s) and no entry anywhere to flag them against")
        else:
            m = _GATE_RE.search(entry)
            if m is None:
                state = f"MISSING the CAPTURE ERRORS line ({where} entry)"
                failures.append(
                    f'{oq}: add  **CAPTURE ERRORS: {n} row(s)**  to its entry')
            elif int(m.group(1)) != n:
                state = f"STALE count (entry says {m.group(1)}, actual {n})"
                failures.append(f"{oq}: CAPTURE ERRORS says {m.group(1)}, actual is {n}")
            else:
                state = f"ok ({where})"
        print(f"{oq:26s}{n:>6}  {state}")
        if args.list:
            for sample_id, kind in sorted(items):
                print(f"      {kind:8s} {sample_id}")

    if unrouted:
        print(f"\n{len(unrouted)} UNROUTED row(s) -- no OQ- identifier in the manifest "
              f"description, so the error has nowhere to be flagged. Fix the generator's "
              f"description at the source:")
        for sample_id, kind in sorted(unrouted):
            print(f"      {kind:8s} {sample_id}")
        failures.append(f"{len(unrouted)} errored row(s) name no owning question")

    if failures:
        print("\nFAILED -- an error with nowhere to be recorded is an error that gets "
              "forgotten:")
        for f in failures:
            print(f"  - {f}")
        return 1

    print("\nEvery errored capture is flagged against the question that asked for it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
