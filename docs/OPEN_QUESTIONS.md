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

**OQ-EXPORTSCOPE — NEW (2026-08-20), backlog feature request, not scheduled.**
James: the tool needs to eventually filter/handle Controller exports as well
as Program/UDT/AOI-only exports (Logix Designer can export any of those
individually, `TargetType` on the L5X root reflects which), but "we will
focus on controller exports today." Implemented today: `L5XDocument` now
exposes `target_type`/`is_controller_export` (`parser/load.py`), and the UI
shows an explicit warning banner rather than silently treating a partial
export's totals as complete (2026-08-20's `311DGeneratedProgram.L5X` is a
real example — `TargetType="Program"`, only 105 tags, clearly not a full
project). What's NOT built: any first-class handling of a Program/DataType/
AOI-only export as its own intentional mode (e.g. sizing just one UDT
definition standalone, or one AOI's locals+params without a surrounding
controller). Logged here as a real backlog item, not lost — pick up when
Controller-export support is solid.

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

**OQ-BOOLPACK — still open, priority raised (2026-08-20).** James doesn't
know for certain either, and his own hunch actually **cuts against** the
current model: "i assume CTRL+W make a new tag as BOOL will pack it and not
take up a whole 32 bits... you will have to test." So the current
`standalone_tag_bytes: 4` / ASSUMED constant in memory_model.yaml isn't just
unconfirmed, it might be flat wrong — this raises OQ-BOOLPACK's priority for
Phase 3, it shouldn't sit at the bottom of the list. This needs an actual
Studio 5000 compile-and-read-Memory-tab test on James's end (per
TESTING_PLAN.md's corrected offline-compile procedure) — not something
resolvable from this remote session, which has no Studio 5000 to test
against. A clean isolating sample (N standalone BOOL tags, delta against a
baseline with them removed, divide by N) would answer it directly and could
be generated now if useful — ask if that's wanted next.

BOOL members *inside a UDT* pack 8-per-byte (SINT-backed), which is why the
L5X BIT-member generation rule in memory already exists for UDT authoring —
need to confirm sizing matches that packing exactly including partial-byte
members. That's a separate, still-open sub-question from the standalone-tag
case above.

**OQ-ALIGN — confidence raised, still not KNOWN (2026-08-20).** James, 100%
confident from field experience: no 4-byte alignment padding at all — `BOOL,
DINT, BOOL` = 6 bytes, `DINT, BOOL, BOOL` = 5 bytes, tight-packed except for
the BOOL-run mechanic itself (consecutive BOOLs share a backing byte, a
non-BOOL member breaks the run and forces a fresh backing byte for the next
BOOL(s)). Verified the current implementation already produces exactly these
numbers, unchanged — see MEMORY_MODEL.md's UDT packing section and
`tests/test_sizing.py::test_bool_packing_run_broken_by_non_bool_member`.
Also confirmed: reordering members *does* affect footprint (this OQ's UI
implication holds) — a UDT authored as `BOOL, DINT, BOOL` wastes a byte
relative to `DINT, BOOL, BOOL`, so "reorder members to save N bytes" is a
real, worthwhile UI finding once the UI supports member-level drill-down.
Confidence still ASSUMED, not KNOWN — a confident field opinion isn't the
same evidentiary bar as a real Phase 3 controller measurement, which hasn't
happened yet.

**OQ-BOOLARRAY — confirmed by direct observation (2026-08-20), strong
evidence but stays ASSUMED per project discipline.** James: "i cannot make a
bool array of 12, it will round to 32. making a bool array of 33 will round
to 64" — this is Studio 5000's own tag-creation behavior he's directly
observed repeatedly, not a recollection or guess, and matches the
`ceil(n/32) × 4` bytes formula exactly (n=12 → 1 word = 32 bits; n=33 → 2
words = 64 bits). Stronger evidence than a field opinion, but still not a
real controller memory-tab measurement, so this stays ASSUMED rather than
promoted to KNOWN — Phase 3 should still confirm it, just doesn't need to
prioritize it the way OQ-BOOLPACK now does (that one, unlike this, has a
hunch pointing *against* the current model).

