# Project Plan

**Current phase: 3 — Sample validation round 1 (tags/UDTs), in progress**

Phase 0 exit criterion met. Phase 1 tag/UDT/array/string sizing is
implemented and unit-tested; Module/IO parsing is still open (needs real
sample L5X files to verify module-tag XML shape against — real files exist
in `samples/local/` now, this just hasn't been picked up yet).

Phase 2 UI v1 merged (PR #2): local Flask server + hand-rolled vanilla JS/SVG
squarified treemap (`l5x-memory-analyzer ui <path>`), verified rendering via
headless-Chromium screenshots. Treemap, breadcrumb drill, sortable list, and
type-utilization pane are working; UDT-defs-pool/module-overhead root groups
and UDT-member drill-down are not yet built (see docs/TASKS.md).

**Phase 2b (AOI sizing) reordered to Phase 4c, 2026-08-20** — James: don't
want to guess AOI size until program logic size is known. What was already
built there (AOI-instance = plain UDT-shaped tag, real-corpus validated,
`parser/aoi.py`) stays in place; the phase itself now runs after Phase 4/4b.

Phase 3 is the active phase: real Studio 5000 Capacity-tab data collected
against 80+ generated samples so far (2026-08-20), see docs/OPEN_QUESTIONS.md
OQ-TAGOVERHEAD for the full results. Several genuinely exact, confirmed
constants have come out of this round already (flat per-tag overhead formula,
UDT-definition-cost-vs-member-count formula, comments cost zero at every
location tested) — see the status summary in chat/OPEN_QUESTIONS.md for what's
closed vs still open before this phase's exit criterion is met.

Update the line above as phases close. Each phase has an exit criterion; don't
start the next phase until it's met, even if it's tempting to jump ahead on UI
because it's more fun than writing another sizing table.

---

## Phase 0 — Setup
- Repo scaffold (this)
- Pick stack (see Open Questions — OQ-STACK)
- L5X sample corpus folder + manifest convention

**Exit criterion:** empty project skeleton runs, can load and print raw XML of a
sample L5X file.

## Phase 1 — Tag / UDT sizing engine
Build the calculable-with-confidence half of the tool first, since it doesn't
depend on empirical logic-compilation data. AOI sizing is intentionally not
part of this phase — see Phase 4c.

- Parse `Controller/DataTypes` (UDTs) → recursive size calculator
- Parse `Controller/Modules` → I/O tag + connection size — **deferred, James
  2026-08-20: "we will leave the module stuff to later, after we get program
  logic sizing stuff taken care of."** Real sample files already exist in
  `samples/local/` for when this gets picked back up; not blocking Phase 3.
- Parse `Controller/Tags` (controller-scope) and `Programs/Program/Tags`
  (program-scope) → resolve each tag's type to a byte size
- Atomic type table, BOOL packing rule, STRING/custom string overhead, array
  overhead — all sourced from `MEMORY_MODEL.md`, not hardcoded
- Output: flat list of `{path, category, bytes, %of_total}` — this is the data
  contract the UI consumes later, so nail the shape here

**Exit criterion:** given any L5X, engine emits a full byte breakdown for every
tag/UDT with no AOI or logic involved yet. Numbers are provisional (pending
Phase 3 validation) but the code path is complete end to end.

## Phase 2 — UI v1 (blank project, tags only)
- Treemap component, root = controller tag space + per-program tag space
  (no tasks/routines/AOI drilling yet, since neither is sized)
- List view sorted by % usage (the WinDirStat "file list" pane), sortable by
  name/type/bytes/%
- Type-utilization summary (the WinDirStat "file type" pane) — e.g. % of budget
  in DINT arrays vs STRING vs UDT X

**Exit criterion:** load a blank/near-blank L5X (tags only, no meaningful logic),
UI renders treemap + list + type summary correctly against Phase 1 output.

## Phase 3 — Sample validation round 1 (tags/UDTs only)
- Generate controlled L5X samples (10k BOOL array, 10k DINT array, 10k-element
  UDT array, nested UDT, string arrays, produced/consumed tag, AOI called N
  times) — see `SAMPLE_GENERATION.md`
- Import each into Studio 5000, download to a real/emulated CompactLogix,
  record actual memory used (see `TESTING_PLAN.md` for exact procedure)
- Compare predicted vs actual, adjust constants in `MEMORY_MODEL.md`
- Re-run until delta is consistently small and understood (not just tuned away)

**Exit criterion:** tag/UDT/AOI predictions match real controller memory within
an agreed tolerance (TBD — see OQ-TOLERANCE) across the full sample set, and
every remaining discrepancy is explained, not just absorbed into a fudge factor.

## Phase 4 — Logic sizing, round 1: bit logic
- Generate samples isolating single instruction types at scale: N rungs of
  XIC/XIO only, N rungs of OTE only, N rungs of OTL/OTU, branch complexity
  variations, empty rungs, rung comments (do comments cost memory? — OQ-COMMENTS)
- Record actual memory delta per sample
- Fit a first-pass per-instruction byte weight

## Phase 4b — Logic sizing, round 2: other instruction classes
- Timers/counters (TON/TOF/RTO/CTU/CTD), math (ADD/SUB/MUL/DIV/CPT), move/logical
  (MOV/AND/OR/MEQ), array/file instructions (COP/FLL/indirect addressing), MSG,
  JSR/subroutine call overhead, indirect/pointer addressing overhead
- **Functional call/task size** (James, 2026-08-20's "big game" category
  breakdown: tag/data size, logic/program size, functional call/task size,
  AOI size, module/IO size): JSR call-site overhead is already listed above;
  separately, per-Task overhead (adding a second/third Task, watchdog
  config, scheduled-program list) isn't yet isolated as its own variable —
  needs samples varying Task count independent of program/routine content.
- Same sample → record → fit loop
- Consolidate into a single instruction-weight table in `MEMORY_MODEL.md`,
  flagged as fitted/estimated, with the sample corpus size and residual error
  documented next to it

**Exit criterion (4 + 4b):** instruction weight table covers every instruction
type actually used in real production programs (not exhaustive AB instruction
set — scope to what's actually in use), residual error on held-out samples is
understood and acceptable.

## Phase 4c — AOI sizing (moved here 2026-08-20, was Phase 2b)
**Reordered — James, 2026-08-20: "lets change the roadmap and permanently
move AOI testing after all program logic size testing has been completed. i
dont want to guess aoi size until we know how big programs are."** AOI
instances are, by the real-corpus finding below, plain named tags sized
exactly like a UDT instance — so AOI *data-space* sizing doesn't strictly
need logic parsing. But AOI-instance *call-site multiplication* and AOI
*logic content* both do depend on knowing what a program actually costs, so
the whole phase waits until Phase 4/4b are done rather than being tested on
guesswork now.

Validating against 4 real production L5X files (2026-08-20) showed every
real AOI-typed tag is a plain named Tag sized exactly like a UDT-typed one —
no logic/call-site parsing needed for that part. That's implemented
(`parser/aoi.py`). Sizing-engine error rate on the real corpus went
41.6% → 29.5% (alias tags + TIMER/COUNTER/CONTROL) → 8.8% (AOI-instance
sizing).

- Parse `Controller/AddOnInstructionDefinitions` → AOI definition size
- Click-to-drill into an AOI to see local/param-level breakdown (UI addition)
- AOI instance multiplication per call site (needs Phase 4's logic parsing)
- **Nested AOIs (James, 2026-08-20): "nested aois need to be tested in
  phase 4 after logic size has been estimated"** — an AOI that calls
  another AOI, tested here specifically, not before. Generator capability
  built 2026-08-20 (`aoi_xml()`, supports Parameters/LocalTags, array
  dims, and a LocalTag typed as another AOI) so samples are ready to go
  the moment this phase actually starts — building the tool now isn't the
  same as running the analysis early, which stays parked per the reorder.
- AOI-instance sizing validated the same way as tags/UDTs (real Capacity-tab
  data, not just L5X-schema inference) — "aoi size needs to be validated"

**Exit criterion:** AOI definitions sized and drillable in the UI at the
per-instance-definition level; instance multiplication implemented (unblocked
by then, since Phase 4/4b are done); nested-AOI call chains sized correctly.

## Phase 4d — Motion structures (AXIS_CIP_DRIVE, AXIS_VIRTUAL, etc.)
**New, James 2026-08-20: "outside the normal scope... maybe ill just upload
a sample program you can modify."** Real reference exports provided
(`samples/generated/axis/`: MotionGroup-only baseline, AXIS_VIRTUAL,
AXIS_CIP_DRIVE, AXIS_SERVO, COORDINATE_SYSTEM, one axis type each). These
are genuinely predefined Rockwell structures exported in `Data Format="Axis"`
with a flat attribute list (`<AxisParameters .../>`), not the
Structure/DataValueMember shape UDTs use — completely unmodeled by the
sizing engine today (confirmed: `build_report` returns an UnknownDataType
error for every AXIS_* tag, doesn't crash, but sizes nothing). Can't be
regenerated synthetically like a UDT; treat as fixed predefined-structure
byte constants once real Capacity-tab numbers come back, same tier as
TIMER/COUNTER/CONTROL. James: still want tests with only CIP drives, only
virtual, and a combination of both in one project — only single-axis-type
reference files exist so far, a combined file is a real follow-up (either
he exports one, or this phase revisits it).

## Phase 4e — Big game: combined final validation
**New, James 2026-08-20 ("big game with all of the above final testing").**
Once tag/data, logic/program, functional call/task, AOI, and module/IO
sizing are each independently validated, run one (or a few) large, realistic
combined program(s) exercising all of them together and check the tool's
total prediction against real Capacity-tab data end to end — the actual
product validation, not just isolated-variable sweeps.

## Phase 5 — UI v2 (logic browsing)
- Extend treemap/list to drill into Tasks → Programs → Routines → Rungs
- Subroutine-level size rollup (JSR call tree aggregation)
- "Estimated" visual flag propagated everywhere logic-derived numbers appear
- Combined root view: tags + logic + module overhead as one 4MB pie

**Exit criterion:** full tool works end-to-end on a real production L5X, logic
numbers clearly marked as estimated, tag numbers clearly marked as exact.

## Phase 6 — Polish / edge cases
- Safety task handling (separate memory pool — scope decision needed, OQ-SAFETY)
- Extended tag properties / alarm instance overhead (OQ-ALARM)
- Multiple controller memory sizes (750KB / 1MB / 2MB / 4MB / 8MB CompactLogix
  variants) as selectable budget targets
- Export/report generation (probably reuses existing C# tooling patterns)
