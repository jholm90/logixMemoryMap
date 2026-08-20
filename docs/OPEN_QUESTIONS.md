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

**OQ-L5XVERSION — RESOLVED (2026-08-20).** Primary target: **v35** (L8x /
CompactLogix 5380-class processors) — this is where Phase 3 validation
testing will primarily happen. Spot-check cross-version compatibility later
against an **L6 v20** processor and an **L7 v30** processor. Build/test
against v35 schema first, but don't hardcode assumptions that only hold for
v35 — the L6/L7 spot checks exist specifically to catch schema drift.

Checked this project's own real sample files against that plan: 3 of 4
(`BAI10048...`, `BaillieLeitchField_Edger...`, `SJ_Gormley...`) are v35
projects at the top level, matching. `311DGeneratedProgram.L5X` is a v32
`TargetType="Program"` snippet export (an older/different project this was
cut from) — not v35, and not a Controller-level export either, so it's an
outlier in the current corpus, not representative of the v35/v20/v30 plan.
(Nested per-element `SoftwareRevision` values inside the v35 files, ranging
v16–v32, are individual module/AOI authored-at versions embedded in the
export, not the project's own schema version — don't confuse the two.)
v20/v30 schema differences remain completely unvalidated — no sample data
for either yet.

**OQ-TOLERANCE — RESOLVED (2026-08-20).** James: 1% delta = good, 3% =
acceptable, 5% = very poor. Explicitly tiered by James along the same
exact/estimated split already built into the tool (`sizing/report.py`'s
`tier` field): **tag/UDT/data-space memory should be within 1%** — that's
the "exact" tier, it's calculable, it should actually be accurate. Program/
logic-structure memory "is a guess at best so that's where the slop will
be" — the "estimated" tier from Phase 4+ doesn't get held to the 1%/3%/5%
bar the same way; no specific number given for it, and given James's own
framing ("a guess at best"), pushing for a tight tolerance there would be
fighting the nature of the problem rather than solving it. Phase 3 exit
criterion (tag/UDT only): 1% good, 3% acceptable, >5% means the model has a
real gap worth chasing before calling that phase done — not a rounding
error to shrug off.

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
counting toward any total. **Updated 2026-08-20 after Phase 2b (AOI-instance
sizing) landed** — that fix also resolved every AOI-nested reference to these
same types (e.g. an AOI LocalTag typed `TIMER` inside another AOI), so the
counts below are what's left of the 300 remaining errors (down from 1411 at
session start) across 4 real files, 3394 tags total:

| Type | Count | Notes |
|---|---|---|
| MOTION_INSTRUCTION | 86 | |
| AXIS_CIP_DRIVE | 64 | |
| FBD_TIMER | 47 | FBD (function block diagram) variant of TIMER, different layout, don't assume it's also 12 bytes |
| AxisSTO | 29 | likely Safety/Guard I/O device-profile-generated |
| DCI_STOP | 26 | likely Safety/Guard I/O device-profile-generated |
| RATE_LIMITER | 10 | |
| CONFIGURABLE_ROUT | 7 | |
| AXIS_VIRTUAL | 5 | |
| GateBox | 5 | |
| MESSAGE | 4 | real MSG structure is large/version-dependent, do not guess |
| MOTION_GROUP | 3 | |
| CAM_PROFILE | 4 | |
| a handful of others (≤3 each) | ~14 | `Ud_Sensor`, `JulianDay`, `IO_Block`, module-connection-style names like `AB:ENC1_DIAG:I:0`, all in the one `TargetType="Program"` partial export -- likely types only fully defined in the parent project this snippet was cut from, not a parser gap |

