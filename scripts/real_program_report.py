"""The customer-program report: every real program, priced by the current engine.

Reports are on customer programs only, never on generated test files, and always from the
engine as it stands (CLAUDE.md, "Reports"). Two outputs:

  docs/REAL_PROGRAM_REPORT.md                public: labels only (realprog_NN, RS-NN), processor,
                                             firmware, engine, reading, error; a dated history
                                             row per run, so the file is a log
  samples/local/reports/real_program_report_<date>.html / .csv
                                             local: the same rows with file and controller names

The label-to-file tables are the gitignored samples/local/aliases.csv (realprog_NN) and
samples/local/safety_aliases.csv (RS-NN). Standard readings come from samples/captures.csv
(load_manifest); safety-controller readings by label from samples/real_safety_readings.csv.
The public text is checked against every file name, controller name and name fragment in
those tables, and nothing is written if one appears.

  python scripts/real_program_report.py
"""

from __future__ import annotations

import csv
import datetime as dt
import hashlib
import html
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LOCAL = REPO / "samples" / "local"
PUBLIC = REPO / "docs" / "REAL_PROGRAM_REPORT.md"
SAFETY_READINGS = REPO / "samples" / "real_safety_readings.csv"
sys.path.insert(0, str(REPO / "src"))

from sample_gen.manifest_store import load_manifest  # noqa: E402

STOP_MEAN_PCT, STOP_MAX_PCT = 1.0, 2.0
PROTECTED_EXCLUSION_THRESHOLD = 10  # the same rule as quick_eval.py
SAFETY_PROCESSOR = re.compile(r"-L\w*S[23]?$", re.I)
HISTORY_HEADER = "| date | engine | standard: counted | mean | worst | in 1% | in 2% | 1756/5069 safety ctl standard: mean / worst | 1769 standard: mean / worst | safety partition: mean / worst |"
# Words a file name may contain that this report also uses on its own.
GENERIC = {"safety", "main", "line", "real", "export"}


def price(path: str) -> dict:
    import xml.etree.ElementTree as ET
    from l5x_memory_analyzer.sizing.constants import load_memory_model
    from l5x_memory_analyzer.sizing.report import build_report
    from l5x_memory_analyzer.sizing.safety import build_safety_report, has_safety_partition
    raw = Path(path).read_bytes()
    root = ET.fromstring(raw)
    model = load_memory_model()
    ctl = root.find("Controller")
    std = sum(e.bytes for e in build_report(root, model)[0])
    saf = sum(e.bytes for e in build_safety_report(root, model)[0]) if has_safety_partition(root) else None
    text = raw.decode("utf-8", errors="ignore")
    return {"std": std, "saf": saf, "controller": ctl.get("Name") or "", "proc": ctl.get("ProcessorType") or "",
            "fw": f'{ctl.get("MajorRev")}.{ctl.get("MinorRev")}', "protected": text.count("<EncodedData"),
            "sfc": text.count('Type="SFC"'), "sha12": hashlib.sha256(raw).hexdigest()[:12]}


def pct(est: int | None, act: int | None) -> float | None:
    return (est - act) / act * 100 if est is not None and act else None


def stats(errs: list[float]) -> dict:
    a = [abs(e) for e in errs]
    if not a:
        return {}
    return {"n": len(a), "mean": sum(a) / len(a), "worst": max(errs, key=abs),
            "in1": sum(x < 1 for x in a), "in2": sum(x < 2 for x in a)}


def fmt_pct(x: float | None, places: int = 2) -> str:
    return "" if x is None else f"{x:+.{places}f}%".replace("-", "−")


def fmt_n(x: int | None) -> str:
    return "" if x is None else f"{x:,}"


def mean_worst(s: dict) -> str:
    return f"{s['mean']:.2f}% / {fmt_pct(s['worst'])}" if s else "—"


def find_file(name: str) -> Path | None:
    hits = sorted(p for p in LOCAL.rglob(name) if "reports" not in p.parts)
    return hits[0] if hits else None


