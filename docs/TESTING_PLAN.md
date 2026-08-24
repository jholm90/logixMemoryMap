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

## Window-title-mismatch retries are automatic (James, 2026-08-25)

"Any test that fails for window title mismatch should be rerun... make sure
you can rerun those tests next time without me prompting you." The AHK/
PowerShell capture loop cross-checks the Logix Designer window title against
the file it just asked to be opened (`batch_memory_capture.ps1`) — a
mismatch means the automation may have read stale data (a real confirmed
case: a request for one file came back with the previous file's title still
showing, the switch silently hadn't happened yet). That row's `actual_bytes`
is untrustworthy and gets flagged `WINDOW TITLE MISMATCH` in `notes`, but
until 2026-08-25 the script's own "already logged" check only looked at
whether `actual_bytes` was non-empty — a mismatched row still has a (wrong)
value there, so it silently counted as done forever and never got retried
without someone manually blanking the row.

**Fixed at the source, not by hand-editing rows each time:**
`batch_memory_capture.ps1`'s already-logged filter now also excludes any row
whose `notes` still says `WINDOW TITLE MISMATCH` — that row is treated as
never-captured and gets picked back up automatically the very next time the
script runs against the same `convert_log.csv`. No ACD rebuild needed:
`convert_log.csv` already has `status=ok` for it (the L5X→ACD conversion
succeeded; only the *capture read* was suspect), so a retry just re-opens
the existing ACD and re-reads the Capacity tab. A successful retry naturally
clears the flag (the row's `notes` gets overwritten with the fresh
cross-check result), so this self-heals with no manual bookkeeping on
either side. On this project's side: any manifest reconciliation (merging
in a pushed capture batch) also blanks the capture columns for rows still
carrying that flag rather than trusting the stale `actual_bytes`, so a
retry is never skipped just because the row "looked" logged.

## Zero-Capacity retries are automatic too (James, 2026-08-27)

"if memory size is 0 it needs to be flagged and not counted." A real
controller's Capacity-tab reading is never actually 0 (every project carries
the `empty_project_baseline` floor at minimum), so a literal `"0"`
`ocd_value` from AHK is a bad-read symptom (wrong dialog/field focused, a
timing glitch), not real data. Same fix, same mechanism as the window-title
case above: `batch_memory_capture.ps1` flags it `ZERO CAPACITY` in `notes`
and excludes that row from "already logged," so it's automatically retried
next run with no manual re-flagging needed.

## 1769-series (CompactLogix 5370) requires clicking "Estimate" first (James, 2026-08-27)

"the 1769 processors require 'estimate' button before giving memory sizes."
Real Studio 5000 UI behavior, confirmed against real capture attempts:
1756/5069-family processors show a real Capacity number in Controller
Properties immediately, but 1769-series (`v35_l16er`/`l18er`/`l18erm`/`l19er`/
`l24er`/`l24er_qbfc1b`/`l27erm_qbfc1b`/`l33er`/`l30erm`, all real 1769-L1xER/
L2xER/L3xER catalog numbers) don't — the "Estimate" button has to be clicked
first before the tab shows anything meaningful. **The AHK loop does not do
this today** and would silently read a stale/blank/wrong value for any
1769-series file without it. All 9 of the currently-staged 1769 points were
manually reported by James for this reason (see `manifest.csv` notes,
`MANUAL ENTRY`), not captured automatically. **Before building or capturing
any FUTURE 1769-series test file**, `logix_build_capture.ahk` needs an extra
click-Estimate step added for that processor family specifically, or every
such row needs to keep going through manual reporting.

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

Phase 3 and Phase 4/4b each close per PROJECT_PLAN.md's stated exit criteria.
Tolerance resolved (OQ-TOLERANCE, 2026-08-20): **tag/UDT (exact tier) within
1% = good, 3% = acceptable, >5% = a real gap worth chasing, not a rounding
error.** Logic/program-structure memory (estimated tier) isn't held to the
same bar — James: "a guess at best," so that's expected to carry more slop
by nature of the problem, not a target to force down to 1%. Don't move to UI
work (Phase 5) with an open, unresolved tag/UDT discrepancy just because
logic sizing is more interesting — an error in the "exact" tier undermines
the tool's whole value proposition more than an acknowledged estimate in the
logic tier does.
