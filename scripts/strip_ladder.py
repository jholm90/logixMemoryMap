"""Attribute a real program's residual by SUBTRACTION, on real content.

Every capture this project has is a single scalar: one number for a whole
project. With roughly fifteen independent cost categories and one equation
per file, the system is hopelessly under-determined at file level -- which
is why isolation files exist, and why a +X in one category and a -X in
another cancel invisibly inside a real program.

That is not a theory. Across the sixteen real captured programs, every
candidate driver computable from the L5X has now been tested against the
percentage error and none of them explains it:

    AOI definitions   r = -0.414      rungs             r = -0.071
    compiled logic    r = -0.185      tag count         r = -0.034
    alarms            r = +0.137      tags per MB       r = +0.028
    modules           r = +0.001      file size         r = -0.015
    processor family  -- disproved directly: murraybros is -5.16% on a
                         1756-L81E, worse than every 5069 file, on the
                         family with the best median

Nine drivers, no attribution. The residual is real, large (-5.16% and
-5.03% on the two worst) and belongs to nothing visible.

So stop correlating and start subtracting. This takes a real program and
emits a descending LADDER of variants, each removing exactly one more
category than the last. Capture every rung of the ladder and the
difference between consecutive rungs is that category's REAL cost inside
real content -- not a synthetic isolation file's cost, the actual one, in
the actual program that is mispredicting.

    L0  full program, untouched
    L1  minus alarm conditions
    L2  minus all rung and ST content (routines emptied to NOP)
    L3  minus all axis tags, coordinate systems and the MotionGroup
    L4  minus all I/O modules except the processor's own Local entry
    L5  minus all AOI definitions and the tags that instantiate them
    L6  minus all remaining tags
    L7  minus all UDT definitions -- the bare shell

The order is not arbitrary: each strip only removes things nothing
remaining can reference.

  - Logic is emptied BEFORE motion, modules and AOIs go, so no rung is
    left pointing at a module tag, driving an axis that is gone, or
    calling a definition that no longer exists.
  - Motion goes BEFORE the modules. A CIP axis names its drive in its own
    MotionModule attribute, so dropping the drive first would leave an
    axis pointing at a module that does not exist.
  - Tags go before the UDTs that type them.

A ladder that does not import measures nothing.

FIRST CUT, AND IT MAY NOT ALL IMPORT. This is XML surgery, not Studio
5000 doing the deleting. Each rung is ordered to be self-consistent, but
real projects carry references this script does not know about. If a rung
is refused on import, the reliable fix is to make that one rung by hand --
delete that category in Logix Designer and re-export -- because Studio's
own delete maintains every reference this script has to guess at. A
hand-made rung and a generated one difference identically; only the making
of it differs.

OUTPUT IS GITIGNORED, DELIBERATELY. These are derived from production
exports and are production content with pieces missing, so they are
written to samples/local/stripped/ and never committed. The SCRIPT is the
committed artifact; the files it makes are not. See CLAUDE.md's repository
rules.

Usage:
    python scripts/strip_ladder.py samples/local/Murraybros_...L5X [more...]
"""

from __future__ import annotations

import copy
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

OUT_DIR = Path(__file__).parent.parent / "samples" / "local" / "stripped"

NOP_RUNG_TEXT = "NOP();"


def _controller(root: ET.Element) -> ET.Element | None:
    return root.find("Controller")


def _drop_alarms(root: ET.Element) -> int:
    n = 0
    for tag in root.iter("Tag"):
        for child in list(tag):
            if child.tag in ("AlarmConditions", "AlarmDigital", "AlarmAnalog"):
                tag.remove(child)
                n += 1
    return n


def _empty_logic(root: ET.Element) -> int:
    """Every rung becomes NOP and every ST routine loses its lines. The
    routines themselves stay, so the Task/Program/Routine shell cost -- a
    separate, already-wired term -- does not move between L1 and L2."""
    n = 0
    for rung in root.iter("Rung"):
        text = rung.find("Text")
        if text is None:
            text = ET.SubElement(rung, "Text")
        text.text = NOP_RUNG_TEXT
        n += 1
    for content in root.iter("STContent"):
        for line in list(content):
            content.remove(line)
            n += 1
    return n


