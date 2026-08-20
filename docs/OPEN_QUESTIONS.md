# Open Questions

Every unresolved question gets an ID (OQ-xxx) so PROJECT_PLAN.md and TASKS.md
can reference it instead of restating it. Resolve in place — don't delete, mark
**RESOLVED** with the answer and date so the reasoning trail survives.

## Scope / stack

**OQ-STACK — RESOLVED (2026-08-19, UI half resolved 2026-08-20).**
Parser/sizing engine: Python. Public release intended, so standard OSS
packaging applies (setup.py/pyproject.toml, pip-installable, CLI entry
point). UI: local Flask server (`l5x-memory-analyzer ui <path>`) + a
hand-rolled vanilla JS/SVG squarified treemap in the browser — deliberately
no D3 or any CDN-loaded JS, since engineering workstations running Studio
5000 are frequently on airgapped OT networks and a public tool can't assume
the browser has internet access at runtime. Keeps the whole project
pip-installable in one language plus a dependency-free frontend.

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

**OQ-PREDEFINED — NEW (2026-08-20), found by running the sizing engine
against James's own real production L5X files.** Beyond TIMER/COUNTER/
CONTROL (now modeled, see MEMORY_MODEL.md), real programs reference a long
tail of other firmware-native/library structure types that also never get a
member list in `Controller/DataTypes`, so they currently surface as explicit
sizing errors (correct/honest behavior per the ground-truth constraint --
better an explicit error than a silently wrong guessed number) rather than
counting toward any total. Frequency across 4 real files (3394 tags, 1411
total sizing errors):

| Type | Count | Notes |
|---|---|---|
| MOTION_INSTRUCTION | 20 | |
| AXIS_CIP_DRIVE | 64 | |
| AXIS_VIRTUAL | 5 | |
| MOTION_GROUP | 3 | |
| MESSAGE | 4 | real MSG structure is large/version-dependent, do not guess |
| ts_CIPAxis, ts_MContactAxis, ts_VFDAxis | 63 combined | not in DataTypes or AOI defs in the source file -- likely from an external motion/axis library this project references but doesn't locally re-export |
| DCI_STOP, CONFIGURABLE_ROUT, AxisSTO | 61 combined | likely Safety/Guard I/O device-profile-generated structures |
| FBD_TIMER | 5 | FBD (function block diagram) variant of TIMER, different layout, don't assume it's also 12 bytes |

None of these get a guessed size -- they need either real Rockwell
documentation confirming a stable byte layout (like TIMER/COUNTER/CONTROL
already have) or empirical Phase 3 measurement before going in
MEMORY_MODEL.md. Motion/axis structures (AXIS_CIP_DRIVE etc.) are the
highest-frequency and most worth chasing next: 64+63+5+3 = 135 occurrences,
and motion axis structures are known to be large, so likely a meaningful
chunk of unaccounted memory in motion-heavy programs specifically.

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

**OQ-MEMREADMETHOD — RESOLVED 2026-08-20, and the answer is bad news for full
automation.** Deep-dive against Rockwell's own docs (converging, independently
repeated results across multiple searches, all pointing at the same official
page — not a single unverifiable snippet):

- **GSV cannot read memory usage at all, on any controller.** There is no
  memory-used/free attribute exposed through the GSV instruction on any
  Logix 5000 platform. Confirmed dead end — stop looking here.
- Rockwell **does** document a programmatic path, but it's MSG-based, not
  GSV: an explicit CIP message (Get Attribute) that returns available/total/
  largest-contiguous **I/O and expansion memory**, as 32-bit values split
  across two INTs. Official page: "Determine Controller Memory Information"
  (`rockwellautomation.com/.../instruction-set/input-output-instructions/
  determine-controller-memory-information.html`, part of the Studio 5000
  Logix Designer 37.00 instruction set docs).
- **That MSG path is explicitly unsupported on the entire current controller
  lineup.** Rockwell's own page states: *"This information is not applicable
  to CompactLogix 5380, CompactLogix 5480, ControlLogix 5580, Compact
  GuardLogix 5380, and GuardLogix 5580 controllers, as the memory used
  attributes are not supported or accessible in these controllers."* It only
  works on legacy families (e.g. 1756-L55-class ControlLogix / older
  CompactLogix 5370-generation hardware).

**Conclusion for this project:** since CompactLogix 5380 is the current
product line and the presumed target (confirm against James's actual
controller model), **there is no programmatic path to memory usage** —
not GSV, not MSG/CIP, nothing documented. Controller Properties → Memory tab
is not a stopgap, it's the only method available on target hardware. This
also means Logix Echo emulator automation (see OQ-GENMETHOD) buys nothing
for memory reading specifically — it would only be worth building if some
other part of the loop needed online access (it doesn't, currently).
`scripts/batch_memory_capture.ps1` is scoped correctly for this reality
already: it never assumed a scripted read, only streamlined the
file-hunting/manifest-formatting around a manual one. If a legacy
1756-L55-class or CompactLogix 5370-gen controller ever enters the sample
set, the MSG path becomes viable for those specific samples and could be
worth automating then — not before.

**OQ-EMULATE** — Is validation done against a real CompactLogix, or Logix
Emulate? If emulate, confirm memory reporting matches real hardware behavior
(not guaranteed — emulate is a different runtime).