**OQ-ARRAYPACK — hunch logged (2026-08-20), stays genuinely open, possible
tension with OQ-ALIGN worth watching.** James, much less confident than his
OQ-ALIGN answer: "i dunno, i think the udt always rolls up to the next
32bit boundary. this will need to be validated." That's a *different* claim
than OQ-ALIGN's (which was about padding *between* members inside a UDT —
confirmed none). This one is about the UDT's *overall total* rounding up to
a 4-byte multiple, which would matter most for array-of-UDT element stride
(and possibly scalar UDT tags too — unclear which from his answer).

Worth being precise about the *possible* reconciliation rather than assuming
a contradiction: his confident OQ-ALIGN numbers (`DINT,BOOL,BOOL` = 5 bytes,
not a multiple of 4) could still both be right if scalar UDT tags aren't
rounded but *array element stride* is — a struct's own size being unpadded
while array indexing still rounds each element to a word boundary is a
common pattern elsewhere, not inherently contradictory. But that's inference
on my part, not something James said — do not code speculative rounding
into `compute_array_size`'s UDT-array branch based on this. Current
implementation (`element_bytes × count`, no rounding) stays as-is until
Phase 3 actually measures an array-of-odd-sized-UDT sample and settles it.

**OQ-PRODCONS — RESOLVED (2026-08-20), deprioritized rather than modeled.**
Checked real data first: 0 produced/consumed tags across all 4 real sample
files, so no example to derive a formula from even if it mattered. James:
no special connection-overhead formula needed at all, *if* done correctly —
a correctly-built produced/consumed tag's DataType is a UDT that includes a
`CONNECTION_STATUS`-typed member itself, so the connection's status data is
already counted by ordinary UDT-member recursion, not something hidden
outside the tag's own size. There's probably some true fixed overhead beyond
that (connection table entry, max-consumers config, etc. — not visible in
the L5X at all) but James: "a couple bytes here/there has no meaningful
impact on the 1%" tolerance (OQ-TOLERANCE). No dedicated connection-overhead
work planned. One loose end: `CONNECTION_STATUS` would need its own
`predefined_structures` entry (MEMORY_MODEL.md) if/when it shows up in real
data, same as TIMER/COUNTER/CONTROL — not urgent since nothing in the
current corpus uses it, but don't assume it's already modeled if a future
sample turns out to need it.

**OQ-PREDEFINED — NEW (2026-08-20), found by running the sizing engine
against James's own real production L5X files.** Beyond TIMER/COUNTER/
CONTROL (now modeled, see MEMORY_MODEL.md), real programs reference a long
tail of other firmware-native/library structure types that also never get a
member list in `Controller/DataTypes`, so they currently surface as explicit
sizing errors (correct/honest behavior per the ground-truth constraint --
better an explicit error than a silently wrong guessed number) rather than
counting toward any total.

**Updated again 2026-08-20 after 12 more real files arrived** (whole real
corpus now 16 files, 39,655 tags, 277MB): overall error rate 5.6%, and the
picture is unambiguous —

| Type | Count | Notes |
|---|---|---|
| MOTION_INSTRUCTION | 1305 | by far the largest single gap in the whole model |
| AXIS_CIP_DRIVE | 382 | |
| CAM_PROFILE | 89 | |
| AXIS_VIRTUAL | 76 | |
| MESSAGE | 50 | real MSG structure is large/version-dependent, do not guess |
| CAM | 50 | |
| FBD_TIMER | 47 | FBD variant of TIMER, different layout, don't assume 12 bytes |
| Timestamp | 34 | |
| AxisSTO | 29 | likely Safety/Guard I/O device-profile-generated |
| ts_SpdAdjOutput | 27 | |
| DCI_STOP | 26 | likely Safety/Guard I/O device-profile-generated |
| ALARM_DIGITAL | 16 | worth double-checking against James's OQ-ALARM answer (ALMD/ALMA tags "never used") -- this may be a different mechanism (e.g. a UDT member referencing the type) rather than a contradiction, not yet investigated |
| MOTION_GROUP | 15 | |
| RATE_LIMITER, SCALE | 10 each | |
| everything else (≤9 each) | ~40 | long tail, not worth itemizing individually |

**Motion/cam structures alone (MOTION_INSTRUCTION + AXIS_CIP_DRIVE +
CAM_PROFILE + AXIS_VIRTUAL + CAM + MOTION_GROUP) = 1917 of 2234 total
errors, ~86%.** This is now unambiguously the single highest-value gap to
close next, confirmed by real data at 16-file scale, not a guess — matches
James's own framing ("lots of motion instructions, camming") exactly. None
of these get a guessed size still -- needs real Rockwell documentation or
empirical Phase 3 measurement before anything goes in MEMORY_MODEL.md.

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

