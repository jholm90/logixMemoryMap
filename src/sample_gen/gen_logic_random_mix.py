"""Random-combination logic validation harness (James, 2026-08-22): "You got
sample instruction sizing already, now you need to generate random
combinations, estimate and test."

The 244-file per-instruction sweep isolated one instruction type per file --
real routines mix dozens of types together. This generates files that DO
that mixing, and predicts each file's total by running the actual sizing
engine (`l5x_memory_analyzer.sizing`) against its own generated output --
not a hand-rolled formula. That matters here specifically: an earlier
version of this file (and of the engine itself) summed each instruction's
RAW per-file sweep weight by occurrence count, which double-counted rungs
like XIC's own test file ("XIC(tag)OTE(tag);" -- a bare XIC can't legally
close a rung) where the raw measured weight was really XIC+OTE combined,
not XIC alone. Caught 2026-08-22 by cross-checking the engine's own
prediction against real captured data (see docs/MEMORY_MODEL.md and
sizing/memory_model.yaml's logic_instructions section for the full
correction). Running the real engine on real generated rung text is
immune to that class of bug by construction: it counts actual instruction
occurrences in the actual rung text and applies the now-decomposed,
properly-additive per-instruction weights, whatever combination a given
rung happens to contain.

Once James tests these, comparing predicted vs actual is the direct test
of whether the per-instruction weights actually compose additively in a
realistic mixed routine -- the same validation OQ-LARGEMIXED already did
for tags/UDTs, now for logic.

Reuses gen_logic_sweep.py's real per-instruction rung-text functions and
shared tag pool directly (no duplicated/reinvented operand shapes) --
excludes the 6 instructions still flagged for re-capture (CPS/COP/FLL/
SIZE/BTD/T_ADD) and JSR/LBL-JMP (special multi-rung/subroutine shapes, not
a simple single-rung-per-count pattern like everything else here).

Run: python -m sample_gen.gen_logic_random_mix
"""

from __future__ import annotations

import random
import xml.etree.ElementTree as ET
from pathlib import Path

from sample_gen.gen_logic_sweep import _POOL_TAGS_XML, INSTRUCTIONS
from sample_gen.builders import rungs_xml
from sample_gen.manifest import append_manifest_row
from sample_gen.wrapper import build_l5x

from l5x_memory_analyzer.sizing.constants import load_memory_model
from l5x_memory_analyzer.sizing.report import build_report

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"
RNG_SEED = 20260822  # reproducible -- same batch every re-run until seed changes

# Excludes the 6 flagged-for-re-capture instructions -- they have no weight
# in memory_model.yaml yet, so any rung using them would silently predict
# zero for that instruction's own contribution.
MODEL = load_memory_model()
CANDIDATE_INSTRUCTIONS = sorted(set(MODEL.logic_instructions.weights) & set(INSTRUCTIONS))


def _predict_via_engine(l5x_text: str) -> int:
    root = ET.fromstring(l5x_text)
    entries, errors = build_report(root, MODEL)
    assert not errors, errors
    logic_entries = [e for e in entries if e.tier == "estimated"]
    assert len(logic_entries) == 1, logic_entries
    return logic_entries[0].bytes


def _write_with_prediction(l5x: str, out_name: str, description: str) -> None:
    predicted = _predict_via_engine(l5x)
    out_path = OUT_ROOT / f"{out_name}.L5X"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(l5x, encoding="utf-8")
    append_manifest_row(out_name, description, "logic_random_mix", out_path, predicted)
    print(f"Wrote {out_path} (predicted {predicted} blocks -- via the real sizing engine)")


def _one_random_file(rng: random.Random, file_index: int, min_types: int, max_types: int,
                      min_rungs: int, max_rungs: int) -> None:
    n_types = rng.randint(min_types, max_types)
    chosen = rng.sample(CANDIDATE_INSTRUCTIONS, n_types)
    counts = {name: rng.randint(min_rungs, max_rungs) for name in chosen}

    rung_blocks = [rungs_xml(counts[name], INSTRUCTIONS[name]) for name in chosen]
    all_rungs = "\n".join(rung_blocks)
    total_rungs = sum(counts.values())

    l5x = build_l5x(target_name=f"RandomMix{file_index}", tags_xml=_POOL_TAGS_XML, extra_rungs_xml=all_rungs)
    mix_desc = ", ".join(f"{counts[n]}x{n}" for n in chosen)
    out_name = f"randommix_{file_index:02d}_n{total_rungs:05d}rungs_{n_types:02d}types"
    _write_with_prediction(l5x, out_name,
                            f"Random mix ({n_types} instruction types, {total_rungs} total rungs): {mix_desc}")


def main() -> None:
    rng = random.Random(RNG_SEED)
    # Small-scale mixes (realistic single-routine size) and large-scale
    # mixes (stress the composition at real-program scale) -- both matter,
    # additive composition could plausibly hold at one scale and drift at
    # another (e.g. if there's any shared/amortized cost across instruction
    # types the isolated per-instruction sweep couldn't see).
    for i in range(5):
        _one_random_file(rng, i, min_types=5, max_types=12, min_rungs=5, max_rungs=200)
    for i in range(5, 8):
        _one_random_file(rng, i, min_types=15, max_types=30, min_rungs=100, max_rungs=2000)
    print("\nDone. 8 files.")


if __name__ == "__main__":
    main()
