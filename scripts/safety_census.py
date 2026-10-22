"""What each real safety program's safety partition carries (OQ-SAFETYLOGICIO).

A gap on one real program is only attributable when the content behind it is compared with
every other real program: a feature that a well-predicted program carries in quantity is
bounded by that program's gap. Per program in samples/local (read only, never rewritten):

  operands   every operand of a safety-routine instruction or AOI call, by spelling: a safety
             tag, a member of one, an AOI instance, a module connection tag named, through an
             adapter's slot (Adapter:1:I) or through Local; literals
  shapes     each safety instruction alone on its rung, chained with nothing else, or beside
             ordinary instructions
  tags       safety tags by scope and kind, program parameters by Usage, descriptions and
             member comments with their characters
  AOI calls  safety AOI calls and their operand count; devices; rungs and rung comments

  python scripts/safety_census.py                 # every real safety program found
  python scripts/safety_census.py RS-17 RS-02     # those labels only

Labels come from the gitignored samples/local/safety_aliases.csv; the report prints labels
only, never file names.
"""

from __future__ import annotations

import collections
import hashlib
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from l5x_memory_analyzer.parser.logic import BIT_INSTRUCTIONS  # noqa: E402
from l5x_memory_analyzer.parser.protected import add_protected_aoi_standins  # noqa: E402
from l5x_memory_analyzer.sizing.safety_io import safety_devices  # noqa: E402

CALL = re.compile(r"\b(THRSe|[A-Za-z_]\w*)\(")
MODULE = re.compile(r"^([A-Za-z_]\w*)(:\d+)?:(I|O|SI|SO|C)\b")
LITERAL = re.compile(r"^[-+]?(\d+(\.\d+)?([eE][-+]?\d+)?|16#[0-9A-Fa-f_]+|2#[01_]+)$")
SAFETY_INSTRUCTIONS = frozenset({
    "ESTOP", "RIN", "ROUT", "LC", "DIN", "ENPEN", "SMAT", "DCM", "FPMS", "CSM", "DCSRT", "DCA",
    "DCAF", "DCS", "THRS", "CROUT", "MVC", "DCST", "THRSe", "CBIM", "CPM", "AVC", "CBSSM",
    "MMVC", "DCSTM", "TSAM", "DCSTL", "TSSM", "EPMS", "CBCM", "FSBM"})


def _args(text: str, start: int) -> list[str]:
    depth, cur, out = 1, [], []
    for ch in text[start:]:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                out.append("".join(cur).strip())
                return out
        if ch == "," and depth == 1:
            out.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    return out


def census(path: Path) -> dict:
    root = ET.parse(path).getroot()
    add_protected_aoi_standins(root)
    c = root.find("Controller")
    aois = {a.get("Name"): a.get("Class") for a in c.iter("AddOnInstructionDefinition")}
    safety_programs = [p for p in c.findall("Programs/Program") if p.get("Class") == "Safety"]
    ctl = [t for t in c.findall("Tags/Tag") if t.get("Class") == "Safety"]
    prg = [t for p in safety_programs for t in p.findall("Tags/Tag")]
    names = {t.get("Name"): t for t in ctl + prg}
    udts = {d.get("Name") for d in c.findall("DataTypes/DataType")}
    out: dict = collections.defaultdict(collections.Counter)
    for scope, tags in (("ctl", ctl), ("prg", prg)):
        for t in tags:
            # A user type is reported as "UDT", never by its name (names stay in samples/local).
            kind = "alias" if t.get("TagType") == "Alias" else (
                "aoi" if t.get("DataType") in aois else "array" if t.get("Dimensions")
                else "UDT" if t.get("DataType") in udts else t.get("DataType"))
            out["tags"][f"{scope} {kind}"] += 1
            if t.get("Usage") and t.get("Usage") != "Local":
                out["parameters"][t.get("Usage")] += 1
            d = t.find("Description")
            if d is not None and (d.text or "").strip():
                out["documentation"]["descriptions"] += 1
                out["documentation"]["description chars"] += len(d.text.strip())
            for cm in t.findall("Comments/Comment"):
                out["documentation"]["member comments"] += 1
                out["documentation"]["member comment chars"] += len((cm.text or "").strip())
    for p in safety_programs:
        for r in p.findall("Routines/Routine"):
            out["logic"]["routines"] += 1
            for rung in r.iter("Rung"):
                out["logic"]["rungs"] += 1
                cm = rung.find("Comment")
                if cm is not None and (cm.text or "").strip():
                    out["documentation"]["rung comments"] += 1
                text = rung.find("Text").text or "" if rung.find("Text") is not None else ""
                calls = [(m.group(1), _args(text, m.end())) for m in CALL.finditer(text)]
                safety = [mn for mn, _ in calls if mn in SAFETY_INSTRUCTIONS]
                if safety:
                    shape = ("alone" if len(calls) == 1 else "chained" if len(safety) == len(calls)
                             else "beside ordinary")
                    out["safety instruction shapes"][shape] += len(safety)
                for mn, args in calls:
                    out["logic"]["instructions" if mn not in aois else "AOI calls"] += 1
                    if mn in aois:
                        out["AOI call operands"][len(args) - 1] += 1
                    for a in args:
                        out["operands"][_kind(a, mn, names, aois)] += 1
    out["devices"]["safety devices"] = len(safety_devices(root))
    return out


def _kind(arg: str, mnemonic: str, names: dict, aois: dict) -> str:
    if not arg or arg == "?":
        return "empty"
    if LITERAL.match(arg):
        return "literal"
    m = MODULE.match(arg)
    if m:
        how = "Local" if m.group(1) == "Local" else "slot path" if m.group(2) else "named"
        return f"module {how}" + (" (AOI call)" if mnemonic in aois else "")
    tag = names.get(re.match(r"[A-Za-z_]\w*", arg).group(0)) if re.match(r"[A-Za-z_]\w*", arg) else None
    if tag is None:
        return "other"
    if tag.get("TagType") == "Alias":
        return "alias"
    if tag.get("DataType") in aois:
        return "AOI member" if "." in arg else "AOI instance"
    return "safety tag" if not re.search(r"[.\[]", arg) else "safety tag member"


def main(argv: list[str]) -> int:
    labels = {}
    alias_file = REPO / "samples" / "local" / "safety_aliases.csv"
    if not alias_file.exists():
        print("samples/local/safety_aliases.csv not found: no real safety programs to read")
        return 1
    for line in alias_file.read_text().splitlines()[1:]:
        label, _file, sha = line.split(",")
        labels[sha] = label
    wanted = set(argv)
    found = []
    for f in sorted((REPO / "samples" / "local").rglob("*.L5X")):
        if "safety_io" in f.parts:
            continue
        label = labels.get(hashlib.sha256(f.read_bytes()).hexdigest()[:12])
        if label and (not wanted or label in wanted):
            found.append((label, f))
    for label, f in sorted(found, key=lambda x: (len(x[0]), x[0])):
        print(f"== {label}")
        for section, counts in census(f).items():
            print(f"   {section:28} " + ", ".join(f"{k}: {v}" for k, v in sorted(counts.items(), key=lambda kv: str(kv[0]))))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