_MOTION_TYPES = {
    "AXIS_CIP_DRIVE", "AXIS_SERVO", "AXIS_SERVO_DRIVE", "AXIS_VIRTUAL",
    "AXIS_GENERIC", "AXIS_GENERIC_DRIVE", "AXIS_CONSUMED",
    "COORDINATE_SYSTEM", "MOTION_GROUP",
}


def _drop_motion(root: ET.Element) -> int:
    """Axis tags, coordinate systems and the MotionGroup.

    Removed BEFORE the modules, not after: a CIP axis names its drive in
    its own MotionModule attribute, so dropping the drive first would
    leave an axis pointing at a module that no longer exists. Removed
    AFTER the logic, so no MAM/MAJ/MSO is left referencing an axis that
    is gone. Its own rung because the model gives motion its own root
    group and its own constants, and because every motion structure is
    large enough that folding it into the general tag step would hide it.
    """
    n = 0
    for parent in root.iter("Tags"):
        for tag in list(parent):
            if (tag.get("DataType") or "") in _MOTION_TYPES:
                parent.remove(tag)
                n += 1
    return n


def _drop_modules(root: ET.Element) -> int:
    modules = root.find("Controller/Modules")
    if modules is None:
        return 0
    n = 0
    for mod in list(modules):
        if (mod.get("Name") or "") == "Local":
            continue   # the processor's own entry; removing it is not a valid project
        modules.remove(mod)
        n += 1
    return n


def _drop_aois(root: ET.Element) -> int:
    defs = root.find("Controller/AddOnInstructionDefinitions")
    names = set()
    n = 0
    if defs is not None:
        for d in list(defs):
            names.add(d.get("Name") or "")
            defs.remove(d)
            n += 1
    # Any tag typed by one of those definitions is now untypeable.
    for parent in root.iter("Tags"):
        for tag in list(parent):
            if (tag.get("DataType") or "") in names:
                parent.remove(tag)
                n += 1
    return n


def _drop_tags(root: ET.Element) -> int:
    n = 0
    for parent in root.iter("Tags"):
        for tag in list(parent):
            parent.remove(tag)
            n += 1
    return n


def _drop_udts(root: ET.Element) -> int:
    dts = root.find("Controller/DataTypes")
    if dts is None:
        return 0
    n = len(list(dts))
    for d in list(dts):
        dts.remove(d)
    return n


LADDER = (
    ("l0_full", None, "the program exactly as exported -- the anchor every other rung differences against"),
    ("l1_noalarms", _drop_alarms, "alarm conditions removed"),
    ("l2_nologic", _empty_logic, "every rung emptied to NOP and every ST line removed"),
    ("l3_nomotion", _drop_motion, "all axis tags, coordinate systems and the MotionGroup removed"),
    ("l4_nomodules", _drop_modules, "all I/O modules removed except the processor's Local entry"),
    ("l5_noaois", _drop_aois, "all AOI definitions removed, and the tags that instantiated them"),
    ("l6_notags", _drop_tags, "all remaining tags removed"),
    ("l7_noudts", _drop_udts, "all UDT definitions removed -- the bare shell"),
)


def build_ladder(path: Path) -> list[tuple[str, Path, int]]:
    tree = ET.parse(path)
    root = tree.getroot()
    stem = path.stem.lower().replace(" ", "_")[:28]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    made = []
    for level, fn, _why in LADDER:
        removed = fn(root) if fn else 0
        out = OUT_DIR / f"strip_{stem}_{level}.L5X"
        # Re-serialise from a copy so later strips keep mutating one tree
        # rather than re-parsing, which is what makes the ladder cumulative.
        ET.ElementTree(copy.deepcopy(root)).write(out, encoding="utf-8", xml_declaration=True)
        made.append((level, out, removed))
    return made


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    for arg in argv[1:]:
        p = Path(arg)
        if not p.exists():
            print(f"missing: {p}")
            return 1
        print(f"\n{p.name}")
        for level, out, removed in build_ladder(p):
            size = out.stat().st_size
            print(f"   {level:14s} removed {removed:6d} element(s)   {size:10,} bytes   {out.name}")
    print(f"\nWrote to {OUT_DIR} (gitignored -- these are production content with pieces "
          f"missing and must never be committed).")
    print("Capture every rung; consecutive differences are each category's real cost.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
