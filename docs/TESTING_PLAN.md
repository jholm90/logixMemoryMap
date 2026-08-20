# Testing / Validation Plan

Goal: for every sample L5X, get a real controller-reported memory-used number
to compare against this tool's prediction. This is the whole feedback loop that
Phases 3/4/4b run on — get the procedure locked before generating 30-40 files
against it, or the whole batch has to be redone.

## Procedure per sample (manual baseline — see OQ-MEMREADMETHOD for automation)

1. Start from a fixed empty baseline project (same controller model/firmware
   rev for every sample — do not mix CompactLogix models mid-test, memory
   reporting granularity may differ).
2. Import the sample's tags/UDTs/logic (however produced — see
   SAMPLE_GENERATION.md).
3. Verify/compile (no errors — a sample that doesn't compile is not valid data).
4. Download to controller (real hardware or Emulate — decision per OQ-EMULATE).
5. Read memory used: Controller Properties → Memory tab (bytes used / bytes
   free), OR scripted GSV read if OQ-MEMREADMETHOD resolves that route.
6. Record: baseline-before bytes, after bytes, delta = sample's actual footprint.
7. Log to `samples/manifest.csv`.
8. Return controller to the fixed empty baseline before the next sample (don't
   accumulate — isolate one variable per sample).

## Manifest columns (`samples/manifest.csv`)

`sample_id, description, category (tag|udt|aoi|module|logic_bit|logic_other), l5x_path, predicted_bytes, actual_bytes, delta, delta_pct, controller_model, firmware_rev, date_tested, notes`

## Sample isolation principle

Every sample changes exactly one variable from the baseline. If testing "does
UDT member order affect size," the sample pair is identical in every respect
except member order — same member types/count, only order differs. This is what
makes the manifest usable for regression later instead of a pile of
unreproducible one-offs.

## Phase 3 sample set (tag/UDT/AOI — see TASKS.md for the generation list)

Each sample should be sized to produce a *measurable* delta against baseline —
10k-element arrays exist specifically because a single tag's byte difference
could get lost in memory reporting granularity/rounding. If a controller only
reports memory in some rounded unit (KB, page-aligned, etc — unconfirmed),
scale samples up until deltas are unambiguous, and note the observed rounding
granularity in MEMORY_MODEL.md once discovered.

## Phase 4/4b sample set (logic)

Same isolation principle, scaled by rung/instruction count instead of tag size:
generate the same logic pattern at N=10, 100, 1000 instances to (a) get a
measurable delta and (b) confirm the relationship is linear (it should be,
for straight-line bit logic with no shared subroutine effects) before fitting
a single per-instruction weight from just two data points.

## Exit criteria

Phase 3 and Phase 4/4b each close per PROJECT_PLAN.md's stated exit criteria —
tolerance TBD in OQ-TOLERANCE. Don't move to UI work (Phase 5) with an open,
unresolved tag/UDT discrepancy just because logic sizing is more interesting —
an error in the "exact" tier undermines the tool's whole value proposition more
than an acknowledged estimate in the logic tier does.
