# Task List

Checkbox per phase from PROJECT_PLAN.md. Keep granular enough that each item is
a single commit-sized unit of work.

Legend: ✅ done — 🟡 partially resolved (real, confirmed piece landed; a
genuinely separate remaining piece stays open, not just paperwork) — 🔴 open

## Phase 0 — Setup
- ✅ Decide stack (OQ-STACK) — parser language, UI framework
- ✅ Repo skeleton: `src/parser`, `src/sizing`, `src/ui`
- ✅ Real production L5X files added to `samples/local/` (gitignored),
      2026-08-20, 4 files.
- ✅ `samples/manifest.csv` created (see SAMPLE_GENERATION.md)
- ✅ XML load + namespace/schema sanity check — `parser/load.py`, records
      SchemaRevision/SoftwareRevision without enforcing a version yet

## Phase 1 — Tag / UDT / AOI sizing engine
- ✅ Atomic type size table — `sizing/memory_model.yaml` + `constants.py`
- ✅ BOOL packing rule (OQ-BOOLPACK) — standalone (4 bytes, unpacked), UDT
      member (hidden-SINT + BIT-alias), array (32-per-DINT packing)
- ✅ UDT parser: recurse `Controller/DataTypes/DataType/Members`
- ✅ UDT alignment/padding (OQ-ALIGN) — tight-packed, confidence KNOWN
- ✅ Per-tag flat overhead + UDT DataType-definition cost — `tag_overhead`/
      `udt_definition` in memory_model.yaml, wired into `report.py`
- ✅ Array-of-atomic sizing (dimension × element size)
- ✅ Array-of-UDT sizing (dimension × recursive size, per-element rounds up
      to a 4-byte boundary — OQ-ARRAYPACK, resolved)
- ✅ STRING (built-in) sizing: 4-byte LEN + configurable DATA array
- ✅ Custom STRING type sizing — separate path from generic UDT recursion,
      `Family="StringFamily"` special-cased
- 🟡 **Module/IO parser — first pass built 2026-08-27.** `parser/
      modules.py` parses `Controller/Modules/Module`; Connection/ConfigTag/
      ConfigScript sizes are read straight off the L5X (Logix Designer
      states them directly, no fitting needed for the raw size). A flat
      `module_overhead` per-module constant is wired (see OPEN_QUESTIONS.md
      OQ-MODULEIO) but only from n=2 real deltas — LOW CONFIDENCE, 141
      test files awaiting capture before this can be trusted broadly. Real
      Studio 5000 conversion errors from the 2026-08-24/25 batch (safety
      controller wiring, 5069 backplane compat, UDC ExtendedProperties,
      dup IPs/AxisIDs) all root-caused and fixed 2026-08-25 — see
      OQ-MODULEIO.
      Produced/consumed tags (OQ-PRODCONS) still untouched.
- ✅ Controller-scope vs program-scope tag separation in output
- ✅ Flat output contract: `{path, category, bytes, pct_of_total,
      confidence: exact|estimated}` — `report.py`'s `SizeEntry` (`tier` =
      exact/estimated, `basis` = KNOWN/ASSUMED/FITTED/UNKNOWN)
- ✅ Unit tests against hand-calculated small UDT (nested, mixed BOOL/DINT/
      STRING members) — `tests/test_sizing.py`, `tests/test_parser.py`
- ✅ Validated against 4 real production L5X files (2026-08-20, 3394 tags).
      Found and fixed Alias tags (now 0 bytes/KNOWN) and TIMER/COUNTER/
      CONTROL (`predefined_structures`). Error rate on the real corpus
      dropped 41.6% → 29.5%; remaining errors were AOI-instance tags
      (confirmed Phase 2b priority) and motion/axis/safety structures
      (cataloged in OQ-PREDEFINED).

