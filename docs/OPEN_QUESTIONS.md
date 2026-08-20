# Open Questions

Every unresolved question gets an ID (OQ-xxx) so PROJECT_PLAN.md and TASKS.md
can reference it instead of restating it. Resolve in place — don't delete, mark
**RESOLVED** with the answer and date so the reasoning trail survives.

## Scope / stack

**OQ-STACK — RESOLVED (2026-08-19).** Parser/sizing engine: Python. Public
release intended, so standard OSS packaging applies (setup.py/pyproject.toml,
pip-installable, CLI entry point). UI framework still open — a Python-native UI
(e.g. a local web server + the existing treemap plan rendered in-browser) keeps
the whole project one language, which matters more now that it's public and
contributors shouldn't need two toolchains to build it.

**OQ-L5XVERSION** — Which Logix Designer / L5X schema version(s) must this
support? Studio 5000 versions have changed L5X schema details over the years
(attribute additions, AOI signature format, etc). Need to pin a minimum
supported version or handle multiple.

**OQ-TOLERANCE** — What delta between predicted and actual bytes counts as
"good enough" for Phase 3 exit? 1%? 0.1%? Exact match? Exact match may be
unrealistic given unknowns like alignment padding; need an agreed threshold
before Phase 3 can formally close.

## Tag / UDT / AOI sizing

**OQ-BOOLPACK** — Confirmed that standalone BOOL controller/program tags each
consume a full 4-byte DINT-equivalent allocation (not bit-packed) in Logix —
**needs empirical confirmation in Phase 3**, this is memory from general Rockwell
knowledge, not yet validated against this tool's actual test data. BOOL members
*inside a UDT* pack 8-per-byte (SINT-backed), which is why the L5X BIT-member
generation rule in memory already exists for UDT authoring — need to confirm
sizing matches that packing exactly including partial-byte members.

**OQ-ALIGN** — Does Logix pad UDT members to 4-byte alignment boundaries (like
C struct padding), or is it byte-packed with no alignment? This changes total
UDT size whenever member order mixes types (e.g. BOOL, DINT, BOOL — does the
second BOOL start a new byte, pad to next DINT boundary, or pack tight?).
Directly affects whether member *order* in a UDT affects its memory footprint —
if alignment is real, reordering members for tight packing is itself a finding
worth surfacing in the UI ("reorder these members to save N bytes").

**OQ-BOOLARRAY** — BOOL *array* tags (as opposed to standalone BOOL tags,
OQ-BOOLPACK) are assumed to bit-pack 32-per-DINT-sized-word (`ceil(n/32) × 4`
bytes), standard documented AB behavior. Implemented in the sizing engine as
ASSUMED pending Phase 3 confirmation against this project's own sample data —
don't conflate with OQ-BOOLPACK, which covers scalar standalone BOOL tags.

**OQ-ARRAYPACK** — For an array of UDTs, is padding applied per-element
(so each element wastes the same padding) or is the array treated as one
contiguous block? Affects array-of-UDT formula.

**OQ-PRODCONS** — Produced/consumed tag connection overhead formula unknown.
Need to isolate: base connection overhead (fixed per connection) vs. per-byte
payload cost vs. number of consumers of a single produced tag (does producing
to 3 consumers cost 3x, or is overhead shared?).

**OQ-AOIINSTANCE** — Does each AOI *call site* in logic allocate a full new set
of local tag memory, or can Logix share/optimize in any case? Assumption is
full per-instance allocation (this is standard AOI behavior) but needs
confirmation, and needs the call-site count to come from logic parsing —
creates a Phase 1 / Phase 4 dependency that TASKS.md currently stubs.

**OQ-COMMENTS** — Do tag descriptions, rung comments, and routine comments
consume controller memory at all, or are they development-environment-only
(stripped at compile/download)? If they do consume memory, that's a very
different kind of "memory hog" to flag (verbose commenting habits) than data
structure bloat.

**OQ-ALARM** — Extended tag properties (min/max/units) and ALMD/ALMA alarm
instances add memory beyond raw tag data size. In scope for v1, or deferred to
Phase 6 / cut entirely? Affects whether Phase 1 needs an extended-properties
parser now.

**OQ-SAFETY** — Safety task tags/logic live in a separate protected memory
region on GuardLogix-class controllers. Since target is CompactLogix, is this
relevant at all, or should the tool explicitly refuse/warn on safety-enabled
projects rather than produce a wrong combined number?