def basis_word(basis: str) -> str:
    b = basis.lower()
    if b.startswith("inferred"):
        return "file inferred from platform"
    if b.startswith("new"):
        return "read from this file"
    return "file matched by reading"


def forbidden_tokens(names: list[str]) -> set[str]:
    out = set()
    for n in names:
        stem = re.sub(r"\.L5X$", "", n, flags=re.I)
        out.add(stem.lower())
        for chunk in re.findall(r"[A-Za-z]{4,}|\d{5,}", stem):
            if chunk.lower() not in GENERIC:
                out.add(chunk.lower())
    return out


def leaks(text: str, tokens: set[str]) -> list[str]:
    low = text.lower()
    return sorted(t for t in tokens if re.search(rf"(?<![a-z0-9]){re.escape(t)}(?![a-z0-9])", low))


def engine_ref() -> str:
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO, capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain", "--", "src"], cwd=REPO, capture_output=True, text=True).stdout.strip()
    return f"`{head}`" + (" + uncommitted engine changes" if dirty else "")


def old_history() -> list[str]:
    if not PUBLIC.exists():
        return []
    lines = PUBLIC.read_text(encoding="utf-8").splitlines()
    if HISTORY_HEADER not in lines:
        return []
    i = lines.index(HISTORY_HEADER) + 2
    rows = []
    while i < len(lines) and lines[i].startswith("|"):
        rows.append(lines[i])
        i += 1
    return rows