## Phase 2 — UI v1
Stack: local Flask server, vanilla JS/SVG squarified treemap, zero CDN/
external-JS dependency (engineering workstations on OT networks are
frequently airgapped). `l5x-memory-analyzer ui <path>` serves it.

- ✅ Treemap component (squarified algorithm, hand-rolled in
      `ui/static/app.js`)
- ✅ Root view: controller tags / program tags (per program), sized by
      bytes
- ✅ UDT/AOI defs pool as its own root-level group (`hierarchy.py`'s
      `NON_TAG_GROUPS`)
- ✅ Click-to-drill: program → its tags
- ✅ **Click-to-drill: infinite depth, down to individual BOOL bits and
      array elements.** `sizing/tree.py` computes one level of children at
      a time via `/api/node`, no eager materialization of the whole tree.
      Verified live to 4 levels deep on a real file via headless-Chromium
      click-through.
- ✅ Breadcrumb / back navigation
- ✅ Sortable list view (name / type / bytes / %) — top-level rollup only,
      by design (expanding every array/UDT eagerly would defeat the
      lazy `/api/node` design)
- ✅ Type-utilization summary pane (% of budget per data type project-wide),
      with a color swatch per type matching the treemap
- ✅ **Color/confidence redesign.** Colors reserved for data types only;
      confidence shown as solid (KNOWN) vs. hatched (unsure) instead of
      color-coded by basis. Deterministic hash-to-HSL for arbitrary UDT/AOI
      type names.
- ✅ Load Phase-0 dev fixture, sanity-check against manual spot-checks
- ✅ **File → Open in the browser, no command prompt needed.**
      `l5x-memory-analyzer ui` (no path arg) starts empty with a File
      Open… button, uploads to `/api/load`. `scripts/LaunchUI.pyw` + a
      desktop shortcut gives a genuine double-click launch.
- ✅ **Processor part number in the header.** `load.py` parses
      `Controller/@ProcessorType`, shown alongside Schema/Software revision.
- ✅ **Export-type detection/warning.** `L5XDocument` exposes
      `target_type`/`is_controller_export`; UI shows an amber warning for
      any non-`Controller` export. Full first-class support for
      Program/DataType/AOI-only exports stays a backlog item
      (OQ-EXPORTSCOPE).
- ✅ **List/Type Summary scoped to current tree level.** Both tabs render
      the current node's direct children, percentages relative to that
      node's own total, re-rendering on every navigation.
