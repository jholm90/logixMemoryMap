# Sample Generation

Need a repeatable, scriptable way to produce the 30-40+ test L5X files without
hand-clicking each one in Studio 5000.

## Open question first (OQ-GENMETHOD)

L5X is just XML, so it's mechanically generatable — the real question is
whether Logix Designer's File→Import will accept hand-built XML cleanly, or
whether it needs GUIDs/checksums/schema quirks that make raw authoring
unreliable. **First sample generated should go straight through the full
TESTING_PLAN.md loop (import → compile → download) before writing a generator
for the other 29+.** If import fails or requires manual fixup, pivot to one of
the fallback approaches below rather than fighting hand-authored XML.

## Approach A — Direct XML authoring (preferred if OQ-GENMETHOD confirms it works)

Template-based generation: a script takes parameters (element count, data
type, nesting depth, instruction type, rung count) and emits valid L5X XML
matching Rockwell's schema for that content type. Fastest iteration — no
Studio 5000 UI automation needed, just XML templates + a parameter sweep.

Needs, at minimum:
- Tag element template (name, data type, dimensions)
- DataType (UDT) template (name, members list)
- AddOnInstructionDefinition template
- Rung/Routine template (instruction text, comments)
- A minimal-but-valid Controller wrapper (the boilerplate every L5X needs:
  controller element, single empty task/program/routine, RSLogix5000Content
  root with correct SchemaRevision/SoftwareRevision matching OQ-L5XVERSION)

## Approach B — Studio 5000 automation (fallback if raw XML import is unreliable)

Logix Designer has a COM/.NET automation interface. A C# script (fits existing
toolchain — same pattern as the WinForms V36 converter) could programmatically
create tags/UDTs/logic in an open project, which sidesteps any raw-XML
schema-fidelity problems since Logix Designer itself generates the L5X on
export. Slower per-sample (UI automation overhead) but guaranteed valid.

## Approach C — Hybrid

Generate the bulk structure via Approach A (fast), but if any sample fails to
import cleanly, hand-fix that one sample in Studio 5000 UI and re-export as the
template for that category going forward. Practical middle ground — don't
over-invest in perfecting the XML generator for edge cases that hit once.

## Naming / organization

- `samples/generated/<category>/<sample_id>_<short_desc>.L5X`
- Every generated sample gets a row in `samples/manifest.csv` at creation time
  (predicted_bytes filled in immediately from the tool's own calculation;
  actual_bytes filled in after the TESTING_PLAN.md loop runs)
- Keep generator scripts in `src/sample_gen/` so a sample can be regenerated
  exactly (not hand-edited and drifted from its own generator)

**Generator CLI built 2026-08-20** (James: "the l5x generator application
where you make up the l5x files based on things you want to test"):
`python -m sample_gen.cli {udt,tags,rungs} ...` -- see that module's
docstring for exact flags. `udt` builds a UDT + one tag of it (matches the
now-confirmed BOOL-packing-run rule exactly, see OQ-ALIGN); `tags` builds N
tags of a given type/dimensions; `rungs` builds N rungs of an instruction
pattern with an optional filler comment (OQ-COMMENTS). All three write the
L5X, compute predicted_bytes via this project's own sizing engine, and log
a manifest.csv row automatically -- actual_bytes stays blank until run
through `scripts/batch_l5x_to_acd.ps1` + `scripts/batch_memory_capture.ps1`
(both resumable, "press any key to stop" / "close the window at any time"
per James's spec) or manually through Studio 5000.

## Feedback loop shape

```
generate sample → predict bytes (this tool) → import/download (Studio 5000)
→ read actual bytes → log to manifest → diff → adjust MEMORY_MODEL.md
→ re-predict all prior samples with new constants → confirm no regressions
```

That last step matters — a constant tuned to fix sample #12 can silently break
the prediction for sample #4. Re-run the full manifest's predicted-vs-actual
comparison after every constant change, not just the sample that prompted it.

## Before hand-picking catalogs into any script (including one-off chat samples)

James, 2026-09-03, real Studio 5000 errors that were both **already
diagnosed and fixed elsewhere in this codebase** before being rebuilt from
scratch by hand: (1) `193-ECM-ETR/A` used directly in a scratch sample --
already in `gen_composite_realistic.py`'s `_UNDIAGNOSED_COMPOSITE_CATALOGS`
exclusion set with a documented real "Child module incompatible with
parent module" error; James's response was to delete it from
`_MODULE_CHAINS` entirely. (2) Several real 5069 Compact I/O catalogs
combined onto the default 1756-L81E non-safety controller -- `gen_module_
sweep.py` already documents (2026-08-27) that 5069 modules need
`_5069_PROCESSOR_TYPE = "5069-L306ER"` (a 5069-series processor, not
1756-L81E -- `Type="5069"` Ports only match a 5069 controller's own local
bus) and that 2 of the 6 (`_5069_SAFETY_CATALOGS`) are
`SafetyEnabled="true"`, needing `5069-L306ERMS2` (safety-rated). James:
"You need to do better checking on safety stuff... you need to 'read'
these modules and use your logic to verify safety stuff cannot go on
non-safety processors."

**Before writing ANY script that picks catalogs by name** (`_MODULE_CHAINS`
keys, `_5069_*`, `_UNDIAGNOSED_*`, etc.), grep this file's own generators
for that catalog first -- an existing exclusion set, a dedicated processor-
type constant, or a safety-catalog set means the question is already
answered. `sample_gen.lint.lint_l5x` now also catches the safety case
mechanically (`safety_module_on_non_safety_controller`, checks every
Module's own `SafetyEnabled="true"` against the file's `<SafetyInfo>`
presence) -- run it on every generated file before sending it anywhere,
scratch chat samples included, not just committed batches.

## After fixing a generator bug: the committed files don't fix themselves

James, 2026-09-04, caught via his own `batch_l5x_to_acd.ps1` output showing
files still queued for conversion that had already been reported "fixed" in
chat. Real gap found: `gen_module_pointio_rack.py`'s Bus Size/slot-resize
fix landed in the generator SOURCE (2026-09-03), and a direct in-memory
test of the fixed function was reported to James as verification -- but the
actual COMMITTED `rack_pointio_n02...n07_full/_alt` files in `samples/
generated/` were never regenerated afterward. They still had the old,
pre-fix content (last touched by an earlier commit), so they kept showing
`FAILED`/never-logged in `convert_log.csv` -- not because the fix was
wrong, but because the shipped files never picked it up. A code fix is not
done until `python -m sample_gen.<module>` has actually been re-run and the
resulting file diff committed -- verifying the FUNCTION in isolation is not
the same as verifying the FILE that ships. Same session, a parallel check
on `cipmodule_scale_*.L5X` (also flagged in the same PowerShell output)
found the opposite: regenerating changed nothing but the export timestamp
-- that fix had already made it into the committed files; the file was
just sitting on a stale, never-retried `FAILED` log entry from before the
fix landed. Distinguishing these two cases (stale FILE vs. stale LOG
entry) needs an actual regeneration + diff, every time -- not an assumption
either way.