None of these get a guessed size -- they need either real Rockwell
documentation confirming a stable byte layout (like TIMER/COUNTER/CONTROL
already have) or empirical Phase 3 measurement before going in
MEMORY_MODEL.md. Motion/axis structures (MOTION_INSTRUCTION, AXIS_CIP_DRIVE,
AXIS_VIRTUAL, MOTION_GROUP = 158 occurrences) are the highest-frequency and
most worth chasing next, and motion axis structures are known to be large,
so likely a meaningful chunk of unaccounted memory in motion-heavy programs
specifically.

**OQ-AOIINSTANCE — NARROWED (2026-08-20).** Named AOI-instance tags (a real
Tag with `DataType=<AOIName>`) are now sized (Phase 2b, see MEMORY_MODEL.md)
and turned out to be 660 of 3394 tags in real production data — the
overwhelming majority of real AOI usage, and it needed no logic parsing at
all since it's sized exactly like a UDT-typed tag. What's still genuinely
open is narrower than originally scoped: does an AOI called in logic
*without* a named backing tag (an inline/anonymous instance, if Logix even
allows that) allocate memory the same way, and does it need call-site
counting from logic parsing to size? Real sample data didn't turn up an
example of this happening, so it's unclear how common (or possible) it even
is — worth checking whether Logix Designer actually permits an AOI call
without a backing tag before investing more here.

**OQ-AOIBOOLPACK — NEW (2026-08-20).** Do BOOL Parameters/LocalTags inside an
AOI definition pack 8-per-byte the way UDT BOOL members do (OQ-BOOLPACK/
OQ-ALIGN), or allocate unpacked like a standalone tag? The L5X evidence points
away from UDT-style packing: AOI BOOL Parameters/LocalTags appear as plain
`DataType="BOOL"` elements with no hidden-SINT/BIT-alias representation the
way a UDT's BOOL members always get. Implemented as unpacked (4 bytes) since
that matches what the XML actually shows, but this is inference from XML
shape, not a confirmed fact — needs the same kind of empirical Phase 3
confirmation as OQ-BOOLPACK, just for AOI instance structures specifically.

**OQ-COMMENTS** — Do tag descriptions, rung comments, and routine comments
consume controller memory at all, or are they development-environment-only
(stripped at compile/download)? If they do consume memory, that's a very
different kind of "memory hog" to flag (verbose commenting habits) than data
structure bloat.

**OQ-ALARM — PARTIALLY RESOLVED (2026-08-20), scope split in two.** James:
alarms are part of standard code, worth adding to the necessary list — but
specifically via **extended tag properties** (min/max/HH/H/L/LL-style alarm
limits configured directly on a tag), which is what FactoryTalk View reads
to display/trigger controller alarms in his shop's standard programs.
**ALMD/ALMA alarm instruction tags are never used** — confirmed out of
scope, don't bother modeling those.

So: extended tag properties are IN SCOPE for the tool (needs an
extended-properties parser eventually, Phase 1/1-adjacent work), ALMD/ALMA
is OUT — cut entirely rather than deferred, no need to revisit later like
OQ-SAFETY. Still open: whether extended tag properties cost any *memory* at
all beyond the tag's own data size, and if so how much — that's a genuine
new sizing question (call it OQ-ALARMPROPBYTES if it needs its own ID once
someone picks this up) that wasn't resolved by this scoping answer, just
confirmed as worth answering.

**OQ-SAFETY — RESOLVED (2026-08-20).** Out of scope for launch entirely —
backlog/feature-request item only ("Phase 99"), not a near-term phase. Tool
should explicitly warn/refuse on safety-enabled projects for now rather than
attempt a wrong combined number; building real GuardLogix safety-pool support
is deferred indefinitely, not scheduled.

## Logic sizing

**OQ-JSRSHARED** — When a subroutine is called from multiple places (shared
JSR target), does its compiled size get counted once (memory) or does each
call site duplicate the routine body? Standard structured-programming
assumption is "compiled once, called many times" (call site only costs the
JSR overhead, not the routine body again) — needs confirmation, and materially
changes the call-tree rollup logic in Phase 5.

