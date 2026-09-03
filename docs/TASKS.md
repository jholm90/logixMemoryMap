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
- ✅ JSR param cost[^jsrparam]
- ✅ MSG logic weight wired (48/rung); operand's own structure cost — see
      OPEN_QUESTIONS.md OQ-PREDEFINED
- ✅ Consolidate full instruction-weight table into MEMORY_MODEL.md
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
- ✅ Export report (CSV/XLSX)[^export]

---

[^moduleio]: `parser/modules.py` reads Connection/ConfigTag/ConfigScript
sizes straight off the L5X (Logix Designer states them directly). Real
per-catalog overhead (51 catalogs, `module_overhead_by_catalog`) replaced
the flat n=2 `module_overhead` estimate for those catalogs 2026-08-29 —
see OPEN_QUESTIONS.md OQ-MODULEIO. Two real threads remain (multi-module
marginal cost, a few connection-variant-dependent catalogs), both need
their own architecture work, not more test generation.
Produced/consumed tags (OQ-PRODCONS) RESOLVED — no special formula needed,
ordinary UDT-member recursion already covers a produced/consumed tag's
`CONNECTION_STATUS`-typed member, which is itself now a wired
`predefined_structures` entry (4 bytes, 2026-08-29 batch). See
RESOLVED_QUESTIONS.md.
**Zero-connection modules made visible 2026-09-02** (`report.py`):
modules with no Connection/stated size of their own (e.g. a bare
`ETHERNET-BRIDGE` IP-only fan-out, James's real "placeholder for IP
addresses with no PLC logic connections" pattern) were being silently
skipped with no SizeEntry and no SizeError; now flagged with an explicit
SizeError (visibility-only, no total changed) — `"Local"` itself stays
excluded since its overhead is already covered by
`empty_project_baseline`. New test file: `bridge_placeholder_*`.
Three more real module-generator bugs found and fixed the same pass (a
regex crossing `<Module>` boundaries, a nameless-module lint blind spot,
an IPv4 4th-octet overflow past ~19 catalogs/file) — see OPEN_QUESTIONS.md
OQ-V3GENBUGS. New per-catalog-shape test batches awaiting real capture:
`axis_scale_*` (18, servo/dual-axis 2198 drive count scaling),
`rack_5069_*` (11), `rack_pointio_*` (11), `rack_1756_*` (12),
`cipmodule_scale_*` (7, CIP-MODULE generic-EDS declared-I/O-size sweep —
first real test of whether the flat `module_overhead` default shows the
same "scales with declared I/O size" pattern already confirmed for
ETHERNET-MODULE/ETHERNET-PANELVIEW).

[^aoidef]: `sizing/udt.py` `compute_aoi_definition_cost()`, FITTED not
KNOWN. AOI type-name-length step CLOSED 2026-08-30 (7/7 exact). The
separate array-of-AOI-instances element-cost formula (`aoi_array`,
downgraded KNOWN→FITTED 2026-08-30) is now its own open item — see
OPEN_QUESTIONS.md OQ-AOIBOOLPACK-PAIRING. **AOI internal Logic-routine
content WIRED 2026-08-31**: `parse_aoi_internal_logic()` aggregates every
AOI's internal RLL routine(s) into one pseudo-routine, weighed with the
same per-instruction-type table as ordinary routine logic
(`charge_shell=False`) — cut max residual on the isolation sweep from
12.02% to 0.55%. Real per-instance routine-count doesn't matter (splitting
content across 2 routines costs identically to 1), so it's aggregated, not
tracked per-routine. **Composite-scale content surcharge WIRED
2026-09-02** (`aoi_logic_composite_surcharge_per_instr=20`, FITTED via
regression on 22 real composite_realistic_v2 files) — real multi-AOI/
JSR-combined project scale showed a further systematic under-prediction
beyond the per-instruction weight alone; see OPEN_QUESTIONS.md
OQ-COMPOSITESCALE for the fit and remaining unexplained variance
(R²=0.66). **Does NOT generalize to real production scale, found
2026-09-02**: `TitusvilleTrimmer_20260902r2.L5X` (real file, 179 distinct
JSR targets, vs. the 22-file/1-target-each fit) misses by +7.71% with the
surcharge applied (+824,363 bytes of surcharge overshoot) but WORSE
(-14.7%) with it removed entirely — a real, larger, separate
under-prediction in the base per-instruction weighting only shows up at
real JSR-target counts. See OPEN_QUESTIONS.md OQ-JSRSCALE; blocked on real
capture data from the newly-built `composite_realistic_v3_*` batch
(deliberately wide-varying JSR-target/program/AOI counts, not fixed at a
floor).

