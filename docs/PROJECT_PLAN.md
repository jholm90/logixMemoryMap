# Project Plan

Phases and their exit criteria. Current state and next work live in
`ROADMAP.md`; the ranked queue lives in `TASKS.md`.

| phase | scope | status |
|---|---|---|
| 0 | Setup | closed |
| 1 | Tag and UDT sizing engine | closed |
| 2 | UI v1 — tags only | closed |
| 3 | Sample validation round 1 | closed |
| 4 | Logic sizing: bit logic | closed |
| 4b | Logic sizing: other instruction classes | closed |
| 4c | AOI sizing | instance sizing closed; definition cost open |
| 4d | Motion structures | closed |
| 4e | Combined final validation | **active** |
| 5 | UI v2 — logic browsing | closed |
| 6 | Polish and edge cases | mostly closed |
| 7 | Close the residual | **active** |
| 8 | Make it safe to hand to someone else | open |
| 9 | UI polish | deferred until accuracy settles |

Phases 4 through 4e were worked in parallel rather than in sequence, driven by
whichever capture data came back each batch. Phase 5 finished early because its
checklist was pure UI and data-contract work on top of already-wired sizing, with
no dependency on capture data.

---

## Phase 0 — Setup

Repo scaffold, stack selection, sample corpus folder and manifest convention.

**Exit:** the skeleton runs and can load and print the raw XML of a sample L5X.
*Met.*

## Phase 1 — Tag and UDT sizing engine

The calculable-with-confidence half of the tool, built first because it does not
depend on empirical logic-compilation data.

- Parse `Controller/DataTypes` into a recursive size calculator.
- Parse `Controller/Tags` and `Programs/Program/Tags`, resolving each tag's type
  to a byte size.
- Atomic type table, BOOL packing, STRING and custom-string overhead, array
  overhead — all sourced from `MEMORY_MODEL.md`, never hardcoded.
- Emit a flat list of `{path, category, bytes, percent_of_total}`, which is the
  data contract the UI consumes.

**Exit:** given any L5X, the engine emits a full byte breakdown for every tag and
UDT. *Met.*

`Controller/Modules` parsing was deferred out of this phase and completed in
phase 6.

## Phase 2 — UI v1, tags only

Treemap rooted at controller tag space plus per-program tag space, a list view
sortable by name, type, bytes and percent, and a type-utilisation summary.

**Exit:** a tags-only L5X renders correctly as treemap, list and type summary.
*Met.*

## Phase 3 — Sample validation round 1

Generate controlled samples, import them into Studio, download to a real
controller, record actual memory used, compare against prediction.

**Exit:** tag, UDT and AOI predictions match real controller memory across the
sample set, with every remaining discrepancy explained rather than absorbed into
a fudge factor. *Met* — zero residual across the confirmed-formula majority of
the corpus, and every remaining discrepancy a named open question with its own
generator built.

## Phase 4 — Logic sizing round 1: bit logic

Samples isolating single instruction types at scale — N rungs of XIC/XIO, of OTE,
of OTL/OTU, branch-complexity variations, empty rungs, rung comments — fitted
into a first-pass per-instruction byte weight.

## Phase 4b — Logic sizing round 2: other instruction classes

Timers and counters, math, move and logical, array and file instructions, MSG,
JSR and subroutine-call overhead, indirect addressing, and per-task overhead
isolated from program and routine content.

**Exit (4 and 4b):** the instruction weight table covers every instruction
actually used in real production programs, with residual error on held-out
samples understood and acceptable. *Met* — see `INSTRUCTION_COVERAGE.md`.

## Phase 4c — AOI sizing

Scheduled after logic sizing so AOI cost is never guessed on top of an unknown
program cost.

- **AOI instance sizing: closed.** Every AOI-typed tag in a real export is a
  plain named Tag sized exactly like a UDT-typed one. Implemented in
  `parser/aoi.py`. Engine error on the real corpus fell from 41.6% to 29.5%
  (alias tags plus TIMER/COUNTER/CONTROL) to 8.8% (AOI instance sizing).
- **AOI definition cost: open.** One itemised form is wired and lands 122 of 124
  instrument files inside ±8, but one 8-byte term remains unexplained. See
  `AOI_KNOWLEDGE_MAP.md`.
- **Nested AOI call chains:** generator support built, isolation batch queued.

