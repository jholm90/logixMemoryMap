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

## Feedback loop shape

```
generate sample → predict bytes (this tool) → import/download (Studio 5000)
→ read actual bytes → log to manifest → diff → adjust MEMORY_MODEL.md
→ re-predict all prior samples with new constants → confirm no regressions
```

That last step matters — a constant tuned to fix sample #12 can silently break
the prediction for sample #4. Re-run the full manifest's predicted-vs-actual
comparison after every constant change, not just the sample that prompted it.