[^branchdepth]: Real cost confirmed (branch bracket structure costs real
memory beyond leg instructions), formula not yet fit — see
OPEN_QUESTIONS.md OQ-BRANCHDEPTH for the leg-count and staggered/nested
test batches now awaiting capture.

[^cmpcpt]: Everything except one CPT thread is CONFIRMED. CPT's
uniform-tier, T1+T2, T1T3/T2T3, and (2026-08-29) all-3-tier mixed cases
are all solved and wired (`sizing/constants.py` `CptExpressionModel`,
confirmed 0 residual on every real data point on file). One thread
remains — the REAL-operand/float-literal interaction is real data
demonstrating genuinely non-monotonic behavior, not yet a wireable
formula — see OPEN_QUESTIONS.md OQ-CMPCPTLAYOUT. CMP's own weight and
OQ-OPERANDTYPE's per-type surcharge are both resolved and wired.

[^jsrparam]: JSR's own flat weight (72/rung) and per-param cost
(`B(n)=4+20n` per call site, `A(n)=104+20n` once per distinct target)
both wired 2026-08-25. `parser/logic.py`'s `_jsr_calls()` reads the param
count off each real call's own 2nd argument. Verified end-to-end against
all 6 real capture points: 4 exact, 2 off by the same small +8 noise seen
elsewhere. **Output/return-param cost added 2026-08-29** —
`output_param_cost=20`/arg, charged per call site — see
RESOLVED_QUESTIONS.md OQ-JSRPARAMCOST for the full correction (the
original wiring only ever saw input-only calibration data) and
OPEN_QUESTIONS.md OQ-JSRPARAMCOST for the remaining residuals: A(n) not
yet output-param-adjusted, a STRING/UDT-specific per-call surcharge (not
cleanly linear yet, 3 real n-points on file). **JSR target content WIRED
2026-08-31**: `is_jsr_target` now weighs the target's own instructions with
the same per-instruction-type table as ordinary routines
(`charge_shell=False`), cutting max residual on the isolated content-scale
sweep from 13.37% to 4.75%. **Composite-scale content surcharge WIRED
2026-09-02** (`jsr_target_composite_surcharge_per_instr=47`, FITTED via
regression on 22 real composite_realistic_v2 files) — real multi-AOI/
JSR-combined project scale showed a further systematic under-prediction
beyond the per-instruction weight alone; see OPEN_QUESTIONS.md
OQ-COMPOSITESCALE for the fit and remaining unexplained variance
(R²=0.66). Same real-scale generalization failure as the AOI surcharge
above (found on `TitusvilleTrimmer_20260902r2.L5X`'s 179 distinct JSR
targets) — see OQ-JSRSCALE.

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

[^export]: `sizing/export.py`, same flat SizeEntry/SizeError contract as
the CLI `size` command and the UI, just serialized differently — no new
sizing logic. CSV is stdlib-only, always available; XLSX needs `openpyxl`
(optional `[xlsx]` extra, pyproject.toml) and degrades to a clear error
(CLI: message + exit 1; UI: 501 JSON error) rather than a broken file if
it's missing. CLI: `l5x-memory-analyzer export <l5x_path> <output_path>`,
format inferred from the output extension. UI: two toolbar buttons next to
File Open, `/api/export.csv` and `/api/export.xlsx`, downloading the
currently-loaded file's report.