## Logic sizing

**OQ-JSRSHARED** — When a subroutine is called from multiple places (shared
JSR target), does its compiled size get counted once (memory) or does each
call site duplicate the routine body? Standard structured-programming
assumption is "compiled once, called many times" (call site only costs the
JSR overhead, not the routine body again) — needs confirmation, and materially
changes the call-tree rollup logic in Phase 5.

**OQ-INSTRUCTIONSCOPE** — TASKS.md Phase 4b lists a specific instruction set
based on what's actually common in production programs. Confirm this list
covers James's actual usage before investing sample-generation effort — no
point fitting weights for instructions never used (e.g. is PID in scope? ASCII
string instructions? SFC?).

## Sample generation / testing

**OQ-GENMETHOD** — Can generated L5X files be imported directly via Studio
5000 File→Import without manual cleanup, or do hand-built XML samples need
adjustment (missing GUIDs, checksums, schema quirks) before Logix Designer will
accept them? First sample in Phase 3 should answer this immediately — if
generated files don't import cleanly, the whole testing loop needs a different
approach (e.g. generating via Logix Designer's own automation/API instead of
raw XML authoring).

**UPDATE 2026-08-20 — CONFIRMED, partially resolves this OQ.** Verified against
Rockwell's own GitHub repos (`RockwellAutomation/ra-logix-designer-vcs-custom-tools`,
`RockwellAutomation/ra-logix-cicd`), not just marketing copy:
- `l5xgit l5x2acd --l5x <file> --acd <file>` (official CLI, built on the Logix
  Designer SDK) converts L5X → ACD with no Logix Designer UI involved. This
  answers the batch-compile half of OQ-GENMETHOD directly — it's a real,
  scriptable, Rockwell-supported path, not raw-XML File→Import at all, so the
  "does hand-built XML import cleanly" risk this OQ originally worried about
  is sidestepped for the conversion step (still relevant for whether the
  *generator's* L5X content itself is schema-valid, which is a generation-time
  concern, not a conversion-time one).
- The SDK's `LogixProject` class (confirmed via `ra-logix-cicd` sample code)
  exposes `DownloadAsync`, `SetCommunicationsPathAsync`, and per-type
  `GetTagValue*Async`/`SetTagValue*Async` once online.
- The FactoryTalk **Logix Echo** SDK can create an emulated chassis+controller
  straight from an ACD file (`CreateChassisFromACD`) and return a comms path —
  no manual Emulate GUI setup per sample.

`scripts/batch_l5x_to_acd.ps1` in this repo wraps the l5xgit conversion over a
whole folder. Still open: whether SDK-driven download+online actually behaves
identically to a GUI-driven one for compile-error detection, and the
GSV/memory-read piece, which stays with OQ-MEMREADMETHOD below.

**OQ-MEMREADMETHOD** — Best method to read actual controller memory usage
after download: Studio 5000 Controller Properties → Memory tab (manual read),
or a GSV (Get System Value) instruction reading a memory-related system
attribute for a fully scripted read-back? GSV approach would let sample
generation AND memory read-back both be automated — worth confirming which
GSV attributes actually expose this (e.g. WHO/CPU memory attributes) before
committing to the manual-read workflow in TESTING_PLAN.md. See LDSDK note
under OQ-GENMETHOD — if GSV exposes it and the SDK can read the tag, this
closes without ever touching the Controller Properties dialog. STILL UNRESOLVED
as of 2026-08-20 — the SDK research confirmed the *plumbing* to read an
arbitrary tag value back programmatically (`GetTagValue*Async`), but did not
turn up confirmation that any GSV attribute actually surfaces memory-used/free.
Interim fallback in place: `scripts/batch_memory_capture.ps1` opens each
converted ACD in Studio 5000 and prompts for a manually-read number — not
automated, but removes the per-sample file-hunting/manifest-formatting toil
so a batch of hundreds of samples doesn't have to be pointed-and-clicked by
hand. Whoever spikes the GSV question next should check the Get System Value
instruction's `WHO`/controller-memory-attribute class list in the current
Logix Designer instruction help.

**OQ-EMULATE** — Is validation done against a real CompactLogix, or Logix
Emulate? If emulate, confirm memory reporting matches real hardware behavior
(not guaranteed — emulate is a different runtime).
