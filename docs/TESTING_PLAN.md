# Testing / Validation Plan

Goal: for every sample L5X, get a real controller-reported memory-used number
to compare against this tool's prediction. This is the whole feedback loop that
Phases 3/4/4b run on — get the procedure locked before generating 30-40 files
against it, or the whole batch has to be redone.

## Procedure per sample (semi-automated — see OQ-MEMREADMETHOD for the still-open piece)

Researched 2026-08-20 (see OQ-GENMETHOD/OQ-MEMREADMETHOD for sourcing): Rockwell
publishes an official **Logix Designer SDK** (.NET, `RockwellAutomation.LogixDesigner`)
plus two CLI tools built on it in `RockwellAutomation/ra-logix-designer-vcs-custom-tools`
(GitHub) — `l5xplode`/`l5xgit`. `l5xgit l5x2acd --l5x <file> --acd <file>` converts
L5X → ACD headlessly, no Logix Designer UI interaction. This is real and confirmed
(Rockwell's own repo, requires Logix Designer SDK 2.2+), not a hypothetical.
`scripts/batch_l5x_to_acd.ps1` in this repo wraps it over a whole folder.

What's confirmed to exist in the SDK beyond that (via `ra-logix-cicd`'s
`LogixDesigner_ClassLibrary`/`LogixEcho_ClassLibrary` sample code): `LogixProject`
exposes `SaveAsync`/`DownloadAsync`/`SetCommunicationsPathAsync` and per-type
`GetTagValue*Async`/`SetTagValue*Async` (BOOL/SINT/INT/DINT/LINT/REAL/STRING,
plus a byte-array path for structured types) once online — so reading an
arbitrary tag's value back programmatically is solved. Separately, the
**FactoryTalk Logix Echo** SDK can spin up an emulated chassis+controller
straight from an ACD file (`CreateChassisFromACD`) and hand back a
communications path — so "download to a target" doesn't require a real
controller or manual Emulate setup either.

What's still NOT confirmed: whether any GSV/system-value attribute actually
exposes controller memory usage as a readable value. If it does, the full loop
(convert → spin up Echo chassis → download → GSV-into-tag → read tag via SDK →
log) closes with zero manual steps per sample. If it doesn't, memory has to be
read from Controller Properties → Memory tab by eye — this is the fallback
below, and the one still confirmed manual step regardless of how far the SDK
work goes.

1. Start from a fixed empty baseline project (same controller model/firmware
   rev for every sample — do not mix CompactLogix models mid-test, memory
   reporting granularity may differ).
2. Convert the sample L5X to ACD (`scripts/batch_l5x_to_acd.ps1`, batchable —
   no per-sample manual import).
3. Verify/compile (no errors — a sample that doesn't compile is not valid data).
4. Download to controller (real hardware or Emulate — decision per OQ-EMULATE).
5. Read memory used: Controller Properties → Memory tab (bytes used / bytes
   free) — manual for now. `scripts/batch_memory_capture.ps1` opens each
   converted ACD in turn and prompts for this number so the file-hunting and
   manifest-row formatting isn't manual too, even though the read itself is.
6. Record: baseline-before bytes, after bytes, delta = sample's actual footprint.
7. Log to `samples/manifest.csv` (batch_memory_capture.ps1 does this per-row;
   resumable across a multi-session batch of hundreds of samples).
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
