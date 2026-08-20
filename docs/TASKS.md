# Task List

Checkbox per phase from PROJECT_PLAN.md. Keep granular enough that each item is
a single commit-sized unit of work.

## Phase 0 — Setup
- [ ] Decide stack (OQ-STACK) — parser language, UI framework
- [ ] Repo skeleton: `src/parser`, `src/sizing`, `src/ui`
- [ ] Get one real (sanitized) production L5X into `samples/` as dev fixture
- [ ] `samples/manifest.csv` created with columns (see SAMPLE_GENERATION.md)
- [ ] XML load + basic namespace/schema sanity check for whatever L5X version(s)
      in use (OQ-L5XVERSION)

## Phase 1 — Tag / UDT / AOI sizing engine
- [ ] Atomic type size table (BOOL, SINT, INT, DINT, LINT, REAL, STRING) in
      MEMORY_MODEL.md, referenced not hardcoded
- [ ] BOOL packing rule implemented (bits-per-byte within DINT/SINT-backed
      storage, per OQ-BOOLPACK resolution)
- [ ] UDT parser: recurse `Controller/DataTypes/DataType/Members`
- [ ] UDT alignment/padding rule implemented (OQ-ALIGN)
- [ ] Array-of-atomic sizing (dimension × element size)
- [ ] Array-of-UDT sizing (dimension × recursive UDT size, padding per-element
      vs whole-array — OQ-ARRAYPACK)
- [ ] STRING (built-in) sizing: 4-byte LEN + configurable DATA array
- [ ] Custom STRING type sizing (user-defined max length UDTs) — separate path
      from generic UDT recursion
- [ ] AOI definition parser: `AddOnInstructionDefinitions` local tags + params
- [ ] AOI instance multiplication: each call site in logic adds one instance's
      worth of local tag memory (needs call-site count from logic parse —
      coordinate with Phase 4 work, may need to stub this until then)
- [ ] Module/IO parser: `Controller/Modules` → connection tag sizing (Local I/O
      first, produced/consumed second — OQ-PRODCONS)
- [ ] Controller-scope vs program-scope tag separation in output
- [ ] Flat output contract finalized: `{path, category, bytes, pct_of_total,
      confidence: exact|estimated}`
- [ ] Unit tests against hand-calculated small UDT (nested, 2 levels, mixed
      BOOL/DINT/STRING members)

## Phase 2 — UI v1
- [ ] Treemap component (squarified or similar algorithm)
- [ ] Root view: controller tags / program tags (per program) / UDT defs pool /
      AOI defs pool / module overhead, sized by bytes
- [ ] Click-to-drill: UDT → members, AOI → locals+params, program → its tags
- [ ] Breadcrumb / back navigation
- [ ] Sortable list view (name / type / bytes / %)
- [ ] Type-utilization summary pane (% of budget per data type across whole
      project, not just top-level categories)
- [ ] Color coding: exact (tags/UDT) vs estimated (logic, once Phase 5 lands) —
      build the visual language now even if unused until later
- [ ] Load Phase-0 dev fixture, sanity-check against manual spot-checks

## Phase 3 — Sample validation round 1
- [ ] Generate: 10k-element BOOL array (controller tag)
- [ ] Generate: 10k-element DINT array
- [ ] Generate: 10k-element UDT array (UDT = mix of BOOL/DINT/REAL, ~20 bytes/ea)
- [ ] Generate: nested UDT (UDT containing UDT containing UDT, 3 levels)
- [ ] Generate: STRING array (default 82-byte) ×1000
- [ ] Generate: custom string type (250-char) ×1000
- [ ] Generate: produced tag + matching consumed tag pair
- [ ] Generate: AOI with 5 local tags, called 50 times vs called 1 time (isolate
      per-instance cost)
- [ ] Generate: program-scope vs controller-scope identical tag (confirm no
      difference, or document the difference)
- [ ] For each: import → download → record actual bytes (TESTING_PLAN.md
      procedure) → log in manifest.csv
- [ ] Reconcile predicted vs actual, update MEMORY_MODEL.md constants
- [ ] Re-run full sample set after each constant change until stable
- [ ] Document final confidence/tolerance achieved

## Phase 4 — Logic sizing round 1 (bit logic)
- [ ] Generate: N rungs (10/100/1000) of single XIC + single OTE, empty branches
- [ ] Generate: same counts for XIO, OTL, OTU
- [ ] Generate: branch depth variations (1, 3, 5 parallel branches) at fixed
      rung count
- [ ] Generate: rung comment presence vs absence at fixed rung count (OQ-COMMENTS)
- [ ] Generate: empty rungs (comment-only, no instructions) at scale
- [ ] Record actual memory delta per sample
- [ ] Fit initial per-instruction weight, log residuals

## Phase 4b — Logic sizing round 2 (other instructions)
- [ ] Timer instructions (TON/TOF/RTO) at scale
- [ ] Counter instructions (CTU/CTD) at scale
- [ ] Math instructions (ADD/SUB/MUL/DIV/CPT with expression length variation)
- [ ] MOV / logical (AND/OR/XOR/NOT) at scale
- [ ] Compare instructions (EQU/NEQ/LES/GRT/LIM/MEQ)
- [ ] Array/file instructions (COP/FLL) at varying array size
- [ ] Indirect addressing overhead (compare direct vs indirect same logic)
- [ ] JSR/subroutine call overhead (call site cost vs routine body cost,
      separate these two numbers)
- [ ] MSG instruction overhead
- [ ] Consolidate full instruction-weight table into MEMORY_MODEL.md
- [ ] Hold out 3-5 samples, validate fitted model against them, log residual

## Phase 5 — UI v2 (logic browsing)
- [ ] Extend data contract: routines/rungs feed the same
      `{path, bytes, confidence}` shape as tags
- [ ] Treemap drill: Task → Program → Routine → (rung-level list, not
      individual-rung treemap nodes — too granular to be useful visually)
- [ ] Subroutine call-tree rollup (JSR chains sum correctly, no double-counting
      shared subroutines called from multiple places — OQ-JSRSHARED)
- [ ] "Estimated" badge/color on every logic-derived number in both treemap and
      list views
- [ ] Combined root view merging tags + logic + module overhead into one map

## Phase 6 — Polish
- [ ] Safety task scope decision implemented (OQ-SAFETY)
- [ ] Alarm instance (ALMD/ALMA) overhead if in scope (OQ-ALARM)
- [ ] Selectable controller memory budget (750KB/1MB/2MB/4MB/8MB) instead of
      hardcoded 4MB denominator
- [ ] Export report (CSV/XLSX — reuse ControlsAutomation XLAM patterns if useful)
