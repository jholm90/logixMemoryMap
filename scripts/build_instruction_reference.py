"""Build the local instruction reference from a Logix instruction manual sent over chat.

The manual is a tagged PDF, so its structure tree gives every paragraph and table in reading
order. One pass walks the tree, a second assembles each instruction section: its languages
(ladder / function block / ST, with the ST call form), the controller-family support rows,
and every operand or parameter table with the description column dropped, so what is kept is
the operand name, data type per controller family and format.

The output is the manual's own content in another shape, so it is written ONLY under the
gitignored samples/local/reference/ and never committed (CLAUDE.md, "Rockwell help
documentation is chat-only", the 2026-10-29 exception). The script refuses any other
destination.

Needs pdfplumber and pikepdf (not project dependencies):
    python -m pip install pdfplumber pikepdf

Run:
    python scripts/build_instruction_reference.py MANUAL.pdf [MANUAL2.pdf ...]
writes samples/local/reference/instructions.json and INSTRUCTION_REFERENCE.md (merged over
every manual given; a later manual's entry for the same mnemonic is added as another source).
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "samples" / "local" / "reference"

TITLE_PART = re.compile(r"(?P<name>[A-Z][^()\n]{1,80}?) \((?P<mn>[A-Z][A-Za-z0-9_]*)\)")
TITLE_JOIN = re.compile(r"^(?:\s*(?:,|and|, and|-|/)\s*)*$")
MNEMONIC = re.compile(r"^(?:[A-Z][A-Z0-9_]+|Is[A-Z]+)$")
LANG_HEADINGS = {"Ladder Diagram": "ladder", "Ladder Diagrams": "ladder", "Function Block": "fbd", "Function Block Diagram": "fbd",
                 "Structured Text": "st"}
RENAME = re.compile(r"mnemonic for this instruction changed from ?([A-Z_]+) to ([A-Z_]+)")
CALL = re.compile(r"^([A-Za-z][A-Za-z0-9_]*) ?\(")

# ---------------------------------------------------------------- pass 1: the page stream

_pdf = None


def _init(path: str) -> None:
    global _pdf
    import pdfplumber
    _pdf = pdfplumber.open(path)


def _page_chars(pn: int):
    by = collections.defaultdict(list)
    for c in _pdf.pages[pn].chars:
        if c.get("mcid") is not None:
            by[c["mcid"]].append((c["top"], c["x0"], c["x1"], c["text"]))
    return pn, dict(by)


def _text(chars) -> str:
    lines, cur, top, lastx = [], "", None, 0.0
    for t, x0, x1, ch in sorted(chars, key=lambda c: (round(c[0]), c[1])):
        if top is None or abs(round(t) - top) > 2:
            if cur:
                lines.append(cur)
            cur, top, lastx = ch, round(t), x1
            continue
        if x0 - lastx > 1.5 and not cur.endswith(" "):
            cur += " "
        cur += ch
        lastx = x1
    if cur:
        lines.append(cur)
    return "\n".join(ln.strip() for ln in lines)


def page_stream(path: Path) -> list[dict]:
    import pikepdf
    pdf = pikepdf.open(path)
    pidx = {p.objgen: i for i, p in enumerate(pdf.pages)}

    def node(el, pg):
        try:
            return ("mcid", int(el), pg)
        except (TypeError, ValueError):
            pass
        if not isinstance(el, pikepdf.Dictionary):
            return None
        if "/Pg" in el:
            pg = pidx.get(el.Pg.objgen, pg)
        kind = str(el.get("/Type", ""))
        if kind == "/MCR":
            return ("mcid", int(el.MCID), pg)
        if kind == "/OBJR":
            return None
        k = el.get("/K")
        kids = [] if k is None else [n for x in (k if isinstance(k, pikepdf.Array) else [k])
                                     if (n := node(x, pg))]
        return ("el", str(el.get("/S", ""))[1:], kids)

    k = pdf.Root.StructTreeRoot.K
    tops = [node(x, None) for x in (k if isinstance(k, pikepdf.Array) else [k])]
    chars = {}
    with Pool(initializer=_init, initargs=(str(path),)) as pool:
        for pn, by in pool.imap_unordered(_page_chars, range(len(pdf.pages)), chunksize=8):
            chars[pn] = by

    def mcids(n):
        return [(n[2], n[1])] if n[0] == "mcid" else [m for c in n[2] for m in mcids(c)]

    def text(ms):
        return _text([c for pg, m in ms for c in chars.get(pg, {}).get(m, [])])

    items = []

    def walk(n):
        if n is None or n[0] == "mcid":
            return
        _, s, kids = n
        if s == "Table":
            rows = []

            def rws(x):
                if x[0] != "el":
                    return
                if x[1] == "TR":
                    rows.append([text(mcids(c)) for c in x[2] if c[0] == "el" and c[1] in ("TD", "TH")])
                else:
                    for c in x[2]:
                        rws(c)
            rws(n)
            items.append({"t": "table", "pg": next((p for p, _ in mcids(n)), None), "rows": rows})
            return
        own = [(c[2], c[1]) for c in kids if c[0] == "mcid"]
        if own:
            s2 = text(own)
            if s2.strip():
                items.append({"t": "p", "ty": s, "pg": own[0][0], "s": s2})
        for c in kids:
            walk(c)

    for t in tops:
        walk(t)
    return items

# ---------------------------------------------------------------- pass 2: instruction sections


def _cell(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def _types(s: str) -> list[str]:
    return [t for t in re.split(r"[\s,]+", s.strip()) if t]


def _operand_table(rows: list[list[str]]) -> dict | None:
    """Keep operand / parameter name, data type column(s) and format; drop descriptions."""
    if not rows or len(rows[0]) < 2:
        return None
    head = [_cell(h) for h in rows[0]]
    low = [h.lower() for h in head]
    if not any(w in low[0] for w in ("operand", "parameter", "input", "output", "member", "name")):
        return None
    keep = [i for i, h in enumerate(low) if i == 0 or "type" in h or h.startswith("format")]
    if len(keep) < 2:
        return None
    out = {"header": [head[i] for i in keep], "rows": []}
    for r in rows[1:]:
        if len(r) < len(head):
            r = r + [""] * (len(head) - len(r))
        name = _cell(r[0])
        if not name:
            continue
        out["rows"].append([name] + [" ".join(_types(r[i])) if "type" in low[i] else _cell(r[i])
                                     for i in keep[1:]])
    return out if out["rows"] else None


def sections(items: list[dict], source: str) -> dict[str, dict]:
    starts = []
    for i, x in enumerate(items):
        if x["t"] != "p" or x["ty"] in ("Link", "Quote"):
            continue
        title = x["s"].strip()
        parts = list(TITLE_PART.finditer(title))
        if not parts or "\n" in title:
            continue
        gaps = [title[:parts[0].start()]] + [title[a.end():b.start()] for a, b in zip(parts, parts[1:])] \
            + [title[parts[-1].end():]]
        if not all(TITLE_JOIN.match(g) for g in gaps) or not all(MNEMONIC.match(m.group("mn")) for m in parts):
            continue
        if starts and i - starts[-1][0] < 20 and not any(
                y.get("s", "").strip() in ("Available Languages", "Available Instructions")
                for y in items[starts[-1][0]:i]):
            continue   # a title named inside the previous section's opening lines
        ahead = " ".join(y.get("s", "") for y in items[i + 1:i + 14] if y["t"] == "p")
        if "Available Languages" in ahead or "Available Instructions" in ahead or \
                "controllers and applications that support" in ahead or "This information applies" in ahead:
            starts.append((i, title, [m.group("mn") for m in parts]))
    out = {}
    for n, (i, name, mns) in enumerate(starts):
        end = starts[n + 1][0] if n + 1 < len(starts) else len(items)
        body = items[i + 1:end]
        e = {"name": name, "mnemonics": mns, "source": source, "page": (items[i]["pg"] or 0) + 1,
             "languages": {}, "st_call": None, "st_expression": False, "renamed_from": None,
             "applies_to": None, "support": [], "operands": []}
        lang_mode, operand_lang, phase = None, None, "head"
        for j, x in enumerate(body):
            if x["t"] == "table":
                rows = x["rows"]
                if rows and rows[0] and _cell(rows[0][0]).lower() == "architecture":
                    e["support"] = [[_cell(c) for c in r] for r in rows[1:]]
                    continue
                t = _operand_table(rows)
                if t:
                    t["language"] = operand_lang
                    ctx = next((y["s"] for y in reversed(body[max(0, j - 3):j]) if y["t"] == "p"), "")
                    t["context"] = _cell(ctx)[:80]
                    e["operands"].append(t)
                continue
            s = x["s"].strip()
            if s.startswith("This information applies to") and not e["applies_to"]:
                e["applies_to"] = _cell(s)
            if (m := RENAME.search(_cell(s))):
                e["renamed_from"] = m.group(1)
            if s in ("Available Languages", "Available Instructions"):
                if phase == "head":   # the first block only; a later one is another chapter's overview
                    phase = "lang"
                continue
            if s == "Operands" or s.startswith("Operands"):
                phase = "operands"
                operand_lang = None
                continue
            if s in LANG_HEADINGS:
                if phase == "lang":
                    lang_mode = LANG_HEADINGS[s]
                    e["languages"].setdefault(lang_mode, True)
                elif phase == "operands":
                    operand_lang = LANG_HEADINGS[s]
                continue
            if phase == "lang" and lang_mode:
                if s.lower().startswith(("this instruction is not available", "not available")):
                    e["languages"][lang_mode] = False
                elif lang_mode == "st" and e["languages"]["st"] is False and "as an operator" in s:
                    e["st_expression"] = True
                elif lang_mode == "st" and e["st_call"] is None and CALL.match(s):
                    e["st_call"] = _cell(s)
        if e["languages"]:
            for lang in ("ladder", "fbd", "st"):
                e["languages"].setdefault(lang, False)
        for mn in mns:
            if mn not in out:
                out[mn] = dict(e, mnemonic=mn)
            else:
                out[mn].setdefault("more", []).append({k: e[k] for k in ("name", "page", "operands")})
    return out

# ---------------------------------------------------------------- output


def _md(ref: dict[str, dict]) -> str:
    yn = {True: "yes", False: "no", None: "?"}
    lines = ["# Instruction reference (local only, never committed)", "",
             "Built by `scripts/build_instruction_reference.py` from the manuals sent over chat.", "",
             "| mnemonic | name | LD | FBD | ST | ST call | renamed from | source p. |", "|---|---|---|---|---|---|---|---|"]
    for mn in sorted(ref):
        e = ref[mn]
        lg = e["languages"]
        lines.append(f"| {mn} | {e['name']} | {yn[lg.get('ladder')]} | {yn[lg.get('fbd')]} | "
                     f"{yn[lg.get('st')]}{' (expression)' if e.get('st_expression') else ''} | "
                     f"{('`' + e['st_call'] + '`') if e['st_call'] else ''} | "
                     f"{e['renamed_from'] or ''} | {e['source']} {e['page']} |")
    for mn in sorted(ref):
        e = ref[mn]
        lines += ["", f"## {mn} — {e['name']}", ""]
        if e["applies_to"]:
            lines.append(e["applies_to"])
        for r in e["support"]:
            lines.append(f"- {' | '.join(r)}")
        for t in e["operands"]:
            lines += ["", f"**{t['language'] or 'operands'}** {('— ' + t['context']) if t['context'] else ''}", "",
                      "| " + " | ".join(t["header"]) + " |", "|" + "---|" * len(t["header"])]
            lines += ["| " + " | ".join(r) + " |" for r in t["rows"]]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("manuals", nargs="+", type=Path)
    ap.add_argument("--out", type=Path, default=OUT_DIR)
    args = ap.parse_args(argv)
    out = args.out.resolve()
    if out != OUT_DIR.resolve() and OUT_DIR.resolve() not in out.parents:
        print(f"refusing to write outside {OUT_DIR}: the reference is manual content and stays local")
        return 2
    out.mkdir(parents=True, exist_ok=True)
    ref_path = out / "instructions.json"
    ref = json.loads(ref_path.read_text()) if ref_path.exists() else {}
    for pdf in args.manuals:
        src = re.sub(r"[_ ].*$", "", pdf.stem).upper() or pdf.stem
        got = sections(page_stream(pdf), src)
        for mn, e in got.items():
            if mn in ref and ref[mn]["source"] != src:
                ref[mn].setdefault("more", []).append(e)
            else:
                ref[mn] = e
        print(f"{pdf.name}: {len(got)} instruction sections")
    ref_path.write_text(json.dumps(ref, indent=1))
    (out / "INSTRUCTION_REFERENCE.md").write_text(_md(ref))
    print(f"{len(ref)} instructions -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
