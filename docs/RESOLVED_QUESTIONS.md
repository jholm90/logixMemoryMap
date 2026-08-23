# Resolved Questions (archive)

Everything here started as an entry in `docs/OPEN_QUESTIONS.md` and is now
answered — moved out to keep that file scannable. Full reasoning trail
preserved, not deleted, per this project's own discipline. Sizing constants
that came out of this belong in `docs/MEMORY_MODEL.md`; this file is the
historical record of *how* each was found, not the source of truth for
current code.

## Scope / stack

**OQ-STACK.** Parser/sizing engine: Python, pip-installable, CLI entry
point. UI: local Flask server + hand-rolled vanilla JS/SVG squarified
treemap — deliberately no D3/CDN JS, since engineering workstations running
Studio 5000 are frequently on airgapped OT networks.

**OQ-L5XVERSION.** Primary target v35 (L8x/CompactLogix 5380-class). 3 of
4 original real sample files were v35, matching. `311DGeneratedProgram.L5X`
is an outlier (v32, Program-scoped snippet, not representative). **Still
genuinely open, not carried forward as its own item because it's low
priority:** v20/v30 cross-version schema differences remain completely
unvalidated — no sample data for either. Revisit if/when a v20 or v30
project shows up in the real corpus.

**OQ-TOLERANCE.** James: 1% delta = good, 3% = acceptable, 5% = very poor
— for the exact (tag/UDT/data-space) tier specifically. Logic/program
structure ("a guess at best") isn't held to that bar.

**OQ-PRODCONS.** No special connection-overhead formula needed — a
correctly-built produced/consumed tag's DataType already includes a
`CONNECTION_STATUS`-typed member, so ordinary UDT-member recursion covers
it. Zero produced/consumed tags in the real corpus anyway. Deprioritized,
not modeled further; `CONNECTION_STATUS` would need its own
`predefined_structures` entry if a future real sample actually uses one.

**OQ-ALARMPROPBYTES.** James, 2026-08-22: not in use on any of his live
projects today, but might be in the future. Not worth a test right now —
added to the feature wish list instead: extended tag properties (alarm
config, Min/Max, Engineering Units, that kind of thing) as a future sizing
category once real usage shows up in the corpus.