**Exit:** AOI definitions sized and drillable per definition, instance
multiplication implemented, nested call chains sized correctly.

## Phase 4d — Motion structures

AXIS_CIP_DRIVE, AXIS_VIRTUAL, AXIS_SERVO, COORDINATE_SYSTEM and MOTION_GROUP.

These are predefined Rockwell structures exported in `Data Format="Axis"` with a
flat `<AxisParameters/>` attribute list, not the Structure/DataValueMember shape
UDTs use, so they cannot be synthesised like a UDT. They are treated as fixed
predefined-structure constants derived from real capture data — the same tier as
TIMER/COUNTER/CONTROL. *Closed* for the six most common structures.

## Phase 4e — Combined final validation — active

With tag, logic, task, AOI and module sizing each independently validated, run
large realistic programs exercising all of them together and check total
prediction end to end. **This is the actual product validation; isolated-variable
sweeps are the instrument, not the result.**

**Exit:** every real production export predicts total memory within 1%. See
`ROADMAP.md` — this target has not been shown to be reachable, and the reasoning
is recorded rather than left implicit.

## Phase 5 — UI v2, logic browsing

Task → Program → Routine → Rung drill, subroutine rollup via the JSR call tree,
an estimated flag propagated everywhere a logic-derived number appears, and a
combined tags-plus-logic root view.

**Exit:** the tool works end to end on a real production L5X, with logic numbers
clearly marked estimated and tag numbers clearly marked exact. *Met.*

## Phase 6 — Polish and edge cases

- **Safety task handling — done.** Safety Task and Program shells have their own
  sizing path; the UI warns that a safety project's total is understated. DCS and
  CROUT are Safety-family instructions and out of scope.
- **Alarm condition overhead — done.** Tag-based alarm conditions are solved to
  within 0.16% on one real program and 8.8% on another.
- **Module and I/O sizing — done** for Ethernet and local in-rack modules.
  ControlNet and DeviceNet remain deferred.
- **Export and report generation — done** (CSV and XLSX).
- **Selectable controller memory budgets** across CompactLogix variants — open.

## Phase 7 — Close the residual — active

See `ROADMAP.md` for the measured state and `TASKS.md` for the ranked queue. The
short version: the residual is no longer one-sided, no per-category correction
can close it, and the one remaining shape that is not eliminated is a term not
proportional to any category the engine counts.

## Phase 8 — Make it safe to hand to someone else

The tool will meet code, naming conventions and AOI libraries nothing like the
corpus it was fitted on. **Accuracy on unfamiliar input is a different property
from accuracy on the real set, and it is not yet measured.**

1. **Never fit anything to a specific AOI, UDT or tag name.** Cost models must be
   functions of structure.
2. **Say what is not known.** The UI warns on a safety project. It should do the
   same for a platform with no real validation behind it, for a partial export,
   and for a file whose instruction mix falls outside the fitted range.
3. **Fail visibly, not silently.** Any element the model cannot price should
   surface as a coverage notice rather than vanish from the total. The plumbing
   exists; the presentation does not.
4. **First-run experience.** Install, point at a file, get a treemap. No
   `cd src`, no manual dependency steps.

## Phase 9 — UI polish

Deferred until the estimator stops moving, but kept current so the work is ready.

- Confidence shown per node, not just a global estimated flag. **Done** — see the
  confidence band model.
- A "what changed" comparison between two exports of the same program, which is
  the question actually asked when a download starts failing.
- Budget selector across controller memory sizes, with headroom shown against the
  selected target rather than a bare byte total.
- Module I/O joins the summed total once its confidence justifies it.
- Export the treemap itself, not only the CSV and XLSX tables.

---

## Backlog

1. **Any-export-type handling** as a first-class mode, with the export type shown
   in the UI. The sizing rules are already implemented; the UI is not.
2. **Extended tag properties** (Min, Max, engineering units) — absent from the
   real corpus; revisit when real usage appears.
3. **v20 and v30 L5X schema support** — no real sample in hand; the corpus spans
   v31 to v38.
4. **ControlNet and DeviceNet module support.**
5. **Cross-version instruction differences.** The weight table assumes one
   Designer and firmware version's behaviour, and instruction names differ
   between installs. Real fleets run mixed versions. Revisit once the
   current-version model is solid.
