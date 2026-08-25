# Task List

Checkbox per phase from PROJECT_PLAN.md. ✅ done — 🟡 partially done — 🔴 open.
Anything non-obvious gets a footnote instead of inline prose — see bottom
of file. Full reasoning trails live in RESOLVED_QUESTIONS.md/
OPEN_QUESTIONS.md, not here.

## Phase 0 — Setup
- ✅ Stack decided, repo skeleton, real sample files added, manifest.csv
      created, XML load + schema sanity check

## Phase 1 — Tag / UDT / AOI sizing engine
- ✅ Atomic type sizes, BOOL packing (standalone/UDT-member/array), UDT
      parser + alignment, tag/UDT-definition overhead, array-of-atomic and
      array-of-UDT sizing, built-in + custom STRING sizing
- 🟡 Module/IO parser[^moduleio]
- ✅ Controller/program tag scope separation, flat output contract
      (`report.py` `SizeEntry`), unit tests, validated against 4 real
      production files

## Phase 2 — UI v1
Local Flask server, vanilla JS/SVG squarified treemap, no CDN dependency.
- ✅ Treemap, root view, UDT/AOI defs pool, click-to-drill (infinite
      depth, lazy `/api/node`), breadcrumbs, sortable list view,
      type-utilization pane, confidence styling (solid/hatched), File→Open
      picker + desktop shortcut, processor part number in header,
      export-type warning banner, list/type-summary scoped per level,
      breadcrumb sibling browser

## Phase 2b — AOI sizing
- ✅ AOI definition parser (locals+params size like a UDT), UI drill-down
      into defs pool, AOI definition cost wired[^aoidef], inline/anonymous
      AOI instances confirmed a zero-occurrence case (not built)

## Phase 3 — Sample validation round 1 — **CLOSED 2026-08-24**
Exit criterion met: tag/UDT/AOI predictions match real Capacity data with
0.00% residual across the confirmed-formula majority; every discrepancy is
a tracked open question with a generator already built.
- ✅ Array/UDT-array/nested-UDT/STRING/custom-string sweeps, produced/
      consumed decided not needed, AOI call-count sweep, tag-scope sweep,
      capture→reconcile→update workflow standing since Phase 0 (1299+ rows),
      final confidence documented (`docs/INSTRUCTION_COVERAGE.md`: 95.1%
      exact fit)

## Phase 4 — Logic sizing round 1 (bit logic)
- ✅ XIC/XIO/OTE/OTL/OTU at scale — CONFIRMED, 0.00% residual
- 🟡 Branch depth[^branchdepth]
- ✅ Comments cost 0 blocks at any length, empty rungs at scale, NOP rate
      confirmed

## Phase 4b — Logic sizing round 2 (other instructions)
Scope from real instruction-frequency data across James's 4 production
files; PID and ASCII-module instructions dropped (zero real occurrences).
- ✅ Timers/counters, motion+cam/route, GSV/SSV, array/file, string
      instructions, indirect addressing — all CONFIRMED and wired
- 🟡 Math/compare[^cmpcpt]
- 🔴 JSR param cost[^jsrparam]
- ✅ MSG logic weight wired (48/rung); operand's own structure cost — see
      OPEN_QUESTIONS.md OQ-PREDEFINED
- 🔴 Consolidate full instruction-weight table into MEMORY_MODEL.md —
      blocked only on JSR param cost landing
- ✅ Holdout validation[^holdout]

## Phase 5 — UI v2 (logic browsing)
- ✅ Routines/rungs share the tag data contract, Task→Program→Routine
      drill, subroutine call-tree (JSR cost-included tooltip), Estimated
      badge/dashed-outline styling, combined root view[^rootview]

## Phase 6 — Polish
- ✅ Safety-project warning (UI banner + CLI stderr)[^safety]
- 🔴 Alarm instance (ALMD/ALMA) overhead if in scope (OQ-ALARM)
- ✅ Per-part-number memory budget (`controller_budgets.yaml`, prefix-
      matched against `Controller/@ProcessorType`, unknown types show
      "budget unknown" rather than a guess)
- 🔴 Export report (CSV/XLSX)

---

[^moduleio]: `parser/modules.py` reads Connection/ConfigTag/ConfigScript
sizes straight off the L5X (Logix Designer states them directly). A flat
`module_overhead` constant is wired but only from n=2 real deltas — see
OPEN_QUESTIONS.md OQ-MODULEIO for the 141-file test batch and its status.
Produced/consumed tags (OQ-PRODCONS) still untouched.

[^aoidef]: `sizing/udt.py` `compute_aoi_definition_cost()`, FITTED not
KNOWN. Two small threads remain — see OPEN_QUESTIONS.md OQ-AOIDEF.

[^branchdepth]: Real cost confirmed (branch bracket structure costs real
memory beyond leg instructions), formula not yet fit — see
OPEN_QUESTIONS.md OQ-BRANCHDEPTH for the leg-count and staggered/nested
test batches now awaiting capture.

[^cmpcpt]: Everything except CPT is CONFIRMED. CPT's uniform-tier, T1+T2,
and T1T3/T2T3 mixed cases are solved and wired
(`sizing/constants.py` `CptExpressionModel`). Two threads remain (all-3-
tier mixes, REAL-operand/float-literal interaction) — see OPEN_QUESTIONS.md
OQ-CMPCPTLAYOUT for the diagnostic batch now awaiting capture. CMP's own
weight and OQ-OPERANDTYPE's per-type surcharge are both resolved and wired.

[^jsrparam]: JSR's own flat weight (72/rung) is wired. Per-param cost
formula is CONFIRMED general (a 3rd real point lands exactly on the
2-point-derived line) but not wired — needs `parser/logic.py` to parse
each JSR call's argument list, which it doesn't do at all today (only the
target routine name). See OPEN_QUESTIONS.md OQ-JSRPARAMCOST.

[^holdout]: 10 real captured files never used to fit anything (random
instruction-type combinations) checked against the current engine: 7/10
land within 0.05%, the other 3 fully explained by the already-tracked
OQ-CMPCPTLAYOUT gap, scaled by call count. No other instruction weight
implicated.

[^rootview]: Tags+logic share the "Program: X" root group; module I/O is
informational/non-summed `SizeError` entries by design — folding it into
the summed total is purely an OQ-MODULEIO confidence question, tracked
there only.

[^safety]: `L5XDocument.is_safety_project`/`.safety_level` parses
`Controller/SafetyInfo/@SafetyLevel`. Doesn't size Safety Task/Program
content — just warns the total is understated on a safety-rated project,
per the OQ-SAFETY decision (RESOLVED_QUESTIONS.md).