**L5X version cross-check.** James, 2026-08-22: keep on the feature wish
list rather than test now. The 7 personal-project files he added to the
corpus this session (`samples/local/DnR_Personal/`, gitignored per the
project's real-export policy) span SoftwareRevision 31.02–35.05 — still no
v20/v30 example in hand, so there's nothing to test yet either way. Revisit
if an actual v20/v30 export turns up.

**OQ-SAFETY.** Out of scope for launch entirely. Tool should warn/refuse
on safety-enabled projects rather than attempt a wrong combined number.

**OQ-EXPORTSCOPE.** James, 2026-08-22: yes, the tool needs to handle any
L5X that comes in — Program/DataType/AOI-only exports, not just full
controller exports — and identify which kind it's looking at in the UI.
Also names the actual product differentiator while answering: Logix
Designer already shows a UDT's total size in bytes, it just never shows
*why* it's that size. The UI's per-member/per-tag breakdown is the value
add, not just a total-bytes number Logix already gives you. Not yet built
(implementation, not just the decision) — the `target_type`/
`is_controller_export` groundwork from OQ-EXPORTSCOPE's earlier partial
pass is still there to build on.

**OQ-MEMREADMETHOD.** No programmatic path to memory usage exists on
current-generation hardware (CompactLogix 5380/5480, ControlLogix
5580/5590, GuardLogix 5380/5580) — confirmed against Rockwell's own docs.
GSV exposes nothing; the MSG/CIP "Determine Controller Memory Information"
path is explicitly documented as unsupported on this hardware lineup, only
works on legacy 1756-L55-class/CompactLogix 5370-gen. Controller Properties
→ Capacity tab is the only method, not a stopgap.

**OQ-EMULATE.** Real hardware only (5069-L306ERS available), no Logix
Emulate — explicit rule of thumb. Bigger finding from the same answer:
**no download/online step is needed at all** — Logix Designer shows memory
usage in Controller Properties as soon as the project compiles/verifies
offline. The real loop is L5X→ACD → open → verify/compile → read Capacity
tab. Confirmed unit: the dialog is **Capacity**, not "Memory," and its
numbers are **blocks**, confirmed 1 block == 1 byte (a 1756-L81E's Total
matched `controller_budgets.yaml` to the byte).

**OQ-GENMETHOD.** `l5xgit l5x2acd` (Rockwell's own CLI, built on the Logix
Designer SDK) converts L5X→ACD headlessly, no Logix Designer UI involved —
confirmed against `RockwellAutomation/ra-logix-designer-vcs-custom-tools`.
`scripts/batch_l5x_to_acd.ps1` wraps this over a whole folder.

## Tag / UDT sizing — the big one

**OQ-TAGOVERHEAD, final state.** Started as "there's a real fixed cost per
tag the model doesn't account for," ended as several exact-fit constants
from a combined ~85-sample sweep (all 1756-L81E/v35.11, baseline = 18,128
blocks for an empty project):

- **Flat per-tag overhead = `84 + 8 × floor(name_length / 8)` blocks.**
  Exact fit across 16 independent data points (13-point DINT-50-tag sweep +
  3-point REAL-40-tag cross-check at different type/count). Tag names are
  stored in 8-character-aligned chunks.
- **Tag count is exactly linear from 5 tags up: 92.000 blocks/tag, zero
  rounding error** across 8/8 counts from 5 to 1000. Only counts 1-2 show a
  small one-time minimum-allocation anomaly, irrelevant for real programs.
- **Atomic type barely affects the flat cost**: SINT 95, INT 94, DINT 92,
  LINT 88, REAL 92, BOOL 92 (all at name_len=8) — treat as type-independent.
- **Array size doesn't affect the flat per-tag cost at all**, 1 to 5000
  elements tested — arrays cost the flat overhead plus exactly 4
  bytes/element, nothing more (plus a small ~4-8 block array-specific
  surcharge over an equivalent-length scalar tag, for dimension metadata).
- **UDT DataType-definition cost = `168 + 16 × member_count`**, exact fit
  for 4/8/16/32 all-DINT members. 1-2 members show the same small-N
  anomaly as tag count.
- **Member type doesn't affect UDT definition cost — except BOOL**, which
  costs +32 (4 members: 240 for SINT/INT/DINT/LINT/REAL, 272 for BOOL).
  Mechanistically explained, not a mystery: BOOL members still need one
  hidden backing-SINT member in the `<DataType><Members>` list, so "4 BOOL
  members" is really a 5-member definition under the hood.
- **UDT DataType's own NAME incurs the same kind of storage cost tag names
  do, different formula: `224 + 8 × ceil(name_length / 8)`.** Exact fit,
  4/4 points (lengths 8/13/20/30, 4 DINT members held constant). Note the
  **ceil** here vs the tag-name formula's **floor** — related mechanism,
  different rounding direction and base constant.
- **Comments/descriptions cost ZERO blocks**, confirmed at all 4 possible
  locations (tag Description, UDT member Description, DataType-level
  Description, UDT-tag-instance Description), 0-200 chars, byte-for-byte
  identical every time. Comment liberally, it's free.
- **DataType-definition-vs-instance is exactly linear**: `total ≈ 304 +
  104 × instance_count` for a 3-member (BOOL/DINT/BOOL) UDT — 0→1 and
  0→10 instance measurements agree to the block.

**OQ-BOOLPACK.** Resolved with real data: standalone BOOL tags show the
same ~92/tag flat overhead as every other atomic type (`sample_0002`,
1000 standalone BOOL tags, baseline-corrected to exactly 92/tag). No
special packing behavior for standalone BOOL tags — James's hunch that
"CTRL+W will pack it" turned out to be wrong, current model (4 bytes,
unpacked) stands confirmed.

**OQ-ALIGN.** James, 100% confident from field experience: no 4-byte
alignment padding between UDT members at all (`BOOL,DINT,BOOL`=6 bytes,
`DINT,BOOL,BOOL`=5 bytes), tight-packed except for the BOOL-run mechanic.
Confirmed by the implementation already matching exactly, and by every
real UDT test this session (dozens, across every sweep) landing on
predictions consistent with tight-packing. Reordering members does affect
footprint — a real, worthwhile future UI finding.

**OQ-NESTEDUDT.** Generator support built (`MemberSpec.nested_members`,
recursive `_udt_structure_body_xml`, `collect_nested_datatypes()`). Real
data: all three shapes (nested scalar member, 10-element array-of-nested
member, 100-element array-of-UDT-containing-nested-member) show the same
~510-block overshoot regardless of structural complexity — meaning the
recursive sizing itself is correct; the residual is just the already-known
flat tag/DataType overhead, not a nested-specific gap.

**OQ-CUSTOMSTRING.** Found and fixed a real generator bug along the way: a
standalone STRING-typed tag (built-in or custom-length) exports as a pair
of `Format="L5K"`/`Format="String"` elements, not `Format="Decorated"` like
every other tag type — confirmed against real corpus
(`RobbinsGrn_2026_05_13r00.L5X`). A STRING *member inside a UDT* is
different again (Decorated `StructureMember`, already correct). Real data
7 points from maxlen=10 to maxlen=2000 (baseline-corrected, 1756-L81E):

| maxlen | total blocks | total − maxlen |
|---|---|---|
| 10 | 312 | 302 |
| 82 | 384 | 302 |
| 100 | 400 | 300 |
| 250 | 552 | 302 |
| 500 | 800 | 300 |
| 1000 | 1304 | 304 |
| 2000 | 2304 | 304 |

**Total size scales 1:1 with maxlen, as expected** — clarifying a prior
version of this note that was ambiguously worded and got read as "size
doesn't depend on length," which is wrong. What's actually flat is the
*fixed component* on top of maxlen: ~300-304 blocks (LEN field + tag/type
overhead), not the total. Formula: `total ≈ maxlen + 302` (±2, likely a
4-byte rounding artifact on maxlen itself).

**OQ-AOIINSTANCE.** James, 2026-08-22, from field experience: every AOI
instance needs a parent tag — no inline/anonymous instances. That backing
tag can be Program(Local)-scoped or Controller-scoped, but it always
exists. Confirms the sizing model's existing assumption (an AOI instance
is always a real Tag with Structure-shaped storage, same as a UDT
instance) needs no special-case for a tag-less call.

