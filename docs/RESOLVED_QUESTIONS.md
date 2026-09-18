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

**OQ-TOLERANCE.** 1% delta = good, 3% = acceptable, 5% = very poor
— for the exact (tag/UDT/data-space) tier specifically. Logic/program
structure ("a guess at best") isn't held to that bar.

**OQ-PRODCONS.** No special connection-overhead formula needed — a
correctly-built produced/consumed tag's DataType already includes a
`CONNECTION_STATUS`-typed member, so ordinary UDT-member recursion covers
it. Zero produced/consumed tags in the real corpus anyway. Deprioritized,
not modeled further; `CONNECTION_STATUS` would need its own
`predefined_structures` entry if a future real sample actually uses one.

**OQ-ALARMPROPBYTES.** 2026-08-22: not in use on any live
project today, but might be in the future. Not worth a test right now —
added to the feature wish list instead: extended tag properties (alarm
config, Min/Max, Engineering Units, that kind of thing) as a future sizing
category once real usage shows up in the corpus.

**L5X version cross-check.** 2026-08-22: kept on the feature wish
list rather than tested now. The 7 personal-project files added to the
corpus in that batch (`samples/local/DnR_Personal/`, gitignored per the
project's real-export policy) span SoftwareRevision 31.02–35.05 — still no
v20/v30 example in hand, so there's nothing to test yet either way. Revisit
if an actual v20/v30 export turns up.

**OQ-SAFETY.** Out of scope for launch entirely. Tool should warn/refuse
on safety-enabled projects rather than attempt a wrong combined number.

**OQ-EXPORTSCOPE.** 2026-08-22: the tool needs to handle any
L5X that comes in — Program/DataType/AOI-only exports, not just full
controller exports — and identify which kind it's looking at in the UI.
The same discussion named the actual product differentiator: Logix
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
special packing behavior for standalone BOOL tags — the hunch that
"CTRL+W will pack it" turned out to be wrong, current model (4 bytes,
unpacked) stands confirmed.

**OQ-ALIGN.** Established from field experience with full confidence: no 4-byte
alignment padding between UDT members at all (`BOOL,DINT,BOOL`=6 bytes,
`DINT,BOOL,BOOL`=5 bytes), tight-packed except for the BOOL-run mechanic.
Confirmed by the implementation already matching exactly, and by every
real UDT test in that batch (dozens, across every sweep) landing on
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

**OQ-AOIINSTANCE.** 2026-08-22, from field experience: every AOI
instance needs a parent tag — no inline/anonymous instances. That backing
tag can be Program(Local)-scoped or Controller-scoped, but it always
exists. Confirms the sizing model's existing assumption (an AOI instance
is always a real Tag with Structure-shaped storage, same as a UDT
instance) needs no special-case for a tag-less call.

**OQ-AOIGEN.** Built `aoi_xml()`, real shape confirmed against the
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
within ~0.3-2.6% of the real number — comfortably inside the
tolerance bands. This is the real payoff of the whole sweep: the
individually-confirmed constants compose correctly in a realistic mixed
file, not just in isolation.

**Re-checked against the current (2026-08-29) engine, full manifest.csv
audit:** `large_mixed_100tags` (+136, 0.49%) and `large_mixed_1100tags`
(+1,336, 1.07%) still land comfortably inside band. `large_mixed_
1000tags_arrays` now shows +4,416 (~3.38% of predicted) — drifted
slightly above the 2.6% figure quoted above and right at the edge of
the "acceptable" ceiling, most likely because array-dimension/
UDT-array formulas have changed since this was originally resolved
(2026-08-22-era). Not re-investigated this pass (single data point, no
isolation of which specific array/UDT-array formula moved) — flagged
here rather than left silently stale; a fresh `large_mixed_*`-style
composite file would confirm whether this is real drift or just this one
file's specific tag mix.

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

**Scope correction, 2026-08-23:** the baseline is not a constant and
changes with processor and firmware. The "universal" framing above overstated
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

**OQ-UDTARRAYALIGN / OQ-ARRAYPACK, fully resolved 2026-08-24.**
`udtarrayalign_tight8b_n00001/n00010/n00100` (array of an already-8-byte-
tight UDT) shows a perfectly constant gap across all 3 counts —
`dimension * udt_size` is exact for already-tight UDTs, zero per-element
padding. `arraypack_odd3b` (array of a 3-byte/odd-sized UDT) was extended
2026-08-24 to n=1/10/100/1000/5000 and resolved cleanly: **each array
element of a UDT rounds up to a 4-byte boundary.** Once that rounding is
applied, every count n≥10 lands on exactly the same flat +4 residual as
the tight8b case (the universal small-baseline noise seen everywhere in
this project, not a per-element effect) — n=1 shows the same +8 small-N
anomaly already documented elsewhere (UDT-definition formula, etc.), not
a new mystery. This *sharpens* rather than contradicts the tight8b
finding: there's no padding beyond the 4-byte boundary itself, but a
sub-4-byte-boundary element genuinely does round up (3 bytes/element
really is charged as 4). Wired into `sizing/udt.py`'s `compute_array_size`
(the `data_type in data_types` branch rounds `element_bytes` up to the
next multiple of 4 before multiplying by count) — atomic-type arrays are
untouched, this only applies to array-of-UDT.

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

**OQ-LBLJMP-STALE, fully resolved (SUPERSEDED 2026-08-25, see below).**
The `LBL(L{i})NOP();` syntax fix (2026-08-22) cleared the build errors as
expected — all 5 `instr_lbljmp_n*` real captures came back clean
(`error_count=0`). Combined LBL+JMP weight was originally read off as an
exact linear fit at "104 blocks/pair" across n=10/50/100/1000/5000 rungs —
**this arithmetic was wrong**, see the 2026-08-25 correction entry below
for the actual decomposed values (LBL=64, JMP=40, 120/pair). Separately,
`SIZE`'s array-subscript syntax bug also cleared: SIZE is an exact linear
fit at 128 blocks/rung across n=10/50/100/1000/5000, 0 residual, wired in
(unaffected by the LBL/JMP correction).

**OQ-LBLJMP, corrected decomposition, 2026-08-25.** Re-deriving from the
same `instr_lbljmp_n*` real data plus two new independent sweeps
(`lbljmp_lblonly` — LBL with 0 JMP targeting it, `lbljmp_manytoone` —
multiple JMP to one LBL) gives an exact 120 blocks/pair, not 104 — the
prior value was a miscalculation, not a data/measurement error. All 3
sweeps cross-validate to the same decomposition: `LBL=64`, `NOP=16`
(already known/separately confirmed elsewhere), `JMP=40`
(`64+16+40=120`). Unlike the old 52/52 placeholder split, this decomposition
is independently confirmed (LBL-only and many-JMP-to-one-LBL both isolate
LBL's and JMP's contributions separately) rather than assumed evenly.
Wired into `logic_instructions.weights` as `LBL: 64`, `JMP: 40`.

**OQ-BTD/COP/CPS/FLL, resolved 2026-08-25.** 5-count real sweeps
(`instr_btd_n*`, `instr_cop_n*`, `instr_cps_n*`, `instr_fll_n*`) each
land on an exact linear fit, 0.00% residual: `BTD=64`, `COP=112`,
`CPS=112`, `FLL=68` blocks/rung. Wired into `logic_instructions.weights`.

**OQ-MAHMSO, resolved 2026-08-25.** 2-count real sweep
(`instr_mah_n*`/`instr_mso_n*`, using the same 2-operand
`(Axis,MotionInstruction)` syntax already confirmed for MAFR/MASR) lands
on an exact linear fit: `MAH=60`, `MSO=60` blocks/rung. Wired into
`logic_instructions.weights`. Contrast with MAM/MAJ/MAS/MRP, which use
the *same* documented 2-operand syntax but 100% build-failed on real
capture (`error_count == rung_count`) — see OPEN_QUESTIONS.md
OQ-MAMFAMILY-BUILDFAIL for the negative result, not resolved.

**OQ-ALIASSIZE, resolved 2026-08-25.** Real captures at 3 scales
(`aliassize_n00001`/`n00010`/`n01000`) prove the prior "0 bytes, KNOWN"
assumption wrong. Alias tags (`TagType="Alias"`) carry the same
per-Tag-table-entry overhead shape as an ordinary tag —
`flat_base + per_8_chars*floor(namelen/8)` — just with a different
flat_base (56 vs the ordinary tag_overhead's 84), and no separate raw-data
term (an Alias has no data space of its own). Exact match across all 3
name-length buckets (gaps 56/560/63200). Wired as a new
`alias_overhead` model in `memory_model.yaml`/`constants.py`,
`report.py`'s alias branch now calls `model.alias_overhead.bytes_for(name)`
instead of hardcoding 0.

**OQ-AXISDEEP, composite case resolved 2026-08-25 (no code change
needed).** `axis_composite_udt_def_only`/`_1_instance`/`_10_instance` real
captures all show small, clean gaps (72/80/156) consistent with ordinary
UDT-definition-cost + UDT-recursion noise, not a new interaction cost —
an embedded axis member inside a composite UDT costs exactly what
standalone-axis-constant + UDT-recursion already predicts. Confirms the
existing model requires no change for the composite case; this was the
one piece of OQ-AXISDEEP still open after the 2026-08-23 predefined-
structure-constants resolution above.

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

**OQ-INSTRFIRSTPASS-X10, 34 of 36 resolved, 2026-08-25.** Real x10
captures for `gen_instruction_firstpass.py`'s 36 single-instruction
sweeps. `weight = (actual_x10 - actual_n1) / 9` for each of 34
instructions (everything except CROUT/MAPC, which build-failed — see
OPEN_QUESTIONS.md OQ-CROUT-MAPC-BUILDFAIL) came back an exact integer,
0.00% residual, same standard as every other confirmed weight in this
project: NOT=40, TRN=52, NEG=40, OSR=56, OSF=56, UID=40, UIE=40, MCR=16,
TND=24, ATN=60, DEG=64, RAD=116, TAN=60, SQR=52, SWPB=76, XOR=40,
FIND=100, INSERT=116, BSL=60, BSR=60, FFL=72, FFU=72, SRT=116, AVE=176,
FAL=104, FSC=104. Motion instructions MAFR/MASR/MDW/MASD (same
`(Axis,MotionInstruction)` shape as MAH/MSO) all land on the identical
60 — confirms cost is governed by operand-type shape, not the specific
mnemonic, same conclusion MAH=MSO already established. MGSD/MGSR (the
`(MotionGroup,MotionInstruction)` shape instead) both land on 56, again
identical to each other. MCCP=204 and MSG=48 also resolved for their pure
LOGIC weight (clean build, error_count=0 for both) — their CAM/MESSAGE
tag operand's own data-space cost is a SEPARATE, still-unmodeled
predefined structure (OPEN_QUESTIONS.md OQ-PREDEFINED item 8), not
entangled with the logic weight itself since the weight derivation uses
only the marginal (n1→n10) delta. All wired into
`logic_instructions.weights`. A flat, instruction-independent +6-byte gap
appears on both n=1 and x10 for the 32 non-MCCP/MSG files (doesn't affect
any weight above since it's a constant offset that cancels in the
marginal calculation) — see OPEN_QUESTIONS.md OQ-INSTRFIRSTPASS-FLATOFFSET,
minor, not root-caused, left open.

**OQ-STRINGTAGOVERHEAD-BUILTIN, resolved 2026-08-25.** Built-in STRING
tags cost exactly 2 bytes LESS than the ordinary flat tag_overhead
formula (`84 + 8×floor(name_len/8)`) predicts. Confirmed via the dense
9-point `stringoverhead_builtin_n*` sweep (n=1 through 1000): gap is
EXACTLY `-2*n` at every single point, and the `stringoverhead_namelen*_
n050` cross-check (name length 4/8/16/40, fixed count=50) shows the
identical -100 (`=-2*50`) regardless of name length — confirms the
correction is a flat per-tag thing, independent of both count and name
length. Wired as `string.builtin_tag_overhead_correction = -2` in
`memory_model.yaml`/`constants.py`, applied in `report.py` when
`tag.data_type == "STRING"`. All 13 real data points (9 count sweep + 4
namelen cross-check) now size at exactly 0 gap. Deliberately NOT extended
to custom StringFamily types — that data shows a maxlen-dependent rate,
not a clean flat -2, and needs more data before wiring (see
OPEN_QUESTIONS.md OQ-STRINGTAGOVERHEAD for the still-open custom-string
piece).

**OQ-PREDEFINED, CAM piece, resolved 2026-08-26.** Real 5-point count sweep
(1/5/10/20/50 elements) confirms the mechanistic prediction from reading
CAM's real Decorated/L5K shape: `base=8, per_element=12` blocks, KNOWN
confidence, 5/5 points at or near zero residual (the small non-zero points
are the same -4 universal noise seen elsewhere). Wired via the existing
`predefined_array_structures` mechanism, same pattern CAM_PROFILE already
used. MESSAGE's own byte cost remains unmodeled — deprioritized
2026-08-25 as acceptable at the 90% tier, MSG not being a common
instruction; MSG's own
LOGIC weight (48/rung) is separately resolved and wired.

## Motion, CPT, string, and task-overhead batch, 2026-08-25–26

**OQ-CROUT-MAPC-BUILDFAIL, resolved 2026-08-25.** CROUT's build failure is
not a bug — CROUT is a Safety-only instruction requiring a safety PLC CPU,
reclassified OUT OF SCOPE alongside DCS. MAPC's build failure
was two real generator bugs (undeclared `Axis_Cip_Drive` tag, and
slave/master axis reusing the same tag instead of two distinct axis tags)
— fixed via `gen_axis_composite.py`/`gen_instruction_firstpass.py`'s
`group_mapc_v2`. Real capture confirmed both fixes: clean build, logic
weight = 260/rung exactly, wired in `memory_model.yaml` (`MAPC: 260`).

**OQ-MAMFAMILY-BUILDFAIL, resolved 2026-08-26.** MAM/MAJ/MAS/MRP's 100%
build failure was a generator bug, not a syntax question — each needs its
own full parameter list — the bare 2-operand call used is MAH/MSO's
shape, not theirs. Real corpus operand counts confirmed: MAM=20, MAJ=17,
MAS=9, MRP=5. Fixed with real corpus-transplanted templates in
`gen_motion_instructions.py`; all 4 now build clean and are wired:
`MAM=224, MAJ=236, MAS=100, MRP=128` blocks/rung. Keyword-value variation
(Merge, Profile, StopType×Decel×Jerk) doesn't change size except MRP's two
real operand-4/5 patterns, which differ by 52 bytes (single flat MRP
weight used regardless).

**OQ-CPT, uniform and T1+T2 mixed-tier cases resolved 2026-08-26, wired.**
`parser/logic.py` now extracts every real `CPT(...)` call's operator
tokens; `sizing/logic.py`'s `CptExpressionModel` costs each call
individually, replacing the old flat-wrong `CPT: 452` weight entirely.
Uniform-tier (single operator type, e.g. plain ADD chains — the dominant
real usage pattern): `base_read=88`, `operator_tier_costs` ADD/SUB=36,
MUL/DIV/MOD=52, POW=116, `per_extra_same_tier_operand=24` — confirmed
exact at 22/24 real manifest rows (2/24 hit a small, already-understood
large-file +264 anomaly unrelated to the formula). Literal operands (int
or float) cost the same as tag operands; operator order and literal
position don't matter. T1(ADD/SUB)+T2(MUL/DIV/MOD) mixed expressions:
`true_cost = 100 + 32*operator_count`, exact at 4/5 operand-count points,
wired as a special case in `CptExpressionModel.cost_for`, live-verified
15/18 real rows exact. T1T3, T2T3, and all-3-tier mixes remain on the
older additive-sum fallback — see OPEN_QUESTIONS.md OQ-CMPCPTLAYOUT for
what's still open there.

**OQ-CMP weight, resolved 2026-08-26.** The apparent inconsistency between
`cmpcpt_cmp_single`'s mined rate and the wired `CMP: 76` weight was a
manual-arithmetic error, not a real bug — `CMP: 76` is exact for a single
condition. A real, previously-unwired compound-condition surcharge
(+64/rung, KNOWN, exact at n=100 and n=1000) and float-literal surcharge
(+72/rung, FITTED, single point) are now wired too, verified 9/10 real
rows exact (1/10 hits the same known large-file anomaly noted above).

**OQ-INDIRECT, resolved 2026-08-26, wired.** Tag-driven array indexing
costs +84 blocks/rung, tag+literal-offset indexing (`tag[idx+1]`) costs
+108 blocks/rung, both confirmed perfectly linear across n=10/50/100/1000
(120/rung and 144/rung total respectively, zero variance). `parser/
logic.py` scans rung text for `Name[...]` brackets and classifies
direct/literal (0 cost) vs tag-driven vs tag+offset; `sizing/logic.py`
applies the cost per occurrence. KNOWN confidence, verified against all 8
real manifest rows. Deliberately scanned across the whole rung, not scoped
to MOV specifically — only MOV-carried indexing was ever captured, so use
inside e.g. a CPT operand is untested.

**OQ-OPERANDTYPE, resolved 2026-08-26, wired.** All 13 type-sensitive
instructions (ADD/SUB/MUL/DIV/MOD/EQU/GEQ/GRT/LEQ/LES/NEQ/MOV/LIM) apply a
real SINT/INT/REAL/STRING surcharge on top of their DINT-rate base weight,
derived from the `typesweep_*` corpus (69 real rows, 1000-rung sweeps,
exact per-1000 deltas). LINT behaves identically to DINT (no separate
handling needed). FITTED confidence (single count point per type) —
verified live: 67/67 real rows land on the same small baseline noise once
the surcharge is applied (was off by 88-164/rung before).

**OQ-CAPTURERACE, resolved 2026-08-26.** The 6 rows flagged by the
tooling as WINDOW TITLE MISMATCH were retested (`_v2` suffix) and
reproduced the original readings almost exactly — not a capture race after
all. n=1 and n=2 DINT arrays genuinely report the identical `actual_bytes`
(a real Capacity-display rounding granularity at that size, not a bug).
Tag comment length (0-200 chars) confirmed zero effect on size,
independently, in the same pass.

**OQ-STRINGTAGOVERHEAD, scalar case (builtin + custom) fully resolved
2026-08-25/26.** Builtin STRING tags cost exactly -2 bytes vs the ordinary
flat tag_overhead formula, confirmed flat across 13 real data points,
wired as `string.builtin_tag_overhead_correction`. Custom StringFamily
types: the DATA member rounds to the NEAREST multiple of 8 (rounding down
at the exact tie) — real bug fix, 0 residual against 9 real maxlen points
spanning every mod-4/mod-8 remainder; maxlen mod 4 == 1 gets its own
confirmed +8 one-time definition bonus. Custom type-NAME length also
resolved: `custom_definition_cost_for(name_len) = base(208) +
8*floor((name_len-5)/8)`, exact across 22 real dense-sweep points — the
earlier suspected "UDT-nesting tax" was fully explained by this same
name-length formula, no separate nesting cost exists. All wired in
`constants.py`'s `StringModel`, `memory_model.yaml`, `report.py`,
`tree.py`.

**OQ-STRINGARRAYPAD, resolved 2026-08-26, wired.** Array-of-STRING (one
tag, `Dimensions=N`) is a structurally different case from a scalar STRING
tag and doesn't inherit the scalar formula: `total = array_base +
(scalar_element_size + per_element) * n`. Builtin: `array_base=6,
per_element=2`, KNOWN, 6/6 real points exact. Custom: `per_element=4`,
KNOWN, 6/6 points exact across 2 type names; `array_base` is FITTED
(type-name-length-dependent, same effect as the scalar case) — wired using
the better-supported 13-char name's value (12). Wired in `udt.py`'s
`compute_array_size` and `memory_model.yaml`'s new `string_array` section.

**OQ-STRINGUDTMEMBER, custom-type piece resolved 2026-08-26.** Custom
STRING type as a UDT member has NO separate nesting tax — fully explained
by the same standalone type-name-length formula (OQ-STRINGTAGOVERHEAD
above) once the wrapping UDT's own unrelated name-length cost is accounted
for, and has no dependence on the string's own `maxlen` (4/4 exact real
points). Builtin STRING as a UDT member is a separate, still-open 2-D
(member-count × instance-count) effect — see OPEN_QUESTIONS.md
OQ-STRINGUDTMEMBER.

**OQ-STRINGCONSTFAIL, resolved 2026-08-26.** The 8/8 build failures in the
constant-flag/processor batch were a tooling artifact, not an L5X content
bug: Studio 5000's same-instance "switch file without closing"
batch-capture flow can't cleanly replace the "Local" module when the
PROCESSOR changes between consecutive files (renames it to "Local1", which
then fails validation) — affects any processor-varying batch run through
that flow, including the `fw_baseline` files. Separately, confirmed
L8/L9/5069 compute constant-STRING sizing identically, so the processor
axis in this particular test was never a real question — dropped, test
rebuilt on a single default processor.

**OQ-TASKOVERHEAD, resolved and wired 2026-08-27.** Per-Task/per-Program/
per-Routine scaffolding costs, cleanly separated via 3 chained real file
comparisons: `routine_extra=272`, `program_extra=484`, `task_extra=700`,
applied once per file in `memory_model.yaml`'s `task_program_overhead`, on
top of the existing (unchanged) `fixed_base_per_routine`/per-rung content
costs. Verified exact against the disentangle-batch files and the original
multi-task sweep (within 0.21% at n=4 tasks). Broad regression across
1,059 manifest rows: exact-match count 279→292, over-3%-residual count
50→43, zero regressions. Also fixed two real multi-program over-counting
bugs found along the way (`xprogref_twoprog_shared_alias_n01000`
4076→16, `lbljmp_samename_diffroutines` 4049→-11).

## Module I/O and empty-routine batch, 2026-08-27

**OQ-EMPTYROUTINE, resolved and wired 2026-08-27.** A `<Routine
Type="RLL"/>` with no `RLLContent` child (a legitimate real construct —
an SBR routine with no rungs is legal, and appears in 15 real production
files) was being silently skipped by `parse_rll_routines`,
charged 0 bytes. Real data (`emptyroutine_n01/n02/n03`) confirms it costs
the same real per-routine shell tax as an ordinary routine (264/extra
routine, matching the already-wired `task_program_overhead.routine_extra`)
— it just has zero content cost. Fixed to emit `rung_texts=[]` instead of
skipping; retroactively corrects every self-closing-routine file in the
corpus, including several `fw_baseline` firmware points whose apparent
"firmware variance" was partly this bug.

**OQ-MIXEDUDT, resolved 2026-08-27.** `mixedudt_messy_def_only/1_instance/
25_instance` real captures (19,384 / 19,704 / 25,472) land within
0.37%-2.65% of the current engine's prediction — comfortably inside the
acceptable band. The existing UDT-definition + per-tag formulas already
generalize to a realistic messy/nested member mix; no formula change
needed.

## Stale-open-question sweep, 2026-08-25

A review of every numbered OPEN_QUESTIONS.md item found that 2 of
them had to already be closed by real capture data that had landed
on disk but was never reconciled back into a conclusion — same root cause
as the CPT/JSR findings logged elsewhere this date.

**OQ-XPROGREF, resolved 2026-08-25.** Was tracking a genuine-looking
-3,948-byte negative gap on the two-program shared-alias case. The 3rd/4th
program files (`xprogref_3prog_shared_alias_n01000`,
`xprogref_4prog_shared_alias_n01000`) already had real capture data
(2026-08-24) sitting unreconciled. Live-recomputed against the current
engine: the gap no longer exists at all — single=0 delta, two-program=-16,
3-program=-32, 4-program=-48 (a clean -16/rung per each additional
program, <0.05% of file total throughout). Whatever fixed the alias
formula in an earlier pass already resolved this as a side effect.

**OQ-STRINGUDTMEMBER (builtin-as-UDT-member piece), resolved 2026-08-25.**
Was tracking a 2-D `correction(m,n)` surface derived from two 1-D slices
(`correction(m,n=1)=2m-4`, `correction(m=1,n)=-2n`). The disentangle files
needed to tell a bilinear surface apart from a simple additive one
(`stringclose_udtmember_builtin_2members_n03`, `_3members_n03`) already
had real capture data (2026-08-24) sitting unreconciled. Live-recomputed
against the current (plain, uncorrected) engine: residuals are 0, 0, +2,
+6 bytes across all 4 points (2/3 members × 1/3 instances) — no correction
term needed at all. Whatever fixed STRING-in-UDT sizing in an earlier pass
already resolved this too.

**Two generator bugs, fixed 2026-08-25, still awaiting recapture (not a
real open question, just implementation status).** Double underscores are
forbidden in Rockwell tag names — a name-length padding filler could
produce one; fixed in 3 places (`cli.py`, `gen_string_tagoverhead.py`,
`gen_string_batch2.py`) to avoid a trailing `_`. AOI call-site tag count
must match the definition's Required/Visible parameter count — 2 files
(`axis_aoi_inout_1_instance`, `axis_full_combo`) wired a value into a
param declared hidden by default; fixed by marking it `required=True,
visible=True`. Both regenerated, lint-clean, stale capture data cleared —
just needs to go through the normal capture pipeline like anything else.

## OQ-JSRPARAMCOST, fully wired 2026-08-25

**CAPTURE ERRORS: 4 row(s)** — rows owned by this question that captured with Studio build errors. The question is closed; the rows outlive it, so the count is recorded here rather than being lost.

JSR's own flat weight (72/rung) was already confirmed. The per-param cost
formula (`delta(n,R) = A(n) + B(n)*R`, `B(n) = 4 + 20*n`, `A(n) = 104 +
20*n`) was confirmed general the same day off a 3rd real point (n=8), but
stayed unwired since `parser/logic.py` never parsed a JSR call's argument
list, only the target routine name.

JSR parameter cost, wired properly:
- `parser/logic.py`'s new `_jsr_calls()` reads `n` straight off each real
  `JSR(...)` call's own 2nd argument (Studio 5000 itself writes the
  declared param count there — confirmed real shape via the full
  `samples/local/` corpus) into `RoutineLogic.jsr_calls`.
- `sizing/constants.py`'s new `JsrParamCostModel` (`a_cost`/`b_cost`),
  loaded from `memory_model.yaml`'s new `jsr_param_cost` block.
- `sizing/logic.py` adds `B(n)` per real call site, on top of the
  existing flat JSR weight.
- `sizing/report.py` builds a target-routine → param-count map across the
  whole file, then charges `A(n)` exactly once per distinct JSR target
  routine (never per call site, never per calling routine) — the target's
  own Parameters-block declaration cost, previously not charged at all.

Verified end-to-end (not just hand-derived) against all 6 real
`jsr_paramcount_n05/08/10_r00100/r01000` capture points: 4 exact, the
other 2 (both n=8) off by the same small +8 universal noise seen
elsewhere in this project. Two new unit tests cover the not-double-
counted case (single call) and the multiple-call-sites-to-one-target case
(A(n) charged once, not per call site).

**CORRECTION, 2026-08-29: "fully wired" was wrong — this covered INPUT
params only.** `group_param_count`'s calibration files always called
`RET()` empty (no return value), so B(n)/A(n) never saw a single real
byte of output/return-param cost — a real, sizeable gap silently
undetected until a full manifest.csv audit found `jsr_mixedio_5in_2out_r01000`/`jsr_multiret_n04_r01000` (real
captures from 2026-08-23) sitting unreconciled, both off by +40,040 and
+40,332 respectively. Both isolate to ~20/output-arg (2 output args each,
matching `b_per_param` exactly) — wired as `output_param_cost=20`,
charged once per output arg per call site (`_jsr_calls()` now returns
`(target, n_in, m_out)`, `m_out` computed from the real
`JSR(name, N_in, in_1..in_N, out_1..out_M)` syntax). `jsr_mixedio` now off
by +40 (noise-band), `jsr_multiret` by +332 — the callee's own one-time
`A(n)` Parameters-block cost almost certainly also needs an output-param
term (real target-routine Parameters blocks include both Input and Output
entries), but that effect is too small relative to a 1-distinct-target
sample to isolate from noise here — flagged as OQ-JSRPARAMCOST in
OPEN_QUESTIONS.md rather than force-fit or silently left uncorrected in
this file.

## OQ-AOIDEF name-length step formula, CLOSED 2026-08-30

An AOI type name's contribution to its own definition cost follows
`8*max(0,(len(name)-8)//4) - 8` -- confirmed exact against all 7 real
`aoiname_len08/09/13/16/20/25/30_def_only` points, which had been sitting
unreconciled. Wired into `AoiDefinitionModel.name_length_bytes` (used by
`compute_aoi_definition_cost` in `sizing/udt.py`), with a matching
`.namelen` breakdown row added to `tree.py`'s `_expand_aoi_definition` so
the UI drill-down sum stays consistent with the total.

The first version wired used divisor `(len-7)//4` instead of `(len-8)//4`
-- both reproduce all 7 tested points identically (none of the 7 sit at
`len % 4 == 3`, the one residue class where the two divisors disagree), so
the bug was invisible against that dataset alone. Caught by cross-checking
two already-captured, unreconciled AOI-array-packing files that differ
ONLY in AOI type name length and are otherwise byte-identical in shape (10
BOOL In/10 BOOL Out/10 BOOL Local, array of 16 instances):
`aoipack_bool_dense_array_n16` (`AoiPureBoolDense`, 16 chars) and
`aoipack_bool_boundary_n16` (`AoiPureBoolBoundary`, 19 chars). Same shape,
same array length -- real captured bytes must be identical once the
(separately confirmed) array-of-instances cost is subtracted out, but the
old divisor put len=19 one bucket higher than len=16, producing a genuine
8-byte prediction mismatch between two files that should have predicted
the same total. `(len-8)//4` resolves it to 0 bytes apart while leaving
all 7 originally-tested points exact.

Investigating that cross-check further turned up a second, larger,
**still-open** issue with the array-of-AOI-instances per-element formula
itself (previously tagged KNOWN) -- see OQ-AOIBOOLPACK-PAIRING in
OPEN_QUESTIONS.md; confidence downgraded to FITTED pending new capture
data (`gen_aoi_boolpack_pairing.py`, 23 files, generated but not yet
captured).

## OQ-INSTRFIRSTPASS, CLOSED 2026-08-30

34/36 real instruction weights confirmed and wired. SCP/FBC/PID were the
2 remaining gaps -- SCP had no second real example to validate a weight
against, FBC and PID had zero real examples at all (PID also needs its
own structure tag, never built). Deprioritized 2026-08-25 as a
safety-related feature, then explicitly closed as out-of-scope 2026-08-30
rather than left open
indefinitely awaiting data that isn't coming.

Small residual not worth reopening the question over: a flat +12 byte
gap (corrected from a misrecorded +6) across all 64 clean `instrfirst_*`
files, ~0.06% of file total, narrowed to an interaction effect among the
7 shared tag types the pool declares but not isolated to which one.

## Real generator bug: SafetyLocked="true" with no SafetySignature, fixed 2026-08-30

L8 safety files failed to generate ACD files. Root cause found by cross-checking all 9 real corpus files
carrying a `SafetyInfo` element: every one with `SafetyLocked="true"`
ALSO carries a real `SafetySignature` attribute (a GUID hash + timestamp
from Studio 5000's actual sign/lock workflow); every one with
`SafetyLocked="false"` has none -- 9/9, zero exceptions. Every generator
in this project hardcoded `SafetyLocked="true"` with no signature at
all -- a combination that appears in zero real files and is almost
certainly what Studio 5000 rejects on import, since a locked safety
program is a claim that real signing happened.

Fixed in both places this template is built: `wrapper.py`'s `build_l5x`
SIL2/SIL3 branches and `gen_fw_catalog_matrix.py`'s `_build_xml` (the
L8xES GuardLogix safety-catalog matrix). Since none of these generated
files ever perform a real sign/lock, `SafetyLocked="false"` is the
correct value, matching every real unsigned file.

Regenerated all 30 L8xES safety-catalog matrix files and all files
downstream of `wrapper.py`'s safety template (`gen_module_bender_full.py`,
`gen_module_sweep.py`, `gen_module_sweep_gap.py`,
`gen_module_sweep_variants.py` -- 117 files total, re-run through their
own generators). 13 additional files with no live generator reference
anymore (orphaned from an earlier iteration of the module-sweep scripts,
2 of which — `modulesweep_1734_ob8s_a/b` — carry real captured
`actual_bytes` that must not be disturbed) were patched directly in
place (string substitution only, doesn't touch `predicted_bytes` --
`SafetyInfo` has no sizing weight). Full 1707+ file corpus re-swept: 0
crashes, 0 remaining `SafetyLocked="true"` instances anywhere.

## OQ-PREDEFINED, CLOSED for all 195 known types

the conversion+capture pipeline ran the full 184-file
`gen_predefined_probe.py` blank-tag discovery batch; 174 imported clean
and got a real Capacity delta. Wired all 174 into `memory_model.yaml` in
one batch (ASSUMED, n=1 real capture each). MESSAGE (688 bytes) and
ALARM_DIGITAL (973 bytes) -- the two longest-standing genuinely-blocked
types -- are now resolved with real totals. SFC_STOP (wired 2026-08-28
from real L5K data) matched the new real capture EXACTLY (0 residual),
independently confirming the derivation method itself, not just that one
type.

**`CONFIGURABLE_ROUT` was WRONGLY documented as unmodeled** -- its real
capture (`predefprobe_configurable_rout`, actual 18,264) was on file in
manifest.csv the whole time and IS wired (52 bytes, same value as
`BUS_OBJ`'s real capture, plausible for a small structure, not a
data-entry error -- cross-checked directly). The commit that wired the
other 174 said "CONFIGURABLE_ROUT remains unmodeled" while its own diff
actually included it correctly -- the prose was wrong, the code wasn't.
It's very likely Safety-family (name root matches `CROUT`, the
already-confirmed Safety-only instruction) -- see OPEN_QUESTIONS.md
OQ-SAFETYSCOPE-SIZING for the still-open display-policy question this
raises (not a data question).

**Note on MessageType variance, still a minor open thread**: MESSAGE's
688-byte total was captured against ONE real MessageType (CIP Generic).
`gen_msg_typesweep.py` built 8 files (one per real MessageType found in
the corpus: CIP Generic, CIP Data Table Read/Write, PLC5 Typed
Read/Write, PLC5 Word Range Write, SLC Typed Read/Write) to test whether
688 holds flat across all 8 (confirming the axis-tag-style "lots of
config, always the same data size" pattern already seen elsewhere in
this project) or varies by attribute-set complexity. Built, awaiting
capture -- low priority given the strong flat-regardless-of-config
precedent this project has seen repeatedly (AOI Required/Visible flags,
etc.), but not yet directly confirmed for MESSAGE specifically.

**Sibling native-structure gap, found 2026-08-27** verifying drill-down
completeness: the UI must browse down to base structure level for every
UDT and AOI. Drill-down itself is fully confirmed for everything the
engine CAN size -- a recursive walk of all 2,780 UDT/AOI definitions across
a real 64-file corpus reached 4,502,812 true leaves with zero bad
leaves and zero silent dead-ends. A real, separate gap surfaced along the
way: any tag whose type transitively includes a member typed SFC_STEP/
SFC_ACTION/FBD_TIMER/SCALE/CAM_PROFILE/DCI_STOP/RATE_LIMITER/
CONFIGURABLE_ROUT/ALARM_DIGITAL/FBD_ONESHOT/FBD_MATH -- confirmed present
in 0 of 64 real files' own `<DataType>`/`<AddOnInstructionDefinition>`
blocks, same as MESSAGE -- couldn't be sized at all (`UnknownDataTypeError`,
caught cleanly by report.py, so the whole file doesn't break, but that tag
was silently excluded from the treemap/list, only showing up in the small
errors footer). 1,277 tag-sizing errors across 24/64 real files traced to
this.

**Wired 2026-08-27.** Native instruction data types are documented in the
Rockwell instruction manual, but rather than trust an instruction-manual citation blind (this
project's own ground-truth discipline -- CLAUDE.md -- wants a real capture
or real corpus evidence first), checked whether the real corpus itself
already reveals the layout via `Data Format="Decorated"` -- it does.
Bender134053_201104.L5X alone has 272 real `SFC_STEP` and 97 real
`SFC_ACTION` tag instances with full decorated field lists; other files
had real (if sparser) evidence for the rest. The mechanism: a predefined
structure's real `Data Format="L5K"` raw value array is one scalar per
DINT-sized field (same convention that already gives TIMER's 3-element/
12-byte L5K array its real shape) -- so the array's length x 4 bytes IS
the real total, independent of how many of those DINTs are further
bit-packed status flags. Confirmed zero-variance across every real
instance checked: 272/272 SFC_STEP (28 bytes: Status+PRE+T+TMax+Count+
LimitLow+LimitHigh, 7 DINT), 97/97 SFC_ACTION (16 bytes: Status+PRE+T+
Count, 4 DINT), 5/5 FBD_TIMER (48 bytes), 4/4 FBD_ONESHOT (12 bytes), 2/2
FBD_MATH (16 bytes); RATE_LIMITER (92 bytes) and SCALE (52 bytes) only
1 real instance each so far. Wired into `memory_model.yaml`
`predefined_structures` at ASSUMED confidence (real and zero-variance,
but not yet independently confirmed against an actual controller
memory-capture delta the way TIMER/COUNTER/CONTROL are) -- closed 523 of
the 1,277 errors. `sizing/tree.py` deliberately does NOT extend the
generic TIMER/COUNTER/CONTROL 3-way-split drill-down to these -- their
field counts vary (SFC_STEP has 7, SFC_ACTION has 4, RATE_LIMITER has
23) and only the TOTAL is confirmed, not a per-field byte attribution,
so a fabricated even split would be worse than staying a correctly-sized,
non-drillable leaf (`_THREE_FIELD_PREDEFINED` set).

**MESSAGE and ALARM_DIGITAL member lists sourced from RM018A, 2026-08-27**
(every instruction data type needs sizing, scoped to 1756-RM018A
specifically). Read directly from the real
manual PDF (`samples/1756-rm018_-en-p.pdf`, 927 pages, via
`pdftotext -layout` + form-feed page-indexed navigation), not guessed.

*MESSAGE* (RM018A pages 142-147): real member list — `.FLAGS` INT (bit-
mapped status word: bit 2=.EW, 4=.ER, 5=.DN, 6=.ST, 7=.EN, 8=.TO, 9=.EN_CC —
confirmed by the manual's own bit table that these 7 BOOL "members" are
aliased VIEWS into `.FLAGS`, not separate storage, exactly the same pattern
already established for TIMER's `.EN`/`.TT`/`.DN`), `.ERR`/`.EXERR`/
`.REQ_LEN`/`.DN_LEN` INT, `.ERR_SRC` SINT, `.DestinationLink`/
`.DestinationNode`/`.SourceLink`/`.Class`/`.Attribute` INT, `.Instance`/
`.LocalIndex` DINT, `.Channel`/`.Rack`/`.Group`/`.Slot` SINT, `.Path` STRING,
`.RemoteIndex` DINT, `.RemoteElement` STRING, `.UnconnectedTimeout`/
`.ConnectionRate` DINT, `.TimeoutMultiplier` SINT. Non-STRING fields sum to
a KNOWN 46 bytes (10 INT×2 + 6 SINT×1 + 5 DINT×4) under this project's
already-confirmed tight-packing/no-alignment rule for structure members —
**but the total stays unwired**: RM018A never states `.Path`/
`.RemoteElement`'s real STRING capacity (searched the manual text directly,
not found), and guessing the default 82-char built-in STRING size would be
exactly the kind of fabrication CLAUDE.md forbids. `gen_msg_typesweep.py`'s
8 files (already built, awaiting capture) are still the right path to the
real total — once captured, the confirmed 46-byte non-STRING subtotal lets
the STRING length be backed out exactly rather than assumed.

*ALARM_DIGITAL/ALMD* (RM018A pages 53-64): real member list — 23 Input
BOOL (EnableIn/In/InFault/Condition/AckRequired/Latched/ProgAck/OperAck/
ProgReset/OperReset/ProgSuppress/OperSuppress/ProgUnsuppress/
OperUnsuppress/OperShelve/ProgUnshelve/OperUnshelve/ProgDisable/
OperDisable/ProgEnable/OperEnable/AlarmCountReset/UseProgTime), 1 Input
LINT (ProgTime), 4 Input DINT (Severity/MinDurationPRE/ShelveDuration/
MaxShelveDuration), 8 Output BOOL (EnableOut/InAlarm/Acked/InAlarmUnack/
Suppressed/Shelved/Disabled/Commissioned), 3 Output DINT (MinDurationACC/
AlarmCount/Status — Status.0/.1/.2 = InstructFault/InFaulted/SeverityInv
are bit-aliases of the Status word, same pattern as MESSAGE/TIMER, NOT
separate storage), 6 Output LINT (InAlarmTime/AckTime/RetToNormalTime/
AlarmCountResetTime/ShelveTime/UnshelveTime). Cross-validated exactly
against the real `Comms_Bus1_ALMD` tag in `samples/local/L5X_Samples/
MRFP_Edger_2026_06_01_r00.L5X` — every real `<AlarmDigitalParameters>`
attribute name matches the manual's Input Parameter table verbatim.
**Two genuine unknowns block a total**: (1) whether the 31 scalar BOOL
members bit-pack 8-per-hidden-SINT (the confirmed convention for ordinary
UDTs) or take a full byte/word each in this controller-native structure —
unconfirmed, native structures go through different firmware than user
UDTs; (2) real ALMD tags always carry an `<AlarmConfig>` message/class-text
block alongside the base structure (confirmed: both real corpus files with
ALMD tags have it) — unknown whether that text counts toward the tag's own
byte cost or is stored/compiled separately. `gen_almd_singletag.py` built
2026-08-27 (2 files: `almd_minimal` isolates the base structure with
1-char message/class text, `almd_realtext` uses real-length text copied
from `Comms_Bus1_ALMD` to test question (2) directly) — awaiting capture,
mirrors the MESSAGE sweep's isolate-one-variable-at-a-time approach.

*COUNTER cross-check* (RM018A pages 92-93): `.CD`/`.DN`/`.OV`/`.UN` BOOL
(bit-aliased status word) + `.PRE`/`.ACC` DINT — matches the already-wired
3-DINT/12-byte model exactly. No change needed; first time this project's
COUNTER model has been confirmed against a real Rockwell primary source
rather than only empirical black-box capture.

**Negative finding, saves future effort**: the L5K-raw-array-length
technique that solved SFC_STEP/SFC_ACTION/FBD_TIMER/etc. (real `Data
Format="L5K"` value-array length × 4 bytes = real total) does NOT work for
either MESSAGE or ALARM_DIGITAL — grepped every real instance of both types
across the full `samples/local/` corpus (not just the 64-file subset)
and confirmed zero use `Format="Decorated"` or `Format="L5K"`; Rockwell's
export tooling always uses a specialized semantic view (`Format="Message"`/
`Format="Alarm"`) for these two types instead. Don't re-attempt that
technique on these two — go straight to a real capture.

**RESOLVED 2026-08-29, real capture batch closes 174 of 184 probe files.**
the conversion+capture pipeline ran the full `gen_predefined_probe.py`
batch. Derivation method: the live engine, run fresh against each probe
file, predicts a uniform `18128` for every still-unmodeled type (real
`empty_project_baseline`(13296) + `task_program_shell`(4816) +
`routine_logic`(16, the file's own default NOP rung) — the unresolvable
`Probe1` tag itself contributes 0 and raises one caught `SizeError`, which
is exactly the uniform "1 error" every one of these rows showed). So
`real_structure_bytes = real_actual_bytes - 18128 - tag_overhead(84,
real "Probe1" 6-char name)`. Validated against `SFC_STOP`, the one type
already wired from real L5K data before this batch landed: the new real
capture matched the live prediction EXACTLY (0 residual) — confirms the
derivation method itself, not just that one type. All 174 resolved values
wired into `memory_model.yaml` `predefined_structures` at ASSUMED
confidence (n=1 real capture each). Full real values, sorted:

```
4:    ALARM_SET_CONTROL, CONNECTION_STATUS, PHASE_INSTRUCTION,
      RAC_ITF_DVC_PWRDISCRETE_CMD/SET, RAC_ITF_DVC_PWRMOTION_CMD/INF/SET,
      RAC_ITF_DVC_PWRVELOCITY_CMD/SET, SEQ_BOOL, SEQ_INT, SEQ_SINT
12:   DATALOG_INSTRUCTION, DOMINANT_RESET, DOMINANT_SET,
      EXT_ROUTINE_PARAMETERS, FBD_BOOLEAN_XOR, FBD_COMPARE, FBD_CONVERT,
      FBD_LIMIT, FBD_LOGICAL, FBD_MASK_EQUAL, FBD_MATH_ADVANCED,
      FBD_TRUNCATE, FLIP_FLOP_D, FLIP_FLOP_JK, ODOMETER,
      P_INTERLOCK_BANK_STATUS, P_STRAPPING_TABLE_ROW, SEQ_DINT, SEQ_REAL,
      SEQ_TRANSITION, SERIAL_PORT_CONTROL, SIGNED_ODOMETER
20-28: CAM_EXTENDED, FBD_COUNTER, FBD_MASKED_MOVE, P_COMMAND_SOURCE,
      SELECT, SELECTABLE_NEGATE, STRING_16 (20); FBD_BIT_FIELD_DISTRIBUTE,
      HMIBC, MANUAL_VALVE_CONTROL, MAXIMUM_CAPTURE, MINIMUM_CAPTURE,
      OUTPUT_CAM, OUTPUT_COMPENSATION, P_LEAD_LAG_STANDBY_MOTOR, PHASE,
      POSITION_DATA, SAFE_DIRECTION, UP_DOWN_ACCUM (28)
MESSAGE: 688. ALARM_DIGITAL: 973 (both previously genuinely blocked --
      see the negative finding above). ALARM_ANALOG: 2461. PID: 180.
      PID_ENHANCED: 396. PIDE_AUTOTUNE: 972.
Full table (all 174): see memory_model.yaml predefined_structures,
      block dated 2026-08-28/29.
```

Note: `ALARM_ANALOG`(2461), `ALARM_DIGITAL`(973), `ENERGY_BASE`/
`ENERGY_ELECTRICAL`(107 each) are the only 4 values not a multiple of 4 —
checked, not a bug in the subtraction (every other value is a clean
multiple of 4/8/12): plausibly genuine odd-byte real internal padding for
those 4 specific structures (several mix SINT/STRING content with DINT
content, unlike the mostly-DINT-uniform structures that land on round
numbers). `CONFIGURABLE_ROUT`: CORRECTED 2026-08-29 — this line was
wrong. `predefprobe_configurable_rout` DID capture real data (actual
18,264, same as `BUS_OBJ`'s real capture) and IS wired at 52 bytes,
already included in the 174-count and the "all 195" total in item 5
above. Full table: 175 real-derived types now, not 174.

**Safety-scope note applies to this whole new batch, not just DCI_STOP.**
Several of the 174 (`DCI_*`, `SAFE_*`/`SAFELY_*`, `MUTING_*`,
`LIGHT_CURTAIN`, `TWO_HAND_RUN_STATION`, `EMERGENCY_STOP`,
`REDUNDANT_INPUT`/`OUTPUT`, `ENABLE_PENDANT`, `DIVERSE_INPUT`,
`SAFETY_MAT`, `SAFETY_FEEDBACK_INTERFACE`, `DOMINANT_SET`/`RESET`, and
`CONFIGURABLE_ROUT` — added 2026-08-29; its name root matches `CROUT`, the
already-confirmed Safety-only instruction requiring a GuardLogix/Safety
CPU) are Safety-Instructions-family types. The VALUES are real and
wired; whether Safety-scoped tags should be included in the displayed
total at all is the same still-open product decision flagged for
DCI_STOP originally — not re-decided here, just now applying to a much
bigger list of types.

**Two findings from this same batch, WIRED 2026-08-29** (`report.py`
`build_report` now reads `SoftwareRevision`/`ProcessorType` straight off
the L5X root/Controller element; constants in `memory_model.yaml`
`firmware_baseline_delta`/`safety_capable_baseline_delta`, ESTIMATED tier
like `module_overhead`, never hardcoded inline per CLAUDE.md):

1. **Real per-firmware-version baseline deltas.** 1756-L8x/5069 (non-
   safety-suffix) on v34/v35 both confirm the already-known 18,112 exact
   (0 residual, unchanged -- v34/v35 stay on the default/no-adjustment
   path). v31/v32 land IDENTICAL at +11,240 (1756 catalogs; actual
   ≈29,368-29,376) and v33 at +14,248 (actual≈32,376-32,384) -- both now
   wired, keyed off the firmware major parsed from `SoftwareRevision`.
   **Correction:** the "v38 shows a real +304" claim from the prior pass
   was wrong -- that row (`fwmatrix_v38_1756_l81e`) is
   `WINDOW TITLE MISMATCH`-flagged in manifest.csv (its 18,416 actual_bytes
   belongs to a different file, `fwmatrix_v35_5069_l340ers2`), so it was
   never real v38 evidence. Manifest row cleared per CLAUDE.md's standing
   rule; v38 stays unadjusted (default_bytes=0) until a real capture
   lands.
2. **Real 5069-safety-model baseline overhead, independent of SafetyInfo
   content.** The 5069 Motion+Safety-suffix catalogs (`L330ERMS2`,
   `L340ERS2`) show a real +296 byte baseline over their non-safety
   siblings (`L330ER`, `L340ER`) on the SAME firmware (18,416 vs 18,120 at
   v34/v35; the identical +296 gap reproduces independently at v31/v32 and
   v33, confirming no firmware x safety interaction term is needed) --
   the mere fact of being a safety-CAPABLE processor model costs real
   memory before any actual safety configuration exists. n=2 real
   catalogs directly confirmed, now wired and applied to the whole 5069
   safety-suffix family (`ProcessorType` ending `S2`/`S3`) on the same
   "same physical family" extrapolation basis this project already uses
   for L72-L75 vs. L71.

Validated against all 50 real (untainted) `fw_catalog_matrix` rows: every
one now predicts within 16 bytes of its real actual_bytes (the same small
per-file noise band already accepted at v34/v35), down from errors as
large as 14,552 bytes before this fix. Cross-checked against 5 more real
points from an earlier, separate `fw_baseline` batch (different generator,
same real capture discipline): `l81_v31`/`v32`/`v33` (blank 1756-L81E)
land within 16 bytes too, independently confirming the firmware delta
outside the `fw_catalog_matrix` batch it was fitted from.

**One real caveat surfaced by that same cross-check, not a regression:**
`v35_l306erms2`/`v35_l306erms3` (also from the `fw_baseline` batch) are
`5069-L306ERMS2`/`MS3` -- safety-suffix, so they now correctly get the new
+296 delta -- but unlike every `fw_catalog_matrix` safety file, these two
ALSO carry a real populated `SafetyTask`/`SafetyProgram` pair
(`SafetyLevel="SIL2/PLd"`, 0 real rungs). Prediction is now 1,424 off
(was 1,128 off before this fix, so not newly broken, just already
inaccurate) -- `task_program_overhead`'s `task_extra`/`program_extra`
(fitted from ordinary Standard-class extra tasks/programs) doesn't
correctly model a Safety-class task/program pair's real marginal shell
cost, a distinct, already-known, already-out-of-scope gap
(`is_safety_project` fires its red warning banner for both files, so the
user is never shown this total without the caveat). `firmware_baseline_delta`
and `safety_capable_baseline_delta` themselves are validated only against
BLANK safety-capable-processor files (no real Safety Task/Program content)
-- accurate for that case, not claimed accurate once real (unsized)
Safety Task/Program content is also present in the same file.

**Also from this same push: real evidence AlarmConfig message/class text
length adds to ALMD's real cost**, confirming the open question from
`gen_almd_singletag.py`'s own docstring. `almd_minimal` (1-char text):
19,719. `almd_realtext` (real-length text copied from `Comms_Bus1_ALMD`):
19,754 -- a real +35 byte delta for the longer real text, on top of the
instruction-call + real ALMD structure content these two files also
carry (not directly comparable to the bare-tag 973-byte ALARM_DIGITAL
figure above, which isolates the structure alone).


## Second real generator bug: L8xES Local module ports missing SafetyNetwork, fixed 2026-08-30

Generated safety modules were failing consistently during conversion, and
the module generator needed rebuilding. Found without an error
message -- same methodology as the SafetyLocked fix above, systematic
attribute-by-attribute diff of a generated GuardLogix-ES file against a
real one.

`samples/local/SJ_Gormley_20251112_r02.L5X`'s own Controller
`ProcessorType` is literally `1756-L81ES` -- the exact catalog family
reported failing. Its real Local module's Ports (`Port Id="1"` ICP and
`Port Id="2"` Ethernet) BOTH carry a `SafetyNetwork="16#0000_..."`
attribute. `gen_fw_catalog_matrix.py`'s `_local_ports_xml` had zero
awareness of `is_safety` at all -- it only ever added `Class="Safety"` to
the Task/Program, never touched the CPU's own Local module Ports. This
is a completely separate code path from `wrapper.py`'s `build_l5x`,
which already got the analogous SIL2/SIL3 SafetyNetwork fix on
2026-08-28 for its module-sweep files -- that fix was never cross-applied
to the L8xES safety-catalog matrix generator.

Real SafetyNetwork values are device-unique (confirmed real corpus
values are effectively random 64-bit hex, not sequential or derivable) --
no way to fabricate a "real" one, so this uses the same
synthetic-but-correctly-formatted placeholder convention `wrapper.py`
already established, one distinct value per port. Regenerated all 30
L8xES safety-catalog matrix files. Full corpus re-swept: 0 crashes.

Checked the rest of the Controller-level attributes for other
differences (`AutoDiagsEnabled`, `TimeSlice`/`ShareUnusedTimeSlice`) --
both differ from the real Gormley reference but neither is
Safety-specific or newly found; `TimeSlice` was already established
2026-08-28 as Studio-5000-optional (real files import fine with or
without it), and `AutoDiagsEnabled` is plausible per-project variance,
not a structural gap.

## OQ-BRANCHDEPTH, CLOSED 2026-08-30

Tests requested a week earlier had still not been decompiled -- the same
recurring pattern as CPT/1769/AOI in that batch: 16 real capture points (`branchdepth_legs01/03/05`,
`branchdepthc_legs02/04/06/08/10/15/20/30`, `branchdepthstag_d01-06`) were
sitting in manifest.csv with real `actual_bytes` -- "Reconciled from
the local branch (james-capture-aug24)" -- unreconciled into the
sizing engine this whole time.

The real mechanism, once understood rather than curve-fit blind: every
real branch (`[...]`) compiles to real BST/NXB/BND-family instructions --
one BST + one NXB per extra leg + one BND, i.e. `(leg_count + 1)`
instructions per bracket group, and **every one of those instructions
costs a flat 4 bytes**. Confirmed on BOTH independently-generated
datasets with the SAME rate, not two separate fits:

- Flat leg-count width (`branchdepthc_legsN`, N=2..30, single level):
  `4 * (N + 1)` bytes/rung. 10/10 real points exact.
- Staggered/nested depth (`branchdepthstag_dD`, D=1..6, always 2 legs per
  level, D nested levels): `4 * 3 * D` bytes/rung (3 instructions/level x
  D levels). 6/6 real points exact.
- `legs01` (a single leg -- i.e. no real branch at all) correctly costs 0,
  the degenerate case, not a formula exception.

Wired end-to-end: `parser/logic.py`'s new `_branch_bracket_instruction_
count`/`_parse_branch_group` (a real bracket-matching scan, not a naive
regex -- correctly distinguishes a branch-open `[` from an array-index
`Tag[5]` bracket by checking the character immediately before it, and
correctly recurses through nested/staggered branches, counting legs only
at paren-depth 0 so a multi-arg instruction inside a leg like `MOV(A,B)`
doesn't get miscounted as two legs). `RoutineLogic.branch_bracket_
instruction_count` carries the total; `sizing/logic.py` multiplies it by
the new `branch_bracket_cost_per_instruction=4` constant
(`memory_model.yaml logic_instructions`), additive on top of every leg's
own already-counted instruction weight.

Verified end-to-end (not just hand-derived): all 17 real files predict
EXACTLY through the live `build_report` pipeline, zero delta. Full
1707-file generated corpus AND all 64 real `samples/local/` corpus files
re-swept: 0 crashes (the real corpus files have genuinely complex nested
branches -- 41,603 `[` characters in one real file alone -- so this is a
meaningful stress test of the bracket-matching parser, not just the
synthetic calibration shapes). 4 new unit tests added
(`tests/test_logic_sizing.py`): no-branch is a no-op, flat branch costs
legs+1 instructions, nested branch sums recursively, array-index bracket
is never miscounted as a branch.

Confidence: FITTED, not KNOWN -- only ever tested at n=1000 rungs and one
tag shape (BOOL XIC legs); linearity with rung count is assumed by this
project's own established convention (every other per-instruction rate
here scales linearly with rung/call count), not independently confirmed
at a 2nd rung count for this specific formula.

## Third real generator bug: GuardLogix 5580 (L8xES) wrong ProductCode, fixed 2026-08-30

A second conversion failure on `fwmatrix_v35_1756_l85es.L5X`, reported AFTER the SafetyLocked and SafetyNetwork fixes
above had already landed and been pushed, ruling both out as the cause
for this file (confirmed directly: `SafetyLocked="false"` already present
in the named file). Root cause was a third, independent bug: `gen_
fw_catalog_matrix.py`'s `_L8XS_PRODUCT_CODES` assumed "L81ES uses the
SAME ProductCode as plain L81E" (164) — a same-hardware plausibility
argument, never actually checked against a real L81ES corpus file.

Real corpus grep across 5 independent real files (`SJ_Gormley_
20251112_r02.L5X`, `Bender134053_201104.L5X` — 2 copies —, `RobbinsGrn_
2026_05_13r00.L5X`, `FlareFunction_311D_240731.L5X`) shows GuardLogix
5580 ProductCodes live in a COMPLETELY SEPARATE numbering space from the
non-safety L8x: `1756-L81ES` is real `ProductCode="211"` (4 files agree),
`1756-L84ES` is real `ProductCode="214"` (`FlareFunction_311D` — never
found by this project until this investigation). 211→214 across
L81ES→L84ES is exactly +1 per catalog step, so L82ES/L83ES/L85ES are now
inferred as 212/213/215 — the same sequential-pattern convention this
project already uses elsewhere, but now anchored to 2 real confirmed
points on the CORRECT numbering space instead of 1 guess built on a
wrong one.

Fixed in `gen_fw_catalog_matrix.py`'s `_L8XS_PRODUCT_CODES`. All 30
L8xES `fw_catalog_matrix` files regenerated (174-file full matrix
re-run to keep everything in sync). `_L8XS_INFERRED` updated to drop
L84ES (now confirmed, no longer inferred). Full corpus re-swept (1793
generated+real files): 0 crashes. Full test suite: 140/140.

This is the reason the L8xES batch has never had a single successful
capture, on top of (not instead of) the two SafetyLocked/SafetyNetwork
bugs above — all three needed fixing before any L8xES file could import.

## OQ-LEGACYNETOVERHEAD, CLOSED as deliberate scope exclusion, 2026-08-30

ControlNet and all legacy networks are excluded from scope. Earlier the
same day this had been wrongly reopened as a data
gap: `modulesweep_1756_cnb_d` (a real ControlNet bridge module,
genericized from real corpus, 2026-08-24 capture) shows a real +448 byte
gap against the live engine, and got briefly wired as a flat
`module_overhead_by_catalog['1756-CNB/D']` entry (2,120 bytes) before
the correction landed -- reverted.

Decision: ControlNet, DeviceNet, DH+, DH-485, and Remote I/O (RIO) bridge
modules are excluded from sizing entirely, the same treatment this
project already gives rack-aliased (`RackConnection`/`InAliasTag`) and
processor-embedded (`CatalogNumber="Embedded"`) modules -- no
`module_overhead` charged, `module_defined_bytes` not summed into the
total, a `SizeError` flags it as unmodeled-but-visible instead of
silently guessed or flat-fitted.

Implementation:
- `parser/modules.py`: `ModuleInfo.port_types` (new field) captures every
  `<Ports><Port Type="...">` value off the module itself.
  `ModuleInfo.is_legacy_network` is true when that set intersects
  `_LEGACY_NETWORK_PORT_TYPES = {"ControlNet", "DeviceNet", "DH+",
  "DH-485", "RIO"}` -- real Port Type strings confirmed against
  gen_module_sweep.py's 1756-CNB/D ("ControlNet"), 1756-DHRIO/E ("RIO"),
  and 1756-DNB ("DeviceNet") fixtures, themselves sourced from real
  corpus captures.
- `sizing/report.py`: the existing `if module.uses_rack_connection or
  module.catalog_number == "Embedded":` exclusion block extended with
  `or module.is_legacy_network`, naming the matched Port Type(s) in the
  SizeError message.
- `sizing/memory_model.yaml`: removed the two other pre-existing flat
  `module_overhead_by_catalog` entries for this class that predate this
  decision -- `1756-DHRIO/E` (1,390 bytes) and `1756-DNB` (6,440 bytes) --
  both were ASSUMED-confidence guesses, not confirmed real per-catalog
  points, same problem as the briefly-wired `1756-CNB/D` entry.

Real corpus evidence backing this as correct, not just deferral: a full
grep of all 64 files in `samples/local/` (the real-capture reference
corpus) for Port `Type=` attributes finds ZERO ControlNet, DeviceNet,
DH+, or RIO entries anywhere -- the one real data point on hand
(`RobbinsGrn_2026_05_13r00.L5X`) isn't even part of that corpus set.
Nothing to isolate or decompose further unless a real project of the
starts using one of these networks.

## Two real bugs in the 1769-series re-add, found 2026-08-30 via live testing

Mid-batch-run: "Failed to set the 'Size' property (Chassis size exceeds
the allowable size for a chassis.)" on `fwmatrix_v31_1769_l30erm`, and the
same chassis-size error on a second file shortly after -- real
Studio 5000 rejections, not code-review catches, surfaced while the
1769 re-add (same session, same day) was still being tested.

**Bug 1: wrong Bus Size on every catalog except L33ERM.** The re-add's
`_local_ports_xml` used a single L33-only-confirmed Bus Size (17) as the
fallback for all 9 catalogs. Real per-catalog data, extracted directly
from the 9 already-real `samples/generated/fw_baseline/v35_*.L5X`
reference exports (genuine Rockwell exports checked into the repo, not
generated by any script): L16ER/L18ER/L18ERM/L19ER use Port
Type="PointIO" Bus Size=2; L24ER-QB1B=6; L24ER-QBFC1B/L27ERM-QBFC1B=8;
L30ERM=9; only L33ERM is genuinely 17.

**Bug 2, same root cause as the earlier L8xES ProductCode bug (an
untested same-hardware plausibility argument): the re-add's Local module
was the ONLY module emitted for every 1769 catalog.** Real data shows
L16ER through L27ERM-QBFC1B all carry a second, real embedded module
(`Name="Discrete_IO" CatalogNumber="Embedded"`, built-in discrete I/O
points) with real `ConfigTag`/`Connection` content specific to each
catalog's own I/O point count -- ranging from a few hundred bytes of
XML (L16ER) to over 41KB (L24ER-QBFC1B/L27ERM-QBFC1B, many more I/O
points). L30ERM/L33ERM genuinely have neither (bare processor-only
units), confirmed by their own real reference exports also lacking it --
not a gap in those two. This is exactly what `XMLSrv_E_IMPORT_ABORTED_
NO_CHANGES` was flagging on every 1769 file in the batch before Bug 1
was even found.

**Fix:** rather than re-derive this per-catalog complexity by hand
(the embedded module's internal Connection/ConfigTag shape isn't
something to guess at), the real `<Modules>` block from each of the 9
confirmed-real reference exports is used VERBATIM (`_1769_MODULES_XML`
in `gen_fw_catalog_matrix.py`) -- only the Local module's own Major/
Minor gets substituted per firmware version (exactly one substitution
site per catalog, asserted), matching how every other catalog in this
matrix already tracks the Controller's own MajorRev. The
EthernetPorts/EthernetNetwork shape (2 ports + a real `EthernetNetwork`
element -- unlike every other family in this matrix, which gets only 1
port and no `EthernetNetwork`) is identical byte-for-byte across all 9
real references, so it's one shared constant (`_1769_ETHERNET_XML`),
not per-catalog.

One more real wiring gap found while regenerating: the sizing engine's
own pre-existing (2026-08-27) rule that a `CatalogNumber="Embedded"`
module is unmodeled (SizeError, not summed) had never been exercised by
`gen_fw_catalog_matrix.py` before -- `write_sample`'s strict
"any error is fatal" check rejected the whole batch. Fixed: `_write`
now falls back to `write_sample_unmodeled` + `predicted_bytes=0` for
this specific, already-established-unmodeled case, same convention this
project already uses elsewhere for unmodeled predefined structures.

All 54 1769 files (9 catalogs x 6 firmware) regenerated. Full corpus
re-swept (1847 files): 0 crashes. 140/140 tests.

**CORRECTION, same day, a few hours later: this fix was itself wrong for
5 of the 9 catalogs, and has been un-wired.** the minimal
hand-built repro file (`ProcessorType="1769-L24ER-QB1B"`) hit the exact
same real Studio 5000 error this section describes fixing -- "Failed to
set the 'Size' property (Chassis size exceeds the allowable size for a
chassis.)" -- with `Bus Size="6"`, the value extracted verbatim above
from `fw_baseline/v35_l24er.L5X`. That broke most chassis sizes: chassis
sizes must not be guessed, only taken from a referenced real file. The
mistake: treating the `fw_baseline` reference
files as ground truth because they're genuine Rockwell exports checked
into the repo, without noticing that those specific files carry their
own "MANUAL ENTRY... clicking Estimate" caveat (built by switching
ProcessorType in Controller Properties from a base project to read
Capacity manually) -- which proves the *Capacity-read* step was manual,
but never proved the *content* had round-tripped through l5xgit import.
Extracting "real-looking" content from an unverified source is still a
guess, and this one was wrong. The only Bus Size value anywhere in the
corpus with independent real confirmation is L33ERMS=17
(`samples/local/DnR_Personal/TOYOTA_135453_20221024.L5X`, a genuine
customer file) -- and even that catalog is included in the "L24..L27
and the L3 series fail" report, so something else about it is still
unconfirmed too. See OQ-BASELINE-PROCFW in `docs/OPEN_QUESTIONS.md`:
`_1769_CATALOGS` is back down to the 4 PointIO-bus catalogs only
(empirically proven working in the live batch), and the other 5 are
pulled from automated generation -- 30 files and manifest rows removed --
until real per-catalog data exists. Not re-guessing.

## 1756-L85ES removed from the automated matrix, 2026-08-30

Live testing: L85ES fails on line 1 of the L5X across multiple firmwares
while L81ES..L84ES work. L81ES(211)/L84ES(214) are
real (4 and 1 independent real corpus files respectively); L82ES(212)/
L83ES(213)/L85ES(215) were all inferred from the same +1-per-catalog-
step pattern anchored on those two real points. the test shows
L82ES/L83ES import fine but L85ES does not -- real proof the sequence
isn't linear all the way to the top of the range, not that the
inference method itself is unsound (it correctly predicted 2 of 3).

Confirmed via web search that 1756-L85ES is a real, current Rockwell
product (GuardLogix 5580, 40MB standard / 3MB safety memory, top of the
line) -- this isn't a fake-catalog problem, just an unconfirmed
ProductCode with no second real anchor left to re-derive it from
(only one real point, L84ES=214, borders the gap; the L81ES anchor is
too far away to trust a linear extrapolation across an already-proven-
nonlinear stretch).

Rather than guess again and cost another test cycle, removed
1756-L85ES entirely from `_L8XS_PRODUCT_CODES`/`_L8XS_CATALOGS` in
`gen_fw_catalog_matrix.py` -- same treatment as 1756-L9x (see
OPEN_QUESTIONS.md OQ-BASELINE-PROCFW): sourced but deliberately not
generated until a real sample or its real ProductCode surfaces. The
6 already-generated L85ES files (one per firmware version) and their
manifest.csv rows were deleted, not left orphaned. Full corpus
re-swept (1841 files): 0 crashes. 140/140 tests.

**OQ-AOIORPHAN.** Real confidential-customer-project grep (2026-08-30,
not committed, never named) found 12 of 39 declared AOI definitions with
zero real tag anywhere (even transitively) instantiating them.
`report.py`'s definition-cost pass only counts a UDT/AOI reachable from
an actually-sized tag (`referenced_udts`), so an orphaned AOI predicted
$0 extra with no error raised — but whether Logix Designer's compiler
actually reserves memory for a never-instantiated AOI definition, or
drops it entirely, was not derivable from the L5X alone. A minimal pair
(`aoi_orphaned_referenced`/`aoi_orphaned_unreferenced`, byte-identical
except one has a live instance+call of a moderate utility AOI and the
other declares the same AOI but never instantiates it) was captured
2026-08-31. `aoi_orphaned_unreferenced`: predicted 19472, real 19480 --
an 8-byte residual (0.04%), essentially exact. `aoi_orphaned_referenced`:
predicted 19676, real 19936 -- a 260-byte residual (1.3%, consistent with
the same small systematic underprediction seen across the composite
batch, not orphan-specific). Real delta between the two (referenced
minus unreferenced) = 456 bytes; this engine's own predicted delta is
204 bytes -- the gap is fully explained by that same ~250-byte residual
on the referenced side, not by the orphan/unreferenced side being wrong.
**Conclusion: `report.py`'s existing rule (a UDT/AOI definition
unreachable from any actually-sized tag predicts $0 extra) is confirmed
correct by real data, not just assumed** -- Logix genuinely does not
reserve real memory for an AOI definition that's declared but never
instantiated anywhere. 18 of the 50-file `gen_composite_realistic.py`
extension (each declares its own orphaned AOI at varying complexity) are
now captured too, all landing within the same small ~3% band, no
orphan-specific outlier among them -- corroborating, not just the
minimal pair. The core question (does an orphaned AOI definition cost
real memory) is closed. Still open, tracked separately under
OQ-COMPOSITESCALE: capturing the remaining composite files (8 blocked on
an unrelated CIP-Safety-catalog import bug, the rest not yet run).

## OQ-ALARMCOND — tag-based alarm conditions (SOLVED EXACTLY, 2026-09-05)

2026-09-04: the alarms prefixed `Alarm1_` were suspected of holding back
the calculations, and they were. They were the
single largest unpriced item in the model — 3,463 across the real corpus,
200-600 in every real program, all costing exactly zero.

Solved from the 37-file `alarmcond_*` batch with **zero residual on every
captured point**:

```
total = 800  (once per file, if any alarm exists)
      + 500  per alarm condition
      + per associated tag, by the resolved type of what it points AT:
            BOOL 88 | DINT 92 | REAL 92 | STRING 256
```

Confirmed **free**, all byte-identical to the 32-alarm control: HMIGroup
(absent / 4 / 16 chars), alarm Name length (8/16/32/40), Severity, OnDelay,
Latched, AckRequired. **Alarm cost depends only on how many alarms there
are and what their associated tags point at.**

Impact: `alarm_condition` category 37/37 within ±1% (0.03% mean), and
pricing it forced the composite AOI/JSR surcharge to be re-examined — which
led directly to both rates being disproved and set to 0 (OQ-SHELLSCALE).

Two things this batch got right that are worth repeating: the four
placeholder arrays were byte-identical in every file, so the *"mute
them in your calculations"* was handled by the experiment design rather
than a subtraction; and assoc-tag count was varied independently of alarm
count, which no real file can do (every real alarm has exactly 3).

## OQ-STSIZING — Structured Text (SOLVED, 2026-09-05)

**An instruction inside ST costs exactly what the same instruction costs in
a rung.** Against the matching `instr_*_n01000` captures, ST is a flat
**+432** (the ST routine shell) and nothing else — COP, DTOS, SIZE, `:=`
against MOV, and a full arithmetic `:=` against CPT, all five at +432. The
entire per-instruction weight table transfers to ST unchanged, and an ST
arithmetic assignment is priced by the existing CPT expression model.

Per plain assignment statement: **40 bytes**, exact at 25/100/400/1000.
Control flow, per construct: IF 48, ELSIF 40, CASE branch 57, **FOR 248**,
WHILE 72 — a loop-heavy ST routine is not priced like a branch-heavy one.

**ST comments are FREE**, answering the question directly: 100 short
leading, 100 long (110-char) leading, 400 leading and 100 trailing comments
all read byte-identical to the control, as do 400 blank lines. Same as rung
comments — but this had to be measured, because a rung comment is a
separate `<Comment>` element while an ST comment sits inside the compiled
source text.

## Closed 2026-09-05 — moved out of OPEN_QUESTIONS.md

2026-09-05, on whether every closed question had actually been moved to the
closed list: they had not. Three items below had been marked solved
in `OPEN_QUESTIONS.md` -- two of them explicitly claiming "moved to
RESOLVED_QUESTIONS.md" -- while their full bodies stayed in the open file
and this archive had only a passing one-line mention of each. The claim was
wrong when written. Bodies moved here verbatim; the open file now carries a
one-line pointer instead.


### **OQ-ALARMCOND** — **SOLVED EXACTLY 2026-09-05, moved to
    RESOLVED_QUESTIONS.md.** Original entry kept below for the trail.
    Opened 2026-09-04, on controller alarms in real use -- specifically the
    ones prefixed `Alarm1_` -- as a suspected source of inaccuracy. They
    were, measurably.

    **3,463 real `AlarmCondition` elements across `samples/local/`, every
    one priced at ZERO.** All 8 real programs fitted the same day carry
    200-600 each. After the composite surcharge was refitted, the leftover
    residual on those 8 correlates **+0.583 with alarm count** — the
    strongest remaining identified driver (AOI-internal instructions
    −0.236, JSR-target −0.094). This is the most likely single reason those
    files sit at 3.29% rather than <1%.

    They were missed because they are **children of the `<Tag>` element
    they alarm**, not of a top-level container, so a parser walking
    `Controller/Tags/Tag` and reading the Tag's own attributes never sees
    them. Now parsed (`parser/alarms.py`) and reported through the coverage
    channel; **no byte value is assigned**, because no capture exists.

    Real usage profile, measured across all 3,463 — one shape, essentially:
    | property | reality |
    |---|---|
    | host tag | BOOL[224] ×3,400, BOOL[256] ×55, UDT scalar ×8 |
    | associated tags | exactly **3** on 3,455; 0 on 8 |
    | AlarmConfig | HMIGroup on 3,455; empty on 8 |
    | ConditionType | TRIP on **all** 3,463 |
    | Severity / Expression / EvaluationPeriod | 500 / `= 1` / 500 ms on all |
    | OnDelay | 1000 on 3,449; 0 on 14 |
    | name length | 10-17, mean 13.9 |

    **Why real files alone can never fit this:** assoc-tag count never
    varies independently of alarm count in any real program on file (always
    exactly 3), so the two are perfectly collinear and no regression can
    separate cost-per-alarm from cost-per-associated-tag. That is exactly
    what the four `Alarm1_*` probes break apart, and what the generated
    42-file `alarmcond_*` batch extends: count ladder bare and at the real
    shape, assoc count 0-4, assoc type DINT/STRING/REAL/BOOL, HMIGroup
    length, alarm-name length, the four analog condition types (0% of real
    conditions are anything but TRIP on a BOOL), and the behavioural
    attributes. The four placeholder arrays are byte-identical in every
    file, so muting them is handled by the experiment design rather than by
    a subtraction. Blocked on capture.

    **Real build results, 2026-09-04 (the first conversion pass).**
    38 of the 42 built clean. The 4 failures are all mine, and two of them
    taught something:
    - `alarmcond_hmigroup_len64` — *"Failed to set the 'HMIGroup' property
      (Invalid Alarm group name.)"* at 55 characters. `len04` and `len16`
      both converted, and `len16` is `LineA_Station12` — **so underscores
      are legal and the constraint is a LENGTH limit somewhere between 16
      and 55.** Replaced by `alarmcond_hmigroup_len40`, probing the
      canonical 40-character Rockwell name limit directly. Real HMIGroup
      values run 5-9 characters (Edger, Stacker, LugLoader), so this axis is
      deliberately far past reality.
    - `alarmcond_type_trip_high` / `_trip_low` / `_deviation` — *"Invalid
      condition type."* **Those three names were invented.** 100% of the
      3,463 real corpus conditions are `ConditionType="TRIP"`, so this
      project has zero evidence for what any other condition type is
      called. Group removed rather than re-guessed — the same mistake the
      ST batch had to be rebuilt for.
    - `alarmcond_type_trip` — a valid TRIP, but on a REAL[128] host:
      *"Condition expression is not compatible with condition type or the
      data type of the input."* Every real condition is TRIP on a BOOL, so
      the expression form an analog input needs is unknown.

    **NEEDED FROM JAMES, and the analog half of this question is blocked on
    it:** the real `ConditionType` list from the Studio 5000 dropdown, plus
    one working analog example (an alarm on a REAL tag with whatever
    Expression it actually requires). With those, the analog group can be
    rebuilt from evidence instead of guesswork. Everything else in the batch
    stands.

---

[^instrfirstpass]: CROUT (safety-only) and MAPC resolved separately
(RESOLVED_QUESTIONS.md). SCP (no 2nd real example), FBC (0 real
examples), PID (0 real examples, needs its own structure tag) —
deprioritized 2026-08-25 as a safety-related feature, then
**explicitly closed as out-of-scope 2026-08-30** rather than left open awaiting data that was never coming.
Small residual noted for the record, not blocking closure: a flat
**+12** byte gap (corrected from a misrecorded +6) across all 64 clean
`instrfirst_*` files (~0.06% of file total), narrowed to an interaction
effect among the 7 distinct tag types the shared pool declares but not
isolated to which one.

[^baseline]: `empty_project_baseline=13,296` only confirmed for
1756-L81E/fw 35.05 — real variance found so far: firmware 30→33 adds a
real, distinct step (29,272 → 32,376 at fw33); 1769-series runs
69,600-98,944, far above the flat prediction; 5069-L306ER family sits at
18,144 base. An "M motion processor costs more" hypothesis was tested and
answered NO (2 identical base-vs-M pairs). The 8 files previously flagged
"contaminated" (named `SafetyTask`/`SafetyProgram` but carrying no real
safety marker — no `Class="Safety"`, empty `<SafetyInfo/>`) are now
corrected and included: subtracting the known task/program/routine shell
overhead (1,456) gives a clean baseline of 18,112 for 4 of them (exact
match to the already-confirmed reference point) and 18,120-18,144 for the
other 4 (small real per-model variance, not error) — see `manifest.csv`
notes on `v35_l82e/l83e/l84e/l85e/l3100erm/l320er/l330er/l340er`. 20 files
remain awaiting capture.

**Full catalog x firmware matrix built 2026-08-25, expanded same day**
(`gen_fw_catalog_matrix.py`, 232 files, `fw_catalog_matrix` category).
Every real catalog number sourced from Rockwell literature/distributor
documentation via web search (not guessed), cross-checked against this
project's own already-confirmed ProductCodes before generating anything:
29 catalogs × 8 firmware versions (31-38, v30 excluded — SDK confirmed
unable to build it at all):
- 5× ControlLogix 5580 (1756-L8x), 14× CompactLogix 5380 (5069-Lxxx) —
  original 152-file batch.
- 5× ControlLogix 5570 (1756-L7x, L71/L72/L75 real ProductCode 92/93/96,
  L73/L74 INFERRED 94/95 from the sequential pattern — flagged per-file).
- 5× GuardLogix 5580 safety-rated (1756-L8xES — real ProductCodes
  CORRECTED 2026-08-30, see below: L81ES=211, L84ES=214 both real,
  L82ES/L83ES/L85ES=212/213/215 INFERRED from that 2-point sequential
  pattern — flagged per-file). Each gets a real `SafetyTask`/`SafetyProgram` pair
  with `Class="Safety"` on both elements (the real marker, confirmed
  against Gormley/Bender corpus — NOT the element name) plus a populated
  `<SafetyInfo SafetyLevel="SIL2/PLd" .../>`.

Firmware attribute shape (SoftwareRevision, AutoDiagsEnabled/
WebServerEnabled presence, v38's DataExchangeId) is real per version,
confirmed from the existing v31-35/v38 samples. **v36/v37 removed
entirely 2026-08-28** (not asked for, deliberately left out) — they
were the only two ASSUMED/unconfirmed firmware majors in the table (no
real v36/v37 L5X sample ever existed in this project); the batch is now
174 files (6 firmware x 29 catalogs), all on real-confirmed firmware
attribute shapes. Files sorted `fwmatrix_v{NN}_{catalog}` so a plain
directory listing groups all of v31 together, then v32, etc.

**Real, systemic structural bug found and fixed 2026-08-28.** The
controller firmware tests had a very high failure rate, and a fresh real
Studio 5000 export of 1756-L71 was supplied for direct comparison; the exact same
evidence was ALSO already sitting unused in `samples/local/
L7_v21_Sample.L5X`, meaning this generator was built without ever
cross-checking against corpus evidence that was already available).
ControlLogix 5570 (1756-L7x) has NO embedded Ethernet interface on the
CPU module itself — real shape is exactly ONE Local Port (`Type="ICP"`,
`Bus Size="4"`, not the L8x-style 17) and no top-level `<EthernetPorts>`
element at all. This generator applied the L8x shape (second Ethernet
Port + EthernetPorts element describing a port that doesn't physically
exist) to all 5 L7x catalogs across every firmware version — a real
structural error, not a cosmetic one, plausible root cause for a large
share of the reported high failure rate. Fixed: `_local_ports_xml` now
branches for `_L7X_PRODUCT_CODES`, and the top-level `<EthernetPorts>`
is conditionally omitted for that family. Only L71 is directly
corpus-confirmed; L72-L75 are the same ControlLogix 5570 physical form
factor so treated identically, not independently confirmed per-catalog.
Also added two real Controller/RedundancyInfo attributes confirmed by
both real references (`TimeSlice="20" ShareUnusedTimeSlice="1"`,
`IOMemoryPadPercentage="90" DataTablePadPercentage="50"`) — `build_l5x`'s
own already-working template omits both and still imports fine across
~1300 tested files, so these are almost certainly Studio-5000-optional
rather than the actual failure cause, but added for fidelity now that
real values exist. All 174 files regenerated — awaiting real
re-conversion to confirm the L7x fix actually resolves the failure rate,
not just structurally plausible like the module fixes made earlier the same day.

**Sourced but deliberately NOT generated, real ProductCode still
unconfirmed:** ControlLogix 5590 (1756-L9x, "TS" suffix — L902TS/L905TS/
L908TS/L915TS/L925TS/L950TS/L980TS) — a brand-new family (FactoryTalk
Design Studio only added support in v2.03, Nov 2025) with zero real L5X
corpus examples anywhere, and zero real ProductCode/Module-signature data
found anywhere publicly accessible despite thorough web search (Rockwell's
own domains are all blocked by this environment's egress proxy; even
distributor/3rd-party sites carry catalog numbers but never the internal
ProductCode). One L9 sample at v38 minimum was requested — still blocked,
needing either a real sample or explicit sign-off on a flagged best-effort
placeholder. CompactLogix 5480 (5069-L4xx process
controllers — L430ERMW/L450ERMW/L4100ERMW/L4200ERMW) — also zero real
corpus examples, not yet requested. Building either without a
real sample risks fabricating a ProductCode/Module shape that fails
Studio 5000 import outright.

**1769-series real per-catalog baseline + v30 wired 2026-08-29** (found
during a full manifest.csv audit —
these 9 real points had been sitting in the `fw_baseline` category,
MANUAL ENTRY, since before this project even had a `firmware_baseline_
delta` mechanism to wire them into, and were never revisited). 8 real
1769-series (CompactLogix 5370) blank-baseline captures, all v35.05 —
real total baseline runs 69,600-98,944 against a flat 18,112 predicted
for everything else, previously documented as "not modeled at all."
Wired as `catalog_baseline_delta` (memory_model.yaml), keyed by the
EXACT `ProcessorType` string (not prefix/suffix-matched like
`safety_capable_baseline_delta`) — real data shows a single expansion-
module suffix character changes the value by 13,000+ bytes
(`1769-L24ER-QB1B`=67,160 vs `1769-L24ER-QBFC1B`=80,832), so any
catalog beyond the 9 exact strings now confirmed correctly stays
unmodeled. Firmware-independence assumed (same convention as
`firmware_baseline_delta`) but genuinely unconfirmed — zero 1769 data
exists at any firmware besides v35. Separately, `l81_v30` (real MANUAL
ENTRY point, read from Capacity directly off a real v30 controller —
this project's SDK can't build/convert v30 exports at all) added to
`firmware_baseline_delta` at +11,160, ASSUMED confidence (single point).
All 29 real `fw_baseline`-category rows now checked: 17 exact, 6 within
the small per-file noise band (<=16 bytes), 3 already-documented small
per-model variance (+32 bytes, `l306er`/`l306erm`/`l320er`), and 3
already-documented Safety-Task-bearing-file gap (`l306erms2`/`erms3`/
`ers2`, -1,424 — real Safety Task/Program content this tool doesn't
size, see this same footnote's `v35_l306erms2`/`v35_l306erms3` note
further below for the root cause).

[^cmpcpt]: T1T3/T2T3 wired 2026-08-25: real capture data existed
unreconciled since 2026-08-24; `pow_tier_mix_base=160,
pow_tier_mix_per_operator=64` is exact at 4 of 5 points, and T1T3/T2T3
give IDENTICAL real bytes at every point (T1-vs-T2 stops mattering once
POW is present). See `sizing/constants.py` `CptExpressionModel.cost_for`.
**All-3-tier mixes: CLOSED 2026-08-29.** The 3
`cptmix_threetier_rem2_n06/n09/n12` files (plus the 4 disentangle files
below) had real capture data from 2026-08-27 sitting unreconciled in
manifest.csv this whole time — found and fixed the same day it was raised
was raised of why this wasn't closed already. The earlier `44*T1-116*T2+76*T3+72`
attempt was wrong (not just "misses n=15" — checked directly, it doesn't
reproduce the n=3/5/8/10/11 points it was supposedly fit from either).
Correct formula, confirmed 0 residual across ALL 9 real all-3-tier points
on file (operator counts 4-14): `base_by_remainder[operator_count % 3] +
4 * pow_operand_count`, `base_by_remainder = {0: 72, 1: 116, 2: 144}`.
remainder=1 exact at 3/3 points, remainder=2 exact at 4/4 points
(including the original n=15 outlier AND the 3 new rem2 probe files —
confirms the remainder-2 trigger hypothesis exactly, and that it's NOT a
flat bonus, it scales at +4/POW-operand same as the other two remainder
classes). remainder=0 rests on a single point (n=10) — same slope,
extrapolated base, one point short of independent confirmation. Wired in
`sizing/constants.py` `CptExpressionModel.cost_for` / `memory_model.yaml`
cpt_expression.

**REAL-operand/float-literal interaction: investigated 2026-08-29, still
open — now for a more specific and more interesting reason than "not
enough points."** The 4 disentangle files' real data (also from
2026-08-27, also unreconciled) rules out any simple per-operand-count
model: extra cost at R=1 REAL operand (276) is HIGHER than at R=2 (236),
and the same pattern holds for float literals (F=1: 280, F=2: 244) — going
from 1 to 2 of the same factor makes the file SMALLER, not bigger. That's
not sub-linear/saturating, it's genuinely non-monotonic, and it holds
identically for both factors, which rules out coincidence/noise. No
formula wired — CLAUDE.md's ground-truth discipline means not force-
fitting a linear or bilinear surface onto data that demonstrably isn't
one. Real hypothesis worth testing next: cost may track the number of
DINT→REAL type-PROMOTION points in the expression tree (a structural
property of where mixed-type sub-expressions meet), not the raw REAL-
operand/float-literal COUNT — needs files that vary operand/literal
POSITION at a fixed count, not just count alone. Additive fallback (no
surcharge) stays the honest default. Full data: 9 total points across the
`cptmix_stacked_*` (5, already on file 2026-08-24) and `cptmix_
disentangle_*` (4, captured 2026-08-27) sample sets.

**Position-probe files built 2026-08-29** (`gen_cpt_mixed_operators.py`
`group_real_float_position_probe`, built after this thread had dragged on
too long -- the hypothesis above had sat undertested since it was
written). 4 new files, all built/lint-clean/
zero engine errors, awaiting real capture: `cptmix_real1_pos_first`/
`cptmix_real1_pos_last` (1 REAL operand at slot 1 vs slot 6 of the same
6-operand T1+T2 shape, "middle" position already on file as
`cptmix_disentangle_real1_noliteral`) and `cptmix_float1_pos_first`/
`cptmix_float1_pos_divisor` (1 float literal at slot 1 vs the divisor
slot, "last" position already on file as `cptmix_disentangle_
float1_noreal`). Once captured: if all 3 positions per factor land on the
same real delta, position is ruled out (points back to an unexplained
pure-count effect); if they differ, the pattern across first/middle/last
tells us whether edge positions (fewer operator-adjacency "boundaries")
cost less, which would directly support the type-promotion-point
hypothesis.

**2026-08-30: four CPT tests were not enough.** The 4 position-probe files above hold REAL-operand/
float-literal COUNT fixed at 1 and only vary where that single factor
sits — they can't touch the actual anomaly this whole thread exists to
explain (2 REAL operands costing LESS than 1, non-monotonic in count).
Added `group_real_pair_adjacency_probe`: `cptmix_real2_adjacent` (2 REAL
operands at slots 1-2, adjacent) vs `cptmix_real2_spread` (2 REAL operands
at slots 1 and 6, same count, spread to opposite ends of the same 6-slot
shape) — directly tests whether adjacency (fewer DINT↔REAL promotion-point
crossings) is what drives the count anomaly, or whether the two layouts
measure the same (which would falsify the promotion-point hypothesis
itself, not just leave it uncalibrated). Built, lint-clean, zero engine
errors, awaiting capture — 6 CPT probe files on file total now, not 4.

**2026-08-30: were there enough tests to fully close this?** No, still not
guaranteed. The adjacent/spread pair only
disambiguates 1-vs-2 REAL operands; it says nothing about whether the
non-monotonic dip continues, reverses, or was specific to exactly 2.
Added `cptmix_real3_adjacent` (3 REAL operands, slots 1-3, same shape) to
extend the count sequence 1→2→3. Even with this, two things stay
untested and are flagged honestly rather than silently assumed closed:
whether REAL-count and float-literal effects compose when both are
present at varying counts/positions together, and whether a different
expression tree shape (not just this flat 6-slot layout) changes the
answer.

**2026-08-30: more tests rather than guessing.** Both remaining gaps now have dedicated files instead of
being left untested:
- **REAL-count x float-literal composition**: `cptmix_real1_float1`,
  `real2_adjacent_float1`, `real3_adjacent_float1` -- same shapes as
  real1_pos_first/real2_adjacent/real3_adjacent with the trailing slot
  replaced by the float literal 1.5, so the marginal float-literal cost
  can be read directly by subtraction at each REAL count (constant
  across n = additive/no interaction; varies = real interaction).
- **Alternate expression tree shape**: `cptmix_real1_nested`,
  `real2_nested` -- same operand/operator multiset as
  real1_pos_first/real2_adjacent but deeply right-nested instead of a
  flat left-to-right chain, REAL operand(s) at the innermost position.
  Tests whether the type-promotion-point hypothesis holds once tree
  structure (not just flat token position) changes.

12 CPT probe files on file now, covering count (1/2/3), position
(first/last/divisor), adjacency (adjacent/spread), float composition, and
tree shape. This is the full hypothesis space as currently understood --
not claiming it's exhaustive of every possible expression shape, but
every specific mechanism proposed so far now has a real test.

**Cross-validated at scale, 2026-08-29** (full manifest.csv audit):
`randommix_07_n19811rungs_24types` (`logic_random_mix` category, real
capture) was off by +39,959 -- traced to its 208 real CPT calls, which
all use `gen_logic_sweep.py`'s exact `(D+D)*R-R/2+1.5` shape (2 REAL
operands, 1 float literal) -- the SAME `original_shape` this thread
already covers. 208 x the already-known ~200/call gives ~41,600, close
to the real 39,959 (the small gap is plausibly the rotating tag pool's
per-call operand variety, not a new effect). Confirms this is the same
open thread recurring at volume, not a separate bug -- no new formula
needed or wired, consistent with the additive-fallback default already
in place.

[^aoidef]: Per-type declared-item rate table (BOOL=16, SINT/INT=18,
DINT/REAL=20, LINT=24/item, base=1184) wired for single-type defs;
mixed-type defs use the flat rate (confirmed non-additive once BOOL sits
next to another type). Live-verified against 85 captured AOI rows: 32
exact, 52 within 1%, 1 at 2.10%. Full derivation: `docs/AOI_KNOWLEDGE_MAP.md`.
Required/Visible/Hidden flag combinations: CLOSED 2026-08-25 — real
2026-08-23 capture data was sitting unreconciled, deltas land within a
32-block band with no direction tied to flag config (noise, not a real
effect).

**Name-length CLOSED 2026-08-30**: `aoiname_len08/09/13/16/20/25/30_def_only`
(7 real points, all sitting unreconciled) confirmed exact against
`8*max(0,(len-8)//4) - 8` — wired into `AoiDefinitionModel.name_length_bytes`.
A real off-by-one bug was found and fixed along the way: the first version
wired (divisor `(len-7)//4`, chosen because it also reproduces all 7 of the
same points) put len=19 one bucket too high. Caught by cross-checking two
real AOI-array-packing captures that only differ in AOI type name length —
`AoiPureBoolDense` (16 chars) and `AoiPureBoolBoundary` (19 chars), both 10
BOOL In/10 BOOL Out/10 BOOL Local, both array of 16 instances — which must
land on the identical total byte count if the shared shape is identical,
but disagreed by exactly 8 bytes under the old divisor. `(len-8)//4`
reproduces all 7 originally-tested lengths identically (none of them sit at
len%4==3, the only residue class where the two divisors disagree) and
resolves the cross-check to 0 bytes apart. AOI-instance-array element cost
split off as its own item, OQ-AOIBOOLPACK-PAIRING, below.

: The `aoi_array` model's "confirmed exact, 15 real
points" claim (mc=10/20/30/60, but only ever checked at n=1/10/25 per
shape) doesn't survive dense n. Reconciling 27 already-captured points that
were sitting unreconciled proved it: for a single-packed-word AOI
(bool_count<=32), real array bytes follow `8*ceil(n/2) + B` — an odd-length
array costs 4 bytes MORE than the even-length prediction the current
formula makes, a term the formula has no place for at all. B itself is
real and flat per shape but does NOT extrapolate cleanly across bool_count:
B=20 for 10-BOOL-all-Input (`aoipack_mc10_b10_array_n01/10/25`, 3/3 exact),
B=44 for 20-BOOL-all-Input (`aoipack_mc20_b20_array_n01/10/25`, 3/3 exact),
B=28 for the original 30-BOOL/3-way-split shape — 10 In+10 Out+10 Local —
(`aoipack_bool_array_n01/05/10/25/50` + `aoipack_bool_boundary_n16-96` +
`aoipack_bool_dense_array_n16-40`, 18/18 exact). Since B doesn't scale
linearly with bool_count across those three, and the only structural
difference between the 30-BOOL case and the 10/20-BOOL cases is the 3-way
section split (the current parser only tracks a flat total bool_count, not
per-section In/Out/Local counts), the section split itself may be what
actually drives B — untested directly until now.

The 60-BOOL case (2 packed words/instance, `aoipack_mc60_b60_array_n01/10/25`)
is worse: all 3 points show a flat +148-byte miss with **no** odd/even
signal at all against the old formula, but do not fit `8*ceil(n/2)+const`
either when checked directly — multi-word packing is a materially
different, still-open shape from the 3 points on file.

Confidence downgraded `aoi_array`: KNOWN → FITTED (`memory_model.yaml`,
2026-08-30) — the formula is left un-replaced rather than guessing a
generalized fix from underdetermined data (this project already ate one
overfit formula in that batch, the CPT three-tier bug — not repeating it).
New dense/isolating test files generated instead, not yet captured:
`gen_aoi_boolpack_pairing.py` → `aoibp_dense_bc{10,20,60}_n{02,03,04,06,08,12}`
(18 files, dense n right where the pairing period would show, including
the FIRST dense points at all for bool_count=60) and
`aoibp_split_allinput30_n{01,05,10,16,25}` (5 files, same bool_count=30 as
the already-solved 3-way-split shape but all-Input/single-section, at the
same n values, to directly test the section-split hypothesis). 23 files
total — not padded to the 60-file floor, which is not a quota.

**Wider dataset surfaced 2026-08-30** during a full-depth open-questions
review — a full manifest.csv reconciliation sweep against the live engine,
not just the mc10/20/60 family already covered above. **Correction to an
initial write-up of this same finding**, surfaced by checking whether new
tests existed for all of those points: this is NOT the
3-way-split shape (10 In + 10 Out + 10 Local) the original `aoipack_bool_*`
finding used. `aoipack_ratio_01b29a` through `_29b01a`
(`gen_batch3_followups.py` `group_b_ratio_sweep`, 6 BOOL:DINT ratios x
n=1/10/25/50, 24 real points) is SINGLE-SECTION (all-Input, mixing BOOL
and DINT in one Parameters list) — structurally the SAME family as
mc10/mc20 above, just with a fixed 30-member total and a MIXED (not pure)
type composition. It shows a real, different residual shape from mc10/
mc20 anyway: FLAT per ratio, **no** odd/even n-parity signal at all
(01b29a=+52 at every n, 05b25a=+36 at every n, 10b20a=+12 to +16,
20b10a=-24 to -28, 25b05a=-44 at every n, 29b01a=-60 at every n, all flat
within measurement) — where mc10/mc20 (single-section, PURE BOOL, no DINT
at all) show real odd/even pairing. A separate non-atomic-type variant
(`aoipack_nonatomic_real/sint_10b20a/20b10a`, 8 real points, REAL/SINT
non-BOOL operands instead of DINT) shows smaller, still-flat-ish deltas
(-66 to +8). Neither dataset was previously reconciled against the live
engine.

This reframes the open question precisely: within the SAME single-section
structural family, a PURE-BOOL declared-member list (mc10/mc20) shows real
2-instance pairing quantization, but a MIXED BOOL+non-BOOL list (the ratio
family, same family, same section shape) does not — suggesting the
pairing mechanism may specifically depend on whether every declared
member is BOOL, not just on section layout. Untested directly until the
`aoibp_puremix_*` isolation batch below.

[^safetyscope]: `DCI_STOP` (35 errors) has real decorated evidence
(SJ_Gormley_20251112_r02.L5X, 80 bytes/20 DINT) but is deliberately NOT
wired -- every real instance found carries `Class="Safety"` on the Tag
itself, and this project's Safety content is currently NOT sized by
design (the UI's red warning banner) even though nothing in the code
actually enforces that exclusion per-tag today -- it just happens that
Safety AOI types are mostly unresolvable native structures. Wiring
DCI_STOP would make Safety-scoped totals partially counted for the first
time, which needs a deliberate decision — exclude Safety-class tags by
design everywhere, or size everything resolvable including Safety and
adjust the warning wording — before it is silently changed.

`CONFIGURABLE_ROUT` -- CORRECTED 2026-08-29, an earlier pass had this
wrong: it DOES have real capture data and IS wired (52 bytes, see
RESOLVED_QUESTIONS.md OQ-PREDEFINED) -- not read in RM018A, but that's
moot now that a real Capacity-based value exists directly. Falls under
the same Safety-scope decision as DCI_STOP (name root matches `CROUT`,
the confirmed Safety-only instruction).

**AOI array "anomaly" investigated 2026-08-29, was contaminated data, not
a real formula problem.** Of the 5 AOI array files re-captured after the
real Dimension/Dimensions bug fix, 4 show a modest positive delta (+400/
+404/+60/+64, plausibly a small remaining formula gap, still genuinely
open) but `aoi_array_param_def_only`'s row was flagged
`WINDOW TITLE MISMATCH` in manifest.csv (window title read back
"ProbeDciStop" -- a completely different file from the predefined-
structure probe batch, not this one) -- the "-1,044 byte overshoot" a
previous pass reported was that mismatched file's real bytes, not this
one's. Per CLAUDE.md's standing rule that row's capture columns are
cleared, not trusted; `aoi_array_param_def_only` is back to needing a
real, clean capture (still in the same NEEDS-RE-CAPTURE bucket the
Dimension/Dimensions bug fix already put it in -- see
[^aoiarraydimension] below, this was never actually re-captured cleanly).
No engine change made or needed here -- AOI array PARAMETER sizing is
UNTESTED, not confirmed broken.

[^aoiarraydimension]: 2026-08-27, a check on whether bit-mapped BOOLs from
hidden SINTs were being handled prompted a broader audit of AOI-local
sizing, which surfaced a real, separate bug (verified via
`compute_udt_size`, `is_bit_alias`/`hidden` in parser/datatypes.py: the
BOOL-hidden-SINT question ITSELF was already correct and directly unit-
tested — `test_udt_mixed_bool_dint_string_with_bit_packing` — 1 byte for
the backing SINT regardless of how many BOOL aliases point into it, 0
extra for each alias, confirmed exact). The real bug found instead:
`parser/aoi.py`'s `_member_from_element` read a `<Parameter>`/`<LocalTag>`
element's array size off a "Dimension" (singular) attribute — correct for
a plain UDT `<Member>` (parser/datatypes.py, unaffected), but real
`<Parameter>`/`<LocalTag>` elements carry it on "Dimensions" (PLURAL) —
confirmed against 80 real `<Parameter Dimensions="N">` and 191 real
`<LocalTag Dimensions="N">` elements across all 64 corpus files, zero
counter-examples for the singular form anywhere. Every array-dimensioned
AOI Parameter/LocalTag was silently sized as a scalar. Real customer-file
impact: 35 tag-sizing errors closed immediately (all CAM_PROFILE, which
was already correctly wired in `predefined_array_structures` but never
reachable through this bug).

Fixed in `parser/aoi.py`. `sample_gen/builders.py` had the IDENTICAL bug
(`Dimension=` instead of `Dimensions=`) generating AOI Parameter/LocalTag
XML — the two bugs self-consistently masked each other for this project's
own synthetic test files (both sides wrong the same way), which is why no
existing test caught it. Fixed there too. 5 existing files (
`aoi_array_localtag_def_only`/`_1_instance`, `aoi_array_param_def_only`,
`aoi_nested_array_localtag_def_only`/`_1_instance`) regenerated with the
corrected attribute — flagged `NEEDS RE-CAPTURE` in manifest.csv, old
actual_bytes/delta cleared rather than trusted. Reasoning: the prior
2026-08-22 capture of these files almost certainly measured SCALAR
behavior, not array behavior — Studio 5000 very likely didn't recognize
the malformed singular attribute either (real syntax requires plural) and
silently coerced it to scalar on import, same as this project's own
buggy parser did. The math backs this out precisely for
`aoi_array_localtag_1_instance`: fixed-engine prediction is 19,832 bytes,
old real capture was 19,424 — a 408-byte gap, matching almost exactly
what a 100-element DINT array minus a scalar DINT should cost (396) plus
the small universal per-file noise (~8-12) seen everywhere else in this
project. Needs a fresh real capture of the corrected files before this
project can claim the AOI-array-local/param formula is confirmed at all
— it currently rests entirely on the already-validated general
array-of-atomic/array-of-UDT member cost formula being assumed to apply
unchanged to an AOI's own Parameter/LocalTag members too, which was never
actually tested end-to-end against a real capture.

**Real import-failure bug found and fixed, 2026-08-29.**
`aoi_array_param_def_only` itself
wouldn't import into Studio 5000 at all -- a real, separate bug from the
Dimension/Dimensions one above, not just a bad capture read. Root cause:
`sample_gen/builders.py` `_aoi_parameter_xml` used the generic
`Required="false" Visible="false"` default for the array Input Parameter
(`InputBuffer`, `Dimensions="50"`). Zero real corpus evidence supports
false/false on an array Parameter of any Usage -- the only two real
array-Parameter examples this project has (`LOG_HMIDisplay
Dimensions="25"`, `BitArray Dimensions="1024"`, both from real customer
files) are both `Usage="InOut"` and both `Required="true" Visible="true"`,
already-confirmed for InOut specifically but never independently tested
for Input/Output. Fixed by forcing `Required="true" Visible="true"` on
ANY dimensioned Input/Output Parameter, extending the one confirmed
real pattern (this is a hypothesis-driven fix given the available
evidence, not a positively-confirmed Input-array real example --
flagged here, not silently treated as certain). File regenerated,
lint-clean, zero engine errors; Required/Visible flag choice doesn't
affect the sizing formula itself (already confirmed no real effect,
see the Required/Visible closure note above), so predicted_bytes is
unchanged (19,332). Still needs a real capture -- was never actually
captured cleanly (first attempt hit the Dimension/Dimensions bug, second
attempt hit WINDOW TITLE MISMATCH, and the underlying file itself was
broken this whole time under both attempts).

**Correction, 2026-08-31: the 2026-08-29 Required/Visible fix did NOT
actually resolve the import failure.** the 2026-08-30 l5x2acd run
shows `aoi_array_param_def_only` still failing with the identical
`XMLSrv_E_IMPORT_ABORTED_NO_CHANGES` generic wrapper text, on the
regenerated (post-fix) file. The `Required="true" Visible="true"` change
was a hypothesis extended from the two real InOut-array examples in the
corpus, explicitly flagged above as "not positively confirmed for
Input/Output" — that hypothesis is now disproven, or at least insufficient
on its own; there's still a real, separate import blocker. Task list
previously (wrongly) marked this fixed — corrected here. Root cause
remains unknown; the wrapper text carries no per-file detail, so guessing
further isn't productive. Added to `samples/known_conversion_failures.csv`.
Needs the real Studio 5000 error-log line to make any further progress on
this file.

[^moduleio]: `module_overhead = 1,672 bytes/module` (flat, mean of 2 real
deltas), wired as ESTIMATED tier. 141 files in `samples/generated/modules/`:
per-catalog sweep (119/119 real corpus catalogs), rack-level tests, a full
Kinetix 2-bus/8-axis subgraph, and a full-fidelity replica of a real
Bender program (69 modules incl. GuardLogix Safety Partner). GuardLogix
SIL2/SIL3 handling is a reusable `build_l5x(..., safety_level=...)`
capability. Real Studio 5000 conversion errors from the 2026-08-24/25
batch all root-caused and fixed: module-level `SafetyEnabled="true"` vs a
non-safety controller; 5069 modules needing `Port Type="5069"`; User-
Defined-Catalog devices needing their real `ExtendedProperties/
UdcAopVersion` schema (150 SMC Flex-E, PowerFlex 525-EENET — PF755
confirmed NOT affected); duplicate Ethernet IPs/AxisIDs; a slot collision;
`ParentModPortId` mismatches. Rack slot-address gaps ("a module in slot
10" concern) audited and confirmed NOT a bug — module size reads
exclusively from `ArrayMember/@Dimensions`, never slot number.
Deliberately not charged `module_overhead`: rack-aliased modules,
`CatalogNumber="Embedded"` I/O. Produced/consumed tags: RESOLVED, see
RESOLVED_QUESTIONS.md OQ-PRODCONS. PowerFlex 525 has multiple real I/O
payload UDTs beyond the one profile covered — needs more real corpus
examples, not guessed.

**Real per-catalog overhead table wired 2026-08-29.** The 141-file batch
above had real capture data landing since 2026-08-22 — 126 rows total, of
which 90 were never checked against the live engine and stayed on the
flat 1,672 estimate. Found the same way OQ-CMPCPTLAYOUT was: re-running
every module-category manifest row through the current engine and
diffing against real actual_bytes. Derived `module_overhead_by_catalog`
(memory_model.yaml, `constants.py` `ModuleOverheadModel`) via the same
subtraction methodology as `predefined_structures`:
`real_catalog_overhead = 1,672 + (actual_bytes - engine_predicted)`, ONLY
for real captures where the file's entire module list is exactly
`[Local, one real module]` — strict on purpose, since several
adapter/bridge catalogs (e.g. `1734-AENTR/C`) turned out to be absorbing
a whole rack of aliased child I/O modules into their own single entry,
which would have corrupted a looser per-catalog derivation with
configuration-dependent numbers. 51 catalogs got a clean, unambiguous
real value (real range: -793 to +10,497 — the flat 1,672 mean was a poor
proxy for this much real spread). Real exact-match rate against the 126
real module rows: 1/126 (before) -> 54/126 (after); full-manifest
regression checked (89 rows affected, 12 multi-module files got
marginally worse by 4-68 bytes each — all already inside the "not solved
this pass" bucket below, net effect strongly positive).

**6 catalogs show a real, unmodeled connection-variant effect** and were
deliberately left off the table rather than force-averaged:
`ETHERNET-MODULE`/`ETHERNET-PANELVIEW` (generic-catalog placeholders —
real overhead scales with declared I/O size, not flat at all),
`1734-AENTR/C` and `1756-EN2T` (real 1-conn vs 2-conn/rack-aliased
variance, up to +2,156 apart for the "same" catalog), PowerFlex
525/755-EENET (a smaller ~48-byte gap between two independent
file-generation methods, ambiguous which is representative).

**38 multi-module files reveal a real, distinct architecture gap: the
per-module marginal cost is NOT flat.** `module_1756_ib16_n01/n03/n10`
(1/3/10 identical 1756-IB16 modules in one file) show delta -4, -1,588,
-7,160 against "N x flat-per-catalog-overhead" — the SAME catalog's 2nd,
3rd, ... Nth instance costs LESS than the 1st, not the same. Rack files
(`modulerack_*`) and zero-connection modules (several `_variant_noconn`
files cost real nonzero bytes despite `module_defined_bytes=0` and
getting silently skipped by the current `continue`-on-0/0 check) show the
same class of gap. Needs its own marginal-vs-fixed decomposition, the
same shape task_program_overhead already got for Task/Program/Routine
counts — real architecture work, not a quick constant fix, so not rushed
into this pass.

**CORRECTION, 2026-08-28**, on a full review of the last batch of L5X
conversions (more than 50 files): the "1734-OB8S/A/B, 442G-MABLB ... CIP Safety
connections needing a safety controller even without that attribute"
claim above was WRONG/incomplete — the earlier fix (switching to a
safety-rated processor_type) was necessary but not sufficient. These
files, plus 5 more, still failed real conversion in the 226-row
2026-08-27 batch (`53e91d9`, `samples/convert_log.csv`) with a generic
`XMLSrv_E_IMPORT_ABORTED_NO_CHANGES ... See error log` that gave no
detail on its own. Real root cause found by diffing a passing vs. failing
pair that differ by exactly one real config axis (`modulesweep_2198_
d012_ers3_variant_2conn` PASS vs. `_variant_4conn` FAIL — same catalog,
2conn has Integrated Safety off, 4conn has it on): `wrapper.py`'s
`build_l5x(..., safety_level="SIL2")` branch assumed a single non-
redundant safety-capable primary (no CPU partner) needed no
`SafetyNetwork` attribute on its own Local module's ICP/Ethernet ports —
"no adjacent slot to reserve, since there's no partner. Only SafetyInfo
differs for SIL2." That conflated two separate real Rockwell concepts:
`Width="2"` reserves the adjacent slot for a redundant CPU partner
(correctly SIL3-only); `SafetyNetwork` establishes the safety NETWORK
SEGMENT identity that any downstream safety-enabled I/O module's own
`SafetyNetwork` attribute references, needed whenever a descendant module
has `SafetyEnabled="true"`, with or without a redundant partner. Every
one of the affected files had a downstream module correctly declaring
`SafetyNetwork`, referencing a network segment the project never
established — an orphaned reference. Confirmed against real corpus
(`SJ_Gormley_20251112_r02.L5X`): its Local module's ICP port carries
`SafetyNetwork="...cbbc"` and its Ethernet port carries `"...cbbd"`, the
exact value every downstream Kinetix ERS3 safety module in that file
references. The `is_5069` branch (checked BEFORE `safety_level`, so a
5069-family safety project like `5069-L306ERMS2` hosting
`5069-IB8S/A`/`5069-OBV8S/A` never reached the SIL2 logic at all) had the
identical bug via a separate code path — confirmed against a second real
corpus file (`samples/local/L306ERS2_Sample.L5X`, `5069-L306ERS2`): all
THREE Local ports (the local "5069" bus and both Ethernet ports) carry a
real `SafetyNetwork`. Both branches fixed 2026-08-28, regenerated (the
`_r2`-suffixed retest files, matching the existing suffix convention so
the re-test run doesn't collide with old files): 12 of the 17 real
failures now carry the fix (6× `2198-*-ERS3` 4conn variants,
`1734-OB8S/A`+`B`, `PowerFlex 527-STO`, `442G-MABLB`, `FANUC Robot`,
`5069-IB8S/A`, `5069-OBV8S/A`) — awaiting a real re-conversion to confirm
this actually resolves the import error, not just structurally plausible.
**The 4 remaining 5069 failures ALSO root-caused, 2026-08-28**, from the
real Studio 5000 error rather than the generic CSV wrapper:
`5069-IB16/A`, `5069-IY4/A`, `5069-OB16/A`, `5069-OB16/B` all real-error
`Failed to set the 'Size' property (Chassis size exceeds the allowable
size for a chassis.)` at `Modules/Module[@Name="Local"]/Ports/Port/Bus` —
a completely different, non-Safety cause from the 13 above, confirming
the earlier guess that these 4 needed a separate diagnosis. `wrapper.py`
used a flat `Bus Size="32"` for every 5069 catalog, sourced from only ONE
real corpus file (5069-L330ERMS2) and silently assumed universal — it's
actually a real per-model maximum local-I/O-slot count, not a constant.
An empty project (no local module attached) never trips this validation
regardless of the declared value (confirmed: `v35_l306er.L5X` passes 8/8
with the same wrong "32"), which is exactly why this stayed hidden until
a real local 5069 I/O module got attached — every one of these 4 failing
files attaches one. Real per-catalog values pulled from 6 separate real
corpus files (never guessed): `5069-L306ERS2`→9 (`L306ERS2_Sample.L5X`),
`5069-L310ERS2`→9 (`PWO_134190.L5X`), `5069-L320ERMS2`/`MS3`→17
(`Fisher_Synergy_Bead_20240725.L5X`, `FlareFunction_311D_240731.L5X`),
`5069-L330ERMS2`→32 (`BT1XX_FFC_20240325.L5X`), `5069-L340ERS2`→32
(`Fisher_P800Sub_20240531.L5X`). The failing files all use
`5069-L306ER` (real max 9, was getting 32) — fixed by keying Bus Size off
the base model number extracted from `processor_type` (the M/MS2/MS3/S2/
ER suffix doesn't change physical backplane capacity within the same
tier), regenerated the 4 `_r2` retest files plus re-verified the 2
already-safety-fixed 5069 files keep their correct value too. All 17 of
the original real failures now have a real, evidenced fix — awaiting
real re-conversion of all 17 affected `_r2` files to confirm.

**A second, separate real 5069 bug found 2026-08-28** on the
5069-LxxERMSx catalogs. `EtherNetIPMode="A1/A2:
Dual-IP"` is a real Controller-level attribute confirmed present, with
the identical value, in EVERY 5069 corpus file checked (6/6, zero
variance) — describes how the CPU's two embedded Ethernet ports are
addressed, something only a 5069 processor has (1756/1769 have at most
one embedded port). It was missing from both `wrapper.py`'s
`build_l5x` (the primary template used across ~1300 already-tested
files) and `gen_fw_catalog_matrix.py`, for every 5069 catalog, not
specifically the ERMSx (motion+safety) subset then under
test — confirmed by diffing a plain non-motion S2 catalog's real
export against a motion+safety ERMS2 one and finding the attribute
identical in both. Fixed in both generators (conditional on
`processor_type`/`catalog` starting with `"5069"`); regenerated all 90
affected files (`fw_catalog_matrix`'s 15 5069 catalogs x 6 firmware, plus
the module-sweep/variant/bender-full files that call `build_l5x`
directly). Whether this attribute is actually required for import or,
like `TimeSlice`/the `RedundancyInfo` pad percentages, Studio-5000-
optional is still unconfirmed — added regardless now that a real value
exists, same reasoning as those two.

**1769-family had the identical class of bug, found by generalizing**
(5069 and 1769 have different backplane sizes depending on the catalog
number ordered). Worse than 5069's case: there was no `is_1769`
branch in `wrapper.py` at all, so every 1769 processor silently fell
through to the generic ICP-chassis `else` branch — wrong Port TYPE
(`"ICP"`), not just a wrong Bus Size number. Real corpus evidence
(`samples/local/DnR_Personal/TOYOTA_135453_20221024.L5X`, `1769-L33ERMS`)
shows a real, distinct `Type="Compact"` (neither 1756's `"ICP"` nor
5069's `"5069"`), single Ethernet port (unlike 5069's dual-Ethernet).
Fixed 2026-08-28: added the missing branch with the correct Port Type
and SafetyNetwork handling (mirroring the SIL2 fix, though not
independently confirmed as required for 1769 the way it was for 5069/
1756 — the one real corpus file has a populated SafetyNetwork but no
downstream safety module to test the orphaned-reference failure mode
against). Only ONE real per-catalog Bus Size data point exists
(`L33ERMS` → 17) — every other 1769 catalog's real max is genuinely
UNCONFIRMED, kept as an explicit fallback rather than guessed model-by-
model the way the 5069 table could be. The 9 existing `fw_baseline`
1769 files predate the current generator scripts (moved in from
elsewhere per `git log`, not reproducible via `python -m`) and already
pass conversion regardless (same "empty project never trips the
validation" pattern already confirmed for 5069) — not regenerated, the
structural fix matters for any NEW 1769 generation going forward.

[^eventtrigger]: 2026-08-25: does an event task triggered by MAW cost more
than one triggered by the EVENT instruction? Real
corpus grep (12 real `Type="EVENT"` Tasks across SJ_Gormley_20251112_r02
and Sorter1_20260722r00) confirms exactly two real `EventTrigger` values:
"EVENT Instruction Only" (no EventTag) and "Axis Watch" (EventTag pointing
at a real `AXIS_CIP_DRIVE` tag — confirmed against Gormley's
`EM108_GradingLC`). "Axis Watch" is a Task-level config, not the MAW
*instruction* itself, but it's the real mechanism the "MAW" question
maps to — there's no other real EVENT-trigger shape in the corpus.
Genuinely untested axis: every existing task-overhead calibration file
(`taskoverhead_n0Xtasks`, the ones that produced task_extra=+700) used
only CONTINUOUS/PERIODIC tasks, never EVENT — so it's currently unknown
whether EVENT itself costs differently from PERIODIC, on top of the
trigger-source question. `eventtask_instronly` and `eventtask_axiswatch`
(`gen_event_task_trigger.py`) mirror `taskoverhead_n02tasks` exactly
(1 Continuous + 1 extra Task, 5069-L306ER/fw35.11, NOP-only programs),
changing only the extra Task's Type/trigger, so direct deltas isolate
both questions. `eventtask_axiswatch` also declares a real
`AXIS_CIP_DRIVE` tag (EventTag must reference a real tag) — that tag has
its own separately-modeled cost and will need subtracting from the raw
capture delta before comparing trigger sources.

**Import failure, 2026-08-30 — root-caused and fixed 2026-08-31.**
`eventtask_instronly` failed to import. The real error this
time: "Failed to set the 'Size' property (Chassis size exceeds the
allowable size for a chassis.)" on the Local module's own backplane Bus —
with NO axis tag involved, which disproves the earlier (2026-08-30)
dismissal of this exact error class as a downstream artifact of the
WatchedAxis tag bug (see that comment above); it's a real, independent
bug. Root cause: `processor_type="5069-L306ER"` (bare, no S2/M/MS2/MS3
suffix) was used ONLY in this one file in the entire project — every
other 5069 generator uses a specific suffixed variant — so
`_5069_BUS_SIZE_BY_MODEL`'s assumption that all L306 variants share Bus
Size=9 (confirmed only against the Safety+Motion `L306ERS2_Sample.L5X`)
was never actually tested against the bare model. Also found: this file's
docstring claimed it mirrors `taskoverhead_n02tasks`'s "5069-L306ER"
baseline, but `gen_task_overhead.py` never passes a `processor_type`
override either — that file is really 1756-L81E, so the comparison was
never actually apples-to-apples. Fixed by dropping the processor_type
override entirely (uses the wrapper default, 1756-L81E) — fixes the
untested/broken bus size AND the baseline mismatch in one real, evidenced
change. Removed from `known_conversion_failures.csv`. `eventtask_axiswatch`
got the same fix (same override removed) even though it wasn't in this
failure batch, since it shares the identical root cause. Needs a real
reconversion pass to confirm — not independently verifiable from here.

[^blockbyte]: `gen_blockbyte_l71.py` (the 1756-L71 half) plus the earlier
`blockbytetest_dint120000` (1756-L81E, `sample_gen.cli tags --type DINT
--dims 120000`). Deliberately the simplest possible content: one DINT[
120000] tag, no other tags, minimal empty-shell program/task/routine, so
the predicted total decomposes into pieces that are all independently
verifiable by hand — 480,000 (120,000×4, atomic array sizing has zero
packing ambiguity per this project's own established rule) + 13,296
(project_baseline) + 4,816 (per-routine fixed_base) + 16 (single NOP rung)
= 498,236. Both files predict exactly that number by construction (same
content, same firmware 35.05/35.11, only `ProcessorType`/`ProductCode`
differ: 1756-L81E/164 vs 1756-L71/92). If both real Capacity readings
come back ~498,236, "block" and "byte" are the same unit, just a
different UI word per processor generation — no corpus-wide fix needed.
If they diverge, the ratio between them (almost certainly a clean
divisor/multiple of the 480,000 array-content portion, since that's the
overwhelming majority of the total) is the real block size, and every
formula in `memory_model.yaml` derived from L81E/5069-family data needs
rescaling by it — which is most of this project's real corpus.

[^compositescale]: `gen_composite_realistic.py` — a deterministic
index-based feature schedule (`_profile_for_index`), not randomness, so
every one of the 50 files' exact composition is reproducible and
documented in its own manifest.csv description. UDT 0 in every file
nests UDT 1 as a member (real "mixed and garbled" nesting pattern,
matching `gen_axis_composite.py`'s established real corpus shape).
Referenced AOIs get a real instance tag + a call rung
(`AoiName(InstanceTag,0,...,OutBit);`); orphaned AOIs get neither, same
mechanism as `gen_aoi_orphaned_def.py`. I/O modules are cycled from
`gen_module_sweep.py`'s `_MODULE_CHAINS` (86 real, previously-extracted
catalog blocks, never fabricated) via `(index*7) % 86` plus an offset, so
the 50 files sample a wide, deterministic spread of the catalog list
rather than always picking the same easy ones. The 24 files that hit an
unmodeled module shape fall back to `write_sample_unmodeled` and are
flagged in their own manifest description — real, already-documented
engine limitations (rack-aliased connections, legacy-network bridges,
modules with unrecognized nested member types), not something this batch
introduced. Full corpus crash-swept clean (1801 files, 0 crashes) and
140/140 unit tests pass with this batch included. The v3 follow-on
generator (`gen_composite_realistic_v3.py`, see OQ-V3GENBUGS) reuses this
module-cycling and AOI/orphan machinery unchanged and adds deliberately
wide-varying program/subroutine/AOI counts (5-24 AOIs, 5-12 programs,
1-3 subs/program) plus a target-byte-count-by-construction technique: it
measures the real content "floor" via a direct `build_report()` call, then
sizes one filler DINT array via already-KNOWN formulas to land within a
few bytes of a per-file target between 1,550,000 and 2,449,999.

[^axiscombo]: Two different real-data-derived axis/motion
predefined-structure number sets exist and were never cross-checked
against each other. OQ-PREDEFINED (RESOLVED_QUESTIONS.md, derived
2026-08-23 via `residual = actual - sizeable_engine_total -
empty_project_baseline`, single-sample-each, FITTED) gives
AXIS_CIP_DRIVE=22,636, COORDINATE_SYSTEM=9,516, AXIS_SERVO=
AXIS_VIRTUAL=16,796 — these ARE the values currently wired into
`memory_model.yaml`'s `predefined_structures`, and the sizing engine does
NOT error on these 4 axis types today. A separate note, OQ-AXISSTRUCT
(RESOLVED_QUESTIONS.md, appears in the Tag/UDT section ahead of
OQ-PREDEFINED's section but reads as never reconciled against it),
records a second real set of Capacity totals — AXIS_CIP_DRIVE=22,728,
COORDINATE_SYSTEM=9,616, AXIS_SERVO=AXIS_VIRTUAL=16,888 — each
consistently 92-100 blocks HIGHER than the wired values — "measured over
a MotionGroup-only local baseline (19,296 blocks)." That 19,296 baseline
figure doesn't appear anywhere else in this project's docs and doesn't
cleanly decompose from what's already wired: `empty_project_baseline`
(13,296) + `MOTION_GROUP` (1,076) = 14,372, leaving an unexplained
~4,924-block gap. Without the actual source L5X/file composition behind
the OQ-AXISSTRUCT numbers, there's no way to tell from the two aggregate
totals alone whether this second set reflects (a) formula drift in some
shared cost since 2026-08-23, (b) a real MotionGroup-only baseline file
with more content than OQ-PREDEFINED's bare per-axis isolation files, or
(c) the still-open multi-axis "combo" case rather than the
single-axis-in-isolation case OQ-PREDEFINED already solved. Genuinely
blocked on that source data (or a fresh, clearly-labeled real capture) —
not guessable from two aggregate totals, and not acted on (no formula
change made) pending it.


### **OQ-SHELLSCALE** — **ANSWERED 2026-09-04, and the answer reverses this
    question's own conclusion. Moved to RESOLVED_QUESTIONS.md.** Summary
    kept here only because the reversal is the useful part:

    This item predicted `program_extra`/`routine_extra` were far too SMALL
    (the 8 real programs implied roughly 4,900/program and 550/routine
    against the wired 484/272 — "a 10× and 2× extrapolation failure").
    The `shellscale_*` isolation batch says the opposite: both constants
    were slightly too LARGE, by exactly 8 bytes each.

    | sweep | measured marginal |
    |---|---|
    | `shellscale_routines_n001..n200` (1 program, 200 rungs fixed) | exactly **264.000**/routine, all 7 steps |
    | `shellscale_programs_n001..n040` (200 rungs fixed, 1 routine per program) | exactly **740.000**/program-with-routine, all 6 steps |

    So `routine_extra = 264`, `program_extra = 740 − 264 = 476`, both now
    wired. Not approximately linear — exactly linear, no rounding, over a
    200× and 40× span. Both pure sweeps now sit at a constant −23 across
    the whole span instead of drifting to +1.97% at the top end.

    **The lesson, which is the fourth time this exact trap has been hit:**
    the +0.871/+0.829 correlations with program and routine count were
    collinear artefacts, the same way the per-instruction surcharge
    correlations before them were. In a real project every count moves
    together, so a regression against real files can nominate any of them
    and will nominate whichever happens to load highest. Isolation
    answered it in one batch; three successive fits against real files
    never would have. **Do not fit a scaling constant off the real
    programs. Build the ladder.**

    `task_extra` (+700) is NOT covered by this: every `shellscale_*` file
    holds Task count at 1 (verified by counting `<Task>` elements, not by
    trusting filenames), so the batch carries zero information about it.
    It stands on its old 2-task derivation.

    Two residuals this batch surfaced and did not close, both small and
    both constant rather than scaling — carried forward as
    **OQ-SHELLCONST** (item 23):
    - a flat **−23** on every pure `shellscale_programs_*`/`_routines_*` file
    - a flat **−815** on all four `shellscale_crossed_*` files, which have
      the same P and R as their pure counterparts but a different generator


### **OQ-AOIORPHAN** — **RESOLVED 2026-08-31, moved to
   RESOLVED_QUESTIONS.md.** Core question (does an orphaned/never-
   instantiated AOI definition cost real memory) is closed: minimal-pair
   real capture confirms `report.py`'s existing $0-extra rule is correct,
   not just assumed (8-byte residual on the unreferenced file, 0.04%).
   See RESOLVED_QUESTIONS.md for the full writeup. The only piece still
   genuinely open is tracked under OQ-COMPOSITESCALE below: real capture
   on the remaining `gen_composite_realistic.py` files (32 of 50 not yet
   captured, 8 of those blocked on an unrelated CIP-Safety-catalog import
   bug) — a larger/varied corroboration, not a reopening of the core
   question.


---

## Closed 2026-09-06

**OQ-PREDEFINED confidence audit — 174 structures were already known.**
185 predefined structures carried `confidence: ASSUMED`. An audit against
the manifest found that 173 of them had `predefprobe_<type>` capture data
sitting on disk at **exactly 0.0000% residual with zero errors**, and
OUTPUT_COMPENSATION at −8 bytes, which is the universal per-file offset
seen corpus-wide rather than a structure-size error. All 174 upgraded to
KNOWN. No byte value changed.

This was a bookkeeping failure, not a knowledge gap, and it was not
cosmetic: `weakest()` propagates a tier upward, so a stale ASSUMED on a
leaf type marks every containing UDT and every real file that uses one.
Combined with the same staleness on BOOL sizing (fixed the same day), the
model was reporting **11.53%** of all real-file bytes as ASSUMED when the
true figure was **4.33%**.

Standing rule from this: a constant carries the tier its evidence supports
on the day the capture lands. `scripts/audit_confidence.py` now checks
this automatically so it cannot drift again.

**OQ-2198ERS3 — root cause found. Not safety-related.**
Six 2198 Kinetix `-ERS3` catalogs were recorded as "undiagnosed" import
failures and were the largest single ASSUMED exposure on real files at
4.07% of total bytes.

**A 2198 `-ERS3` drive runs on a standard, non-safety controller.**
`composite_realistic_v4_001` through `_031` carry `-ERS3` drives on a plain
1756-L81E with no `SafetyLevel`, and all 31 captured at **zero errors**.

The real cause is two defects in `gen_module_sweep_variants.py`'s own
hardcoded copy of the module XML, both confirmed by diffing it against that
known-good file:

1. **No `<ExtendedProperties>` block** — Vendor, CatNum, FeedbackDevice1-4,
   ConfigID. This omission was already found and fixed on **2026-03**
   in `gen_module_motion.py`'s `_drive_module_xml()`, by a byte-for-byte
   diff against a real SampleAxis export. `gen_composite_realistic_v4.py`
   uses that function, which is why its files import cleanly.
   `gen_module_sweep_variants.py` keeps a separate hardcoded copy and never
   received the fix.
2. **A corrupted ConfigData payload** — 119 L5K values against the real
   118, with a spurious `0` at index 114.

So the fix already existed in the repo for three days, in one generator,
while a second generator kept shipping the broken block and the failures
were recorded as an unexplained Rockwell behaviour.

**Correction to an earlier entry in this file.** A first pass at this
concluded that Studio synthesises `:SI`/`:SO` safety tags from the catalog
and that every `-ERS3` therefore needs a safety controller. That was wrong.
It was inferred from the failures alone without checking the repo for
`-ERS3` files that already worked, and 31 of them did. The wrong conclusion
also produced a lint rule flagging any `-ERS3` on a non-safety controller,
which fired on five modules in each of those known-good files. Rule
reverted, with a regression test pinning that a non-safety `-ERS3` is
**not** a finding.

Fixed: `gen_assumed_closeout.py` group A now builds every `-ERS3` catalog
from `_drive_module_xml()` on a plain non-safety controller, count-swept
n=1/2/4.

**OQ-FBDSFC — the last 10 unmeasured predefined structures.** FBD_TIMER,
FBD_ONESHOT, FBD_MATH, FBD_BOOLEAN_AND/OR/NOT, SCALE, RATE_LIMITER,
SFC_STEP and SFC_ACTION were the only predefined types with no capture
behind them. Probe files built (`gen_assumed_closeout.py` group C), same
one-bare-tag shape that closed the other 174.

**Closed as out of scope, not as measured:**

- **v30 firmware baseline.** A single manual reading, and the SDK cannot
  convert v30 exports at all, so it can never be re-measured through the
  capture pipeline. v30 is below the supported firmware range.
- **1769-series per-catalog baselines (9 catalogs).** 1769 is dead
  architecture by decision. The existing captures are also contaminated by
  the I/O-memory-field capture bug and would need a re-run that is not
  coming. Wiring stays in place; nothing further is invested.
- **AXIS_GENERIC.** Predicted and actual agree exactly (35,008) but the
  capture carries a real error — "AXIS_GENERIC axes are not supported by
  this controller" — so it cannot be made a valid fitting point on
  1756-L8x or 5069. Out of scope for both active platforms.
- **~175 predefined structures that no real file uses.** Sized from
  RM018A and now confirmed by probe capture, but they are not exposure on
  any real program. Tracked as KNOWN, not as open risk.


---

## Closed 2026-09-08

**OQ-REAL5069 — CLOSED. The 5069 platform now has real validation.**
`Elmsdale_20251017r01.L5X`, a real 5069-L330ERM production program on fw
35.11, 4.8 MB, Capacity 1,147,896.

Predicted 1,083,267 -> **-5.63%**. Second-worst of the ten real files,
ahead only of MurrayBros at -5.88%.

Until this file, every one of the nine real programs was a 1756-L8x, so
everything the model knew about 5069 came from files it had been fitted on
itself. That is no longer true.

**OQ-BLOCKBYTE — resolved for 5069 by the same file.** The Capacity figure
was reported as "blocks". Treated 1:1 against predicted bytes it gives
-5.63%, in line with every other real file. A 4-byte block reading gives
-76.41% and an 8-byte reading -88.20%, both absurd. So on 5069 the readout
is labelled blocks but the unit is directly comparable to what this project
calls bytes; no conversion is applied, and none should be.

**OQ-L9PRODUCTCODE — CLOSED.** Real ProductCodes for the ControlLogix 5590
family, read directly from four real blank v38 exports rather than
web-sourced or inferred:

| catalog | ProductCode |
|---|---:|
| 1756-L902TS | 316 |
| 1756-L905TS | 317 |
| 1756-L908TS | 319 |
| 1756-L915TS | 320 |

318 is absent between L905TS and L908TS, and L925TS/L950TS/L980TS have no
real export, so nothing beyond these four is generated -- the same rule
that kept 1756-L85ES out until it was confirmed.

Real structural notes, all four identical apart from catalog and code:
ProductType 14, MajorRev 38, MinorRev 11; backplane `Port Id="1"
Address="0" Type="ICP"` with `Bus Size="4"`; **two Ethernet ports at Port
Id 3 and 4**, not 1 and 2, labelled A1/A2 with `EtherNetIPMode="A1/A2:
Dual-IP"` -- the 5069 dual-IP shape on a 1756 chassis; and
`<SafetyInfo SafetyEnabled="false"/>` as an attribute, a form this project
had not seen.

The engine parses all four cleanly: 13,296 predicted, zero blocking errors.

**Chassis-size lint counted a module as its own child — CLOSED.** Not a
sizing question, but it silently blocked a generator for five days and is
worth the trail.

`chassis_size_mismatch` (added 2026-09-03) compared a `PointIO`/`Flex`
port's declared `Bus Size` against the number of modules parented to it,
expecting `children + 1` for the adapter itself. A controller's own `Local`
module is self-parented — it carries `ParentModule` pointing at itself,
the real Rockwell convention in every export checked, generated and real
alike, including the four L9 v38 files. It was therefore counted as a child
on its own backplane, inflating the expected size by one.

The effect: `gen_fw_catalog_matrix.py` aborted partway through v31 on
`fwmatrix_v31_1769_l16er_bb1b`, whose module block is real, verbatim 1769
data (`Port Type="PointIO"`, `Bus Size="2"`, one embedded `Discrete_IO`
child). Correct data, wrong rule. Because `lint_or_raise` aborts the whole
run, no file after that point could be regenerated at all — which is why
the L9 catalogs, added the same day, produced nothing until this was found.

Fixed by skipping any module whose own `Name` equals its `ParentModule`.
The rule had no test coverage at all, which is how it shipped broken;
`tests/test_lint.py` now pins both the real self-parented shape and a
genuine undersize.

**OQ-CSARRAYBASE, resolved 2026-09-11, wired.** The one-time array-level
base for an array of a custom string type is a CONSTANT 4. It does not
vary with the type's name length, and the earlier two-point reading that
said it did (11 chars -> 4, 13 chars -> 12) was an artifact of having no
control.

The closing batch built every array against a SCALAR control of the same
type at the same name length. Differencing the pair cancels the type's
definition cost, and the remainder is a flat 936 at every one of the eight
measured lengths -- 4, 8, 11, 13, 16, 24, 32, 40. The entire name-length
effect belongs to the DEFINITION cost, which was already KNOWN; without a
control it was being read as if it belonged to the array.

Confirmed one-time as well as constant: the 11-char and 13-char count
sweeps differ by exactly +8 at n=1, 16, 100, 255 and 512 -- a fixed gap
that does not grow with n, which is what "one-time" has to mean. That +8
is the definition step between those two names.

The lesson is the method, not the number: a two-point fit with no control
produced a confident wrong answer that looked right on the only two points
it had. 28 name lengths, 23 counts and 8 controls now say otherwise.

**OQ-STRARRAYLARGEN, resolved 2026-09-11, no code change.** The array
formulas were right and the worry was unfounded. Both rates hold exactly
to n=1000, far past the n=100 the constants were originally fitted on:

    built-in STRING array   88.00/element at n=128..1000, zero variance
    custom string array    104.00/element at n=1..1000, zero variance

88 is exactly the wired element(86) + per_element(2); 104 is exactly
element(100) + per_element(4). No block or page allocation appears at any
size, and the consecutive n=1..8 run shows no odd/even pairing artifact of
the kind the AOI-array model has.

This closes the leading hypothesis for the MurrayBros/Elmsdale error --
their STRING[200] and STRING[255] arrays are priced correctly, and were
all along. The KNOWN tier those constants carried was unearned when it was
applied past the evidence, but the answer it gave was right.

**OQ-FBDSFC, resolved 2026-09-11, wired.** The whole FBD/SFC family was
ASSUMED -- sized by reading real Decorated-XML L5K data and never probed
against a controller. The predefprobe_* batch probed all 22, every file at
error_count=0, and the sizes were right: 19 predicted EXACTLY and three
were over-charged by exactly 4 bytes (SFC_ACTION 16 -> 12, FBD_TIMER
48 -> 44, FBD_MATH 16 -> 12). All now KNOWN.

The -4 is a real correction rather than the familiar universal noise: the
other 19 structures, captured in the same run, land dead on.


## OQ-CAMSHAPE — CLOSED 2026-09-11, and it corrected a wired constant

CAM and CAM_PROFILE were fitted on standalone tags while every real use is
a UDT member. `gen_cam_closure.py`'s 27 files captured 2026-09-11 and the
answer is that the container does not matter — but the original CAM
constant was wrong, and the member arm is what exposed it.

**CAM base corrected 8 -> 4, plus 8-byte element-block alignment.** The old
value read exact at n=1/5 and "a flat -4 of already-familiar small
universal noise" at n=10/20/50. It was not noise: the -4 fell exactly on
the EVEN element counts, which is where `12*n` is already 8-aligned. The
real rule is

    CAM array bytes = 4 + align8(12 * n)

and it lands at zero residual on every captured CAM point — the
1/2/5/10/11/20/30/50/100 count sweep, the 04/10/20/30 UDT-member
dimensions, and the 5-tag multi-tag file. The old base-8 form had 3 of
those 15 exact and 12 off by +4.

The same rule is a no-op for CAM_PROFILE, whose 56-byte element is always
8-aligned, so its 13 captured points are untouched. That is the
cross-check: one mechanism explains the type that needed it and leaves the
other exactly where it already was. **CAM_PROFILE promoted FITTED ->
KNOWN** on those 13 points (the original 4-point count sweep plus camx's
tag, UDT-member and multi-tag arms — the independent shapes that were
missing).

Container shape: confirmed a non-effect. `camx_member_*` matches
`camx_tag_*` at every dimension once the alignment rule is applied, and
`camx_nested_i01/i05` follow the instance count.

Still open, and moved into their own thread rather than left inside a
closed item: `camx_scalar_cam` (-104) and `camx_scalar_prof` (-144) — a
SCALAR CAM/CAM_PROFILE, which the corpus contains zero real examples of
and which this model prices as though it were an array of one.
`camx_mixed_d10/d20` (+4), `camx_nested_i01/i05` (+4/+20) and
`camx_udtarray_n05` (+28) each carry one additional unknown beyond the cam
types themselves.


## RET / SBR — CLOSED 2026-09-11, measured at exactly zero

Both were ABSENT from `logic_instructions.weights`, which charged them zero
as an absence of data rather than as a measurement, and coverage.py
correctly reported them as unpriced every time a real file used one.

All 12 `subrtn_*` files captured 2026-09-11 predict at **zero residual** —
`shell` / `sbronly` / `sbrret` at 1, 5, 25 and 100 extra routines, 12 of
12 exact. An SBR or RET costs nothing beyond the routine shell that holds
it, and the three arms agree with each other, which is the cross-check on
both weights at once.

Now listed explicitly at `SBR: 0` and `RET: 0`. Absent from that table
means "no data"; present at 0 means "measured zero". The two must not look
the same, and the coverage error is correctly gone.


## FOR — CLOSED 2026-09-11, weight 80

Also previously absent and charged zero. `forloop_for_r{001,005,025,100}`
came back short by exactly **80 x rung_count** — -80, -400, -2000, -8000.
Four points, perfectly linear, zero intercept.

Cross-checked against its own control arm rather than against zero:
differencing `forloop_for_r<N>` against `forloop_ctl_r<N>` (the same N
target routines reached by JSR instead) gives 8, 40, 200, 800 — a FOR rung
costs exactly 8 bytes more than a JSR rung, at every count. `FOR: 80`
wired; all four files now predict exactly.

The control arm itself does NOT predict exactly, and that is a separate
finding rather than a caveat on this one — see OQ-JSRFOLD.

## Closed 2026-09-11 — stale entries moved out of OPEN_QUESTIONS.md

A staleness pass found four entries in OPEN_QUESTIONS.md that were already
answered, and one whose closed half was still filed under the open half's
name. Each is reproduced below verbatim as it last stood, so the reasoning
trail survives the move.

**OQ-STSIZING** was the most misleading of them: it still read "Structured
Text is completely unmodeled" while `sizing/structured_text.py` has priced
ST since 2026-09-05, `coverage._SIZED_ROUTINE_TYPES` counts ST as sized, and
the full answer was already recorded above under "OQ-STSIZING — Structured
Text (SOLVED, 2026-09-05)". Confirmed against the sixteen real programs:
their 26 ST routines raise no coverage gap at all. The surviving ST thread
is OQ-STEXPR, which stays open on its own entry.

**OQ-AOIORPHAN, OQ-ALARMCOND and OQ-SHELLSCALE** were one-line stubs saying
the content had moved here — which it had. The stubs themselves are the only
thing removed.

**OQ-AOIARRAYDIMENSION** closed 2026-09-03; only its array-LocalTag
dimension-scaling sub-thread is still open, and that now stands on its own
as OQ-AOIARRAYLOCALTAG in OPEN_QUESTIONS.md.

### Verbatim, as it last stood in OPEN_QUESTIONS.md

5. **OQ-AOIARRAYDIMENSION** — the `aoi_array_param_def_only.L5X` import
   thread is **CLOSED 2026-09-03**. Real root cause, from live controller
   testing: BOOL/SINT/INT/DINT cannot be arrays for Input parameters —
   an array parameter must be InOut. The two prior "fixes" (Required/
   Visible forced true/true 2026-08-29, then a real `<Array>`/`<Element>`
   DefaultData body 2026-08-30) were chasing a formatting bug that never
   existed — an array-dimensioned atomic Input/Output Parameter is not a
   legal Logix construct at all; only `Usage="InOut"` permits an array
   Parameter (matches this project's own real corpus evidence,
   `LOG_HMIDisplay`/`BitArray` — both `Dimensions` AND `InOut`, which is
   now understood as the ONLY combination that can exist, not a coincidence
   of the only 2 examples on file). Fixed for real:
   `builders.py::_aoi_parameter_xml` now hard-fails (`ValueError`) if a
   caller ever asks for a dimensioned Input/Output Parameter, so this
   generator-level bug class cannot recur; `lint.py`'s new
   `aoi_array_param_wrong_usage` check is a defense-in-depth net for any
   L5X reaching lint by another path. The broken `aoi_array_param_def_
   only.L5X` file and its never-successfully-captured manifest row are
   removed (confirmed via `convert_log.csv`: FAILED at every one of 5
   logged attempts, 2026-08-30 through 2026-08-31, `XMLSrv_E_IMPORT_
   ABORTED_NO_CHANGES` every time — never had real ground truth to lose).
   Same fix pass also found and closed a second, previously-untested gap
   in the SAME function: the InOut branch never rendered a `Dimensions`
   attribute at all (no generated file had ever actually exercised
   `inout_params=[...]` with `dimension` set until a new test for this
   fix exercised it) — now fixed to match the real `LOG_HMIDisplay`/
   `BitArray` shape.

   **Still genuinely open, separate sub-thread**: the array-LocalTag
   dimension-scaling question (real +400/+404-byte, ~2%, gap on
   `aoi_array_localtag_1_instance`/`_def_only`, both at dimension=100 —
   the only 2 real data points on file, both the SAME size, so it's
   unknown whether the gap is a flat per-array-LocalTag declaration cost
   or scales with dimension/element type). The current `aoi_definition`
   formula charges `per_declared_item` once per declared item regardless
   of `dimension`, so if the real gap DOES scale with size this is a
   genuine missing term. 27-file isolation sweep built 2026-09-03
   (`gen_aoi_arraylocaltag_sweep.py`: dimension 10–1000, type SINT/INT/
   DINT/REAL/BOOL, multiplicity 1–3 array LocalTags/AOI) awaiting real
   capture.[^aoiarraydimension]

6b. **OQ-MODULESTRUCTURAL** — NEW, 2026-09-04, and it changes the target
   for OQ-MODULEIO below. The target application is testing an unknown
   file, and every catalog module number cannot be captured
   individually — the model has to tell that a 16pt digital
   card has XX overhead + 16pts of data, whereas a 8pt analog card has
   different overhead."*

   The per-catalog `module_overhead_by_catalog` table is the wrong shape
   for the real goal. It can only ever cover catalogs we have personally
   captured; a real customer file will contain catalogs we've never seen,
   and those silently fall back to one flat cross-catalog default (1,672)
   that is badly wrong for whole families (the 5069 family sits +28% to
   +35% under-predicted on that default). The table should become a
   FALLBACK for known-exact catalogs, not the primary mechanism.

   What's needed instead: predict a module's overhead from its own
   STRUCTURE, which is already in the L5X and already parsed. First look
   at the evidence, 2026-09-04:
   * A naive structural regression (constant + module count + connection
     input/output/config bytes + module_defined_bytes) over the 98
     error-free single-module `modulesweep_*` captures lands at MAE 845
     bytes / 3.84% mean — better than nothing but not close to the <1%
     target, because it lumps genuinely different module CLASSES (simple
     discrete I/O, analog, drives, safety, network bridges) into one
     linear model.
   * The missing variable is class, and Rockwell already states it: every
     module carries its own PROFILE string on its Input/Output/Config tag
     (`ModuleInfo.input_profile` etc., already parsed since 2026-08-27).
     `AB:1756_DI:I:0` is "1756 digital input", `AB:1756_DO:C:0` is
     "1756 digital output config", `AB:1734_8SLOT:I:0` is an 8-slot
     PointIO adapter, `AB:MotionDevice_Diagnostics:S:0` a drive. This is
     catalog-INDEPENDENT and exactly the "16pt digital vs 8pt analog"
     axis needed here -- 1756-IA16 and 1756-IB16 are different
     catalogs but both `AB:1756_DI`. Across the 98 valid files there are
     143 distinct profile strings resolving to a much smaller set of
     class tokens (DI, DO, IB, OE, OF, SLOT, ...).
   * Point count is recoverable the same way (the `_16` / `_8SLOT`
     numeric token, cross-checkable against the real connection byte
     counts already parsed).

   Proposed model shape, NOT yet fitted or wired:
       overhead = class_base[profile_class] + per_point[class] * points
                  + per_connection_byte * (in + out + cfg)
   fitted per class from the single-module captures, with the existing
   per-catalog table kept as an exact-match override where we have real
   data. This is the single highest-value remaining architecture change
   for the North Star, because it is what makes an UNSEEN catalog
   predictable at all.

### Verbatim, as it last stood in OPEN_QUESTIONS.md

9. **OQ-AOIORPHAN** — **CLOSED. Full entry and reasoning trail moved to `docs/RESOLVED_QUESTIONS.md`** ("Closed 2026-09-05" section).

### Verbatim, as it last stood in OPEN_QUESTIONS.md

18. **OQ-STSIZING** — new, 2026-09-04. **Structured Text is completely
    unmodeled.** `parse_rll_routines` handles RLL only, so every ST routine
    in every file contributes exactly **0** to the prediction. Every file
    in the `gen_st_sizing.py` batch predicts an identical 23,365 today —
    that is the diagnostic property, not a bug: whatever Capacity movement
    comes back IS the ST cost, with nothing to subtract.

    **This is not a small corner.** Measured across `samples/local/`, 23
    real files: **297 ST routines, 24,017 ST lines.**
    | construct | count | | construct | count |
    |---|---:|---|---|---:|
    | `:=` assignment | 8,688 | | `FOR`/`DO`/`END_FOR` | 600/879/148 |
    | `IF`/`THEN`/`END_IF` | 1,739/1,831/1,230 | | `WHILE`/`END_WHILE` | 38/3 |
    | `ELSIF`/`ELSE` | 559/332 | | `REPEAT`/`UNTIL` | 1/8 |
    | `CASE`/`OF`/`END_CASE` | 90/1,085/84 | | `EXIT`/`RETURN` | 39/5 |
    Comments: **5,931 leading `//`, 967 trailing `//`, 27 `(* *)` = 6,925
    lines, 29% of all real ST.** Instruction-style calls INSIDE ST: COP
    362, CONCAT 67, SBR 44, RET 42, DTOS 26, TRUNC 25, TONR 22, JSR 18,
    DELETE 16, OSRI 12, ABS 10, GSV 8, SIZE 7, STOD 7, BTDT 6, CPS 4,
    SCL 4, MSG 2, SSV 1.

    So real ST is ~36% control flow, ~29% comments, and it calls the SAME
    instructions the ladder does. That last fact is the cheapest possible
    route to closing this hole and is what group D tests: 1,000 COP /
    CONCAT / DTOS / SIZE calls hosted in ST, each using operands
    byte-for-byte identical to `gen_logic_sweep`'s own rung text, paired
    against the existing valid `instr_*_n01000` captures. **If they land on
    the same number, the entire per-instruction weight table transfers to
    ST unchanged** and ST needs only a per-statement term and control-flow
    terms on top.

    Sub-question, **OQ-STCOMMENT** (2026-09-04): does an ST comment line or
    block take up data memory, or is it free like tag and rung comments?
    The RLL half of this is already ANSWERED and free:
    `instr_cpt_n05000_comment100` and `instr_cpt_n05000_nocomment` came
    back **byte-identical at 2,282,944**. But that result does not
    transfer, and assuming it would be a real mistake: an RLL rung comment
    is a separate `<Comment>` element hanging off the rung — metadata
    beside the logic — whereas an ST comment lives INSIDE the routine's own
    source CDATA, in the same text Studio compiles. Group B holds 100
    executable lines identical to `realscale_st_n00100` and varies only the
    comments: 100 short leading, 100 long leading (110 chars, the real
    header width from Bender134053's T_ADD routine), 400 short leading, 100
    trailing (zero added lines), and 400 genuinely blank lines with no
    comments at all. That set separates per-comment-LINE from
    per-comment-CHARACTER from per-`<Line>`-element, and answers whether
    blank lines are free.

    Also open and covered by the same batch: whether an ST assignment with
    an arithmetic right-hand side is just a CPT expression (group E
    transcribes `instr_cpt_n01000`'s expression operand for operand into ST
    — if it lands on 474,944 the existing tier-aware CPT model is reusable
    as-is), and whether an ST routine used as a JSR target is charged the
    same parameter cost as an RLL one (group F; all JSR param constants
    were fitted on RLL targets only, and 44 SBR / 42 RET in the corpus say
    ST targets are a real shape). Blocked on capture — **not on anyone
    writing samples: 24,017 real ST lines is more idiom than this needs,
    and every construct and call in the batch is taken from that corpus,
    not invented.**

### Verbatim, as it last stood in OPEN_QUESTIONS.md

20. **OQ-ALARMCOND** — **CLOSED. Full entry and reasoning trail moved to `docs/RESOLVED_QUESTIONS.md`** ("Closed 2026-09-05" section).

### Verbatim, as it last stood in OPEN_QUESTIONS.md

21. **OQ-SHELLSCALE** — **CLOSED. Full entry and reasoning trail moved to `docs/RESOLVED_QUESTIONS.md`** ("Closed 2026-09-05" section).


## OQ-BLOCKBYTE — CLOSED 2026-09-12. A block is a byte on the active platform.

The question, raised 2026-08-30, was foundational and correctly flagged as
"very serious if real": Studio 5000 labels its Capacity readout "bytes" for
1769/L7x processors and "blocks" for 5069/L8x, and this project treats
`actual_bytes` as one uniform unit across the whole corpus with 1756-L81E as
the dominant baseline. If a block were not numerically a byte, every constant
in `memory_model.yaml` fitted against L81E/5069 data would need rescaling.

**The two-file test was captured and never read.** Both files are a single
120,000-element DINT array tag and nothing else, so 480,000 bytes of the total
is exactly 120,000 x 4 with zero packing ambiguity:

    blockbytetest_dint120000   (1756-L81E)  predicted 498,236   actual 498,240

**Four bytes on a 498 KB file: 0.0008%.** On the "blocks"-labelled L8x
processor a block IS a byte, at the scale where any conversion factor would be
unmissable -- a factor as small as 1.001 would show as ~500 bytes and a factor
of 2 as a quarter of a megabyte. The -4 is the same small per-file residual seen
throughout the corpus and is not a unit effect. Every constant fitted against
L81E/5069 data stands as fitted; no rescaling is needed.

**The 1756-L71 twin is excluded, and deliberately.** It lands at -59,076
(-10.4%), which looks like a discrepancy until you note that L7x is dead
architecture in this project: its own per-processor baseline is separately
known to be wrong (`fwmatrix_v33_1756_l7x` sits at -65.7% while every L8x row
in the same matrix is byte-exact), so it cannot isolate a units factor from a
baseline error. Per the platform-scope rule it may not be cited as a reason the
model is out of spec either. The circumstantial 1769/L7x evidence recorded in
the original entry -- two batches landing on a single tiny constant -- is a real
oddity about how those families' Capacity gets read, and it belongs to the dead
architecture rather than to this question.

**Routing correction made the same day.** 50 `composite_realistic_*_r2` rows
named OQ-BLOCKBYTE in their descriptions and were being counted against it by
`scripts/capture_errors.py`. They are composite-scale rows -- 2 to 5% under-
predicted with error counts that scale with file size -- and now route to
OQ-COMPOSITESCALE, which is the question they actually bear on.


## OQ-BASELINE-PROCFW — CLOSED for the active scope, 2026-09-12

**1756-L8x at v35 is EXACT, and that is what this project runs on.** Every
`fwmatrix_1756_L8xE` row at v31, v32, v33 and v38 predicts to the byte, and the
v34/v35 rows carry a +16 that is NOT a baseline error -- it is a
firmware-dependent CONTENT gap (the real MainRoutine content drops to 0 bytes on
v34+ hardware while this engine still predicts 16), already recorded against
whatever eventually prices that content. The baseline itself has no error on the
platform that matters.

The 5069 per-family corrections were wired the same day and took
active-platform baseline rows from 68/140 to 118/140 exact; the 22 that remain
are exactly the L8x content gap above.

**The remaining thread is deliberately NOT being pursued, on instruction:**
whether the per-family firmware correction stays additive once a file carries
real content. Every captured non-L81E-v35 file is bare -- 0 of them carry
content, against 1,255 content files on 1756-L81E v35 -- so that composition is
verified at zero content only. Closing it would need identical content
replicated across the cells where the correction differs, at two sizes, roughly
22 files.

Marked **very low priority, do not build those files**: production work here is
1756-L8x on v35, where the baseline is already exact. Reopen only if a real
program on another processor or firmware ever needs predicting.


## OQ-AOIBOOLPACK-PAIRING, CLOSED 2026-09-13

Groups A, B and C closed on 2026-09-13 as capture-batch segment 1
(`aoialgn_*`, 71 files) and group D as segment 4 (`aoimix_*`, 34 files). The
entry as it stood at the moment it closed is kept verbatim below, because the
two readings it went through -- "a per-family fixed offset tied to which
boundary the packed BOOLs cross", then "a two-variable surface in
(bool_count, atomic_count)" -- were both wrong in instructive ways.

**Group A: the DWORD per-instance term has a mechanism.** The engine counted
packed words as `ceil(bool_count / 32)`. The real count is
`ceil((bool_count + 2) / 32)`: EnableIn and EnableOut occupy two bits in the
same words, and `bool_count` deliberately excludes them because they are not
declared members -- an exclusion that was correct for the member sum and got
carried into the word arithmetic by accident. Confirmed flat-versus-sloped at
12 of 12 points across three consecutive 32-bit boundaries (30/31/32/33,
62/63/64/65, 94/95/96/97), with the slope measured twice per family. Wired as
`aoi_array.enable_bits_packed_with_bools`. This supersedes the "only the
32-bit/DWORD boundary specifically also carries a real per-instance term"
reading, which was the right observation with no mechanism and could not have
predicted 63/64 or 95/96 -- it treated 32 as special rather than as the first
place two extra bits spill a word.

**Group C: the +4 array-tag term is real and is wired.** It had been fitted
and rejected on 2026-09-12 because applying it cost five exact predictions.
Those five rows are now explained: every one is a `b02` file -- bool_count 2,
exactly the number of enable bits -- so the engine's BOOL term cancelled its
own error at that single degenerate count and the row was exact by
coincidence.

**Group D (`aoimix_*`, 34 files): the alignment rule is confirmed at 17 of 17
mixes with zero exceptions, and composition was never the variable.** Member
total held constant while the BOOL fraction was swept, every point built at an
even AND an odd array length. The even and odd deltas are IDENTICAL at all 17
grid points, which is the array side reading exactly: the per-instance size is
`4*atomic_count + 4*ceil((bool_count + 2)/32)` rounded up to 8, confirmed
directly at each mix rather than inherited from a neighbour. The dead premise
this grid was built for -- "a two-variable surface in (bool_count,
atomic_count), sampled far too sparsely" -- is dead for the reason group A
found: BOOL/atomic mix only ever moved the per-instance size.

What group D also did was the thing it was kept for after its premise died:
it put the remaining residual on the AOI DEFINITION, on the one axis
(BOOL fraction at fixed member total) the definition-cost model handled worst.
That residual ran -105 to +69 across the 34 rows when the segment opened. It
is now +8 or +16 on every row, one-sided, 26 of 34 inside the band -- and the
itemised definition formula that did it is the segment's real result. The 8
that is left is the subject of OQ-AOIDEFSHAPE.


### The entry as it stood, verbatim

3. **OQ-AOIBOOLPACK-PAIRING** — split off the now-closed OQ-AOIDEF's old
    "BOOL-array-packing-boundary" thread once its 27 already-captured
    points got reconciled. The `aoi_array` per-instance formula was tagged
    KNOWN ("confirmed exact... 15 real points") but that claim was only
    ever checked at 3 widely-spaced instance counts per shape (n=1/10/25)
    — real dense data disproves it. Confidence downgraded to FITTED.
    2026-08-30: the dense/isolating files got real captures in the
    latest push. Pattern is now clearer, not yet closed: each `bc<N>`
    family (bit-count-per-element family, presumably) carries its OWN
    fixed offset that's constant across instance count within that family
    but differs BETWEEN families — `aoibp_dense_bc10_*` off by a flat
    ~20-24 bytes regardless of n (2 through 12), `bc20_*` flat ~36-40,
    `bc60_*` flat 140, while `aoibp_puremix_8b2a_*` is flat ~-8 to -12 and
    `aoibp_split_allinput30_*` flat ~60-64. A per-family fixed offset that
    doesn't scale with instance count points at a missing per-
    boundary-crossing term (something tied to WHICH bit/byte boundary the
    packed BOOLs cross, not how many instances exist) rather than a
    missing per-instance term — real, promising lead, not yet
    derived/wired.

    **Real capture landed 2026-08-31 for the dedicated boundary-crossing
    isolation sweep** (`aoibp_boundary_bc{16,24,31,32,33,40,48}_n{02,04,
    08}_iso2`, bit-count families straddling several byte/dword
    boundaries, each at 3 instance counts) — and it sharpens the lead into
    a precise one. Five of the seven bit-count families (16, 24, 33, 40,
    48) show a flat delta across all 3 instance counts (+36, +52, +92,
    +108, +124 respectively) — confirming the fixed-per-family-offset
    pattern already found. But the two families AT the 32-bit/DWORD
    boundary — bc31 and bc32 — do NOT stay flat: bc31 goes 92→100→116
    (n=2/4/8) and bc32 goes 100→108→124, both a clean +4 bytes/instance
    on top of their own fixed offset. **Every other tested boundary is a
    pure fixed one-time cost; only the 32-bit/DWORD boundary specifically
    also carries a real per-instance term.** This pinpoints exactly which
    boundary crossing needs the extra term (the DWORD one) rather than
    leaving it as "some boundary, not derived" — genuine progress toward
    a wireable formula, though still needs the "why 32-bit specifically"
    mechanism nailed down (likely a real DINT-alignment packing rule) and
    a check of whether bc63/64 (the next DWORD-adjacent pair up) shows the
    same +4/instance signature before generalizing.

    **PER-INSTANCE LAW DERIVED AND WIRED 2026-09-12. The remaining residual
    is no longer an array question.** All 178 captured `aoibp_*`/`aoipack_*`
    rows were live-recomputed and grouped into 52 sweep families. The
    "odd-length arrays cost 4 bytes more, except when they don't" surface is
    one constant: **the whole instance-array block is padded up to an 8-byte
    boundary**, so the extra 4 bytes appear exactly when the per-instance size
    is congruent to 4 mod 8 and never otherwise. 48 of 48 families that can
    distinguish the two cases agree, **zero exceptions**, across per-instance
    sizes of 4, 8, 12, 20, 24, 32, 40, 44, 48, 64, 76, 84, 104, 120, 124, 220
    and 244 bytes. Wired as `aoi_array.block_alignment_bytes`; same mechanism
    and same constant as `predefined_array_structures`' element-block padding
    (CAM's 12-byte element), which is the independent cross-check.

    The earlier reading in this entry -- a per-family fixed offset plus a
    composition-dependent parity term, "a two-variable surface in
    (bool_count, atomic_count)" -- was wrong in a specific way worth keeping:
    composition was never the variable. It only moved the per-instance size,
    and the per-instance size mod 8 was doing all the work. `mc10` looked like
    "pure BOOL pairs, mixed does not" (b00 -4, b01/b05/b09 0, b10 -4) purely
    because those mixes happen to land on per-instance 44/40/24/8/4.

    Effect: **49 of 52 families are now FLAT in instance count** (were 37 of
    52), captured AOI rows inside +-8 bytes went 37 -> 49, and corpus-wide
    exact predictions went 1,026 -> 1,028 with no family regressing.

    **A flat +4 array-tag term was fitted and deliberately NOT wired.** The
    five families that have a `def_only` control (same AOI definition, no
    instance tag) each sit exactly 4 bytes further under than their own
    definition-only twin: atomic -4/-8, bool -4/-8, mixed +59/+55, mix25_75
    +19/+15, mix75_25 +42/+38 (def residual / array residual). Five for five
    is real evidence, but applying it reduced total absolute residual over the
    178 rows by only 40 bytes (5,818 -> 5,778) while costing three exact
    predictions (`aoipack_mc20_b02_array_n01/n10/n25`, all three at exactly
    0). Moving rows from -10 to -6 inside a noise band the project already
    treats as noise is not progress worth a constant. Recorded here, settled
    by group C below.

    **What is genuinely left, and it is a definition question, not an array
    one.** After the alignment wiring every remaining residual is a per-family
    CONSTANT ranging -38 to +180, and the five controlled pairs above put that
    constant on the AOI DEFINITION. That is the same place the model is
    already known to be weakest: mixed-type AOI definitions fall back to a
    flat 20/item rate because per-type rates do not compose once BOOL sits
    alongside another type (see `memory_model.yaml aoi_definition`). This
    thread therefore hands off to **OQ-AOIDEF**, and what is left under this
    entry is the three families that still vary with instance count.

    **Files built 2026-09-12, awaiting capture** --
    `src/sample_gen/gen_aoi_array_align_closeout.py`, 71 files, plus
    `src/sample_gen/gen_aoi_boolmix_grid.py`, 34 files:

    - **A, `aoialgn_bc{30,31,32,33,62,63,64,65,94,95,96,97}_n{02,04,08}`**
      (36 files). `bc31` and `bc32` are 2 of the 3 families still varying
      with instance count -- `-40/-48/-64` and `-46/-54/-70` at n=2/4/8, a
      clean 4 bytes/instance under-charge -- while bc16, bc24, bc33, bc40 and
      bc48 are dead flat. Either a real DINT-alignment rule that must recur at
      63/64 and 95/96, or the FIRST packed word is special and there is
      nothing to generalize. The corpus has no data above bool_count=60 at
      more than one instance count, so it cannot tell them apart. Same
      all-Input single-section shape as the captured `bc*_iso2` sweep so these
      difference straight against it; n=2/4/8 makes a per-instance term show
      as +8 then +16 while a flat offset stays put.
    - **B, `aoialgn_un_{s01,s02,s03,s05,s01i01,s03i01,s01i03,i01,i03}`**
      (27 files: each shape at `_def_only`, `_n02`, `_n03`). Every captured
      family has a per-instance size congruent to 0 or 4 mod 8 except
      `aoipack_nonatomic_sint_20b10a` (14 bytes, 6 mod 8) -- which is the
      third and last family still varying with instance count (+108 at n=1,
      +60 at n=25). One family at one residue cannot say whether the 8-byte
      block padding is general or whether a non-4-aligned instance size
      triggers something else. SINT/INT parameter counts put the per-instance
      size at the other residues; a real AOI with SINT or INT parameters lands
      there routinely, so this is not a corner case.
    - **C, `aoialgn_def_{mc10_b00,mc10_b05,mc10_b10,mc20_b02,mc20_b18,
      mc60_b30,mc60_b54,mc60_b60}`** (8 files). The `def_only` control the
      `mc*` families never got. Without it their offsets cannot be split
      between definition cost and array cost at all, and it is the direct test
      of the +4 array-tag term above -- including on `mc20_b02`, the one
      family whose exact-zero contradicts it.
    - **D, `aoimix_t{08,32,64}_b*_n{02,03}`** (34 files). Member total held
      constant while the BOOL fraction is swept, every point at an even AND an
      odd array length: the densest available confirmation of the alignment
      rule on an axis designed to vary only what it depends on, and the right
      instrument for the definition-side offset that is left.


## OQ-COMPOSITESCALE, CLOSED 2026-09-13 -- the categories ARE additive

**CAPTURE ERRORS: 82 row(s)** — rows owned by this question that captured with Studio build errors. The question is closed; the rows outlive it, so the count is recorded here rather than being lost.

Closed as capture-batch segment 5 (`addit_*`, 33 files). The question was
whether this project's formulas, each fitted by scaling ONE thing at a time,
stay correct when a real project mixes UDTs, AOIs, arrays, modules and rungs at
once -- and whether an INTERACTION between categories explains why synthetic
composites over-predict below 200 KB and under-predict above 1 MB while real
programs sit at a flat offset.

**There is no interaction.** The grid builds a 3x3 (none / mid / high) for each
of the six pairs drawn from D = UDT-typed tags, L = rungs, A = AOI instances,
M = 1756-IB16 modules, with everything not named by the two axes held at zero.
Additivity is then a subtraction, not a fit:

    residual(a,b) = cost(a,b) - cost(a,0) - cost(0,b) + cost(0,0)

All **24 of 24** residuals -- six pairs at four level combinations each -- come
out with the measured interaction EXACTLY equal to the predicted one. Zero
difference, every cell. The `LxA` cells all carry 16 and the engine predicts 16
in all four. So the composite sign-flip cannot be an interaction between
categories, and every remaining error lives in the four marginal costs
themselves.

**Which the grid then measures exactly, because the all-zero corner is exact
(18,392 predicted, 18,392 actual) and each axis is clean.** All four slopes are
exact between their two points:

| axis | engine charges | real | error |
|---|---:|---:|---|
| D, one UDT-typed tag (40-byte UDT, 11-char name) | 135 | 128 | −7.000/tag over 360 tags |
| L, one `XIC(Bit0)MOV(1,Dst0)ADD(Dst0,1,Dst0)OTE(Bit1);` rung | 96 | 72 | −24.000/rung over 3,600 rungs |
| A, one AOI instance tag + one call passing 2 params | 272 | 256 | −16.000/unit over 180 units |
| M, one 1756-IB16 | 1,712 | 1,704 first, 904 after | −808/module after the first |

**Two of the four were wired.** The A axis resolves against `dscale2`'s own
measurement of the same thing: dscale2's calls pass 3 parameters and cost 168,
these pass 2 and cost 152, so the call site is `120 + 16 per parameter` -- two
independently written generators, different AOI shapes, both exact. The D axis
resolves against `dscale2_udt`, which measures a 9-byte UDT tag as exactly right
over 500 tags where this measures a 40-byte one 7 too high: pad the standalone
tag's data slot to 8 and set `udt_tag_extra` to −4. Together: corpus mean
absolute error 1.853% -> **1.833%**, rows within 1% 2,661 -> **2,667**; the
sixteen real programs 2.133% -> **2.073%** with files inside 1% **3 -> 4**.

**Two were measured, are exact, and are REJECTED by the real programs.** Both
are recorded rather than fitted, with files built:

- The L axis says a rung over-charges 12 bytes per output instruction beyond the
  first, and `UID()UIE();` says the same thing independently at a different
  count (−12.000/rung for 2 outputs). Applying it takes the real programs from
  2.07% to **2.90%** and makes every one of the sixteen worse. Counting outputs
  only outside branch brackets does not save it. -> **OQ-SERIESOUTPUT**, 16 files.
- The M axis measures the module repeat discount cleanly, on a file containing
  nothing but modules: 808 bytes for every 1756-IB16 after the first, against
  the 792 the existing `module_overhead_repeat_discount` table holds. It stays
  gated off for the same reason it was gated off before -- real programs
  under-predict and a discount predicts less. -> **OQ-MODULEMARGINAL**.

The pattern across all four is itself the finding worth keeping: on isolated
synthetic files the engine consistently OVER-charges, while on real programs it
UNDER-charges by 2%. Those are not the same error with different signs. Something
present in real programs and absent from every isolated file is unpriced, and it
is larger than all four of these corrections combined. That is OQ-REALUNDER, and
the additivity result narrows it usefully: whatever it is, it is not an
interaction between the categories this grid covers.


### The entry as it stood, verbatim

11. **OQ-COMPOSITESCALE** — new, real, raised 2026-08-30 after a review of
    a confidential project found a >20% real gap. The requirement: at
    least 50 large programs with I/O and logic, exercising AOIs and UDTs
    at production scale. Every calibration file in this
    project before now isolated ONE feature at a time — never tested
    whether the individually-confirmed formulas are actually additive at
    real project scale/density, or whether interaction effects between
    many UDTs/AOIs/arrays/modules/rungs at once produce a real
    discrepancy that isolated tests can't catch. 50 composite files built
    (`gen_composite_realistic.py`, `samples/generated/composite/`), each a
    genuinely different combination (not the same shape resized): 2-6
    UDTs (1 always nested), 2-5 referenced AOIs + 1-3 orphaned AOIs (also
    feeds OQ-AOIORPHAN), 3-6 large atomic arrays + 1 UDT array,
    TIMER/COUNTER, 2-4 real I/O modules (cycled from `gen_module_sweep.
    py`'s 86 real catalog blocks), 150-900 rungs mixing XIC/OTE/MOV/ADD/
    CPT/TON/CTU/AOI-calls. All on the wrapper's default 1756-L81E/fw35.05
    (corrected 2026-08-31; the processor-family question is isolated
    separately, OQ-BLOCKBYTE, to keep this batch's findings unambiguous).
    26 of the 50 have a fully-predicted total; 24 hit an already-known
    unmodeled real I/O module shape
    (rack-aliased connections, legacy-network bridges, a handful of
    modules with unrecognized nested member types) and fall back to
    predicted_bytes=0/unmodeled, same convention as elsewhere in this
    project — genuinely unmodeled, not a bug in this batch. Real Capacity
    on the 26 fully-predicted files is the actual test: if predicted and
    real land within ~1% at this scale, the individually-confirmed
    formulas really are additive; any real divergence pinpoints an
    interaction effect (or a formula that only breaks at
    scale/density) invisible to every prior isolated test.[^compositescale]

    **Import failures, 2026-08-30 (the l5x2acd run) — 14 of the 50
    fail, not just "awaiting capture."** All 14 hit the same generic
    `XMLSrv_E_IMPORT_ABORTED_NO_CHANGES` wrapper text, no per-file detail.
    Cross-referenced every file's module catalog mix (deterministic,
    computed via `_profile_for_index`) against
    `samples/known_conversion_failures.csv`'s already-known-bad catalog
    list:
      - **8 fully explained** — each includes at least one already-known-
        bad catalog baked into its module mix, no separate cause:
        `composite_realistic_10` (5069-OB16/B, 5069-OBV8S/A),
        `_11` (FANUC Robot R30iB Plus/A), `_22` (5069-IY4/A, 5069-OB16/A,
        5069-OB16/B), `_34` (5069-IB16/A, 5069-IB8S/A, 5069-IY4/A),
        `_36` (PowerFlex 527-STO CIP Safety), `_46` (442G-MABLB-UR-
        E0JP4679/A, 5069-IB16/A), `_47` (5069-OBV8S/A), `_48` (FANUC
        Robot R30iB Plus/A).
      - **6 genuinely new and unexplained (at the time)** — module mix
        contains NO already-known-bad catalog: `composite_realistic_07`
        (1794-OE4/B, 1794-OW8/A, 1794-VHSC/A), `_19` (1794-IR8/A,
        1794-OA8/A, 1794-OE4/B), `_31` (1794-IB16XOB16P/A, 1794-IB32/A,
        1794-IR8/A), `_32` (193-ECM-ETR/A, 193-ECM-ETR/B, 2097-V34PR5-LM,
        2198-C4004-ERS), `_43` (1794-IA16/A, 1794-IB16/A,
        1794-IB16XOB16P/A), `_44` (1794-OW8/A, 1794-VHSC/A,
        193-ECM-ETR/A, 193-ECM-ETR/B).

        **Root-caused and fixed, 2026-08-31**, from the real
        Studio 5000 error-log detail for `_07`: "Slot number in use by
        another module" + "Failed to set the 'ParentModule' property
        (Requested item could not be found.)". All three of `_07`'s
        catalogs were extracted from the SAME real reference export
        (`RobbinsGrn_2026_05_13r00.L5X`) and each independently claims the
        identical real backplane slot that one customer's rack actually
        used — fine standalone, a genuine collision once 2+ such catalogs
        land in the same composite file (same class of bug as the IP
        collision `_modules_xml_unique_ips` already fixed 2026-08-30, just
        a different attribute). Fixed by also remapping each catalog's own
        Local-parented ICP slot to a unique value per file
        (`_remap_local_icp_slot`, `gen_composite_realistic.py`). `_19`,
        `_31`, `_43`, `_44` share the same "2+ catalogs from the same real
        1794-family source rack" pattern and are very likely fixed by the
        same change (not independently confirmed each, but the mechanism
        is generic, not `_07`-specific) — removed from
        `known_conversion_failures.csv` alongside `_07`. `_32` has NO
        1794-family catalog in its mix at all, so this fix doesn't apply
        to it — stays in `known_conversion_failures.csv`, genuinely still
        unexplained, still needs its own real error-log line.

      All 8 catalog-explained failures (`_10`, `_11`, `_22`, `_34`, `_36`,
      `_46`, `_47`, `_48`) remain in `known_conversion_failures.csv` —
      unrelated bug class (the still-undiagnosed CIP-Safety-connection
      failure shared with the standalone modulesweep files), not touched
      by this fix. Cross-checked against which of the 50 have a
      fully-predicted total (predicted_bytes != 0 in manifest.csv, 26
      files) vs which fell back to unmodeled (predicted_bytes=0, 24
      files): 8 of the 14 original failures (`_10`, `_11`, `_22`, `_32`,
      `_34`, `_36`, `_46`, `_48`) are among the 26 fully-predicted files.
      Of those 8, only `_32` is still blocked — the other 7 remain fully
      catalog-explained and still blocked by the separate CIP-Safety bug,
      so real capture on this OQ is still gated on that unrelated fix
      too. `_07`, `_19`, `_31`, `_43`, `_44` were already unmodeled/$0,
      so fixing their import doesn't add real-capture value to this OQ
      directly, but does let them serve as clean structural validation
      (does the file import and match the real module count/shape) even
      without a byte comparison. Needs a real reconversion pass to
      confirm any of this — not independently verifiable from here.

      **Renamed with a "_r2" suffix, 2026-08-31.** The 50 tests needed
      new filenames and the old ones abandoned: real Studio 5000 verify
      errors found separately (see
      OQ item covering aoi_call_arg_count_mismatch/XIC-OTE-data-type,
      meant every one of the 50 composite files changed real content
      again after an l5x2acd batch had already run against the
      names above). All references to `composite_realistic_NN` in this
      section are the OLD, now-deleted filenames, describing what was
      diagnosed against them at the time — the CURRENT files are
      `composite_realistic_NN_r2.L5X` (same index numbers, same
      per-file composition/catalog mix, just fixed content). The 9 still
      catalog-explained-broken filenames in `known_conversion_failures.csv`
      were updated to their new `_r2` names alongside this rename so
      they stay correctly flagged.

      **Real capture landed, 2026-08-31 — the core question is
      essentially answered, and it's good news.** the batch
      captured real Capacity for 36 of the old-named files; 18 of those
      are among the 26 fully-predicted (not catalog-explained-broken,
      not unmodeled) composites — mapped onto the current `_r2` rows
      (confirmed safe: predicted_bytes is identical before/after the
      AOI-arg/XIC-OTE fixes for every index checked). Real vs predicted
      across those 18: **mean +3.15% underprediction, range -0.46% to
      +5.25%**, only one file (`_03`, -0.46%) overpredicted. This is a
      dramatically better result than the >20% real gap on the
      confidential project that started this whole OQ — at realistic
      project scale/density (multiple UDTs/AOIs/arrays/modules/rungs
      combined), the individually-confirmed formulas ARE essentially
      additive; no interaction effect blew up the total the way the
      confidential-project review worried it might. The remaining ~3%
      is small but real and consistently one-directional (17/18 files
      underpredict, not scattered noise) — worth a future investigation
      into which specific residual bucket accounts for it (candidates:
      the still-ESTIMATED-tier logic-content weighting, or a small
      per-file baseline this project hasn't isolated yet), but not
      urgent at this magnitude. The other 8 fully-predicted composites
      (`_10/_11/_22/_34/_36/_46/_47/_48`) remain blocked on the separate
      CIP-Safety-catalog import bug, still no real data for them.

      **Candidate hypothesis proposed 2026-08-31, RULED OUT same day once
      wired.** The OQ-JSRPARAMCOST target-content fix and OQ-AOIINTERNAL-
      LOGIC fix above were both wired and re-checked directly against
      these 18 composite files: **the residual is completely unchanged,
      byte-for-byte, before and after both fixes** (mean still +3.28%,
      same range -0.45% to +5.55%). Root cause: despite the composite
      generator's own docstring claiming "AOI calls... mixing... AOI-
      calls," `gen_composite_realistic.py`'s AOI definitions still use the
      OLD hardcoded self-closing `<Routine Name="Logic" Type="RLL"/>`
      shape (never updated to pass `aoi_xml()`'s `logic_rungs_xml` param,
      the same gap OQ-AOIINTERNALLOGIC found everywhere else) — so there's
      no internal AOI content to weigh in these files either way. Same for
      JSR: the composite generator doesn't appear to declare any JSR-
      target routines with real content. **The composite batch's ~3%
      residual remains genuinely unexplained** — this was a real, testable
      hypothesis, tested directly against real data, and it didn't hold;
      not left as an untested guess.

      **6 more real captures landed 2026-08-31** for composites that fall
      back to unmodeled (`predicted_bytes=0`): `composite_realistic_
      {02,07,19,31,43,44}_r2` now have real Capacity on file (69,048 /
      108,712 / 175,528 / 235,272 / 300,976 / 274,882) but aren't usable
      for tuning anything — no predicted total to compare against. Kept on
      record for whenever the unmodeled real-I/O-module shapes these files
      hit get real formulas of their own.

      **New v2 batch, 2026-09-02 — the residual reappears at a MUCH larger
      magnitude once composites actually exercise AOI-internal-logic and
      JSR-target content, and this time it's explained and wired.**
      Against the 2026-08-30 requirement for 50 large programs with I/O and
      logic, `gen_composite_realistic_v2.py`
      built 50 new files, same UDT/array/module/AOI-declaration shape as v1
      but with every referenced AOI now carrying real internal Logic-
      routine content (5-45 real instructions) and one real 0-param JSR-
      target subroutine per file (20-220 real instructions) — the two gaps
      OQ-JSRPARAMCOST/OQ-AOIINTERNALLOGIC found and wired in isolation,
      now exercised together at composite scale for the first time. Real
      capture landed against all 50 (5 files — `_07`/`_18`/`_19`/`_30`/
      `_50` — carry real Studio 5000 import errors unrelated to sizing: a
      193-ECM-ETR module-compatibility issue and a safety-drive-on-
      non-safety-PLC issue in the module mix, both deprioritized as
      generator-script fixes, not sizing bugs; excluded from all figures
      below). Before any composite-scale fix, the 45 error-free files
      under-predicted by a mean **+5.16%** even with both isolated-test
      fixes already wired — the composite hypothesis this OQ's 2026-08-31
      entry ruled out for v1 (v1 never exercised either gap) turned out to
      be real once a generator actually did exercise them.

      Linear regression (`np.linalg.lstsq`, no intercept) of real residual
      bytes against candidate explanatory variables across the 22 files
      with BOTH zero reported import errors AND a fully-modeled I/O mix
      (indices 1,2,3,4,8,9,10,21,23,26,27,29,31,32,33,34,37,40,42,43,45,46):
      `residual ≈ 20.155 × (AOI-internal-logic instruction count) +
      47.331 × (JSR-target instruction count)`, R²=0.6619511766511494, mean
      abs error 1,507.79 bytes. Beat a flat-%-of-predicted model (R²=0.6015)
      and a combined model (R²=0.6631 — barely better, with the flat-%
      term going slightly negative, meaning the content-count model does
      the real work, not a size proxy). Rounded and wired 2026-09-02 as
      `aoi_logic_composite_surcharge_per_instr: 20` and
      `jsr_target_composite_surcharge_per_instr: 47`
      (`memory_model.yaml`/`constants.py`), applied additively on top of
      the already-wired per-instruction content weight at both the
      AOI-internal-logic and JSR-target-content sites in `report.py`.

      **Re-validated post-wiring: mean abs error on the 22 clean files
      drops from 5.16% to 1.06% (max 5.66%, file #10); all 45 error-free
      v2 files average 1.17% mean abs error.** Confidence is FITTED, not
      KNOWN — R²=0.66 leaves real unexplained variance (max residual still
      5.66% on one file), and the JSR rate being ~2.3x the AOI rate despite
      a similar real instruction mix is not yet mechanistically understood,
      just what the real data shows. More isolated real data — ideally
      varying AOI-count/JSR-content independently of overall file scale,
      rather than all three scaling together as they do in this batch —
      would sharpen or could disprove either constant. The 5 error-flagged
      files' generation-script fixes (module catalog compatibility,
      sequential slot numbering) remain separately tracked and
      deprioritized until this tuning work lands.


    **CAPTURE ERRORS: 82 row(s)** flagged here by `scripts/capture_errors.py` (step 2b), 2026-09-11;
    count revised 2026-09-12 when 35 `composite_realistic_*_r2` rows were
    re-routed here from the now-closed OQ-BLOCKBYTE. They are composite-scale
    rows -- 2 to 5% under-predicted with error counts that scale with file
    size -- so this question is where they belong.
    47 captured WITH Studio build errors, so their `actual_bytes` is
    SUSPECT rather than wrong — part of the file may never have reached the
    controller, which inflates apparent over-prediction. None of them carries
    any error text: every errored row in the manifest was captured between
    2026-08-23 and 2026-09-08, and the error-log reader only began working
    2026-09-10, so these need RECAPTURE before their numbers are used.
    `composite_realistic_v3_02`, `composite_realistic_v3_03`, `composite_realistic_v3_04`, `composite_realistic_v3_05`, `composite_realistic_v3_06`, `composite_realistic_v3_07` (+41 more)


## OQ-STEXPR, CLOSED 2026-09-13 -- one law replaces a five-entry table

**CAPTURE ERRORS: 1 row(s)** — rows owned by this question that captured with Studio build errors. The question is closed; the rows outlive it, so the count is recorded here rather than being lost.

Closed as capture-batch segment 6 (`stx_*`, 30 files). The entry it replaces held
five measured shapes with confidence MEASURED_SPARSE and everything else falling
back to the ladder CPT model, which over-predicted a one-operator ST assignment
roughly threefold.

**THE LAW.** One form, wired as `structured_text.assignment_low_operator_bytes` /
`assignment_two_operator_bytes` / `assignment_per_operator_bytes` /
`real_dest_integer_source_bytes`:

    per_statement = base(n_operators, destination type)
                  + each operator's own CPT tier premium above tier 1
                  + 48 per INTEGER-typed NAMED source read into a REAL destination

The measured grid, 1,000 statements per file differenced against the routine
shell, so each number is one statement:

| operators | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 8 | 10 | 12 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DINT dest | 36 | 40 | 148 | 172 | 196 | 220 | 244 | 292 | 340 | 388 |
| REAL dest | 60 | 56 | 204 | 244 | 284 | 324 | 364 | 444 | 524 | 604 |

Both rows are 148/204 at two operators and then dead linear at 24/40 per operator
after, exact at every one of the eight higher counts. The step between one and two
operators (108 DINT, 148 REAL) is real and large, which is the mechanism the old
entry had already guessed at: a single-operator assignment compiles to one
instruction, a compound one reaches for expression evaluation. REAL at one
operator costing 4 LESS than REAL at zero is measured, not a transcription error.

**WHY THE OLD TABLE WAS WRONG RATHER THAN INCOMPLETE.** Its five entries were each
measured on a DIFFERENT expression and then keyed on operator count alone, so the
shape's own cost was baked into the count. All three of the non-trivial ones come
back EXACTLY from the law:

| old entry | the file it came from | law |
|---|---|---|
| `1\|true` 152 | `R0 := D0 + D1;` | 56 + 2 DINT sources x 48 |
| `2\|false` 164 | `D0 := D1 + D2 * 2;` | 148 + 1 multiplicative x 16 |
| `5\|true` 452 | `R0 := (D0+D1)*R1 - R2/2 + 1.5;` | 324 + 2 multiplicative x 16 + 2 DINT sources x 48 |

**THE OPERATOR PREMIUM IS THE CPT TIER TABLE, UNCHANGED.** `stx_opkind_*` holds
the count at four and varies only which operator: `+`, `AND` and `XOR` all read
196/statement, `*`, `/` and `MOD` all read 260. 64 over four operators is 16 each,
and 16 is exactly `cpt_expression.operator_tier_costs`' own tier-1-to-tier-2 step
(36 -> 52). So ST needs no parallel classification -- it asks that table for
`tier_cost(op) - tier_cost('+')`. AND and XOR are now measured at tier 1, which
that table did not cover at all.

**AN AOI CALLED FROM ST COST NOTHING, AND COSTS `120 + 16 PER PARAMETER`** -- the
same two constants as a call from a rung. Same invisibility as segment 3's RLL
call sites and the same cause: an ST call statement is matched by an all-caps
instruction pattern and real AOI names are mixed-case. Measured on
`stx_call_aoi_p{01,02,04,08}`, whose labels count declared INPUT parameters while
each call also passes the output, so the parameters actually passed are 2, 3, 5
and 9: 152, 168, 200, 264 per call, exact at all four.

    A first pass fitted 136 + 16p by taking the label as the parameter count. It
    fits all four points just as exactly and is wrong -- two constants against
    four collinear points absorbed the off-by-one silently. Recorded in
    memory_model.yaml as a warning.

**EFFECT.** 42 of the 48 ST rows in the corpus now land exactly (26 of 26
assignment and opkind rows, plus the three old shapes). Corpus mean absolute error
**1.833% -> 1.545%**.

**AND THE HONEST HEADLINE: this moved the sixteen real programs by nothing**
(2.073% -> 2.074%). The claim that justified the call-statement arm was wrong.
`gen_st_expression_grid.py` states the real corpus holds "128 ST routines, 6,586
ST lines" of which "call statements 2,094 -- the single largest shape". Re-counted
against the current parser:

| | ST routines | ST lines | assignments | AOI call statements |
|---|---:|---:|---:|---:|
| the 16 held-out programs | 26 | 3,994 | 2,499 | **0** |
| all 91 files in `samples/local` | 307 | 24,745 | 8,099 | **82** |

Of 758 bare call statements across all of `samples/local`, **690 are built-in
instructions** -- COP 325, CONCAT 61, SBR 63, JSR 46, RET 42, TONR 22, DTOS 17,
DELETE 15 -- every one already priced through the routine's own `code_text` by the
RLL weight table. Only 68 are AOI calls. The parser finds all 26 ST routines the
raw XML holds in the held-out set, so this is not a detection gap: real ST is
simply a much smaller share of these programs than the docstring asserted. The
figure was never verified before it was used to size a batch.

**Carried forward, with files built** (`gen_st_closeout.py`, 21 files, OQ-STEXPR
remains the owner in `docs/OPEN_QUESTIONS.md` for these): the operator premium at
exactly one operator and on the REAL row, `**` and `OR` in ST, the conversion rate
for SINT/INT/LINT sources, and the +256..+268 one-time that every
`stx_call_aoi_p*` file carries -- the same ~264 a routine containing AOI calls
carries in RLL, which no file in either language separates from a per-call term.


### The entry as it stood, verbatim

29. **OQ-STEXPR** — ST assignment expression cost, five shapes measured.
    2026-09-04.

    An ST assignment is **not** priced like the equivalent CPT. That was
    the working hypothesis — the `st_expr_cpt_mirror`/`instr_cpt` pair
    differ by exactly the +432 routine shell, which looked conclusive — and
    routing every assignment through the tier-aware CPT model on that basis
    over-predicted `realscale_st_n01000` by **+132%**.

    | shape | operators | dest | measured |
    |---|---:|---|---:|
    | `D := 0;` | 0 (bare literal) | DINT | 36 |
    | `D := D + 1;` | 1 | DINT | 40 |
    | `D := D + D * 2;` | 2 | DINT | 164 |
    | `R := D + D;` | 1 | REAL | 152 |
    | `R := (D+D)*R - R/2 + 1.5;` | 5 | REAL | 452 |

    The tell is the 1-operator case at 40: that is an ADD's own weight, not
    a CPT's. Logix appears to compile a simple assignment to the single
    equivalent instruction and only reach for CPT-like evaluation on a
    compound expression — which is why the 2-operator DINT case lands on
    the CPT number and the 1-operator cases land nowhere near it.

    Five points are clearly not one curve, so they are stored as an
    explicit sparse table rather than interpolated. A shape outside it
    falls back to the CPT model AND is reported as a
    `coverage/st_expression/...` gap, so a real file says so rather than
    quietly carrying a wrong number.

    **What would close it:** the direct ST analogue of what `cmpcpt_*` did
    for RLL — operator count 0..6 × DINT/REAL destination × with and
    without a float literal. Not yet generated; it is the obvious next ST
    batch and is not blocked on anything external.

    Also still open on ST, one thread each:
    - `st_jsr_param_target_n00100` is the only ST file not exact (−243,
      −0.52%). Every JSR parameter constant was fitted on RLL targets, and
      the corpus has 44 SBR / 42 RET inside ST, so an ST JSR target is a
      real shape that may be charged differently.
    - `st_ctl_case` carries a +21 residual; the CASE decomposition into
      per-construct and per-selector is one data point short.
    - `while_block` was corrected 72 → 76 on the strength of the
      literal-RHS rate (36). Only one WHILE file exists, so the split
      between per-WHILE and per-assignment rests on that substitution.



    **CAPTURE ERRORS: 1 row(s)** flagged here by `scripts/capture_errors.py` (step 2b), 2026-09-11.
    1 captured WITH Studio build errors, so their `actual_bytes` is
    SUSPECT rather than wrong — part of the file may never have reached the
    controller, which inflates apparent over-prediction. None of them carries
    any error text: every errored row in the manifest was captured between
    2026-08-23 and 2026-09-08, and the error-log reader only began working
    2026-09-10, so these need RECAPTURE before their numbers are used.
    `st_instr_concat_n01000`

---

# Archived 2026-09-18 — the in-depth review

## OQ-STEXPR-OPERATOR — new 2026-09-17, split out of OQ-STEXPR by the
    21-row `stc_*` closeout. **Every number below is measured and none of it may
    be wired, because each operator has exactly two points and the fit needs
    two parameters.**

    Each file is 1,000 ST assignment statements, one operator kind, so the
    per-statement under-charge is the file total over 1,000:

    | shape | operators | dest | per statement |
    |---|---:|---|---:|
    | `stc_prem1_{add,sub,mul,div,mod}` | 1 | DINT | **0 — exact** |
    | `stc_prem1_{and,or,xor}` | 1 | DINT | **+84** |
    | `stc_prem1_pow` | 1 | DINT | **+84** |
    | `stc_opkind_or` | 4 | DINT | **0 — exact** |
    | `stc_opkind_pow` | 4 | DINT | **−168** |
    | `stc_premreal_add` | 4 | REAL | **0 — exact** |
    | `stc_premreal_mul` | 4 | REAL | **−64** |
    | `stc_premreal_pow` | 4 | REAL | **−288** |
    | `stc_conv_sint` | 1 | REAL ← SINT | **+88** |
    | `stc_conv_int` | 1 | REAL ← INT | **+112** |
    | `stc_conv_lint` | 1 | REAL ← LINT | **−96** |
    | `stc_conv_mixed` | 1 | REAL ← mixed | **+44** |

    **THE BLOCKER IS GONE, AND IT WAS NEVER A TWO-PARAMETER FIT. CLOSED AND
    WIRED 2026-09-18.**

    The framing above -- "two unknowns from two points, exactly determined and
    therefore unfalsifiable" -- was wrong about the model it was fitting into.
    The ST assignment law does NOT have a single first-operator-plus-rate form.
    It already has two separate regimes, and has had since the 30-file `stx_*`
    grid: at fewer than two operators the cost is a LOOKUP, and at two or more it
    is base-plus-per-operator-rate. The step between them is 108 bytes on the
    DINT row and 148 on the REAL row, large and measured.

    So the 1-operator and 4-operator points do not compete for the same two
    parameters. Each one pins a constant in its own regime, alone:

      * `stc_prem1_and/or/xor` pin the DINT one-operator LOOKUP at **124** --
        +84 over the additive 40, the same 84 on all three files, which is what
        makes it a class effect rather than three coincidences. `stc_prem1_pow`
        pins the same lookup for `**` at **204**.
      * `stc_opkind_or` pins the DINT n>=2 bitwise premium at **0** -- four OR
        operators read exactly the tier-1 196, residual 0. Nothing is fitted:
        the 84 belongs to the one-operator compile and not to the operator.
      * `stc_opkind_pow` pins the DINT n>=2 `**` premium at **38** per operator
        (348 against 196 over four), less than half the 80 that ladder CPT's tier
        table charges.
      * `stc_premreal_mul` and `stc_premreal_pow` pin the all-floating-point
        premiums at **0** and **8**. Assumption B is refuted in the opposite
        direction from the one predicted: the premium does not scale with the
        REAL row's larger per-operator rate, it VANISHES. Multiplying REALs is
        one FPU operation like adding them; multiplying DINTs is not.
      * `stc_conv_{sint,int,lint}` pin the conversion per source type at **92,
        104 and 0**, and `stc_conv_mixed` is an independent additivity check that
        lands to the byte: one DINT plus one SINT source is 56 + 48 + 92 = 196.
        Four files, three unknowns, one exact cross-check -- over-determined
        already.

    **One genuinely new finding came out of wiring it, and it decides between two
    readings nothing else in the corpus separates.** Keying the premium on the
    DESTINATION type broke `st_expr_cpt_mirror_n01000` by exactly +32 per
    statement. That file is `R0 := (D0+D1)*R1 - R2/2 + 1.5;` -- a REAL
    destination, but it multiplies a DINT subexpression by a REAL and divides a
    REAL by an integer literal. It pays 16 per multiplicative operator;
    `stc_premreal_mul`, same count and same destination type but REAL sources
    throughout, pays 0. **The premium follows the OPERANDS, not the
    destination.** The base still follows the destination. Both files are exact
    only under that split, and there is no other pair in the corpus that would
    have caught it.

    That fix exposed a real parser bug on the way: `_NUMBER` in
    `sizing/structured_text.py` matched the digits INSIDE identifiers, so
    `R0 := R0 * R1` counted five integer literals and every all-REAL statement
    looked like it had integer operands. Harmless until the premium started
    keying on exactly that. Now anchored with `(?<![\w.])`.

    **`stc_callone` DOES separate per-call from per-routine, and this entry said
    it does not.** The correction: the three `stc_callone_*` files carry one call
    each, but the four `stx_call_aoi_p*` files they difference against carry
    **one thousand**, and the residual is +268 at one call and +256 to +268 at a
    thousand. A 1,000x change in call count moving the number by 12 bytes is the
    separation. Wired as `st_aoi_call_routine_bytes: 264`, once per ST routine
    containing any AOI call -- the same one-time an RLL routine with AOI calls
    carries, which is the point: an AOI costs the same from Structured Text as
    from a rung, one-time term included.

    **Result: the ST family goes from 8.3291% to 0.0091% mean absolute error --
    60 of 69 rows byte-exact, 67 of 69 inside the universal +-8.** The only two
    outside are the two threads that were already their own: the +228 on
    `st_jsr_param_target_n00100` and the -32 on `st_ctl_case`. Real set
    1.6732% -> 1.6725%, flat as it must be: the sixteen held-out programs carry
    26 ST routines between them.

    **What the six 2-operator files are now for.** They were the enabler; they
    are the FALSIFICATION TEST. Every constant above is pinned by one file, and
    each rests on the law's existing assertion that the per-operator premium is
    CONSTANT in n -- an assertion validated across ten counts for `+` and `*`
    (`stx_ops02..12`) and now extended to the bitwise operators, `**` and the
    all-float row on one count each. A 2-operator point for `and`, `or`, `xor`
    and `pow` at DINT and for `mul` and `pow` at REAL would reject a premium that
    is not constant in n. Worth building; no longer blocking. SPEC ONLY.

---

# FULL OPEN-QUESTIONS REVIEW, 2026-09-18

Every entry above was recomputed live against the current engine. Status of all
39, with the measurement behind each. "Within 8" means inside the universal
per-file residual this corpus carries everywhere, which is the practical
definition of exact for a whole file.

## Closed by data already in hand — no files needed

| question | evidence |
|---|---|
| **OQ-AOIDEFSHAPE** | 54 of 54 rows within ±8, 38 byte-exact, mean 0.012%. |
| **OQ-BRANCHDEPTH** | 17 of 17 byte-exact, mean 0.000%. |
| **OQ-TASKOVERHEAD** | 10 of 10 byte-exact. |
| **OQ-PREDEFINED** | 191 of 191 within ±8, 183 byte-exact, mean 0.001%. |
| **OQ-SHELLCONST** | 9 of 9 within ±8, 6 byte-exact. |
| **OQ-IDENTNAMELEN** | 24 of 24 byte-exact once the Task-name term was wired today. Program and routine names are `floor(len/8)` confirmed at twelve lengths; a Task name is the same step with a minimum of 8. |
| **OQ-CAMSCALAR** | 36 rows, 29 within ±8, mean 0.066%. |
| **OQ-AXISMARGINAL** | 13 of 13 byte-exact on every row that captured clean. Its remaining 57 errored rows are all the bus-sharing defect, which is OQ-MODULEMARGINAL's, not a sizing question. |

## Wired today, from measurements with zero residual

| question | what was wired |
|---|---|
| **OQ-EVENTTRIGGER** | EVENT instruction = **56 bytes**. It had no weight at all. 56n + 8 exactly at n = 10/100/1000. Instruction half closed; trigger-source half still open. |
| **OQ-MODULEIO** | **1756-EN2T = 432**, off the 1672 fallback. Flat −1,240 per module, zero curvature, four counts. |
| **OQ-MODULEMARGINAL** | Six 2198 −ERS3 catalogs: **flat per copy, no repeat discount**, 3,640 (3,376 for S130), one-time term 4,008 lower for D012/S086. 23 of 24 points byte-exact. |
| **OQ-IDENTNAMELEN** | Task names charged, minimum 8. |

## Measured exactly and DELIBERATELY NOT APPLIED

**OQ-SERIESOUTPUT.** −12 per writing instruction beyond the first in a rung.
Byte-exact on all 16 rows across eight output counts, invariant to type, tag
uniqueness and series-versus-branch, and independently corroborated by
`ntag_uidpair` from an unrelated family. Applying it moves the real set
**1.7036% → 3.2167%** with every one of the sixteen going the wrong way, so it
is wired end to end and gated `apply: false`. The confound is that every
`srout_*` rung has exactly one condition instruction and real rungs carry
several; 12 new files sweep that.

## Files generated to close the rest — 22, all lint-clean

| arm | files | question | what it decides |
|---|---:|---|---|
| `sroutc_c{1,2,4}_k{1,2,4,8}` | 12 | OQ-SERIESOUTPUT | whether the discount survives multiple conditions. `c01_k01` is shape-identical to `srout_ote_k01` and must read 0. |
| `cpttri_k3_t{211,212,221}` | 3 | OQ-CMPCPTLAYOUT | completes the 8-sequence k=3 tier truth table so the +4 discriminant is read, not guessed. |
| `cpttri_pow_p3_adjacent` | 1 | OQ-CMPCPTLAYOUT | separates `**` adjacency from operator count. |
| `stc2_prem2_{and,or,xor,pow}` | 4 | OQ-STEXPR-OPERATOR | the missing middle count at DINT. |
| `stc2_premreal2_{mul,pow}` | 2 | OQ-STEXPR-OPERATOR | the missing middle count at REAL. |

## Ruled out today, which is progress of its own

- **UDT definitions are not the real-file gap.** `pukall` carries 205,099
  udt_definition bytes against a +9,008 residual; `emporium` carries 207,814
  against +129,375. Scaling the category 10–15% makes the mean worse.
- **AOI definitions are not either.** `defscale_aoidefs_n{5,10,20,40,60}` reads
  −20/−40/−80/−160/−240 — exactly −4 per definition, five points, zero
  residual. All 331 definitions across the sixteen real files total ~1,300
  bytes.
- **No single per-unit cost fits the real residual, and less well than before.**
  Re-running the correlation with modules now exact, every feature's coefficient
  of variation got *worse* — all ≥1.10, where the best was 0.66. The module
  error had been flattering that analysis.
- **`routine_logic` remains the best single correlate (k = +0.105) and must not
  be fitted**: the strip ladder measured logic as OVER-charged on both programs.

## Cannot be closed by a generated file

| question | why |
|---|---|
| **OQ-LADDERBASE** | Two capture sessions on one real export disagree by 18–25k. Needs three existing files recaptured in one session. |
| **OQ-REALUNDER** | Its own hypothesis is disproven; needs OQ-LADDERBASE settled and a third real ladder. |
| **OQ-CTLSHELL** | Sized at +7,800 (1756) / +4,072 (5069), worth 1.7036% → 1.5964% alone. Three probe files specified; needs the decision to generate. |
| **OQ-193ECMETR** | Needs the raw Studio error-log line, not a generator run. |
| **OQ-EXPORTSCOPE** | Needs a controller at the bench. |
| **OQ-L9BUDGET** | Needs real per-catalog user memory from an L9 controller. |
| **OQ-MODULEMARGINAL** (bus half) | Needs a decision between a standalone-drive donor and decoding the ConfigData bus-sharing indices. |
| **OQ-ALARMDEF** | Parked: zero ALMD/ALMA occurrences in any of the sixteen real programs. |

## Still open with work specified but files not yet built

`OQ-AOIARRAYLOCALTAG` (byte-count versus element-count),
`OQ-UDTMEMBERNAME` (a UDT with no BOOL members swept by member count),
`OQ-AOISTRUCT` (several untested packing assumptions),
`OQ-SAFETYSCOPE-SIZING` (a code decision: whether Safety-class tags are sized at
all), `OQ-AOIDEFITEMIZE`, `OQ-V3GENBUGS`, `OQ-BUILDFAIL-OPEN`, `OQ-AXISCOMBO`,
`OQ-REAL5069`, `OQ-DEFSCALE`, `OQ-BASELINE-PROCFW` (contaminated only by dead
L7x/1769 rows; 0.019% across the 55 active-platform rows).

## OQ-CAMSCALAR — CLOSED as OQ-CAMSHAPE 2026-09-11 (see
    RESOLVED_QUESTIONS.md: container shape is a non-effect, the CAM base was
    corrected 8 -> 4 with 8-byte element-block alignment, CAM_PROFILE
    promoted to KNOWN). What survives is narrower and stays open:

      - `camx_scalar_cam` (-104) and `camx_scalar_prof` (-144). A SCALAR
        CAM or CAM_PROFILE — no dimension at all. The corpus contains ZERO
        real examples of one, and this model prices it as an array of one
        element, which these two files say is wrong by about a hundred
        bytes. Whether a scalar is even legal in real Logix is part of the
        question; the files converted, so it is.
      - `camx_mixed_d10/d20` (+4), `camx_nested_i01/i05` (+4/+20) and
        `camx_udtarray_n05` (+28). Each carries one unknown beyond the cam
        types themselves — two cam members in one UDT, depth, and an array
        of a UDT containing arrays of a predefined. All four are small and
        none is explained by the cam constants, which are now exact
        standalone and as members.

## OQ-CPTARRANGE — does operator ARRANGEMENT change CPT cost?
    **ANSWERED 2026-09-12 from the 28 captured `cptarrange_*` rows, which had
    never been reconciled. No, with one clean exception — and reading them
    turned up a +348 nobody had seen.**

    **Arrangement is a non-effect.** Four arms (alternating, frontloaded,
    grouped, split) sweep operand counts 3 to 9 with the multiplications in
    completely different places, and 26 of the 28 rows land on the IDENTICAL
    residual. The slopes agree exactly as well: alternating n03 -> n04 steps
    +4,000 in both prediction and actual, n04 -> n05 steps +2,400 in both. The
    arrangement-blind expression model is right.

    **The one exception is a rule, not noise.** Five rows sit 400 bytes higher
    in actual than the other 23, and they are exactly the five whose expression
    begins with TWO additions before the first multiplication:

        cptarrange_grouped_n03   L0+L1+L2*L3
        cptarrange_grouped_n04   L0+L1+L2*L3*L4
        cptarrange_split_n07     L0+L1+L2*L3*L4*L5+L6+L7
        cptarrange_split_n08     L0+L1+L2*L3*L4*L5*L6+L7+L8
        cptarrange_split_n09     L0+L1+L2*L3*L4*L5*L6+L7+L8+L9

    `grouped_n05` at `L0+L1+L2+L3*L4*L5` (THREE leading additions) and
    `split_n03` at `L0+L1*L2+L3` (ONE) are both in the majority, so the trigger
    is the POSITION of the first multiplication -- the third operand
    specifically -- and not "grouped" or "split" as a style. Two of the four
    arms happen to produce that prefix at some counts and not others, which is
    why it reads as arm-specific noise until the rung text is lined up.

    **The +348, which is the more interesting find.** The majority residual is
    not zero; it is **+348, identical on all 26 rows regardless of operand
    count** -- a flat per-file over-charge, not a slope error. The neighbouring
    `cptrd_*` families, same generator and same tag pool, sit at **+4**. Two
    things differ and either could be the cause:

        cptarrange   destination Dest (DINT)   operands L0..L9 (DINT)
        cptrd        destination R2   (REAL)   operands R*/N* (REAL/LINT)

    **Test files built 2026-09-12, `gen_cpt_arrangement_closeout.py`, 21
    files.** The engine predicts an identical total for all nine arm-A files,
    so every captured difference there is a pure measurement.

      - `cptpos_m{1..8}_n09` + `cptpos_add_n09` (9) -- nine DINT operands, every
        operator an addition except ONE multiplication, swept across all eight
        positions, plus an all-addition control. Operand count, tag pool,
        destination and rung count held identical. If the rule is "first
        multiplication at operand 3", `cptpos_m3_n09` stands alone and the other
        seven agree. No existing file varies position with the count fixed.
      - `cptdest_d{dint,real}o{dint,real}_n{010,100,1000}` (12) -- destination
        type crossed with operand type crossed with RUNG count, expression held
        at `A+B*C+D`. Read three ways: destination type, operand type, and --
        the part neither existing family can give -- whether 348 is per FILE or
        per RUNG, since every captured file in both families has exactly 100
        rungs and cannot distinguish 348 once from 3.48 each.


    **ANSWERED 2026-09-14 (segments 20 and 22). Arrangement is free. CLOSED.**

    `cptpos_m{1..8}_n09` moves a single `*` through an otherwise all-`+`
    nine-operand expression, 100 CPT calls per file. **Seven of the eight
    positions are byte-identical to the prediction and to each other**, which
    extends the already-recorded parenthesization result: neither grouping nor
    position changes the cost. `cptpos_add_n09`, the all-`+` control, is exact.

    `cptpos_m3_n09` is the lone exception at +400 -- exactly +4 per call -- with
    positions 1, 2, 4, 5, 6, 7 and 8 all at 0. There is no mechanism for position
    3 being special that is absent at 2 and 4. **Flagged for RECAPTURE, not
    modelled**; a one-row special case is what this project has twice been burned
    by.

    **Two type-mismatch costs found on the way, measured exactly and deliberately
    not fitted.** `cptdest_d{dint,real}o{dint,real}_n{00010,00100,01000}` is a
    clean 2x2 on one shape (`L0+L1*L2+L3`, three operators, four operands):

        destination   operands      residual per CPT
        DINT          4 x DINT                     0
        DINT          4 x REAL                   +48
        REAL          4 x DINT                    +4
        REAL          4 x REAL                     0

    Exactly linear across a 100x span in all four arms, and **both matched arms
    are byte-exact at every count** -- an independent validation of the
    integer-tier and REAL-destination models at scale.

    The two mismatched arms are real under-charges with no term in the model, and
    neither is wired because **one operand count cannot separate a per-call cost
    from a per-operand cost**: +48 on four REAL operands is equally 48 per call or
    12 per operand, and +4 on four DINT operands equally 4 per call or 1 per
    operand. Real-file exposure was measured before deciding -- **3 of the 256 CPT
    calls in the sixteen real programs** are integer-destination with a REAL
    operand or float literal, roughly 144 bytes across the whole real set -- so
    there is no pressure to guess.

    **Discriminator: the same four arms at two operand counts (2 and 8), operator
    count held at three.** Four files settle both constants outright.

    **THE ARRANGEMENT RULE IS SOLVED AND WIRED 2026-09-18, and it is exact on
    every row that ever contradicted a tier-count model.**

    The 28-file `cptarrange_*` sweep captured: four arrangements at every operator
    count 3 through 9, tier counts held fixed, 100 rungs each. Read after
    subtracting the batch's −352 per-file constant (see OQ-CPTREALDEST, item 0 —
    without that subtraction these rows look like noise):

    | arrangement | n=3 | 4 | 5 | 6 | 7 | 8 | 9 | leading tier-1 run |
    |---|---:|---:|---:|---:|---:|---:|---:|---|
    | alternating | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 at every n |
    | frontloaded | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 at every n |
    | grouped | **+4** | **+4** | 0 | 0 | 0 | 0 | 0 | 2, 2, 3, 3, 4, 4, 5 |
    | split | 0 | 0 | 0 | 0 | **+4** | **+4** | **+4** | 1, 1, 1, 1, 2, 2, 2 |

    **The six rows that cost 4 more are exactly the six rows whose leading run of
    tier-1 operators is 2.** Every other row has a run of 0, 1, 3, 4 or 5 and
    costs nothing extra. One rule, 28 rows, zero residual:

        + 4 bytes per call iff EXACTLY TWO tier-1 operators precede the first
          tier-2 operator

    It also retro-explains every point this question was opened for, without
    being fitted to any of them:

      * `cptmix_scaling_grouped_n05` (`L0+L1+L2*L3*L4`, run 2) costs 4 more than
        `cptmix_scaling_alternating_n05` (run 1) at identical tier counts — the
        original smoking gun.
      * The same pair is IDENTICAL at 11 operators, which is what made this look
        inconsistent: at n=11 the grouped run is 6, not 2.
      * The three (2,1) files the two-tier refit left 4 short —
        `cptcx_operatormix_mixedops`, `_nested` and
        `cptcx_spotcheck_mixedops4op_n100`, all measuring 192 where the model
        said 188 — are `L0+L1+L2*L3`, a run of 2.

    Wired as `cpt_expression.leading_tier1_run_length: 2` /
    `leading_tier1_run_bytes: 4`. All 28 `cptarrange_*` rows now sit on the
    identical −352, so nothing arrangement-dependent is left unpriced on the
    integer path. `tests/test_logic_sizing.py` previously pinned those four as
    unexplained misses and now pins the rule with the real captured numbers.

    Why exactly two and not "two or more" is not known, and it is stored as the
    measurement it is rather than smoothed into a curve.

    **The REAL-destination path is NOT given this rule**, and the reason is
    counted rather than asserted: `cptrdarrange_grouped_n04` needs it (+4, run of
    2) but the eight parenthesised n=5 rows that pin `operator_count_base[5]` at
    328 have a run of 1, so applying the rule there together with the 324 those
    new files measure fixes 4 rows and breaks 10. See OQ-CPTREALDEST item 2 — the
    two questions are entangled at n=5 and have to be settled together.

## OQ-STEXPR — **ALL FOUR ASSUMPTIONS MEASURED AND WIRED 2026-09-18.**
    The 21-file `stc_*` closeout captured cleanly (every row `error_count` 0,
    every residual an exact multiple of the 1,000 statements per file) and
    answered all four, plus the fifth item that was measured-but-unseparated.
    The numbers and the reasoning are in **OQ-STEXPR-OPERATOR** below, which is
    now closed rather than blocked; the headline is that the ST family went from
    8.3291% to **0.0091%** mean absolute error, 60 of 69 rows byte-exact.

    Answers, one line each:
      1. **The one-operator premium** is not a premium. That row is a LOOKUP per
         operator CLASS: additive 40, multiplicative 56, bitwise 124, `**` 204.
      2. **The premium on the REAL row** does not scale up — it vanishes. And it
         is keyed on the OPERANDS, not the destination.
      3. **`**`** is 38 per operator in ST, not the tier table's 80. **`OR`** is
         confirmed tier-1 at four operators.
      4. **Conversion is per SOURCE, keyed on the source's own type**: DINT 48,
         SINT 92, INT 104, LINT 0. `stc_conv_mixed` confirms the additivity to
         the byte.
      5. The AOI-call one-time IS separated and is **once per ST routine** (264),
         not per call.

    What is left on ST, unchanged and each its own single-point thread: the +228
    on `st_jsr_param_target_n00100`, the −32 on `st_ctl_case`, and the WHILE
    split resting on one file. The original text follows.

    The ST assignment law's four remaining assumptions.
    The expression-cost thread CLOSED 2026-09-13 (capture-batch segment 6) and
    is in `docs/RESOLVED_QUESTIONS.md`: one law replaced the five-entry
    count-keyed table, 42 of 48 ST corpus rows now land exactly, corpus mean
    absolute error 1.833% → 1.545%, and an AOI called from ST — which cost
    nothing — is `120 + 16 per parameter`, the same two constants as a call
    from a rung. **21 files built, awaiting capture.**

    What the law still assumes, each because every file that pins the constant
    holds another variable fixed:

      1. **The operator premium at exactly ONE operator.** Every file that
         measures a premium has two operators or more, and the one-operator row
         is a lookup (40 DINT, 56 REAL) rather than base-plus-rate.
      2. **The premium on the REAL row.** All six `stx_opkind_*` files write to
         a DINT destination, where the per-operator rate is 24; the REAL row's
         is 40, so the premium could scale with it rather than staying at 16.
      3. **`**` and `OR`.** The tier table prices `**` at a premium of 80,
         untested in ST; `OR` is absent from that table and so falls to tier 1
         beside AND and XOR, which *are* measured there.
      4. **The conversion rate for integer types other than DINT.** The 48 comes
         from DINT sources only. SINT and INT are narrower conversions, LINT a
         wider one.

    And one thing measured but unseparated: with the call law applied, all four
    `stx_call_aoi_p*` files land at **+256, +260, +268, +268** — the same
    one-time ~264 a routine containing AOI calls carries in RLL (see
    `memory_model.yaml aoi_call_site`). No file in **either** language separates
    that one-time from a per-call term, because every existing file scales the
    two together.

    Also still open on ST, one thread each, unchanged:
    - `st_jsr_param_target_n00100` is the only non-exact ST file (+628). Every
      JSR parameter constant was fitted on RLL targets and the corpus holds 63
      SBR / 42 RET inside ST, so an ST JSR target is a real shape that may be
      charged differently.
    - `st_ctl_case` carries a −32 residual; the CASE decomposition into
      per-construct and per-selector is one data point short.
    - `while_block` was corrected 72 → 76 on the strength of the literal-RHS
      rate. Only one WHILE file exists, so that split rests on a substitution.

    **Files built 2026-09-13** — `src/sample_gen/gen_st_closeout.py`, 21 files,
    1,000 statements each except group E, all on the same tag pool and routine
    shape as the existing `stx_*`/`st_*` captures:

    - **A, `stc_prem1_{add,sub,mul,div,mod,pow,and,or,xor}`** (9 files). One
      operator, DINT destination — reads each operator's premium at the count
      where the law currently applies none. Against `stx_ops01_dint`'s 40.
    - **B, `stc_premreal_{add,mul,pow}`** (3 files). Four operators, REAL
      destination and REAL sources so no conversion term intrudes. Against
      `stx_ops04_real`'s 284.
    - **C, `stc_opkind_{pow,or}`** (2 files). The two entries `stx_opkind_*` left
      out, in its identical shape, against its 196 and 260.
    - **D, `stc_conv_{sint,int,lint,mixed}`** (4 files). One operator, REAL
      destination, both sources of one integer type; `mixed` reads one DINT and
      one SINT in the same statement, which says whether the rate is per source
      or per statement.
    - **E, `stc_callone_n{00010,00100,01000}`** (3 files). Exactly ONE AOI call
      statement in a routine of 10, 100 and 1,000 statements, so the call count
      is pinned at 1 while the routine grows 100x — the first separation of the
      +264 one-time from anything per-call, in either language.

    **CAPTURE ERRORS: 1 row(s)** flagged here by `scripts/capture_errors.py`
    (step 2b). `st_instr_concat_n01000` captured WITH Studio build errors, so its
    `actual_bytes` is SUSPECT rather than wrong -- part of the file may never
    have reached the controller, which inflates apparent over-prediction (it
    reads −52,000). No error text was recorded: every errored row in the manifest
    was captured between 2026-08-23 and 2026-09-08 and the error-log reader only
    began working 2026-09-10, so it needs RECAPTURE before its number is used.
    It is excluded from every figure quoted above.

## OQ-VERIFINSTR —
    **the ZERO-OPERAND half is CLOSED 2026-09-13 (capture-batch segment 8,
    `ntag_*`).** MCR, TND, UID and UIE each land EXACTLY at all five counts from
    10 to 5,000 rungs — 20 of 20 rows, zero residual anywhere, so those four
    weights are confirmed at three orders of magnitude and no longer need a
    zero-operand caveat. The 5 non-exact rows in that family are all the PAIRED
    shape and belong to OQ-SERIESOUTPUT, which they sharpen considerably: see
    that entry for the −12 × (outputs − 1) law now measured at 2, 3 and 4
    outputs, and for the elimination of the repetition candidate by a one-rung
    file that pays the full discount.

    The rest of the entry, unchanged: instruction weights measured but never
    wired, and
    the classification of what is left. **Ten wired 2026-09-12; four
    reclassified out of scope; one left alone on purpose; one still open.**

    Found by `scripts/unreconciled.py`: ten count sweeps had been captured,
    were clean, and had never been differenced. All ten were charged ZERO.
    Every slope is exact at n=10/100/1000, differenced between consecutive
    points so the shared per-file base cancels, and both intervals agree:

        MCD 184   PID 156   MAG 124   MCS 120   UPPER 84
        STOR 80   FBC  76   LFU  72   RTOS  72   BRK   56

    `PID` is the per-RUNG instruction weight, not the 180-byte PID predefined
    structure -- a PID rung costs 156 plus whatever its control tag costs as
    data.

    **DTR: the cause is found and the fix already landed. RECAPTURE.**
    Corrected 2026-09-12 -- an earlier note here claimed the terminating NOP
    "is already present and always has been", which was wrong. Reading the
    file as it stood on its capture date:

        rung THEN (captured 2026-09-08)   DTR(D0,-1,D1);
        rung NOW  (fixed    2026-09-10)   DTR(D0,-1,D1)NOP();

    DTR is a comparison: it conditions the rung instead of writing to it, so a
    rung containing only DTR has no output and every one of them fails --
    which is exactly the observed error_count of one per rung. The NOP was
    added two days after the capture, so the three `unweighted_dtr_*` rows
    measured a file that no longer exists. Their capture columns are cleared
    and the files need nothing but recapture; the "real cost 0" reading off
    them was an artefact of the rungs being rejected, and 16 stays wired until
    a clean capture says otherwise.


    **THE DTR RECAPTURE LANDED, AND THE SBR/RET LADDER WITH IT. BOTH WIRED
    2026-09-18. The `unweighted_*` family goes from 4.6865% to 0.1574% mean
    absolute error, 18 of 22 rows inside the universal +-8.**

    **DTR is 40 per rung, and 16 was wrong.** The recaptured rows are clean
    (`error_count = 0` at all three counts, so the NOP fix worked) and they read
    +404, +4,004 and +40,004 at 10, 100 and 1,000 rungs against a weight of
    **zero** — DTR never made it into `logic_instructions.weights` at all, so
    the "16 stays wired" above was describing a constant that was not there. The
    slope is exactly 40.000 at three counts two orders of magnitude apart, with
    the family's universal +4 per file left over. Wired as `DTR: 40`.

    Correction to this entry while here: the same sweep's five siblings are NOT
    unweighted. AND 40, OR 40, RTOS 72, LFU 72 and UPPER 84 were already in the
    table by the time these files were captured, and all fifteen of their rows
    read the universal +4, so this batch **confirms** those five weights at
    three counts rather than measuring them. DTR was the only one of the six
    still unpriced. The generator's own docstring still says all six carry no
    weight; that was true when it was written and is not now.

    **An SBR/RET pair that carries OPERANDS costs 112 per JSR target. Wired.**
    `unweighted_sbrret_t{001,010,050,200}` put one such pair inside 1, 10, 50
    and 200 distinct targets:

        targets     1      10       50      200
        residual  -164    +844   +5,324  +22,124

    112 per target at every step — (844+164)/9, (5324−844)/40 and
    (22124−5324)/150 are all exactly 112 — with a per-file constant of −276.
    After wiring, all four rows sit at that flat −276.

    Three things make this a law rather than one family's slope:

      * **It is not the instructions.** The 12 `subrtn_*` files use
        parameterless `SBR();` and `RET();` and measure exactly 0 at 1/5/25/100
        rungs. They still do after this change — no leak. So
        `logic_instructions.weights` keeps `SBR: 0` and `RET: 0`, correctly, and
        the operands are what cost.
      * **It is not per operand or per parameter.**
        `jsr_paramcount_n01..n15` hold one target and sweep the parameter count
        from 1 to 15 with a residual that is FLAT. A per-param reading needs
        n=15 to sit 1,568 below n=1.
      * **It collapses a discrepancy in an unrelated family.** The two JSR
        file-level constants were 96 apart — −280 on the zero-param
        multi-target sweep, which has no SBR at all, and −184 on the
        param-bearing sweep, which does. Charging this 112 moves the second to
        −296, so the two agree within 16 instead of 96. A constant derived from
        one family closing a gap in another is the cross-check that was missing
        when `b_base` and `per_target` were fitted against each other.

    Real set: 1.6721% -> **1.6566%**, every one of the sixteen the right way.
    Real programs carry SBR on 126 of their 128 nonzero-param JSR targets, so
    this reaches them.

    A 7-file variant batch built to hunt this cause was deleted the same day
    rather than shipped: it was designed against the false premise and would
    have spent seven conversion slots re-confirming a fix already in the tree.

    `error_count` is EXACTLY the rung count -- 10 at n=10, 100 at n=100, 1000
    at n=1000 -- so it is one error per rung, a per-rung shape problem rather
    than anything file-level. DTR is a comparison and conditions the rung
    instead of writing to it, so it needs a terminating output; that is
    already present and always has been (`DTR(D0,-1,D1)NOP();`), so a missing
    terminator is NOT the cause and adding one changes nothing. Three
    differences from the ONE real DTR call site in the corpus
    (`Sorter1_20260722r00.L5X`,
    `DTR(...)OTE(THGHeartbeatPulse)TON(THGHeartbeatTmr,?,?)`) are each
    candidates, and `gen_dtr_variants.py` (7 files) separates them:

      - `dtrnop_n{010,100}` — the committed shape unchanged, the control that
        reproduces the error rather than assuming it.
      - `dtrote_n{010,100}` — OTE terminator instead of NOP, Reference still
        shared. Isolates whether NOP is simply not acceptable after DTR.
      - `dtruniq_n{010,100}` — OTE plus its OWN Reference element per rung.
        DTR's third operand is its stored previous-scan value, not a plain
        destination, so n rungs sharing one may be the same class of error as
        two OTEs driving one bit. Leading suspect, because the error count
        tracks the rung count exactly.
      - `dtrreal_n010` — the real rung transplanted whole, TON and all. If even
        this errors, the rung is not the problem and the tag pool or file shell
        is implicated.

    Two counts on the three main arms, so whichever builds clean also yields
    DTR's per-rung weight in the same round instead of needing a second.

    **ESTOP / ROUT / LC / RIN: OUT OF SCOPE (Safety), not unpriced.** All four
    appear only inside a GuardLogix SafetyProgram, which this project does not
    size; CROUT was reclassified the same way 2026-08-24. Identified from their
    real call shapes, every one of which takes the `_S`-suffixed safety reset
    tags that exist only in a safety task. Now in `coverage._SAFETY_FAMILY`.
    Reporting them as holes overstated the gap and buried the real ones.

    **SCP: a USER AOI, not a built-in.** Four real exports declare an
    `AddOnInstructionDefinition` named SCP; a fifth calls it without declaring
    it, and its arity varies across the corpus (3 operands in one program, 7 in
    another). The gap is a partial export, not a missing weight. Now in
    `coverage._KNOWN_USER_AOI`, and the coverage note for such a mnemonic says
    CONFIRMED rather than "the name shape suggests".

    **Net on the held-out programs: unpriced native instruction uses fell from
    133 to 57 — and all 57 are EVENT.**

    **STILL OPEN: EVENT.** 57 real uses, charged zero, and its per-rung cost
    has never been measured: `eventtask_instronly` is a single point, which can
    confirm a total but cannot separate the instruction from the file.
    `gen_unweighted_closeout.py` (3 files, `uwclose_event_n{00010,00100,01000}`)
    sweeps it, with the call shape transplanted VERBATIM from the real corpus
    (`EVENT(TrackingInfeed)`, the most common of 44 real uses; all 16 distinct
    real shapes are the same single-operand form naming an EVENT task) and a
    real EVENT task declared for the rungs to resolve against. All three files
    predict an identical 18,900, so the whole captured delta is the EVENT cost.
    Awaiting capture.

    **CAPTURE ERRORS: none. RECAPTURED CLEAN, verified 2026-09-18.** The rows
    this entry used to flag as captured-with-errors now carry `error_count = 0`
    in the manifest, so their `actual_bytes` is trustworthy and every number
    above is drawn from clean captures. `scripts/capture_errors.py` routes no
    errored row here any more; the old block was a warning that had outlived
    its cause.

    **Zero-operand (non-tag) instructions, reviewed 2026-09-12 on a direct
    question — were NOP, AFI, TND, UID and UIE tested?** Two halves, very
    different states.

    **Solved:** `NOP` (16) and `AFI` (4) have five count points each
    (n = 10 / 50 / 100 / 1,000 / 5,000) and every one reconciles at a flat
    −8 — the universal per-file residual, not an instruction error — across
    that whole 500× range.

    **Weights right, evidence thin:** `TND` (24), `UID` (40), `UIE` (40) and
    `MCR` (16) rest on exactly TWO points apiece, `instrfirst_<x>` (n=1) and
    `instrfirst_<x>_x10` (n=10). Their slopes are exact there — TND 216 bytes
    over 9 extra instructions, UID and UIE 360 over 9, MCR 144 over 9, each
    matching its wired weight and the real bytes with no remainder — and all
    four sit at a flat −12 rather than a growing residual, so nothing looks
    wrong. But two points cannot separate a true per-instruction constant from
    a first-pass offset plus a different slope, and none has been measured
    above 10 while NOP and AFI were checked to 5,000.

    **25 files built** (`src/sample_gen/gen_nontag_instruction_sweep.py`):

    - `ntag_{tnd,uid,uie,mcr}_n{00010,00050,00100,01000,05000}` (20 files) —
      the same count points NOP and AFI were confirmed at, so each instruction
      goes from 2 points to 7 over the same range and the two halves become
      directly comparable.
    - `ntag_uidpair_n{00001,00010,00100,01000}` + `ntag_uidpair_withbody_n00100`
      (5 files) — every existing UID/UIE point measures a **bare, unmatched**
      instruction, which is not how either is used: they bracket an
      uninterruptible region. If the matched-pair cost is not simply 40 + 40
      then the separate sweeps have been measuring a shape real Logix never
      contains. The body arm checks whether instructions inside a protected
      region cost what they cost outside one.

    **`EOT`, `IOT`, `SFR`, `SFP` — real instructions, no weights entry, priced
    at zero, and deliberately NOT built.** Files were written and withdrawn:
    `lint.py` rejects all four as unrecognized (accurate — no real rung
    containing one has been verified into this project); `SFR`/`SFP` address an
    SFC routine by name and this project's builders produce none, so the file
    would name a routine that does not exist, Studio would reject the rung, and
    the rest would still import and still fill in `actual_bytes` — the exact
    mechanism behind OQ-AOIINTERNALLOGIC's suspect calibration; and `IOT`'s
    operand is a real output module reference while `EOT`'s is an SFC storage
    bit, so both invented shapes are guesses. Per CLAUDE.md's
    transplant-never-compose rule these four need **one verified rung apiece
    from a real export**. Recorded in `docs/INSTRUCTION_COVERAGE.md`.

## OQ-TAGORDER — tag declaration order is FREE

**Closed 2026-09-18, measured, six files, all six byte-identical.** Raised
from outside the model: "BOOL LINT INT DINT BOOL takes up different space in
the controller than another order." It does not.

`tgord_{grouped,widefirst,narrowfirst,alternating,pairs,shuffled}` each hold
the SAME 400 controller tags — 100 each of BOOL, INT, DINT and LINT, with
identical names — and move nothing but the declaration sequence. The engine,
which has no order term at all, predicted all six at **56,528**. All six
captured at **56,528**, delta 0, `error_count` 0.

That covers the widest span the multiset allows: strictly descending width,
strictly ascending width, one-of-each rotation (the maximum number of width
transitions possible), two-of-each, a fixed seeded shuffle, and grouped by
type. **If adjacent-tag alignment padding existed, `widefirst` and
`narrowfirst` would be the extremes and they are equal to the byte.**

This also generalises the one prior order result rather than merely agreeing
with it. `aoidshape_order_*` had shown order to be free INSIDE an AOI
definition, which is a packed structure whose layout Logix controls; the
open question was whether a controller tag list — a series of independently
allocated slots — behaves differently. It does not. **Order is free at both
scopes.**

The question was worth asking and worth closing rather than assuming: before
this batch the corpus had no file anywhere that held a mixed tag multiset and
varied only the order, so every order effect was invisible to every test the
project had run. It changes cost without changing any count, which is exactly
what a per-tag rate, a per-type rate and a category scale all fail to see.

A defect caught by `scripts/confound_check.py` before the batch was
committed: the control was originally grouped in ascending width order, which
reproduced `narrowfirst` exactly and would have spent a capture slot on a
duplicate.


## Produced / Consumed tags — FORCE-CLOSED as below the noise floor

**Closed 2026-09-18 by decision, not by solving it, and that distinction is
the point.** A Produced tag does cost more than the model charges. It is not
worth another capture slot, and no further file may be specced for it.

**What was measured.** `prodcons_{base,produced,consumed}`, 20 tags of one UDT
each. Base captured at 22,640 against 22,648 predicted (−8, the universal
band). **Produced captured at 44,080 against 22,648 — +21,432, a 48.6%
under-prediction, exactly 1,072 bytes per tag.** The `<ProduceInfo>` block
carries a cost the model has no term for.

**Why it is closed anyway.** Produced tags are **0.11% of the 31,532 tags in
the sixteen real programs** and Consumed 0.06%. The headline residual is
653,678 bytes; at 1,072 each, the entire real Produced population is on the
order of a thousand bytes. Most of what such a tag costs is already charged —
through the UDT definition that types it and through the module that carries
the connection — so the unmodeled part is the remainder, not the tag.

**The Consumed row is suspect and stays that way.** `prodcons_consumed`
captured with `error_count = 20`, one per tag, which is what a Consumed tag
does when the producing controller it names is absent from the project. It
read identical to the Base control, which is equally consistent with all 20
tags never reaching the controller. Testing it properly needs a producer
module in the file. That will not be built.

**The general rule this established**, now in `CLAUDE.md`: a feature below
roughly 0.5% of real tags or real instructions does not get a capture slot,
however cleanly it measures. A precise number on a negligible feature is
still a day not spent on the residual.


---

# CLOSED 2026-09-18 — bounded at zero by the ceiling result

The measurement that closed these is in `docs/TASKS.md`: let all eight
category scales float and fit them **directly on the held-out real programs**
— cheating, an upper bound no honest procedure can beat — and the result is
mean 1.0149%, max 2.5919%. Still fails the stopping rule. Then leave-one-out,
fitting on fifteen files and scoring the sixteenth: **mean 1.5539% against a
1.5607% baseline. 0.007 points, with 8 of 16 files getting worse.**

Every question below has the same mechanism: *a cost constant for some
category is slightly wrong.* The experiment above bounds the total possible
payoff of getting **every one of them right at once** at approximately zero
on a program the model has not seen. They are not closed because they are
wrong, uninteresting, or unanswerable — several are answered, and the
reasoning in each is kept intact below. They are closed because their
maximum achievable contribution to the only number that matters has been
measured, and it rounds to nothing.

Reopening one requires new evidence that its mechanism is NOT a category
scale — i.e. that it represents content the engine does not count at all. A
better constant is not such evidence.

2. **OQ-CMPCPTLAYOUT** —
    **A SECOND THREAD FOUND AND WIRED 2026-09-13 (capture-batch segment 12,
    `cpttier_*`): `per_extra_same_tier_operand` was only ever a TIER-1 rate.**
    Its 24 came from `cptcx_operandcount_n01..n10`, which uses the same ADD
    operator throughout, and it was being applied to every uniform-tier
    expression. Uniform tier-2 expressions read:

    | MUL/DIV/MOD operators | engine (24) | real | under-charge |
    |---:|---:|---:|---:|
    | 1 | 140 | 140 | 0 (`cmpcpt_cpt_op_{mul,div,mod}`) |
    | 3 | 188 | 220 | **+32** |
    | 4 | 212 | 260 | **+48** |

    16 per operator beyond the first, with a single tier-2 operator already
    exact to pin the intercept, so the tier-2 rate is 24 + 16 = **40** — exact at
    both counts and both rung counts, four rows, zero residual. Tier 1 stays 24
    (`cpttier_k3_t1x3` and `k4_t1x4` were already exact). `cpttier_*` rows landing
    exactly went **10 of 22 → 14 of 22**, within ±8 **14 → 18**.

    **TIER 3 IS DELIBERATELY LEFT ON THE TIER-1 FALLBACK, because two shapes at
    the same operator count disagree by 40.** `cptpow_p2` reads −16/rung and
    `cptpow_p3` −12/rung, while `cptpow_p2_adjacent` reads **+24/rung** — same
    two `**` operators, different adjacency. So adjacency of `**` is an unmodelled
    term of its own worth 40 bytes, and setting any uniform tier-3 rate would fit
    one of those shapes and break the other. `cptpow_p1`, `p1_t1x1` and `p1_t2x1`
    are all exact, so a single `**`, alone or mixed with one other tier, is right.

    **What is left in the two-tier mix path is ±4 and below the band.** After the
    tier-2 wiring the only non-exact `cpttier_*` rows sit at exactly +4/rung:
    `t1x2_t2x1` and `t1x2_t2x2` (the two non-nested mixes with tier-1 count
    exactly 2), plus `nested_t1x1_t2x2` (whose non-nested twin is 0) and
    `nested_t1x2_t2x1` (whose twin is also +4). Read as a tier-1-count effect it
    is 2 shapes of 5; read as a nesting effect it is 1 of 2. Four bytes, two
    shapes each way, inside the project's ±8 residual band — recorded, not
    fitted.

    **The `cmpfl_*` float-literal arm stays open and is not derivable from what
    exists.** All 13 rows are single-rung files, so each is one point with no
    slope: 0, 0, +8, +16, +16, +32, +32, +48, +52, +52, +92, +108, +116. That is
    the non-monotonic REAL/float-literal interaction this entry already describes
    as needing dedicated architecture rather than more raw points, and 13 isolated
    points cannot separate operand type from operator tier from literal count.

    The original thread, for the record, unchanged below.

2b. **OQ-CMPCPTLAYOUT, the original entry** — down to one thread. Uniform, T1+T2, T1T3/T2T3,
   and (as of 2026-08-29) the all-3-tier mix are ALL solved and wired,
   confirmed exact on every real data point on file. Only the REAL-
   operand/float-literal interaction remains open, and it's now a harder
   problem than "assumed linear, awaiting more points" — real new data
   shows it's genuinely NOT monotonic in operand count, ruling out any
   simple per-count model. 2026-08-30: the 12 `cptmix_*` probe files
   (float1/real1/real2/real3 position/adjacency/nesting variants) got
   real captures in the latest push — all land within 0.7-1.3% (188-272
   bytes on ~20,500-byte totals), small and real but too tight/consistent
   across position/nesting variants on their own to isolate a clean new
   term from; still needs the dedicated architecture work, not more raw
   points.[^cmpcpt]

   **2026-09-12: the thread above is CLOSED, and the entry's numbers were
   stale.** All 65 captured `cptmix_*` rows were live-recomputed against the
   current engine: **63 land at exactly 0**, and the other two at −4
   (`scaling_grouped_n05`) and −16 (`scaling_t1t3/t2t3_alternating_n08`),
   both inside the project's universal small-residual band. The "0.7–1.3%,
   188–272 bytes" figure predates later wiring and no longer describes any
   file. Every REAL-operand and float-literal probe the batch was built for
   — `real1_float1`, `real2/real3_adjacent_float1`, `float1_pos_*`,
   `disentangle_*`, `stacked_dint_floatliteral`, `realcheck_real` — is
   exact. The non-monotonicity that made it look hard was the pre-refit
   two-tier rate, and the 2026-09-04 split-by-tier refit removed it.

   **WIRED 2026-09-12, a different and structural gap found by the same
   reconciliation: CMP had no expression model at all.** CPT has been priced
   from its own expression's operators since 2026-08-23; CMP was priced as a
   flat weight plus two boolean surcharges (compound, float-literal). So a
   CMP whose operands are themselves arithmetic expressions was charged as
   though they were bare tags — `CMP(L0+L1>L2)` paid nothing for the `+`.
   Every bare-tag and bare-literal CMP shape in the corpus measured exact;
   every arithmetic one carried a real negative residual, and nothing
   connected the two facts.

   The fix routes CMP's arithmetic operators through **CPT's own
   operator-tier table with no separate CMP fit** (`cost_for(operators) −
   base_read`, since CMP keeps its own 76-byte base weight). The tiers
   fitted on CPT land on CMP's measured residuals as they are — which is the
   evidence that CMP and CPT share one expression law rather than that a
   constant was tuned:

   | CMP shape | was | now |
   |---|---:|---:|
   | `L0+L1>L2` | −36 | **+0** |
   | `L0+L1>5` | −36 | **+0** |
   | `(L0+L1)*L2>L3-L4` | −100 | **+0** |
   | `L0+L1>L2+L3` | −64 | −4 |
   | `(L0+L1)>L2&&(L3-L4)<L5` | −64 | −4 |
   | `L0*1.5>L1+2.5` | −128 | −52 |

   Comparison operators and the `&&`/`||` connectives are deliberately not
   tokenized as arithmetic — the connective is already priced by
   `compound_cost`, and double-charging it would break every bare compound
   CMP, all of which measure exact. Corpus exact predictions 1,028 → 1,031.

   **Two residuals survive, and 47 files were built for exactly those two**
   (`src/sample_gen/gen_cmpcpt_expr_closeout.py`):

   - **A, `cmpfl_*`** (13 files). The −52 on `L0*1.5>L1+2.5`.
     `cmp_surcharge.float_literal_cost` (72) is charged once per call as a
     BOOLEAN, fitted on one shape (`CMP(L0>5.5)`, no arithmetic, exact). The
     surviving −52 says the boolean breaks once there is more than one float
     literal or once a float sits inside an arithmetic sub-expression, and
     one file cannot say which — nor whether the rate is per-literal (72 is
     then wrong, since 128−76 = 52) or a float-context promotion of the
     operator tiers. Float-literal count is swept 0..3 at fixed arithmetic
     operator count, plus a **REAL-TAG arm** (`CMP(R0+R1>R2)`, no literal
     anywhere) that separates "a float literal costs something" from
     "evaluating in floating point costs something". The corpus has no data
     on the REAL-tag case at all.
   - **B, `cpttier_*`** (22 files). The −4 on `L0+L1-L2*L3` and
     `(L0+L1)*(L2-L3)`, and the matching −4 on two 2-operator CMP shapes.
     4 bytes would be noise except it scales exactly:
     `cptcx_spotcheck_mixedops4op_n100` is 100 rungs of the first shape and
     lands at −400. It is also not simply "mixed tiers" — every
     `cptmix_pair_t1t2_*` file mixes tier 1 with tier 2 and measures exact.
     Tier composition is swept at **fixed operator count** (3 and 4
     operators, every tier split), each shape at n=1 and n=100 so a per-rung
     term shows as −400 and a per-file offset stays at −4. The existing files
     vary count and composition together, which is why this was never
     separable. Shares its answer with **OQ-CPTARRANGE** (now closed and
     archived in `docs/RESOLVED_QUESTIONS.md`), where the same
     four −4 rows are already recorded.
   - **C, `cptpow_*`** (12 files). `CPT(Dest,L0**L1+L2**L3)` is the only
     shape in the corpus that OVER-predicts (+16), and `**` is the only
     tier-3 operator (116 against tier 2's 52), so an error there costs 2–3×
     what one costs anywhere else in the table. Two `**` in one expression is
     untested, and `cptrdpow_k2/k3` (−848/−1648) say repeated `**` is badly
     wrong on the REAL-destination path too. Swept 1..4 `**` operators, alone
     and mixed with tier 1, at n=1 and n=100.


3. **OQ-AOIDEFSHAPE** — one unexplained 8 bytes in the AOI-definition cost.
    Opened 2026-09-13 (capture-batch segment 4), replacing the four separate
    fitted terms that used to absorb it. **54 files built, awaiting capture.**

    The definition cost is now one itemised form (`memory_model.yaml
    aoi_definition`):

        base 1163
        + 12 per declared member
        + that member's OWN data bytes (0 for a scalar BOOL, element x
          dimension for an array, the structure's size for a TIMER/STRING/UDT)
        + 24 per 32-bit word the declared BOOLs occupy, counting
          EnableIn/EnableOut as two further bits
        + the members' names, pooled with one byte per name and rounded up to 8
        + name_length_bytes(the AOI's own type name)

    Measured on 124 captured def-only files -- an AOI definition with no
    instance tag anywhere and no internal rungs, so the definition is the only
    AOI cost in the file and its true value reads straight off the capture.
    They span 1 to 128 declared members, six atomic types, BOOL fractions 0 to
    100%, and Input, Output and LocalTag usages. **70 of the 124 land exactly,
    122 of 124 within the project's ±8 band, worst 11.**

    Effect of wiring it, live-recomputed: corpus rows landing EXACTLY went
    **1,120 → 1,198** and rows inside ±8 went **1,690 → 1,907**. Per category,
    within 1%: `aoi_array_packing` **283/283** (was 35 of 283 inside ±8),
    `aoi` **160/160**, `axis` **61/61**, `driveaxis` **15/15**, `aoi_reqvis`
    **9/9**, `aoistructure` 105/110, `defscale` 60/69. On the sixteen real
    programs mean |error| 2.16% → **2.13%**, and `griffin_stackerline` went
    from 394 bytes out to **94** on 2.36 MB. The real-file residual also went
    one-sided: 14 of 16 now under-predict, where it used to be split.

    **What each superseded term was really measuring**, kept because every one
    of them fitted its own sweep exactly and was still the wrong shape:
    `per_declared_item: 20` was 12 + the 4 data bytes of the DINT every count
    sweep happened to use; `per_type_rate` (BOOL 16, SINT 18, INT 18, LINT 24)
    was the same 12 + own-size relation seen through the old linear name term;
    `member_name_char_bytes: 1` with 3 free chars was a pool rounded to 8
    misread as a per-character rate; and `aoi_member_type_extra`'s REAL 0,
    TIMER 8 and COUNTER 8 are exactly (own size − 4), with its
    sum-then-floor-to-8 shape an artifact of that mis-attribution. The
    mixed-versus-single-type split went with them: per-type rates "did not
    compose additively once BOOL sat alongside another type" because the
    name-pool error showed up as a composition effect.

    **WHAT IS LEFT.** A residual of exactly 0 on 70 of the 124 instrument
    files and exactly +8 on 35 more. It is not usage, not member count, not
    composition and not type. Three candidates remain and every captured file
    confounds at least two of them:

      1. **The AOI type-name bucket boundary.** The wired law
         `8*max(0,(len-8)//4) - 8` was fitted 7/7 on lengths 8, 9, 13, 16, 20,
         25 and 30, leaving 10-12, 14-15 and 17-19 unsampled. Two pairs
         differing only across those gaps disagree by exactly 8:
         `paramcount_n04_def_only` (13 chars) vs `_v2` (15) — the name is the
         ONLY difference in the whole file — and
         `aoidefcost_typeint_n08_def_only` (16) vs
         `paramtype_dint_n8_def_only` (14), same 8 DINT params, same member
         names, 8 bytes apart.
      2. **A fixed offset inside the name pool before it rounds.** On the
         `localcount_*` family the +8 appears exactly when the character total
         is congruent to 0, 6 or 7 mod 8 and not when it is 3 or 4, which is
         what an `8*ceil((chars + 4)/8)` pool would do. That fits all six
         localcount points and then contradicts `aoidefcost_typeint_n08`.
      3. **Member ORDER.** `aoi_boolpack_clean_alternating_def_only` (0) and
         `aoi_boolpack_clean_grouped_def_only` (+8) are the same 10 BOOL + 10
         DINT with the same member names in a different order.

    `base` is set to the value that centres the residual on zero for the
    124-file instrument (total absolute residual 316 bytes). A base 8 higher
    scores about 86 more exact rows corpus-wide and 53 more inside ±8, which is
    recorded here rather than taken: it makes the isolating instrument strictly
    worse, and it would bury the term this question exists to find.

    Two smaller things measured and deliberately not fitted, for the same
    reason: **STRING**'s old rate of 84 is 2 more than its 86 bytes minus 4
    (its capture, `altype_string_n00010_def_only`, reads −2 — inside the
    band), and **MOTION_INSTRUCTION**'s old 12 is 4 more than its 12-byte size
    predicts (`altype_motion_instruction_n00010_def_only` reads **+44**, the
    largest residual left in the array-localtag families).

    **Files built 2026-09-13, awaiting capture** —
    `src/sample_gen/gen_aoidefshape_closeout.py`, 54 files, every one def-only:

    - **A, `aoidshape_tname_len{08..32}`** (25 files). The AOI type name at
      every single length 8 to 32, with 4 DINT Input parameters named P0..P3
      held byte-for-byte identical, and **the controller name pinned to one
      fixed string across all 25** — which the existing `aoiname_len*` sweep
      did not do: there the project name tracked the AOI name, so a
      project-name cost was invisible. Reads candidate 1 directly at every
      length instead of at 7 of them.
    - **B, `aoidshape_pool_c{06..21}`** (16 files). Member-name character
      total growing one character at a time across two complete 8-byte residue
      cycles, with member count, types, data bytes and the type name all
      pinned. Only the pool's input moves, and every residue is read twice.
      Settles candidate 2.
    - **C, `aoidshape_count_n{01..08}`** (8 files). Member count 1 to 8 with
      single-character names, so the character total stays inside one 8-byte
      chunk for n=1..4 and the next for n=5..8. Separates the
      `localcount_n01` (0) vs `localcount_n02` (+8) step from the pool offset.
    - **D, `aoidshape_order_{boolsfirst,dintsfirst,alternating,pairs,
      blocks5}`** (5 files). 10 BOOL + 10 DINT in five arrangements with
      identical names and one pinned type name, so composition, count, pool
      and word count are identical by construction and any spread is
      candidate 3 and nothing else. The current engine predicts the same
      19,664 bytes for all five, which is what makes it a clean instrument.


4. **OQ-SAFETYSCOPE-SIZING** — Task/Program/Routine SHELL sub-thread
   **decided and wired 2026-09-03**: safety tasks and safety programs are
   a separate memory pool and need their own sizing calculation.
   `report.py` now excludes Safety tasks/programs/routines from the
   ordinary `task_program_shell` aggregate entirely and charges a new
   flat `safety_task_program_shell` (296 bytes/file, see
   `memory_model.yaml`) once per file with at least one Safety task
   instead, replacing the old +1,456-byte ordinary-shell overcharge.
   Live-verified against all 24 real L81ES-L84ES fwmatrix rows: exact (0
   delta) at fw v31-v33, a known +16-byte (0.087%) residual at v34-v38
   (real SafetyProgram MainRoutine content apparently drops to 0 bytes on
   that firmware; this engine still predicts a firmware-independent 16 —
   a separate, tiny, content-side gap, not a shell gap, well inside the
   <1% North Star, not chased further).

   **Still genuinely open, separate sub-thread, NOT covered by the above
   decision**: whether resolvable Safety-CLASSED TAG content (`DCI_STOP`,
   real corpus evidence, 80 bytes; `CONFIGURABLE_ROUT`, wired 52 bytes but
   Safety-family by name-root) should be sized at all. The tool already
   warns rather than refuses on a Safety-rated project
   (`is_safety_project`, cli.py/ui/server.py), but these two Safety-classed
   tag types are still left unsized by convention, not by any code that
   enforces the exclusion. the shell decision doesn't resolve this —
   it was specifically about Task/Program/Routine containers, not tag
   content. Still needs a call: exclude Safety-class tags from sizing
   everywhere by design (and wire that exclusion explicitly), or size
   everything resolvable including Safety tag content and adjust the
   warning wording.[^safetyscope]


5. **OQ-AOIARRAYLOCALTAG** (was the open sub-thread of
   OQ-AOIARRAYDIMENSION, whose import-failure thread closed 2026-09-03 and
   is now in RESOLVED_QUESTIONS.md) — an AOI array LocalTag's DIMENSION was
   unpriced. **All 27 sweep files were captured 2026-09-03 and never
   reconciled. Reconciled and the main term WIRED 2026-09-11; four smaller
   things stay open and are measured by a new 20-file batch.**

   `aoi_definition` charged `per_declared_item` once per declared member
   regardless of `dimension`, so an array member's data space cost nothing.
   Against a prediction that was FLAT at every dimension:

       DINT dim   10    50   100    250    500   1000
       deficit   -41  -201  -401  -1001  -2001  -4001

   Exactly `element_size x dimension`, and by element type at dimension 50:
   SINT 1.0/element, DINT and REAL 4.0/element. Definition-side only — every
   `_1_instance` twin carries the same deficit, so an instance does not pay it
   again. Now wired through `compute_array_size` (not element size x
   dimension: CAM_PROFILE is a predefined ARRAY structure with no scalar
   element size, real programs declare ten of them, and it raised
   `UnknownDataTypeError` on the first real file the new term met). 27 rows
   went from -41..-4001 to inside +-4 on 20 of them.

   **Exposure, measured before deciding how much to spend on it:** array
   LocalTags are ~17 KB across the sixteen real programs — **0.036%**, worst
   single file 0.058%. Real-file mean |error| moved 2.1733% -> 2.1504%. This
   category will never be the reason a real file misses 1%, and the 20-file
   batch below is sized accordingly. It exists because unexplained rows sit
   inside a category that otherwise measures exactly, which is how a wrong
   constant gets adopted — not because the bytes are large.

   **Still open, and `gen_aoi_arraylocaltag2.py` (20 files) measures each:**

     - **BOOL, deliberately left unpriced.** `BOOL[50]` measured -13, which
       fits neither the 7-byte packed size nor an 8-byte two-word rounding.
       `albool_n{1,8,16,32,33,50,64,65}` walks the packing boundaries. Real
       programs do declare BOOL array LocalTags (2, 64 elements).
     - **An 8-byte discount per array member after the first.** 1/2/3 arrays
       of 50 DINT measured 200/392/592, not 200/400/600 — 196 per array after
       the first. Two points cannot say whether that is linear;
       `almult_n{04,06,08}` settles it. After wiring, n02/n03 sit at +8.
     - **Structure element types, never tested.** The sweep covered five
       atomics. Two thirds of the real exposure is MOTION_INSTRUCTION (16
       arrays / 112 elements), CAM_PROFILE (10 / 100), STRING (4) and TIMER
       (2). `altype_*_n00010` prices one array of each of six structure types.
       The dimensioned-structure LocalTag shape (no `Radix`, no data body,
       unlike a dimensioned atomic which keeps `Radix="Decimal"`) was taken
       verbatim from the real exports before building any of them.
     - **The dim=25 outlier.** Every other dimension lands at -1 after
       wiring; 25 lands at +3 — four bytes, exactly one element, off the line
       through 10 and 50. The file's XML does declare `Dimensions="25"`, so it
       is not a generator bug. `aldim_n000{24,25,26}` re-measures it with its
       neighbours: either a real granularity effect near there, or the
       original row was a capture artefact.

   `INT[50]` at -99 against its predicted 100 is the fifth loose end and is
   covered by the same wiring note rather than a file of its own: the
   existing INT row already brackets it, and the multiplicity and neighbour
   arms above test the two mechanisms (a per-array term, or 4-byte
   granularity) that could produce it.

    **CLOSED 2026-09-14 (segments 25-28). 20 rows across four families, nineteen
    in or within 12 of the +-8 band, and the model needs no change.**

    - **`aldim_n000{24,25,26}_def_only`** -- array dimensionality is free:
      +4 / 0 / +4.
    - **`almult_n0{4,6,8}_def_only`** -- multiple array local tags are additive:
      +8 flat at all three counts.
    - **`altype_*_n00010_def_only`** -- per element type, all in band: CAM_PROFILE
      0, STRING -2, CONTROL / COUNTER / TIMER +4 each. **MOTION_INSTRUCTION is the
      one real gap at +44**, which is consistent with it being an unmodelled
      predefined structure (OQ-PREDEFINED) rather than anything about array local
      tags.
    - **`albool_n*_def_only`** -- +4 for n = 1..32 and +12 for n = 33..65. One
      8-byte step at the 32-bit word boundary and **no second step at 64**, so it
      is not a per-word term, and a single occurrence of a step cannot be
      generalised. 8 bytes, recorded not wired.



6b. **OQ-MODULESTRUCTURAL** — NEW, 2026-09-04, and it changes the target
   for OQ-MODULEIO below. The target application is testing an unknown
   file, and every catalog module number cannot be captured
   individually — the model has to tell that a 16pt digital
   card has XX overhead + 16pts of data, whereas a 8pt analog card has
   different overhead."*

   The per-catalog `module_overhead_by_catalog` table is the wrong shape
   for the real goal. It can only ever cover catalogs we have personally
   captured; a real customer file will contain catalogs we've never seen,
   and those silently fall back to one flat cross-catalog default (1,672)
   that is badly wrong for whole families (the 5069 family sits +28% to
   +35% under-predicted on that default). The table should become a
   FALLBACK for known-exact catalogs, not the primary mechanism.

   What's needed instead: predict a module's overhead from its own
   STRUCTURE, which is already in the L5X and already parsed. First look
   at the evidence, 2026-09-04:
   * A naive structural regression (constant + module count + connection
     input/output/config bytes + module_defined_bytes) over the 98
     error-free single-module `modulesweep_*` captures lands at MAE 845
     bytes / 3.84% mean — better than nothing but not close to the <1%
     target, because it lumps genuinely different module CLASSES (simple
     discrete I/O, analog, drives, safety, network bridges) into one
     linear model.
   * The missing variable is class, and Rockwell already states it: every
     module carries its own PROFILE string on its Input/Output/Config tag
     (`ModuleInfo.input_profile` etc., already parsed since 2026-08-27).
     `AB:1756_DI:I:0` is "1756 digital input", `AB:1756_DO:C:0` is
     "1756 digital output config", `AB:1734_8SLOT:I:0` is an 8-slot
     PointIO adapter, `AB:MotionDevice_Diagnostics:S:0` a drive. This is
     catalog-INDEPENDENT and exactly the "16pt digital vs 8pt analog"
     axis needed here -- 1756-IA16 and 1756-IB16 are different
     catalogs but both `AB:1756_DI`. Across the 98 valid files there are
     143 distinct profile strings resolving to a much smaller set of
     class tokens (DI, DO, IB, OE, OF, SLOT, ...).
   * Point count is recoverable the same way (the `_16` / `_8SLOT`
     numeric token, cross-checkable against the real connection byte
     counts already parsed).

   Proposed model shape, NOT yet fitted or wired:
       overhead = class_base[profile_class] + per_point[class] * points
                  + per_connection_byte * (in + out + cfg)
   fitted per class from the single-module captures, with the existing
   per-catalog table kept as an exact-match override where we have real
   data. This is the single highest-value remaining architecture change
   for the North Star, because it is what makes an UNSEEN catalog
   predictable at all.


    **THE CONCRETE CASE, found 2026-09-12.** Counting every non-CPU module
    across the sixteen real programs gives 438, and the largest single catalog
    by a wide margin is the GENERIC `ETHERNET-MODULE` profile at **109
    instances -- 25% of them**. It has NO entry in
    `module_overhead_by_catalog`, so all 109 fall back to the flat 1,672-byte
    cross-catalog default.

    A per-catalog constant is not merely imprecise for it, it is the wrong
    SHAPE. ETHERNET-MODULE is the profile used for any EtherNet/IP device with
    no AOP: the connection sizes are typed in by hand, so two instances of the
    same "catalog" are different devices. The 109 real instances carry **40
    distinct connection shapes**, primary input spanning **2 to 450 bytes** (a
    225x range) and output 2 to 64:

        x11  In  10  Out  4        x6   In  6  Out 2
        x10  In 450  Out  8        x5   In 12  Out 2
        x9   In   4  Out  2        x5   In  4  Out 6
        x7   In  64  Out 64        x4   In 14  Out 2
                                   x4   no connections at all

    Five more generic or third-party profiles are missing from the table on the
    same terms: `193-ECM-ETR/B` (20 uses), `PowerFlex 525-EENET` (12),
    `ETHERNET-BRIDGE` (8), `DPI-DRIVE-PERIPHERAL-MODULE` (6),
    `ETHERNET-PANELVIEW` (2). **161 of the 438 real modules -- 37% -- are
    priced by the flat default.**

    **The rack sweeps say the same thing from the other direction.** All 57
    `rack_*` rows captured clean, and none was ever reconciled. Recomputed
    2026-09-12, the per-module error FLIPS SIGN by family:

        1756 chassis cards   +523 per module (over-charged), max resid 1,436
        5069                 -992 per module (under-charged), max resid 5,831
        POINT I/O / Flex     -932 per card   (under-charged), max resid 3,008
        5069 singles          ~0 slope, but per-CATALOG residuals to 4,005

    Worst rows are `rack_pointio_n15_full` at **-27.8%** and
    `rack_5069_rand03` at **-25.4%**, while `rack_1756_n16_full` is
    **+11.8%** -- and `rack_5069_rand_combined10` (74 modules) flips to
    **+7.0%**, so it is not even monotone in count. A flat per-family constant
    does not absorb those residuals either. Those three families are only 14%
    of the real module population, so they are a large CORPUS error and a small
    real-file one; ETHERNET-MODULE is the reverse.

    **Test files built 2026-09-12, `gen_generic_ethernet_module.py`, 19
    files.** The module block is transplanted from a real instance; only
    identity and the swept size differ. Sizes are in BYTES and the connection
    data is INT-typed, so the array dimension is bytes/2 and the
    `AB:ETHERNET_MODULE_INT_<n>Bytes` type name carries the byte count -- all
    three move together in a real export, so they are derived from one number
    rather than settable apart and drifting out of agreement.

      - `genem_in{002..450}` (8) -- primary INPUT size swept
        2/4/10/32/64/128/256/450 bytes at output 4, bracketing the whole real
        range including both extremes.
      - `genem_out{002..064}` (6) -- primary OUTPUT size swept at input 4.
        Separates the two directions, which no real instance can do because
        real devices vary both at once.
      - `genem_n{01,02,04,08}` (4) -- OQ-MODULEMARGINAL's per-module question
        for the one catalog where it matters most on a real file.
      - `genem_dt{sint,int}_008` / `genem_dt{sint,int,dint,real}_064` /
        `genem_dt{sint,int}_450` (8) -- element DATA TYPE crossed with byte
        size, which nothing in the corpus can separate. Real generic modules
        use three element types (INT on 130 connections, SINT on 80, DINT on
        2) and the same byte size appears under different ones -- 450 bytes as
        SINT in 14 real instances, 64 bytes as INT in 14 -- but no real pair
        holds bytes fixed while the type changes. If cost follows ELEMENT
        COUNT rather than byte count, SINT and INT at one size differ by 2x
        and DINT/REAL by 4x: `genem_dtsint_450` declares 450 elements against
        `genem_dtint_450`'s 225 for the identical 450 bytes. The engine
        predicts an identical total for every file in this arm, so the whole
        captured difference is the type effect. REAL is the one type with no
        corpus instance -- a legitimate comm-format choice with mechanical
        `AB:ETHERNET_MODULE_<TYPE>_<n>Bytes` naming, so a conversion failure
        there would be a finding about the shape rather than the cost.
      - `genem_noconn` (1) -- the no-connection shape four real instances have.
        `zero_connection_module_bytes` (2,344, FITTED) claims to cover it and
        has never been tested for this profile.

    The engine currently charges **exactly 1 byte per connection byte** on top
    of the flat overhead (20,206 at input 2 rising to 20,654 at input 450), so
    the input sweep tests that claim directly and the 450-byte case -- ten real
    instances -- is where a wrong rate would show most.

    **CAPTURE ERRORS: none. RECAPTURED CLEAN, verified 2026-09-18.** The rows
    this entry used to flag as captured-with-errors now carry `error_count = 0`
    in the manifest, so their `actual_bytes` is trustworthy and every number
    above is drawn from clean captures. `scripts/capture_errors.py` routes no
    errored row here any more; the old block was a warning that had outlived
    its cause.


    **ETHERNET-MODULE SOLVED 2026-09-13 (capture-batch segment 7), which is the
    single largest slice of this question.** That profile is 109 of the 438
    non-CPU modules in the sixteen real programs — 25% of them — and had no
    entry in `module_overhead_by_catalog` at all, so every one fell back to the
    flat cross-catalog 1,672. A per-catalog constant was never the right SHAPE
    for it: the connection sizes are typed in by hand, and the 109 real
    instances carry 40 distinct connection shapes with input spanning 2 to 450
    bytes.

    **A connection's data costs 4x its declared bytes, not 1x.** Each direction
    is rounded up to a 4-byte word, the two word counts are summed, and the
    block costs 16 per word less 8 when that total is odd:

        W = ceil(input_bytes / 4) + ceil(output_bytes / 4)
        connection_bytes = 16 * W - 8 * (W % 2)

    | W | 2 | 3 | 4 | 5 | 9 | 17 | 33 | 65 | 114 |
    |---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
    | bytes | 32 | 40 | 64 | 72 | 136 | 264 | 520 | 1032 | 1824 |

    EXACT on all 14 points, with the catalog's own overhead at **1,592** and its
    400-byte config array charged as declared. **The two directions are
    interchangeable**, which no real instance could show because real devices
    vary both at once: `genem_in032`/`genem_out032` are byte-identical captures
    (20,256) and so are `genem_in064`/`genem_out064` (20,384). Only the sum of
    the word counts matters.

    20 of the 24 captured `genem_*` rows now land exactly, from none. Corpus mean
    absolute error 1.545% → 1.536%; the sixteen real programs 2.074% → **2.025%**.

    Scoped to this profile deliberately. The rack sweeps point the same way (5069
    −992/module, POINT I/O −932/card, both under-charged), so a 4x connection
    cost may well be general — but applying it to all 325 captured module rows on
    one profile's evidence is the move this project has had to undo before.

    **AND TWO OF THAT BATCH'S FOUR ARMS MEASURED NOTHING, both from the same
    root cause: a composed rather than transplanted module shape.** The
    generator hardcoded `CommMethod="536870915"` for every variant, and
    CommMethod ENCODES the comm format. Across 183 real ETHERNET-MODULE
    instances in `samples/local` the correspondence is unambiguous, with no
    counter-example:

    | CommMethod | connection element type | real instances |
    |---|---|---:|
    | 536870915 | INT | 109 |
    | 536870916 | SINT | 57 |
    | 536870932 | no connection at all | 11 |
    | 536870913 | DINT | 4 |
    | 536870914 | REAL | 2 |

    - **Arm E (`genem_dt*`, element type at fixed byte size).** The three SINT
      files FAILED conversion outright — `XMLSrv_E_IMPORT_ABORTED_NO_CHANGES`,
      `samples/convert_log.csv` 2026-09-12 — because the method said INT and the
      declared type said SINT. Worse, the DINT and REAL files imported and
      captured, and read byte-identical to `genem_dtint_064`: Studio resolved
      the contradiction from CommMethod and built all three as INT connections.
      That was briefly taken as evidence that cost follows byte count rather
      than element count. **It is not evidence of anything — all three files
      were the same connection.** Byte-count versus element-count remains OPEN.
    - **Arm D (`genem_noconn`).** Built as the connected method with the two
      PrimCxn size attributes simply removed. All 11 real no-connection
      instances use 536870932. The file captured "clean" and reads +3,976, which
      measures whatever Studio does with an inconsistent CommMethod.
      `zero_connection_module_bytes` (2,344) stays untested for this profile.

    Generator corrected and all six affected files rebuilt with the real
    per-type CommMethod. The three captures whose file content changed
    (`genem_dtdint_064`, `genem_dtreal_064`, `genem_noconn`) had their capture
    columns VOIDED in `samples/manifest.csv` rather than carried against a file
    they no longer describe; `genem_dtint_*` were already consistent and keep
    theirs. 6 files await recapture.

    **CONVERSION STATUS (step 2), logged explicitly:** 3 committed files with no
    `ok` on record — `genem_dtsint_008`, `genem_dtsint_064`, `genem_dtsint_450`,
    all `FAILED` with `XMLSrv_E_IMPORT_ABORTED_NO_CHANGES` on 2026-09-12. Cause
    diagnosed above, not guessed; fix applied.


6. **OQ-MODULEIO** — mostly closed 2026-08-29. 126 real module captures
   were sitting unreconciled in manifest.csv; 51 catalogs now have a real
   per-catalog overhead value (exact-match rate on real data went from
   1/126 to 54/126). Two real sub-threads remain, both needing
   architecture work not more generation: multi-module marginal cost
   (adding a 2nd/3rd of the same module doesn't cost the same as the
   1st), and a handful of catalogs with real connection-variant-dependent
   overhead.[^moduleio]


    **IN-DEPTH REVIEW 2026-09-18 — thirteen catalogs wired off isolation rows
    that had been captured and clean the whole time. Real set 1.6566% ->
    1.5611%, the largest single improvement of this review.**

    `modulesweep_*` is 96 single-variable rows and 54 of them sat outside ±8.
    Each measures one catalog on top of an adapter whose own row is separately
    captured, so the catalog's overhead falls straight out: 1,672 plus the
    file's residual, with the adapter's residual differenced out first. Thirteen
    catalogs derived that way are now in `module_overhead_by_catalog`, and every
    one of their isolation rows lands at **exactly 0** afterwards.

    Largest: PowerFlex 525-EENET +5,346, 1794-VHSC/A +4,280, PowerFlex
    755-EENET +2,436, 1794-IR8/A +2,311, 1734-IE4C/C +1,763.

    **THE THING THAT COST TWO WRONG DERIVATIONS, recorded so the next person
    does not repeat it.** `report.py` handles rack-aliased and zero-connection
    modules in a branch that `continue`s BEFORE `module_overhead_by_catalog` is
    ever consulted. An entry for such a catalog is inert. The first attempt
    wired twenty catalogs without checking which branch each took, and the
    isolation rows did not move; the second attempt read each module's charged
    bytes from the report and mistook `module_defined_bytes + overhead` for the
    overhead alone. Only the third — splitting the catalogs by branch first —
    produced entries that land their own rows at zero. **Check the branch before
    deriving a per-catalog constant.**

    **Six catalogs are measured and NOT wireable from this table**, because they
    take the rack-aliased branch: 1756-OW16I **+4,594**, 1734-8CFG/C +1,308,
    1794-IB16XOB16P/A +1,100, 1794-IA16/A +992, 1794-OA8/A and 1794-OW8/A +905
    each. Every rack-aliased module is charged the same flat 454 regardless of
    catalog (`rack_aliased_module`, wired earlier today), and these say the true
    cost varies by thousands between catalogs. **That flat 454 is an average
    over catalogs that genuinely differ, and it is the same finding as
    OQ-POINTIOCONN's per-card result seen from the other side.** Fixing it means
    giving the rack-aliased branch a per-catalog table of its own, which is a
    code change, not a constant.

    `1783-NATR` was wired and removed the same day: its isolation row did not
    move at all, so it reaches a bypass branch too, and its −2,344 is unfixable
    from here.

    **The caveat that matters, stated because one real file shows it.** Each
    constant is measured on a file containing exactly ONE module of that
    catalog, so it is the FIRST-instance cost. This table already carries a
    `repeat_bytes` discount for 16 catalogs measured the same way, and nothing
    measures one for these thirteen. `realprog_murraybros` carries FOUR
    PowerFlex 525-EENET drives and moves from +1.150% to −1.178% — an
    over-correction of roughly 10,600 across those four, which implies a repeat
    discount near 3,600 per additional drive. Elmsdale, with six affected
    modules of mixed catalogs, moves the other way and lands almost exactly:
    **+1.991% -> −0.247%**.

    **One file settles the discount**: `modulesweep_powerflex_525_eenet` at two
    and four drives, everything else identical. PowerFlex 525-EENET is 12 of the
    21 real occurrences of these catalogs, so it is the one worth measuring.

   **The marginal-cost sub-thread is closed 2026-09-13 (capture-batch segment
   14, 71 `asmclose_*` rows).** The law is `d x (n - 1)` per catalog, flat at
   n=1/2/4/8, and it is wired for the ten catalogs whose rate was measured on a
   shape real programs contain. 64 of the 71 rows land byte-exact with it
   applied against 16 without. Full derivation, the two deliberate exclusions,
   and the per-rack-vs-per-project measurement are in OQ-MODULEMARGINAL.

   Two of the 71 rows are not usable and their capture columns are now actually
   empty: `asmclose_1756_ob32_rackaliased_n02` and `_n04` shipped duplicate
   module names (the copier renamed only the first element of a 2-deep chain),
   so Studio merged the copies and the files measured N adapters sharing ONE
   output card at zero import errors. The 2026-09-11 note saying they had been
   cleared was written but **the values were never removed**, so both rows kept
   feeding every reconciliation for two days. `lint.duplicate_module_name` has
   caught this class since 2026-09-11, one day after these files were generated;
   `gen_assumed_closeout._place_copies` now renames every `<Module>` in a block
   and repoints each internal `ParentModule`, leaving references outside the
   block alone. `modmarg_ob32chain_*` is the correctly-built replacement and is
   captured.

   Four more are a different kind of bad read: `asmclose_al1222_1conn_n*` reads
   **18,128 at all four module counts**, distinct names, zero errors — the
   AL1222 modules never reached the controller. Left in place rather than
   cleared because the observation is consistent and reproduced at four counts,
   but nothing may be derived from them; see the corrected AL1222 note in
   OQ-MODULEMARGINAL.


    **CAPTURE ERRORS: 9 row(s)** flagged here by `scripts/capture_errors.py` (step 2b), 2026-09-11.
    Was 39. The other 30 went on 2026-09-14 when the 28 never-converted
    `modulesweep_*` files and both `modulerack_bender_full_program*` were
    DISCARDED -- see the conversion-status audit in `docs/TASKS.md`.
    12 captured WITH Studio build errors, so their `actual_bytes` is
    SUSPECT rather than wrong — part of the file may never have reached the
    controller, which inflates apparent over-prediction. None of them carries
    any error text: every errored row in the manifest was captured between
    2026-08-23 and 2026-09-08, and the error-log reader only began working
    2026-09-10, so these need RECAPTURE before their numbers are used.
    `modulemotion_d012_dual_axis`, `modulemotion_d012_single_axis`, `modulemotion_s086_safety_axis`, `modulerack_kinetix_full_bus`, `modulesweep_193_ecm_etr_a`, `modulesweep_193_ecm_etr_b` (+6 more)
    30 committed file(s) attempted and never reached `ok` in
    `convert_log.csv`: `modulerack_bender_full_program`, `modulerack_bender_full_program_r2`, `modulesweep_1734_ob8s_a`, `modulesweep_1734_ob8s_a_r2`, `modulesweep_1734_ob8s_b`, `modulesweep_1734_ob8s_b_r2` (+24 more)


7. **OQ-JSRPARAMCOST** — reopened 2026-08-29 for one small residual.
    Output/return-param call-site cost is now wired and confirmed
    (see RESOLVED_QUESTIONS.md). The callee's own one-time `A(n)`
    Parameters-block cost almost certainly ALSO needs an output-param
    term (real Parameters blocks include both Input and Output entries)
    — `jsr_multiret_n04` still off by +332 after the call-site fix, too
    small relative to a 1-distinct-target sample to isolate from noise.
    Needs a dedicated small file (2+ distinct targets with different
    output-param counts, input count held constant) to isolate A(n)'s
    real output term cleanly. 2026-08-30: `jsr_multiret_n02_r01000` came
    back within 0.09% (140/155,272), consistent with the wired call-site
    fix. But two NEW real, larger, param-TYPE-specific gaps showed up in
    the same push: `jsr_paramtype_string_n05_r00100` is off by +4,096
    (9.76%) and `jsr_paramtype_udt_n05_r00100` by +4,048 (9.78%) — both
    5-param/100-call files, both off by almost exactly the same amount,
    while the plain-DINT/REAL paramtype files in the same batch
    (`jsr_paramcount_*`, `jsr_paramtype_real_n05_r00100`) land within
    0.04%. Points at a real, currently-unwired per-call-site surcharge
    specifically for STRING/UDT-typed JSR parameters (not a flat A(n)
    definition-cost issue, since it scales with something in this file
    that plain-atomic-typed params don't have) — genuinely new, not yet
    derived.

    2026-08-31, real, structurally important: `report.py`'s `is_jsr_target`
    branch treats a JSR target's own logic content as fully absorbed into
    the flat `jsr_fixed_base_per_routine`/`A(n)` cost, `continue`s past it,
    and never weighs its instructions at all — confirmed 2026-08-22, but
    only ever tested against a trivial `SBR(...)NOP();RET();` stub target.
    Real AccuTally review (confidential, not committed) found 123 real
    JSR-target routines averaging 85 real instructions each (one has 201)
    — 10,488 total real instructions currently contribute $0. Built
    `jsr_target_content_scale_{010,050,100,150}` (target content as the
    only variable, 13-153 real instructions) to test this directly — the
    engine predicts the identical 19,452 bytes regardless of target size,
    proving the model treats content as irrelevant; awaiting real capture
    to prove whether that's actually true.

    **Real capture landed 2026-08-31 — confirmed, and cleanly linear.**
    File suffix is the real instruction count (010=10, 050=50, 100=100,
    150=150 instructions). Real deltas: n=10 → +76 (0.39%), n=50 → +800
    (4.11%), n=100 → +1,696 (8.72%), n=150 → +2,600 (13.37%) — escalating
    smoothly with content size exactly as hypothesized, proving JSR-target
    logic content is NOT free. Fitting `delta(n) = a + b*n` against the two
    most separated points (n=50, n=150) gives `b=18, a=-100`; checked
    against n=10 and n=100, both land within 4 bytes of that line (a clean
    4-point linear fit, no residual pattern left over). **18 bytes/
    instruction is suspiciously close to this project's own already-
    confirmed weighted-average instruction cost for ordinary routine
    logic** — consistent with the real fix being architectural, not a new
    formula: stop `continue`-ing past JSR target routines in `report.py`
    and weigh their instructions with the SAME per-instruction-type table
    already confirmed for every other routine, rather than treating target
    content as a special zero-cost case.

    **WIRED 2026-08-31.** `report.py`'s `is_jsr_target` branch now calls
    `compute_routine_logic_bytes(routine, model.logic_instructions,
    tag_types, charge_shell=False)` on the target's own content (using the
    REAL per-instruction weight table already confirmed for ordinary
    routines, not a new guessed 18/instr constant) and adds it to the A(n)
    entry, merged into one `logic_entries` tuple per routine path (two
    separate tuples sharing a path would have silently collided in any
    by-path grouping — caught and fixed before committing). `charge_shell=
    False` confirms the target still doesn't pay its own
    `fixed_base_per_routine` — that stays folded into the caller's
    `jsr_fixed_base_per_routine` as before. Re-validated against the real
    capture data with the new code: residuals dropped from 0.39%/4.11%/
    8.72%/13.37% (n=10/50/100/150) to **-0.81%/-2.13%/-3.47%/-4.75%** —
    max error cut from 13.37% to 4.75%, using only already-trusted
    weights, no new constant. `jsr_midchain_real_chain`/`_leaf_control`
    also improved: predicted delta went from 144 (old, wrong) to 276 (new),
    against a real delta of 332 — most of the previously-reported 188-byte
    "midchain" gap was actually THIS SAME target-content gap, not a
    separate outbound-call cost; only 56 bytes remain unexplained now (down
    from 188), too small to isolate a per-outbound-call rate from one data
    point. 3 pre-existing tests in `test_logic_sizing.py` had hardcoded the
    old (now-disproven) "target content is free" expectation — updated to
    the correct values, plus a new dedicated regression test
    (`test_jsr_target_content_scales_with_instruction_count`) added.
    Remaining small negative residual (grows to -4.75% at n=150) is a new,
    much smaller, separate open thread — not urgent at this magnitude.

    Same review also found `is_jsr_target` is checked BEFORE whether that
    routine itself makes further JSR calls (`continue`s immediately) — a
    routine that's both a target and a caller (mid-chain) has its own
    outbound call cost dropped too. 29 real AccuTally routines are
    mid-chain; one makes 10 real JSR calls of its own. Built
    `jsr_midchain_real_chain`/`jsr_midchain_leaf_control` to isolate this
    (predicted delta is 144, fully explained by the leaf's own A(2)
    declaration cost and nothing for the mid-chain call — any real delta
    beyond 144 proves the gap).

    **Real capture landed 2026-08-31 — the gap is real.** Predicted delta
    (real_chain minus leaf_control) = 144, as expected. Real delta = 332
    (19,068 vs 18,736) — **188 bytes beyond what the leaf's own A(2)
    declaration cost explains**, confirming a genuine, previously-
    unmodeled cost for a routine that is both a JSR target AND itself
    issues an outbound JSR call. Only one data point (a single real_chain
    file, one outbound call) — enough to confirm the gap is real, not
    enough to isolate a per-outbound-call rate yet; needs an n-scale sweep
    (2/5/10 outbound calls from the same mid-chain routine, matching the
    real AccuTally routine that makes 10) before this is wireable.

    **STRING/UDT per-call surcharge — extended 2026-08-31 with n=1/3/5
    disentangle points** (`jsr_paramtype_{udt,string}_n{01,03,05}_
    r00100_iso2`, 100 calls each, param count as the only variable). Real
    deltas: UDT n=1→+428 (1.5%), n=3→+2,448 (7.44%), n=5→+4,064 (10.89%);
    STRING n=1→+428 (1.5%), n=3→+2,464 (7.43%), n=5→+4,096 (10.81%). Two
    findings: (1) STRING and UDT deltas are nearly identical at every n
    (within 16-32 bytes) — the surcharge looks like a general "non-atomic-
    typed JSR param" cost, not type-specific. (2) It is NOT cleanly linear
    in n — fitting `a+b*n` off n=1/n=5 predicts 2,246 at n=3 against a real
    2,448 (202 off, 8.3% miss), a real, non-trivial deviation from a
    straight line. Genuine progress (3x the data of the original single-n
    anchor), but the functional form isn't nailed down yet — needs either
    one more n point or the exact per-call-site byte breakdown to
    distinguish a fixed-plus-linear form from something else before
    wiring anything.

    2026-08-31, real, caught reviewing the target-content-scale
    files: "if there was no jsr parameters then there is no sbr/ret
    instructions inside the called subroutine." Checked against all 8
    real customer L5X files in `samples/local/` (2,534 unique real JSR
    targets): 2,314/2,315 zero-param targets have NO SBR at all,
    2,218/2,315 (95.8%) have no RET either — essentially a hard rule.
    Every EXISTING JSR calibration file in this project uses nonzero
    params (1/5/7/8/9/10/15) and correctly includes SBR/RET (126/128 real
    nonzero-param targets DO have SBR, confirming that whole existing
    calibration set is representative). Only the two brand-new
    target-content-scale files (0 params) had this bug — fixed by
    removing the forced SBR()/RET(), now just ordinary logic rungs
    matching the real, dominant, previously-untested case (AccuTally: 77%
    of real JSR calls are 0-param, and all 103 of its real 0-param
    targets have zero SBR/RET, matching the corpus norm exactly).

    **IN-DEPTH REVIEW 2026-09-18 — every SLOPE in this question is now closed
    and wired. What is left is two flat constants.**

    The even-n paramtype files requested on 2026-08-31 have landed, so the
    non-atomic surcharge now has seven param counts instead of three, and the
    whole family was re-derived from scratch against the live engine rather
    than patched.

    **(a) The "non-linear" non-atomic surcharge was never non-linear. It was
    measured against the wrong baseline.** Subtracting each row's own
    atomic-param control at the SAME n — which the earlier pass did not do —
    gives:

    | n | atomic control | non-atomic | surcharge | − 800n |
    |---:|---:|---:|---:|---:|
    | 1 | −180 | +636 | 816 | 16 |
    | 2 | +220 | +1,836 | 1,616 | 16 |
    | 3 | +224 | +2,672 | 2,448 | 48 |
    | 4 | +224 | +3,472 | 3,248 | 48 |
    | 5 | +224 | +4,304 | 4,080 | 80 |
    | 6 | +224 | +5,104 | 4,880 | 80 |
    | 8 | +224 | +6,736 | 6,512 | 112 |

    That last column is exactly `16 + 32 × floor((n − 1) / 2)` at every one of
    the seven counts, with no residual at all. So

        surcharge(n) = 800·n + 16 + 32·floor((n − 1) / 2)     at 100 calls

    fits all 12 rows (7 UDT, 5 STRING) to the byte. The earlier "n=1 → 2.7
    bytes/param, n=3 → 7.7, n=5 → 7.9, something changes between 1 and 3"
    reading was an artifact: n=1's atomic control sits at −180 where every
    n≥2 control sits at +224, a 404-byte baseline shift that was being read
    as curvature in the surcharge.

    STRING and UDT agree to the byte at n=1, 3 and 5 despite an 88-byte
    STRING against an 8-byte 2-DINT UDT, so the cost is keyed on *non-atomic*
    and not on the operand's size. That is now three independent counts'
    worth of confirmation, not one.

    **NOT WIRED, and the reason is a genuine ambiguity, not caution.** Every
    non-atomic row in the corpus has exactly 100 calls, so `800n` is
    indistinguishable from `8 per param per call` (8 × 100) and from `800 per
    param, once per target`. The two readings differ by 100× on real files:
    the sixteen real programs carry **176 non-atomic JSR param operands**
    (resolved through UDT/AOI member chains — `CMU_TrayLayer` ×68, `PosnLug`
    ×32, `Board` ×12, `CMU_Discharge` ×12, `udtServo` ×10, `ts_CIPAxis` ×8,
    the rest in ones and twos), so per-call is **1,408 bytes across sixteen
    files** and per-target is **~140,800 — about 1.4% of the real set, in the
    direction the real set needs.** Wiring the wrong one either does nothing
    or moves the headline by more than a percent for the wrong reason. This is
    the single highest-value-per-file measurement left in the question, and it
    is three files: `jsr_paramtype_udt_n04` at r=10 and r=1000 against the
    existing r=100, plus one STRING r=1000 cross-check.

    **(b) B(n) is not affine in n, and the step keys on TOTAL operands.
    WIRED.** Solving for the per-call slope and the per-file constant
    separately — possible now that several param counts have two or three call
    counts — gives `residual(n, R) = p(n)·R + c(n)` with `p = 4, c = −176` for
    every n ≥ 3 at all three call counts: `4×10 − 176 = −136` (n=7/9/15),
    `4×100 − 176 = +224` (n=3/4/6/12), `4×1000 − 176 = +3,824` (n=5/8/10).
    Thirteen rows, call counts an order of magnitude apart, one pair of
    constants. n=1 is the control and is flat — −180 at both R=100 and
    R=1000 — so B(1) was already right and the step sits between 1 and 2.

    The step is keyed on `n_in + m_out`, not `n_in`, and the row that decides
    that is `jsr_multiret_n02_r01000`: 1 input, 2 outputs, 1,000 calls, which
    sat at **+3,952** and is the largest single residual this question ever
    had. Under the input-only reading n_in = 1 and no step applies. Keying on
    total operands takes it to **−56**, into the flat band with everything
    else. Wired as `jsr_param_cost.b_multiparam_extra: 4` with
    `b_multiparam_threshold: 2`. Zero-operand JSRs are untouched, which
    matters because 1,973 of the real corpus's 2,221 JSR calls pass nothing.

    **(c) A distinct JSR target costs 8 more than the model charged. WIRED.**
    With (b) in place the zero-param multi-target sweep's residual resolved to
    exactly `8t − 280`: −272, −256, −240, −200, −160, −120, +40, +120 at
    t = 1, 3, 5, 10, 15, 20, 40, 50 — **+8 per target at every step**, across
    two generators and name lengths 4 through 40 (the namelen rows are all
    identical, so this is not a name term; that law is already correct).
    `jsr_target_declaration.per_target` 152 → 160 flattens all thirteen rows
    to the same −280.

    **Real-set effect of (b) and (c) together: 1.6894% → 1.6753% mean absolute
    error, and all sixteen moved the right way.** Small, as it must be — these
    are tens of bytes per call site on megabyte files — but it is the right
    sign and it is measured rather than fitted.

    **What is actually left.** After (b) and (c) every slope in the JSR family
    is zero. Thirty-three captured rows reduce to two flat per-file constants:

    * **−184** on every param-bearing single-target file (16 rows: n = 1…15,
      call counts 10 / 100 / 1,000 — the constant does not move with either).
      −188 at n ≤ 2, a further 4-byte thread of its own.
    * **−280** on every zero-param multi-target file (13 rows).

    They differ by 96 and cannot be separated further here: every row in the
    first group has exactly one distinct target, so per-file and per-target are
    collinear, and the second group's targets have no SBR/RET at all (the
    confirmed real rule for zero-param targets). On a real megabyte program a
    200-byte file constant is 0.02%, so this is now the smallest thing in the
    project, and it stays documented rather than absorbed into `a_base` where
    it would be untraceable.

    Two small threads survive alongside it: `jsr_multiret_n04_r01000` sits
    +184 from `_n02` at the same call count and operand shape, which is the
    2 extra RET points in the target and wants a per-RET-point rate from a
    third point; and `jsr_midchain_real_chain`'s 56 bytes, unchanged, still
    one data point.


    **CAPTURE ERRORS: 4 row(s)** flagged here by `scripts/capture_errors.py` (step 2b), 2026-09-11.
    4 captured WITH Studio build errors, so their `actual_bytes` is
    SUSPECT rather than wrong — part of the file may never have reached the
    controller, which inflates apparent over-prediction. None of them carries
    any error text: every errored row in the manifest was captured between
    2026-08-23 and 2026-09-08, and the error-log reader only began working
    2026-09-10, so these need RECAPTURE before their numbers are used.
    `jsr_target_content_scale_010`, `jsr_target_content_scale_050`, `jsr_target_content_scale_100`, `jsr_target_content_scale_150`


8. **OQ-EVENTTRIGGER** — **the instruction half CLOSED 2026-09-17 and WIRED.**
    The EVENT instruction had no weight in the table at all and was charged
    zero. `uwclose_event_n{00010,00100,01000}` -- an EVENT task plus n rungs of
    `EVENT(EvtTask);`, nothing else varying -- reads 20,232 / 25,272 / 75,672
    against a flat predicted 19,664, so the under-charge is 568 / 5,608 /
    56,008: **exactly 56n + 8**, the 8 being the universal per-file residual.
    Three counts spanning 100x with zero residual, so KNOWN. Wired as
    `logic_instructions.weights.EVENT: 56`; all three rows now land at +8.

    The trigger-SOURCE half of this entry (what an EVENT task's own
    configuration costs, as against the instruction that fires it) is untouched
    and stays open below.

    task_extra (+700) was derived only
    from CONTINUOUS+PERIODIC tasks; EVENT-type tasks are completely
    untested, and so is trigger-source (Axis Watch vs. EVENT-instruction)
    within EVENT. Two files built, awaiting capture.[^eventtrigger]

    **`eventtask_instronly` real capture landed 2026-08-31 — the task-TYPE
    question is closed.** Predicted 19,600, real 19,600 — exact, 0.00%
    residual. `task_extra`'s existing formula (derived only from
    CONTINUOUS/PERIODIC before now) extends cleanly to an EVENT-type task
    with no separate term needed. Still open: `eventtask_axiswatch` (the
    trigger-SOURCE sub-question, Axis Watch vs. EVENT-instruction) has no
    real capture yet — that comparison is the only piece of this OQ still
    genuinely awaiting data.


    **CAPTURE ERRORS: 1 row(s)** flagged here by `scripts/capture_errors.py` (step 2b), 2026-09-11.
    1 captured WITH Studio build errors, so their `actual_bytes` is
    SUSPECT rather than wrong — part of the file may never have reached the
    controller, which inflates apparent over-prediction. None of them carries
    any error text: every errored row in the manifest was captured between
    2026-08-23 and 2026-09-08, and the error-log reader only began working
    2026-09-10, so these need RECAPTURE before their numbers are used.
    `eventtask_axiswatch`



11. **OQ-SERIESOUTPUT** — a rung with more than one output instruction in
    series. Opened 2026-09-13 (capture-batch segment 5), replacing the closed
    OQ-COMPOSITESCALE at this slot. **16 files built, awaiting capture.**

    **CAPTURE 2026-09-18, 25 files, all converted `ok`, all `error_count` 0.
    Kept short deliberately.**

    **Arm A, `sroutc_c{1,2,4}_k{1,2,4,8}` — THE RATIO HYPOTHESIS IS DEAD.** The
    grid is completely FLAT in condition count:

        per rung      k=1    k=2    k=4    k=8
        c=1             0    -12    -36    -84
        c=2             0    -12    -36    -84
        c=4             0    -12    -36    -84

    Identical to the byte at every one of the twelve cells. The discount is
    −12 × (k − 1) and condition count does not enter it. `sroutc_c01_k01` reads
    0, matching `srout_ote_k01` exactly, so the control holds.

    This was specified as "the decisive measurement for the whole project"
    because a condition/output RATIO was the one hypothesis that reconciled the
    synthetic families with the real ones. **It does not.** The law is now
    confirmed by a FOURTH independent family and all sixteen real programs still
    reject it (applying it: 1.70% → 3.22%, every file worse).

    **What is left, and it is now the only candidate.** Every generated file that
    shows the discount repeats ONE rung 1,000 times. Rung COUNT is excluded
    (200 and 1,000 give the same per-rung figure) and tag UNIQUENESS is excluded
    (`srout_oteuniq_k08`). What has never been varied is **rung IDENTITY within
    a file** — real ladder never repeats a rung, and no file in the corpus
    contains a multi-output shape where every rung differs.

    That is the same systematic corpus defect OQ-TAGORDER names at tag scope:
    **the corpus is uniform where real programs vary.** Two independent
    questions now point at it. A file of 1,000 DISTINCT 4-output rungs, against
    `sroutc_c01_k04`'s 1,000 identical ones, settles it and costs one file.

    **Arm B, `cpttri_k3_*` — the k=3 tier truth table is closed.** t211 and t221
    read 0, t212 reads +4/rung. `cpttri_pow_p3_adjacent` reads **+48/rung**:
    `**` adjacency is a real unmodelled effect, separate from operator count.

    **Arm C, `stc2_*` — THE FALSIFICATION TEST PASSED.** These are the six
    2-operator midpoints specified to over-determine the ST constants wired from
    single points earlier the same day. Four of six land at exactly **0**:
    `and`, `or`, `xor` at two operators, and both all-float rows
    (`premreal2_mul`, `premreal2_pow`). So the bitwise premium of 0 and the
    all-float premiums of 0 and 8 hold at a second operator count and are no
    longer single-point. Only `stc2_prem2_pow` is off, at +28/rung — the DINT
    `**` premium of 38 is right at four operators and not at two.

    **Arm D, `cptnar_j*` — narrowing is badly wrong on mixed-width shapes**:
    +88, +204 and +120 per rung. OQ-CPTNARROW's `rate_T × k − 132` was derived on
    uniform-width operands and does not survive mixing. Real exposure is still 27
    calls in one program, so this stays unwired.

    Two captured single-shape sweeps say the engine over-charges by exactly 12
    bytes per output instruction beyond the first in a series cascade:

        UID()UIE();                                      2 outputs  −12.000/rung
        XIC(Bit0)MOV(1,Dst0)ADD(Dst0,1,Dst0)OTE(Bit1);   3 outputs  −24.000/rung

    Both slopes are exact across three orders of magnitude of rung count. The
    one-output controls are exact too — `XIC(B0)OTE(B1);` reads 0 over 1,000
    rungs, and `MOV(0,D0);`, `ADD(D0,D1,D2);` and `OTE(B0);` each read the
    universal +8 at 10 through 5,000 rungs — so the per-instruction weights are
    right in isolation and something about the cascade is not. Parallel branch
    legs are already known exempt: `[XIC(B0),XIC(B1)]OTE(B2);` is 0, and
    `branchdepthc_legs30_n01000` carries 30,000 extra instructions at exactly 0.

    **IT IS NOT WIRED, AND MUST NOT BE FITTED, because the real programs reject
    it.** Applying −12 per extra series output takes the sixteen held-out
    programs from 2.07% to **2.90%** mean absolute error and makes every single
    one of them worse — they already under-predict and this predicts less.
    Counting outputs at bracket depth 0 only (branches exempt) gives the same
    2.90%; counting branch contents as well gives 4.51%. So the law is exact on
    two generated shapes and wrong on the only files that count, which means
    something those two shapes share is absent from real ladder.

    Four candidates, none separable in the existing corpus:

      1. The count may not be linear at 12 — two points cannot tell 12-per-extra
         from "12 for the second output and nothing after", or from a cap.
      2. Every rung in both sweeps is BYTE-IDENTICAL thousands of times over,
         addressing the same operands. Real rungs differ. One-output shapes are
         exact under the same repetition (`instr_mov_n05000` is 5,000 identical
         rungs), so repetition alone is not it — repetition *plus* a cascade is
         untested.
      3. Series versus parallel at matched output counts, which nothing in the
         corpus does.
      4. Repeated instruction type versus distinct types within the rung.

    **Files built 2026-09-13** — `src/sample_gen/gen_seriesoutput_closeout.py`,
    16 files, every shape built from instructions whose isolated weight is
    already confirmed exact:

    - **A, `srout_ote_k{01..08}_n01000`** (8 files). One XIC condition and k OTE
      outputs in series, each to its own bit. Eight consecutive counts read the
      shape of the law instead of two points on it.
    - **B, `srout_oteuniq_k{02,04,08}_n00200`** (3 files). The same cascade with
      every rung writing its own distinct bits, so no two rungs are identical
      and no tag is addressed twice. Tests candidate 2 against group A directly.
    - **C, `srout_branch_k{02,04,08}_n01000`** (3 files). The same k outputs in
      parallel legs, same tags, same rung count — candidate 3 at matched counts.
    - **D, `srout_mixed_k04_n01000`** vs **`srout_same_k04_n01000`** (2 files).
      Four outputs of four different types against four OTEs — candidate 4.

    **TWO MORE POINTS AND ONE CANDIDATE ELIMINATED, 2026-09-13 (capture-batch
    segment 8, `ntag_*`).** The law is now measured on THREE independently
    generated shapes at three different output counts, all exact:

    | shape | outputs | per rung |
    |---|---:|---:|
    | `UID()UIE();` | 2 | **−12** at n = 1, 10, 100 and 1,000 |
    | `XIC(Bit0)MOV(1,Dst0)ADD(Dst0,1,Dst0)OTE(Bit1);` | 3 | **−24** at n = 400 and 4,000 |
    | `UID()XIC(B0)OTE(B1)MOV(D0,D1)UIE();` | 4 | **−36** at n = 100 |

    −12 × (outputs − 1) at 2, 3 and 4 outputs, nothing fitted to get there.

    **Candidate 2 — identical-rung repetition, or deduplication — is DEAD.**
    `ntag_uidpair_n00001` is a ONE-RUNG file and pays the full −12. There is no
    repetition in a one-rung file, so the discount cannot be amortisation of a
    repeated structure. That was the candidate I thought most likely, and group B
    of the built batch (`srout_oteuniq_*`) existed to test it; it is answered
    without capture.

    **Candidate 4 — repeated versus distinct instruction types — is badly
    weakened.** The `withbody` rung's four outputs are four DIFFERENT
    instructions (UID, OTE, MOV, UIE) and it pays exactly 12 per extra, the same
    rate as `UID()UIE();`'s two distinct ones. The law does not care about type
    distinctness.

    So: the discount needs no repetition, ignores instruction type, exempts
    parallel branches, and is exact at three output counts on three shapes — and
    the sixteen real programs still reject it outright (2.07% → 2.90% even
    counting series-only outputs at bracket depth 0).

    **JOINT HYPOTHESIS WITH OQ-REALUNDER, and it makes both coherent.** That
    entry's differencing puts the real-file residual on compiled logic, with
    `residual / routine_logic_bytes` bimodal — eleven programs 9% to 22% SHORT.
    If the −12 discount is in fact real and universal, then real ladder's true
    under-charge is LARGER than 9–22%, and applying only the discount makes real
    files worse precisely because the bigger positive term is still missing. One
    unpriced positive term in real ladder explains both observations; two
    independent errors of opposite sign in the same category does not.

    That makes `strip_ladder.py`'s **L2 rung — minus all rung and ST content —
    the decisive measurement for this entry too**, not just for OQ-REALUNDER.
    Nothing further should be fitted here until it is captured.


11b. **OQ-UDTTAGSLOT** — is a standalone UDT tag's data slot padded to 8 bytes?
    Opened 2026-09-13 (capture-batch segment 5). **WIRED, and thin. 52 files
    built, awaiting capture.**

    Two captured families disagreed about what one UDT-typed tag costs, and only
    because they sit on opposite sides of an 8-byte boundary:

        dscale2_udt_u001_t001..t500   9-byte UDT, 1 to 500 tags   EXACT (14/18 rows 0)
        addit_dm_ln / addit_dh_ln    40-byte UDT, 40 and 400 tags −7.000/tag, exact slope

    One hypothesis fits both with zero residual: pad a standalone (non-array)
    UDT tag's DATA slot up to 8 — 40 stays 40, 9 becomes 16 — and set
    `definition_scale_correction.udt_tag_extra` to −4 rather than the +3 that
    held for as long as only the 9-byte family existed. Both are wired
    (`memory_model.yaml standalone_udt_tag_slot`); corpus mean absolute error
    1.853% -> 1.841% and the `udt` category picked up 7 more rows inside ±8.
    It is the same kind of per-TAG slot rule as the already-KNOWN
    `standalone_atomic_tag_slot` of 4, one level up.

    **Why it stays open**: the padding constant and the −4 are not separable
    from either family alone, and the whole corpus contains exactly TWO UDT
    sizes that bear on it, 9 and 40 — a two-parameter hypothesis fitted to two
    points, one on each side. That is the shape of fit this project has had to
    undo four times in the AOI-definition cost alone.

    **A second reading, recorded rather than fitted**: padding the UDT ELEMENT
    size instead of the tag slot improves the sixteen real programs *more*
    (2.13% -> 1.88%) but costs the `tags` category its accuracy outright (0.27%
    -> 2.03% mean absolute error) and is flatly contradicted by
    `dscale2_udt_arr002/arr010/arr100/arr500`, which read +1 at every length
    against a 12-byte 4-aligned element. So that real-file gain is absorbing
    some other missing term and must not be spent here — see OQ-REALUNDER.

    **Files built 2026-09-13** — `src/sample_gen/gen_udttagslot_closeout.py`,
    52 files, 8-character tag names throughout so the `tag_overhead` bucket
    never moves:

    - **A, `udtslot_s{01..16}_t{050,400}`** (32 files). A UDT of k SINT members
      for k = 1..16, packing to exactly k bytes, at 50 and 400 tags. Every
      residue mod 8 twice, on both sides of the boundary, with the per-tag cost
      read as a slope 350 tags apart rather than a single count.
    - **B, `udtslot_d{01,02,03,04,05,06,08,10}_t{050,400}`** (16 files). DINT
      UDTs of 4 to 40 bytes — says whether the step is really at 8 and not at 4,
      and the 40-byte point reproduces the additivity D axis as a cross-check.
    - **C, `udtslot_arr_s{03,05}_n{050,400}`** (4 files). Arrays of the 3- and
      5-byte UDTs — the first array arm that can see an element-padding rule at
      two different residues.

    **FOUR NEW POINTS 2026-09-18, and one long-standing candidate is DEAD.**
    The `rshape_pack_i*` files were built to isolate a per-rung term and
    instead landed squarely on this law, because they pack OTEs — output
    instructions — more densely per rung. Extra series outputs and the
    rung-count drop are the same number in that design, so the files cannot
    say which of the two they measured; see the confound note in
    `OQ-RUNGSHAPE`. What they CAN say is what the value is, and it is −12 at
    four fresh points:

    | file | rungs | OTE/rung | extra outputs | delta | per extra output |
    |---|---:|---:|---:|---:|---:|
    | `rshape_pack_i02` | 2,000 | 2 | 2,000 | −24,000 | **−12.000** |
    | `rshape_pack_i04` | 1,000 | 4 | 3,000 | −36,000 | **−12.000** |
    | `rshape_pack_i08` | 500 | 8 | 3,500 | −42,000 | **−12.000** |
    | `rshape_pack_i16` | 250 | 16 | 3,750 | −45,000 | **−12.000** |

    `rshape_pack_i01`, one OTE per rung and therefore no cascade at all, is
    byte-exact. The law now holds at k = 2, 3, 4, 8 and 16 across three
    unrelated shapes, and **candidate A is settled**: it is linear at 12 per
    extra output, not a one-time step and not capped, out to fifteen extra
    outputs in a single rung.

    **CANDIDATE B IS DEAD, and it was the leading explanation.** The entry
    argued that both original sweeps repeat a BYTE-IDENTICAL rung thousands of
    times over the same operand tags, and that real ladder never does — so
    deduplication of repeated rung structure, not a genuine layout rule, might
    be what the −12 measures. **Every rung in the `rshape_pack_*` files writes
    its own distinct bits** (`B0000`…`B3999`, each addressed exactly once), so
    no two rungs are identical and no tag is addressed twice. The discount
    survives at exactly −12. It is a real per-output layout rule, not an
    artefact of repetition.

    That sharpens the paradox rather than resolving it: a law now exact at
    five counts across three shapes, with rung uniqueness ruled out, is still
    rejected by all sixteen real programs (applying it takes mean absolute
    error from 2.07% to 2.90% and makes every one of them worse). Candidates C
    and D — series versus parallel at matched output counts, and repeated
    versus distinct output TYPES — remain the open ones, and the
    `srout_branch_*` and `srout_mixed/same` files that test them are still
    uncaptured.



12. **OQ-AOIINTERNALLOGIC** — new, real, corpus-wide gap, found 2026-08-31:
    AOIs were closed out without ever putting logic inside one. Every AOI
    has at least one internal subroutine and can have more (HomeToTorque
    is the real example).
    `aoi_xml()` (builders.py) has hardcoded a self-closing
    `<Routine Name="Logic" Type="RLL"/>` for EVERY AOI test file this
    project has ever generated — $0 real internal-logic content has ever
    been exercised in ANY AOI calibration file, and the shared builder
    never supported more than one internal routine. The existing
    `aoi_definition` formula (base + per_declared_item*count +
    name-length term) is purely a Parameter/LocalTag declaration-cost
    model — it has never been tested against real Logic-routine content
    or a second internal routine, both of which are common in real AOIs.
    Real confidential-project review (not committed, never named beyond
    this generic description) confirms this is a real, material gap: 39
    real AOI definitions there have 573 total real rungs of internal
    logic (111,507 chars) — 100% currently unsized anywhere in this
    project — and 8 of the 39 have 2 internal RLL routines, not 1 (e.g.
    HomeToTorque: Logic 21 rungs + EnableInFalse 1 rung). Fixed the
    builder (`logic_rungs_xml`/`extra_routines_xml` params, both default
    `""`, confirmed byte-identical output for every existing caller) and
    built `aoi_logic_scale_{000,010,050,100}` (Logic-content-scale sweep)
    plus `aoi_multiroutine_control`/`aoi_multiroutine_real` (mirrors
    HomeToTorque's real 2-routine shape exactly) — all 6 predict the
    identical 19,440 bytes regardless of Logic content size or
    second-routine presence, confirming both are currently zero-weighted.
    Awaiting real capture; if either scales with real Capacity, this is a
    second, independent, currently-unmodeled cost category on top of
    OQ-JSRPARAMCOST's target-content finding — real AccuTally logic
    content (routine + AOI-internal combined) may be substantially larger
    than this project has ever priced.

    **Real capture landed 2026-08-31 — confirmed, AOI internal logic
    content is NOT free, and multi-routine vs single-routine content of
    the same size costs the same.** All 6 files share predicted 19,440
    (the model still doesn't weigh AOI-internal logic at all). Real
    results: `aoi_logic_scale_000` (0 rungs) → 19,440, exact 0.00% —
    confirms the empty-shell baseline itself is right. `_010` → 19,676
    (+236, 1.21%), `_050` → 20,620 (+1,180, 6.07%), `_100` → 21,776
    (+2,336, 12.02%) — a clean, escalating, real cost that scales with
    logic-content size, same shape as the JSR-target-content finding
    above. `aoi_multiroutine_control` (HomeToTorque's real 2-routine
    shape, same total content as `_050`) reads the exact same 20,620 as
    `_050` — **splitting the same content across 2 internal routines
    instead of 1 costs identically to keeping it in one routine**, so the
    per-routine count itself isn't a separate cost driver, only total
    content is. `aoi_multiroutine_real` (the literal HomeToTorque content,
    not a synthetic same-size stand-in) reads 20,912 (+1,472, 7.57%) —
    close to but not identical to `_control`, the gap presumably from real
    instruction-mix differences (HomeToTorque's real rungs vs the
    synthetic control's), not the routine-count structure. **Architectural
    conclusion: AOI internal Logic-routine content should be weighed with
    the same per-instruction model as ordinary routine logic (same fix
    direction as the JSR-target-content finding above), not treated as
    zero-cost; the per-routine-count dimension can be dropped from the
    model entirely — real data shows it doesn't matter.**

    **WIRED 2026-08-31.** New `parser/logic.py` function,
    `parse_aoi_internal_logic()`: walks `Controller/
    AddOnInstructionDefinitions/AddOnInstructionDefinition/Routines/
    Routine` for every AOI definition and aggregates ALL of its internal
    RLL routines' rung text into ONE pseudo-`RoutineLogic` per AOI name
    (deliberately not tracked per-routine, matching the confirmed "routine
    count doesn't matter" finding). `report.py`'s AOI-definition-cost path
    now calls `compute_routine_logic_bytes(..., charge_shell=False)` on
    that aggregate and adds it to the existing param/localtag declaration
    cost (`AoiDefinitionModel` untouched — confirmed via the n=0 file
    landing at an exact 0.00% match, so no double-counting). Re-validated
    against real data: residuals dropped from 0.00%/1.21%/6.07%/12.02%
    (n=0/10/50/100) to **0.00%/0.00%/-0.29%/-0.55%** — essentially exact
    at every point tested, max error cut from 12.02% to 0.55%.
    `aoi_multiroutine_control` (2 internal routines, same total content as
    `_050`) now predicts identically to `_050` as designed (-0.29%);
    `aoi_multiroutine_real` (literal HomeToTorque content) lands at +1.02%,
    a small real instruction-mix difference, not a routine-count effect.
    **Checked against `gen_composite_realistic.py`'s AOI calls: this fix
    does NOT move the composite batch's ~3% residual at all** — that
    generator still uses the old hardcoded self-closing `<Routine
    Name="Logic" Type="RLL"/>` shape (never updated to use `aoi_xml()`'s
    new `logic_rungs_xml` param), so its AOIs have zero internal content to
    weigh either way. **Correcting the composite-residual hypothesis
    written earlier in the same pass** (see OQ-COMPOSITESCALE below): neither
    this fix nor the JSR-target-content fix explains the composite
    batch's residual, since composite files don't currently exercise
    either gap — that residual's real source is still unidentified.

    **REOPENED 2026-09-12. The wiring above is validated against SUSPECT
    rows, and the files were gone.** All six calibration files had been
    deleted from the repo entirely, so nothing could be re-examined, and
    **five of the six captured WITH Studio build errors**:

    | file | recorded `error_count` |
    |---|---:|
    | `aoi_logic_scale_000` (empty shell) | 0 |
    | `aoi_logic_scale_010` | 1 |
    | `aoi_logic_scale_050` | 8 |
    | `aoi_logic_scale_100` | 16 |
    | `aoi_multiroutine_control` | 8 |
    | `aoi_multiroutine_real` | 8 |

    No error text was ever recorded. The count rises with rung count, so a
    repeating rung shape in the generator's 5-shape mix is being rejected
    while Studio imports the rest of the project — which is the worst case,
    because `actual_bytes` still gets filled in from a project missing part of
    the logic it was built to measure. Per CLAUDE.md that makes every one of
    those rows **suspect, not wrong**, and it points one way: the measured
    bytes UNDER-state the real cost, so the per-instruction weighting fitted
    to them is likely **under-charging AOI internal logic**. The headline
    "essentially exact at every point tested, max error cut from 12.02% to
    0.55%" is an exactness against those numbers. Only `aoi_logic_scale_000`,
    the zero-logic baseline, is clean — and that file contains no AOI internal
    logic at all, so it validates nothing about the weighting.

    This matters at real scale: the same real program reviewed above has 39
    AOI definitions carrying 573 rungs of internal logic between them.

    The six files are **rebuilt** and now exist again. The gate reports all
    five errored rows as STALE — the rebuild does not reproduce the captured
    content byte-for-byte, because the shared builder has moved since — so
    their `actual_bytes` describes content the repo no longer holds and cannot
    be used even with a caveat. They need recapture.

    **One diagnosis was tried and is recorded here because it is WRONG.** The
    suspect shape looked like `MOV(In0,In1)`, on the theory that an AOI's
    Input parameters are read-only inside its own logic. They are not. Real
    shipping AOIs write to their Input parameters routinely —
    `MOV(RawInput,RawMax)`, `OTU(HMI_ResetStats)` in the real corpus — because
    an Input is a local copy made at invocation, not a reference; only InOut is
    by-reference and only Output flows back. A lint rule built on that premise
    fires on 133 committed files including all four real production programs,
    which demonstrably compile. It was written, tested, and reverted.

    Counting shape occurrences does not settle it either. The mix cycles 5
    shapes, so at 13/42/78 rungs each shape appears a known number of times,
    and **no single shape appears 1, 8 and 16 times**: `CLR(Loc0)` appears
    8 and 16 at n=50/100 but 3 at n=10; `MOV(In0,In1)` appears 2, 8 and 15.
    Either the error is not one-per-rung, or more than one shape is involved.

    **17 files built to measure it instead of inferring it**
    (`src/sample_gen/gen_aoi_internal_shape_isolation.py`):

    - **`aoishape_{mov,xicote,clr,add,equote}_n{01,05,10}`** (15 files). Each
      of the five mix shapes alone in an AOI's Logic routine, at 1/5/10 rungs,
      same 3 In / 1 Out / 2 Local parameter shape as the captured sweep. The
      recorded error count then names the offender directly: a shape rejected
      once per rung shows its count tracking the rung count in its own three
      files and zero in the other twelve. Shapes are verbatim from the captured
      mix, `MOV(In0,In1)` included — changing them would measure a different
      question.
    - **`aoishape_control_empty`** — zero internal logic, current builder
      output. Separates a rung-shape cause from the surrounding project
      structure: if this errors too, no rung is at fault.
    - **`aoishape_control_mix13`** — the same 13 mixed rungs
      `aoi_logic_scale_010` carries. Its error count is directly comparable to
      that row's recorded 1 (its bytes are not — a different AOI type-name
      length carries its own cost).

    If every one of the 17 comes back at zero errors, the cause was in project
    structure the sweep has since changed, and the next step is **the raw
    Studio 5000 error-log line** for one of the original six files rather than
    another round of inference.

    **CAPTURED 2026-09-14 (segment 15). All 17 at ZERO errors, the 13-rung mix
    included. No rung shape is at fault**, so that condition is met: the original
    five errored rows were broken by the surrounding project structure, and the
    next step is the raw Studio error-log line. Two rounds of shape inference
    have now been tried and both were wrong; there is no third.

    **The calibration question this was protecting is answered. The AOI-internal
    weighting under-charged by exactly 4 bytes per instruction that WRITES A
    NON-BOOL DESTINATION. Wired 2026-09-14, KNOWN.**

        aoishape_{mov,add,clr}_n{1,5,10}    +4 per rung
        aoishape_{xicote,equote}_n{1,5,10}   0 at every count
        aoishape_control_empty               0
        aoishape_control_mix13              +32 on 8 word destinations
        aoistr_scale_rung_n{011..085}       +4 per rung, 7.7x span
        realscale_aoiint_n{0..12000}         0 through 12,000 instructions

    MOV/ADD/CLR write a DINT, OTE writes a BOOL, EQU and XIC write nothing. ADD
    at three operands, MOV at two and CLR at one all cost the same +4, so it is
    not per-operand. `control_mix13` is the additive cross-check on a mixed file:
    3 MOV + 3 CLR + 2 ADD = 8, residual 8x4 exactly. All 27 rows across the five
    families are byte-exact with it wired.

    **This explains `aoi_internal_per_rung`** — the 4 bytes/rung measured
    2026-09-10, which looked perfect and was rejected for making the 122-file
    `aoi` family four times worse. Right number, wrong carrier:
    `aoistr_scale_rung`'s rungs are `XIC(EnableIn)MOV(In0,In1);`, **one MOV
    each**, so per-rung and per-word-destination coincide on that family and
    nowhere else. Both readings that note was stuck between are dead — per-rung
    requires xicote/equote to cost 4 (they cost 0), and per-instruction-at-2
    requires a 2-instruction rung to cost more than a 1-instruction rung (the
    split is the other way round).

    **Negative control: PROGRAM routines are unaffected.**
    `instr_{mov,clr,add,equ,xic,ote}_n{10..5000}` all sit at the universal +8
    per-file residual — the same 8 for every instruction at every count to 5,000.
    The weights are already right outside an AOI. `word_destination_count` is
    populated by `parse_aoi_internal_logic` only and stays 0 for
    `parse_rll_routines`.

    Real set 1.6289% -> **1.6051%** mean, +1.2579% -> **+1.1797%** sum-weighted;
    corpus byte-exact 1,220 -> 1,235. `composite` gets worse, 1.663% -> 1.682%,
    recorded rather than hidden — it is the family whose own generator defects
    are still open.

    **Still open here:** segments 30/31 (`aoi_logic_scale_*`,
    `aoi_multiroutine_*`) need recapture and are now a TEST of this law rather
    than an input to it. `_DESTINATION_ARG` in `parser/logic.py` covers 42
    mnemonics; MOV/ADD/CLR are measured and the rest are classified from
    documented operand order, so a mnemonic whose destination sits elsewhere
    would be mis-charged by 4. Real AOI-internal inventory, corrected 2026-09-18:
    38,821 instructions across ALL sixteen programs, of which 9,291 are charged
    and 6,963 of those are the measured three. (The "11,241 across 6 of the 16"
    written here previously was wrong -- see the in-depth review below.)

    **IN-DEPTH REVIEW 2026-09-18 — the `_DESTINATION_ARG` exposure is now
    MEASURED instead of feared, and it is an order of magnitude smaller than
    this entry claimed. Two real defects in the table were found and fixed.**

    The open worry above was that 39 of the 42 mnemonics are classified from
    documented operand order rather than captured, so a mis-classified one is
    charged or spared 4 bytes on no evidence. That worry was never sized. It is
    now, by inventorying every AOI-internal instruction in all sixteen real
    programs against the table:

    | | instructions | bytes at 4 each |
    |---|---:|---:|
    | total AOI-internal | 38,821 | — |
    | charged the surcharge | 9,291 | 37,164 |
    | of those, MEASURED (MOV/ADD/CLR) | 6,963 | 27,852 |
    | of those, classified but NEVER measured | **2,328** | **9,312** |

    So the entire unmeasured exposure across the whole held-out set is **9,312
    bytes, about 0.09%** — and that is the figure for every one of those
    classifications being wrong at once, in the same direction. The largest
    single one is DIV at 538 instructions (2,152 bytes); CPT 471, SUB 372,
    MUL 350, COP 206 and then a tail of 14 mnemonics under 110 each. **No test
    batch for this is justified ahead of anything that moves a percent**, which
    is the disposition this thread should have had all along, and the number is
    recorded here so the question is not reopened on vibes.

    Correcting this entry's own arithmetic while here: it said "11,241
    instructions across 6 of the 16 programs". The real figure is **38,821
    across all sixteen** — every real program has AOI-internal logic, from
    1,315 (emporiumedger) to 4,124 (accutally). The old number was counting
    something narrower and was being used to argue the exposure was larger than
    it is.

    **Defect 1, fixed: five entries named the wrong operand.** COP, CPS and FLL
    are `(Source, Dest, Length)` and BSL/BSR are `(Array, Control, Source,
    Length)`, so the table's `-1` inspected the LENGTH operand. It charged the
    right total anyway — a literal length does not resolve to BOOL, and the
    unresolved default is a word — so it was right for the wrong reason and
    would have started charging a BOOL-destination COP the moment a length was
    a tag. Now explicit: `COP/CPS/FLL: 1`, `BSL/BSR: 0`. 300 real instructions
    read the correct operand; the predicted total does not move, which is the
    expected result and the reason this was invisible.

    **Defect 2, fixed: five word-destination writers were missing entirely.**
    The same inventory lists every mnemonic charged nothing, and `GSV` is in it
    — 363 real occurrences of an instruction whose whole purpose is to read a
    controller attribute INTO a tag. With MVM, SCP, SIZE and AVE that is 453
    real instructions that write a word and were charged zero. Added on the
    same documented-operand-order basis as the other 39. `SSV` is deliberately
    NOT added: it writes the attribute and only reads the tag.

    Judged against what was already spared correctly, the table holds up: every
    comparison (EQU 2,314, GRT 661, NEQ 644, LIM 442, LES 410, GEQ 330, LEQ
    145, CMP 109, MEQ) writes nothing and is charged nothing, and the bit
    outputs (OTE 2,432, OTU 1,869, OTL 990, ONS 1,514, OSR, OSF) are correctly
    outside a set defined as NON-BOOL destinations. Timers and counters
    (TON 732, RES 621, RTO 156, CTU 130) write a structure rather than a word
    and stay out; that is a judgement, not a measurement, and it is 1,639
    instructions (6,556 bytes) — the one remaining item here worth a file if
    anything ever is.

    Real set: 1.6753% -> **1.6732%**. No generated row moved at all, which is
    itself the finding: not one file in the 2,500-row corpus puts a GSV, MVM,
    COP or FLL inside an AOI, so this whole surface was only ever exercised by
    the real programs.

    **CAPTURE ERRORS: 5 row(s)** — `aoi_logic_scale_010/050/100`,
    `aoi_multiroutine_control/real`. These were routed to OQ-AOIDEFITEMIZE and
    OQ-BUILDFAIL-OPEN by sample-prefix rules, so the rows that invalidate this
    question's headline were being flagged against two unrelated questions.
    `samples/oq_owners.csv` now routes both families here, which is where the
    consequence actually lands.


13. **OQ-IDENTNAMELEN** — new, real, found 2026-08-31 in the same push as
    the "5/10/15/20/50 subroutines... different routine name lengths"
    directive. `gen_jsr_multi_distinct_targets_scale.py`'s
    `group_name_length` (10 fixed JSR targets, name length swept 4/8/16/
    32/40 chars — 40 capped per Rockwell's real Logix identifier limit,
    see that generator's own comment) and `gen_program_multi_distinct_
    scale.py`'s matching `group_name_length` (10 fixed extra Programs,
    same length sweep) both currently predict a FLAT total regardless of
    name length — neither `jsr_target_param_counts`' `A(n)` nor
    `task_program_shell`'s `program_extra` has a name-length term, unlike
    tags/UDTs/AOI definitions (all confirmed real name-length bucket
    costs already).

    **Real capture landed 2026-08-31 for both sweeps at namelen04/08/16/
    32 (namelen40 not yet captured — that variant failed import under the
    old, invalid namelen48; see the fix below) — and the two
    independent sweeps show the SAME real pattern.** Deltas (against the
    flat predicted baseline, so pure name-length signal) at len 4/8/16/32,
    10 items per file:
      - JSR targets: +1,440 / +1,520 / +1,600 / +1,760 (7.13% / 7.53% /
        7.92% / 8.72%)
      - Programs: -160 / -80 / 0 / +160 (-0.62% / -0.31% / 0.00% / 0.62%)
    (JSR shows a large constant offset because its predicted baseline is
    already under-costed by the separate, still-open target-content and
    per-param findings above; Programs' baseline is exact at len=16 so its
    deltas read as pure signal directly.) Per-item, both sweeps show the
    IDENTICAL step shape: +8/item from len4→len8 (a 4-char step), +8/item
    from len8→len16 (an 8-char step — HALF the per-char rate of the first
    step), +16/item from len16→len32 (a 16-char step — same per-char rate
    as the second step). Expressed relative to a 4-char name: `extra_bytes
    (len) = 2*(min(len,8)-4)` for `4<=len<=8`, `= len` for `len>8` — fits
    all 8 real data points (both sweeps) within rounding. The doubled rate
    in the first 4-char step, then a steady ~1 byte/char/item above that,
    is consistent with a real 8-byte-aligned minimum name-field allocation
    (matches the shape, though not the exact constants, of the already-
    wired AOI type-name-length bucket formula). **Real, general, and
    reproducible across two independent identifier classes (JSR target
    routine names, Program names) — genuinely new, not previously known,
    and NOT yet wired.** Needs the len=40 capture (in flight) to confirm
    the fit holds at the real Rockwell maximum before committing to
    exact constants, and a decision on whether this generalizes to
    Routine names too (untested) or is specific to JSR-target/Program
    identifiers.

    **WIRED 2026-09-12. The len=40 capture this was held open waiting for
    had already landed** — `jsr_multi_distinct_targets_namelen40` and
    `program_multi_distinct_namelen40` are both in the manifest with
    `error_count = 0`, and the fit holds at Rockwell's real identifier
    maximum. Per-identifier cost relative to a 4-character name, 10
    identifiers per file:

    | name length | 4 | 8 | 16 | 32 | 40 |
    |---|---:|---:|---:|---:|---:|
    | JSR targets | 0 | +8 | +16 | +32 | +40 |
    | Programs | 0 | +8 | +16 | +32 | +40 |

    Above 8 characters the cost is exactly the character count — 1 byte per
    character, no bucketing, unlike the AOI type-name and alias-tag formulas
    which both bucket. At 4 characters it is zero, not 4. Wired as ONE shared
    `identifier_name_length` in `memory_model.yaml`, used by both the
    JSR-target declaration and the Program shell, because the whole finding
    is that two independent identifier classes agree:

        name_bytes(len) = 0               for len <= 4
                        = 2 * (len - 4)   for 4 < len <= 8
                        = len             for len > 8

    Results: all five `program_multi_distinct_namelen*` rows went from
    `0 / −80 / −160 / −320 / −400` to **exactly 0** — Programs had no
    name-length term at all, so len=40 was under-predicting by 400 bytes on
    10 programs. All five `jsr_multi_distinct_targets_namelen*` rows collapsed
    onto a **uniform +200** (was +240 at len=4, +200 elsewhere): the JSR path
    already had a straight `1 × len` term with the right slope but no floor,
    and with the floor applied there is no name-length signal left in that
    residual at all — the remaining flat +200 is the separate per-target
    under-charge (OQ-JSRPARAMCOST). `jsr_crossed_n20/n40_namelen16/32` are
    unchanged, correctly: they were already flat in name length. Corpus exact
    predictions 1,031 → 1,040.

    **Two things the wired law does not rest on measurements for. 24 files
    built** (`src/sample_gen/gen_identname_closeout.py`):

    - **A, `identnamelen_prog_c01..c12`** (12 files). The law is two pieces
      meeting at 8 characters and the sub-8 piece is a straight line drawn
      between two anchors (0 at 4 chars, 8 at 8 chars) with **no data of its
      own**. Real Logix names that short are common, so this sweeps every
      length 1..12 directly, 10 Programs per file. Programs rather than JSR
      targets deliberately: the Program sweep reconciles at exactly 0 across
      its whole range, so any deviation is pure name-length signal, whereas
      the JSR sweep's flat +200 would have to be subtracted first.
    - **B, `identnamelen_rtn_c{01,04,08,12,16,32,40}`** (7 files). Whether
      the law generalizes to plain ROUTINE names, which this entry flags as
      untested. `routine_extra` has no name-length term, exactly as
      `program_extra` had none. If plain routines follow the same law they
      need the same wiring; if they do not, the law belongs to **scheduling
      and call targets** (Programs, JSR targets) rather than to every named
      object — a materially different rule that changes where else it should
      be applied. The routines are uncalled on purpose so the JSR-target
      declaration path cannot contribute.
    - **C, `identnamelen_task_c{04,08,16,32,40}`** (5 files). Tasks are the
      third identifier in the same shell formula (`task_extra`) and the only
      one whose name no sweep has ever varied. Each extra Periodic task
      schedules one Program held at a fixed 16-character name so only the
      task name moves.

    The engine currently predicts a **flat** total across every file in B and
    C, which is the hypothesis under test: flat captures confirm the law is
    specific to scheduling/call targets, varying ones say it is general and
    two more terms need wiring.

    **CAPTURE ERRORS: none. RECAPTURED CLEAN, verified 2026-09-18.** The rows
    this entry used to flag as captured-with-errors now carry `error_count = 0`
    in the manifest, so their `actual_bytes` is trustworthy and every number
    above is drawn from clean captures. `scripts/capture_errors.py` routes no
    errored row here any more; the old block was a warning that had outlived
    its cause.

    **CLOSED 2026-09-14 (capture-batch segment 9). 19 of 19 rows byte-exact,
    against 7 of 19 before. Two corrections, and the second one was invisible
    until both arms were read together.**

    **1. The law is a STEP, not a ramp: `8 * floor(namelen / 8)`** per
    identifier -- the same form the project already uses for tag, UDT and
    AOI-definition names, so there is now one name law rather than two. The
    previous three-regime fit (0 below 5 characters, 2/char to 8, then 1 x len)
    was anchored at 1, 4, 8, 16, 32 and 40, and the new law agrees with it at
    **every one of those anchors**. It was wrong only across the interval it had
    to interpolate -- which its own entry described as "an interpolation between
    two anchors rather than measured", and which is exactly what this sweep
    measures:

        len   old (ramp)   measured (step)
          5            2                 0
          6            4                 0
          7            6                 0
          9            9                 8
         12           12                 8

    `identnamelen_prog_c{01..12}` carries 10 Programs at each length and reads
    25,688 flat for lengths 1-7 then 25,768 flat for 8-12 -- seven files at seven
    lengths on one total, then five files at five lengths on another. A ramp
    cannot produce that.

    **2. ORDINARY routines pay it too, and only JSR targets were being charged.**
    `identnamelen_rtn_c{01,04,08,12,16,32,40}` carries 10 non-JSR routines and
    reads 0 / 0 / 80 / 80 / 160 / 320 / 400 over its baseline -- 8 bytes per
    routine per bucket, identical to the per-program rate. The engine predicted
    those seven files FLAT, because routine names were charged only through
    `jsr_target_declaration`.

    **3. The n-1 convention is PER PROGRAM for routines, per project for
    programs** -- and this is the part neither arm could settle alone. Charging
    routines with a flat project-wide n-1 makes the `rtn` arm exact and
    over-charges every `prog` file by exactly 80. The two arms distribute the
    same routine count differently: `rtn` puts 11 routines in ONE program (10
    charged), `prog` puts 11 routines across 11 programs, one each (none
    charged). The first routine in each program is inside the baseline
    `fixed_base_per_routine` was fitted against, which is also what keeps
    `identnamelen_rtn_c01` and `_c04` exact at zero.

    **Effect on the real set: slightly worse, and the change is still right.**
    1.6091% -> 1.6112% mean, +1.2261% -> +1.2417% sum-weighted. The step law
    lowers the charge for every 9-15, 17-23 and 25-31 character name, real
    programs are full of them, and the real set under-predicts -- so removing an
    over-charge costs the headline. That is the fifth time today the same
    arithmetic has appeared, and the reasoning is the same: the old value was a
    self-documented interpolation, this one is measured on a sweep built to
    measure it, and 19 of 19 rows land on the byte.

    **Still open: the TASK arm.** `identnamelen_task_c{04,08,16,32,40}` (5 rows)
    was never captured, so whether a Task's own name follows the same law is
    untested. Those are the 5 errored/uncaptured rows this segment carried.



14. **OQ-193ECMETR** — new, real, genuinely undiagnosed (now covering TWO
    catalogs — see the correction below). 2026-09-02, real Studio
    5000 error on `composite_realistic_v2_18`/`_50` ("Error:
    TestMod2_193ECMETRA: Child module incompatible with parent module").
    Self-audit (checking for real currently-unreconciled `error_count`
    data per CLAUDE.md's standing rule, not just the composite files
    originally reported) found this is NOT composite-specific: BOTH standalone
    `modulesweep_193_ecm_etr_a`/`_b` already carry a real `error_count=1`
    in `manifest.csv` — sitting there uninvestigated since capture, never
    previously flagged. No real Studio 5000 error-log line exists for the
    standalone repro (only the composite-context quote above), so the
    exact cause is unconfirmed — plausible candidates (EKey/revision
    mismatch between the extracted 1756-EN4TR adapter and the E300 relay
    child, or the E300 family needing a different real parent device
    entirely) are just guesses, not verified. Excluded from
    `gen_composite_realistic.py`'s module pool
    (`_UNDIAGNOSED_COMPOSITE_CATALOGS`) so future composite files stop
    reproducing it. Needs the real per-file Studio 5000 error-log detail
    (not just the generic error line already quoted) to actually
    root-cause.

    **CORRECTION, same day, within the hour:** `2198-S130-ERS3` was
    initially diagnosed below as "requires a safety-capable controller"
    and wired into `_SIL2_CATALOGS` — DISPROVEN by real evidence almost
    immediately after: a real production file
    (`TitusvilleTrimmer_20260902r2.L5X`) runs a real `2198-D057-ERS3`
    module (`EM113_TrimmerLC_EM109_TrimInfdLC`) on a plain non-safety
    1756-L82E (`<SafetyInfo/>` empty, no SafetyTask anywhere) —
    `SafetyEnabled="false"`, no `SafetyNetwork`, structurally the same
    shape this project's own genericized block already uses. An
    "-ERS3" catalog genuinely CAN run on a non-safety controller for
    real, so the safety-controller theory is wrong. Reverted out of
    `_SIL2_CATALOGS`. The real `error_count=2` signal on
    `modulesweep_2198_s130_ers3` (and the clean 7/7 correlation across
    every "-ERS3" catalog in the corpus) is still real and still
    unexplained — `2198-S130-ERS3` moves into the SAME genuinely-
    undiagnosed bucket as `193-ECM-ETR/A`/`/B` above
    (`_UNDIAGNOSED_COMPOSITE_CATALOGS`) rather than standing on a second
    guessed theory.

    **SOLVED 2026-09-06, and the lead above was close.** The genericized
    `-ERS3` blocks were indeed missing something the real modules carry: the
    `<ExtendedProperties>` element (Vendor, CatNum, FeedbackDevice1-4,
    ConfigID), plus a corrupted ConfigData payload of 119 L5K values against
    the real 118. Both confirmed by diffing against
    `composite_realistic_v4_001`, which carries the same catalogs on a plain
    non-safety 1756-L81E and captured at zero errors — one of 31 such files.
    The `<ExtendedProperties>` fix had already been made on 2026-09-03 in
    `gen_module_motion.py`'s `_drive_module_xml()`;
    `gen_module_sweep_variants.py` keeps a separate hardcoded copy of the
    module XML and never received it. Full entry in RESOLVED_QUESTIONS.md.

    **Worth recording, because it cost real time:** the safety-controller
    theory was disproven here, in writing, with real evidence — and was then
    re-derived from scratch two weeks later and briefly wired into a lint
    rule that flagged the known-good files. The disproof was in this
    document the whole time. Read the correction before re-opening a
    question, and check the repo for files that already work before
    theorising about why one does not.

    **New real evidence, 2026-09-03 — the "missing Motion/Axis
    association" lead above is now DISPROVEN too.** All 50
    `composite_realistic_v3_*` files hit the exact same 2-error signature
    on real Studio 5000 conversion: `Tag 'D012_23:SI': Invalid
    data type for safety tag` + `Project size exceeds controller
    capacity` — 2 errors, matching the "clean X/X correlation" pattern
    already noted above for other "-ERS3" catalogs. Critically, v3's
    `2198-D012-ERS3` module is NOT missing a Motion/Axis association the
    way `modulesweep_2198_s130_ers3` was — it's dual-axis-bound (2 real
    `AXIS_CIP_DRIVE` tags, `MotionModule="D012_NN:Ch1"`/`"...Ch2"`,
    matching `gen_module_motion.py`'s already-real, already-confirmed
    shape) plus a shared MOTION_GROUP tag, and STILL hits the identical
    error. So the "needs a real axis" theory doesn't hold either — every
    "-ERS3" catalog this project has ever generated fails this way
    (with or without an axis bound), while only a real
    Titusville production file has ever shown it working. Direct,
    attribute-by-attribute comparison of a real `2198-D057-ERS3`
    Module block (from Titusville) against this project's generated
    `2198-D012-ERS3` block found them structurally near-identical
    (same Ports/EKey/Communications/Connections shape, same
    `SafetyEnabled="false"`, no `SafetyNetwork`) — the one confirmed
    difference is the real block's `<ExtendedProperties>`
    (`Vendor`/`CatNum`/`FeedbackDevice1-4`/`ConfigID`) is entirely absent
    from every generated instance, but that can't be confirmed as the
    cause either: `gen_module_sweep_variants.py`'s own real-corpus-
    verbatim `2198-D012-ERS3` "2conn" block (source:
    `motion_p208/p208_D012_NodeAndAxisDual3.L5X`, a real reference
    export) ALSO has no `<ExtendedProperties>` and the exact same zeroed
    `ControllerToDriveConnectionSize`/etc. diagnostic fields our
    generator produces — meaning that shape was already confirmed real
    once, not a generator bug in itself, so a missing `ConfigID` isn't a
    safe conclusion without a same-catalog real counter-example that DOES
    import clean. Still needs the raw Designer error-log detail (not
    l5xgit's one-line summary) or a same-catalog Titusville-style real
    file confirmed to import successfully in isolation to make further
    progress — not re-guessing a third theory here. `Project size exceeds
    controller capacity` is unconfirmed whether it's a second real issue
    or a downstream artifact of the first import failure (this project's
    own established pattern elsewhere: a primary import failure has
    previously been found to silently produce a second, misleading
    symptom — see the IP-duplicate/axis-tags-never-made finding,
    2026-08-27, `gen_module_motion.py`).

    **Real generator bug found and fixed, 2026-09-03 — root cause of the
    SI/SO error still NOT confirmed, but a real, independently-confirmed
    channel-numbering mistake found and corrected along the way.** This
    project's own real source file for the dual-axis case
    (`motion_p208/p208_D012_NodeAndAxisDual.L5X`/`Dual3.L5X`, which
    `gen_module_motion.py`'s own docstring claims to genericize
    "structurally verbatim") uses `MotionModule="D012_1:Ch1"` and
    `"...Ch3"` for its two axis tags — **never Ch2.** Both
    `gen_module_motion.py`'s `group_motion_dual_axis_drive()` and
    `gen_composite_realistic_v3.py` had instead hand-typed `Ch2` for the
    second axis — a real transcription bug, confirmed independently
    against 2 real corpus files, not a guess. Fixed (Ch2 -> Ch3 in both
    places), all affected files regenerated, lint-clean.

    **CORRECTION, same day, within the hour:** initially theorized Ch2
    might be internally reserved for the drive's Safe-Torque-Off/safety
    channel, explaining the SI/SO auto-creation — disproven
    immediately by two more real reference exports
    (`SampleAxis.L5X`/`SampleAxis_2and4.L5X`): a real 4-axis Kinetix 5700
    config genuinely uses all 4 channels — Ch1/Ch3 carry the two real
    motor axes (`AxisConfiguration="Position Loop"`), Ch2/Ch4 carry their
    paired **Feedback-Only companion axes** (`AxisConfiguration="Feedback
    Only"`, `FeedbackConfiguration="Master Feedback"`, no motor/tuning
    params at all) — legitimate, ordinary channels, nothing safety-related
    about them. So Ch2 itself isn't the problem; the real, still-open
    question is why our generator's ORIGINAL mistake (a full
    `Position Loop`-configured axis tag placed on Ch2, a slot real
    Kinetix 5700 configs use for a structurally DIFFERENT
    `Feedback Only`-shaped axis) specifically produced a SAFETY-tagged
    error rather than some other kind of mismatch error. The Ch1/Ch3 fix
    still stands (matches 2 independent real corpus captures exactly for
    a 2-declared-axis file), but calling it "the fix for the SI/SO
    error" is not yet confirmed — needs a real ACD retest of the
    regenerated files to know whether it actually clears that error or
    just happens to also be correct for an unrelated reason.

    **Real symptom clarified, real second bug found and fixed, still
    2026-09-03.** A retest of the Ch2->Ch3 fix (`modulemotion_
    d012_dual_axis.L5X`) gave the same 2-error signature, and clarified the
    actual crash: opening the **module's own I/O-tree profile page**
    (not the axis properties page) crashes Studio outright -- confirmed
    by testing the original, unmodified real source file
    (`p208_D012_NodeAndAxisDual.L5X`, the one this project's D012 module
    block is extracted from) side by side: **that file opens fine.**
    Definitive proof the bug is in how this project's own pipeline
    reassembles the real content, not in the real content itself. A
    precise structural diff (whitespace-normalized, identifiers scrubbed)
    against that real file found a second real, concrete bug: `_axis_tag`
    -- the ONE helper this project used to build every axis tag -- was
    also being used to build P208's own on-board "DC BUS" axis, but a
    real DC-bus axis is a structurally DIFFERENT, much shorter
    `AxisConfiguration="Non-Regenerative AC/DC Converter"` shape with no
    servo-tuning parameters at all -- nothing like the full `Position
    Loop` servo template `_axis_tag` always applied. Every P208 axis this
    project has ever generated (5 `modulemotion_*` files, all 50
    `composite_realistic_v3_*` files, all 18 `axis_scale_*` files) has
    been structurally malformed this way -- the leading real suspect for
    the module-page crash, though NOT yet confirmed (the P208 module was
    ruled out independently of this fix, before it was applied -- still
    needs a retest of the regenerated file to know either way).
    Fixed: new `_dcbus_axis_tag()` helper using the real, verbatim-
    extracted DC-bus shape, wired into all 3 generators
    (`gen_module_motion.py`, `gen_composite_realistic_v3.py`,
    `gen_module_axis_scale.py` -- the last one had never been checked
    against this bug before). All affected files regenerated, lint-clean,
    177/177 tests passing.

    **Two separate, real bugs found and fixed the same pass, NOT this
    one:**
    - **Sequential slot numbering.** Many racks did not use slot numbers in
      sequence; a lint check for this was added.
      `gen_composite_realistic.py`'s `_modules_xml_unique_ips` keyed each
      catalog's assigned Local-ICP backplane slot off its raw index in the
      file's full catalog list (`slot=2+i`), regardless of whether that
      catalog even has an ICP-backplane root module — an Ethernet-only
      catalog between two ICP catalogs silently consumed an index without
      consuming a slot, leaving a real gap (confirmed real example:
      `composite_realistic_22_r2.L5X`, slots 3 and 5 present, 4 missing).
      Also always started at slot 2, one too high — `wrapper.py`'s own
      Local module template puts the CPU's downstream ICP port at
      `Address="0"` in every branch, so the first real expansion module is
      physically slot 1. Fixed: only catalogs whose block actually
      contains a Local-ICP root module consume a slot, numbered
      sequentially from 1 with no gaps. New lint check added,
      `non_sequential_module_slots` (`sample_gen/lint.py`
      `_slot_sequence_findings`) — flags any (ParentModule, PortId) group
      of 2+ modules with numeric addresses that isn't a contiguous run, so
      a future generator can't reintroduce this silently. (Also flags 2
      pre-existing `modulerack_1756_local`/`_remote` files not touched by
      this fix — those may be intentionally sparse racks, not bugs; not
      changed, flagged for confirmation before any future regen.)
    - **"Safety-rated module in a non-safety-declared composite"
      (`2198-S130-ERS3`, `composite_realistic_v2_19`/`_30`)** — this WAS
      diagnosed and fixed here initially, then disproven within the hour
      by real evidence. See the CORRECTION under OQ-193ECMETR above for
      the full story: it's genuinely undiagnosed, not a safety-controller
      requirement, and now sits in the same exclusion bucket as
      `193-ECM-ETR/A`/`/B`.


    **CAPTURE ERRORS: none. RECAPTURED CLEAN, verified 2026-09-18.** The rows
    this entry used to flag as captured-with-errors now carry `error_count = 0`
    in the manifest, so their `actual_bytes` is trustworthy and every number
    above is drawn from clean captures. `scripts/capture_errors.py` routes no
    errored row here any more; the old block was a warning that had outlived
    its cause.


15. **OQ-V3GENBUGS** — three real generator bugs found via the actual
    Studio 5000 ACD-conversion errors on the v3 composite batch (50 files,
    2026-09-02), all root-caused to the exact reported symptom and fixed:
    `_LOCAL_ICP_SLOT_RE` crossing `<Module>` boundaries in DOTALL mode
    (corrupted an unrelated child module's valid ICP slot when the "root"
    module's own port didn't match), `lint.py`'s `_module_slot_findings`
    treating a real, valid nameless `<Module>` (e.g. `1756-OF8/B`) as
    invisible to slot-collision checks, and an IPv4 4th-octet overflow in
    `_modules_xml_unique_ips` (`base = 60 + (i+1)*10` broke past ~19
    catalogs/file — v3 routinely has 15-34). All three fixed and covered
    by new regression tests (`tests/test_gen_composite_realistic.py`).
    New test batches this same pass, all lint-clean and pushed:
    `composite_realistic_v3_*` (50, deliberately wide-varying program/AOI/
    subroutine counts — see [^compositescale] — built specifically to
    re-derive the JSR/AOI composite-scale surcharge that over-generalized
    at Titusville's real 179-distinct-JSR-target scale, see OQ-JSRSCALE
    below), `axis_scale_*` (18, single/dual-axis 2198 servo drive counts
    1-20 ± regen), `rack_5069_*` (11, real `Remote5069.L5X`-derived AENTR
    multi-child racks), `rack_pointio_*` (11, real `1734-AENT/B` multi-slot
    adapter), `rack_1756_*` (12, local-rack size scaling 2-16 modules),
    `cipmodule_scale_*` (7, CIP-MODULE declared-I/O-size sweep 64-2048
    bytes, anchored against Titusville's real 496-byte `IO_Optm` instance),
    `bridge_placeholder_*` (2, real zero-connection `ETHERNET-BRIDGE`
    IP-only fan-out node). None of these have real capture data back yet
    (ACD conversion still being validated as of 2026-09-02) — no sizing
    formula changes from this item, generator-correctness only.

    **2026-09-12: that status was stale and the answer is bad.** Every one of
    the 133 rows across the seven families named above is captured, and **65 of
    them captured WITH Studio build errors**:

    | family | rows | convert ok | captured | captured WITH errors |
    |---|---:|---:|---:|---:|
    | `composite_realistic_v3` | 50 | 50 | 50 | **49** (exactly 2 each) |
    | `axis_scale` | 18 | 18 | 18 | **18** (n+1 single, n/2+1 dual) |
    | `rack_5069` | 34 | 34 | 34 | 0 |
    | `rack_pointio` | 12 | 12 | 12 | 0 |
    | `rack_1756` | 12 | 12 | 12 | 0 |
    | `cipmodule_scale` | 7 | 5 | 5 | 0 — **2 never attempted, files gone** |
    | `bridge_placeholder` | 2 | 2 | 2 | 0 |

    The three racks and the bridge are clean and can be used. The other two
    cannot be used as they stand.

    `axis_scale`'s signature is **one error per axis plus one** — exactly the
    pattern CLAUDE.md cites as the reason the step-2b gate exists. It routes to
    OQ-AXISMARGINAL, which already carries it.

    **`composite_realistic_v3` is the new one, and it taints another
    question.** 49 of 50 files carry **exactly 2** errors, constant across a
    batch whose size spans 1.3–1.9 MB and whose programs (5–12), AOIs (5–24),
    modules (17–34) and routines all vary widely. A count that scales with no
    content dimension is two discrete template defects, not a per-item problem.
    And v3 was built specifically to re-derive the composite-scale JSR/AOI
    surcharge, so **OQ-COMPOSITESCALE's re-derivation is standing on 49 suspect
    rows.**

    Structural inference was tried and did not find it. Recorded so it is not
    repeated:

    - v3 declares four catalogs v4 does not (`1756-OA16I`, `1756-OF4/A`,
      `1756-OF8/B`, `1794-IB16/A`). **All four, plus `1794-ACN15/C` and
      `1756-CNB/D`, have their own standalone `modulesweep_*` capture at zero
      errors.** No single catalog is the offender.
    - Nameless `<Module>` elements are not it: v3_12 has 3 and errors,
      v4_013 has 8 and is clean. They are legitimate drive-peripheral and
      POINT I/O sub-modules, so the earlier decision to teach lint to tolerate
      them was right.
    - The one clean file, `composite_realistic_v3_13`, is not structurally
      special — 11 programs, 18 AOIs, 48 modules, 4 axes, mid-range for the
      batch. Its immediate neighbours v3_12 and v3_14 both error.
    - **v4 is clean**: 31 captured rows, 0 errors, from a successor generator
      whose files are bigger (97 modules, 14 axes against v3's 48 and 4). So
      the defect is specific to the v3 template, not to composite files.

    **8 files built to name the subsystem by measurement**
    (`src/sample_gen/gen_v3_error_ablation.py`): profile 12 — a known 2-error
    profile — with one subsystem removed per file (`v3abl_control`, `noaoi`,
    `minudt`, `nomodules`, `noprograms`, `norungs`, `nostrings`, `minarrays`).
    The arm that drops to zero errors names it. Every arm lands within 2 bytes
    of the same 1.75 MB total because the generator pads to a target size, so
    project size cannot be the confound — only the removed subsystem varies.
    The control must reproduce the 2 errors or the v3 template has moved since
    those captures and the whole batch needs recapturing before anything else
    is concluded from it. If every arm still shows 2, the defect is in the
    fixed scaffolding no ablation touches — the motion block, MainProgram, or
    controller header — and the next step is **the raw Studio 5000 error-log
    line** for one v3 file rather than more inference.

    **A real sizing bug found while building that batch and FIXED.**
    `parser/modules.py`'s `_ATOMIC_BYTES` was a hardcoded literal listing only
    the SIGNED atomics, so every module member declared `USINT` / `UINT` /
    `UDINT` / `ULINT` fell through to `unknown_member_types` and the module's
    size came back as an explicit floor instead of a real total — two modules
    in the v3 template (`AL1122`, `AL1222`) have 25 such members each. All four
    types are standard Logix atomics already present in `memory_model.yaml`'s
    `atomic_types`, and they are not rare: **109 committed sample files declare
    them, and all four appear in the real production corpus** (25 `UINT`, 20
    `USINT`, 16 `UDINT`, 9 `ULINT` member declarations). The table now derives
    from the model, so this cannot recur for a type the model already knows —
    which is what CLAUDE.md's no-hardcoded-sizes rule exists to prevent.

    **ABLATION CAPTURED 2026-09-14 (segment 24) AND IT CANNOT BE DIFFERENCED.
    That is itself the finding about the v3 template. BLOCKED.**

    Each `v3abl_*` variant is supposed to remove exactly one feature from a common
    control. `v3abl_noprograms` has 2 programs against the control's 10 and 690
    rungs against 2,013 -- and is **larger on disk than the control**, 14.66 MB
    against 13.99 MB. Removing eight programs and two-thirds of the rungs cannot
    increase a project, so the variant changes more than the feature it names.

    The totals say the same. Predicted is near-constant across all eight variants
    (1,745,740 to 1,749,057) while actual ranges 1,686,379 to 1,748,759, so the
    engine is blind to whatever actually differs between them.

    Two further problems on the same eight rows. `v3abl_minarrays` has a **blank
    `error_count`** -- never recorded -- so its -62,678 is suspect on top of being
    undifferenceable. And `v3abl_noprograms` reading -296 against the control's
    -34,961 invites exactly the wrong conclusion ("the whole error is program
    content") from a comparison that is not valid; it is recorded here so that
    reading is not reached a second time.

    **Needed: the ablation rebuilt so each variant removes only its named feature,
    with the control's content otherwise byte-identical.** Until then no `v3abl_`
    row may be differenced and the ~2% error on these files stays attributed to
    nothing.


16. **OQ-JSRSCALE / OQ-COMPOSITESCALE** — the composite AOI/JSR surcharge.
    **REFITTED ON REAL PROGRAMS 2026-09-04. Was the project's #1 error
    source; is now its largest remaining one, but 5x smaller.**

    supplied real Capacity readings for 8 whole real customer
    programs, joining `Cardin_TrimSortStack` for **9 real data points** —
    the first time this question has had more than one. Under the old model
    (`aoi=20`, `jsr=47`, file-wide cap 12,000) **all nine under-predicted**,
    by +8.35% to +30.63%, aggregate **+12.62%**, mean |error| **14.95%**.

    The driver was identified BEFORE anything was refitted, deliberately —
    correlating each real file's residual against every measurable
    candidate:

    | driver | corr | | driver | corr |
    |---|---:|---|---|---:|
    | JSR-target instructions | **+0.813** | | routine count | +0.769 |
    | all RLL instructions | +0.805 | | controller tags | +0.514 |
    | unweighted instructions | +0.524 | | AOI-internal instructions | +0.203 |
    | **ST source lines** | **−0.396** | | **unsized modules** | **−0.255** |

    So the residual is JSR-target logic content, and it is NOT unmodeled ST
    (negative) and NOT the unsized rack-aliased modules (negative). That
    matters: it rules out the two most tempting alternative explanations
    before the surcharge was touched, which is the check that was missing
    when the drive-bus discount got fitted on bad data and had to be
    reverted.

    Refit: least squares of (actual − prediction-with-no-surcharge) on
    [aoi_instr, jsr_instr] over all 9 real files → **52.52 / 20.81**,
    rounded to **52 / 21** with no meaningful loss. **Cap disabled** (0) —
    it was a patch for a jsr rate 2.3x too high, and at real scale it was
    suppressing 252,749–1,260,885 bytes per file, which IS the +12.62%.

    Leave-one-out over the 9 (fit on 8, predict the 9th): **mean |error|
    3.83%, max 9.41%**. Two rates beat one combined rate (same mean, max
    12.78%) and a JSR-only rate (4.86% / 17.69%), which is why both are
    kept.

    Result: real programs **14.95% → 3.29%** mean, aggregate **+12.62% →
    −0.41%**, 2 of 8 now inside ±1%. Cost, stated not buried: the 176
    corpus rows carrying AOI/JSR content go 3.09% → 3.57% and the whole
    1,885-row corpus 1.378% → 1.423%. The synthetic composites and the real
    programs genuinely disagree about this law; this trades a rounding
    error on the instruments for a 5x gain on the thing the project exists
    to predict, per CLAUDE.md's North Star.

    **STILL OPEN, and this is the main remaining gap:** 3.29% is not <1%,
    and leave-one-out says expect ~3.8% on a file nobody has seen. The two
    worst are `MurrayBros` (+7.43%, the smallest file at 923 KB) and
    `K3M16_Edgers` (+5.55%) — both still UNDER — against `Pukall_Gang`
    (−5.44%) OVER, so the remaining error is not a single sign and not a
    simple scale term. What is needed: **more real programs** (each one has
    been worth more than any synthetic batch), and the captures for the
    already-generated `realscale_jsrtgt_xic_n*` ladder, which is the only
    thing that can separate per-instruction cost from per-target and
    per-routine cost at real scale.

    **IN-DEPTH REVIEW 2026-09-18 — the composite residual is IDENTIFIED, and
    it is not a composite effect at all.** The `addit_*` additivity grid
    (33 captured rows) was built to ask whether categories interact. It
    answers cleanly, and the answer relocates this question.

    Every grid cell was re-evaluated live against the current engine and
    sorted by its logic dimension L (rung count 0 / 400 / 4000):

    | L | cells | residual range | per-rung |
    |---:|---:|---|---:|
    | 0 | 3 | −40 … 0 | — |
    | 400 | 4 | −9,332 … −9,848 | −23.3 … −24.6 |
    | 4000 | 10 | −95,732 … −96,248 | −23.93 … −24.06 |

    So the residual is **−24 per rung, at two scales an order of magnitude
    apart, across 10 independent cells**, and it is **entirely carried by the
    L dimension**. Hold L at 0 and every combination of D (UDT definitions),
    A (AOI definitions/instances) and M (modules) reads within 40 bytes of
    zero. Vary D, A or M at fixed L and the residual does not move by more
    than ±300. **The categories ARE additive.** There is no composite
    surcharge to fit; there is one mispriced ladder term that composite files
    happen to contain a lot of.

    And that term is already known. The grid's rung shape is

        XIC(Bit0)MOV(1,Dst0)ADD(Dst0,1,Dst0)OTE(Bit1);

    which is **three writing instructions** (MOV, ADD, OTE). −24/rung is
    exactly **−12 × (3 − 1)** — the OQ-SERIESOUTPUT law, at a rung width
    nothing else in the corpus tests. `addit_*` is therefore the **third
    independent confirmation** of that law, after the `srout_*` sweeps
    (k = 1…8, 16 rows byte-exact) and `ntag_uidpair` (k = 2). Three unrelated
    synthetic families, built by different generators months apart for
    different questions, all land on −12 per extra output.

    This sharpens rather than resolves the central contradiction. The same
    −12 that is byte-exact on three synthetic families takes the sixteen real
    programs from 1.6894% to 3.2167% and makes every one worse. The refitted
    52/21 AOI/JSR surcharge above is now best understood as **a proxy that
    absorbs the real files' side of that contradiction** — it is fitted on
    real files, where the −12 does not appear, so it is soaking up whatever
    real ladder does that synthetic cascades do not. That is why the
    surcharge costs the corpus 1.378% → 1.423% while paying 5x on the real
    set: the two sets disagree about one specific thing, and both terms are
    fitted to opposite sides of it.

    **Consequence for the plan.** Refitting the 52/21 surcharge harder cannot
    reach 1%, because it is compensating for a term it does not name. The
    decisive measurement is the `sroutc_c{1,2,4}_k{1,2,4,8}` grid (arm A of
    `gen_oq_closeout.py`, 12 files, built and awaiting capture), which is the
    only thing in flight that separates output count from condition count
    inside one rung. If the discount is a function of the condition/output
    RATIO rather than the raw output count, the real files — which carry many
    conditions per output — sit where the discount is near zero, the
    synthetic cascades sit where it is −12, and both sets are describing the
    same law. That is the single hypothesis that reconciles them, and one
    capture batch tests it.

    Until then the surcharge stays at 52/21 and OQ-SERIESOUTPUT stays
    `apply: false`. Neither is right; together they are the least wrong
    configuration measured.



17. **OQ-AXISCOMBO** — cited in RESOLVED_QUESTIONS.md (OQ-AXISSTRUCT,
    OQ-AXISDEEP) as "the one remaining piece," but no item by this name —
    or covering this ground — was ever actually created here. A real
    doc-sync gap, not a resolved one. Chasing it down surfaced a second,
    more substantive gap: OQ-AXISSTRUCT's real Capacity numbers don't
    match what's already wired into `memory_model.yaml`'s
    `predefined_structures` from OQ-PREDEFINED. Correction to the record:
    axis content is NOT "100%-blind, priced at exactly $0" as previously
    stated — AXIS_CIP_DRIVE/AXIS_SERVO/AXIS_VIRTUAL/
    COORDINATE_SYSTEM are wired and sizing without error today (FITTED,
    single-sample-each). See footnote for the actual unreconciled numbers
    and what's needed to close this for real.


23. **OQ-DEFSCALE** — definition- and instance-count scaling. **CAPTURED
    AND RECONCILED 2026-09-11, all 30 files, zero import errors. Four exact
    linear laws, none of them wired, and the reason is a confound, not a
    doubt about the numbers.**


    **IN-DEPTH REVIEW 2026-09-18. One term wired exactly, one measured exactly
    and BLOCKED by a confound that runs through the whole corpus.**

    **(a) An AOI DEFINITION is over-charged 7, not 3. Wired, KNOWN.**
    `defscale_aoidefs_n{001,002,005,010,020,040,060}` varies only the definition
    count and carries no instances at all, so it reads the definition term
    alone:

        definitions   1    2     5     10     20      40      60
        residual     -4   -8   -20    -40    -80    -160    -240

    Exactly 4 per definition beyond the 3 already applied, at all seven counts.
    The original −3 came from ONE file, `dscale2_aoi_d060_t060`, solved jointly
    with the per-instance −8 from that same file — and a single file cannot
    separate two per-unit terms. It did not. With −7 wired, all seven rows are
    byte-exact. Corrected in `definition_scale_correction`, not in
    `aoi_definition.base`, because the base is what one definition costs and
    this is the term that scales with how many there are.

    **(b) An RLL routine containing AOI calls carries a one-time ~260, and it is
    the SAME constant the ST side carries at 264 — but it CANNOT be wired.**

    `dscale2_aoi_d001_t{001..100}_call` reads a flat **+260** at every target
    count from 1 to 100. Flat across a 100x span means once per file or once per
    routine, not per call or per instance. `defscale_aoiinst_n{001..060}` reads
    `+260 − 4n`, the same 260 plus the per-instance term.

    That 260 is `st_aoi_call_routine_bytes` (264) seen in the other language,
    within the per-instance 4. **The RLL path has no such term at all.**

    **Why it is not wired: every generated file in the corpus that contains an
    AOI call — all 80 of them, both languages — has exactly ONE calling
    routine.** So "once per routine" and "once per file" fit every row
    identically, and on the sixteen real programs the two readings differ by
    **764 routines × 264 = 201,696 bytes against 16 × 264 = 4,224**. A 48x
    spread on a term large enough to move the headline. Guessing here would be
    the largest unforced error available in this model.

    **This also forced a correction to something wired earlier the same day.**
    `st_aoi_call_routine_confidence` was marked KNOWN when the ST batch closed;
    it is now **FITTED**, because the 264 is measured but its CARRIER is not.
    The ST side happens to be safe either way — 26 real ST routines against 16
    files is 2,640 bytes — but the tier was claiming more than the data
    supports, and the KNOWN register is what surfaced it.

    **What settles it: one file with AOI calls in TWO routines**, everything
    else held identical to `dscale2_aoi_d001_t002_call`. If the residual goes to
    520 it is per routine; if it stays at 260 it is per file. One file decides a
    200,000-byte term, and it unblocks the ST constant at the same time.

    All four sweeps came back perfectly linear with zero residual:

        defscale_aoidefs_n*    over-prediction = +3 x n          7 points
        defscale_aoiinst_n*    over-prediction = -264 - 157 x n  7 points
        defscale_udts_n*       over-prediction = -16 x n         8 points
        defscale_udttag_n*     over-prediction = -19 x n         8 points

    Subtracting the paired sweeps: an AOI **definition** is over-charged by
    **3** bytes; an **instantiated** AOI is under-charged by **160** per unit
    plus **264** once; a **UDT definition** is under-charged by **16**; a UDT
    that has a tag is under-charged by a further **3**.

    Applied to the sixteen real programs those four numbers give:

        mean |error|   2.17%  ->  1.63%
        within 1%          4  ->  6
        within 2%          9  ->  11

    and they move every file UP — the direction the real files need, and the
    opposite direction to OQ-MODULEMARGINAL's module over-charge. The two
    together are the clearest evidence yet that the real-file residual is
    composed of large offsetting terms rather than one missing cost.

    **Why it is not wired: every sweep varies two things at once.**
    `defscale_aoiinst_n` holds n definitions, each with exactly ONE instance
    tag AND exactly ONE calling rung, so n = definitions = instance tags =
    calls, and "160 per instance tag", "160 per AOI call" and "160 extra for
    a definition that is instantiated at all" fit all seven points
    identically. `defscale_udttag_n` holds n UDTs with ONE tag each, so "3
    per UDT tag" and "3 once for a UDT that has any tag" fit all eight.

    On a real program those readings are nowhere near each other. AccuTally
    carries 902 AOI instances across 39 definitions and 33,574 UDT tags
    across 174 UDT definitions:

        per instance / per tag   160 x 902 + 3 x 33,574  = +245,042
        per definition           160 x  39 + 3 x    174  =   +6,762

    238 KB apart on one file, 4% of it — the same structural ambiguity as
    OQ-MODULEMARGINAL's per-catalog-vs-per-file question, in a different cost
    category, and it gets measured for the same reason: on this project the
    tidier reading has been wrong before.

    **Test files built 2026-09-11, `gen_defscale2.py`, 39 files.** Every
    definition is built from `gen_defscale`'s own `_aoi_members()` /
    `_udt_members()`, so they are byte-identical to the captured sweep and
    difference straight against it. The model's own prediction is a perfectly
    straight line across every new sweep (112/instance tag, 101/UDT tag,
    20/AOI array element, 12/UDT array element, and **0 per call**), so any
    slope error or curvature in the capture is unambiguous.

    | arm | files | what is pinned | what it decides |
    |---|---:|---|---|
    | `dscale2_aoi_d001_t*_call` | 8 | 1 definition | slope is per-INSTANCE, not per-definition (1→100 instances) |
    | `dscale2_aoi_d001_t*_nocall` | 4 | 1 definition, no logic | splits the instance TAG from its CALL |
    | `dscale2_aoi_d001_t001_c*` | 3 | 1 definition, 1 instance | the converse: call count varies alone. The model charges 0 per call, so any movement here is pure call cost |
    | `dscale2_aoi_d*_t*_nocall` | 3 | — | `defscale_aoiinst_n{05,20,60}` minus its calling rungs, for a direct difference at real-file scale |
    | `dscale2_aoi_arr*` | 3 | 1 definition, 1 tag | per-instance or per-tag: an ARRAY of 2/10/50 instances |
    | `dscale2_udt_u001_t*` | 9 | 1 UDT definition | slope is per-TAG, not per-definition (1→500 tags) |
    | `dscale2_udt_u{005,025}_t*` | 5 | — | definition count x tag count crossed: additive or interacting |
    | `dscale2_udt_arr*` | 4 | 1 UDT, 1 tag | per-element or per-tag, 2→500 elements |

    `dscale2_udt_u001_t001` is byte-identical to the already-captured
    `defscale_udttag_n001` and is kept deliberately: it anchors the new
    sweep's intercept in the same capture run and doubles as a
    run-to-run reproducibility check.

    **Not covered, and reported rather than guessed:** program-scoped
    structure tags. A Program-scoped ATOMIC tag has a confirmed real shape
    (`program_tag_xml`, dual L5K+Decorated), but no real corpus file has been
    read for a Program-scoped UDT or AOI-instance tag — and real programs put
    most of their instances there. Building one from a guessed shape would
    put an unverified XML shape inside the experiment meant to settle the
    question. It needs a real export first.

    **The original framing of this item stands and is now confirmed rather
    than suspected.** Across all captured non-real files the maximum was 7
    AOI definitions and 6 UDTs, while the real programs carry 11–39
    definitions and 51–174 UDTs; the first batch to bracket them found an
    exact error at every point. What the first batch could not do was
    attribute it, which is what the 39 new files are for.



24. **OQ-SHELLCONST** — new, 2026-09-04, split out of OQ-SHELLSCALE. Two
    small CONSTANT (non-scaling) residuals the shell isolation exposed
    once the slopes were exact:

    - **−23 bytes** on every `shellscale_programs_*` and
      `shellscale_routines_*` file, dead flat from n=1 to n=200. A fixed
      per-file baseline offset, worth 0.09% at the small end and 0.03% at
      the large end. Too small to chase on its own, but it is real and
      exact, so it is probably one concrete unpriced item rather than
      accumulated rounding.
    - **−815 bytes** on all four `shellscale_crossed_*` files, also dead
      flat. These have the same Program and Routine counts as their pure
      counterparts (verified by element count) but come from a different
      generator, so something that generator emits — most likely the
      cross-program JSR wiring — costs 815 bytes that nothing prices. This
      one is worth identifying: 815 flat is 1.5% on a 54 KB file.

    Both are constants, not slopes, so neither affects the OQ-DEFSCALE
    reading above.

    **The `pool*` arm is CLOSED 2026-09-14 (segment 23). Nine rows, all nine
    inside the +-8 band, six byte-exact**: `control`, `bool03`, `dint04`,
    `real06`, `str82x2` and `strarr02` at 0, and `arr20`, `full` and `full_rungs`
    at +4. The two composed files are the point -- `full` and `full_rungs` carry
    every pool member at once and land in band, so the shell constants are
    additive and none of them needed changing.

    That does NOT close the two constants above: `pool*` is a different generator
    from `shellscale_*`, so the -23 and the -815 are untouched by it. The -815 in
    particular still wants identifying.


    **THE -23, LOCALISED 2026-09-12 -- and it is a TAG constant, not a shell or
    logic one.** A residual census over every clean generated capture: of 2,563
    files, 844 (32.9%) predict EXACTLY right and **263 (10.3%) sit at exactly
    -23**, by far the largest non-zero bucket. 23 is an odd number, which a
    memory allocation essentially never is.

    Narrowed in three steps:

      - 258 of the 263 contain real ladder rungs, so it looked like a logic
        term. It is not: the -23 is identical at 1 rung and at 27,267
        (`instr_*_n00010` and `randommix_00_n00609rungs` alike), so nothing
        about it scales with logic.
      - "Any file with logic" does not fit either -- among real-rung files 25.6%
        are at -23 and 20.2% are at exactly 0.
      - What separates the two groups is the **tag pool**. Every -23 family
        (`instr_*` 234 files, `shellscale_*`, `randommix_*`, `lbljmp_*`) shares
        one pool: 4 DINT, 6 REAL, 3 BOOL, a DINT[20], a CONTROL, a 2-element
        STRING array and two STRING(82). Every real-rung family at exactly 0
        (`cmpcpt_*`, `cptmix_*`) uses only DINTs, REALs and BOOLs.

    So this is a tag-sizing error. Two consequences: the instruction weights
    fitted from those 263 files are UNAFFECTED, because a constant pool cancels
    in every difference between counts -- but every absolute prediction carrying
    that pool is 23 bytes low.

    Already ruled out: the string shapes are exact. All 8 `customstring_*` files
    and every `stringarray_*` file (built-in and custom, n=1 to 100) predict to
    the byte. That leaves the **CONTROL** tag -- the only pool member with no
    isolation probe anywhere in the corpus -- and the DINT[20] array.

    **Test files built 2026-09-12, `gen_pool_residual.py`, 9 files.** Each pool
    member alone with no logic (`pool23_{dint04,real06,bool03,arr20,control,`
    `strarr02,str82x2}`), the whole pool with no logic (`pool23_full`), and the
    whole pool plus 10 XIC/OTE rungs (`pool23_full_rungs`). Differencing the
    seven single-shape files against `pool23_full` says which member carries the
    23; `pool23_full` against `pool23_full_rungs` pins it as pool-borne rather
    than logic-borne, since the two must read the same residual.

    Checked before shipping: the engine is internally additive here -- the seven
    parts sum to `pool23_full` net of the empty-project baseline with a
    difference of exactly 0 -- so the 23 is one of the seven constants being
    wrong, not an additivity failure, and each file measures one constant.


25. **OQ-VERIFINSTR** — **everything measurable from generated files is
    CLOSED and WIRED; see `docs/RESOLVED_QUESTIONS.md`.** The zero-operand half
    (MCR/TND/UID/UIE, 20 of 20 rows exact), the ten weights found unreconciled
    2026-09-12, `DTR = 40`, and the 112-per-target SBR/RET operand cost are all
    in the engine, with the last two in MEMORY_MODEL.md's KNOWN register.

    **What is left cannot be closed by a generated file, and needs one thing
    from James: a single verified rung apiece for `EOT`, `IOT`, `SFR` and
    `SFP`.** All four are real instructions with no entry in
    `logic_instructions.weights`, so every occurrence is charged zero.

    Files were written for them and WITHDRAWN rather than shipped, which is the
    part worth remembering:

    - `lint.py` rejects all four as unrecognized — accurately, since no real
      rung containing one has ever been verified into this project.
    - `SFR`/`SFP` address an SFC routine by name and this project's builders
      produce none, so the rung would name a routine that does not exist.
      Studio would reject that rung, the rest of the file would still import,
      and `actual_bytes` would still be filled in — the exact mechanism behind
      OQ-AOIINTERNALLOGIC's suspect calibration, arrived at deliberately.
    - `IOT`'s operand is a real output module reference and `EOT`'s an SFC
      storage bit, so both invented shapes are guesses.

    Per CLAUDE.md's transplant-never-compose rule these need one real rung each,
    not a composed one. Tracked in `docs/INSTRUCTION_COVERAGE.md`.


26. **OQ-CPTREALDEST** — REAL-destination CPT: two measured constants with
    no known mechanism. 2026-09-04. **Not blocking — the path is exact on
    all 47 captured calls — but both terms are descriptions, not theory,
    and a model you cannot explain is a model that will surprise you on a
    file you have not seen.**

    The ladder itself is clean and tier-blind: `124 + 40n`, and fitting
    `a + b*tier1 + c*tier2` against the opcount files returns b = c = 40
    (which makes sense — it is all float arithmetic, so a MUL should not
    cost more than an ADD the way it does on the integer path). Sitting on
    top:

    - **A 5-operator expression measures 328, not the 324 the ladder
      says.** Three files from three different generators
      (`cptmix_real*`, `cptcx_constants_floatconst_n4`,
      `instr_cpt_literaloperands`) independently agree on 328, and 6 and 8
      operators are back on the ladder exactly (364, 444). So it is not a
      ">= 5" step — the previous model had it as one and over-charged the
      6- and 8-operator files by 4 each.
    - **`**` adds 8, plus another 4 when the expression also contains a
      tier-2 operator**, and a pow expression does NOT get the 5-operator
      bump (`powmulti_n05` is 324+12, not 328+12).

    Two ad-hoc +4s is one too many to be comfortable. `cptrdops_n07/09/10`
    fills the ladder either side of the anomaly, `cptrdpow_k2/k3` tests
    whether pow_extra is per-operator or per-call (every existing real-dest
    pow file has exactly ONE `**`), and `cptrdarrange_*` tests whether the
    5-operator +4 is really the same arrangement effect OQ-CPTARRANGE found on
    the integer path, wearing a different hat (that question is now closed and
    archived in `docs/RESOLVED_QUESTIONS.md`). Blocked on capture.

    **IN-DEPTH REVIEW 2026-09-18 — the captures landed, and the FIRST thing
    they say is that every number in this batch had to be normalised before it
    could be read. Two of the sub-questions are now closed.**

    **(0) A per-file constant of −352 runs through the whole `gen_cpt_closeout`
    batch, and it is why this looked unreadable.** Of the 58 captured `cpt` rows
    from it, 53 sit at −352 plus a whole number of 4-bytes-per-rung; the other
    five — `cptwide_lint_k1..k4` and `cptwide_mixed_sint_lint` — sit on a
    baseline of **0**. The discriminator is exact and mechanical: **a file whose
    logic REFERENCES one of the pool's LINT tags has baseline 0; one that does
    not has baseline −352.**

    With that one substitution, **every one of the 58 residuals is its baseline
    plus an exact multiple of 4 bytes per rung. No exceptions.** That is what
    makes the batch usable, and it is also a warning: any conclusion drawn by
    differencing a file in this batch against a file from an OLDER generator
    carries a spurious 352, and several readings in this entry were contaminated
    that way before this was found.

    The −352 itself is NOT explained. It is numerically 4 × 88, the engine's
    charge for the four unreferenced LINT tags `N0..N3` that `gen_cpt_closeout`
    adds to the shared pool, so the arithmetic is consistent with "unreferenced
    LINT tags cost nothing, and referencing any one of them costs the full 352".
    That reading is uncomfortable — it makes one reference pay for four tags —
    and the measured standalone LINT tag slot is 4 bytes (`type_lint_50tag`,
    KNOWN), which does not obviously produce 88. Not patched. Recorded as the
    normalisation it is, with its own probe named below.

    **(1) The REAL-dest operator ladder is EXACT at 7, 9 and 10 operators.**
    `cptrdops_n07/n09/n10` all sit precisely on baseline, so `124 + 40n` holds
    and there is no ">= 5 step". That half of the question is closed.

    **(2) The 5-operator anomaly is NOT an operator-count effect, and it is not
    resolved either — it is now a CONTRADICTION between shapes.** The two
    all-REAL, unparenthesised 5-operator files built for this
    (`cptrdarrange_alternating_n05`, `cptrdarrange_grouped_n05`) both read −4 per
    rung against `operator_count_base[5] = 328`: they measure the ladder's 324.
    The three older families that pinned 328 still measure 328 and are still
    exact.

    | n=5 REAL-dest shape | measures |
    |---|---:|
    | all-REAL, no parentheses, `R0+R1*R2+R3*R4+R1` | **324** |
    | parenthesised, mixed DINT/REAL, `(R0+L1)*L2-L3/L4+L5` | 328 |
    | nested parentheses, `L5+(L4-(L3/(L2*(R0+R1))))` | 328 |
    | no parentheses, three float literals, `R0*1.5+R1*2.5-R2/3.5` | 328 |

    No single discriminator covers all four. Parenthesisation explains the middle
    two and fails on the last; integer operands explain the middle two and fail
    on the last; the leading-tier-1-run rule that CLOSED the integer path (see
    OQ-CPTARRANGE, now archived) predicts 324 for the run-of-1 rows and breaks
    eight of them.
    **Left at 328, unchanged**, because every candidate change fixes fewer rows
    than it breaks — applying the integer path's rule here with base 324 fixes 4
    and breaks 10. Counted, not guessed at.

    **(3) `**` on the REAL-dest path is per-operator, and the rate is not what is
    wired.** Normalised, `cptrdpow_k2` is **+12 per rung** and `cptrdpow_k3` is
    **+20** — a clean +8 per additional `**`, which answers the question the two
    files were built for: per operator, not per call. The wired `pow_extra: 8`
    plus `pow_with_tier2_extra: 4` charges a flat 12 for any count, so it is
    right at k=1 by construction and 8 short per extra `**`. NOT wired, and the
    reason is (2): `cptrd_powmulti_n05` is a 5-operator pow row, so the pow base
    and the 5-operator base are entangled and moving one moves the other. They
    have to be settled together.

    **(4) The narrow-operand rate is badly wrong, and SINT and INT do not
    match.** Normalised per rung — SINT k=0..4: 0, **−92**, **−44**, 0, **+44**;
    INT k=0..4: 0, **−80**, **−20**, **+36**, **+92**. Both monotone in k with a
    roughly constant step after k=1 (SINT ~+48 per operand, INT ~+56) and a large
    negative jump at k=1, so the one-point fit `3*40 + 136` is wrong in base and
    rate, and the assumption that the two narrow types behave identically is
    refuted. That belongs to OQ-CPTNARROW below and is cross-referenced rather
    than duplicated.

    **(5) A float literal with an INTEGER destination is unpriced, and it is
    large.** `cptidflit_k1/k2/k3` normalise to **+120, +124 and +188 per rung**:
    the integer CPT path charges nothing at all for a float literal where the
    REAL path charges 4. These three files exist precisely because no
    integer-destination CPT capture had ever contained one, and real logic writes
    `CPT(Dest,A*1.5+B)` routinely. **120+ bytes per rung is the largest single
    unpriced CPT term found in this project.**

    **NOT wired, and the reason is a CONFOUND IN THE FILES rather than a hard
    law.** The three shapes vary the operator count alongside the literal count:

        file            expression                 operators  float lits  per rung
        cptidflit_k1    L0*1.5+L1                       2          1         +120
        cptidflit_k2    L0*1.5+L1*2.5                   3          2         +124
        cptidflit_k3    L0*1.5+L1*2.5-L2/3.5            5          3         +188

    So "not linear in the literal count", written here earlier the same day, was
    the wrong diagnosis. Fitting `a x literals + b x operators + c` reproduces
    all three EXACTLY — a = −56, b = +60, c = +56 — and that is worthless:
    three parameters against three points is exactly determined, unfalsifiable,
    and it returns a NEGATIVE per-literal rate, which is not a thing. Same trap
    OQ-STEXPR-OPERATOR was stuck in, except there a regime split dissolved it and
    here there is nothing to dissolve.

    **What is needed, in priority order.** (a) FOUR integer-destination files at
    a FIXED operator count of three, varying only the float literals:
    `L0*1.5+L1*L2` (1), `L0*1.5+L1*2.5` (2), `L0*1.5*2.5+L1` (3) and
    `L0*1.5*2.5*3.5` (3 again, moved) — the last pair separating literal COUNT
    from literal POSITION. The 1..6 sweep at a fixed operator count written here
    before would have repeated the confound, because the existing files' operator
    skeleton is what changes between them. This is still the biggest number
    here. (b) Three files to settle the −352: the identical rung shape with the
    pool's LINT tags removed entirely, with exactly one LINT tag, and with four
    of which one is referenced. (c) An n=5 REAL-dest discriminator set — all-REAL
    parenthesised, all-REAL with one float literal, mixed-operand unparenthesised
    — which separates the three candidates for (2) in three files.


    **CAPTURE ERRORS: 1 row(s)** flagged here by `scripts/capture_errors.py` (step 2b), 2026-09-11.
    1 captured WITH Studio build errors, so their `actual_bytes` is
    SUSPECT rather than wrong — part of the file may never have reached the
    controller, which inflates apparent over-prediction. None of them carries
    any error text: every errored row in the manifest was captured between
    2026-08-23 and 2026-09-08, and the error-log reader only began working
    2026-09-10, so these need RECAPTURE before their numbers are used.
    `cptrd_operand_bool`


27. **OQ-CPTNARROW** — how the SINT/INT → DINT widening scales. 2026-09-04.

    2026-09-04: INTs use a behind-the-scenes conversion to DINT. That is
    the mechanism, and it resolved two things at once:
    LINT operands cost **nothing** (already 64-bit, no widening), and
    SINT/INT operands cost **+256/rung** on the 3-operator all-REAL control.

    **What is NOT determined: how that 256 splits.** There is exactly one
    file in the corpus with narrow operands in a REAL-destination CPT
    (`cptrd_operand_sint`, 3 SINT operands). 256/3 is not an integer, which
    rules out a pure per-operand rate, but per-call, per-operand-plus-block
    and per-conversion-site all fit that single point identically. The
    model currently charges `3*40 + 136` — the ordinary per-int-operand
    conversion each operand pays, plus one widening block per call. That
    split has a physical story and no evidence.

    It matters for real files, which have arbitrary SINT/INT counts: if the
    truth is per-operand, a 10-narrow-operand expression is wrong by ~600
    bytes per call.

    `cptnarrow_{sint,int}_k0..4` varies ONLY the narrow count at a fixed
    3-operator shape (k=0 must reproduce the 244/rung control, which is the
    built-in check that the batch is comparable). INT is swept alongside
    SINT because the model assumes they behave identically and that has
    never been tested — this project already assumed LINT belonged in the
    same set and it turned out to cost nothing. `cptwide_lint_k1..4`
    confirms LINT is free at every count rather than just at the one count
    (3) the single existing file happens to use, and
    `cptwide_mixed_sint_lint` covers mixed integer WIDTHS, which nothing in
    the corpus does. Blocked on capture.



    **CAPTURE ERRORS: none. RECAPTURED CLEAN, verified 2026-09-18.** The rows
    this entry used to flag as captured-with-errors now carry `error_count = 0`
    in the manifest, so their `actual_bytes` is trustworthy and every number
    above is drawn from clean captures. `scripts/capture_errors.py` routes no
    errored row here any more; the old block was a warning that had outlived
    its cause.


    **SOLVED 2026-09-18, and deliberately NOT wired. The law is
    `rate_T x k - 132`**, where k is the number of narrow operands in the
    expression and `rate_T` is per narrow type. Differenced against
    `cptnarrow_*_k0` (the same expression with every operand REAL), 100 rungs
    each, so the file base and the operator structure both cancel:

        k          1      2      3      4      rate   intercept
        INT      -80    -20    +36    +92        56       -132
        SINT     -92    -44     +0    +44        44       -132

    Eight of the ten points are EXACT on that form. Both types share the same
    -132 intercept, which is what makes it a law rather than two curve fits, and
    the two misses are a consistent **-4 at exactly k=1 in both types** -- not
    noise, and unexplained.

    **Why it is not wired: it cannot move the real set.** Across all sixteen real
    programs there are **27 CPT calls with any SINT/INT operand, and they are all
    in ONE file** (by narrow-operand count: 7 at k=1, 12 at k=2, 7 at k=3, 1 at
    k=7). At these rates that is on the order of 1,300 bytes on a single program.
    CLAUDE.md's rule applies as written -- a task that does not move real
    prediction error toward 1% waits -- so the derivation is recorded here and
    the wiring is not spent now.

    Two things to carry forward when it is wired. The k=7 real call is outside
    the measured range (k goes to 4 here), so the rate's linearity past 4 is an
    extrapolation. And the -4 at k=1 should be resolved first: a single
    `cptnarrow_{int,sint}_k1` variant with the narrow operand in a non-leading
    position would say whether it is positional.


28. **OQ-CPTTYPEMISMATCH** (the one thread OQ-CPTARRANGE left open; that
    question itself is CLOSED and wired — see `docs/RESOLVED_QUESTIONS.md`).

    A CPT whose destination and operands disagree in type costs more, and
    nothing in the model has a term for it.
    `cptdest_d{dint,real}o{dint,real}_n{00010,00100,01000}` is a clean 2x2 on
    one shape (`L0+L1*L2+L3`, three operators, four operands):

        destination   operands      residual per CPT
        DINT          4 x DINT                     0
        DINT          4 x REAL                   +48
        REAL          4 x DINT                    +4
        REAL          4 x REAL                     0

    Exactly linear across a 100x span in all four arms, and **both matched arms
    are byte-exact at every count** — an independent validation of the
    integer-tier and REAL-destination models at scale.

    **Not wired: one operand count cannot separate a per-call cost from a
    per-operand one.** +48 on four REAL operands is equally 48 per call or 12
    per operand; +4 on four DINT operands equally 4 per call or 1 per operand.

    Real exposure was measured before deciding: **3 of the 256 CPT calls in the
    sixteen real programs** are integer-destination with a REAL operand or float
    literal, roughly 144 bytes across the whole real set. No pressure to guess.

    **Discriminator: the same four arms at two operand counts (2 and 8),
    operator count held at three.** Four files settle both constants outright.


29. **OQ-STEXPR** — **the four assumptions and the AOI-call separation are
    CLOSED and WIRED 2026-09-18; see `docs/RESOLVED_QUESTIONS.md` for the
    derivation and `docs/MEMORY_MODEL.md`'s KNOWN register for the constants.**
    The ST family went 8.3291% -> 0.0091% mean absolute error, 60 of 69 rows
    byte-exact, 67 of 69 inside the universal ±8.

    **Three single-point threads survive, and they are the only ST rows outside
    that band:**

    - `st_jsr_param_target_n00100` is the only non-exact ST file (+228). Every
      JSR parameter constant was fitted on RLL targets and the corpus holds 63
      SBR / 42 RET inside ST, so an ST JSR target is a real shape that may be
      charged differently. One file with the same target at a second call count
      separates a per-call error from a per-file one.
    - `st_ctl_case` carries a −32 residual; the CASE decomposition into
      per-construct and per-selector is one data point short.
    - `while_block` was corrected 72 -> 76 on the strength of the literal-RHS
      rate. Only one WHILE file exists, so that split rests on a substitution.
      A WHILE-count sweep at fixed assignment content settles it outright.

    None of the three is worth a batch on its own; they are the natural
    passengers on the next ST batch, whatever drives it.

    **CAPTURE ERRORS: 1 row(s)** — `st_instr_concat_n01000` captured WITH Studio
    build errors, so its `actual_bytes` is SUSPECT rather than wrong: part of the
    file may never have reached the controller, which reads as the model
    over-predicting (it sits at −52,000). No error text was recorded — it was
    captured before the error-log reader worked — so it needs RECAPTURE before
    its number is used, and it is excluded from every ST figure quoted above,
    including the 0.0091%.


30. **OQ-REAL5069** — *amended 2026-09-14 by the strip ladder: the
    "identical content, identical residual" result holds and is not in doubt,
    but it was measured on GENERATED files. On real exports the two platforms'
    bare shells differ by 3,736 where the engine has them 8 apart. Read this
    entry as "no per-platform CONTENT model is needed", not "the platform
    difference is fully wired". The residue is unpriced controller-shell
    content — see OQ-CTLSHELL.*
    **SHELVED 2026-09-11 until 2026-09-18. Not closed,
    and not to be raised again before then.**

    Two corrections belong on the record first.

    **The premise below is out of date.** Four of the sixteen real captured
    programs ARE 5069 (elmsdale and salamanca and superior on 5069-L330ERM,
    flarefunction on 5069-L320ERMS3). The platform is no longer unvalidated.

    **The platform breakdown that replaced it was worse than the stale
    premise, and it was mine.** Grouping the sixteen real files by processor
    family gave 5069-L330ERM a -4.00% median and called it the corpus's
    worst platform — with **salamanca at +1.08%, one of the four most
    accurate files in the whole set, counted inside that bucket.** Family
    sizes are n=1, n=2 and n=3. Those medians are not measurements.

    The disproof is already in the same table: **murraybros is -5.16% on a
    1756-L81E**, worse than every 5069 file, on the family with the best
    median. Whatever drives the large residuals is not the processor, and
    reading one into a catalog string is exactly the failure this file
    already documents once — the rejected per-platform baseline that fitted
    190 near-empty files beautifully and broke 612 real ones.

    `gen_platform_equivalence.py` and its 15 files are KEPT, uncaptured, for
    when this is picked back up. They are still the right experiment if the
    question turns out to be real; nothing about them assumes it is.

    Priority: low, by the project owner's call. The residual is real and
    lives somewhere else.

    **CAPTURED AND ANSWERED 2026-09-14 (segment 17). 10 of the 15 landed, and
    they say the platform costs nothing beyond the baseline constant already
    wired. CLOSED.**

    The design was: identical content at five densities on each of three
    processors, so flat-across-densities means a real constant, growing means a
    rate, and zero means the platform is not the cause. Each density unit is one
    `PlatEqUdt` tag (8 DINTs), one DINT tag and one rung, byte-identical across
    platforms.

        density   5069-L306ER    1756-L81E
              0             0            0
             25          -332         -332
            100        -1,232       -1,232
            400        -4,832       -4,832
          1,600       -19,232      -19,232

    **The two processors' residuals are identical to the byte at every density**,
    and both empty-project rows are exact (18,160 and 18,128 predicted and
    actual). So the entire platform difference is the 32-byte baseline constant,
    which is already wired exactly. There is no per-platform rate, and the
    rejected per-platform baseline that broke 612 files stays rejected for a
    second, independent reason: even if it had fitted, there is nothing for it
    to fit.

    That settles the question this entry was shelved on. It does NOT make 5069
    a validated platform end-to-end — see the residual below, which is shared
    and is not 5069's.

    **A real finding that is NOT the platform's, and must not be fitted here.**
    Both arms over-predict by exactly `12n + 32`, exact at all four densities on
    both processors. Each unit contains a UDT tag, a DINT tag and a rung, and
    **all three scale together in this family**, which is the collinearity trap
    this project has now hit seven times. Two of the three are independently
    exact elsewhere -- `dscale2_udt_u001_t{001..500}` is flat in tag count over
    a 500x span, so a UDT tag is not it, and `instr_*` sits in the universal +-8
    band to 5,000 instructions -- but the rung here is
    `XIC(PeBit0)MOV(0,PeDint0000)OTE(PeBit1);`, a three-instruction rung with a
    LITERAL MOV source, which no isolating family covers. So the 12 is not
    attributed. **The discriminator is three files at one fixed unit count, each
    carrying only one of the three components.**

    **`platform_plateql330_*` (5 rows) never captured**, so the equivalence
    result rests on two processors rather than three. A second 5069 model would
    confirm it; it is not needed to reach the conclusion, since the two arms
    already agree to the byte.

    ---

    *Original entry, retained for history:*

    **the 5069 platform has ZERO real-file validation.**
    Found 2026-09-05, while checking which platforms the real corpus
    actually covers.

    Every one of the nine real production exports in `samples/local/` is a
    **1756-L8x**:

    | file | processor | fw |
    |---|---|---|
    | k3m16_edgers | 1756-L82E | 32.04 |
    | murraybros | 1756-L81E | 35.05 |
    | emporium | 1756-L83E | 32.04 |
    | pukall_gang | 1756-L81E | 35.05 |
    | ipc_edgerline | 1756-L81E | 35.05 |
    | cmu | 1756-L82E | 35.05 |
    | emporiumedger | 1756-L81E | 35.05 |
    | mrfp_edger | 1756-L81E | 35.05 |
    | accutally | 1756-L83E | 35.05 |

    Everything the model knows about 5069 -- the safety-capable baseline
    delta (+304), the 5069 catalog entries in `module_overhead_by_catalog`,
    the 5069 processor baselines -- comes from files this project generated
    itself. Not one of them has ever been checked against a real 5069
    program.

    That is the same extrapolation risk as OQ-DEFSCALE, and it went
    unnoticed for the same reason: corpus-level pass rates looked healthy
    because the corpus is full of synthetic 5069 files that the model was
    fitted on. Per CLAUDE.md's accuracy rule (real programs only, generated
    files are an instrument not evidence), the honest statement is that
    **this tool is validated on 1756-L8x and unvalidated on 5069.**

    It matters more than the raw file count suggests: 1756-L7x and 1769 are
    now formally dead architecture (2026-09-05), which leaves
    5069/CompactLogix 5380 as the platform this tool most likely gets used
    on going forward -- and it is the one with no real evidence behind it.

    **What is needed:** one real 5069 export with a controller capture.
    An "Elmsdale" project is known to run on 5069, but that file is not in
    `samples/local/`. Any real 5069 program would do -- the point is a
    first real data point, not that specific one.

    Until then, the UI should arguably say so on a 5069 file the way it
    already warns on a Safety project. Not implemented yet -- flagged here
    rather than built, because a warning banner claiming more precision
    about its own uncertainty than the data supports would be its own kind
    of dishonesty.

    **CAPTURE ERRORS: none. RECAPTURED CLEAN, verified 2026-09-18.** The rows
    this entry used to flag as captured-with-errors now carry `error_count = 0`
    in the manifest, so their `actual_bytes` is trustworthy and every number
    above is drawn from clean captures. `scripts/capture_errors.py` routes no
    errored row here any more; the old block was a warning that had outlived
    its cause.


31. **OQ-AOISTRUCT** — **what an AOI costs to DECLARE, as a function of its
    structure rather than its name.** New, 2026-09-06, under two
    constraints set the same day: the AOIs in the worst-predicting real
    file also appear in other real projects, so they are not that file's
    problem; and the tool is going to people outside the organisation whose
    code will be different and whose AOI libraries will be entirely
    unfamiliar.

    Those two together rule out the tempting move. MurrayBros' residual
    correlates hardest with AOI structure (aoiaxisparam +0.889, aoirungs
    +0.848, aoidefs +0.838, aoilocals +0.835), and the shared definitions
    that recur across the nine projects (`PTimer`, `HomeToTorque`,
    `SpecialInputs`, `T_ADD`, `T_DST`, `AnalogSensor`, `Debounce`,
    `ts_PilotLight`, `VirtualAxis`, `ts_AxisGap`, `TierPinchAOI`,
    `ts_TotalSB` are byte-identical across projects) would make a
    per-AOI-name correction table easy to fit and worth exactly nothing to
    a stranger importing an L5X full of AOIs this project has never seen.

    **What the model prices today**, read straight out of
    `compute_aoi_definition_cost` + `AoiDefinitionModel.bytes_for`: base
    1184, plus a per-type rate (BOOL 16 / SINT 18 / INT 18 / LINT 24,
    single-type definitions only) or a flat 20 per declared item, plus AOI
    TYPE-name length buckets. That is the entire function.

    **Seven structural properties are therefore priced at exactly ZERO**,
    each of them an untested assumption rather than a measurement, and
    each measured against the real corpus (81 AOI definitions / 2,120
    Parameters+LocalTags in `samples/local`):

    | # | unpriced property | real corpus evidence |
    |---|---|---|
    | 1 | member NAME length | mean 12.1 chars, max 32; tag names elsewhere in this model cost 8 bytes per 8-char chunk |
    | 2 | member DESCRIPTIONS | 803 of 2,120 carry one; **zero** generated files ever emitted one |
    | 3 | InOut parameters | skipped outright by `compute_aoi_definition_cost`; 94 real ones, and the only legal way to pass an array/STRING/MESSAGE/UDT into an AOI |
    | 4 | predefined-structure members | TIMER 557 real member uses, DateTime 120, COUNTER 66, STRING 58, MOTION_INSTRUCTION 36, MESSAGE 15 — **none ever generated**; all fall off the per-type table onto the flat atomic rate |
    | 5 | array dimensions | a member counts once whether scalar or `Dimensions="1024"`; 46 real dimensioned AOI members |
    | 6 | member counts past the fitted range | real AOIs run to 102 params / 128 locals / 85 internal rungs (median 12/11/11); the generated corpus topped out near 6/2/1 |
    | 7 | extra internal routines | 7 of 81 real definitions carry an EnableInFalse and/or Prescan routine besides Logic |

    #6 is the identical extrapolation shape as OQ-SHELLSCALE (a constant
    fitted at n=2, applied at n=200, wrong by 8 bytes/unit and invisible
    until the ladder was built) and OQ-DEFSCALE. Both of those were real.

    **`gen_aoi_structure.py`, 56 files**, one property per group, everything
    else held fixed — including the AOI type name, which IS priced and
    would otherwise contaminate every reading:

    | group | files | varies |
    |---|---:|---|
    | `aoistr_namelen_c{04,08,12,16,20,28,40}` | 7 | member name length, 20 DINT params |
    | `aoistr_desc_l{000,016,064,256}`, `_all_l{000,064}`, `_aoidesc_l256`, `_aoirevnote_l256` | 8 | member and AOI-level description text |
    | `aoistr_inout_n{00,04,16,48}` | 4 | InOut param count |
    | `aoistr_predef_{base,timer,counter,motion,string,msg_inout}_n{01,08}` | 11 | predefined-structure member type |
    | `aoistr_dim_{base,local_atomic,local_timer,inout}_d{8,64,512}` | 9 | array dimension |
    | `aoistr_scale_{param,local,rung}_n*` | 12 | member/rung count to the real p90 and past it |
    | `aoistr_routines_n{1,2,3}` | 3 | internal routine count, total rungs held at 24 |
    | `aoistr_real_{median,p90}` | 2 | composite: do the isolated parts add? |

    **The design property that makes this readable**: the model predicts a
    DEAD FLAT line across every group except the three scale sweeps —
    19,712 for all seven name-length files, 19,472 for all nine
    inout/predefined files, 19,392 for all nine dimension files, 20,352 for
    all three routine-count files. Any spread at all in the captured
    numbers is an unpriced item, with no fitting or disentangling required
    to see it.

    Platform is 1756-L81E fw35.05 for all 56 — the same processor and
    firmware as MurrayBros and MRFP_Edger, so nothing here is confounded by
    OQ-BASELINE-PROCFW.

    Only the two composites are instantiated; the other 54 are
    definition-only, so what is captured is the declaration cost itself
    with no tag_overhead or member storage mixed in.

    Three generator gaps had to be closed to build this and are worth
    recording, because each one was a silent hole rather than a deliberate
    omission:
    - `builders.py` could not emit a predefined-structure AOI member at
      all. The atomic path writes a bare `Radix` + scalar `DataValue`
      (wrong for TIMER); the nested-UDT path writes an L5K value list that
      does not match the real positional encoding (a real TIMER LocalTag's
      L5K default is `[0,1500,0]` — three fields for five members, because
      EN/TT/DN alias into the leading status word). `predefined_members.py`
      now supplies the exact block captured from the real corpus rather
      than a guessed encoding that would only have failed in Studio 5000,
      costing a capture run to discover.
    - `builders.py` could not emit a member `<Description>`, an AOI-level
      `<Description>`/`<RevisionNote>`, or an `EnableInFalse`/`Prescan`
      routine. All three now render in the real shape and order
      (Description then RevisionNote before `<Parameters>`; routines
      alphabetical as EnableInFalse/Logic/Prescan, with the matching
      `ExecuteEnableInFalse`/`ExecutePrescan` attribute flipped to "true").
    - `lint.py`'s missing-array-subscript rule fired on an array InOut
      Parameter passed bare to an AOI call — which is the correct real
      form (LOG_HMIDisplay `Dimensions="25"`, BitArray
      `Dimensions="1024"`). Exempted at the AOI call site. This project had
      never before wired an array InOut param to an actual caller, so the
      rule had never been exercised against it.

    **Blocked on capture.**



32. **OQ-MODULEMARGINAL** — the last ASSUMED exposure that reaches a real
    file. 4.15% of real-file bytes on the current engine, of which the 2198
    `-ERS3` drives are 4.07% and eleven other catalogs are the rest. The
    worst-exposed real files are `k3m16` (7.06% ASSUMED), `horizon` (7.00%)
    and `ipc` (6.44%), and every ASSUMED byte in all sixteen real files is a
    `module_io` entry — nothing else in the model is both ASSUMED and
    reachable from a real export.

    **CAPTURED AND RECONCILED 2026-09-11, 54 files (`asmclose_*`, n=1/2/4
    per catalog). The marginal law is exact, and it must not be wired on
    its own.**

    Over-prediction is exactly linear in the module count, with zero
    residual at n=1, n=2 and n=4 for every catalog:

        over-prediction(n) = discount x (n - 1)

        1794-AENT                 432      1756-EN4TR             1520
        1734-AENT/B               520      1756-IB16IF/A          2208
        1734-AENT/C               520      440C-CR30-22BBB/A      3768
        1756-IB16                 792      AL1222                    0
        1756-IB32/B               792      842E-CM-M              1000
        PowerFlex 755-EENET-CM-S  976

    So the model charges every module full price and the controller charges
    the first one full price and `full - discount` for the rest.

    **The AL1222 "control" is void — corrected 2026-09-13.** This entry
    previously read AL1222's discount of exactly 0 as the control proving a
    real per-catalog-shape property rather than a flat per-module fudge.
    `asmclose_al1222_1conn_n{01,02,04,08}` all read **18,128 — the bare
    baseline — at every one of the four counts**, with distinct module names
    and zero import errors. A module cannot cost the same at n=8 as at n=1,
    so the AL1222 modules never reached the controller at all. A catalog that
    contributes nothing has a zero discount trivially and is a control for
    nothing. (The table's `'AL1222': bytes: -793` is an artifact of the same
    non-arrival: it happens to cancel the 850 declared bytes, which is why
    the n=1 row still lands within 57.) The per-catalog reading is now
    settled on real evidence instead — see the mixture arm below.

    The 2198 `-ERS3` family does not fit that form — it carries an extra
    flat error at n=1 as well:

        D012 / D020 / D032 / D057   +6,384 at n=1, then +7,368 per extra
        S086-ERS3                   +3,264 at n=1, then +4,248 per extra
        S130-ERS3                   +3,228 at n=1, then +4,212 per extra

    i.e. a drive after the first costs 984 less than the first, AND the
    first is itself over-charged. This is the single largest ASSUMED block
    in the project.

    **WIRED 2026-09-13 for ten of the seventeen catalogs. The blanket "makes
    every real file worse" reading was true and the conclusion drawn from it
    was wrong.** Applying all seventeen rates removes 189,570 bytes across
    216 repeated modules in the sixteen real programs and does make all of
    them worse. Attributing that catalog by catalog, which had not been done,
    puts **95% of it in two families**: ETHERNET-MODULE (67,450 bytes) and the
    six 2198-*-ERS3 drives (112,176). With those two held out, the other ten
    catalogs move the real programs by 10,464 bytes across 47.4 MB:

        variant                                   mean |%|   sum-weighted
        discount off                                1.6009       +1.2370%
        all 17 catalogs                             1.7492       +1.6298%
        without ETHERNET-MODULE and 2198-*-ERS3     1.6289       +1.2579%

    So the ten ordinary I/O and adapter catalogs are neutral on real files to
    within noise, while taking the `asmclose_*` rows from 16 byte-exact to 47.
    Both exclusions are on shape grounds and were decided from the shapes, not
    from which way they moved the number:

      - **ETHERNET-MODULE is not a catalog.** It is a generic placeholder
        whose cost is driven by connection sizes typed in by hand — 109
        instances across the sixteen real programs carry 40 distinct
        connection shapes, which is why `module_connection_data` exists. The
        `genem_n{01,02,04,08}` sweep cloned ONE shape, so its 710-byte repeat
        rate is the cost of a second identical clone and says nothing about a
        second differently-configured device.
      - **2198-*-ERS3 was measured on bare drives with no axis tag,** which no
        real program contains. Arm C exists to fix exactly that and every one
        of its six rows captured WITH Studio build errors, so the with-axis
        rate is still unmeasured.

    The compensating-error problem stated in OQ-REALGAP survives this and is
    now better quantified: with the ten clean catalogs wired, the real-file
    under-prediction is +1.2579% sum-weighted, and the honest figure once the
    two suspect families are also resolved is nearer +1.63%. That is the size
    of the gap OQ-REALUNDER has to close, and it is larger than the headline
    suggested.

    **PER-CATALOG, NOT PER-FILE — SETTLED 2026-09-13 by Arm B.** Every one of
    the 54 single-catalog captures fits both readings identically:

      - PER-CATALOG — the first module *of each catalog* pays full price:
        error = sum over catalogs of `d_i x (n_i - 1)`
      - PER-FILE — the first module *in the file* pays full price and
        everything after it is discounted whatever its catalog:
        error = `sum(d_i x n_i) - d_first`

    On a single-catalog file these are the same number; on a real program
    carrying 20-60 modules across 10-20 catalogs they differ by most of the
    module total. The mixtures separate them three independent ways and all
    three say PER-CATALOG:

        quadruple   sum(d)   over-prediction at x2   x2rev     at x1
        mixq1        2,744            2,834          2,834        33
        mixq2        7,472            7,424          7,424       -32
        mixq3        7,080            7,048          7,048        24

      1. `x2rev` is **byte-identical** to `x2` in all three quadruples. Under
         PER-FILE the total has to move by `d_first - d_last` (1,224 / 3,704 /
         3,312 here). It does not move at all.
      2. The `x1` residual is ~0 against a PER-FILE prediction of
         `sum(d) - d_first`, i.e. 1,224 to 6,944 bytes.
      3. The `x2` over-prediction equals `sum(d)` to within 90 bytes on a
         five-module file whose own baseline residual is already ~30.

    This is what the engine already implemented, so no code changed — but it
    was an assumption until now and is now measured.

    **Test files built 2026-09-11, `gen_module_marginal.py`, 36 files.**

      - **Arm A, 17 files** (`asmclose_*_n08`) — n=8 for every catalog that
        already has n=1/2/4, from the same builders so it differences
        straight against n=4. This is the first point that can FALSIFY the
        law: three points fit it exactly but two of them define it, so a
        per-rack or per-connection-block step above four modules would be
        invisible in the existing data.
      - **Arm B, 9 files** (`modmarg_mix{q1,q2,q3}_{x1,x2,x2rev}`) — the
        decisive experiment. Three quadruples of catalogs with widely
        separated discounts, each at 1 and 2 copies per catalog. The two
        readings are separated by 2,744 / 6,952 / 6,288 bytes on the `x1`
        and `x2` files, on files that are otherwise exact to the byte, so
        one capture each settles it. The `x2rev` files reverse module order
        within the file: PER-FILE requires the total error to move by
        `d_first - d_last` (1,224 / 3,704 / 3,312 here), PER-CATALOG
        requires it not to move at all — so the mixture is self-checking
        rather than one arithmetic coincidence.
      - **Arm C, 6 files** (`modmarg_drvaxis_*`) — the -ERS3 drives WITH
        their axis (one `AXIS_CIP_DRIVE` per drive plus the one shared
        `MOTION_GROUP`), at n=1/2/4/8 for D012 and n=1/2 for S086. All 54
        `asmclose_*` files hold bare drive modules with no axis tag; a real
        program never does. Differencing against the bare-drive capture at
        the same count separates the drive's own marginal cost from the
        axis's, which is the form the cost actually takes on a real file.
      - **Arm D, 4 files** (`modmarg_ob32chain_n{01,02,04,08}`) — see the
        contamination note below.

    **Contaminated data found and cleared, 2026-09-11.**
    `asmclose_1756_ob32_rackaliased_n02` and `_n04` are not usable and their
    capture columns have been cleared. The 1756-OB32 block is the only
    2-deep chain in the set (a 1756-EN2T adapter plus the output card behind
    it), and the copier that multiplies a module block renames only the
    FIRST `<Module>` in it. Every copy after the first therefore shipped an
    identically-named OB32 still pointing at `ParentModule="<the first
    adapter>"` and still sitting in the same slot 3. Studio merged the
    identical duplicates instead of rejecting them, so both files captured
    at ZERO import errors while measuring N adapters sharing ONE output
    card. The "1756-OB32 discount = 1760" read off them is therefore not a
    discount at all — it is the cost of the cards that never got imported.
    `lint.duplicate_module_name` now catches this class outright; a
    corpus-wide sweep found these two files and no others. Arm D rebuilds
    the full n=1/2/4/8 sweep under a new sample_id, with every module in
    every copy renamed and its `ParentModule` repointed at its own adapter,
    rather than regenerating in place — regenerating in place would leave
    the old captured `actual_bytes` attached to different file content.

    One catalog is still deliberately not covered and is reported rather
    than faked: **150 SMC Flex-E** (0.069% exposure) has no real module XML
    in either sweep table, so there is nothing verbatim to build from. It
    needs a real export before it can be tested at all.

    **Arms A, B and D captured and reconciled 2026-09-13. Arm C is the only
    one still outstanding, and it is outstanding because all six of its rows
    captured with build errors.**

      - **Arm A (n=8) does not falsify `d x (n - 1)`.** 64 of the 71
        `asmclose_*` rows land byte-exact with the discount applied against 16
        without it, and the marginal is flat at every one of n=1/2/4/8 on 13
        catalog families. A per-rack or per-connection-block step above four
        modules would have shown here and does not.
      - **Arm B settled per-catalog vs per-file** — see above.
      - **Arm D (`modmarg_ob32chain_n{01,02,04,08}`) reads 21,760 / 24,080 /
        28,720 / 38,000**, a flat marginal of **2,320 per additional
        EN2T-plus-OB32 chain** against a modelled 3,544 — so a 1,224 discount
        per chain, exact at three counts. It does **not** split between the two
        catalogs: one equation, two unknowns. The n=1 point gives the pair at
        88 bytes over what the table charges, which is the second equation, but
        both equations are the pair rather than either catalog. **The missing
        file is an EN2T-only count sweep** (n=1/2/4/8, every copy under
        `Local`, no downstream child): differenced against Arm D it gives
        1756-EN2T's own rate and leaves rack-aliased 1756-OB32 by subtraction.

    **PER-RACK VS PER-PROJECT: implemented, measured, and irrelevant on real
    files.** This was recorded as the open scope question and as the reason the
    discount could not be wired. `ModuleOverheadModel.repeat_scope`
    (`project | parent`) now implements both, and they produce **byte-identical
    totals on all sixteen real programs**. The reason is structural rather than
    lucky: in every one of the sixteen, no catalog carrying a measured repeat
    rate ever appears under more than one parent module. Exactly one real export
    in `samples/local/` splits one at all (`BAI10048_TrimmerTally`, a 1756-IB32/B
    across two parents), and it is not in the held-out sixteen. So the question
    stays genuinely open — nothing in the corpus discriminates, because every
    copy in every captured sweep sits under `Local` — but it cannot be what made
    the real files worse, and it cannot change a real-file number until a real
    file contains a split catalog. Default is `project`.

    **A 16-byte disagreement on 1756-IB16, unresolved and small.** The
    additivity M axis (a file holding nothing but 1756-IB16 modules) gives
    1,704 first / 904 after; `asmclose_1756_ib16_1conn_n*` gives 1,684 / 892,
    which is what is wired. Both are byte-exact on their own zero points, so
    the two file shapes differ by 8 somewhere outside the module term. Flagged
    rather than chased: it is 16 bytes on a 1,712-byte constant.

    **ROOT CAUSE OF 33 ERRORED ROWS FOUND AND FIXED 2026-09-14.** A 2198 drive
    needs its 2198-P bus supply module AND that supply's converter axis -- an
    AXIS_CIP_DRIVE whose `AxisConfiguration` is `"Non-Regenerative AC/DC
    Converter"`, pointed at the supply's `Ch1`. Without them Studio converts the
    file and then fails Build, once PER DRIVE MODULE:

        Primary Bus Sharing Group 1 contains a module configured as Shared DC or
        Shared DC/DC with no module configured as Shared AC/DC or Shared DC -
        Non-CIP Converter.

    Only one of the 33 rows carried that text. The error COUNTS identified the
    rest: `axmarg_1cat_n{02,04,08,12,20}` record exactly 2/4/8/12/20 errors, and
    `axis_scale_n{02..20}_dual` -- the same axis counts on half as many modules --
    record n/2 + 1. Per drive module, not per axis.

    The representation is the one the `kinetix_drive_without_bus_supply` lint rule
    said it could not check: that rule tests only for a supply MODULE, noting the
    power group "is not an attribute of `<Module>` -- it appears nowhere in the
    real corpus either". It is on the AXIS_CIP_DRIVE TAG.
    `BaillieLeitchField_Edger` carries 25 `"Position Loop"` axes and 2 converters
    (`MotionModule="BUS_601A:Ch1"`, `"BUS_601B:Ch1"`); `SJ_Gormley` 27 and 2.

    **This also explains the -ERS3 family's otherwise unexplained EXTRA flat
    over-charge at n=1** (recorded above as +6,384 for the D-series before the
    per-extra-drive term). Those files had no bus supply either, so part of every
    one of them never reached the controller. That is why segment 14 excluded the
    2198 repeat rate as measured-on-a-broken-shape, and it means the six
    `'2198-*-ERS3': { bytes: 4113, confidence: KNOWN }` first-instance entries
    rest on the same broken captures and are **suspect, not KNOWN**.

    Fixed in `gen_module_motion.bus_supply_with_converter()`, which returns both
    halves together because needing one without the other is always a bug, and
    applied in `gen_assumed_closeout` (the n=1/2/4 2198 sweep), `gen_module_marginal`
    (Arm A n=8 and Arm C drive+axis), and `gen_axis_marginal`. A second real defect
    was corrected alongside it: `gen_module_axis_scale` put a dual drive's second
    axis on **Ch2**, and across the three real Kinetix exports there are 33 `Ch1`
    references, 25 `Ch3` and **no `Ch2` at all**.

    Two new lint rules make both unshippable: `kinetix_axis_without_converter` and
    `drive_axis_unreal_channel`. They caught 36 and 9 committed files respectively
    before the fix; the converter rule is down to 6 and the channel rule to 0.

    **48 rows had their capture columns cleared** -- 26 `asmclose_2198_*`, 9
    `axmarg_*`, 9 `axis_scale_*_dual*`, 6 `modmarg_drvaxis_*` (the last of which
    was Arm C, whose whole purpose was to measure the drives WITH their axes and
    which had failed for this exact reason). All need recapture. Nothing wired
    regresses: the 2198 repeat rate was already excluded in segment 14.

    **CAPTURE ERRORS: 6 row(s)** flagged here by `scripts/capture_errors.py`
    (step 2b), 2026-09-17 -- `modmarg_drvaxis_2198_d012_ers3_n{01,02,04,08}` and
    `modmarg_drvaxis_2198_s086_ers3_n{01,02}`. Was 0.

    **AND THEY FINALLY CARRY ERROR TEXT, WHICH DIAGNOSES A DEFECT IN EVERY
    GENERATED KINETIX FILE.** Studio says, once per drive:

        Drv1: Primary Bus Sharing Group 1 contains a module configured as
        Shared DC or Shared DC/DC with no module configured as Shared AC/DC
        or Shared DC - Non-CIP Converter.

    So the drive declares itself a **Shared DC** bus member and nothing in its
    group declares itself the **Shared AC/DC** converter. Adding the `2198-P208`
    module and its converter axis -- done on 2026-09-13 -- was necessary and is
    not sufficient: the P208 has to be configured as the converter *for that
    group*, and it is not.

    **Why, and it is a structural flaw in how payloads are stored.** Bus sharing
    lives inside the module's `ConfigData` L5K blob, not in any attribute the
    generator sets. `sample_gen/data/kinetix.py` keys payloads by CATALOG, but
    bus sharing is a per-PROJECT, per-BUS property, so a payload lifted from a
    shared-bus drive in one real export carries that export's bus role and group
    number into a generated file whose supply came from somewhere else. A table
    keyed on catalog alone cannot produce a coherent bus.

    **Located but NOT decoded, and it must not be guessed.** Across all real
    2198 drives the only indices that vary in a bus-shaped way are **50, 52, 58,
    62** in the 114-value (Major 9/11) layout and **51, 53, 59, 63** in the
    119-value (Major 13/14) layout -- one pair per channel, since 50 always
    equals 58 and 52 always equals 62. Griffin's drives read `(0,0)`, `(2,0)` or
    `(2,4)` there, which says plainly that **some real drives are standalone and
    some are shared** on the same project. That is consistent with 0 = standalone
    and 2 = Shared DC, but the enum is inferred, not measured, and no constant
    may be set from it.

    **The fix that needs no decoding, and the donor already exists.** Griffin
    carries three genuinely standalone drives -- `EM112_StickReclaimDeck`
    (2198-D012-ERS3), `EM114_StickUnscrambler` (D012) and `EM101_PkgDeck1`
    (D057) -- all reading `0` at every one of those four indices. A standalone
    drive requires no converter, so the error cannot arise, and the generated
    files would stop needing a P208 at all. Whether a standalone drive costs the
    same bytes as a shared one is then a question the corpus can answer, rather
    than a confound the corpus is silently carrying.

    Not done here because it changes the shape of every generated Kinetix file
    and that is a decision, not a cleanup. Suspect, not wrong:
    `actual_bytes` is filled in but part of the file may never have reached the
    controller, which reads as the model over-predicting.

    **MEASURED CLEANLY 2026-09-13 (capture-batch segment 5), and still gated
    off.** The additivity grid's M axis is a file containing nothing but
    1756-IB16 modules on the local chassis — no tags, no UDTs, no AOIs, one NOP
    rung — at 0, 4 and 16 modules, with the all-zero corner exact (18,392
    predicted, 18,392 actual). The over-charge is `808n − 800`, exact at both
    counts, which decomposes without ambiguity:

        first module    1,712 charged, 1,704 real   (8 out, inside the band)
        every one after 1,712 charged,   904 real   (808 out)

    So the repeat discount is real, it is 808 for this catalog, and the FIRST
    instance carries no discount at all. The existing
    `module_overhead_repeat_discount` table holds 1,684 / 892 for 1756-IB16 — a
    792 discount, 16 short of this — derived from the module sweeps rather than
    from a file with nothing else in it.

    `apply_repeat_discount` is **true** since 2026-09-13, for the ten catalogs
    whose rate was measured on a shape real programs contain. The reason it was
    false — that the sixteen real programs under-predict and a discount predicts
    less — held for the table as a whole and not for those ten: they are worth
    10,464 bytes across 47.4 MB. The per-rack-versus-per-project question this
    paragraph raised is implemented and measured above; it changes nothing on
    any of the sixteen.


33. **OQ-ALARMDEF** — *scope note added 2026-09-14: this entry covers the ALMD
    / ALMA INSTRUCTIONS only. Tag-based `<AlarmCondition>` elements are a
    separate feature, are present in real programs at 19–21% of total memory,
    and are NOT parked — see OQ-ALARMCONDREAL.*
    **PARKED 2026-09-14, not closed. Zero ALMD / ALMA /
    ALARM_DIGITAL / ALARM_ANALOG occurrences across all sixteen real programs**,
    verified by direct grep. Nothing in this entry can move real prediction
    error, so it waits behind everything that can, and no further alarm test
    files are to be generated. The `almd_*`, `alarmbits_*`, `alarmdef_*` and
    `alarmsep_*` families are parked with it. Revisit when real-file error is
    under 1% or a real program starts using the instruction.

    Datatype-level alarm definitions. **RESOLVED except one
    term, 2026-09-12, by reading the 68 `alarmdef_*` and 33 `alarmsep_*` rows
    TOGETHER for the first time. They collapse to a single law, and that law
    disproves what this entry previously recorded.**

        deficit = SUM over UDTs of (8 + 8 x floor(BIT_members / 2))

    Zero residual on 64 of the 68 `alarmdef_*` rows and on all 33
    `alarmsep_*`. `alarmdef_l81_d1_*` sits at -72 because its UDT has 16 BIT
    members and 8 + 8x8 = 72 exactly; d02/d04/d08 sit at -16/-32/-64 because
    each of their 2/4/8 UDTs has one BIT member at 8 apiece. Four processor and
    firmware variants (l81, l81 v35, l81 v38, l902ts) give identical numbers, so
    it is platform-invariant across the active set.

    **DISPROVED: "8 bytes per DatatypeAlarmDefinition".** That came off the d0N
    ladder, in which definition count and UDT count are both N -- perfectly
    collinear. `alarmsep_u04_b04_def{1,2,3}` breaks it: four UDTs held fixed
    while definitions run 1, 2, 3, 4, and all four files are BYTE-IDENTICAL. The
    8 belongs to the UDT, not the alarm definition. **Alarm definitions cost
    exactly ZERO**, now confirmed 19 ways -- 15 matched `_alarm`/`_noalarm`
    pairs plus the def1/2/3/4 quadruple. Had the 8/definition been wired it
    would have been a wrong constant on every real file, which all carry
    hundreds of conditions.

    **Also re-confirmed, and both already recorded:** operator message text is
    free (`msg_none/s/m/l` byte-identical), and member-alarm count is free
    (`d1_m00` through `d1_m16` byte-identical).

    **The +72 "does not fit, and is the reason nothing is wired" note in the
    previous version of this entry is closed.** The extra 64 bytes were never an
    alarm term: the `d1_*` UDT carries 16 BIT members against 2 in the d0N
    files, and the law above accounts for the difference to the byte.

    **THE "2 BYTES PER TAG" THREAD IS CLOSED 2026-09-14 (segment 21). It was
    never per-tag, and the per-tag bytes are now modelled anyway.**

    `alarmbits_b{08,16,32,64}_t{01,04,16}` sweeps BIT-member count against tag
    count. The residual is **flat in tag count on every one of the 12 rows** --
    -24 / -56 / -112 / -232 at 8 / 16 / 32 / 64 BIT members, identical at t01,
    t04 and t16. A per-tag term cannot do that.

    Re-run live against the current engine, the `alarmdef_*_t{01,04,16}` ladders
    that produced the -2 / -8 / -32 below now read **-56 flat**, identical to
    `alarmbits_b16_*`. So the per-tag 2 bytes was real and is now supplied by the
    standalone-UDT-tag 8-byte slot alignment wired earlier on 2026-09-14. Both
    families agree, and the hypothesis below is superseded rather than merely
    unconfirmed.

    **What is left is a per-DEFINITION term scaling with BIT-member count**, and
    it is not fitted. Backing 24 / 56 / 112 / 232 out of the engine's
    `8 + 8*floor(BIT/2)` charge leaves a required 16 / 16 / 24 / 32: flat to 16
    bits, then +8 per doubling. Four points, all powers of two, and no mechanism
    predicting a step there rather than at a 32-bit word boundary.
    **Discriminator: BIT counts BETWEEN the powers of two -- 12, 20, 24, 40, 48
    -- which is where a bucket law shows its step shape.**

    *Superseded hypothesis, retained because the numbers are still the record:*
    Exactly four of the 68 rows carry a
    residual beyond the law, and they are the tag ladders:

        inst_t01   -2      noinst_t01   -2
        inst_t04   -8      noinst_t04   -8
        inst_t16  -32      noinst_t16  -32

    2 bytes per tag, identical WITH and WITHOUT an alarm definition -- so a tag
    term, not an alarm term. Those files' UDT has 16 BIT members, and 16 bits is
    exactly 2 bytes, so the hypothesis with a mechanism behind it is that a
    BIT-member UDT tag's own backing storage goes uncharged at
    `ceil(BIT_members / 8)` bytes per tag.

    **Test files built 2026-09-12, `gen_alarm_bitbacking.py`, 12 files.**
    `alarmbits_b{08,16,32,64}_t{01,04,16}` crosses BIT-member count with tag
    count. Under `ceil(bits/8)` per tag the deficit beyond the law runs 1/4/16,
    2/8/32, 4/16/64, 8/32/128 across the grid; under a flat 2 per tag every row
    reads 2/8/32 regardless of member count -- 128 against 32 at b64/t16, on
    files whose other terms cancel exactly. Every existing file in the tag
    ladder has the same 16-member UDT, so the two readings fit it identically:
    the same one-variable trap the 8-per-definition claim fell into. No alarm
    definitions anywhere in the batch, since they are now known to cost zero.

    **Nothing is wired yet, and the reason is OQ-UDTMEMBERNAME.** The law above
    is the same `8 + 8 x floor(bool/2)` per UDT that OQ-UDTMEMBERNAME records,
    and it is contradicted there by `udttype_bool_n4` -- a structural twin with
    2-character member names that predicts EXACTLY while `alarmsep_u01_b04`
    with 7-character names is 24 short. Wiring the law would fix 97 rows and
    break that one, and the 47 pending `udtmn*`/`udtmn2*` files decide which of
    member-name length or BIT count is the real driver.

    **CAPTURE ERRORS: 1 row(s)** flagged here by `scripts/capture_errors.py` (step 2b), 2026-09-11.
    1 captured WITH Studio build errors, so their `actual_bytes` is
    SUSPECT rather than wrong — part of the file may never have reached the
    controller, which inflates apparent over-prediction. None of them carries
    any error text: every errored row in the manifest was captured between
    2026-08-23 and 2026-09-08, and the error-log reader only began working
    2026-09-10, so these need RECAPTURE before their numbers are used.
    `almd_realtext`




34. **OQ-L9BUDGET** — no memory budget for the 1756-L9xTS family.
    `controller_budgets.yaml` returns None for all four catalogs, so the UI
    has no denominator on an L9 file and cannot show headroom.

    Deliberately not guessed. The catalog digits look like they encode
    memory (L902/L905/L908/L915), but that is a pattern, not a source, and
    this project has been wrong before inferring a constant from a catalog
    name. Needs the real per-catalog user memory from a datasheet or a
    controller.

    The UI degrades correctly today -- it shows the byte total without a
    percentage rather than inventing one.

    **Test files built 2026-09-08**: `fwmatrix_v38_1756_l9{02,05,08,15}ts`.

    **CAPTURED 2026-09-11, and they do NOT close it.** The premise above
    was wrong: the capture harness records memory USED, not the capacity
    denominator, and `message_value` came back 0 on all four. What the
    four files did settle is the **baseline**, which was a different
    question — an empty v38 L9 project measures 20,404 against 18,128 for
    a 1756-L81E on the same firmware, a flat **+2,276 with zero variance
    across all four catalogs**. Wired as a `catalog_baseline_delta`, and
    independently replicated by the 14 `alarmdef_l902ts_*` files, which
    sit exactly 2,276 above their L81 twins once the shared alarm offset
    is removed.

    The budget itself still needs the real per-catalog user memory from a
    datasheet or a controller. The UI continues to degrade correctly,
    showing the byte total with no percentage rather than inventing one. Generated at v38
    only -- the family postdates the v31-v37 firmwares in the matrix, and
    building an L9 at v31 would fabricate a firmware that never shipped.



37. **OQ-UDTMEMBERNAME** (supersedes OQ-UDTBOOLMEMBER) — a UDT member's
    NAME LENGTH is unmodelled, and the whole corpus is blind to it because
    every generator ever written used two-character member names.

    The `alarmsep` batch captured 2026-09-11 and its 15 points fit one law
    with **zero residual**:

        deficit = udt_definitions x (8 + 8 * floor(bool_members / 2))

            u\b      1     2     4     8    16
              1     -8   -16   -24   -40   -72
              2    -16   -32   -48   -80  -144
              4    -32   -64   -96  -160  -288

    That reads as a BOOL-member cost, which is what OQ-UDTBOOLMEMBER
    predicted, and it is **wrong**. `udttype_bool_n4` is a structural twin
    of `alarmsep_u01_b04` — one UDT, one hidden backing SINT, four BIT
    members, no tags, both type names bucketing to the same ceil(len/8) —
    and it predicts EXACTLY while alarmsep_u01_b04 is 24 short. The one
    thing that differs is the member names: `M0`..`M3` against
    `Sts_A00`..`Sts_A03`. Two characters against seven.

    So the driver is member name length, or something travelling with it,
    and alarmsep cannot separate them because it varies BOOL count and
    total name length together. Nothing is wired off that law.

    `udt_definition` charges for the TYPE name (`name_per_8_chars`) and
    nothing at all for member names. Real programs are nothing like the
    fixtures:

        311DGeneratedProgram          689 members, avg  8.2 chars
        BaillieLeitchField_Edger      619 members, avg 10.2 chars
        Elmsdale                      877 members, avg 10.7 chars
        SJ_Gormley                    509 members, avg  9.8 chars
        FlareFunction_311D          2,284 members, avg  9.7 chars
        BAI10048_TrimmerTally       1,861 members, avg 12.3 chars

    **Test files built 2026-09-11**, `gen_udt_membername.py`, 24 files, all
    1756-L81E v35, type name held at exactly 8 characters throughout so the
    already-modelled type-name bucket cannot move. The engine predicts
    IDENTICALLY across every name length in every arm, so all 24 are direct
    measurements of an unmodelled quantity:

      - `udtmn_bool_short_b{01,02,04,08,16}` — BOOL count at 2-char names.
        The control; should predict exactly, matching udttype_bool_n4.
      - `udtmn_bool_l07_b{01,02,04,08,16}` — the same counts at alarmsep's
        7-char names, with no alarm definitions in the file at all.
      - `udtmn_bool_len{02,04,08,12,16,24,32}_b04` — the pure name-length
        sweep. Free, per character, or bucketed by 8 like every other name
        cost in this model?
      - `udtmn_dint_len{02,07,16,32}_n04` — the same on DINT. BOOLs are the
        one member kind with a hidden backing SINT, so this rules a
        BOOL-specific explanation in or out.
      - `udtmn_bool_len{02,07,16}_b16` — name length where a second backing
        SINT appears, and where the alarmsep law needed floor(b/2) rather
        than a flat per-member rate.

    **HOLE FOUND IN THAT BATCH, 2026-09-11, same day.** All 24 `udtmn_*`
    files carry `tags_xml=""`. Zero tags, in every arm. So whatever they
    measure, they measure it PER DEFINITION, and they are structurally
    incapable of saying whether the same term is ALSO charged per tag of the
    type. That distinction is the whole of the real-file exposure: AccuTally
    carries 33,574 UDT tags against 174 UDT definitions -- 193 tags per
    definition -- so a per-definition name term and a per-tag one differ by
    more than two orders of magnitude on that file. It is the identical
    failure mode OQ-DEFSCALE's captured sweeps hit from the other direction.

    `gen_udt_membername2.py`, **23 more files**, built from the same
    `_member_name()` / `_type_name()` so every arm differences straight
    against the 24 pending ones. Type names stay at 8 characters throughout,
    and the engine predicts IDENTICALLY across name length in every arm, so
    every difference is a measurement:

      - `udtmn2_bool_len{02,16,32}_b04_t{01,05,25}` (9) — the same 4-BOOL UDT
        at three name lengths with 1/5/25 tags of it; the t=0 point already
        exists. Per-definition means the length effect is identical at every
        t; per-tag means it grows 25x across the arm.
      - `udtmn2_dint_len{02,32}_n04_t{01,25}` (4) — the same on DINT. A
        BOOL-specific explanation was already assumed once and was wrong
        (OQ-UDTBOOLMEMBER), so no name-length result is believed on BOOL
        evidence alone.
      - `udtmn2_nest_len{02,32}` (2) — an outer UDT whose 4 members are each
        an inner UDT with 4 members at the swept length. Are a nested type's
        member names charged again inside every containing definition? If so
        the cost compounds with nesting depth, and real programs nest heavily.
      - `udtmn2_bool_len32_b04_arr{010,100}` (2) — one tag that is an array of
        10/100 elements. Per-tag applies once; per-element multiplies.
      - `udtmn2_aoi_{plen,llen}{02,16,32}` (6) — the same question for an AOI's
        PARAMETER and LOCAL TAG names, which no generator has ever varied.

    **Do not oversell this as the fix for the real-file error.** Checked
    directly: the real-file deficit per declared member/parameter/local tag
    ranges from **+15 to −46 bytes** across the 16 real programs, and four
    of them over-predict. Whatever drives the 2–5% real-file error is not
    one missing per-name term, and this is not it. It is a real gap worth
    closing on its own terms, not the headline.

    Also confirmed by this batch, and worth keeping: **alarm DEFINITIONS
    cost nothing.** Every `alarmsep_*_alarm` measured byte-identical to its
    `_noalarm` twin, and `def1/def2/def3` identical again.



    **THE NAME-LENGTH LAW IS SOLVED AND WIRED 2026-09-13 (capture-batch
    segments 10 and 11, `udtmn2_*` 23 files and `udtmn_*` 24 files).** A UDT
    definition charged NOTHING for its members' own names. They cost the SAME
    8-aligned pool as an AOI definition's member names — which is the right
    answer for the right reason: it is the same thing, a definition's member
    names, in the same file format.

        member_name_pool = 8 * ceil(sum(len(name) + 1) / 8)

    `udtmn_bool_len{02,04,07,08,12,16,24,32}_b04` holds four BOOL members and
    varies ONLY the name length, so nothing else can move:

    | name length | 02 | 04 | 07 | 08 | 12 | 16 | 24 | 32 |
    |---|---:|---:|---:|---:|---:|---:|---:|---:|
    | residual before | −8 | 0 | +8 | +16 | +32 | +48 | +80 | +112 |
    | increment | | +8 | +8 | +8 | +16 | +16 | +32 | +32 |

    The pool's own increments are those same seven numbers. **A raw
    1-byte-per-character rate fits five of the seven and misses 04→07 (it wants
    +12) and 07→08 (it wants +4)** — that pair is the whole discrimination, and
    nothing in the `udtmn2_*` batch could have made it, because every one of its
    name lengths lands on the same residue mod 8. The two batches together are
    what settled the form; either alone would have fitted the wrong one.

    Cross-checks, all clean: `udtmn2_bool_len{02,16,32}_b04_t{01,05,25}` is FLAT
    in tag count at each length (−8/−8/−8, +48/+48/+48, +112/+112/+112), so the
    cost is per DEFINITION and not per instance. `udtmn2_dint_len{02,32}_n04`
    and `udtmn2_nest_len{02,32}` agree at 4 and 8 members. And the six
    `udtmn2_aoi_*` rows are the control — flat at −4 across all three lengths,
    because segment 4 had already priced the AOI side.

    **Effect.** Every family is now flat in name length, where it used to span
    120 bytes. The `udt` category is **108 of 108 within 1%** (mean absolute
    error 0.148%). On the sixteen real programs, mean absolute error
    **2.025% → 1.605%** and sum-weighted **+2.145% → +1.245%** — the largest
    single real-file gain of the day, because real UDT member names average
    around 12 characters and a real program carries 174 UDT definitions. The
    residual also went two-sided again: five programs now over-predict, worst
    +3.28% (was +4.22%), and `pukall_gang` is −0.06%.

    **WHAT IS LEFT, and it is deliberately NOT fitted.** With the length law in,
    every family collapses to a per-shape CONSTANT over-charge:

    | shape | declared members | hidden BOOL runs | residual |
    |---|---:|---:|---:|
    | `udtmn_bool_l07_b01` | 1 | 1 | −8 |
    | `udtmn_bool_l07_b02` | 2 | 1 | −16 |
    | `udtmn_bool_*_b04` | 4 | 1 | −24 |
    | `udtmn_bool_l07_b08` | 8 | 1 | −40 |
    | `udtmn_bool_*_b16` | 16 | 2 | −64 |
    | `udtmn_dint_len*_n04` | 4 | 0 | −32 |
    | `udtmn2_nest_len*` | 8 | ? | −64 |

    `−(4m − 8r + 16)` fits five of those seven exactly and misses `b01` by 4 and
    `nest` by 16. That is **three constants** — a `per_member` of 12 rather than
    16, a `bool_run_bonus` of 40 rather than 32, and a −16 per definition — fitted
    to five points, in the one family where member count and hidden backing SINTs
    are inseparable. Fitting it is precisely the move that gave the AOI
    definition four overlapping terms and had to be undone. It needs a UDT
    member-count sweep with NO BOOL members, so runs cannot confound the count;
    the existing `dint_n04` is the only such point.

    Also recorded: hidden backing SINTs are excluded from the pool, the same
    convention `declared_member_count` already uses. Their generated names are
    long (`ZZZZZZZZZZBoolMember00`, 22 characters), so including them would be a
    large change, and the member-COUNT arm is exactly where that would show —
    and it does not come out flat either way.


38. **OQ-JSRFOLD** — new, 2026-09-11. A JSR and its target routine are
    over-charged at low counts and under-charged per unit, and the shape
    points at how the target's cost is folded in.

    `forloop_ctl_r{001,005,025,100}` — N JSR rungs against N target
    routines, built as the control arm for FOR:

        N      predicted   actual   delta
        1         18,831   18,552    +279
        5         20,235   19,960    +275
       25         27,255   27,000    +255
      100         53,580   53,400    +180

    Both arms are exactly linear and they disagree in two ways at once:
    actual is `18,552 + 352(N-1)`, predicted is `18,831 + 351(N-1)`. So a
    fixed **+279 excess** plus **1 byte per unit short**.

    Routine shells alone are not the problem: `subrtn_shell_r100` adds 100
    extra routines and predicts exactly, 12 of 12 across that family. What
    differs here is that these targets are JSR TARGETS, and report.py
    deliberately never emits a JSR target as its own SizeEntry — its cost
    is folded into the caller instead (`RoutineLogic.is_jsr_target`). The
    FOR arm has the same 100 target routines and, once FOR was weighted,
    predicts exactly at all four counts; those targets are NOT JSR targets
    and so are emitted normally. That asymmetry is the suspect.

    Not wired. A 1-byte-per-unit term is not a plausible memory quantity on
    its own, so the fold-in is probably misattributing a larger cost rather
    than being off by one, and guessing at that would be fitting noise. The
    isolation needed is a JSR-target sweep that varies the TARGET's own
    content while holding the call count fixed, which nothing covers:
    every existing JSR file uses a one-rung target.

    Stake: real programs are full of JSRs. Small per-file, but it applies
    everywhere.



    **CAPTURE ERRORS: 2 row(s)** flagged here by `scripts/capture_errors.py` (step 2b), 2026-09-11.
    2 captured WITH Studio build errors, so their `actual_bytes` is
    SUSPECT rather than wrong — part of the file may never have reached the
    controller, which inflates apparent over-prediction. None of them carries
    any error text: every errored row in the manifest was captured between
    2026-08-23 and 2026-09-08, and the error-log reader only began working
    2026-09-10, so these need RECAPTURE before their numbers are used.
    `jsr_midchain_leaf_control`, `jsr_midchain_real_chain`


40. **OQ-AOIDEFITEMIZE** — an AOI's priced definition cost and its own
    itemized member breakdown are two different computations, and they
    disagree by a large margin on every real AOI.


    **IN-DEPTH REVIEW 2026-09-18 — the `mbshape_*` family read in full, and the
    answer is that it is NOT a per-member constant, which is worth knowing
    because the shape of the residual makes it look like one.**

    `mbshape_*` is 15 files built to a real program's AOI profile (19
    definitions, 453 parameters, 280 local tags) with one axis varied at a time.
    It sits at 2.36% mean absolute error while every isolated AOI family is
    essentially exact -- `aoipack_*` 281 rows at 0.048%, `aoistructure` 110 rows
    at 0.118%, `aoi` 159 rows at 0.037%. So whatever this is, it does not show up
    when one AOI is measured alone.

    Regressing the residual on definition count, parameter count and local-tag
    count over all 15 rows:

        residual = -1.9 x parameters - 1.9 x locals - 97     RMS 1,496 -> 33

    Parameters and locals carry it at the SAME rate, from two independent axes
    over a 2.3x span, and the fit is tight. Definition count does not: its
    coefficient is +2.4 and its three rows are the three worst fits (+85, -61,
    +57). `mbshape_rungs_{05,10,20}` are byte-identical to each other, so AOI
    internal rung count is priced correctly and contributes nothing here.

    **Why it is NOT wired: the rate is not an integer, and splitting it does not
    make it one.** A per-member cost has to be a whole number of bytes. Fitting
    BOOL and non-BOOL members separately gives -1.11 and -2.62 and barely moves
    the residual (RMS 35 against 37 for the single shared rate), so the
    BOOL-packing explanation is refuted rather than unconfirmed. A non-integral
    per-member rate that is stable across two axes is the signature of something
    being counted at a different granularity than the thing it correlates with.

    **Real exposure is small**: roughly 5,000 declared members across the 331 AOI
    definitions in the sixteen programs, so about 9,500 bytes, 0.01%. This is not
    where the remaining error is, which is the other reason it is recorded rather
    than fitted.

    **What would settle it**: a single-definition file with the same
    BOOL/BOOL/REAL/DINT/BOOL/REAL type cycle, member count swept 6/12/24/48. If
    the rate survives at one definition it is genuinely per member and the
    non-integer is an averaging artifact to be decomposed; if it vanishes, it
    belongs to the 19-definition shape and the per-member reading is a
    coincidence of this family's construction.

    Found 2026-09-11 while making the treemap sum to the report. For each
    AOI, `report.py` charges a definition cost (per-declared-member rate
    table plus the type-name-length bucket, OQ-AOIDEF's wiring), while
    `sizing/tree.py`'s `expand_definition_children` enumerates the same
    definition member by member. The enumeration always comes in LOWER.
    On Elmsdale, all 21 AOIs:

        AOI               priced    itemized    unexplained
        DriveAxis         18,873       3,633         15,240
        T_DST             12,344       3,000          9,344
        TS_VFD            10,581       3,361          7,220
        T_Clock            6,975       2,231          4,744
        VirtualAxis        6,589       2,085          4,504
        HomeToTorque       6,122       1,902          4,220
        TS_TrackSts        5,268       1,568          3,700
        ... (21 total)                              66,908

    66,908 bytes, 6.1% of that file's whole predicted total, is charged by
    the report and accounted for by nothing in the breakdown. It is not
    a rounding effect and it is not uniform: it scales with something the
    member enumeration does not see.

    Two possibilities, and they need separating before either is acted on:

      - The per-member rate table is right and the enumeration is
        incomplete — it is missing whole categories of declared thing
        (nested UDT members expanded at the wrong depth, InOut parameters,
        local tags of structured type). This would be a pure display bug.
      - The rate table over-charges and the real definition cost is closer
        to the enumeration. This would be a SIZING error worth 6% on a
        real file, which is six times the whole error budget.

    The first is more likely — the rate table was fitted against real
    capture data and the real-file error is currently 2.17%, which a 6%
    over-charge would not survive — but "more likely" is not measured.

    The isolation test is cheap and exists in shape already: a
    single-AOI file whose definition declares a known member roster,
    captured, differenced against the same file with one member added.
    `aoidef_*` covers the flat single-type case; what is missing is an AOI
    whose members are themselves structured (a UDT member, a TIMER, an
    InOut of UDT type), which is exactly what every real AOI above has and
    every existing test file lacks.

    Until then the UI carries the difference as an explicit
    "Unitemized definition cost" row rather than dropping it, so the
    treemap sums to the report total and the size of the unexplained part
    is visible instead of silent.


    **CAPTURE ERRORS: 40 row(s)** flagged here by `scripts/capture_errors.py` (step 2b), 2026-09-11.
    43 captured WITH Studio build errors, so their `actual_bytes` is
    SUSPECT rather than wrong — part of the file may never have reached the
    controller, which inflates apparent over-prediction. None of them carries
    any error text: every errored row in the manifest was captured between
    2026-08-23 and 2026-09-08, and the error-log reader only began working
    2026-09-10, so these need RECAPTURE before their numbers are used.
    `aoi_logic_scale_010`, `aoi_logic_scale_050`, `aoi_logic_scale_100`, `composite_realistic_03_r2`, `composite_realistic_04_r2`, `composite_realistic_05_r2` (+37 more)


41. **OQ-POINTIOCONN** — a POINT I/O card's memory cost depends on its
    connection format, which the model does not represent at all, and the
    flat rate it charges instead is wrong in both directions.

    Three real captures, 2026-09-11. Identical content otherwise: one
    1756-L81E v35, one adapter, sixteen 1734-IB8/C cards. The non-module
    part of the prediction is byte-identical (18,336) across all three, so
    the whole difference is the I/O subsystem.

        format          adapter          actual   module subsystem   per module
        Enhanced        1734-AENTR/C     32,616        14,280             840
        Enhanced Data   1734-AENTR/C     37,320        18,984           1,117
        Optimized       1734-AENT/A      28,688        10,352             609

    Against predictions of 47,280 / 47,360 / 20,050 — over by 45% and 27%
    on the first two, under by 30% on the third.

    The three formats are structurally distinct in the L5X and the parser
    already tells them apart:

      - **Enhanced** — the card has a ConfigTag and NO `<Connections>`
        element at all.
      - **Enhanced Data** — the card carries its own `InputData`
        `<Connection>`.
      - **Optimized** — the card carries `<RackConnection><InAliasTag/>`,
        its I/O aliased into the adapter's own Slot array.

    One clean single-variable result is already in hand. Enhanced Data
    minus Enhanced is the same adapter, the same sixteen cards and only
    the connection format changed: **+4,704, exactly 16 × 294.** A card's
    own connection costs 294 bytes more than no connection. That is a real
    per-module, per-format cost and nothing in the model has a term for it.

    What is NOT separable from these three points: the adapter's own cost
    from the per-card cost, because every file has sixteen cards; and the
    Optimized arm changes the adapter catalog (1734-AENT/A) at the same
    time as the format, confounding the two.

    Both fall out of a count sweep — the same differencing method every
    other constant in this project came from. For each format, N =
    1, 2, 4, 8, 16 cards: the slope is the per-card cost of that format
    and the intercept is that adapter's own cost, each fitted
    independently of the other.

    **Built 2026-09-11**, `gen_pointio_conn_sweep.py`, **15 files** --
    `pioconn_{enhanced,enhdata,optimized}_n{01,02,04,08,16}`, 1756-L81E
    v35, every module block verbatim from the real exports. Only what
    genuinely depends on the card count is rewritten, and the three
    formats need different rewrites because they carry the rack
    differently:

      - **Enhanced Data** -- the adapter's InputTag is just the two status
        DINTs and every card carries its own self-contained Connection.
        Only the card count, the adapter's Bus Size, the L5K per-slot
        blobs and the rack-sized `pad` arrays on its input and output
        types change.
      - **Enhanced** -- the adapter's InputTag holds one StructureMember
        per card (`Slot01`..`Slot16`), and the file DEFINES that
        module-scoped type itself under `<ExtendedProperties>`, so the
        slot list is rewritten in both places alongside the status arrays
        and the output pad. The type NAME carries a Studio-computed hash,
        `AB:1734_ERACK_649387C8:I:0`, which is not derivable from the
        L5X, so it is kept verbatim; the file supplies the matching
        definition. Whether Studio 5000 accepts a self-described type
        whose hash it would have computed differently is something a real
        conversion answers and guesswork does not.
      - **Optimized** -- every card is rack-aliased into the adapter's own
        SINT array and the profile is named after the slot count,
        `AB:1734_17SLOT:I:0`. Systematic rather than hashed, so it is
        rewritten to match along with the array dimensions and element
        lists. Unlike the Enhanced case this type is NOT defined in the
        file -- it is a catalog profile -- so if `AB:1734_<n>SLOT` does
        not exist at some n, that file fails to import.

    A conversion failure in either of the latter two arms is a RESULT, not
    a defect: it says the rack-optimized profile exists only at certain
    sizes, or that the ERACK hash must match. Logged, not worked around.

    Verified before shipping: slots 1..N, adapter Bus Size N+1, per-slot
    L5K arrays and pad dimensions all N+1, slot member lists trimmed in
    both the Decorated structure and the type definition, and zero sizing
    errors in the two arms the model can price.

    **Naming arm, 12 more files** (`pioname_*`). Every card in all three
    real exports is NAMELESS -- catalog and slot only. That is the unusual
    shape, not the normal one: a module you name in the I/O tree gets
    module-defined tags of its own, and this model already charges real
    bytes for a tag's NAME LENGTH elsewhere (`alias_tag`, the AOI and UDT
    type-name-length buckets). So naming a card plausibly costs something,
    plausibly scales with the name, and plausibly differs by connection
    format -- a rack-aliased card has no tag of its own to name, so it may
    be free there and not free in the other two.

      - `pioname_{enhanced,enhdata,optimized}_named_n08` — 8 named cards,
        8-character names, one per format. Differences against the
        nameless `pioconn_<fmt>_n08` at the same count.
      - `pioname_enhdata_len{05,08,16,24,32}_n08` — the same 8 cards at
        five name lengths. Flat rate or per character?
      - `pioname_enhdata_named_n{01,02,04,16}` — named-card count, against
        the nameless file at each count. Per card or once per file?

    The engine currently predicts **exactly the same total named or
    nameless, at every length and every count** — it has no term for a
    module name at all. That makes all twelve direct measurements of an
    unmodeled quantity: any nonzero capture delta is a gap, and a zero
    delta confirms the zero rather than leaving it assumed.

    Stake: this is not a corner case. Elmsdale alone has three of these
    racks (JB101_IO, C102_IO, MCP101_IO — 19 cards), all currently priced
    at either a flat 1,672 they do not cost or, for the rack-aliased ones,
    at zero.

    **IN-DEPTH REVIEW 2026-09-18 — all 27 rows captured and read. Every slope
    is now measured; NOTHING is wired, and the reason is a classifier problem
    rather than a measurement one.**

    **The per-card cost, by connection format.** Differencing consecutive card
    counts within each format, which cancels both the adapter and the file base:

    | format | n=1 | 2 | 4 | 8 | 16 | per card |
    |---|---:|---:|---:|---:|---:|---:|
    | Optimized | +574 | +566 | +566 | +582 | +582 | **0 — flat** |
    | Enhanced | +648 | −496 | −2,776 | −7,304 | −16,392 | **−1,136** |
    | Enhanced Data | +643 | −218 | −1,924 | −5,320 | −12,144 | **−852** |

    The Optimized arm is FLAT across a 16x span — a rack-aliased card is priced
    correctly today and the +570 it carries is a per-file constant, not a slope.
    The other two are over-charged by 1,136 and 852 per card, exactly linear
    from n=4 upward (n=2 and n=4 sit 8 and 16 off the line, the usual small
    noise). Their difference, 284, is the same order as the 294 bytes per card
    the three original real captures put on Enhanced Data over Enhanced, so the
    RELATIVE ordering the model has is right and the absolute level is not.

    **The module-NAME measurement, which was the naming arm's whole point, and
    it is unambiguous.** `pioname_enhdata_len{05,08,16,24,32}_n08` — 8 cards,
    name length the only variable:

        length     5      8     16     24     32
        residual -4,808 -4,808 -4,744 -4,680 -4,616

    Length 5 and length 8 are IDENTICAL, and every 8 characters after that is
    exactly +64 across 8 cards, i.e. **8 bytes per card per 8 characters, with
    the first 8 characters free.** The engine charges a module name nothing at
    all, so this is a direct measurement of an unmodeled quantity, as designed.
    The named-versus-nameless arm adds that having a Name AT ALL costs 64 per
    card (+64, +128, +256, +512 at n=1, 2, 4, 8 — per card, no free first one),
    but a nameless module cannot occur in a real export, so that 64 is already
    inside the per-catalog `module_overhead` that was fitted on real modules.

    **NOT wired, and the disagreement is worth stating precisely.** The measured
    module-name law is `8 × ((len − 1) // 8)` — a full eight characters free.
    The shared `identifier_name_length` law, KNOWN from the program, task,
    routine and JSR-target sweeps, is `8 × (len // 8)` — it charges 8 at exactly
    length 8, where these files measure 0. One 8-byte bucket apart, on the
    strength of one length pair. Real exposure across all sixteen programs is
    **449 modules and 4,816 bytes, 0.05% of the real set**, so introducing a
    SECOND name law for that is not justified; recorded here instead, and the
    len05/len08 pair should be repeated before anyone acts on it.

    **The per-card correction is NOT wired because real cards cannot be
    classified.** Real exposure is 45 POINT I/O modules in 4 of the 16
    programs — Elmsdale 20, FlareFunction 14, CMU 7, K3M16 4 — so at 1,136 per
    card this is 38,000 to 51,000 bytes, material. But at the CARD level an
    Enhanced card and an Optimized card are structurally identical in L5X: both
    carry no `<Connection>` element at all, and they differ only in the
    adapter's InputTag. 34 of the 45 real cards are in exactly that
    indistinguishable state. The two formats' corrections differ by 1,136, so
    guessing is worse than not charging.

    And the sweep cannot settle it, by its own admission: the Optimized arm
    changes the adapter CATALOG at the same time as the format, so "Optimized is
    flat" and "that adapter is flat" are not separated either.

    **One observation that should be tested rather than believed.** Applying
    −1,136 per card to Elmsdale's 20 cards takes its residual from **+22,862 to
    +142** — from 1.99% to 0.01%. That is either a coincidence or it says
    Elmsdale's racks are Enhanced and this is most of its remaining error. The
    same correction makes FlareFunction, which over-predicts, substantially
    worse. So the hypothesis is testable and the test is cheap: Elmsdale's
    adapters are named `JB101_IO`, `C102_IO` and `MCP101_IO`, and reading which
    format each one uses off the real export settles which way the correction
    goes on the one real program where it matters most.

    **What is needed: two files, not twelve.** The same adapter catalog
    (`1734-AENT/B`) carrying 8 cards in Enhanced and in Optimized form — the
    one comparison this batch confounded. That separates the format from the
    adapter, and with it the 34 unclassifiable real cards become classifiable
    by their adapter's InputTag shape.



42. **OQ-AXISMARGINAL** — new 2026-09-11, and the largest single-sign
    unreconciled block in the corpus. Found by `scripts/unreconciled.py`, also
    new that day, which recomputes every captured row against the CURRENT
    engine: **1,601 of 2,770 captured rows sit outside +-8 bytes**, and the
    worst family by magnitude is the 31-row axis set, captured 2026-09-03.

    Every `axis_scale_*` file with n>=2 over-predicts, monotonically, to
    **+62,528 bytes (+10.5%)** at 20 axes. Both arms are perfectly linear in
    axis count with zero residual at every step:

        single-axis drives   +3,288 per axis    n = 2,4,6,8,12,16,20
        dual-axis drives     +2,600 per axis    n = 2,4,6,8,12,16,20

    and the two shared base points (n=1 single, n=2 dual) both sit at +56 —
    exact. So the FIRST axis in a file is priced right and every one after it
    is not. This is a marginal error, not a base-constant error, which matters
    because `AXIS_CIP_DRIVE` was promoted FITTED -> KNOWN earlier the same day
    on single-axis evidence. That promotion is correct for one axis and wrong
    for the twentieth, and the entry should be read that way until this
    closes.

    Real exposure: the sixteen real programs carry **359 AXIS_CIP_DRIVE and 65
    AXIS_VIRTUAL** tags. At the single-arm rate that is roughly **650 KB** of
    over-prediction sitting inside the real totals, the same order as
    OQ-MODULEMARGINAL's 824,864 — and in the same direction, so the two
    together are most of what the under-predicting real files are being
    compensated by.

    **Why the two arms do not decompose on their own.** The naive subtraction
    gives a clean-looking answer:

        single: 1 module per axis      A + M    = 3,288
        dual:   1 module per 2 axes    A + M/2  = 2,600
        -> M = 1,376, A = 1,912   (A identical from both arms)

    It is not valid, for two reasons that come from reading the files rather
    than the numbers:

      - The single arm is 8 x 2198-S086-ERS3, **one catalog repeated**. The
        dual arm is one each of D012/D020/D032/D057, **four distinct
        catalogs**, repeating only as n grows. OQ-MODULEMARGINAL's open
        question is exactly whether the module discount is per catalog or per
        file, so `M` is not the same quantity in the two arms.
      - **Every one of these 31 files carries `error_count = n+1` with an
        EMPTY `error_log`.** All 144 errored rows in the manifest were
        captured between 2026-08-23 and 2026-09-08; the error-log reader in
        `logix_build_capture.ahk` only began working 2026-09-10, so not one of
        them has any error text on record. The n=1 file has 2 errors and is
        still byte-exact, which suggests they are benign — but that is an
        inference, and this is the direct reason a 31-row family with a 10%
        systematic error sat unexamined: there was no way to tell whether the
        rows were trustworthy. **The 144 errored rows need recapture under the
        current tooling**, and that is the single highest-value thing the
        capture rig can do.

    **Test files built 2026-09-11, `gen_axis_marginal.py`, 16 files.**

      - `axmarg_virtual_n{01,02,04,08,12,16,20}` (7) — the decoupling arm.
        AXIS_VIRTUAL needs no drive module at all, so a count sweep with ZERO
        modules in the file measures the per-axis term with nothing to share
        it with, which neither captured arm can do. Real programs carry 65 of
        these, so it is their real shape.
      - `axmarg_1cat_n{02,04,08,12,20}` (5) — the same axis and module counts
        as the captured `axis_scale_n*_dual`, but ONE catalog repeated instead
        of four distinct. Same axes, same modules, only catalog repetition
        differs.
      - `axmarg_ncat_n08_{1,2,4}cat` (3) — axis count AND module count both
        pinned at 8 and 5; only the number of distinct catalogs moves. All
        three predict an identical 245,080 (they draw from one catalog family
        the engine prices identically), so any difference in the captured
        actual is purely the catalog-diversity effect. Under a per-catalog
        discount the three differ; under a per-file one they do not move.
      - `axmarg_mixed_n08` (1) — 8 AXIS_VIRTUAL plus 8 AXIS_CIP_DRIVE in one
        file, against the two single-type files at the same count: is the
        marginal term per axis TAG regardless of type, or per type?

    **Do not wire any of this before the virtual arm lands.** The 1,912/1,376
    split is arithmetically exact on 14 points and still rests on an
    assumption the data cannot support, which is the same mistake the axis
    promotion already made once today.

    **CAPTURE ERRORS: 57 row(s)** flagged here by `scripts/capture_errors.py` (step 2b),
    recounted 2026-09-17. Was 51; the 6 added are `axis_scale_n02_dual`,
    `axis_scale_n08_dual`, `axis_scale_n08_dual_regen` and
    `axmarg_ncat_n08_{1cat,2cat,4cat}`, all newly captured in the 212-row batch
    and all failing for the SAME newly-diagnosed reason as OQ-MODULEMARGINAL's
    six -- see the bus-sharing diagnosis recorded there. This is the first time
    any axis-family row has carried real Studio error text.
    Previously 51, before that 74, then 56.
    Was 74, then 56. The last 5 went when `axis_scale` was trimmed from 18 files to
    7 on 2026-09-14: nine count points per shape bought nothing a four-point
    geometric ladder does not, every one of them needed recapture anyway for the
    Ch2/Ch3 fix, and the marginal has been flat wherever this project has measured
    one. Removed: `axis_scale_n{04_dual,06_single,06_dual,12_single,12_dual,
    16_single,16_dual,20_single,20_dual,20_dual_regen,08_single_regen}`.
    **18 were CLEARED 2026-09-14** -- the nine `axmarg_*` drive
    files and the nine `axis_scale_*_dual*` files -- because their content changed:
    a 2198-P bus supply plus its converter axis were added to the first group and
    the second group's dual-axis channel was corrected from Ch2 to Ch3. Their old
    `actual_bytes` measured a project whose drives never got bus power, so it
    describes content the repo no longer holds. See OQ-MODULEMARGINAL for the
    root cause and the evidence.
    65 captured WITH Studio build errors, so their `actual_bytes` is
    SUSPECT rather than wrong — part of the file may never have reached the
    controller, which inflates apparent over-prediction. None of them carries
    any error text: every errored row in the manifest was captured between
    2026-08-23 and 2026-09-08, and the error-log reader only began working
    2026-09-10, so these need RECAPTURE before their numbers are used.
    `axis_scale_n01_single`, `axis_scale_n02_dual`, `axis_scale_n02_single`, `axis_scale_n04_dual`, `axis_scale_n04_single`, `axis_scale_n06_dual` (+59 more)
    1 committed file(s) attempted and never reached `ok` in
    `convert_log.csv`: `daxis_axis_cip_drive`

    **THE STRIP-LADDER APPROACH IS DEAD, 2026-09-18, and this entry may not
    reach for it again.** A FlareFunction ladder was built and refused on
    import with **19 errors**. The cause is structural, not a bug to fix: an
    XML round trip destroys CDATA, and Studio's schema requires it — `<Line>`
    fails with *"Required CDATA for element 'Line' was missing"*, string
    `<Data>`/`<DefaultData>` fails as *"String invalid"*, and one broken AOI
    cascaded into four more tags as *"Data type does not exist"*. The ladder
    had passed an element-for-element equality check against the original
    (97,211 elements, every rung `Text` matching) and was still worthless,
    so that check is not evidence of anything.

    See the READ-ONLY rule in `CLAUDE.md`. The consequence for THIS question:
    the two existing Elmsdale/Griffin ladders are the only per-category real
    measurements that will ever exist, no third one is coming, and
    OQ-LADDERBASE — which says those two disagree by 18,000–25,000 bytes —
    can no longer be settled by generating more rungs. Attribution of the
    real-set residual has to come from files built as valid projects, or from
    variants Studio itself exported after a delete made in Logix Designer.


44. **OQ-ALARMCONDREAL** — new 2026-09-14, from the strip ladder. Tag-based
    alarm conditions are the **second-largest category in both real programs
    measured**, and the wired model is nearly exact on one of them and 8.8%
    short on the other.

    | | conditions | actual step | predicted step | per condition actual | per condition predicted |
    |---|---:|---:|---:|---:|---:|
    | `griffin_stackerline_1mar25` | 400 | 443,128 | 442,400 | 1,107.8 | 1,106.0 |
    | `elmsdale_20251017r01` | 200 | 243,040 | 221,600 | **1,215.2** | 1,108.0 |

    That is 19% and 21% of the whole program respectively. The step is clean:
    an exhaustive element-tag diff of each full export against its `NoAlarms`
    sibling shows `AlarmCondition`, `AlarmConfig`, `HMIGroup` and the
    `AlarmConditions` container are the **only** elements that differ — no tags,
    rungs, routines, programs, UDTs or AOIs moved.

    These are controller-scope **Alarm Manager** alarms, and they must not be
    confused with a scheduled program that happens to be named for alarms.
    Elmsdale has both: 200 controller Alarm Manager conditions, and a separate
    `AlarmsAndMessages` **program** of ordinary ladder whose
    `TiltHoist_Alarms` routine makes 161 references to `Alarms_TiltHoist`. The
    two are measured by different files and never double-count — `NoAlarms`
    strips the definitions and keeps the program, the per-program `NoAlarmMsg`
    strips the program and keeps the definitions, and because the associated
    array is a CONTROLLER tag neither strip leaves a dangling reference.

    Only the alarm definitions were stripped; the associated tags remain in the `NoAlarms`
    files as ordinary controller tags, so their data cost is NOT inside this
    step. `alarm_conditions` prices the definitions 800 + 500n + an
    associated-tag term keyed on each `AssocTag1/2/3` target's resolved type.

    **ASSOCIATED-TAG AUDIT DONE 2026-09-14, AND IT RULES ITSELF OUT.** All 600
    Elmsdale and 1,200 Griffin associated-tag references were resolved:

        Elmsdale   Alarms_TiltHoist[0..199].{Number, Description, MoreInfo}
        Griffin    StackerAlarms[0..199].{Number, Description, MoreInfo}

    Both arrays are **the same UDT, `Alarms_SE`, at the same `Dimensions=200`**,
    with the same members (`SINT` filler, `BIT Active`, `STRING Description`,
    `STRING MoreInfo`, `DINT Number`) and the same three members referenced.
    An attribute-by-attribute frequency diff of all 600 conditions shows every
    one of the 37 `AlarmCondition` attributes identically distributed between
    the two programs **except the tag names themselves**, which the `alarmcond_*`
    batch already proved free. So associated-tag type mix cannot explain the
    gap, and neither can severity, delays, condition type, or HMI group.

    **The one structural difference found: conditions per array element.**
    Elmsdale has 200 conditions over a 200-element array (1:1). Griffin has
    **400 conditions over a 200-element array (2:1)** — its alarms come in two
    named sets, `StackerAlarm*` and `Stacker3Alarm*`, both pointing into the
    same 200 elements.

    **And the two files cannot both fit the wired shape.** Solving
    `cost = B + n·k` on the two measured steps gives

        200,088 = 200k   ->   k = 1000.44,  B = 42,952

    A non-integer per-condition cost means `base + flat-per-condition` is the
    wrong shape for a real Alarm Manager, not that one of the constants is
    slightly off. Two files cannot say what the right shape is.

    **This is NOT the parked ALMD/ALMA question (OQ-ALARMDEF).** That entry is
    parked because zero ALMD/ALMA *instructions* appear in any of the sixteen
    real programs, which remains true. Tag-based alarm *conditions* are a
    different feature, they are present in real programs, and on the evidence
    above they are one of the largest single levers on real-file error. The
    CLAUDE.md scope note has been corrected accordingly.

    **What the existing `alarmcond_*` batch already covers, and its two gaps.**
    39 of 43 rows captured clean. `alarmcond_count_bare_n000..n128` pins
    800 + 500 per condition exactly; `alarmcond_count_real_n001..n128` runs at
    exactly 1,104 per condition (500 + 604 of associated-tag cost), which is
    within 4 bytes of Griffin's measured 1,107.8 — the synthetic family and the
    real Griffin agree. Elmsdale at 1,215.2 is the outlier. Every row in the
    family reads `predicted = actual − 16` including `n000`, which has zero
    conditions, so that 16 is the generator shell and not an alarm term — it
    must not be wired as one.

    Never captured, and both are real gaps: `alarmcond_type_{trip, trip_high,
    trip_low, deviation}` (condition type is assumed free and has never been
    measured; every real condition is `TRIP`) and `alarmcond_hmigroup_len64`.

    **Next measurement, and it is small.** Hold condition count fixed and sweep
    **conditions per associated array element** (1:1, 2:1, 4:1) and array size
    independently — that is the only structural difference the audit left
    standing. Four to six files, plus the four never-captured
    `alarmcond_type_*` rows re-submitted.


46. **OQ-LADDERBASE** — new 2026-09-14, and it blocks every conclusion the
    strip ladder produced on Elmsdale. **The per-program strip batch and the
    category ladder batch cannot both be true, and the discrepancy is
    18,000–25,000 bytes.**

    Nine per-program variants of `elmsdale_20251017r01` were captured — each
    the full export minus exactly one `<Program>`. Scored against the captured
    full-file actual of 1,147,896, every one of the nine is under-charged by a
    near-constant amount that has no relationship to program size:

    | program removed | routines | rungs | actual drop | predicted drop | engine |
    |---|---:|---:|---:|---:|---:|
    | `TiltHoist` | 21 | 267 | 109,004 | 81,264 | +27,740 |
    | `TiltHoist_Infeed` | 10 | 79 | 37,640 | 18,892 | +18,748 |
    | `Inputs` | 4 | 110 | 33,956 | 15,256 | +18,700 |
    | `Outputs` | 4 | 33 | 27,948 | 9,520 | +18,428 |
    | `TiltHoist_Outfeed` | 5 | 31 | 29,036 | 11,008 | +18,028 |
    | `InfeedData` | 4 | 31 | 36,488 | 19,160 | +17,328 |
    | `PlanerInterface` | 3 | 21 | 26,376 | 9,932 | +16,444 |
    | `Housekeeping` | 5 | 27 | 25,508 | 9,280 | +16,228 |
    | `AlarmsAndMessages` (the program) | 3 | 114 | 36,324 | 20,764 | +15,560 |

    **Those sum to +167,204 against a whole-file residual of +30,432 — 5.5x
    too much.** A per-program cost cannot behave that way. A 3-routine program
    and a 21-routine program cannot both cost ~17,000 more than predicted while
    the file containing all nine is only 30,432 short.

    **It is a baseline problem, not a model problem, and two independent checks
    say so.**

    *Base-free check.* `Inputs` and `Outputs` carry the same four routine names
    (`C102`, `JB101`, `Main`, `MCP101`) and differ only in content — 110 rungs
    against 33. Their predicted drops differ by 5,736 and their actual drops by
    6,008: **a gap of 272** with no baseline involved at all. The engine is
    right on the margin; the constant is common to every variant, which is the
    signature of a wrong shared base.

    *Solving for the base.* Setting each program's error to zero implies a
    full-file actual of 1,129,148 … 1,132,336 for seven of the nine, tightly
    clustered. Taking the median, **1,129,868 — 18,028 below the captured
    1,147,896** — re-scores the batch as:

        TiltHoist_Outfeed      +0        InfeedData          -700
        Outputs             +400        Housekeeping      -1,800
        Inputs              +672        PlanerInterface   -1,584
        TiltHoist_Infeed    +720        AlarmsAndMessages -2,468
        TiltHoist         +9,712

    Eight of nine inside ±2,500, from +15,560…+18,748. (This fit is circular on
    its own — the base is derived from the same rows it then scores. The
    independent evidence is below.)

    **THE INDEPENDENT CONFIRMATION, and it closes a second anomaly at the same
    time.** The alarms step does not use any per-program file. Re-scored against
    1,129,868 it goes from **+21,440 to +3,412**, and Elmsdale's cost per alarm
    condition moves from 1,215.2 to **1,125.1** against Griffin's measured
    1,107.8. The 107-byte-per-condition disagreement that OQ-ALARMCONDREAL was
    opened for is 17 bytes once the base is corrected. **One wrong number
    explains both anomalies**, which is a far better account than two unrelated
    structural effects.

    **What does NOT reconcile, and why nothing may be wired yet.** The Trials
    ladder rungs are still inconsistent with that base. `NoProgramLogic`
    (760,800) and `NoLogic` (733,988) imply the engine OVER-charges program
    content by 29,676, while the rebased per-program batch implies it is right
    to within about +4,950 in total. Those differ by roughly 34,600. Also
    unexplained: removing the whole `AlarmsAndMessages` **program** costs
    36,324 actual, while removing its same 3 routines **and** all 63 program
    tags **and** all 9 program shells costs 26,812 — strictly more content for
    strictly less memory, which no monotone cost model permits. (Neither of
    those touches the controller Alarm Manager, which is stripped by a
    different file.)

    So one of the two capture sessions carries an error of 18,000–25,000 and
    the arithmetic cannot say which. **Every Elmsdale conclusion in
    OQ-REALUNDER, OQ-ALARMCONDREAL and the logic-step split is provisional
    until this is settled.** Griffin's ladder is unaffected — it is a separate
    program captured in one pass and its steps close without a floating base.

    **CAPTURE ERRORS: none. RECAPTURED CLEAN, verified 2026-09-18.** The rows
    this entry used to flag as captured-with-errors now carry `error_count = 0`
    in the manifest, so their `actual_bytes` is trustworthy and every number
    above is drawn from clean captures. `scripts/capture_errors.py` routes no
    errored row here any more; the old block was a warning that had outlived
    its cause.

    **The measurement that settles it, and it is three files in one session:**
    the unmodified full export, `Elmsdale_NoAlarms`, and any one per-program
    variant, captured back to back without the software being restarted between
    them. If the full export reads ~1,129,868 the per-program batch is right and
    the Trials full-file number was wrong; if it reads 1,147,896 again then the
    per-program batch shares a common defect and the ladder stands.


50. **OQ-TAGSHAPE** — new 2026-09-18. **Controller tags are 59.00% of all
    predicted mass across the sixteen, so the whole residual would be a 2.36%
    error there. It is not. Every tag shape real programs use is already
    covered, and the gaps that do exist are too small to hold it.**

    Recorded as a NEGATIVE result so this is not re-opened as the obvious
    place to look. Surveyed 31,532 real tags against 91,641 corpus tags over
    3,479 captured files:

    | shape | real | corpus | verdict |
    |---|---:|---:|---|
    | `Base` | 96.05% | 98.89% | covered |
    | `Alias` | 3.77% | 1.11% | covered, formula wired |
    | `Produced` | 0.11% | **0.00%** | **never tested** |
    | `Consumed` | 0.06% | **0.00%** | **never tested** |
    | scalar | 93.44% | 95.90% | covered |
    | 1-D array | 6.40% | 4.10% | covered |
    | 2-D array | 0.16% | **0.00%** | **never tested** |

    Child elements per 1,000 real tags with **zero** corpus coverage:
    `ProduceInfo` 1.14, `ConsumeInfo` 0.60, `Maxes` 0.35, `Mins` 0.35.

    **None of those can hold the residual.** Produced, Consumed and 2-D array
    tags together are **0.33% of real tags** — at 84 bytes of flat base each,
    the entire untested population is about 8,700 bytes against a residual of
    653,678. They are worth one cheap file each for completeness, not a
    capture session.

    **The name-length term was the strongest-looking candidate and is
    CLEARED.** Real tag names run far longer than the corpus average — 91% are
    8 characters or more and **53% are 16 or more**, against a corpus that is
    **56.83% names of 0–7 characters** and only 2.74% in the 16–23 bucket. An
    8-bytes-per-8-characters term (`tag_overhead.per_8_chars`) calibrated on
    short names and applied to long ones is exactly the extrapolation that
    broke array-of-STRING past n=100. It is not broken here: the name-length
    families are **88 clean rows at mean 0.1207%, 66 of them byte-exact**, and
    they cover 4, 8, 16, 32 and 40 characters directly.

    **What remains unexplained on the tag side.** 368 distinct real DataTypes
    appear in no corpus file at all, covering **4,950 tags — 15.7% of the real
    population** (`SpecialInputs` 1,013, `DigitalSensor` 738,
    `SingleSolValve` 369, `ts_CIPAxis` 358, `PTimer` 279). These are
    customer UDTs and AOIs, and they are sized structurally from their own
    member lists rather than by name, so there is no per-type constant to be
    wrong. That reasoning is an argument, not a measurement, and it is the one
    thread here still worth pulling if `OQ-RUNGSHAPE` does not close the gap.

    **Conclusion: the residual is not in tag DATA SPACE.** It is in the
    18.25% of mass that is compiled logic, where the evidence gap is
    measured and large — see `OQ-RUNGSHAPE`.

    **THE THREE UNCOVERED SHAPES ARE NOW BUILT, 2026-09-18.** 2-D arrays are
    the `rshape_sub2d_{a,b,c}` ladder under `OQ-RUNGSHAPE`; Produced and
    Consumed are `prodcons_{base,produced,consumed}` — 20 tags of one UDT
    each, differencing against the Base control on tag type alone. Both
    shapes are copied from a real export (Elmsdale's `TiltHoistToPlaner` and
    `PlanerToTiltHoist`) rather than extrapolated, including the part most
    likely to be got wrong: neither carries a `<Data>` element.

    **PRE-REGISTERED PREDICTION: all three at 22,648 bytes.** The engine
    charges Produced and Consumed exactly as Base, so a split says the
    `ProduceInfo` / `ConsumeInfo` block carries a cost the model has no term
    for. This closes a coverage claim rather than chasing the residual — the
    entry's own arithmetic puts the whole untested population at about 8,700
    bytes against 653,678.

    **PRODUCED / CONSUMED TAGS ARE CLOSED, 2026-09-18 — FORCE-CLOSED, NOT
    SOLVED.** Produced tags do carry an unmodeled +1,072 bytes each, and it is
    not worth another file: they are **0.11% of real tags**, Consumed 0.06%,
    and the bulk of what such a tag costs is already charged through its UDT
    definition and its module. The measurement and the reasoning are in
    `RESOLVED_QUESTIONS.md`. **Do not reopen this and do not spec another
    produced/consumed file.**

    **CAPTURE ERRORS: 1 row(s)** — `prodcons_consumed`, `error_count = 20`,
    one per Consumed tag. It names this entry in its manifest description so
    it routes here, but the question it belonged to is closed; the row is
    suspect, is not used in either direction, and no re-test is planned. See
    the force-close in `RESOLVED_QUESTIONS.md`.

    The 2-D array thread from this entry IS resolved on its own terms:
    subscripting a 2-D array costs 0, the declaration costs 1,688 measured
    against 1,684 predicted. That leaves no uncovered real tag shape worth a
    capture slot.

## OQ-CTLSHELL — **CLOSED 2026-09-18. The gap it was opened for does not
    exist; it was two bookkeeping errors compounding.**

    The entry claimed a bare real controller shell read **21,096 against a
    predicted 13,296** — 7,800 bytes of "unpriced controller-shell content
    that generated files do not carry". It was the last remaining structural
    lead in the project and the only candidate the ceiling result did not
    bound. Both numbers were wrong.

    **The engine predicts a File|New project exactly.** A fresh 1756-L81E at
    v35 reads **18,112**; the engine predicts **18,112**. Confirmed twice
    independently — read off a new Studio project, and back-solved from
    captures: `emptyrungs_n00010` at 18,272 and `emptyrungs_n00100` at 19,712
    give 16 bytes per empty rung, so the zero-rung base is 18,272 − 160 =
    18,112.

    **Error one, mine: a component compared against a whole-file total.**
    13,296 is `empty_project_baseline_bytes`, the controller-only scaffolding.
    The MainTask/MainProgram/MainRoutine that File|New also creates are charged
    separately at 4,816, and 13,296 + 4,816 = 18,112. The "prediction" in the
    table below was never the engine's prediction for that file.

    **Error two, in the record: the actual was wrong.** Griffin `_Empty` is
    **17,352**, not 21,096.

    | | actual | predicted | delta |
    |---|---:|---:|---:|
    | as recorded | 21,096 | 13,296 | +7,800 |
    | corrected actual only | 17,352 | 13,296 | +4,056 |
    | **both sides corrected** | **17,352** | **18,112** | **−760** |

    The sign flips: the engine **over**-charges that shell by 760, it does not
    under-charge it by 7,800.

    **Consequence, and it is the important part.** This was the only measured
    evidence of content the engine does not count at all — the one shape the
    ceiling experiment could not bound. There is now **no such evidence
    anywhere**, which strengthens rather than weakens the conclusion in
    `docs/TASKS.md`: no per-category correction reaches the stopping rule, and
    nothing else is known to be missing.

    **Kept from this reading, unwired:** a dual-IP / DLR controller
    configuration costs **+40 bytes** (Elmsdale 17,320 → 17,360). One reading,
    one controller, far below the noise floor — recorded so it is not
    re-measured, not queued as work.

    **Two rules this leaves behind.** Quote a whole-file prediction against a
    whole-file capture, never a component against a total; `predict_batch` is
    the only output comparable to a Capacity reading. And any number derived
    from the strip ladder is suspect by default — those files were later found
    not to import at all.

