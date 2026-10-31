"""Layer files: copies of a real export with whole top-level sections removed.

Owner's decision, 2026-10-31 (CLAUDE.md, "Layer files"): Claude builds the cut-down programs the
deletion ladder needs; the owner only runs them. The export is never modified. Each layer is
written by text slicing, with no XML round trip, so every CDATA section and every byte outside
the removed spans is the export's own. Layers, each from the one before, in dependency order so
nothing left behind refers to anything removed:

  L1_noprogs    every program removed, and every task's program list (the tasks stay)
  L2_notags     every controller-scope tag removed
  L3_nomodules  every module but the controller's own ("Local")
  L4_nounused   every data type that no AOI uses, directly or through another type
  L5_empty      every AOI and every data type

Sections that only point at removed content (watch lists, parameter connections and the
like) are emptied in every layer; none of them is downloaded.

Customer content: input and output both under samples/local/, never anywhere else.

Run: python scripts/real_layers.py samples/local/<export>.L5X [...]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LOCAL = REPO / "samples" / "local"
OUT = LOCAL / "layers"

_TOKEN = re.compile(rb'<!\[CDATA\[.*?\]\]>|<!--.*?-->|<\?.*?\?>|<(/?)([A-Za-z_][\w.:-]*)\b((?:[^>"\']|"[^"]*"|\'[^\']*\')*?)(/?)>', re.S)
# Present in exports, never downloaded, and refer to tags or programs by name.
_EMPTIED_ALWAYS = ("Trends", "QuickWatchLists", "ParameterConnections", "DataLogs")


def elements(text: bytes):
    """(name, depth, start, end, attrs) for every element; depth 0 is the root."""
    stack: list[tuple[bytes, int, bytes]] = []
    for m in _TOKEN.finditer(text):
        if m.group(2) is None:
            continue
        close, name, attrs, selfclose = m.group(1), m.group(2), m.group(3), m.group(4)
        if close:
            open_name, start, a = stack.pop()
            assert open_name == name, (open_name, name, m.start())
            yield name.decode(), len(stack), start, m.end(), a
        elif selfclose:
            yield name.decode(), len(stack), m.start(), m.end(), attrs
        else:
            stack.append((name, m.start(), attrs))
    assert not stack, "unbalanced export"


def _cut(text: bytes, spans: list[tuple[int, int, bytes]]) -> bytes:
    """Replace each (start, end, replacement) span; spans must not overlap."""
    out, pos = [], 0
    for start, end, rep in sorted(spans):
        assert start >= pos, "overlapping spans"
        out += [text[pos:start], rep]
        pos = end
    out.append(text[pos:])
    return b"".join(out)


def _sections(text: bytes) -> dict[str, tuple[int, int]]:
    return {n: (s, e) for n, d, s, e, _ in elements(text) if d == 2}


def _empty(text: bytes, names) -> bytes:
    sec = _sections(text)
    return _cut(text, [(s, e, f"<{n}/>".encode()) for n in names if n in sec for s, e in [sec[n]]])


def _attr(attrs: bytes, key: str) -> str | None:
    m = re.search(rb'\b' + key.encode() + rb'="([^"]*)"', attrs)
    return m.group(1).decode() if m else None


def _drop_children(text: bytes, section: str, keep) -> bytes:
    """Remove every direct child of a top-level section for which keep(attrs) is false."""
    spans = []
    inside = None
    for n, d, s, e, a in elements(text):
        if d == 2 and n == section:
            inside = (s, e)
    if inside is None:
        return text
    for n, d, s, e, a in elements(text):
        if d == 3 and inside[0] < s < inside[1] and not keep(n, a):
            # take the line break after the child with it
            end = e + (2 if text[e:e + 2] == b"\r\n" else 1 if text[e:e + 1] == b"\n" else 0)
            spans.append((s, end, b""))
    return _cut(text, spans)


def no_programs(text: bytes) -> bytes:
    text = _empty(text, ("Programs",) + _EMPTIED_ALWAYS)
    spans = [(s, e, b"") for n, d, s, e, _ in elements(text) if n == "ScheduledPrograms" and d == 4]
    return _cut(text, spans)


def no_tags(text: bytes) -> bytes:
    return _empty(text, ("Tags",))


def no_modules(text: bytes) -> bytes:
    return _drop_children(text, "Modules", lambda n, a: _attr(a, "Name") == "Local")


def _type_refs(text: bytes, start: int, end: int) -> set[str]:
    return {m.group(1).decode() for m in re.finditer(rb'\bDataType="([^"]+)"', text[start:end])}


def no_unused_types(text: bytes) -> bytes:
    els = list(elements(text))
    udts = {_attr(a, "Name"): (s, e) for n, d, s, e, a in els if n == "DataType" and d == 3}
    aois = [(s, e) for n, d, s, e, a in els if n == "AddOnInstructionDefinition" and d == 3]
    need: set[str] = set()
    for s, e in aois:
        need |= _type_refs(text, s, e)
    todo = [t for t in need if t in udts]
    while todo:
        t = todo.pop()
        for r in _type_refs(text, *udts[t]):
            if r in udts and r not in need:
                need.add(r)
                todo.append(r)
    return _drop_children(text, "DataTypes", lambda n, a: _attr(a, "Name") in need)


def empty(text: bytes) -> bytes:
    return _empty(text, ("AddOnInstructionDefinitions", "DataTypes"))


LAYERS = (("L1_noprogs", no_programs), ("L2_notags", no_tags), ("L3_nomodules", no_modules),
          ("L4_nounused", no_unused_types), ("L5_empty", empty))


def build(src: Path) -> list[Path]:
    src = src.resolve()
    if LOCAL not in src.parents:
        raise SystemExit(f"{src}: a real export is read from samples/local/ only")
    OUT.mkdir(exist_ok=True)
    text = src.read_bytes()
    out = []
    for label, step in LAYERS:
        text = step(text)
        list(elements(text))  # still balanced
        path = OUT / f"{src.stem}_{label}.L5X"
        assert LOCAL in path.resolve().parents
        path.write_bytes(text)
        out.append(path)
    return out


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        for p in build(Path(arg)):
            print(p.relative_to(REPO), p.stat().st_size)
