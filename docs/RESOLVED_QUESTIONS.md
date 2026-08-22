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