- ✅ **Breadcrumb sibling browser.** Hovering a non-root breadcrumb segment
      shows up to 10 sibling nodes under its parent; click to jump
      sideways. Entirely client-side (ancestors' children already cached).

## Phase 2b — AOI sizing (deferred from Phase 1)
- ✅ AOI definition parser: `AddOnInstructionDefinitions` local tags +
      params — `parser/aoi.py`. Every AOI-typed tag sizes like a UDT-typed
      tag (AOI definitions merged into the same `data_types` dict
      `compute_udt_size` recurses); `InOut` Parameters excluded (reference,
      not storage). Dropped sizing-engine error rate on the real corpus
      from 29.5% → 8.8%.
- ✅ **UI: click-to-drill into a UDT/AOI defs pool node → locals+params
      breakdown.** `sizing/tree.py`'s `expand_definition_children()` breaks
      a definition's flat cost formula into one row per member/param/local.
      Verified end-to-end against 2 real generated files — children sum
      back exactly to the parent's own value.
- ✅ **AOI definition cost — WIRED (OQ-AOIDEF), FITTED not KNOWN.**
      `sizing/udt.py`'s `compute_aoi_definition_cost()`. See
      OPEN_QUESTIONS.md OQ-AOIDEF for the 2 remaining small open threads.
- ✅ **AOI instance multiplication for inline/anonymous instances —
      resolved by real corpus evidence, not built (correctly).** All 6,075
      real AOI call sites found across 83 real files have a plain
      tag-like first argument — zero anonymous/inline instances exist in
      practice. Not worth building speculative logic for a zero-occurrence
      case.

## Phase 3 — Sample validation round 1 — **CLOSED 2026-08-24**

James, 2026-08-24: "we have done lots of stuff in phase 3. I want phase 3
closed now." Exit criterion met: tag/UDT/AOI predictions match real
Capacity-tab data with 0.00% residual across the confirmed-formula majority
of the real corpus; every remaining discrepancy is a named, tracked open
question with its own generator already built. `empty_project_baseline`'s
processor/firmware scoping (OQ-BASELINE-PROCFW) and the odd-byte-count
UDT-array residual are the two most significant open threads carried
forward, not closed by this phase.

- ✅ 1000 standalone BOOL controller tags vs. 0-tag baseline — superseded
      by the confirmed per-tag flat overhead formula
- ✅ 10k-element BOOL array — `boolarray_n*` spans 8-5000 elements, exact
      `ceil(dim/32)×4` fit
- ✅ 10k-element DINT array — `array_dint_*` spans 1-5000 elements, exact
      `dimension×4` fit
- ✅ 10k-element UDT array — `udtarrayalign_tight8b_n*`, zero per-element
      padding for a tight UDT
- ✅ 10k-element array of a NOT-4-byte-aligned UDT — `arraypack_odd3b_n*`
      spans 1-5000, resolved (elements round up to 4-byte boundary)
- ✅ Nested UDT (3 levels) — `nested_udt_3level.L5X`
- ✅ STRING array (82-byte) ×1000 — `string_builtin_x1000.L5X`
- ✅ Custom string type (250-char) ×1000 — `customstring_250char_x1000.L5X`
- ✅ Produced/consumed tag pair — decided not needed (OQ-PRODCONS): a
      correctly-built produced/consumed tag's DataType already includes a
      `CONNECTION_STATUS`-typed member, ordinary UDT recursion covers it;
      zero produced/consumed tags exist in the real corpus anyway
- ✅ AOI with 5 local tags, called 50× vs 1× —
      `aoi_realistic_50_instance_1.L5X` / `_array.L5X`
- ✅ Program-scope vs controller-scope identical tag — resolved via
      OQ-TAGSCOPE, zero cost difference
- ✅ Import → verify/compile → record actual bytes → log in manifest.csv —
      standing per-batch workflow since Phase 0, 578+ real rows as of
      2026-08-23
- ✅ Reconcile predicted vs actual, update MEMORY_MODEL.md constants —
      ongoing standing practice, not a one-time task; bar is cleared
- ✅ Re-run full sample set after each constant change until stable — same,
      now just how the project works
- ✅ Document final confidence/tolerance achieved — every MEMORY_MODEL.md
      constant tagged KNOWN/ASSUMED/FITTED/UNKNOWN;
      `docs/INSTRUCTION_COVERAGE.md` quantifies it: 95.1% of all real
      instruction usage across the corpus is an exact confirmed fit

## Phase 4 — Logic sizing round 1 (bit logic)
Real data note: 126 of 560 real routines (~22%) are Structured Text, not
RLL — ST uses different syntax and its compiled-size characteristics vs.
equivalent RLL are still completely unknown, worth its own sample set once
RLL bit logic is fully fitted.

- ✅ N rungs (10/100/1000+) of single XIC + single OTE, empty branches —
      CONFIRMED, 0.00% residual (`docs/INSTRUCTION_COVERAGE.md`)
- ✅ Same counts for XIO, OTL, OTU — CONFIRMED, 0.00% residual
- 🟡 Branch depth variations (1/3/5 parallel branches) at fixed rung count
      — real cost found, not yet a formula, see OPEN_QUESTIONS.md
      OQ-BRANCHDEPTH
- ✅ Rung comment presence vs absence — comments/descriptions cost ZERO
      blocks at every tested length (0-200 chars)
- ✅ Empty (content-free) rungs at scale — `emptyrungs_n00010/00100/01000`
      captured; NOP's marginal rate confirmed as part of OQ-TASKOVERHEAD's
      resolution
- ✅ Record actual memory delta per sample — done for every ✅ item above
- ✅ Fit initial per-instruction weight, log residuals — done for every ✅
      item above

## Phase 4b — Logic sizing round 2 (other instructions)
Scope set from real instruction-frequency data (OQ-INSTRUCTIONSCOPE) — 24,941
real instruction instances counted across James's 4 production files. PID and
ASCII-module instructions dropped entirely (zero real occurrences).

The 244-file per-instruction sweep (`gen_logic_sweep.py`) covers bit logic,
timers/counters, math/compare, array/file, string, GSV/SSV, and JSR — 42
instructions fitted at 0.00% residual, full table in `docs/MEMORY_MODEL.md`.

- ✅ Full-directory AHK build/verify batch review, 2026-08-22 — found and
      fixed real generator bugs (SIZE's array-subscript syntax, undeclared
      tags in rung-count sweeps, LBL requiring a trailing NOP, CMP compound
      condition syntax needing `&&` not `&`)
- ✅ Re-capture genuine title-bar-mismatch rows — all now have clean real
      data (auto-retry fix in `batch_memory_capture.ps1`)
- ✅ Re-run ACD conversion + capture for CPS/COP/FLL/BTD/SIZE/xic_ote_1000/
      LBL-JMP/CMP compound — all 39 rows now carry real `actual_bytes`
- ✅ Timer instructions (TON/TOF/RTO/CTU) at scale — CONFIRMED, 0.00%
      residual
- 🟡 **Math/compare instructions (MOV/EQU/ADD/NEQ/GRT/MUL/GEQ/LES/SUB/LIM/
      LEQ/DIV/CPT).** Everything except CPT is CONFIRMED. CPT: real
      per-operand expression parser built and wired (`parser/logic.py` +
      `sizing/logic.py`'s `CptExpressionModel`, replacing the old
      flat-wrong `CPT: 452`). Uniform-tier case and the T1+T2 mixed-tier
      case are both resolved and wired (RESOLVED_QUESTIONS.md OQ-CPT).
      T1T3/T2T3 pairs, all-3-tier mixes, and REAL-operand/float-literal
      interaction inside a mixed expression remain open — see
      OPEN_QUESTIONS.md OQ-CMPCPTLAYOUT. CMP's own weight (76/rung,
      +64/rung compound-condition surcharge, +72/rung float-literal
      surcharge) is resolved and wired (RESOLVED_QUESTIONS.md
      OQ-CMP weight). Operand data type (OQ-OPERANDTYPE) is resolved and
      wired: 13 type-sensitive instructions apply a real SINT/INT/REAL/
      STRING surcharge over their DINT-rate base weight.