**OQ-AOIGEN.** Built `aoi_xml()`, real shape confirmed against James's own
AOI export templates after an earlier version (built off a different real
AOI) failed Studio 5000 import. Fixed real discrepancies: needs
Vendor/CreatedDate/CreatedBy/EditedDate/EditedBy attributes;
`ExternalAccess` is Read/Write (Input) or Read Only (Output), not "None";
nested-UDT/AOI-typed LocalTags need a Structure-shaped DefaultData, not
atomic DataValue. Real InOut parameter shape also confirmed (self-closed,
no DefaultData/ExternalAccess, `Required="true" Visible="true"
Constant="false"`) — and directly confirmed an InOut param carries **zero
storage**: the real instance Tag's Structure body only ever contains
EnableIn/EnableOut, InOut is completely absent. The previously-unconfirmed
array-dimensioned `Parameter`/`LocalTag` extrapolation is now confirmed
too — real data collected, imported clean, sane numbers.

**OQ-LARGEMIXED.** Three composite files (100 tags, 1100 tags, 1000 tags
in a different composition), no logic, real data now in. Naively comparing
against the raw engine prediction alone looks like a 34-82% miss — but
that's because the raw engine doesn't yet include the empirically-found
overhead constants above. Hand-applying the confirmed per-tag/UDT-def/
UDT-instance formulas on top of the raw prediction brings every file to
within ~0.3-2.6% of the real number — comfortably inside James's own
tolerance bands. This is the real payoff of the whole sweep: the
individually-confirmed constants compose correctly in a realistic mixed
file, not just in isolation.

