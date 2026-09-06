# Project Plan

Phases, their exit criteria, and their status. Day-to-day work and the
current focus live in `ROADMAP.md`; this file is the structural plan.

| phase | scope | status |
|---|---|---|
| 0 | Setup | closed |
| 1 | Tag / UDT sizing engine | closed |
| 2 | UI v1 — tags only | closed |
| 3 | Sample validation round 1 | closed 2026-08-24 |
| 4 | Logic sizing: bit logic | closed |
| 4b | Logic sizing: other instruction classes | closed |
| 4c | AOI sizing | instance sizing closed; definition cost open |
| 4d | Motion structures | closed |
| 4e | Combined final validation | **active** |
| 5 | UI v2 — logic browsing | closed 2026-08-27 |
| 6 | Polish / edge cases | mostly closed |

Phases 4 through 4e were worked in parallel rather than in sequence, driven
by whichever real capture data came back each batch. Phase 5 was completed
early because its checklist was pure UI and data-contract work on top of
already-wired sizing, with no dependency on capture data.

---

## Phase 0 — Setup
Repo scaffold, stack selection, sample corpus folder and manifest convention.

**Exit criterion:** project skeleton runs and can load and print the raw XML
of a sample L5X. *Met.*

## Phase 1 — Tag / UDT sizing engine
The calculable-with-confidence half of the tool, built first because it does
not depend on empirical logic-compilation data.

- Parse `Controller/DataTypes` into a recursive size calculator
- Parse `Controller/Tags` and `Programs/Program/Tags`, resolving each tag's
  type to a byte size
- Atomic type table, BOOL packing, STRING and custom-string overhead, array
  overhead — all sourced from `MEMORY_MODEL.md`, never hardcoded
- Emit a flat list of `{path, category, bytes, %of_total}`, which is the data
  contract the UI consumes

**Exit criterion:** given any L5X, the engine emits a full byte breakdown for
every tag and UDT. *Met.*

`Controller/Modules` parsing was deferred out of this phase and completed
later; see Phase 6 and `IO_MODULES.md`.

## Phase 2 — UI v1 (tags only)
Treemap rooted at controller tag space plus per-program tag space, a list
view sortable by name/type/bytes/percent, and a type-utilization summary.

**Exit criterion:** a tags-only L5X renders correctly as treemap, list and
type summary. *Met.*

## Phase 3 — Sample validation round 1
Generate controlled L5X samples, import them into Studio 5000, download to a
real controller, record actual memory used, and compare against prediction.

**Exit criterion:** tag/UDT/AOI predictions match real controller memory
across the sample set, with every remaining discrepancy explained rather than
absorbed into a fudge factor. *Met 2026-08-24* — 0.00% residual across the
confirmed-formula majority of the corpus, and every remaining discrepancy is
a named open question with its own generator already built.

## Phase 4 — Logic sizing, round 1: bit logic
Samples isolating single instruction types at scale — N rungs of XIC/XIO, of
OTE, of OTL/OTU, branch-complexity variations, empty rungs, rung comments —
fitted into a first-pass per-instruction byte weight.

## Phase 4b — Logic sizing, round 2: other instruction classes
Timers and counters, math, move and logical, array and file instructions,
MSG, JSR and subroutine-call overhead, indirect addressing, and per-Task
overhead isolated from program and routine content.

**Exit criterion (4 + 4b):** the instruction weight table covers every
instruction actually used in real production programs, with residual error on
held-out samples understood and acceptable. *Met* — see
`INSTRUCTION_COVERAGE.md`.

## Phase 4c — AOI sizing
Scheduled after logic sizing so that AOI cost is never guessed on top of an
unknown program cost.

- AOI *instance* sizing: **closed.** Validation against real production
  exports showed every AOI-typed tag is a plain named Tag sized exactly like
  a UDT-typed one. Implemented in `parser/aoi.py`; sizing-engine error on the
  real corpus fell 41.6% → 29.5% (alias tags plus TIMER/COUNTER/CONTROL) →
  8.8% (AOI-instance sizing).
- AOI *definition* cost: **open.** Base plus per-item rate plus type-name
  length is wired, but seven structural properties are still unpriced — see
  `OQ-AOISTRUCT` and `AOI_KNOWLEDGE_MAP.md`.
- Nested AOI call chains: generator support built, isolation batch queued.

**Exit criterion:** AOI definitions sized and drillable at the
per-definition level, instance multiplication implemented, nested call chains
sized correctly.

## Phase 4d — Motion structures
AXIS_CIP_DRIVE, AXIS_VIRTUAL, AXIS_SERVO, COORDINATE_SYSTEM and MOTION_GROUP.
These are predefined Rockwell structures exported in `Data Format="Axis"`
with a flat `<AxisParameters/>` attribute list, not the
Structure/DataValueMember shape UDTs use, so they cannot be synthesized like
a UDT. They are treated as fixed predefined-structure byte constants derived
from real capture data, the same tier as TIMER/COUNTER/CONTROL. *Closed* for
the six most common structures.

## Phase 4e — Combined final validation — **active**
With tag/data, logic/program, task, AOI and module/IO sizing each
independently validated, run large realistic programs exercising all of them
together and check total prediction against real controller data end to end.
This is the actual product validation; isolated-variable sweeps are the
instrument, not the result.

**Exit criterion:** every real production export predicts total memory within
1%.

## Phase 5 — UI v2 (logic browsing)
Task → Program → Routine → Rung drill, subroutine-level rollup via the JSR
call tree, an "estimated" flag propagated everywhere a logic-derived number
appears, and a combined tags-plus-logic root view.

**Exit criterion:** the tool works end to end on a real production L5X, with
logic numbers clearly marked estimated and tag numbers clearly marked exact.
*Met 2026-08-27.*

## Phase 6 — Polish / edge cases
- Safety task handling — **done.** Safety Task/Program shells have their own
  sizing path; the UI warns that a safety project's total is understated.
  DCS and CROUT are Safety-family instructions and out of scope.
- Alarm instance overhead — **done.** Tag-based alarm conditions are solved
  exactly.
- I/O module and connection sizing — **done** for Ethernet and local in-rack
  modules. ControlNet and DeviceNet remain deferred; see `IO_MODULES.md`.
- Export and report generation — **done** (CSV and XLSX).
- Selectable controller memory budgets across CompactLogix variants — open.

---

## Backlog

1. **Any-export-type handling.** Program-only, DataType-only and AOI-only
   L5X exports as a first-class mode with the export type shown in the UI.
2. **Extended tag properties** (Min/Max, engineering units) — absent from the
   real corpus today; revisit when real usage appears.
3. **v20/v30 L5X schema support** — no real sample in hand; the corpus ranges
   v31–v35.
4. **ControlNet/DeviceNet module support.**
5. **Cross-version instruction differences.** The instruction weight table
   assumes one Designer/firmware version's behavior, and instruction names
   differ between v35.5 and v38 installs. Real fleets run mixed versions.
   Revisit once the current-version model is solid.