- ✅ **Motion instructions (MAM/MAS/MAJ/MAH/MSO/MSF/MDW/MAW/MASR/MAFR) and
      cam/route (DCS/CROUT).** All confirmed and wired (RESOLVED_QUESTIONS.md
      OQ-MAMFAMILY-BUILDFAIL, OQ-CROUT-MAPC-BUILDFAIL). CAM structure
      (base=8, per_element=12) also resolved and wired.
- ✅ GSV/SSV instruction overhead — CONFIRMED, wired (~90 real uses across
      the corpus, James called these out explicitly)
- ✅ Array/file instructions (COP/CLR/FLL/BTD/MVM) at varying array size —
      all CONFIRMED, 0.00% residual
- ✅ String instructions (CONCAT/DTOS/SIZE/MID/TRUNC) — all CONFIRMED
      (TRUNC has 0 real corpus occurrences, never separately tested —
      flagged, not a gap in practice)
- ✅ **Indirect addressing overhead — WIRED.** Parser scans rung text for
      `Name[...]` brackets, classifies direct/literal (0 cost), tag-driven
      (+84/rung), or tag+literal-offset (+108/rung). KNOWN confidence.
- 🔴 **JSR/subroutine call overhead.** JSR's own flat weight (72/rung) is
      CONFIRMED and wired. Per-param cost decomposition mechanism is
      solved (`A(n)=104+20n`, `B(n)=4+20n`) but only from 2 param counts —
      not yet confirmed general, not wired. See OPEN_QUESTIONS.md
      OQ-JSRPARAMCOST.