**OQ-COMMENTS — test plan set (2026-08-20), still genuinely open.** James
doesn't know from experience either ("i dunno, i assume it takes up space
somewhere") — this one actually needs the Phase 3/4 empirical test, no
shortcut from asking. Test pair specified: 10k rungs of XIC/OTE with no
comments vs. 10k rungs of XIC/OTE with a 100-char comment per rung, same
rung/instruction count otherwise so the only variable is comment presence.
Logged in TASKS.md Phase 4 with these exact parameters.

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

**OQ-JSRSHARED — confirmed genuinely open (2026-08-20), no shortcut.** James:
"ive never tested memory for logic/programming so its an open item" — no
hunch either way, straight to Phase 4/5 empirical testing, same as
OQ-COMMENTS. Standard structured-programming assumption ("compiled once,
called many times") stays the working assumption in the model until tested,
but carries no more weight than that.

**OQ-EVENTTASK — NEW (2026-08-20).** Same conversation, James: "same with
calling tasks via events/MAW" — flagging an analogous but distinct open
question about **Event Tasks** (a Task `Type` alongside Continuous/
Periodic, triggerable by things like a Motion Axis Watch/MAW instruction).
Does an event-triggered task's logic get counted once in the static memory
model regardless of trigger source/count (should be yes, since it's just
another Task/Program/Routine in the project structure, not duplicated per
trigger event — but unconfirmed), and is there any event-task-specific
overhead (trigger configuration, watchdog, etc.) beyond the routine logic
itself? Checked the real corpus immediately: **52 of 86 real Tasks (60%) are Type
"EVENT"** — more common than PERIODIC (19) and CONTINUOUS (14) combined.

**Clarified by James (2026-08-20):** these are triggered on an axis rolling
past a motion watch point (MAW), and the logic inside each one is small —
"not a big handful of logic inside" — shifting/moving some data, matching
the real task names seen (`DataMove_GradingLC`, `zDataMove_ScannerLC`,
etc). So the priority here isn't "invest heavily in event-task-specific
overhead research" — the per-task logic footprint is small and probably
sizes fine as an ordinary Routine once Phase 4/5 exists. The actual risk is
**correctness, not depth**: Phase 4/5's Task→Program→Routine parsing must
not silently skip or mis-handle Type="EVENT" tasks just because they're
structured differently from Continuous/Periodic — James: "not something to
forget." Treat Event Tasks the same as any other Task for structural
parsing purposes; no special event-triggering-overhead modeling needed
unless real data later suggests otherwise.

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

**Unit correction (2026-08-20):** the dialog James actually reads from is
Controller Properties → **Capacity** tab (not a "Memory" tab), and its
numbers are labeled **"blocks,"** not bytes. Confirmed 1 block == 1 byte:
Total shown there for a 1756-L81E (35.11) was exactly 3,145,728, matching
this project's `controller_budgets.yaml` figure to the byte — upgraded that
entry ASSUMED→KNOWN. `batch_memory_capture.ps1` now prompts for "blocks"
explicitly so there's no unit ambiguity in what James types in.

## First real batch (2026-08-20) — 7 samples, 1756-L81E v35.11

First round of real data back from `batch_memory_capture.ps1`, all against
the same empty-project baseline (`sample_0001`, 0 extra tags, Capacity Used
= **18,128 blocks** — this is real fixed overhead: controller scaffolding,
MainTask/MainProgram/MainRoutine, the module, etc., and every delta below
is baseline-corrected against it, i.e. `(actual - 18128) - predicted`, per
`samples/manifest.csv`). Full numbers there; three real findings came out
of it, filed as new open questions rather than silently folded into
MEMORY_MODEL.md, since one data point each isn't enough to fit a constant:

**OQ-TAGOVERHEAD — NEW (2026-08-20), high impact.** There's a real fixed
cost per tag/DataType that the current model doesn't account for at all —
it only sizes raw data bytes.
- 1000 standalone BOOL tags (`sample_0002`): predicted 4000, baseline-corrected
  actual 96000 → **~92 blocks/tag** beyond the predicted 4 bytes/tag.
- `dint_10k_array` (1 array tag, 10000 elements): predicted 40000, actual
  delta 40096 → **96 blocks** overshoot for a *single* tag, i.e. this looks
  like a flat per-tag-descriptor cost (~92-96), not per-element — matches
  the /tag rate above closely.
- `motorstatus_test` (1 scalar UDT-typed tag, and the sample also defines
  the `MotorStatus` DataType with 3 members): predicted 6, actual delta
  402 — much bigger than the ~96 flat tag cost alone, implying the DataType
  *definition* itself (independent of instance count) also costs real
  blocks, roughly ~300 here for a 3-member UDT with no descriptions.
- Net effect: predicted_bytes will systematically **undershoot** real
  usage on any file with many small/atomic tags, and the undershoot is
  driven by tag *count*, not byte size — the opposite failure mode a
  WinDirStat-style tool needs to avoid (silently making small stuff look
  cheaper than it is). Needs isolating follow-up samples (1/10/100/1000
  standalone tags of one type, DataType defined-but-uninstantiated vs
  instantiated) to fit an actual per-tag and per-DataType-member constant
  before this goes in MEMORY_MODEL.md.
- **Tag-name-length variable — CONFIRMED (2026-08-20), real data.**
  James's hunch was right. `tagname_short_100dint.L5X` (100 DINT tags,
  4-char names) baseline-corrected to **84 blocks/tag**; `tagname_long_100dint.L5X`
  (same 100 tags, names padded to 40 chars) baseline-corrected to **124
  blocks/tag**. That's +40 blocks over 100 tags for 36 extra
  characters/tag → **≈1.11 blocks per additional tag-name character**, on
  top of a ≈80-block flat per-tag cost at the short end (linear fit off
  just these two points: `overhead ≈ 79.6 + 1.11 × name_length`).
  Cross-validated against data already collected before this test existed:
  `sample_0002`'s BOOL tags (`TestBool0000`, 12 chars) predict
  79.6+1.11×12 ≈ **93** vs measured ~92; `dint_10k_array`'s tag
  (`dint_10k_array`, 14 chars) predicts 79.6+1.11×14 ≈ **95** vs measured
  ~96. Both land within ~1 block of this 2-point fit — strong signal this
  is real and not coincidence, though still only 4 total data points (all
  on 1756-L81E/v35) and no length values yet between 14 and 40 chars to
  confirm it stays linear across the whole range rather than being a
  bucketed/rounded cost. Not yet promoted to MEMORY_MODEL.md — the flat
  component still needs to be separated from tag-name-string cost
  specifically (a *type descriptor* cost that doesn't depend on the name
  at all is folded into that ~80 intercept right now) before this becomes
  an actual model constant rather than a fitted-line observation.