def main() -> int:
    from sample_gen.progress import run
    aliases = list(csv.DictReader(open(LOCAL / "aliases.csv", encoding="utf-8")))
    safety_aliases = list(csv.DictReader(open(LOCAL / "safety_aliases.csv", encoding="utf-8")))
    manifest = {r["sample_id"]: r for r in load_manifest() if r["category"] == "real_program"}
    safety_read = {r["label"]: r for r in csv.DictReader(open(SAFETY_READINGS, encoding="utf-8"))}

    jobs, missing = [], []
    for a in aliases:
        f = LOCAL / f"{a['label']}.L5X"
        f = f if f.exists() else find_file(a["file"])
        (jobs.append((a["label"], str(f))) if f else missing.append(a["label"]))
    for a in safety_aliases:
        f = find_file(a["file"])
        (jobs.append((a["label"], str(f))) if f else missing.append(a["label"]))
    live = run(jobs, price, label="customer programs", item_timeout=900, total_timeout=3600)

    rs_of = {r["standard_from"]: lab for lab, r in safety_read.items() if r.get("standard_from")}
    std_rows, saf_rows = [], []
    for a in aliases:
        lab = a["label"]
        if lab not in live or lab in rs_of:
            continue  # a safety controller's standard reading is reported under its RS label
        p, m = live[lab], manifest.get(lab, {})
        act = int(m["actual_bytes"]) if (m.get("actual_bytes") or "").isdigit() else None
        counted, why = True, ""
        if SAFETY_PROCESSOR.search(p["proc"]):
            counted, why = False, "safety processor"
        elif p["protected"] >= PROTECTED_EXCLUSION_THRESHOLD:
            counted, why = False, f"{p['protected']} source-protected blocks"
        elif act is None:
            counted, why = False, "no reading"
        std_rows.append({"label": lab, **p, "act": act, "err": pct(p["std"], act), "counted": counted, "why": why,
                         "basis": basis_word(a.get("basis", "")), "file": a["file"]})
    for a in safety_aliases:
        lab = a["label"]
        if lab not in live:
            continue
        p, r = live[lab], safety_read.get(lab, {})
        src = r.get("standard_from") or ""
        act = (int(manifest[src]["actual_bytes"]) if src in manifest and manifest[src].get("actual_bytes")
               else int(r["standard_bytes"]) if (r.get("standard_bytes") or "").isdigit() else None)
        sact = int(r["safety_bytes"]) if (r.get("safety_bytes") or "").isdigit() else None
        group = "1769" if p["proc"].startswith("1769") else "1756/5069"
        note = r.get("note", "")
        counted = r.get("counted_standard", "yes") == "yes" and act is not None
        saf_rows.append({"label": lab, **p, "act": act, "err": pct(p["std"], act), "sact": sact,
                         "serr": pct(p["saf"], sact), "group": group, "counted": counted, "note": note,
                         "counted_safety": r.get("counted_safety", "yes") == "yes" and sact is not None,
                         "same_as": src, "file": a["file"]})

    s_std = stats([r["err"] for r in std_rows if r["counted"]])
    s_ctl = stats([r["err"] for r in saf_rows if r["counted"] and r["group"] == "1756/5069" and r["err"] is not None])
    s_1769 = stats([r["err"] for r in saf_rows if r["counted"] and r["group"] == "1769" and r["err"] is not None])
    s_saf = stats([r["serr"] for r in saf_rows if r["counted_safety"]])
    weighted = (sum(r["std"] - r["act"] for r in std_rows if r["counted"])
                / sum(r["act"] for r in std_rows if r["counted"]) * 100)
    met = s_std["mean"] < STOP_MEAN_PCT and abs(s_std["worst"]) < STOP_MAX_PCT
    today = dt.date.today().isoformat()
    ref = engine_ref()

    L = [
        "# Real-program report",
        "",
        "Every customer program on file, priced by the engine as it stands, against its controller's",
        "Capacity reading. Generated by `scripts/real_program_report.py`; customer programs only,",
        "never the generated test corpus. Programs are named by label only (`realprog_NN` for a",
        "standard-processor export, `RS-NN` for a safety-controller export); the names stay in the",
        "gitignored `samples/local/`. Error is engine minus reading, as a share of the reading:",
        "negative means the engine predicts too little.",
        "",
        f"**Run {today}, engine {ref}.**",
        "",
        "## Summary",
        "",
        f"- **Standard processors, counted: {s_std['n']} programs, mean {s_std['mean']:.3f}%, worst "
        f"{fmt_pct(s_std['worst'], 3)}**, {s_std['in1']}/{s_std['n']} inside 1%, {s_std['in2']}/{s_std['n']} "
        f"inside 2%, sum-weighted {fmt_pct(weighted, 3)}. Stopping rule (mean under {STOP_MEAN_PCT:g}% and "
        f"worst under {STOP_MAX_PCT:g}%): **{'MET' if met else 'NOT MET'}**.",
    ]
    for r in std_rows:
        if not r["counted"]:
            L.append(f"- Not counted: {r['label']} ({r['why']}), {fmt_pct(r['err'])}.")
    L += [
        f"- **Safety controllers, standard partition** (1756 / 5069, counted): {mean_worst(s_ctl)} on "
        f"{s_ctl.get('n', 0)} programs.",
        f"- **1769 Compact GuardLogix, standard partition**: {mean_worst(s_1769)} on {s_1769.get('n', 0)} programs.",
        f"- **Safety partition** (every safety controller with a safety reading): {mean_worst(s_saf)} on "
        f"{s_saf.get('n', 0)} programs.",
    ]
    s_saf1769 = stats([r["serr"] for r in saf_rows if r["counted_safety"] and r["group"] == "1769"])
    s_saf_other = stats([r["serr"] for r in saf_rows if r["counted_safety"] and r["group"] != "1769"])
    L.append(f"  Of those, 1756 / 5069: {mean_worst(s_saf_other)} on {s_saf_other.get('n', 0)}; "
             f"1769: {mean_worst(s_saf1769)} on {s_saf1769.get('n', 0)}.")
    if missing:
        L.append(f"- Labelled but not on this machine, not priced: {', '.join(missing)}.")
    L += [
        "",
        "## Standard processors",
        "",
        "| label | processor | firmware | engine | reading | error | reading | counted |",
        "|---|---|---|---:|---:|---:|---|---|",
    ]
    for r in sorted(std_rows, key=lambda r: r["label"]):
        L.append(f"| {r['label']} | {r['proc']} | v{r['fw']} | {fmt_n(r['std'])} | {fmt_n(r['act'])} | "
                 f"{fmt_pct(r['err'])} | {r['basis']} | {'yes' if r['counted'] else 'no: ' + r['why']} |")
    L += [
        "",
        "## Safety controllers",
        "",
        "Two readings each on the Capacity tab: the standard partition and the safety partition.",
        "",
        "| label | processor | firmware | standard engine | standard reading | error | safety engine | safety reading | error | note |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for r in sorted(saf_rows, key=lambda r: (r["group"] != "1756/5069", int(re.sub(r"\D", "", r["label"])), r["label"])):
        note = "; ".join(x for x in (f"standard reading is {r['same_as']}'s" if r["same_as"] else "",
                                     r["note"], "" if r["counted"] else "standard figure not counted",
                                     "" if r["counted_safety"] or r["sact"] is None else "safety figure not counted") if x)
        L.append(f"| {r['label']} | {r['proc']} | v{r['fw']} | {fmt_n(r['std'])} | {fmt_n(r['act'])} | "
                 f"{fmt_pct(r['err'])} | {fmt_n(r['saf'])} | {fmt_n(r['sact'])} | {fmt_pct(r['serr'], 1)} | {note} |")
    row = (f"| {today} | {ref} | {s_std['n']} | {s_std['mean']:.3f}% | {fmt_pct(s_std['worst'], 3)} | "
           f"{s_std['in1']} | {s_std['in2']} | {mean_worst(s_ctl)} | {mean_worst(s_1769)} | {mean_worst(s_saf)} |")
    history = [h for h in old_history() if not h.startswith(f"| {today} | {ref} |")] + [row]
    L += [
        "",
        "## History",
        "",
        "One row per run at a given engine commit, oldest first. A row is the engine of that day on the",
        "programs and readings on file that day.",
        "",
        HISTORY_HEADER,
        "|---|---|---:|---:|---:|---:|---:|---|---|---|",
        *history,
        "",
    ]
    public = "\n".join(L)

    names = [a["file"] for a in aliases] + [a["file"] for a in safety_aliases]
    names += [p["controller"] for p in live.values() if p["controller"]]
    bad = leaks(public, forbidden_tokens(names))
    if bad:
        print(f"REFUSED: the public report would name {len(bad)} customer token(s): {bad[:10]}", file=sys.stderr)
        return 1
    PUBLIC.write_text(public, encoding="utf-8")

    out = LOCAL / "reports"
    out.mkdir(exist_ok=True)
    cols = ["label", "file", "controller", "proc", "fw", "std", "act", "err", "saf", "sact", "serr", "counted", "why", "note"]
    with open(out / f"real_program_report_{today}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in std_rows + saf_rows:
            w.writerow({k: (f"{r[k]:.3f}" if isinstance(r.get(k), float) else r.get(k, "")) for k in cols})
    cell = lambda v: html.escape("" if v is None else (f"{v:+.2f}%" if isinstance(v, float) else f"{v:,}" if isinstance(v, int) and not isinstance(v, bool) else str(v)))
    trs = "".join("<tr>" + "".join(f"<td>{cell(r.get(k))}</td>" for k in cols) + "</tr>" for r in std_rows + saf_rows)
    (out / f"real_program_report_{today}.html").write_text(
        f"<!doctype html><meta charset=utf-8><title>Customer programs {today}</title>"
        f"<style>body{{font:14px sans-serif;margin:16px}}td,th{{padding:3px 8px;border-bottom:1px solid #ccc;text-align:right}}"
        f"td:nth-child(-n+5){{text-align:left}}</style><h1>Customer programs, {today}, engine {html.escape(ref)}</h1>"
        f"<p>Local copy with names. Public copy: docs/REAL_PROGRAM_REPORT.md.</p><table><tr>"
        + "".join(f"<th>{c}</th>" for c in cols) + f"</tr>{trs}</table>", encoding="utf-8")
    print(public)
    return 0


if __name__ == "__main__":
    sys.exit(main())
