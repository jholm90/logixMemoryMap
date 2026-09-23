"""Refuse a test family that varies more than one thing between files.

An isolation file earns its capture slot by differencing against its
neighbour: hold everything fixed, move one dimension, and the difference IS
that dimension's cost. A family that moves two dimensions between consecutive
files measures their SUM, and no arithmetic separates them afterwards. That
failure is silent -- the files convert, the captures come back clean, and the
number is simply not the number anyone thinks it is.

This has already cost real work. Three specs written on one day each varied
two things at once: literal count together with operator count, connection
format together with adapter type, and a per-routine term together with a
per-file one. All three would have produced captures that answered nothing.

So this profiles every file in a family across the dimensions a cost model
cares about and reports the consecutive pairs that move more than one. Run it
on a SPEC before the files are built, and on the family afterwards.

    python scripts/confound_check.py --family 'cpttri_'
    python scripts/confound_check.py path/to/*.L5X

Exit code is 1 when any consecutive pair varies more than one dimension, so
it can gate a generator.
"""

from __future__ import annotations

import argparse
import collections
import csv
import glob
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
# Mixed case, not just ALL-CAPS: an AOI call site is an instruction too, and
# real AOI names are mixed-case (DigitalSensor, AnalogSensor, PTimer). With an
# ALL-CAPS-only pattern the checker was blind to every AOI call site's
# operands, and reported four litop_bool_* files whose call arguments genuinely
# differ as IDENTICAL -- a false negative, which is the one failure mode worse
# than not checking at all. Sixth blind spot found in this script.
CALL = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]{1,39})\s*\(")


def _split_operands(s: str) -> list[str]:
    """Split on top-level commas only.

    A naive split counts `COP(Hist[0,0],Tmp[0,0],800)` as five operands
    because of the subscript commas. That mistake was made and briefly
    believed -- it manufactured a "COP takes four and five
    operands in real programs, and the corpus only builds three" finding that
    does not exist. With bracket-aware splitting, 19 of the top 20 real
    instructions have operand counts the corpus already covers exactly.
    """
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch in "[(":
            depth += 1
        elif ch in "])":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    out.append(cur)
    return [a.strip() for a in out if a.strip()]


def profile(path: str) -> dict[str, object] | None:
    """The dimensions a sizing model can charge for. Each is compared as a
    whole, so a change anywhere inside one counts as that dimension moving."""
    try:
        root = ET.parse(path).getroot()
    except Exception:
        return None
    ctl = root.find("Controller")
    if ctl is None:
        return None

    tags = collections.Counter()
    dims = collections.Counter()
    namelens = collections.Counter()
    # Declaration ORDER. `tags` is a Counter and so is order-blind, which
    # makes a family that permutes the same tag multiset read as
    # byte-identical -- the fifth blind spot of this class. Types only, not
    # names, so renaming is not mistaken for reordering.
    order = []
    for tg in root.iter("Tag"):
        tags[(tg.get("DataType") or "?", tg.get("TagType") or "Base")] += 1
        dims[(tg.get("Dimensions") or "").strip()] += 1
        namelens[len(tg.get("Name") or "")] += 1
        order.append(tg.get("DataType") or "?")

    opcodes = collections.Counter()
    operands = collections.Counter()
    # The literal operand text, kept separately. Opcode and operand COUNT are
    # blind to everything inside an expression -- a CPT whose tier arrangement
    # moves from 2,1,1 to 2,1,2 is one opcode with one operand either way, and
    # without this the checker calls two genuinely different files identical,
    # which is a worse failure than not checking at all.
    exprs = collections.Counter()
    branches = rungs = 0
    for rung in root.iter("Rung"):
        txt = rung.findtext("Text") or ""
        rungs += 1
        if "[" in txt:
            branches += 1
        for m in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]{1,39})\s*\(([^()]*)\)", txt):
            args = _split_operands(m.group(2))
            opcodes[m.group(1)] += 1
            operands[(m.group(1), len(args))] += 1
            exprs[(m.group(1), tuple(args))] += 1

    return {
        "processor": ctl.get("ProcessorType"),
        "firmware": root.get("SoftwareRevision"),
        "tag inventory": dict(tags),
        "tag declaration order": order,
        "tag dimensions": dict(dims),
        "tag name lengths": dict(namelens),
        "instruction inventory": dict(opcodes),
        "operand shapes": dict(operands),
        "operand text": dict(exprs),
        "rung count": rungs,
        "branched rungs": branches,
        # ARRANGEMENT. The opcode multiset and the operand text are both
        # identical whether eight XICs sit in series or in two branch legs of
        # four, so without this a family built to test arrangement -- which is
        # the largest measured evidence gap in the project -- reads as
        # byte-identical. Operand contents are blanked so only the bracket
        # structure and opcode order remain.
        "rung structure": dict(collections.Counter(
            re.sub(r"\(([^()]*)\)", "()", (rg.findtext("Text") or "").strip())
            for rg in root.iter("Rung"))),
        "ST lines": sum(len(list(c)) for c in root.iter("STContent")),
        # ST bodies live in <STContent><Line>, not in <Rung><Text>, so the
        # rung sweep above cannot see them. Without this, a family that varies
        # only its ST operator -- which is most of the structured-text
        # families -- reads as byte-identical.
        "ST text": dict(collections.Counter(
            (ln.text or "").strip()
            for c in root.iter("STContent") for ln in c)),
        "routines": sum(1 for _ in root.iter("Routine")),
        "programs": len(root.findall("Controller/Programs/Program")),
        "tasks": len(root.findall("Controller/Tasks/Task")),
        "UDT definitions": len(root.findall("Controller/DataTypes/DataType")),
        "AOI definitions": len(
            root.findall("Controller/AddOnInstructionDefinitions/AddOnInstructionDefinition")),
        # Definition member ORDER, not just count. Permuting the members of a
        # UDT or an AOI changes nothing countable, so without this a family
        # built to test exactly that reads as byte-identical -- the same
        # blind spot as expressions and ST bodies above. Any new dimension a
        # family is built to vary has to be added here, or this checker will
        # wave it through.
        "definition member order": [
            (d.get("Name"), tuple((m.get("Name"), m.get("DataType"), m.get("Dimension"))
                                  for m in d.iter("Member")))
            for d in root.findall("Controller/DataTypes/DataType")
        ] + [
            (a.get("Name"), tuple((m.get("Name"), m.get("DataType"), m.get("Usage"))
                                  for m in a.iter("Parameter")),
                            tuple((m.get("Name"), m.get("DataType"))
                                  for m in a.iter("LocalTag")))
            for a in root.findall(
                "Controller/AddOnInstructionDefinitions/AddOnInstructionDefinition")
        ],
        "modules": sorted(
            (m.get("CatalogNumber") or "?") for m in root.findall("Controller/Modules/Module")),
        # Module NAME lengths. Catalogs alone read a family that renames one
        # module as byte-identical -- the name-length sweep did exactly that.
        "module name lengths": sorted(
            len(m.get("Name") or "") for m in root.findall("Controller/Modules/Module")),
        # Tag-based alarm conditions hang off a tag's <AlarmConditions>, not
        # off anything above, so a condition-count family read as identical.
        "alarm conditions": sum(1 for _ in root.iter("AlarmCondition")),
    }