**OQ-INSTRUCTIONSCOPE — RESOLVED (2026-08-20), real data not guessed.** Ran a
frequency count across all 4 real production L5X files instead of asking
James to recall from memory: 24,941 instruction instances across 434 RLL
routines + 126 ST routines (0 SFC, 0 FBD routines found — drop those from
scope entirely, not worth building a parser for logic formats that don't
appear in real usage).

| Category | Instructions (uses) |
|---|---|
| Bit logic | XIC 8406, OTE 3424, XIO 2940, OTL 572, OTU 725, ONS 676 — dominates by far |
| Compare/move/math | MOV 1941, EQU 951, ADD 280, NEQ 242, GRT 231, MUL 213, GEQ 173, LES 164, SUB 109, LIM 98, LEQ 96, DIV 85, CPT 66, MOD 15, CMP 15, MEQ 3 |
| Timers/counters | TON 445, RTO 39, TOF 28, CTU 25 (no CTD seen) |
| Motion | MAM 10, MAS 9, MAJ 7, MAH 5, MSO 5, MSF 5, MDW 4, MAW 4, MASR 3, MAFR 3 — confirmed real and varied, James: "lots of motion instructions, camming" |
| Cam/route | DCS 37, CROUT 16 — matches CONFIGURABLE_ROUT/cam-related structure types already found unresolved in OQ-PREDEFINED |
| GSV/SSV | GSV 101, SSV 47 — confirmed real, James called these out explicitly |
| Program flow | JSR 238, JMP 31, LBL 27, SBR 6, RET 4 |
| Array/file | COP 292, CLR 457, FLL 42, BTD 71, MVM 20, BSL 2, BSR 2 |
| String | CONCAT 312, DTOS 22, SIZE 20, MID 1, TRUNC 4, FIND 1 — some string handling, just not ASCII-module instructions specifically |
| MSG | 4 — barely used, don't over-invest in getting its structure size right |
| Not seen at all | PID, ASCII-module instructions (AHL/ARD/AWT/etc), SFC, FBD |

Phase 4/4b instruction scope in TASKS.md updated to match: bit logic first
(by far the highest-frequency, as already planned), then compare/move/math,
then motion+cam+GSV/SSV (previously not planned for at all, now confirmed
must-have given real frequency), then array/string/program-flow. PID and
ASCII-module instructions dropped from scope entirely — zero real usage
found, not worth fitting weights nobody needs.

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

**OQ-EMULATE — RESOLVED (2026-08-20).** Real hardware only, no Logix Emulate
— explicit design rule of thumb: "primarily run on hardware L6/L7/L8 and not
emulators." Real unit available for validation: a 5069-L306ERS (CompactLogix
5380-class) with no safety program on it currently. This also settles the
emulate-vs-real question that OQ-MEMREADMETHOD's Logix Echo research left
open — moot now, not being used regardless of whether it would have worked.

**Bigger finding from the same answer, corrects OQ-MEMREADMETHOD's
procedure (not its programmatic-access conclusion):** James doesn't need to
download to hardware at all for memory validation. Logix Designer shows
memory usage in Controller Properties as soon as the project successfully
**compiles/verifies offline** — no online/download step required. This was
an incorrect assumption baked into `docs/TESTING_PLAN.md`'s procedure (step
4 currently says "download to controller or Emulate" before reading memory)
and into how big a deal the Logix Echo/download research seemed — the real
loop is just: convert L5X→ACD (`scripts/batch_l5x_to_acd.ps1`) → open in
Logix Designer → verify/compile → read Controller Properties → Memory tab.
No hardware, no emulator, no online session needed for the bulk of sample
validation. The 5069-L306ERS is still worth having for occasional spot
double-checks (compiled-memory-estimate vs. actual-downloaded-and-running
memory could theoretically differ), but it's not the default per-sample
loop. TESTING_PLAN.md needs updating to match — see that file.