**OQ-AXISSTRUCT (numbers, not the combo test).** Real reference exports
confirmed these use `Data Format="Axis"` with a flat `AxisParameters`
attribute list — structurally nothing like UDT/AOI, totally unmodeled by
the sizing engine (confirmed: explicit UnknownDataType error, not a
crash). Real Capacity numbers now exist for 4 of 5 axis types, measured
over a MotionGroup-only local baseline (19,296 blocks): AXIS_VIRTUAL and
AXIS_SERVO both 16,888 blocks, AXIS_CIP_DRIVE 22,728, COORDINATE_SYSTEM
9,616. Treat these as KNOWN predefined-structure constants once written
into `MEMORY_MODEL.md`, same tier as TIMER/COUNTER/CONTROL. **Not fully
closed** — see OQ-AXISCOMBO in the open list for the one remaining piece.

## Logic sizing

**OQ-INSTRUCTIONSCOPE.** Real frequency count across the corpus (24,941
instruction instances, 434 RLL + 126 ST routines, 0 SFC/FBD) settled scope
for Phase 4/4b: bit logic dominates, then compare/move/math, then
motion+cam+GSV/SSV (previously not planned for, now confirmed must-have),
then array/string/program-flow. PID and ASCII-module instructions dropped
entirely — zero real usage.