- **DataType-definition-vs-instance — CONFIRMED (2026-08-20), real data,
  exact linear fit.** `motorstatus_def_only.L5X` (0 instances):
  baseline-corrected 304 blocks — this is the pure DataType-definition
  cost for a 3-member UDT (BOOL/DINT/BOOL, no descriptions), independent
  of any instance. `motorstatus_test.L5X` (1 instance, `TestInstance`):
  baseline-corrected 408 blocks → 408-304 = **104 blocks for that one
  instance**. `motorstatus_10_instances.L5X` (10 instances,
  `TestInstance0`..`TestInstance9`): baseline-corrected 1344 blocks →
  (1344-304)/10 = **104 blocks/instance**, exactly matching the 1-instance
  case. Both the 0→1 and 0→10 measurements agree to the block — genuinely
  linear: `total ≈ 304 + 104 × instance_count` for this UDT. Slightly
  higher than the atomic-tag-name model above would predict for a
  ~12-13 char name (≈93-94 blocks), suggesting a small structure/UDT-typed-
  tag increment (~10 blocks) on top of the atomic-tag model, or just noise
  at 3 data points — not worth chasing further until more UDT shapes
  (different member counts/types) are tested. Still open before this goes
  in MEMORY_MODEL.md: whether the 304 definition cost scales with member
  *count*, member *type*, or both (only one 3-member UDT tested so far).

