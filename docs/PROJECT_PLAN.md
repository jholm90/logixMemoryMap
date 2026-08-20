# Project Plan

**Current phase: 2 — UI v1 (in progress)**

Phase 0 exit criterion met. Phase 1 tag/UDT/array/string sizing is
implemented and unit-tested; Module/IO parsing is still open (needs real
sample L5X files to verify module-tag XML shape against — none in
`samples/local/` yet). AOI sizing was pulled out of Phase 1 into Phase 2b —
an AOI is part local-tag data, part compiled logic (call-site
multiplication), so sizing it correctly means touching the same unresolved
logic-size problem Phase 4 exists to solve.

Phase 2 UI v1 is underway: local Flask server + hand-rolled vanilla JS/SVG
squarified treemap (`l5x-memory-analyzer ui <path>`), verified rendering
against both the Phase-0 fixture and a richer synthetic multi-program/UDT
fixture via headless-Chromium screenshots. Treemap, breadcrumb drill,
sortable list, and type-utilization pane are working; UDT-defs-pool /
module-overhead root groups and UDT-member drill-down are not yet built
(see docs/TASKS.md for the precise cut line).

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
part of this phase — see Phase 2b.

- Parse `Controller/DataTypes` (UDTs) → recursive size calculator
- Parse `Controller/Modules` → I/O tag + connection size
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

## Phase 2b — AOI sizing (deferred from Phase 1)
Picked up once the UI shell exists, so AOI's local-tag-plus-logic-call-site
nature doesn't stall UI progress. Definition-level sizing (locals + params)
is tag-like and tractable now; instance multiplication needs call-site counts
and is likely blocked on Phase 4 logic parsing (OQ-AOIINSTANCE) — expect this
phase to close partially and finish once Phase 4 lands.

- Parse `Controller/AddOnInstructionDefinitions` → AOI definition size
- Click-to-drill into an AOI to see local/param-level breakdown (UI addition)
- AOI instance multiplication per call site (may stub pending Phase 4)

**Exit criterion:** AOI definitions sized and drillable in the UI at the
per-instance-definition level; instance multiplication either implemented or
explicitly stubbed with the blocking dependency documented.

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
- Same sample → record → fit loop
- Consolidate into a single instruction-weight table in `MEMORY_MODEL.md`,
  flagged as fitted/estimated, with the sample corpus size and residual error
  documented next to it

**Exit criterion (4 + 4b):** instruction weight table covers every instruction
type actually used in real production programs (not exhaustive AB instruction
set — scope to what's actually in use), residual error on held-out samples is
understood and acceptable.

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