**OQ-LOGICVISIBILITY.** Definitively yes — the Capacity tab reflects
compiled logic size, cleanly and linearly. The 244-file per-instruction
sweep (baseline 18,128) fits `delta = 4,816 + weight × rung_count` at
**0.00% residual** across 42 of 46 real instructions (4 more — plus 2
garbled rows — flagged for re-capture, see docs/OPEN_QUESTIONS.md; the
resolution here doesn't depend on those). Same fixed 4,816-block base cost
across every instruction. Weights range 16 blocks/rung (OTE/OTL/OTU/NOP) up
to 452 (CPT). The earlier "zero movement" finding from 2 pre-sweep samples
was wrong — an undeclared-tag artifact in that flawed test, not a real
null result. Full weight table pending the 32-row re-capture before it goes
into `MEMORY_MODEL.md`.

**OQ-JSRSHARED.** Strong evidence for "compiled once, referenced not
duplicated": JSR-to-the-same-target cost stays exactly linear
(`4,816 + 5,096-4,816=280 fixed, 72 blocks/call`) as call count scales
10→5,000, with zero residual — no blow-up that would appear if the target
subroutine's body were re-compiled per call site. Not 100% conclusive
(can't independently isolate the callee's own compiled size from this data
alone), but nothing in the data points toward duplication either.

**OQ-EVENTTASK.** 52 of 86 real Tasks (60%) are Type="EVENT", more common
than Periodic+Continuous combined. Triggered by things like a Motion Axis
Watch point, logic inside each is small (data-move style). Conclusion:
correctness matters here, not extra depth — Phase 4/5's Task→Program→
Routine parsing must not skip/mishandle Event Tasks just because they're
structured differently; no special event-triggering-overhead model needed.

## Sample generation / testing infrastructure

Everything under this heading was methodology/tooling work, not a sizing
question — archived here rather than carried forward as "open."

- Confirmed `l5xgit` headless L5X→ACD conversion works at scale (400+
  files converted across this project with only one expected failure, an
  intentionally-different-processor-family old fixture).
- Confirmed and fixed multiple real L5X shape gaps by comparing generator
  output against real corpus files rather than guessing: array/UDT tag
  Data bodies, STRING tag dual-format, TIMER/COUNTER tag dual-format,
  AOI Parameter/LocalTag attributes, rung Text CDATA wrapping.
- `batch_l5x_to_acd.ps1` / `batch_memory_capture.ps1` both resumable and
  self-auto-pushing straight to `main`, no branches/merges.

## Sizing-rebase batch, 2026-08-23

Full-corpus rebase: every clean manifest.csv row (546 of them) re-parsed
fresh through the current engine and compared against real `actual_bytes`.
Went from 0 exact matches / 16 engine errors to 77 exact matches / 0 engine
errors. Everything below came out of that pass.

**OQ-BASELINE (new discovery, not a prior open question).**
`empty_project_baseline = 13,296 blocks`. A previously-completely-
unmodeled, universal, exact-zero-variance gap between engine total and real
Capacity data, confirmed across 200+ independent real data points spanning
wildly different categories (tag_overhead sweeps, UDT-name sweeps,
tagscope, boolarray, udtarrayalign, comment-length sweeps). Represents
controller/module/task/program scaffolding cost that exists in every real
program regardless of content — nothing in the L5X "causes" it, it's just
always there. A few categories show a small ADDITIONAL amount on top of
this floor (logic_instr sweep: +13 → 13,309; customstring: +206 → 13,502;
`arraypack_odd3b` growing slightly with count) — each explained by its own
constant below, not folded into the baseline itself. Wired in as
`empty_project_baseline` in `memory_model.yaml`, emitted as a
`project_baseline` SizeEntry on every report (`report.py`), confidence
KNOWN (zero variance across 200+ points is about as confirmed as this
project's data gets).

**Scope correction, 2026-08-23 (James):** "not a constant... will change
based on processor and firmware." The "universal" framing above overstated
it -- every one of those 200+ points was generated on the same processor/
firmware (`wrapper.py`'s 1756-L81E/35.05 default), so what's actually
confirmed is 13,296 for THAT combo, not for any CompactLogix/ControlLogix
generally. See `docs/OPEN_QUESTIONS.md` OQ-BASELINE-PROCFW for the
follow-up test batch (per-processor and per-firmware blank-project sweeps)
needed to turn this into the (processor_type, firmware_rev)-keyed lookup
it actually needs to be.

**OQ-CUSTOMSTRINGDEF.** Custom STRING types (`Family="StringFamily"`) get
their own one-time definition cost, `custom_definition_cost = 206`,
confirmed flat/constant across all 7 real `customstring_len*` points
(maxlen 10 to 2000) — the definition cost doesn't scale with the type's
DATA length, only the per-instance cost does (already-modeled, unaffected
by this). NOT yet tested for type-NAME-length sensitivity — don't assume
it's independent of that. Wired into `report.py`'s UDT-definition loop
(string-family types now get a real `udt_definition` entry using this
constant instead of being silently skipped) and `StringModel` in
`constants.py`.

**OQ-TAGSCOPE.** No code change needed. `tagscope_public_n00010`/`n00100`
show the exact same 13,296 baseline gap as `tagscope_local` — zero cost
difference between `Usage="Local"` and `Usage="Public"` program tags. The
existing generic tag_overhead formula already covers both correctly.

**OQ-BOOLARRAY, confidence upgrade.** `boolarray_n00008` through `n05000`
all show a small, ~constant residual (13,300-13,304, the same small-noise
band documented for several other categories) once the baseline is
subtracted — meaning the existing `ceil(dim/32)*4` BOOL-array formula was
already accurate, real data now confirms it. Was ASSUMED; treat as
confirmed by real data going forward (no formula change, just a real
data point behind a formula that was previously untested).

**OQ-UDTARRAYALIGN, partial.** `udtarrayalign_tight8b_n00001/n00010/
n00100` (array of an already-8-byte-tight UDT) shows a perfectly constant
13,300 gap across all 3 counts — `dimension * udt_size` is exact for
already-tight UDTs, zero per-element padding. Still open (see
OPEN_QUESTIONS.md OQ-ARRAYPACK): `arraypack_odd3b_n00001/n00010/n00100`
(array of a 3-byte/odd-sized UDT) shows a gap that grows slightly with
count (13,305 / 13,310 / 13,400) — not a clean linear fit, roughly but not
exactly ~1 byte/element extra. Real, but not resolved to a formula; not
wired into code.

**OQ-PREDEFINED, motion/axis/CAM_PROFILE piece.** Derived from real data
via `residual = actual - sizeable_engine_total - empty_project_baseline`
(sizeable_engine_total = engine's total over only the tags it could
already size, ignoring the axis/motion tags that were still `SizeError`ing
at the time). All exact fits, all previously-`SizeError`ing files now
size cleanly:
  - `MOTION_GROUP = 1,076`
  - `AXIS_CIP_DRIVE = 22,636`
  - `COORDINATE_SYSTEM = 9,516`
  - `AXIS_SERVO = 16,796`
  - `AXIS_VIRTUAL = 16,796` (identical to AXIS_SERVO)
  - `MOTION_INSTRUCTION = 12` (same 3-DINT-style layout as TIMER/COUNTER/
    CONTROL, exact fit across a 1/5/50 tag-count sweep)
  - `CAM_PROFILE`: `base=4, per_element=56` (exact linear fit across a
    1/5/20/50-element real count sweep). `per_element=56` = 14 fields x
    4 bytes, independently confirming an earlier corpus-based hypothesis
    that CAM_PROFILE has 14 real per-element L5K fields, only 1 of which
    is visible in the Decorated XML shape — this is Rockwell's own
    "voodoo" internal layout, not derivable structurally, pure empirical
    constant like axis.
All wired into `memory_model.yaml` (`predefined_structures` for the first
6, new top-level `predefined_array_structures` section for CAM_PROFILE)
and `constants.py`/`udt.py` (`compute_array_size`'s new
`predefined_array_structures` branch — array/dimensioned tags only,
deliberate: CAM_PROFILE is never used scalar in real Logix, so a scalar
CAM_PROFILE tag still correctly hits `UnknownDataTypeError` rather than
silently returning a wrong number). 16 previously-`SizeError`ing real
files across the axis/motion categories now size with 0 engine errors.
Remaining piece (CAM the instruction wrapper, MAH/MSO's real per-rung
logic weight) still open, see OPEN_QUESTIONS.md.

**OQ-LBLJMP-STALE, fully resolved.** The `LBL(L{i})NOP();` syntax fix
(2026-08-22) cleared the build errors as expected — all 5
`instr_lbljmp_n*` real captures came back clean (`error_count=0`).
Combined LBL+JMP weight is an exact linear fit at 104 blocks/pair across
n=10/50/100/1000/5000 rungs, 0 residual. **Not independently decomposable**
from this data (the generator always emits LBL:JMP 1:1 paired) — split
52/52 as an unbiased placeholder that reconstructs the confirmed 104
exactly for that pairing, explicitly flagged in `memory_model.yaml` as
unvalidated for any other LBL:JMP ratio (e.g. one JMP targeting multiple
LBLs, or vice versa). Wired into `logic_instructions.weights`. Separately,
`SIZE`'s array-subscript syntax bug also cleared: SIZE is an exact linear
fit at 128 blocks/rung across n=10/50/100/1000/5000, 0 residual, also
wired in.

**Small-residual buckets, spot-checked, no action needed.** After all of
the above, most of the remaining ~469 non-exact rebase-check rows cluster
into small buckets (-5, 4, 8, 13, ...) a handful of blocks off zero.
Spot-checked one file from each of the -5/4/8 buckets
(`typesweep_add_dint_n01000`, `indirect_direct_index_n01000`,
`array_dint_00001`/`boolarray_n00008`): all are single-digit-block gaps
against multi-thousand-block totals (e.g. -5 out of 61,592) — noise-level,
consistent with the same small-residual pattern already documented
elsewhere (OQ-BOOLARRAY etc.), not a new systematic issue. No code change.
The one bucket NOT in this category, 1264 (all `*_def_only` AOI files),
is real and substantial — see OPEN_QUESTIONS.md OQ-AOIDEF, not resolved,
the single biggest remaining known gap.