**OQ-LOGICVISIBILITY — NEW (2026-08-20), high impact, blocks Phase 4.**
1000 rungs of `XIC(In{i})OTE(Out{i});`, both with and without a 100-char
comment on every rung, showed Capacity Used identical at 18,112 — actually
*below* the 18,128 baseline (delta -16, i.e. noise-level, not growth).
**Zero measurable cost for 1000 rungs of real logic**, comments included.
Two possible explanations, not yet distinguished: (a) the Capacity tab
specifically reflects I/O-and-tag-data memory only, and compiled ladder
logic lives in a separate pool this dialog never shows (consistent with
Rockwell's own "Logix5000 I/O and Tag Data" memory-manual terminology
referenced under OQ-MEMREADMETHOD); or (b) 1000 simple two-instruction
rungs is genuinely too small relative to the ~18K baseline to register.
This matters a lot: if (a), then **offline Capacity-tab reads can never
validate the Phase 4 logic-size heuristic at all**, no matter how large a
logic sample gets, and a different validation method is needed for that
piece specifically. Next step: one sample with a drastically larger/more
complex logic body (e.g. 10,000+ rungs, or rungs with many operands/AOI
calls) — if Capacity still doesn't move, that's a strong signal for (a).

**OQ-UDTARRAYALIGN — NEW (2026-08-20).** `oddudt5_array_1000` (array of
1000 `OddUdt5` structures, each predicted at 5 bytes: DINT=4 + two packed
BOOLs sharing 1 backing SINT): predicted 5000, baseline-corrected actual
delta 3360 → **actual ≈8.36 blocks/element**, well above both the 96-block
flat per-tag cost (OQ-TAGOVERHEAD) and the 5-byte/element prediction even
after subtracting it (3360 - ~96 ≈ 3264 over 1000 elements ≈ 3.26/element
extra). Plausible explanation: each element of an array-of-structure gets
padded up to a 4-byte (DINT) boundary for addressing — 5 bytes/element
tight-packed would round up to 8 bytes/element (8000 total), which is much
closer to the observed 3360-ish-over-flat-overhead than 5000 is. This does
**not** contradict OQ-ALIGN's earlier "UDT members tight-pack with no 4-byte
alignment" finding — that was about *member* layout inside one struct;
this would be a separate *array-element* alignment rule. Needs an isolating
sample: an array of a UDT that's already exactly 4 (or 8) bytes tight-packed
— if the overshoot-per-element disappears, that confirms element rounding
to a 4-byte boundary rather than some other cause.

**OQ-TAGSCOPE — NEW (2026-08-20), James's thought, backlog/not scheduled.**
Does a Program-scoped tag's *Usage* (Local vs. the newer Program Parameter
Input/Output/InOut visibility, i.e. "public" scope reachable from other
programs) change its own memory cost, independent of DataType/dimensions?
Untested — every sample so far uses plain controller-scope tags or default
Local program tags. Needs an isolating sample: the same tag shape (e.g. one
DINT) generated once per Usage value, program-scoped, to isolate any
scope-driven overhead from the already-modeled type/dimension cost.

**OQ-ALIASSIZE — NEW (2026-08-20), James's thought, backlog/not scheduled.**
Current model (`report.py`) sizes every Alias tag at a flat 0 bytes,
tagged KNOWN, on the reasoning that an Alias has no DataType of its own in
the L5X and just points at its target's existing storage — but that's an
inference from the L5X schema, not yet verified against real Capacity-tab
data at any scale. Does that hold at 1, 10, and 1000 aliases, or does each
alias carry its own small reference/pointer-table cost (plausibly similar
in shape to the flat per-tag overhead found in OQ-TAGOVERHEAD, since an
Alias is still its own named Tag entry)? Needs an isolating batch: N alias
tags all pointing at one real backing tag, at N = 1/10/1000, baseline-
corrected the same way as the other tag-count sweeps.

**OQ-XPROGREF — NEW (2026-08-20), James's thought, backlog/not scheduled,
Phase 4 (logic size) scope.** Cross-program references to a public/output
Program Parameter tag, written as `\ProgramName.PublicTagName` in another
program's logic — does referencing a tag this way (vs. a same-program
local reference) cost anything extra in compiled logic size? Explicitly
logic-size territory (estimated/heuristic model, not the exact tag-data
sizing this project can nail down precisely per CLAUDE.md's ground-truth
constraint) — parked here until Phase 4 starts, not actionable yet.
