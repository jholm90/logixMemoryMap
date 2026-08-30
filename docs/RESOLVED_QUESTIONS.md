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

**Re-checked against the current (2026-08-29) engine, full manifest.csv
audit:** `large_mixed_100tags` (+136, 0.49%) and `large_mixed_1100tags`
(+1,336, 1.07%) still land comfortably inside band. `large_mixed_
1000tags_arrays` now shows +4,416 (~3.38% of predicted) — drifted
slightly above the 2.6% figure quoted above and right at the edge of
James's "acceptable" ceiling, most likely because array-dimension/
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
used. MESSAGE's own byte cost remains unmodeled — deprioritized by James
2026-08-25 ("fine for 90% accuracy, not a common instruction"); MSG's own
LOGIC weight (48/rung) is separately resolved and wired.

## Motion, CPT, string, and task-overhead batch, 2026-08-25–26

**OQ-CROUT-MAPC-BUILDFAIL, resolved 2026-08-25.** CROUT's build failure is
not a bug — CROUT is a Safety-only instruction (James: "requires a safety
plc cpu"), reclassified OUT OF SCOPE alongside DCS. MAPC's build failure
was two real generator bugs (undeclared `Axis_Cip_Drive` tag, and
slave/master axis reusing the same tag instead of two distinct axis tags)
— fixed via `gen_axis_composite.py`/`gen_instruction_firstpass.py`'s
`group_mapc_v2`. Real capture confirmed both fixes: clean build, logic
weight = 260/rung exactly, wired in `memory_model.yaml` (`MAPC: 260`).

**OQ-MAMFAMILY-BUILDFAIL, resolved 2026-08-26.** MAM/MAJ/MAS/MRP's 100%
build failure was a generator bug, not a syntax question — each needs its
own full parameter list (James: the bare 2-operand call used is MAH/MSO's
shape, not theirs). Real corpus operand counts confirmed: MAM=20, MAJ=17,
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

**OQ-CAPTURERACE, resolved 2026-08-26.** The 6 rows flagged by James's own
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
that flow, including the `fw_baseline` files. Separately, James confirmed
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
James: "you're allowed to have a SBR with no rungs," found in 15 of his
real production files) was being silently skipped by `parse_rll_routines`,
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

James asked for a review of every numbered OPEN_QUESTIONS.md item; 2 of
them turned out to already be closed by real capture data that had landed
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

James: "I hope you are going to have the jsr param cost sorted finally."
Wired properly:
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
undetected until a full manifest.csv audit (James: "make another in-depth
pass") found `jsr_mixedio_5in_2out_r01000`/`jsr_multiret_n04_r01000` (real
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