# When a coarser dimension moves, the finer one it contains necessarily moves
# too. Reporting both would turn every genuine one-dimension change into a
# false CONFOUND, so the finer one is dropped whenever its parent already
# fired; the parent is the more informative description.
_IMPLIED_BY = {
    "operand text": ("operand shapes", "instruction inventory"),
    "operand shapes": ("instruction inventory",),
    # The multiset of rung shapes determines how many rungs there are and how
    # many of them branch, so reporting those alongside it is the same
    # double-count as operand text against instruction inventory.
    # Chained: inventory -> structure -> count/branching. `differing` tests
    # parents against everything that moved, not against what it has already
    # printed, so the whole chain collapses to its most informative link.
    "rung structure": ("instruction inventory",),
    "rung count": ("rung structure", "instruction inventory"),
    "branched rungs": ("rung structure", "instruction inventory"),
    "ST text": ("ST lines",),
    "tag declaration order": ("tag inventory",),
    "tag dimensions": ("tag inventory",),
    "tag name lengths": ("tag inventory",),
}


def differing(a: dict, b: dict) -> list[str]:
    moved = {k for k in a if a[k] != b[k]}
    return sorted(k for k in moved
                  if not any(parent in moved for parent in _IMPLIED_BY.get(k, ())))


def _family_paths(family: str) -> list[tuple[str, str]]:
    manifest = REPO_ROOT / "samples" / "manifest.csv"
    out = []
    with open(manifest, encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            if re.search(family, row["sample_id"]) and (REPO_ROOT / row["l5x_path"]).exists():
                out.append((row["sample_id"], str(REPO_ROOT / row["l5x_path"])))
    return sorted(out)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("paths", nargs="*", help="L5X files or globs")
    ap.add_argument("--family", help="regex over sample_id, resolved through manifest.csv")
    args = ap.parse_args(argv[1:])

    if args.family:
        named = _family_paths(args.family)
    else:
        named = [(Path(p).stem, p) for pat in args.paths for p in sorted(glob.glob(pat))]
    if len(named) < 2:
        print("need at least two files to difference")
        return 2

    profiles = [(n, profile(p)) for n, p in named]
    profiles = [(n, pr) for n, pr in profiles if pr]
    print(f"{len(profiles)} file(s)\n")

    bad = 0
    for (n1, p1), (n2, p2) in zip(profiles, profiles[1:]):
        diff = differing(p1, p2)
        if len(diff) == 1:
            print(f"  ok        {n1} -> {n2}: varies {diff[0]}")
        elif not diff:
            bad += 1
            print(f"  IDENTICAL {n1} -> {n2}: nothing varies -- one of these is a wasted slot")
        else:
            bad += 1
            print(f"  CONFOUND  {n1} -> {n2}: varies {len(diff)} dimensions -- {', '.join(diff)}")

    print()
    if bad:
        print(f"{bad} consecutive pair(s) cannot be differenced. A capture on these "
              f"measures a SUM, not a cost.")
        return 1
    print("every consecutive pair varies exactly one dimension.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
