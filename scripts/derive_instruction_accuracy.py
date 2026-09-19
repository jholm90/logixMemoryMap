"""Measure how accurate the engine is, per instruction, from captures.

Confidence was a PROVENANCE tag -- KNOWN / FITTED / ASSUMED -- which says where a
number came from, not how likely it is to be right. That under-sells the model:
every compiled-logic weight is tagged FITTED because ladder size cannot be
derived from first principles, so a routine reported "0% measured" even where its
instruction weights reproduce real captures to the byte.

This replaces the tag with a measurement. For each instruction it finds the
captured files where that instruction is the VARIABLE UNDER TEST -- exactly one
non-scaffold opcode, compiled logic the dominant cost, enough occurrences for the
slope to beat the per-file base -- and records how far the engine's prediction
landed from the controller's own reading.

    307 of 413 qualifying rows within 0.1%. Median 0.0030%.

The tail is not noise and must not be averaged away: CPT sits at 3.27% mean and
119.6% worst because the SINT/INT widening defect is real and unfixed, and that
is exactly what a confidence display is for.

XIC, XIO, OTE and NOP get no isolated sweep of their own because they ARE the
scaffolding every other test rung is built from. They are not unmeasured -- they
are the most-measured weights in the model: the `emptyrungs` sweep fixes NOP and
the per-rung base, and the `rshape_arr_*` files hold eight XICs and one OTE fixed
while moving only the branch arrangement, and came back byte-exact at every leg
count. `confidence.py` pins them explicitly rather than reporting them as
unknown.

Output is written into `memory_model.yaml` as data: a sizing constant belongs in
the model file, not in code. Re-run whenever a capture batch lands.

Run: python scripts/derive_instruction_accuracy.py [--write]
"""

from __future__ import annotations

import argparse
import collections
import re
import statistics as st
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from accuracy_report import _MODEL, is_valid_capture  # noqa: E402
from sample_gen.manifest_store import load_manifest  # noqa: E402
import l5x_memory_analyzer.sizing.report as rep  # noqa: E402

CALL = re.compile(r"\b([A-Z][A-Z0-9_]{1,15})\s*\(")

# The rung scaffolding. A test file for MOV still needs a condition and an
# output, so these appear everywhere and can never be "the one thing moving".
SCAFFOLD = ("XIC", "XIO", "OTE", "NOP")

# A file counts as measuring its one opcode only if compiled logic is most of
# what it costs, and only if the opcode appears enough times for the slope to
# dominate the per-file base.
LOGIC_SHARE_FLOOR = 0.25
MIN_OCCURRENCES = 5

MODEL_YAML = REPO_ROOT / "src" / "l5x_memory_analyzer" / "sizing" / "memory_model.yaml"


def measure() -> dict[str, list[float]]:
    per: dict[str, list[float]] = collections.defaultdict(list)
    for row in load_manifest():
        if not is_valid_capture(row):
            continue
        # An isolation file is identified by WHAT IT CONTAINS -- exactly one
        # non-scaffold opcode -- never by its name. Two filename whitelists
        # were tried first and both silently dropped real evidence: `verif_`
        # missed all 33 hand-verified `verifinstr_*` motion files and made
        # every motion instruction look untested, and the next attempt still
        # missed `unweighted_*`, `uwclose_*`, `forloop_*`, `lbljmp_*` and
        # `subrtn_*`. Naming conventions drift; the rung text does not.
        if row["sample_id"].startswith("realprog_"):
            continue                      # held-out set, never a fitting input
        if not (row.get("actual_bytes") or "").strip():
            continue                      # specced but never captured
        path = REPO_ROOT / row["l5x_path"]
        if not path.exists():
            continue
        try:
            root = ET.parse(path).getroot()
        except Exception:
            continue
        ops = collections.Counter()
        for rung in root.iter("Rung"):
            for m in CALL.finditer(rung.findtext("Text") or ""):
                ops[m.group(1)] += 1
        subject = [o for o in ops if o not in SCAFFOLD] or list(ops)
        if len(subject) != 1:
            continue                      # not an isolation file for anything
        try:
            entries, _ = rep.build_report(root, _MODEL)
        except Exception:
            continue
        predicted = sum(e.bytes for e in entries)
        actual = int(row["actual_bytes"])

        # The file's error only measures this instruction if the instruction
        # is what the file mostly COSTS. A tag-packing test whose rungs are
        # all NOP contains exactly one opcode and is not a NOP test: its error
        # belongs to the tags. Without this, NOP picked up 2,057 "samples" and
        # a 94.8% worst case borrowed from whatever those files were really
        # testing, and CPT inherited the cptnar narrowing defect the same way.
        logic = sum(e.bytes for e in entries if e.category == "routine_logic")
        if predicted <= 0 or logic / predicted < LOGIC_SHARE_FLOOR:
            continue
        if ops[subject[0]] < MIN_OCCURRENCES:
            continue

        per[subject[0]].append(abs(actual - predicted) / actual * 100)
    return per


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true",
                    help="write the table into memory_model.yaml")
    args = ap.parse_args(argv[1:])

    per = measure()
    rows = sorted(((o, len(v), st.mean(v), max(v)) for o, v in per.items()),
                  key=lambda r: -r[2])
    allv = [x for v in per.values() for x in v]
    print(f"{len(per)} instructions with an isolated sweep, {len(allv)} rows")
    print(f"mean {st.mean(allv):.4f}%  median {st.median(allv):.4f}%  "
          f"within 0.1%: {sum(1 for x in allv if x < 0.1)}/{len(allv)}\n")
    print(f"{'instr':10s} {'n':>3s} {'mean%':>9s} {'worst%':>9s}")
    for o, n, m, mx in rows[:12]:
        print(f"{o:10s} {n:3d} {m:9.4f} {mx:9.4f}")
    print("   ... (rest are all under 0.1%)")

    if args.write:
        lines = ["", "# Measured per-instruction prediction accuracy, generated by",
                 "# scripts/derive_instruction_accuracy.py from captured isolation files.",
                 "# worst_pct is the largest |error| the engine actually made on a file",
                 "# where that instruction was the only variable. Do not hand-edit.",
                 "instruction_accuracy:"]
        for o, n, m, mx in sorted(rows):
            lines.append(f"  {o}: {{samples: {n}, mean_pct: {m:.4f}, worst_pct: {mx:.4f}}}")
        text = MODEL_YAML.read_text(encoding="utf-8")
        marker = "\ninstruction_accuracy:"
        if marker in text:
            head = text.index(marker)
            tail = text.find("\n\n", head + 1)
            text = text[:head] + ("\n" + "\n".join(lines[1:])) + (text[tail:] if tail > 0 else "\n")
        else:
            text = text.rstrip("\n") + "\n" + "\n".join(lines) + "\n"
        MODEL_YAML.write_text(text, encoding="utf-8")
        print(f"\nwrote {len(rows)} entries into {MODEL_YAML.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