- ✅ MSG instruction overhead — only 4 real uses, low priority. LOGIC
      weight resolved (48/rung); operand's own MESSAGE-structure tag cost
      stays unmodeled, deprioritized (OPEN_QUESTIONS.md OQ-PREDEFINED).
- 🔴 Consolidate full instruction-weight table into MEMORY_MODEL.md — table
      exists and is kept current; blocked only on OQ-JSRPARAMCOST landing.
- 🔴 Hold out 3-5 samples, validate fitted model against them, log residual

## Phase 5 — UI v2 (logic browsing)
Built while waiting on test captures — none of this needed real capture
data, it's UI/data-contract work on top of already-wired logic sizing.

- ✅ Extend data contract: routines/rungs feed the same
      `{path, bytes, confidence}` shape as tags — already true, confirmed
      and smoke-tested. Rung-level entries deliberately don't exist (too
      granular to be visually useful).
- ✅ **Treemap drill: Task → Program → Routine.** `parser/tasks.py`
      (`parse_tasks`/`program_to_task_map`) wired through `hierarchy.py`/
      `server.py`. No parser "sizing awareness" needed — a Task's total is
      just the sum of its Programs' already-correct bytes. Smoke-tested
      live: full breadcrumb `All > Task > Program > Routines > Routine`,
      correct nesting and totals.
- ✅ **Subroutine call-tree (lightweight version).** `RoutineLogic.
      jsr_target_names` (parser/logic.py) captures which routine(s) each
      routine calls; `server.py` exposes it as `jsr_calls`; tooltip/list
      view show "Calls via JSR: X (cost already included above)." Not a
      full interactive call-graph — targeted fix for making the existing
      double-counting-prevention visible/explainable in the UI.
- ✅ **"Estimated" badge/color on every logic-derived number.** New
      `.tier-chip` shown alongside (never merged with) the existing
      basis-chip; dashed outline on estimated-tier treemap rects. Tier and
      basis are deliberately separate confidence axes per CLAUDE.md.
- 🟡 **Combined root view merging tags + logic + module overhead.**
      Tags+logic have always shared the same "Program: X" root group.
      Module I/O is surfaced as informational, non-summed `SizeError`
      entries — deliberately not merged into the byte map since its
      formula isn't confirmed yet (OQ-MODULEIO).

## Phase 6 — Polish
- 🔴 Safety task scope decision implemented (OQ-SAFETY)
- 🔴 Alarm instance (ALMD/ALMA) overhead if in scope (OQ-ALARM)
- ✅ **Per-part-number memory budget.** Real capacity ranges 0.6MB-40MB by
      catalog number, was hardcoded to a flat 4MB. `sizing/
      controller_budgets.yaml` + `controller_budgets.py` looks up
      `Controller/@ProcessorType` (prefix-matched) against a sourced table;
      unknown processor types show "budget unknown" rather than a guess.
      Confirmed CompactLogix 5380/ControlLogix 5580/5590 (James's actual
      target hardware) use one unified memory pool, unlike legacy
      ControlLogix 5570's split I/O/Data pools. Table deliberately
      incomplete (e.g. 5069-L340ER/L350ER unconfirmed by any source, left
      out); 1769-Lxx CompactLogix 5370 not covered yet.
- 🔴 Export report (CSV/XLSX — reuse ControlsAutomation XLAM patterns if
      useful)
