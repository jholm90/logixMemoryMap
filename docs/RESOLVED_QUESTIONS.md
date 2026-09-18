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
