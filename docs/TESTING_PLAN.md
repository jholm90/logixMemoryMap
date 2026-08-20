# Testing / Validation Plan

Goal: for every sample L5X, get a real controller-reported memory-used number
to compare against this tool's prediction. This is the whole feedback loop that
Phases 3/4/4b run on — get the procedure locked before generating 30-40 files
against it, or the whole batch has to be redone.

## Procedure per sample (offline compile, no hardware/emulator — settled 2026-08-20)

**Corrected 2026-08-20 (James, resolving OQ-EMULATE):** no download to a
controller or Emulate is needed at all. Logix Designer shows memory usage in
Controller Properties as soon as a project **successfully compiles/verifies
offline** — that was an incorrect assumption in this file's earlier version
of the procedure (and made the Logix Echo/SDK-download research below look
more load-bearing than it turned out to be; keeping that research inline
since it's still accurate about what the SDK can do, just not the critical
path for this loop). Design rule of thumb: build/validate primarily against
real hardware (L6/L7/L8, no emulator) when a physical download-and-run check
is actually warranted — not the default per-sample step. Real unit available
for that: a 5069-L306ERS (CompactLogix 5380-class, no safety program on it).

Researched 2026-08-20 (see OQ-GENMETHOD for sourcing): Rockwell publishes an
official **Logix Designer SDK** (.NET, `RockwellAutomation.LogixDesigner`)
plus two CLI tools built on it in `RockwellAutomation/ra-logix-designer-vcs-custom-tools`
(GitHub) — `l5xplode`/`l5xgit`. `l5xgit l5x2acd --l5x <file> --acd <file>` converts
L5X → ACD headlessly, no Logix Designer UI interaction. This is real and confirmed
(Rockwell's own repo, requires Logix Designer SDK 2.2+), not a hypothetical.
`scripts/batch_l5x_to_acd.ps1` in this repo wraps it over a whole folder.

What's confirmed to exist in the SDK beyond that (via `ra-logix-cicd`'s
`LogixDesigner_ClassLibrary`/`LogixEcho_ClassLibrary` sample code): `LogixProject`
exposes `SaveAsync`/`DownloadAsync`/`SetCommunicationsPathAsync` and per-type
`GetTagValue*Async`/`SetTagValue*Async` once online, and separately the
**FactoryTalk Logix Echo** SDK can spin up an emulated chassis+controller
straight from an ACD file. Neither is needed for the default loop now that
offline compile is enough — worth revisiting only if the SDK turns out to
also expose a scripted "verify project, read compiled memory stat" call
*without* going online, which would close the automation loop with zero
hardware involved at all. Not yet researched; flag for whoever picks this up
next rather than assumed.

**RESOLVED 2026-08-20 (OQ-MEMREADMETHOD): there is no programmatic memory
read, online or offline.** GSV has no memory attribute on any Logix 5000
platform, and Rockwell's documented MSG/CIP path is explicitly unsupported
on the entire current controller lineup regardless. Controller Properties →
Memory tab, read by eye, is the only method — but per the correction above,
it only requires an offline compile, not a download.

1. Convert the sample L5X to ACD (`scripts/batch_l5x_to_acd.ps1`, batchable —
   no per-sample manual import).
2. Open in Logix Designer, verify/compile (no errors — a sample that doesn't
   compile is not valid data). No download, no going online.
3. Read memory used: Controller Properties → Memory tab (bytes used / bytes
   free) — this is the only method, confirmed, and available right after
   compile. `scripts/batch_memory_capture.ps1` opens each converted ACD in
   turn and prompts for this number so the file-hunting and manifest-row
   formatting isn't manual too, even though the read itself always will be
   (update that script's comments to stop implying a download step).
4. Record predicted vs. actual, delta.
5. Log to `samples/manifest.csv` (batch_memory_capture.ps1 does this per-row,
   resumable across a multi-session batch of hundreds of samples).

Keep controller model/firmware rev consistent across a comparison set (don't
mix CompactLogix models mid-test — memory reporting granularity may differ),
but there's no shared physical resource to reset between samples anymore
since nothing gets downloaded — each ACD compile is independent.

Occasional spot-check against the 5069-L306ERS (actual download, real
running memory) is still worth doing periodically to confirm compiled/
offline-shown memory actually matches what the controller reports once
running — not proven identical yet, just assumed for now.

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
